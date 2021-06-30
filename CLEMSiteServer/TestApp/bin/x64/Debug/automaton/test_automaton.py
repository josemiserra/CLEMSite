
from findCentroidSquare import findSquare
from findCentroidSquare2 import findSquare2
from ESB_findTrench import detectorWorks,saveTrenchPoints
from detectFocusPoints import detectPointsFile
from isFeatureless import checkFeatures
from detectCell import getCell
import matplotlib.pyplot as plt
from Reporter import Reporter

import time
from os import path
from glob import glob
import unittest
import json

class AutomatonCPTestCase(unittest.TestCase):
    def test_find_SEM_square(self):
        tag = "-any-date"
        # test 2
        file_before = "test_images\\coincidence_point_checks_t6\\SEM_1st.tif"
        file_after = "test_images\\coincidence_point_checks_t6\\SEM_1st_square.tif"
        print('find SEM square \n')
        self.assertTrue(findSquare(file_before, file_after, tag))

    def test_find_Square2_SEM(self):
        tag = "-SEM-any-date"
        file_im= "test_images\\coincidence_point_checks_t6\\SEM_2nd.tif"
        folder_store, file = path.split(file_im)
        # Get the template file from the folder
        template_file = glob(folder_store + "\\square_template*.tif")
        print('find SEM Square 2 \n')
        self.assertTrue(findSquare2(file_im,template_file[0],tag))

    def test_find_Square2_FIB(self):
        tag = "-FIB-any-date"
        file_im=  "test_images\\coincidence_point_checks_t6\\FIB_2nd.tif"
        folder_store, file = path.split(file_im)
        # Get the template file from the folder
        template_file = glob(folder_store + "\\square_template*.tif")
        print('find FIB Square 2 \n')
        self.assertTrue(findSquare2(file_im,template_file[0],tag))

    def test_find_Detector_Works(self):
        file_im = "test_images\\Trench.tif"
        tag = "ESB_any_date"
        print("Detector Works \n")
        self.assertTrue(detectorWorks(file_im,tag))

class AutomatonTrenchTestCase(unittest.TestCase):
    def test_find_Trench(self):
        file_im = "test_images\\Trench_5.tif"
        file_im_before = "test_images\\Trench_5_before.tif"
        tag = "ESB_any_date"
        # file_im_before = "D:\GOLGI\\13_November_2017\\FIRST_PART\\My_Project\\4Q_field--X03--Y20_0041___0003\\ESB_0-2018-04-22_02-59-55-.tif"
        # file_im = "D:\GOLGI\\13_November_2017\\FIRST_PART\\My_Project\\4Q_field--X03--Y20_0041___0003\\ESB_0-2018-04-22_03-34-57-.tif"
        # file_im_before = "test_images\\Trench_4_before.tif"
        # file_im = "test_images\\Trench_4.tif" #  "test_images\\Trench_4_SESI.tif"
        tag = "ESB"
        print("Find Trench \n")
        self.assertTrue(saveTrenchPoints(file_im_before,file_im,tag))


class AutomatonFocusPointsTestCase(unittest.TestCase):
    def test_detectPointsFile(self):
        # file_im = "test_images\\FocusTest4.tif"
        file_im = "test_images\\FocusTest2.tif"
        #file_im ="D:\\INES\\My_Project06052018\\7V_03___0002\\7V_03___0002__acq\\slicecell__00302_z=5.9851um.tif"
        # file_im = 'D:\\GOLGI\\PR_3Mar2017\\My_Project\\1O_field--X00--Y24_0010___0029\\Focus_Points_0-2017-04-04_08-45-27-.tif'
        # file_im = "D:\\GOLGI\\PR_27Mar2017\\PR_27Mar\\6P_field--X01--Y29_0021___0004\\PR_27Mar_6P_field--X01--Y29_0021___0004\\slicecell__00054_z=5.3875um.tif"
        tag = "fp_any"
        start = time.time()
        print("Detect focus points \n ")
        self.assertTrue(detectPointsFile(file_im,tag,remove_black = True))
        end = time.time()
        print(end - start)

class AutomatonDetectCell(unittest.TestCase):
    def test_checkFeaturesPositive(self):
        file_im = "test_images\\TestFace_Positive.tif"
        tag = "testFace"
        print("CheckFeatures Positive \n")
        self.assertTrue(checkFeatures(file_im,tag))

    def test_checkFeaturesNegative(self):
        file_im = "test_images\\TestFace_Negative.tif"
        tag = "testFace"
        print("CheckFeatures Negative \n")
        self.assertFalse(checkFeatures(file_im, tag))

    def test_getCell(self):
        file_im ="test_images\\sample\\slicecell__00002_z=0.5755um.tif"
        tag = "testImages"
        cell = getCell(file_im)
        print("Get Cell contour")
        self.assertTrue(True)



class AutomatonRunCheckerTestCase(unittest.TestCase):
    def test_OnlineAF(self):
        file_im = "D:\\GOLGI\\14Nov_NOSPOTS\\Project_InfinityWar\\2J_field--X01--Y04_0016--003___0011\\2J_field--X01--Y04_0016--003___0011__acq\\slicecell__00004_z=0.5761um.tif"
       # file_im = "D:\\GOLGI\\13_July_2018\\My_Project_halloween\\8P_field--X03--Y23_0036--001___0014\\8P_field--X03--Y23_0036--001___0014__acq\\slicecell__00010_z=1.7398um.tif"
       # file_im = "D:\\GOLGI\\13_July_2018\\My_Project_halloween\\9N_field--X03--Y19_0033___0016\\9N_field--X03--Y19_0033___0016__acq\\slicecell__00056_z=10.9504um.tif"
        tag = "r655672415"
        my_dir = path.dirname(path.realpath(__file__))
        preferences_file = my_dir + '\\fromMSite\\user.pref'

        with open(preferences_file) as f:
            preferences = json.load(f)

        rep = Reporter(file_im,tag, preferences)
        rep.runCheck()

#class AutomatonTrackingTestCase(unittest.TestCase):
#    def test_SIFT(self):

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(AutomatonCPTestCase))
  # test_suite.addTest(unittest.makeSuite(AutomatonFocusPointsTestCase))
  # test_suite.addTest(unittest.makeSuite(AutomatonRunCheckerTestCase))
  # test_suite.addTest(unittest.makeSuite(AutomatonTrenchTestCase))
    return test_suite

mySuit=suite()
runner=unittest.TextTestRunner()
runner.run(mySuit)


# if __name__ == '__main__':
    # unittest.main()


