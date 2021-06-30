import cv2
from os import path
import pandas as pd
import numpy as np
import os, sys, re
import matplotlib.pyplot as plt
import focus_measures as fm
from datetime import datetime
from scipy.signal import argrelmax
import xml.etree.ElementTree as ET
import time
from time import gmtime, strftime
import bisect
import csv

def filterPick(myList, myString):
    """

    :rtype: string
    """
    pattern = re.compile(myString);
    indices = [i for i, x in enumerate(myList) if pattern.search(x)]
    return indices

def getFiles(m_folder,re_tag):
    """
         Search for an image with the specified regular expression

        :param val:
        :return:
    """
    dname = m_folder
    onlyfiles = [ f for f in os.listdir(dname) if path.isfile(path.join(dname, f)) ]

    x = filterPick(onlyfiles,re_tag)
    if not x:
            return "";
    # List of files
    files_to_check = []
    for el in x:
        files_to_check.append(path.join(m_folder,onlyfiles[el]))
        # Get the filename of the image
    files_to_check.sort(key=lambda x: os.path.getmtime(x))
    return files_to_check

def extractInfoXMLImages(fileinput):
    """
    Extract all possible information from .ve-a3f files into a pandas dataframe
    :param fileinput:
    :param fileoutput:
    :return:
    """
    try:
        tree = ET.parse(fileinput)
    except ET.ParseError as err:
        print err
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

def extractInfoXMLAutotune(fileinput):
    """
        Extract all possible information from .ve-a3f files into a pandas dataframe
        :param fileinput:
        :param fileoutput:
        :return:
        """
    try:
        tree = ET.parse(fileinput)
    except ET.ParseError as err:
        print err
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
        if(child.findall('Status')):
            Status = child.findall('Status')[0]
            Time = child.findall('Time')[0]
            if child.findall('Focus'):
                Focus = child.findall('Focus')[0]
            if(child.findall('QRel')):
                Qrel = child.findall('QRel')[0]
                Qabs = child.findall('QAbs')[0]
        else:
            continue
        l_status.append(Status.text)
        l_focus.append(float(Focus.text))
        indt = Time.text.find(".")
        vtime = Time.text[:indt]
        vtime = vtime.replace('T',' ')
        l_time.append(vtime)
        l_qrel.append(float(Qrel.text))
        l_qabs.append(float(Qabs.text))
        l_operation.append("AutoFocus")
        l_stigX.append(float(0))
        l_stigY.append(float(0))

    for child in atlas_rinfo.findall('AutoStig'):
        if (child.findall('Status')):
            Status = child.findall('Status')[0]
            Time = child.findall('Time')[0]
            Focus = 0
            if (child.findall('QRel')):
                Qrel = child.findall('QRel')[0]
                Qabs = child.findall('QAbs')[0]
            if(child.findall('StigX')):
                StigX = child.findall('StigX')[0]
            if(child.findall('StigY')):
                StigY = child.findall('StigY')[0]
        l_status.append(Status.text)
        indt = Time.text.find(".")
        vtime = Time.text[:indt]
        vtime = vtime.replace('T', ' ')
        l_time.append(vtime)
        l_qrel.append(float(Qrel.text))
        l_qabs.append(float(Qabs.text))
        l_operation.append("AutoStig")
        l_stigX.append(float(StigX.text))
        l_stigY.append(float(StigY.text))
        l_focus.append(float(0))

    # Time has to be changed to a minutes sequence

    df = pd.DataFrame({'Operation': l_operation, 'Status': l_status, 'Focus': l_focus,
                       'Qrel': l_qrel,'Qabs':l_qabs, 'Time': l_time, 'StigX': l_stigX, 'StigY': l_stigY})

    return df

def extractInfoXMLAFAS(fileinput):
    """
    Extract all possible information from .ve-a3f files into a pandas dataframe
    :param fileinput:
    :param fileoutput:
    :return:
    """
    try:
        tree = ET.parse(fileinput)
    except ET.ParseError as err:
        print err
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

