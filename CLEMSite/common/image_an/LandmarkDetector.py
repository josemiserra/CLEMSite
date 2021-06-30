import pandas as pd
import glob
from common.image_an.readers import getInfoHeaderAtlas
from common.image_an.lineDetector.gld_imaging import *
from common.image_an.lineDetector.gld_helpers import *
from common.image_an.lineDetector.gridLineDetector import GridLineDetector
from common.image_an.image_utils import borderEnhancer
from common.MsiteHelper import filterPick
from common.image_an.PatternClassifier import PatternClassifier
import json
from common.image_an.readers import  imageToStageCoordinates_SEM
from common.occupancy_map import Map
import time
from common.terrainChecker import *
from os.path import basename
from tqdm import tqdm
from skimage.morphology import skeletonize
from skimage.transform import probabilistic_hough_line
from math import sqrt
import os

class LandmarkDetector(object):
    """
    """
    iclahe = cv2.createCLAHE(clipLimit=0.01, tileGridSize=(32, 32))

    def __init__(self, ilogger, iserver, ifolder, ihelper, grid_map):
        """ Return a Customer object whose name is *name*."""
        self.logger = ilogger
        self.msc_server = iserver
        self.orientation = None
        self.folderOperations = ifolder
        self.msite_helper = ihelper
        self.grid_map = grid_map
        # Get information data from the grid

    def setPreferences(self, iprefdict):
        self.prefdict = iprefdict
        self.gld = GridLineDetector()
        self.my_pclas = PatternClassifier(self.prefdict['pattern_detector'][0]['architecture'],
                                          self.prefdict['pattern_detector'][0]['weights'], self.grid_map)
        self.terrainChecker = terrainChecker(self.prefdict['terrain_detector'][0]['architecture'],
                                             self.prefdict['terrain_detector'][0]['weights'])

        self.graph = tf.Graph()
        self.session = tf.compat.v1.Session(graph=self.graph)
        self.loadModel(self.prefdict['cross_detector'][0]['architecture'],
                       self.prefdict['cross_detector'][0]['weights'])

    def generateInformationFile(self, input_im, outputdir, tag, orientation="", letter=""):
        """
            Information about the Picture stored in an info dictionary
            Important info is PositionX, PositionY, PixelSize, orientation and letter center
        :param outputdir:
        :param tag:
        :return:
        """
        # Prepare data from preferences file (user.pref is a json file)
        ## Prepare data from preferences file (user.pref is a json file)
        try:
            info = getInfoHeaderAtlas(input_im)
        except:
            return None,None
        error, realCoords = self.msc_server.getCurrentStagePosition()
        info['posx'] = float(realCoords[0])  # coordinates plus BS
        info['posy'] = float(realCoords[1])  # coordinates plus BS
        info['orientation'] = orientation

        info['tag'] = tag
        info['letter_center'] = letter
        infoname = outputdir + "\\" + tag + "_info.txt"
        with open(infoname, 'w') as outfile:
            json.dump(info, outfile)
        return info, infoname


    def detect(self, input_im, tag, orientation, letter, trueletter):
        """
        Calls Detector to compute the line detection and perform the image analysis
        """
        self.logger.info("Applying detection on "+str(tag))
        self.orientation = orientation
        data ={}
        if (input_im == ""):
            self.logger.info("Image "+input_im+" not found.")
            return False,[0]
        # Output directory for images
        output_dir = self.folderOperations+"\\"+tag
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Preferences file needed for SOFT parameters and grid params
        params_fname = os.path.abspath(".\\preferences\\user.pref")
        # Matlab directory where matlab script are
        ####################################
        info, infofilename = self.generateInformationFile(input_im, output_dir, tag, orientation, letter)

        try:
            self.gld.runGLD(input_im,output_dir, params_fname, infofilename, microscopy_type='SEM')
        except GLDException as gld_e:
            return False, str(gld_e)

        ## Search for files
        directories = glob.glob(output_dir + '\*')
        xd = filterPick(directories, 'ld_')
        if (xd == None):
            self.logger.error("Directory with image analysis files not found.")
            return False,[0]
        xdir = directories[xd[0]]
        xfiles = glob.glob(xdir + '\*')
        #################################################################
        ######## Check files
        ########################################################################
        x = filterPick(xfiles, 'cutpoints.csv')
        if (not x):
            self.logger.error("Error, generated file cutpoints (.*cutpoints.csv) not found.")
            return False,[]
        cutpoints_file = xfiles[x[0]]
        ### Search swt
        x = filterPick(xfiles, '_swt')
        if (not x):
            self.logger.error("Error, generated file *_swt*.tif not found.")
            return False,[]
        swt_file = xfiles[x[0]]
        ### Read negative and positive angle
        x = filterPick(xfiles, 'peaks.csv')
        if (not x):
            self.logger.error("Error, generated file cutpoints (.*cutpoints.csv) not found.")
            return False,[]
        peaks_file = xfiles[x[0]]
        ####
        x = filterPick(directories, 'info.txt')
        if (not x):
            self.logger.error("Error, generated file info file (.*info.txt) not found.")
            return False,[]
        info_file = directories[x[0]]
        with open(info_file) as data_file:
            data = data_file.read()
        info = json.loads(data)

        # throw to a pandas dataframe and extract positive angle and negative angle
        ####
        df_peaks = pd.read_csv(peaks_file, names=['peak', 'angle', 'magnitude'], skiprows=1)
        df_peaks = df_peaks.apply(pd.to_numeric)
        angneg = np.mean(np.array(df_peaks.where( df_peaks['angle'] < 1)['angle'].dropna()))
        angpos = np.mean(np.array(df_peaks.where( df_peaks['angle'] > 0)['angle'].dropna()))

        # ang = min(np.abs(angneg), angpos)
        #if ang == np.abs(angneg) :
        #    ang = -ang

        ####################
        date = time.strftime("%d%m%Y-%H%M")
        sample_data = {}

        sample_data['orientation'] = self.orientation
        sample_data['true_pattern'] = True
        sample_data['e_pattern'] = info['letter_center']
        sample_data['distsq'] = round(float(self.prefdict['grid'][0]['div2']) / float(info['PixelSize']))

        df_points = self.my_pclas.predict_letters_from_picture(cutpoints_file, swt_file, "letters_" + date, sample_data, flip= True)
        # The center point is marked as 2, the ones in the central square as 1, and if is not the central square as 0
        if df_points is None:
            self.logger.info("Problems, no data points found.")
            return False, []
        data = {}
        data['tag'] = tag
        try:
            data['cpoint'] = df_points.where(df_points['center_point'] == 2).dropna().index.tolist()[0]
        except IndexError as err:
            self.logger.info("Problems finding center point.")
            return False,[]
        data['angneg'] = angneg
        data['angpos'] = angpos
        data['letter'] = df_points.loc[data['cpoint']]['letter']
        data['total_points'] = len(df_points.where(df_points['in'] == 1).notnull())

        self.logger.info("--- Grabbed image info:")
        self.logger.info ("Center square: " + str(data['cpoint']))
        self.logger.info ("Negative angle: " + str(data['angneg']))
        self.logger.info ("Positive Angle: " + str(data['angpos']))
        self.logger.info ("Total points found: " + str(data['total_points']))


        ##########################################
        px = float(info['PositionX'])
        py = float(info['PositionY'])
        size = (int(info['Height']), int(info['Width']))
        #
        fpoints = np.array([[df_points.loc[i]['x'], df_points.loc[i]['y']] for i in range(len(df_points))])
        stage_coordinates = imageToStageCoordinates_SEM(fpoints, (px, py), size, float(info['PixelSize']))
        df_points['cx_stage'] = stage_coordinates[:, 0]
        df_points['cy_stage'] = stage_coordinates[:, 1]
        ## add to df_points
        df_points.to_csv(xdir + '\\' + info['tag'] + '_final_points.csv')
        # Remove Non used points
        df_points = df_points.where(df_points['in'] == 1).dropna()
        tags = list(df_points['letter'])
        datamap = Map.getMapCoordinates(tags)
        datamap = [[el[0],el[1],0] for el in datamap ]
        datasem = [[df_points.loc[i,'cx_stage'], df_points.loc[i,'cy_stage'],0] for i in df_points.index.tolist()]

        ######################################################################
        ## Move to squares and refine the coordinate system
        datasem = self.refineCoordinates(datasem,output_dir,tags)
        ## remove failed refinements
        datasem_aux = list(datasem)
        datamap_aux = list(datamap)
        tags_aux = list(tags)

        for ind,el in enumerate(datasem):
            if(el[0]==-1 or el[0]==-2): # and el[1] = -1
               self.logger.info("Coordinate from:" +str(tags[ind])+" removed.")
               datasem_aux.remove(el)
               datamap_aux.remove(datamap[ind])
               tags_aux.remove(tags[ind])
        datasem = datasem_aux
        datamap = datamap_aux
        tags = tags_aux
        ## Save refined coordinates
        self.msite_helper.saveXML(xdir + '\\' + info['tag'] + "_fcoordinates_calibrate.xml",
                             tags, datasem, datamap)

        data['sem']=datasem
        data['tags'] = tags
        data['map']= datamap
        data['orientation'] = orientation
        return len(data['sem'])>2,data

    def refineCoordinates(self, datasem, output_dir, tags, dwell_time=8,psize =0.8 ):
        datasem_purged = [None]*len(datasem)
        error,origin_coords = self.msc_server.getCurrentStagePosition()
        for ind,p_coords in enumerate(datasem):
            c_name ="ref_"+str(ind)+"_"+str(tags[ind])
            self.msc_server.setStageXYPosition(p_coords)
            #error, image_ref = self.msc_server.grabImage(7, 0.4, 1, 1, 0, output_dir, c_name, shared=False)
            error, image_ref = self.msc_server.grabImage(dwell_time, psize, 0, 2, 0, output_dir, c_name, shared=True)
            if(not image_ref):
                self.logger.warning("Refine Coordinates FAILED.")
                return datasem
            new_point = self.getCrossPoint(image_ref, output_dir, str(tags[ind]),c_name)
            if(not new_point):
                datasem_purged[ind] = [-1, -1]
                continue
            if(new_point[0]>0.0): # Positive coordinates
                # Substitute coordinates
                datasem_purged[ind] = new_point
            else:
                datasem_purged[ind]= [-2,-2]

        self.msc_server.setStageXYPosition(origin_coords)
        return datasem_purged

    def getCrossPoint(self, image_ref, output_dir, tag, c_name):
        """
        1. Detect if image is inside the grid
        2. Apply CROSS detection subroutine
        3. return value

        :param image_ref:
        :param output_dir:
        :param tag:
        :param c_name:
        :return:
        """
        check_if_out = self.terrainChecker.checkTerrain(image_ref)
        if (check_if_out < 0):
            self.logger.info("Point detected outside sample by Terrain Checker. Blocking point:" + str(tag))
            if check_if_out == -1:
                self.logger.info("Image totally uniform.")
            return [-2, -2]  # To avoid AUTOFOCUS
        info, infofilename = self.generateInformationFile(image_ref, output_dir, tag)
        if not info:
            return -201
        cross_point = self.crossingDetector(image_ref, output_dir, infofilename)
        cross_point = np.array(cross_point,dtype= np.float32)
        if not cross_point.size:
            self.logger.info("Cross point not found.")
            return [-1,-1]

        p_coords = [0, 0, 0]
        p_coords[0] = float(cross_point[0])
        if (p_coords[0] < 0):
            p_coords[0] = -p_coords[0]
        p_coords[1] = float(cross_point[1])
        if (p_coords[1] < 0):
            p_coords[1] = -p_coords[1]
        return p_coords

    def loadModel(self,architecture,weights):
        json_file = open(architecture,'r')
        json_model = json_file.read()
        json_file.close()
        with self.graph.as_default():
            with self.session.as_default():
                self.model = model_from_json(json_model)
                self.model.load_weights(weights)
        return

    def preprocess(self,image):
        image = cv2.GaussianBlur(image, (5, 5), 0)
        n_image = self.iclahe.apply(np.uint8(image))
        final = np.array(n_image, dtype=np.float32)
        final = (final - np.min(final)) / (np.max(final) - np.min(final))  # Normalization has to be done AFTER AUGMENTATION
        return final

    def path_to_tensor(self,img_path):
        img = cv2.imread(img_path, 0)
        final = cv2.resize(img, (256, 256))
        final = self.preprocess(final)
        # convert 3D tensor to 4D tensor with shape (1, 128, 128, 1) and return 4D tensor
        return np.expand_dims(final, axis=0)

    def paths_to_tensor(self,img_paths):
        list_of_tensors = [self.path_to_tensor(img_path) for img_path in tqdm(img_paths)]
        return np.vstack(list_of_tensors)


    def crossingDetector(self,input_image_file, output_dir, infofilename):
        """

        :param input_image_file:
        :param output_dir:
        :param infofilename:
        :return:
        """
        theta_plus = [np.pi * sqrt(2) * 0.5 + i for i in np.linspace(-0.17, 0.17, num=5)]
        theta_minus = [-np.pi * sqrt(2) * 0.5 + i for i in np.linspace(-0.17, 0.17, num=5)]
        ftheta = theta_plus + theta_minus


        input_image = cv2.imread(input_image_file,0)
        res = input_image.shape[0]
        image = self.path_to_tensor(input_image_file)
        im_test = image.reshape(1, 256, 256, 1)
        with self.graph.as_default():
                with self.session.as_default():
                    prob_img = self.model.predict(im_test)
        prob_img = np.squeeze(prob_img)
        imgw, fa = autoThreshold(prob_img, 0.1)

        skel = skeletonize(imgw > 0)
        skel = borderEnhancer(skel, [2, 2])
        lines = probabilistic_hough_line(skel, threshold=10, line_length=20,
                                         line_gap=20, theta=np.array(ftheta))
        im2 = np.zeros((256, 256))
        for line in lines:
            p0, p1 = line
            cv2.line(im2, p0, p1, 255, thickness=2, lineType=8, shift=0)

        imgw[im2 < 255] = 0
        imgw = cv2.resize(np.uint8(imgw*255), (res, res))

        img_to_save = cv2.cvtColor(input_image, cv2.COLOR_GRAY2RGB)
        img_to_save[:, :, 2] = np.max([imgw, img_to_save[:, :, 2]], axis=0)
        image_name = basename(input_image_file)
        # remove extension
        img_n = image_name[:-4]
        fin_dir = output_dir+"\\"+"cross_"+img_n
        if not os.path.exists(fin_dir):
            os.makedirs(fin_dir)

        cv2.imwrite(fin_dir+"\\"+img_n[:8]+"_det_cross.jpg",img_to_save)
        d_info = {}
        # Read info file.
        with  open(infofilename,'r') as info_file:
            dic_str = info_file.read()

        file_data = json.loads(dic_str)
        pxsize = float(file_data['PixelSize'])
        thickness = np.min([int(self.prefdict['grid'][0]['div1']),int(self.prefdict['grid'][0]['div2'])])/pxsize # getImageDiv


        fpeaks_pos, fpeaks_neg, projections = getPeaks(input_image,imgw,[thickness], minpeaks = 2)

        if fpeaks_pos.shape[0] == 0 or fpeaks_neg.shape[0] == 0 :
            # Try cross detection by traditional filters:
            #swt = getSWT(input_image)
            # fpeaks_pos, fpeaks_neg, projections = getPeaks(input_image, swt, [thickness])
            # cv2.imwrite(fin_dir + "\\" + img_n[:8] + "_swt.jpg", np.uint8(swt*255))
            #if fpeaks_pos.shape[0] == 0 or fpeaks_neg.shape[0] == 0:
            self.logger.info("No peaks found")
            return []

        d_info['PositivePeaks'] = str(fpeaks_pos)
        d_info['NegativePeaks'] = str(fpeaks_neg)

        #fig, ax = plt.subplots(nrows=1, ncols=1)
        #ax.imshow(projections,'hot')
        #fig.savefig(fin_dir + "\\" + img_n[:8] + "_projections.png", bbox_inches='tight')
        #plt.close(fig)
        cpoint, fpoints, iimgc, _ =selectGridPoints(np.uint8(input_image*255),fpeaks_pos, fpeaks_neg)
        if len(cpoint)==0 :
            return []
        if cpoint[0]<0 or cpoint[1]<0 or cpoint[0]>res or cpoint[1]>res :
            return []
        iimgc = cv2.cvtColor(iimgc, cv2.COLOR_BGR2RGB)
        cv2.imwrite(fin_dir + "\\" + img_n[:8] + "_sketch.jpg", iimgc)
        d_info['mid_point_pixels'] = str(cpoint)
        d_info['square_points_pixels'] = str(fpoints)
        tpoint =  (float(file_data['posx']),float(file_data['posy']))
        pstack = np.vstack([cpoint, fpoints])
        coords_stage = imageToStageCoordinates_SEM(pstack, -np.array(tpoint, dtype = np.float32), imgw.shape, pxsize)
        d_info['coords_stage']= str(coords_stage)
        with open( fin_dir+'\\data.json', 'w') as fp:
            json.dump(d_info, fp, indent=4)
        self.msite_helper.saveTXT(fin_dir+"\\"+img_n[:8]+'_fpoints.csv',[file_data['tag']], [coords_stage[0]],[])
        self.msite_helper.saveTXT(fin_dir + "\\" + img_n[:8] + '_pixpoints.csv', [file_data['tag']], [cpoint],[])
        return coords_stage[0]








