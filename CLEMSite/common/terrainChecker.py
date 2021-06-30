
import numpy as np
import cv2

import tensorflow as tf
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization, \
    GlobalAveragePooling2D
from os import listdir
from os.path import isfile, join
from keras.models import model_from_json
from skimage.filters.rank import enhance_contrast_percentile
from skimage.morphology import disk

class terrainChecker():
    """
      MODEL CONDITIONS:
         Binary classifier of 256 by 256 images.
         Preprocessing conditions can be modified by the preprocess.


    """
    model = []

    def __init__(self,iarchitecture,iweights):
        self.graph = tf.Graph()
        self.session = tf.compat.v1.Session(graph=self.graph)
        self.loadModel(iarchitecture,iweights)

    def loadModel(self,architecture,weights):
        json_file = open(architecture,'r')
        json_model = json_file.read()
        json_file.close()
        with self.graph.as_default():
            with self.session.as_default():
                self.model = model_from_json(json_model)
                self.model.load_weights(weights)
        return


    def preprocess(self,img):
        nimg = cv2.GaussianBlur(img, (5, 5), 0)
        # iclahe = cv2.createCLAHE(clipLimit=0.01, tileGridSize=(32, 32))
        # n_image = iclahe.apply(np.uint8(n_image))
        # Local contrast enhancement
        nimg = enhance_contrast_percentile(nimg, disk(3), p0=.1, p1=.9)
        return nimg


    def checkTerrain(self,iimage_path):
        """
        It is important to consider that
            0 - Means we are INSIDE the terrain
            1 - Means we are OUT

        :param iimage_path:
        :return:
        """
        n_image = cv2.imread(iimage_path, 0)
        if n_image is not None:
            nimg = self.preprocess(n_image)
            image = cv2.resize(nimg, (256, 256))
            # If 90% of image is black or white, return False
            if np.mean(image)<20 or np.mean(image)>240:
                return -1
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            image = ((np.array(image, dtype=np.float32)-127.)/128.)
            im_test = image.reshape(1, 256, 256,3)
            with self.graph.as_default():
                with self.session.as_default():
                    probabilities = self.model.predict(im_test)

            if(probabilities[0][0]<probabilities[0][1]): # or equivalently np.argmax(probabilities) == 1, means it is out
                return -2
            return 0
        else:
            return -100