def blackBorderDetection(im_1):
    height, width = im_1.shape

    ret, th = cv2.threshold(im_1, 0, 1, cv2.THRESH_BINARY)
    # Find corners of picture
    # if not possible, leave it like this
    th = th * 255
    try:
        contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        _, contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except:
        return False
    # imageC = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
    # imageC = cv2.drawContours(imageC, contours, -1, (0,255,0), 3)

    # This has to be change to a list and to get the MINIMUM x and y from all contours
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # If area of square is smaller than
        if (w * h < 1000):  # avoid errors.
            continue
        else:
            break
    # otherwise, take the corners
    return x,y,w,h

def is_slice_file(file):
    p = re.compile(r'.*slice.*tif$')
    # if name has slice and um
    if(p.match(file)):
        return True
    return False

def createRunFile(outdir,jobfile,v3f_file):
    """
        Generates file tag_pdata.csv
    :param outdir:
    :param tag:
    :return:
    """
    # read the .v3f file
    df1 = extractInfoXMLImages(v3f_file)
    df_new = appendAllSlices(outdir,df1)
    if(np.any(df_new)):
        df_new.to_csv(jobfile)
    return df_new

def appendAllSlices(outdir,v3f_df):
    # Check if there is a slice in the folder.
    # if NOT return empty
    slices = []
    flist =  os.listdir(outdir)
    for el in flist:
        if(is_slice_file(el)):
            slices.append(el)

    df_new = getInfoSlice(outdir,slices[0],v3f_df)
    for slice_file in slices:
         dataSlice = getInfoSlice(outdir,slice_file,v3f_df)
         df_new = df_new.append(dataSlice,ignore_index=True)
         f1.write('New slice added:'+str(slice_file)+'\n')
         print 'New slice added:'+str(slice_file)
    df_new = df_new.drop_duplicates(['Name'])
    return df_new

def getInfoSlice(outdir,slice_file,v3f_df):
    im_1 = cv2.imread(outdir + "\\" + slice_file, cv2.IMREAD_GRAYSCALE)
    if(not np.any(im_1>0)):
        return
    x, y, w, h = blackBorderDetection(im_1)
    im_crop = im_1[y:y + h, x:x + w]

    M1_p = fm.fmeasure('GLVA',im_crop)
    M1_s = fm.fmeasure('SFREQ',im_crop)
    M2_p = fm.fmeasure('GDER',im_crop)
    M2_s = fm.fmeasure('VOLA',im_crop)

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
    df_new.loc[0, 'x'] = x
    df_new.loc[0, 'y'] = y
    df_new.loc[0, 'w'] = w
    df_new.loc[0, 'h'] = h
    df_new.loc[0, 'M1_p'] = M1_p
    df_new.loc[0, 'M1_s'] = M1_s
    df_new.loc[0, 'M2_p'] = M2_p
    df_new.loc[0, 'M2_s'] = M2_s
    return df_new

def addNewSlices(outdir,df_slices,v3f_file):
    # Read file .v3f and check if the ImageNo last matches
    df1 = extractInfoXMLImages(v3f_file)
    ly, lx = df1.shape
    for i in range(0,ly,1):
        lastImNo =    df1['ImageNo'][i]
        if(lastImNo not in df_slices['ImageNo'][:]):
            # we add it
            slice_name = df1['Name'][i]
            df_newSlice = getInfoSlice(outdir, slice_name,df1)
            df_slices = df_slices.append(df_newSlice,ignore_index=True)
            print 'Adding new slice:'
            print str(df_newSlice)

    df_slices = df_slices.sort_values(by="ImageNo")
    df_slices = df_slices.drop_duplicates(['Name'])
    df_slices = df_slices.reset_index(drop=True)
    return df_slices

