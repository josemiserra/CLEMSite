import cv2
from os import path
import pandas as pd
import numpy as np
import os, sys, re
import matplotlib.pyplot as plt
import focus_measures as fm
from datetime import datetime
import xml.etree.ElementTree as ET
import time
import bisect
import csv
from shutil import copyfile
import glob, subprocess
from subprocess import PIPE

from detectFocusPoints import detectPoints,writeErrorFile,preprocess
import logging
from imutils import blackBorderDetection, getPixelSize, getFiles
from removeBlack import save_no_black
import math
from SIFT import computeShiftImages
import json
from automaton_utils import getInfoFromA3DSetup, send_email
from isFeatureless import hasFeaturesImage
import errno




def is_slice_file(file):
    p = re.compile(r'.*slice.*tif$')
    # if name has slice and um
    if(p.match(file)):
        return True
    return False

def findTimeStamp(time_list,timeaf):
    """
    time_list is assumed sorted
    :param time_list:
    :param time:
    :return:
    """
    if(timeaf):
         i = bisect.bisect_left(time_list, timeaf)
    else:
        i = -1
    return i


class V3FNotFoundException(Exception):
   pass


class Reporter:
    """

    Class that analyzes folder with slices and extracts data.
    It also processes images and saves data

    """
    lastSlice = -1

    INCREMENT_UP = 0.25
    INCREMENT_DOWN = 0.5
    INCREMENT_DOWN_PERCENTAGE = 0.25
    SECTION_THICKNESS_LIMIT = 15
    MAXIMUM_INTERPHASE_ALLOWED_PERCENTAGE = 0.25

    def __init__(self,file_im,itag, ipreferences):
        # Input options

        acq_parameters = ipreferences['preferences']['acquisition_parameters'][0]
        email_preferences = ipreferences['preferences']['email_preferences'][0]


        self.file_im = file_im
        self.folder_store, self.file_slice = path.split(file_im)
        self.tag = itag

        self.email_exists = False
        if email_preferences["user_address"]:
            self.user_data = {}
            self.user_data = email_preferences
            self.email_exists = True

        self.python_exe = ipreferences['preferences']['server_images'][0]['python_folder']

        self.SIFT_tracking = acq_parameters['tracking_ASIFT_active']>0
        self.section_thickness = int(acq_parameters['section_thickness'])
        self.tracking_stop_point_active = int(acq_parameters['tracking_stop_point_active'])>0
        self.tracking_xcorr = int(acq_parameters['tracking_xcorr'])>0
        self.black_threshold_active = int(acq_parameters['black_threshold_active'])>0
        if self.black_threshold_active:
            self.black_threshold = int(acq_parameters['black_threshold'])


        # Setup
        # Search .a3dsetup
        folder_st2, _ = path.split(self.folder_store)
        a3d_files = getFiles(folder_st2, ".a3d-setup")
        self.info_a3d = getInfoFromA3DSetup(a3d_files[0])
        self.number_slices = round(self.info_a3d['dY'] / self.info_a3d['SliceThickness'])
        self.AFAS_period = self.info_a3d['AF_Interval']
        # LOGGER
        self.log_file = self.folder_store+"\\run_info"
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # By default, logs all messages
        fh = logging.FileHandler("{0}.log".format(self.log_file))
        fh.setLevel(logging.DEBUG)
        fh_format = logging.Formatter('%(asctime)s - %(lineno)d - %(message)s')
        fh.setFormatter(fh_format)
        logger.addHandler(fh)
        self.logger = logger

        self.job_file = self.folder_store + "\\runcheck.csv"
        self.folder_fdata = self.folder_store + "\\f_data"
        self.email_folder = self.folder_store+"\\email_data"

        # If we already worked here before
        if (os.path.isfile(self.job_file)):
            self.lastSlice = self.getLastSlice(self.job_file)
        else:
            if not os.path.exists(self.folder_fdata):
                os.mkdir(self.folder_fdata)
        # Find V3F files
        v3f_files = getFiles(self.folder_store, "ve-a3f")
        if (not v3f_files):
            raise V3FNotFoundException("ve-a3f file not found")

        v3f_file = ''
        for el in v3f_files:
            if (el[-6:] == "ve-a3f"):
                self.v3f_file = el

        if not (os.path.exists(self.email_folder)):
            os.mkdir(self.email_folder)
        self.pixelSize = getPixelSize(file_im,atlas=True)
        self.logger.info("Initialized succesfully for "+file_im)
        self.not_active = False

    def getLastSlice(self, file_prev):
        """
        Obtain index of last slice from the file. Its a simple counter
        :param file_prev:
        :return:
        """
        myrow = 0
        with open(file_prev, 'r') as csvfile:
            lastfreader = csv.reader(csvfile, delimiter='\n')
            for row in lastfreader:
                myrow +=1
        return myrow

    def runCheck(self):
        """
            It is the core of the Reporter.
            First, read old .csv info in a pandas dataframe and update information from v3f file,
            V3F are files from Atlas that keep track of images and events happening in Atlas.
        """
        ################## READ DATA #############################################
        if self.not_active :
            return
        if os.path.isfile(self.job_file):
            # Read data if already exists
            df_old = pd.read_csv(self.job_file,index_col=0)
            # Proceed to add extra empty info from new slices from v3f_file if emptied (not processing)
            df_new = self.addNewSlices(df_old)
            self.logger.info("Previous file checked.")
            new = False
        else:
            df_new = self.createRunFile()
            new = True

        ############## Get image ###################

        islice = df_new.Name.iloc[-1] #Get last slice
        last_ind = df_new.index[-1]
        im_last = self.folder_store + "\\" + islice
        slice_count = len(df_new)
        stop_point_pix = 0
        # Crop black borders of image
        im_crop, df_new = self.removeBorder(im_last,df_new,last_ind)

        # Now, just in case, save
        df_new.to_csv(self.job_file)  # save
        self.logger.info("Computing drifts for "+self.file_slice)

        #  the FIRST slice has to center the image and it has to use the stop_point. In God we trust!
        if new:
            self.tracking_stop_point_active = True

        # This SIFT_track_good is a status variable, it is True if SIFT_track can be done.
        # To decide if SIFT is done is the variable SIFT_tracking
        SIFT_track_good = True
        if self.tracking_stop_point_active:
            SIFT_track_good = False
            # Compute stop point
            percentage_slices = (slice_count / (1.0 * self.number_slices))
            fimg, stop_point_pix = preprocess(im_crop, True)
            if (percentage_slices > 0.5): # The coat is lost, then entropy HAS TO BE AVOIDED. We use average to reduce the impact of shift
                fimg, stop_point_pix_no_entropy = preprocess(im_crop, False)
                stop_point_pix = percentage_slices*stop_point_pix_no_entropy + (1-percentage_slices)*stop_point_pix

            stop_point_um = stop_point_pix*self.pixelSize
            df_new.loc[last_ind,'stop'] =  stop_point_um
            self.logger.info("Old stop point:"+str(df_new.stop.iloc[-2])+", new stop point:"+str(stop_point_um))

            if len(df_new) <= 4 :
                df_new.loc[last_ind, 'shift_y'] = 1.5 # Default shift

            if len(df_new) > 4 and  not df_new.at[last_ind-1, 'cancel_next_shift'] : # If we did a shift before, now we ignore it
                #  Amount of drift is calculated relative to the previous section
                drift = np.abs(np.abs(stop_point_pix * self.pixelSize) - np.abs(df_new.stop.iloc[-2]))
                ignore_stop_point = False

                # Section thickness below 15 and after 20 sections, tracking can go by ASIFT or xcorr
                if int(self.section_thickness)< Reporter.SECTION_THICKNESS_LIMIT and len(df_new)>20:
                    ignore_stop_point = True
                    SIFT_track_good = True

                # Stop point is too close to the cell or inside the cell (stop_point == 0)
                if stop_point_pix < 0.075*im_crop.shape[0] and not ignore_stop_point: # 0.075 Less than 1 percent of the total shape
                    df_new.loc[last_ind, 'cancel_next_shift'] = False  # We should keep going up
                    increment = Reporter.INCREMENT_UP # um.
                    df_new.loc[last_ind, 'shift_y'] = df_new.loc[last_ind, 'shift_y']+increment
                    self.logger.info("Stop_point detected close to the cell. Shift computed in Y using stop point:"+str(df_new.loc[last_ind, 'shift_y']))
                    self.SIFT_track_good = False

                # There is too much imaged interphase (more than 25 percent). Then we have to move down a percentage of that stop point, do it progressively
                elif stop_point_pix > Reporter.MAXIMUM_INTERPHASE_ALLOWED_PERCENTAGE*im_crop.shape[0] and not ignore_stop_point: # 0.25, before was 0.15
                    increment = -np.min([Reporter.INCREMENT_DOWN_PERCENTAGE*stop_point_um,Reporter.INCREMENT_DOWN])
                    df_new.loc[last_ind, 'cancel_next_shift'] = False # We should keep going down
                    df_new.loc[last_ind, 'shift_y'] = (df_new.loc[last_ind, 'shift_y']+increment)
                    self.logger.info("Stop_point detected too deep, showing too much interphase. Increment in Y :"+str(increment)+". Final shift computed in Y :" + str(df_new.loc[last_ind, 'shift_y']))
                    self.SIFT_track_good = False

                elif drift> 0.025*im_crop.shape[0]*self.pixelSize : # There was a shift that has to be tracked
                    self.logger.info('Drift detected :'+str(drift))
                    # We will perform other tracking if active
                    if self.SIFT_tracking:
                        SIFT_track_good = True
                else:
                    df_new.loc[last_ind, 'cancel_next_shift'] = True  # Continue as this

        if self.SIFT_tracking and SIFT_track_good and len(df_new) > 4 :
                # Get previous slice
                prev_slice = df_new.Name.iloc[-2]
                im_previous_nob = self.folder_store + "\\no_border\\" + prev_slice
                # check if file of last slice exists, if not, produce it!
                if(not os.path.isfile(im_previous_nob)):
                    im_previous_nob = self.folder_store + "\\no_border\\" + prev_slice
                    prev_ind = df_new.index[-2]
                    im_prev_last = self.folder_store + "\\" + prev_slice
                    im_crop_pre, df_new = self.removeBorder(im_prev_last, df_new, prev_ind)

                # Check that we didn't do a tracking in the last before one.
                if not df_new.cancel_next_shift.iloc[-2]:
                    # compute shift
                    self.logger.info('Performing SIFT')
                    previous_img   = cv2.imread(im_previous_nob,0)
                    # If stop point was calculated previously, it helps to remove useless parts from the image to do ASIFT
                    remove_from_image = 0
                    if  df_new.stop.iloc[-2]>0:
                        stop_point_previous = int(df_new.stop.iloc[-2]/self.pixelSize)
                        self.logger.info('Previous stop_point :' + str(stop_point_previous))
                        remove_from_image = stop_point_previous - 10
                    previous_img[0:remove_from_image, :] = 0

                    remove_from_image = 0
                    if stop_point_pix>0:
                        remove_from_image = stop_point_pix -10
                    fimg = im_crop.copy()
                    fimg[0:remove_from_image,:] = 0

                    shift,_,_ = computeShiftImages(previous_img, fimg,self.logger)
                    self.logger.info('Shift in Y detected using SIFT:' + str(shift)+' pixels.')
                    shift = np.array(shift,dtype=np.float32) * self.pixelSize

                    # Small shifts means the same as no shifts
                    if (np.abs(shift[0]) < 0.0025 and np.abs(shift[1]) < 0.0025):
                        shift = np.array([0.0, 0.0], dtype=np.float32)

                    # Don't allow big jumps using SIFT (sometimes gives crazy results)
                    # Limit to maximum 0.5 increments, to 2 um if we have sections smaller than 50 um
                    limit = 3.5
                    if self.section_thickness > 50 :
                        limit = 0.5
                    # Increment is done by a moving average
                    if np.abs(shift[0])<limit and np.abs(shift[1])<limit :
                        self.logger.info('Shift used in detection:' + str(shift))
                        beta = 0.8
                        # if shift is not bigger than 1 um
                        # Shift is going to be accumulative
                        df_new.loc[last_ind, 'shift_x'] = 0
                        df_new.loc[last_ind, 'shift_y'] =  beta*df_new.loc[last_ind-1, 'shift_y']+(1-beta)*(df_new.loc[last_ind, 'shift_y'] + shift[1])
                        self.logger.info('Shift accumulated in total:' + str(df_new.loc[last_ind, 'shift_y']))
                        self.logger.info('SIFT operation completed successfully.')
                        df_new.loc[last_ind, 'cancel_next_shift'] = True

        # Compute other needed measures from images.
        val = df_new.loc[last_ind, 'shift_y']
        df_new = df_new.reset_index(drop=True)
        last_ind = df_new.index[-1]
        # Double checking of shift. Sometimes, computations can fail. In order to avoid that
        if val == 0 and (self.tracking_stop_point_active or self.SIFT_tracking):
            i = last_ind-1
            while df_new.at[i,'shift_y']==0 and i>0:
                i = i-1
            val = df_new.at[i,'shift_y']
            if np.abs(val)>0.2: # Give a tolerance.  It cannot jump from +/-0.2 to 0, but it can do it if 0.05
                df_new.loc[last_ind, 'shift_y'] = val
                self.logger.info("Detected 0 shift. This cannot be possible. Restoring to:"+str(val))


        # Remove black part. TODO : needs better testing and improve efficiency in detection. Is too slow and delays execution of Reporter
        if self.black_threshold_active:
            df_new.loc[last_ind, 'hasFeatures'] = True
        #    if ((slice_count/(1.0*self.number_slices))> (self.black_threshold)*0.01):
        #        remove_from_image = 0
        #        if stop_point_pix > 0 and stop_point_pix < im_crop.shape[0]-5:
        #            remove_from_image = stop_point_pix + 5
        #       im_crop = im_crop[remove_from_image:, :]
        #        df_new.loc[last_ind, 'hasFeatures'] = hasFeaturesImage(im_crop)

        # AutoFocus measures to be used to detect bad focus
        for ind, slice_name in enumerate(df_new.Name):
                if self.compute_Measures(df_new, slice_name, ind, val) :
                    self.logger.info("Computing measures for :" + slice_name)

        if fm.hasQualityDrop(list(df_new['VOLA']), 5, 5) and not fm.hasQualityDrop(list(df_new['VOLA'][:-1]), 5, 5):
            # First, check that the quality didn't drop in the previous on
            # self.executeAFAS()
            self.sendEmailFocusDown(df_new, im_crop, islice)

          ###################TIME AFAS LINE ##########################################
        # Read from .bak where was the last time than AFAS happened
        timeAF,firstAFAS = self.getLastAutofocus(self.v3f_file)
        timeAF = np.datetime64(timeAF,'ms')

        # expected time for new AFAS
        # if Default Stabilization Period has not happened
        if(firstAFAS):
            nextAF = timeAF + 300000 # 600000 Variable Default Stabilization Period
        else:
            nextAF = timeAF + self.AFAS_period

        ct = datetime.now()
        ct = np.datetime64(ct, 'ms')
        try:
            eAF_time = np.int64(nextAF - ct)
        except TypeError:
            self.logger.info('Something wrong is going on here, negative time before autofocus.')
            return
        slice_time = 80000
        if len(df_new) < 3:
            self.logger.info("Less than 3 slices. Not computing AF.")
            rem_slices = np.inf
        else:
            sl_1 = df_new.Time.iloc[-2]
            sl_2 = df_new.Time.iloc[-1]
            slice_time = (np.datetime64(sl_2) - np.datetime64(sl_1)) / np.timedelta64(1, 'ms')
            rem_slices = int(math.floor(eAF_time / slice_time))

        if rem_slices == np.inf:
            df_new.at[last_ind, 's_to_AF'] = 1 # 1000000  # high number
        else:
            df_new.at[last_ind, 's_to_AF'] = rem_slices

        self.logger.info("Next autofocus expected at "+str(nextAF))
        # Launch an independent process that executes AF one minute and half before
        eAF_time = eAF_time -  120000 #(slice_time+80000)
        self.launchAF(eAF_time,timeAF)
        # Launch process with timer countdown at X autofocus time - 1 minute

        if df_new.isnull().values.any() :
            self.logger.info("PROBLEM!  "+str(last_ind))
            df_new = df_new.dropna()

        df_new.to_csv(self.job_file)  # save
        self.logger.info("Completed computations for "+str(islice))
        self.logger.info("############################")


    def sendEmailFocusDown(self, df, im_crop, islice):
        msg = 'Warning, quality in focus down. Check if Autofocus needed.'
        img_files = []
        fig, ax = plt.subplots(nrows=1, ncols=1)
        plt.figure(figsize=(12, 14))
        ax.plot(df['VOLA'], color = (255./255., 52./255., 50./255.))
        ax.spines["top"].set_visible(False)
        # ax.spines["bottom"].set_visible(False)
        ax.spines["right"].set_visible(False)
        # ax.spines["left"].set_visible(False)
        plot_name = self.email_folder + "\\" + str(islice) + '_VOLA.png'
        fig.savefig(plot_name, bbox_inches='tight')
        plt.close(fig)
        img_files.append(plot_name)
        ####
        h, w = im_crop.shape
        r = 1.0
        if (h > 1024 and w > 1024):
            r = 1024.0 / w
            dim = (1024, int(h * r))
            # perform resizing to speed up
            rimg = cv2.resize(im_crop, dim, interpolation=cv2.INTER_AREA)
        else:
            rimg = im_crop.copy()

        img_name = self.email_folder + "\\" + islice + "_red.jpg"
        cv2.imwrite(img_name, rimg)
        img_files.append(img_name)
        if self.email_exists:
            send_email(self.user_data['user_address'], [self.user_data['recipients']],
                   'FIB-SEM Message focus Dropdown at ' + str(islice), msg,
                   files=img_files, server=self.user_data['smtp'], username=self.user_data['username'], password= self.user_data['password'])



    def launchAF(self,eAF_time,timeAF):
        """
        Process that will be launched now with a countdown. When the countdown times up
        launches the AF detection of points.

        :param nextAF_time:
        :return:
        """
        files = getFiles(self.folder_store, ".*af.pid")
        if(files):
            return
        else:
            self.logger.info("Producing AF points.")
            dir_path = path.dirname(os.path.realpath(__file__))
            values = "/C "+self.python_exe+" "+dir_path+"\\AFPoints.py"+\
                " "+str(eAF_time)+" "+str(timeAF) + " " + self.folder_store
            self.logger.info(values)
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            DETACHED_PROCESS = 0x00000008
            subprocess.Popen(["cmd.exe", values], stdin=PIPE, stdout=PIPE, stderr=PIPE, creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)


    def removeBorder(self,image_path,df_new,ind):
        imgor = cv2.imread(image_path, 0)
        if imgor is None:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),image_path)

        im_crop, bb = blackBorderDetection(imgor)
        x, y, w, h = bb
        df_new.loc[ind, 'x'] = x
        df_new.loc[ind, 'y'] = y
        df_new.loc[ind, 'h'] = h
        df_new.loc[ind, 'w'] = w

        head, tail = os.path.split(image_path)
        # If a folder to save blackborder images does not exist, do it.
        if not os.path.exists(self.folder_store+"\\no_border"):
            os.makedirs(self.folder_store+"\\no_border")
        im_no_border = self.folder_store+"\\"+tail
        dir_border = self.folder_store+"\\no_border"
        save_no_black(im_no_border,dir_border)
        return im_crop, df_new


    def compute_Measures(self,df, slice_file, index_slice,shift_y):
        if df.w[index_slice] == 0 or df.VOLA[index_slice] < 0: # Means nothing has been computed!
            im_1 = cv2.imread(self.folder_store + "\\" + slice_file, cv2.IMREAD_GRAYSCALE)
            if (not np.any(im_1 > 0)):
                return False
            im_crop,bb = blackBorderDetection(im_1)
            x, y, w, h = bb
            if df.w[index_slice] == 0 :
                df.loc[index_slice, 'x'] = x
                df.loc[index_slice, 'y'] = y
                df.loc[index_slice, 'h'] = h
                df.loc[index_slice, 'w'] = w
                _, stop_point = preprocess(im_crop)
                df.loc[index_slice, 'shift_x'] = 0
                df.loc[index_slice, 'shift_y'] = shift_y
                df.loc[index_slice, 'stop'] = stop_point * self.pixelSize
                df.loc[index_slice, 'hasFeatures'] = True
    #else:
    #    x = int(df.loc[index_slice, 'x'])
    #    y = int(df.loc[index_slice, 'y'])
    #    w = int(df.loc[index_slice, 'h'])
    #    h = int(df.loc[index_slice, 'w'])
    #        im_crop = im_1[y:y + w, x:x + h]

    #        df.loc[index_slice, 'M1_p'] = fm.fmeasure('GLVA', im_crop)
    #        df.loc[index_slice, 'M1_s'] = fm.fmeasure('SFREQ', im_crop)
    #        df.loc[index_slice, 'M2_p'] = fm.fmeasure('GDER', im_crop)
            if df.VOLA[index_slice] < 0 :
                df.loc[index_slice, 'VOLA'] = fm.fmeasure('VOLA', im_crop)
            return True
        return False

    def extractInfoXMLImages(self,fileinput):
        """
        Extract all possible information from .ve-a3f files into a pandas dataframe

        :param fileinput:
        :return: pandas dataframe with file information
        """
        try:
            tree = ET.parse(fileinput)
        except ET.ParseError as err:
            self.logger.info(err)
        root = tree.getroot()
        l_focus = []
        l_zpos = []
        l_stigX = []
        l_stigY = []
        l_time = []
        l_name = []
        l_number = []

        atlas_rinfo = root.getchildren()[1] # 'ATLAS3D-Run'
        for child in atlas_rinfo.findall('Image'):
            Number = child.findall('ImageNo')[0]
            Time = child.findall('Time')[0]
            ZPos = child.findall('ZPos')[0]
            Focus = child.findall('Focus')[0]
            StigX = child.findall('StigX')[0]
            StigY = child.findall('StigY')[0]
            Name = child.findall('Filename')[0]

            l_number.append(int(Number.text))
            l_focus.append(float(Focus.text))
            indt = Time.text.find(".")
            vtime = Time.text[:indt]
            vtime = vtime.replace('T', ' ')
            l_time.append(vtime)
            l_zpos.append(float(ZPos.text))
            l_stigX.append(float(StigX.text))
            l_stigY.append(float(StigY.text))
            l_name.append(str(Name.text))
        # Time has to be changed to a minutes sequence

        df = pd.DataFrame({'Name': l_name, 'ImageNo': l_number,'Focus':l_focus,
                           'Zpos':l_zpos,'Time':l_time,'StigX':l_stigX,'StigY':l_stigY})

        return df

    def extractInfoXMLAutotune(self,fileinput):
        """
            Extract all possible information from .ve-a3f files into a pandas dataframe
            from previous autotune
            :param fileinput:
            :param fileoutput:
            :return: pandas datafram with file information
            """
        try:
            tree = ET.parse(fileinput)
        except ET.ParseError as err:
            self.logger.info(err)
        root = tree.getroot()
        l_focus = []
        l_qrel = []
        l_qabs = []
        l_time = []
        l_stigX = []
        l_stigY = []
        l_operation = []
        l_status = []

        atlas_rinfo = root.getchildren()[1]  # 'ATLAS3D-Run'

        for child in atlas_rinfo.findall('AutoFocus'):
            Qrel = "0.0"
            Qabs = "0.0"
            Focus = "nan"
            if child.findall('Status'):
                Status = child.findall('Status')[0]
                Time = child.findall('Time')[0]
                if child.findall('Focus'):
                    Focus = child.findall('Focus')[0].text
                if(child.findall('QRel')):
                    Qrel = child.findall('QRel')[0].text
                    Qabs = child.findall('QAbs')[0].text
            else:
                continue
            l_status.append(Status.text)
            l_focus.append(float(Focus))
            indt = Time.text.find(".")
            vtime = Time.text[:indt]
            vtime = vtime.replace('T',' ')
            l_time.append(vtime)
            l_qrel.append(float(Qrel))
            l_qabs.append(float(Qabs))
            l_operation.append("AutoFocus")
            l_stigX.append(float(0))
            l_stigY.append(float(0))


        for child in atlas_rinfo.findall('AutoStig'):
            StigX = "nan"
            StigY = "nan"
            Qrel = "0.0"
            Qabs = "0.0"
            if (child.findall('Status')):
                Status = child.findall('Status')[0]
                Time = child.findall('Time')[0]
                Focus = 0
                if (child.findall('QRel')):
                    Qrel = child.findall('QRel')[0].text
                    Qabs = child.findall('QAbs')[0].text
                if(child.findall('StigX')):
                    StigX = child.findall('StigX')[0].text
                if(child.findall('StigY')):
                    StigY = child.findall('StigY')[0].text
            else:
                continue
            l_status.append(Status.text)
            indt = Time.text.find(".")
            vtime = Time.text[:indt]
            vtime = vtime.replace('T', ' ')
            l_time.append(vtime)
            l_qrel.append(float(Qrel))
            l_qabs.append(float(Qabs))
            l_operation.append("AutoStig")
            l_stigX.append(float(StigX))
            l_stigY.append(float(StigY))
            l_focus.append(float(0))

        # Time has to be changed to a minutes sequence

        df = pd.DataFrame({'Operation': l_operation, 'Status': l_status, 'Focus': l_focus,
                           'Qrel': l_qrel,'Qabs':l_qabs, 'Time': l_time, 'StigX': l_stigX, 'StigY': l_stigY})

        return df

    def extractInfoXMLAFAS(self,fileinput):
        """
        Extract all possible information from .ve-a3f files into a pandas dataframe
        from Events.
        :param fileinput:
        :param fileoutput:
        :return:
        """
        try:
            tree = ET.parse(fileinput)
        except ET.ParseError as err:
            self.logger.info(err)
        root = tree.getroot()
        atlas_log_info = root.getchildren()[2] #'Log'
        l_time_dt = []
        l_dt = []

        l_time_afas = []
        l_afas_message = []

        for child in atlas_log_info.findall('Event'):
            for melem in child:
                System = child.findall('System')[0]
                Time = child.findall('Time')[0]
                if(System.text == 'Imaging'):
                    Message = child.findall('Message')[0]
                    if(Message.text.find("dwell time")>0):
                        indt = Time.text.find("T")
                        vtime = Time.text[indt+1:19]
                        l_time_dt.append(vtime)
                        indt = Message.text.find("dwell time to")
                        dt =  Message.text[indt+14:indt+17].replace(',','.')
                        l_dt.append(float(dt))
                elif(System.text =='AutoTune'):
                    Message = child.findall('Message')[0]
                    indt = Time.text.find("T")
                    vtime = Time.text[indt + 1:19]
                    l_time_afas.append(vtime)
                    indt = Message.text.find("dwell time to")
                    l_afas_message.append(Message.text)

        df_dt = pd.DataFrame({'Time': l_time_dt, 'DwellTime': dt})
        df_afas = pd.DataFrame({'Time': l_time_afas, 'Message':l_afas_message})

        return df_dt,df_afas

    def createRunFile(self):
        """
            Generates file tag_pdata.csv
        :param outdir:
        :param tag:
        :return:
        """
        # read the .v3f file
        df1 = self.extractInfoXMLImages(self.v3f_file)
        df_new = self.appendAllSlices(self.folder_store,df1)
        if(np.any(df_new)):
            df_new.to_csv(self.job_file)
        return df_new

    def appendAllSlices(self, outdir, v3f_df):
        # Check if there is a slice in the folder.
        # if NOT return empty
        slices = []
        flist =  os.listdir(outdir)
        for el in flist:
            if(is_slice_file(el)):
                slices.append(el)

        df_new = self.initializeInfoSlice(slices[0],v3f_df)
        for slice_file in slices:
             dataSlice = self.initializeInfoSlice(slice_file,v3f_df)
             df_new = df_new.append(dataSlice,ignore_index=True)
             self.logger.info('New slice added:'+str(slice_file)+'\n')
        df_new = df_new.drop_duplicates(['Name'])
        df_new.reset_index(drop=True)
        return df_new

    def initializeInfoSlice(self, slice_file, v3f_df):
        # get information ONLY of your row
        ly,lx = v3f_df.shape
        slice_name_list = []
        slice_found = False
        for i in range(ly):
            if(slice_file == v3f_df['Name'][i]):
                slice_found = True
                break
        if(slice_found == False):
            return

        # The file must contain the following information
        #NameSlice, NumberSlice, Zpos, WD, StigX, StigY, x, y, w, h, M1, M2, M3

        df_new = v3f_df[i:i+1].copy()
        df_new = df_new.reset_index(drop=True)
        df_new.loc[0, 'shift_x'] = 0
        df_new.loc[0, 'shift_y'] = 0
        df_new.loc[0, 'stop'] = 0
        df_new.loc[0, 'x'] = 0
        df_new.loc[0, 'y'] = 0
        df_new.loc[0, 'h'] = 0
        df_new.loc[0, 'w'] = 0
        df_new.loc[0, 'VOLA'] = -1.0
        #df_new.loc[0, 'M1_s'] = 0.0
        #df_new.loc[0, 'M2_p'] = 0.0
        #df_new.loc[0, 'M2_s'] = 0.0

        df_new.loc[0, 's_to_AF'] = 0.0
        df_new.loc[0, 'cancel_next_shift'] = False
        df_new.loc[0, 'hasFeatures'] = True
        return df_new

    def getLastAutofocus(self, fileinput):
        df_Autofocus = self.extractInfoXMLAutotune(fileinput)
        if df_Autofocus.empty:
            df1 = self.extractInfoXMLImages(self.v3f_file)
            return df1['Time'][0],True
        else:
            TimeLapse = df_Autofocus['Time'].to_dict()
            TimeLapse_v = sorted(TimeLapse.values(), key=lambda x: time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S')))
            return TimeLapse_v[-1],False

    def addNewSlices(self, df_slices):
        # Read file .v3f and check if the ImageNo last matches
        df1 = self.extractInfoXMLImages(self.v3f_file)
        ly, lx = df1.shape

        for i in range(ly): #to_check in debugging synchronized mode
            lastImNo =    df1['ImageNo'][i]
            if(lastImNo not in list(df_slices['ImageNo'][:])):
                # we add it
                slice_name = df1['Name'][i]
                df_newSlice = self.initializeInfoSlice(slice_name,df1)
                # Look backwards to find first non_zero value in df_slices
                j = i - 1
                df_ind = df_slices.index[j]
                if j>0:
                    while df_slices.at[df_ind, 'shift_y'] == 0 and j > 0:
                        j = j - 1
                        df_ind = df_slices.index[j]
                    df_newSlice.loc[0,'shift_y'] = df_slices.at[j, 'shift_y']
                    df_newSlice.loc[0, 'stop'] = df_slices.at[j, 'stop']
                    df_newSlice.loc[0, 'x'] = df_slices.at[j, 'x']
                    df_newSlice.loc[0, 'y'] = df_slices.at[j, 'y']
                    df_newSlice.loc[0, 'h'] = df_slices.at[j, 'h']
                    df_newSlice.loc[0, 'w'] = df_slices.at[j, 'w']
                df_slices = df_slices.append(df_newSlice,ignore_index=True, sort = False)
                self.logger.info('Adding new slice:')
                self.logger.info(str(df_newSlice))

        df_slices = df_slices.sort_values(by="ImageNo")
        df_slices = df_slices.drop_duplicates(['Name'])
        df_slices = df_slices.reset_index(drop=True)
        return df_slices

def main():
    # Slice acquired including directory of images
    # Tag
    try :
        file_im = sys.argv[1]
        my_dir = os.path.dirname(os.path.realpath(__file__))
        preferences_file = my_dir + '\\fromMSite\\user.pref'
        tag = sys.argv[2]
        # Read preferences file
        with open(preferences_file) as f:
            preferences = json.load(f)

        rep = Reporter(file_im,tag, ipreferences = preferences)
        rep.not_active = False
        rep.runCheck()

    except TypeError:
            pass
    except SystemExit:
            pass
#    except:
#           print("Something WRONG with parameters")


if __name__ == "__main__":
    main()
