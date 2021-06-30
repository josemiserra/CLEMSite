import datetime
import logging
import json
import numpy as np
import csv
import os
import cv2
import pandas as pd

# from matplotlib import pyplot as plt

from common.image_an import tifftest
from common.image_an.lineDetector.gld_helpers import *




class GridLineDetector:
    """
    Given an input image, computes the detection of a grid and writes
    the resulting data coordinates to a text file.

    PARAMETERS contains information given by the user that affects the
           performance of the line detection during the preprocessing part.
               - Gaussian blur for noise averaging
               - CLAHE if necessary because uneven illummination
               - CANTHRESH it is the amount of white pixels recovered for
               the canny edges histeresis thresholding algorithm.
               This value is related to the amount of clutter being present in the image. If the
               amount of clutter is substantial this parameter can help to
               reduce it, but needs to be balanced with the amount of
               features from the grid that can be seen (too much removal
               can make it disappear them).
               - Values are between 0.05 to 0.3. For SEM images 0.06 is
                   recommended, for LM 0.075 works generally well.

    It also requires information about the grid to be detected.
               - gridsize : this algorithm is designed for 2 spacing
               grids, but can be easily modified for any desired grid
               pattern.
       IMAGE_DATA must contain at least 4 essential parameters:
           - PixelSize IN MICROMETERS
           - Coordinate X,Y from the center.
           - Predicted letter in the center (this letter will be evaluated
           by Image analysis algorithms and changed to one of the
           neighbors in case of a bad prediction).
           - If the value true_letter is true, then no image analysis
           checking is done
           - Orientation of the grid. Necessary to reduce the amount of
           comparisons performed by the letter matching algorithm. It is
           not absolutely necessary but simplifies and avoids unnecessary
           errors coming from a bad prediction in the image analysis side.
           This orientation can be done by extra algorithms on the client
           side, or simply asked to the user.
           - TAG - image sample name
    """
    # This is done for refactoring purposes without breaking functionality.
    class _logger:
        def __init__(self):
            self.log = ""

        def info(self, message):
            self.log = message
            print(message)

        def warning(self, message):
            self.log = message
            print(message)

    def __init__(self):
        self.softParams = {}
        self.logger = GridLineDetector._logger()

    def initialize_parameters(self):
        """
        Avoid faul initialization by setting up default parameters
        :return:
        """
        self.softParams['sigma'] = 1.5
        self.softParams['clahe'] = True
        self.softParams['laplacian'] = True
        self.softParams['canny_thresh'] = 0.085
        self.softParams['ignore_calibration'] = False
        self.softParams['K'] = 12
        self. softParams['wiener'] = np.array([2, 2])
        div1 = 40
        div2 = 560
        self.softParams['gridSize'] = np.array([div1, div2])
        self.softParams['strokeWidth'] = 15
        self.softParams['PixelSize'] = 1.5137
        self.softParams['p_angles'] = -1
        self.softParams['tag'] = 'tag'
        self.softParams['gridSizeUnits'] = self.softParams['gridSize'] / self.softParams['PixelSize']


    def runGLD(self, input_image_path, output_folder, parameters_file = None, image_metadata = None, microscopy_type = 'LM', debug = False, ilogger = []):
        """
        Launcher method for GLD
        :param input_image_path: .tif with reflected type
        :param output_folder:
        :param parameters_file:
        :param image_metadata:
        :param microscopy_type:
        :param debug:
        :return:
        """
        if ilogger:
            self.logger = ilogger()

        self.micro_type = microscopy_type
        self.debug = debug

        # Get current data
        now_date = datetime.datetime.now()
        self.now_string = now_date.strftime("%H_%M_%S_%B_%d_%Y")

        # Parse parameters name
        if parameters_file:
            self.softParams = self.readParametersFile(parameters_file, image_metadata)
            self.logger.info('Reading parameters from files :'+parameters_file)
            self.logger.info('Reading image parameters from :'+image_metadata)
            self.logger.info(str(self.softParams))
        else:
            self.initialize_parameters()
            self.logger.info('Using default parameters.'+str(self.softParams))

        self.dir_ld = output_folder+"\\ld_"+self.now_string
        if not os.path.exists(self.dir_ld):
            os.makedirs(self.dir_ld)

        input_image = cv2.imread(input_image_path,0)

        try:
            if self.micro_type == 'LM':
                self.softParams['inverse_stroke'] = True
                # images, fpoints, info = self._gld(input_image, self.softParams)
                self.softParams['do_alternative'] = True
                self.softParams['num_peaks'] = 8
                self.softParams['autoEdge'] = True
                self.softParams['force_peaks'] = False
                self._gld(input_image, self.softParams)
            elif self.micro_type == 'SEM':
                self.softParams['inverse_stroke'] = True
                self.softParams['ignore_calibration'] = True
                self.softParams['do_alternative'] = False
                self.softParams['num_peaks'] = 8
                self.softParams['force_peaks'] = True
                self.softParams['autoEdge'] = False
                self._gld(input_image, self.softParams)
        except GLDException as e:
            self.logger.info("ERROR in runGLD in gridLineDetector: "+e.args[0])

    def readParametersFile(self,parameters_file,image_metadata):
        """
        GLD is adapted to the CLEMSite software. Thus, it receives two files with all the
        respective parameters.
        :param parameters_file: file with grid sizes and line detection parameters for GLD
        :param image_metadata: Pixelsize and name of image (tag)
        :return: softParams, dictionary with all parameters
        """
        with open(parameters_file, "r") as read_file:
            data = json.load(read_file)
        softParams = {}
        softParams['sigma'] = float(data['preferences']['line_detection'][0][self.micro_type][0]['gaussian'])
        softParams['clahe'] = bool(int(data['preferences']['line_detection'][0][self.micro_type][0]['clahe']))
        softParams['laplacian'] = bool(int(data['preferences']['line_detection'][0][self.micro_type][0]['laplacian']))
        softParams['canny_thresh'] = float(data['preferences']['line_detection'][0][self.micro_type][0]['canny_thresh'])
        softParams['ignore_calibration'] = bool(int(data['preferences']['line_detection'][0][self.micro_type][0]['ignore_calibration']))
        softParams['K'] = int(data['preferences']['line_detection'][0][self.micro_type][0]['k'])
        softParams['wiener'] = np.array([2, 2])
        div1 = float(data['preferences']['grid'][0]['div1'])
        div2 = float(data['preferences']['grid'][0]['div2'])
        softParams['gridSize'] = np.array([div1, div2])
        softParams['strokeWidth'] = int(data['preferences']['line_detection'][0][self.micro_type][0]['stroke'])

        with open(image_metadata, "r") as read_file:
            dataIm = json.load(read_file)
        softParams['PixelSize'] = float(dataIm['PixelSize'])
        softParams['p_angles'] = translateAngle(float(dataIm['orientation']))
        softParams['tag'] = dataIm['tag']
        softParams['gridSizeUnits'] = softParams['gridSize'] / softParams['PixelSize']
        return softParams


    def _gld(self,input_image_original, gldParams):

        PREPRO, BWEDGE, ORIENTIM, RELIABILITY, FSWT = soft_launch(input_image_original, gldParams, v =True)

        cv2.imwrite(self.dir_ld + "\\" + gldParams['tag'][:14] + "_prepro.tiff", np.uint8(PREPRO))
        cv2.imwrite(self.dir_ld + "\\" + gldParams['tag'][:14] + "_edges.tiff", np.uint8(BWEDGE*255))
        cv2.imwrite(self.dir_ld + "\\" + gldParams['tag'][:14] + "_orientation.jpg", ORIENTIM,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
        cv2.imwrite(self.dir_ld + "\\" + gldParams['tag'][:14] + "_reliability.jpg", RELIABILITY,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
        cv2.imwrite(self.dir_ld + "\\" + gldParams['tag'][:14] + "_swt.tiff", np.uint8(FSWT*255))

        images = {}
        images['prepro']= PREPRO
        images['edges'] = BWEDGE
        images['orientation'] = ORIENTIM
        images['reliability'] = RELIABILITY
        images['SWT'] = FSWT

        self.logger.info('Preprocessing done.')


        npeaks, R = self.findBestPeaks(FSWT, ORIENTIM, gldParams['K'], 1, gldParams['gridSizeUnits'], [gldParams['p_angles']],gldParams['num_peaks'],gldParams['do_alternative'],gldParams['force_peaks'])

        min_peaks = gldParams['num_peaks']*0.5
        if len(npeaks[0])< min_peaks or len(npeaks[1])< min_peaks :
            raise GLDException("ERROR: Not enough peaks found.")

        #if self.debug:
        #    fig, ax = plt.subplots(nrows=1, ncols=1)
        #    ax.imshow(R, 'hot')
        #    fig.savefig(self.dir_ld + "\\"+gldParams['tag'][0:14]+"_projections.png", bbox_inches='tight')
        #    plt.close(fig)

        self.logger.info('Peaks found :'+str(npeaks))
        self.logger.info('Finding lines')

        goodLines, sketch = findLines(PREPRO, npeaks[0], npeaks[1])
        ### save sketched lines
        name_sketch = self.dir_ld + "\\"+gldParams['tag'][0:14]+"_lines.tiff"
        cv2.imwrite(name_sketch, np.uint8(sketch))

        mpoints = calibrateIntersections(input_image_original, BWEDGE, npeaks, goodLines, self.dir_ld, gldParams['laplacian'], gldParams['ignore_calibration'])
        if not mpoints:
            raise GLDException("ERROR: Not enough intersection points found.")

        all_cutpoints = cutSquares(mpoints,BWEDGE,gldParams['gridSizeUnits'])

        ### info
        ### Check, if less than 4 cutpoints and NOT ignore_bad_points
        ###  raise "Points found unable to past quality check in calibrate intersections. Not enough good points."
        # TO SAVE

        # log_+date+tag.txt
        # Inside ld folder

        npeaks2 = np.vstack([npeaks[0], npeaks[1]])
        npeaks2 = np.reshape(npeaks2, (-1, 3))
        df_peaks = pd.DataFrame(npeaks2)
        df_peaks.columns = (['projection', 'angle', 'value'])
        df_peaks.to_csv(self.dir_ld + "\\"+gldParams['tag'][0:14]+"_peaks.csv", index = False)
        #  - impar.csv
        #  - fpoints.csv
        #  - peaks.csv
        #  - cutpoints.csv
        all_cutpoints = np.squeeze(all_cutpoints)
        all_cutpoints = np.reshape(all_cutpoints, (-1, 5))
        df_cutpoints = pd.DataFrame(all_cutpoints)
        df_cutpoints.columns = (['x', 'y', 'group_number', 'is_in_image', 'is_in_square'])
        # name columns x, y, group_number, is_in_image, is_in_square

        df_cutpoints.to_csv(self.dir_ld + "\\"+gldParams['tag'][0:14]+"_cutpoints.csv", index=False)
        # fpoints and impar needed?
        return



    def findBestPeaks(self, swt, orientation, k_neighs, delta, gridsize, p_angles = None, num_peaks = 8, do_alternative = True, force_peaks = False):
        """
        Project via rotations and find peaks
        :param swt:
        :param orientation:
        :param k_neighs:
        :param delta:
        :param gridsize:
        :param p_angles:
        :return:
        """
        pos_angles = []
        neg_angles = []
        if p_angles:
            self.logger.info('Projections at angles '+str(p_angles))
            for ang in p_angles:
                if ang > 0:
                    newang = ang - 90
                else:
                    newang = 90 + ang
                if newang > -1 :
                    pos_angles.append(newang)
                    neg_angles.append(ang)
                else:
                    pos_angles.append(ang)
                    neg_angles.append(newang)
            self.logger.info('Computing projections for positive angles: '+str(pos_angles))
            rhigh_pos = projections(swt, orientation, k_neighs, delta, pos_angles, 5)
            self.logger.info('Computing projections for negative angles:' + str(neg_angles))
            rhigh_neg = projections(swt, orientation, k_neighs, delta, neg_angles, 5)
            R = rhigh_pos + rhigh_neg
            peaks_pos, _ = detectPeaksNMS(rhigh_pos, numpeaks=num_peaks*2, threshold=0.05, nhood=None)
            peaks_neg, _ = detectPeaksNMS(rhigh_neg, numpeaks=num_peaks*2, threshold=0.05, nhood=None)
        else:
            # Reduce image resolution by binning and find projections
            iLength, iWidth = swt.shape

            red_im = cv2.resize(swt, (int(iLength / 4),int(iWidth / 4)), cv2.INTER_NEAREST) # Use nearest neighbor interpolation, gives best results
            red_or = cv2.resize(orientation, (int(iLength / 4),int(iWidth / 4)), cv2.INTER_NEAREST)

            R = projections(red_im, red_or, 8, 1, 0, 0)
            self.logger.info('Projections at low resolution. \n')

            # Select the most prevalent angles at low resolution
            lrpeaks,_ = detectPeaksNMS(R, 8, threshold=0.25)
            sangles = np.unique(lrpeaks[:, 1])
            if len(sangles) == 0 :
                R = projections(swt, orientation, k_neighs, delta, [], 0)
                hrpeaks, _ = detectPeaksNMS(R, numpeaks=num_peaks, threshold=0.05, nhood=None)
                # Split in pos peaks and neg peaks
                peaks_pos, peaks_neg = splitpeaks(hrpeaks)
            else :
                # take all angles, but also the complementary ones
                for ang in sangles:
                    if ang > 0:
                        newang = ang - 90
                    else:
                        newang = 90 + ang
                    if newang > 0 :
                        pos_angles.append(newang)
                        neg_angles.append(ang)
                    else:
                        pos_angles.append(ang)
                        neg_angles.append(newang)
                pos_angles = np.unique(pos_angles)
                neg_angles = np.unique(neg_angles)
                self.logger.info('Projections at high resolution with angles: \n')
                self.logger.info(str(pos_angles))
                self.logger.info(str(neg_angles))
                Rhigh_pos = projections(swt, orientation, k_neighs, delta, pos_angles, 5)
                Rhigh_neg = projections(swt, orientation, k_neighs, delta, neg_angles, 5)
                R = Rhigh_pos + Rhigh_neg
                peaks_pos, _ = detectPeaksNMS(Rhigh_pos, numpeaks=num_peaks, threshold=0.05, nhood=None)
                peaks_neg, _ = detectPeaksNMS(Rhigh_neg, numpeaks=num_peaks, threshold=0.05, nhood=None)

        self.logger.info('Peak detection finished')
        self.logger.info('Positive peaks found '+str(peaks_pos))
        self.logger.info('Negative peaks found '+str(peaks_neg))
        self.logger.info('Executing purging of wrong peaks. Minimum amount of peaks expected '+str(num_peaks*0.5))
        ppeaks, npeaks = discardwrongpeaks(R, peaks_pos, peaks_neg, gridsize, min_peaks = num_peaks*0.5)
        self.logger.info('Purge completed')
        self.logger.info('Positive peaks :' + str(ppeaks))
        self.logger.info('Negative peaks :' + str(npeaks))


        ppeaks = np.array(ppeaks)
        npeaks = np.array(npeaks)
        ppeaks.reshape(-1,3)
        npeaks.reshape(-1,3)
        if do_alternative:
            self.logger.info('Executing alternative peaks')
            ppeaks = alternativePeaks(R, ppeaks)
            npeaks = alternativePeaks(R, npeaks)
        # Select only the peaks with highest rating
        return [ppeaks,npeaks], R