def FocusEval(ifocus_values,izpos,eval_pos, epsilon = 0):

    focus_values = ifocus_values[0:eval_pos]
    zpos = izpos[0:eval_pos]

    focus_values2 = ifocus_values[eval_pos:]
    zpos2 = izpos[eval_pos:]


    if(epsilon==0):
        epsilon = 2*np.std(focus_values)
    zpos = np.array(zpos, dtype=np.float32)
    X = np.array([np.ones(np.array(zpos.shape)), zpos], dtype=np.float32)
    X = np.mat(X.transpose())
    X_inv = np.linalg.pinv(X.transpose() * X)
    X_aux = X_inv * X.transpose()
    theta = X_aux * np.array(focus_values).reshape((len(focus_values), 1))

    pred_z = []
    for el in zpos2:
       pred_z.append(theta[0] + theta[1] * el)

    pred_z = np.squeeze(pred_z)
    if(pred_z.size==1):
        pred_z = np.array([pred_z])
    error = np.sqrt((pred_z - np.array(focus_values2,dtype=np.float32))**2)
    M1 = (error>epsilon)
    return M1, error, pred_z

def StigsEval(istigx,istigy,izpos,eval_pos, epsilon = 0):

    zpos = np.array(izpos, dtype=np.float32)

    stigx_values = istigx[0:eval_pos]
    stigy_values = istigy[0:eval_pos]
    zpos = izpos[0:eval_pos]

    stigx_values2 = istigx[eval_pos:]
    stigy_values2 = istigy[eval_pos:]
    zpos2 = izpos[eval_pos:]

    if(epsilon==0):
        epsilon_sx = np.std(stigx_values)
        epsilon_sy = np.std(stigy_values)
    if(epsilon_sx<1e-8):
        epsilon_sx = 0.5 # We don't  allow variation superior to 0.5 per cent
    if(epsilon_sy<1e-8):
        epsilon_sy = 0.5
    M2a = (np.abs(stigx_values2-np.mean(stigx_values)) > epsilon_sx)
    M2b = (np.abs(stigy_values2-np.mean(stigy_values)) > epsilon_sy)
    M2 = M2a | M2b
    # Good stigs are the ones before evaluation
    fstigsx = np.full(M2.shape, istigx[eval_pos-1])
    fstigsy = np.full(M2.shape, istigy[eval_pos-1])
    return M2,fstigsx,fstigsy

def MetricEval(m1_p,m1_s, eval_pos, focus_hap=[]):
    m1_p1 = m1_p[0:eval_pos]
    m1_s1 = m1_s[0:eval_pos]

    mu_p1 = np.mean(m1_p1)
    sd_p1 = np.std(m1_p1)
    m1_p = (m1_p - mu_p1)/sd_p1

    dm1_p = np.abs(np.diff(m1_p))
    #
    max_values = []
    if(focus_hap):
        max_values.append(focus_hap-1)
    else:
        max_values = argrelmax(dm1_p)
        max_values = max_values[0]

    max_values = np.array(max_values)
    # from all maxima we find how many beat 2 times the std
    fp = dm1_p[max_values] > 2 * np.std(dm1_p)
    final_max_p = max_values[np.where(fp)]

    # Now we repeat for second measure
    mu_s1 = np.mean(m1_s1)
    sd_s1 = np.std(m1_s1)
    m1_s = (m1_s - mu_s1)/sd_s1
    dm1_s = np.abs(np.diff(m1_s))
    # Do we also have a peak?
    fp2 = dm1_s[final_max_p] > 2 * np.std(dm1_s)
    fmax = final_max_p[np.where(fp2)]
    fmax = fmax[np.where(fmax >= eval_pos-1)]

    ns = m1_p[eval_pos:]
    measure = np.full(ns.shape,False,dtype=bool)
    if(np.any(fmax>0)):
        measure[fmax-eval_pos+1] = True
    return measure

def getLastAutofocus(fileinput):
    df_Autofocus =  extractInfoXMLAutotune(fileinput)
    TimeLapse = df_Autofocus['Time'].to_dict().values()
    TimeLapse.sort(key=lambda x: time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S')))
    return TimeLapse[-1]

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

def evaluate(df_new, df_old,focus_hap,no_measures=False):

    focus_values = df_new['Focus'][:].to_dict().values()
    zpos = df_new['Zpos'][:].to_dict().values()

    evdict = df_new.where(df_new.isin(df_old))['ImageNo'][:].to_dict()

    eval_pos = -1
    for key,value in zip(evdict.keys(),evdict.values()):
        if(np.isnan(value)):
           eval_pos = int(key)
           break

    if(eval_pos ==-1):
        return False,[]

    # evaluate Focus
    M1,error,good_focus = FocusEval(focus_values,zpos,eval_pos)
    # evaluate_stigs
    stigx_values = df_new['StigX'][:].to_dict().values()
    stigy_values = df_new['StigY'][:].to_dict().values()
    M2,good_stigsx,good_stigsy = StigsEval(stigx_values,stigy_values,zpos,eval_pos)

    final = False
    if(no_measures):
        final = M1 | M2
    else:
        # Evaluate blurring
        m1p_values = df_new['M1_p'][:].to_dict().values()
        m1s_values = df_new['M1_s'][:].to_dict().values()
        M3 = MetricEval(m1p_values,m1s_values,eval_pos,focus_hap) # Variance

        m2p_values = df_new['M2_p'][:].to_dict().values()
        m2s_values = df_new['M2_s'][:].to_dict().values()
        m2p_values = np.array(m2p_values) # Blur metrics
        M4 = MetricEval(m2p_values,m2s_values,eval_pos,focus_hap) # Blur
        final = (M1 & M4) | (M2 & M3)

    good_values = dict()
    revert = False
    if(np.any(final)):
        ind = focus_hap-eval_pos # Point where last focus happened
        f1.write("AFAS FAILED. Reverting values in slice number " + str(df_new.loc[eval_pos]['Name']))
        print "AFAS FAILED. Reverting in slice number " + str(df_new.loc[eval_pos]['Name'])
        good_values['Focus'] = good_focus[-1]
        good_values['StigX'] = good_stigsx[-1]
        good_values['StigY'] = good_stigsy[-1]
        good_values['LastSlice'] = str(df_new['ImageNo'][df_new.last_valid_index()])
        f1.write(str(good_values))
        print str(good_values)
        revert = True
    return revert,good_values

def purgeStabilizationPeriod(df_new,df_old):
    ############################################################
    # From Time of the last element, check if we are over 10 minutes
    # Stabilization period must be excluded
    # if <10 minutes
    # return

    r, c = df_new.shape
    last = df_new['Time'][r - 1]
    begin = df_new['Time'][0]
    FMT = '%Y-%m-%d %H:%M:%S'
    tdelta = datetime.strptime(last, FMT) - datetime.strptime(begin, FMT)
    if (int(tdelta.seconds / 60) < 11):
        # Nothing else to do
        sys.exit(1)
        return
    # remove data from first 10 minutes
    for tel, i in zip(df_new['Time'], df_new.index.tolist()):
        last = str(tel)
        tdelta = datetime.strptime(last, FMT) - datetime.strptime(begin, FMT)
        if (int(tdelta.seconds / 60) < 10):
            df_new = df_new[df_new.index != i]

    for tel, i in zip(df_old['Time'], df_old.index.tolist()):
        last = str(tel)
        tdelta = datetime.strptime(last, FMT) - datetime.strptime(begin, FMT)
        if (int(tdelta.seconds / 60) < 10):
            df_old = df_old[df_old.index != i]
    df_new = df_new.reset_index()
    df_old = df_old.reset_index()
    return df_new, df_old

def purgeUntilLastCorrection(df_new,df_old,ilastSlice):

    if (ilastSlice > -1):
        rmask = (df_new.ImageNo == ilastSlice)
        if(np.any(rmask)):
            # remove data from first 10 minutes
            for iel, i in zip(df_new['ImageNo'], df_new.index.tolist()):
                if (int(iel) <= ilastSlice):
                    df_new = df_new[df_new.index != i]
            for iel, i in zip(df_old['ImageNo'], df_old.index.tolist()):
                if (int(iel) <= ilastSlice):
                    df_old = df_old[df_old.index != i]
            df_new = df_new.reset_index()
            df_old = df_old.reset_index()
        else:
            sys.exit(-1)
            return
    return df_new,df_old

def runCheck(file_im,tag,ilastSlice):
    # Read data file tag_data.csv. If not present, then create
    folder_store, file_slice = path.split(file_im)
    job_file = folder_store + "\\" + tag + ".csv"

    v3f_files = getFiles(folder_store, "ve-a3f")
    if (not v3f_files):
        return
    v3f_file = ''
    for el in v3f_files:
        if (el[-6:] == "ve-a3f"):
            v3f_file = el

    if os.path.isfile(job_file):
        ## Read data
        df_old = pd.DataFrame.from_csv(job_file)
        df_new = addNewSlices(folder_store, df_old, v3f_file)
        df_new.to_csv(job_file)
    else:
        df_new = createRunFile(folder_store,job_file, v3f_file)
        return


    df_new_or = df_new.copy()
    df_old_or = df_old.copy()

    df_new, df_old = purgeStabilizationPeriod(df_new,df_old)

    df_new,df_old = purgeUntilLastCorrection(df_new,df_old,ilastSlice)

    # Read from .bak where was the last time than AFAS happened
    timeAF = getLastAutofocus(v3f_file)
    time_list = df_new['Time'].to_dict().values()
    indAF = findTimeStamp(time_list,timeAF)
    if(indAF==0 and ilastSlice>-1): # AF already evaluated
        return

    revert_afas = False
    revert_list = dict()
    if(df_old.empty and indAF>-1):
        # The autofocus was just after the stab. period.
        time_list = df_new_or['Time'].to_dict().values()
        indAF = findTimeStamp(time_list, timeAF)
        revert_afas, revert_list = evaluate(df_new_or, df_old_or, indAF, no_measures = True)
    else:
        # if AFAS AFTER the last evaluated
        revert_afas, revert_list = evaluate(df_new,df_old,indAF)

    if (revert_afas):
        stim = strftime("%Y_%m_%d_%H:%M:%S", gmtime())
        file_data = folder_store + "\\check_" + tag + str(stim)+".csv"
        if(os.path.isfile(file_data)):
            os.remove(file_data)
        with open(file_data, 'w') as f:
            f.write("Focus,"+str(revert_list['Focus'])+"\n")
            f.write("StigX,"+str(revert_list['StigX'])+"\n")
            f.write("StigY,"+str(revert_list['StigY'])+"\n")
            f.write("LastSlice," + str(revert_list['LastSlice']) + "\n")
    return

def getLastSlice(file_prev):
    with open(file_prev, 'rb') as csvfile:
        lastfreader = csv.reader(csvfile, delimiter='\n')
        for row in lastfreader:
            vr = row[0].split(',')
            if(vr[0]=='LastSlice'):
                myrow = int(vr[1])
                break
    return myrow
# Slice acquired including directory of images
# Tag
#file_im = sys.argv[1]
#tag = sys.argv[2]
file_im = "D:\\GOLGI\\TEST_FOCUS\\25OCT\\My_Project25_Focus\\5S_33___0000\\My_Project25_Focus_5S_33___0000\\slicecell__00000_z=0.0000um.tif"
tag = "r090"


folder_store, file_slice = path.split(file_im)
f1=open( folder_store+'\\log_'+tag, 'w+')
file_check = folder_store + "\\runcheck_" + tag + ".csv"
lastSlice = -1
if(os.path.isfile(file_check)):
    lastSlice = getLastSlice(file_check)
runCheck(file_im,tag,lastSlice)
f1.write("Completed")
f1.close




