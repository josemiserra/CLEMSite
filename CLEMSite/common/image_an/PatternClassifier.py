
from common.image_an.imtools import *
import cv2
import numpy as np
import tensorflow as tf
from os import listdir
from os.path import join, isfile, split
from keras.models import model_from_json
import pandas as pd
import matplotlib.pyplot as plt
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

def softmax(y):
    s = np.exp(np.array(y,dtype=np.float64))
    y_prob = np.divide(s,np.sum(s),where=s>0)
    return y_prob

class PatternClassifier:
    my_letters = []

    def __init__(self, model_filename, model_weights_filename, occupancy_map):
        """"
            Loads the Keras model
        """

        #Classes
        self.patterns_list = [ el for el in  occupancy_map.getLabels() if ("*") not in el and not ("+") in el]
        self.oc_map = occupancy_map
        # Model
        try:
            with open(model_filename) as data_file:
                data = data_file.read()
        except FileNotFoundError:
            print("Model File Not found. Check preferences directory.")

        self.graph = tf.Graph()
        self.session = tf.compat.v1.Session(graph=self.graph)
        with self.graph.as_default():
            with self.session.as_default():
                self.model = model_from_json(str(data))
                self.model.load_weights(model_weights_filename)
                self.model._make_predict_function()

    def predictFrom(self,image_path,center_letter=None):
        patterns_subset = None
        if(center_letter):
            patterns_subset = self.oc_map.getNeighbors(center_letter)
        if isfile(image_path):
            if  image_path[-4:] == '.tif':
                image = self.path_to_tensor(image_path)
            else:
                return -1
        else:
            return -2
        tensor_image = np.expand_dims(image, axis=3)
        res = self.predictPattern(tensor_image,patterns_subset)
        return self.patterns_list[np.argmax(res)],np.max(softmax(res))

    def path_to_tensor(self,img_path):
        img = cv2.imread(img_path, 0)
        final = cv2.resize(img, (128, 128))
        final[-8:, :] = 0
        final[:, -8:] = 0
        final[:8, :] = 0
        final[:, :8] = 0
        final = np.array(final, dtype=np.float32)
        # convert 3D tensor to 4D tensor with shape (1, 128, 128, 1) and return 4D tensor
        return np.expand_dims(final, axis=0)


    def predictPattern(self,image_pattern, subset=[]):
        """
            Given a image and a model, converts to tensor and gives back the result of a prediction by the model.
            If a subset of the classes of the model is provided, puts to 0 all non-valid classes and re calculates
            probabilities using a softmax.
        """
        if subset:
            valid_tags = [el in subset for el in self.patterns_list]
            valid_tags = np.array(valid_tags, dtype=np.float32)
            non_valid_indexes = [ind for ind, el in enumerate(valid_tags) if el == 0.0]
            valid_indexes = [ind for ind, el in enumerate(valid_tags) if el != 0.0]
        with self.graph.as_default():
            with self.session.as_default():
                results = self.model.predict(image_pattern)[0]
        if subset:
            minimum_value = np.min(results[valid_indexes])  # normalization
            results[valid_indexes] = results[valid_indexes] - minimum_value
            results[non_valid_indexes] = 0.0
            results = softmax(results)
        return results



    def loadImages(self,folder):
        onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
        images_path = [join(folder, f) for f in onlyfiles if f[-4:] == '.tif']
        images_names = [f[:-4] for f in onlyfiles if f[-4:] == '.tif']
        tensors = self.paths_to_tensor(images_path)
        tensors = np.expand_dims(tensors, axis=3)
        return tensors, images_names

    def paths_to_tensor(self,img_paths):
        list_of_tensors = [self.path_to_tensor(img_path) for img_path in img_paths]
        return np.vstack(list_of_tensors)

    def fill_letters(self, idf, flip = False):
        if flip:
            topo = np.array([[4, 1, 5, 2], [7, 4, 8, 5], [3, 0, 4, 1], [6, 3, 7, 4]], dtype=np.int32)
        else:
            topo = np.array([[4, 7, 5, 8], [1, 4, 2, 5], [3, 6, 4, 7], [0, 3, 1, 4]], dtype=np.int32)
        letter_p = idf['letter']
        old_count = np.sum(letter_p.notnull())
        new_count = 0
        while np.any(letter_p.isnull()) and old_count!=new_count:
            old_count = np.sum(letter_p.notnull())
            m_groups = idf.groupby('group')
            for ind, m_group in m_groups:

                m_group = m_group.sort_values('dist').reset_index()
                # Swap values, sorting the two middle ones by x
                good_index = m_group.loc[[1, 2], :].sort_values('cx', ascending=False).index
                m_group.loc[[1, 2], :] = m_group.loc[good_index.tolist(), :].values
                indices = m_group.index.tolist()
                indices_original = np.array(m_group['index'])
                nan_values = m_group['letter'].isnull().tolist()
                if not nan_values[0]:
                    neighs = self.oc_map.getNeighbors(m_group.loc[indices[0],'letter'], N=1, complete_group = True )
                    idf.loc[indices_original, 'letter'] = [neighs[topo[0,0]],neighs[topo[0,1]],neighs[topo[0,2]],neighs[topo[0,3]]]
                elif not nan_values[1]:
                    neighs = self.oc_map.getNeighbors(m_group.loc[indices[1],'letter'], N=1,  complete_group = True )
                    idf.loc[indices_original, 'letter'] = [neighs[topo[1,0]],neighs[topo[1,1]],neighs[topo[1,2]],neighs[topo[1,3]]]
                elif not nan_values[2]:
                    neighs = self.oc_map.getNeighbors(m_group.loc[indices[2],'letter'], N=1,  complete_group = True )
                    idf.loc[indices_original, 'letter'] = [neighs[topo[2,0]],neighs[topo[2,1]],neighs[topo[2,2]],neighs[topo[2,3]]]
                elif not nan_values[3]:
                    neighs = self.oc_map.getNeighbors(m_group.loc[indices[3],'letter'], N=1,  complete_group = True )
                    idf.loc[indices_original, 'letter'] =  [neighs[topo[3,0]],neighs[topo[3,1]],neighs[topo[3,2]],neighs[topo[3,3]]]
            ### Do we have empty letters?
            duplicated_l = idf[idf.duplicated(['x', 'y'], keep=False)]
            ngroups = duplicated_l.groupby(['x','y'])
            ## Yes, then, get all duplicates. If a duplicate group has a letter, then copy the letter
            for ind, ngroup in ngroups:
                indices = ngroup.index.tolist()
                nan_values = ngroup['letter'].notnull().tolist()
                if(not np.all(nan_values)):
                    for ind,el in enumerate(nan_values):
                        if el:
                            letter = duplicated_l.loc[indices[ind],'letter']
                            idf.loc[indices,'letter'] = letter
            new_count = np.sum(idf['letter'].notnull())
            ## When no more duplicates, we have to do the round again

        return idf

    def predict_letters_from_picture(self, crop_points_path, image_path, folder_name, sample_data, flip = False):
        """
        Input : img_path = preprocessed image
                crop_points_path =list of cut points in csv point, x,y,index
                sample_data is a dictionary with the following codes
                    sample_data['orientation'] = angle to rotate
                    sample_data['ind_pattern'] = from all patterns in the image, which is the pattern that falls in the center
                    sample_data['e_pattern'] = expected letter from the pattern
                    sample_data['true_pattern'] = if the pattern is true or not, in that case, classification is ignored
        folder = folder to save the crops
        image = image to crop
        lop = list of points
            Format for cropping is at follows
            x,y,n

            x coordinate
            y coordinate
            n number of crop
        This function validates that we have a total of 4 points, and for each group,
        then crops the letters and saves them in a folder specified

        """
        folder_head, _ = split(image_path)
        # take folder from image and generate folder letters
        folder_to_save = folder_head+"\\"+folder_name
        if not os.path.exists(folder_to_save):
            os.makedirs(folder_to_save)

        # Read file csv to pandas dataframe
        try:
            df = pd.read_csv(crop_points_path, sep=',', names=['x', 'y','group','in','center_point'],skiprows=1)
        except pd.errors.EmptyDataError:
            print("Error parsing file: "+(crop_points_path))
            return None
        if df.index.shape[0] == 0:
            return None
        # x, y image coordinates of point
        # group is the group that they belong to (4 points make a cut group)
        # in defines if the point is valid or not. Can be used to crop, but not counted for transformations
        # center point says if the group has the middle point of the image, e.g. if the image is 512,512, the point 256,256
        # The user was previously asked to mark the letter associated to the middle point, so it is the main reference
        # df.columns = ['x', 'y','group','in','center_point'] # 'x', 'y', 'group_number', 'is_in_image', 'is_in_square'
        img_prepro = cv2.imread(image_path, 0)
        h, w = img_prepro.shape
        # The process is as follows. We have to rotate our image
        # so the character is perfectly perpendicular and oriented
        orientation = sample_data['orientation']
        # sample_data['e_pattern'] = sample_data['e_pattern'].upper()

        M = cv2.getRotationMatrix2D((w / 2, h / 2), orientation, 1)
        img_rot = cv2.warpAffine(img_prepro, M, (w, h))
        # To debug
        image_c = cv2.cvtColor(img_rot, cv2.COLOR_GRAY2BGR)
        # Now proceed with points
        group_rotated = []
        for index, group_points in df.iterrows():
            # check if point is valid
            xp = int(group_points[0])
            yp = int(group_points[1])
            cg = df.loc[index, 'group']
            # rotate points
            tmp = np.float32([xp, yp, 1.0])
            trh = np.dot(M, tmp.transpose())
            group_rotated.append((trh[0],trh[1]))

            df.loc[index,'cx_p'] = trh[0]
            df.loc[index,'cy_p'] = trh[1]
            x = int(round(trh[0]))
            y = int(round(trh[1]))
            df.loc[index,'cx'] = x
            df.loc[index,'cy'] = y
            if df.loc[index,'in'] == 1:
                cv2.circle(image_c, (x,y), 3, (0,0,255), -1)

        groups = df.groupby('group')
        images_to_eval = []
        groups_to_eval = []
        predict_friend = False
        if np.sum(df.loc[:,'center_point'])==0 :
            predict_friend = True


        for ind,group in groups:
            indices = group.index.tolist()
            x_values = np.array(group['cx'],dtype = np.int32)
            y_values = np.array(group['cy'],dtype = np.int32)
            dist_values = (np.sqrt(x_values ** 2 + y_values ** 2))
            df.loc[indices, 'dist'] = dist_values
            if (np.all(df.loc[indices, 'in'] > 0)):
                ind_min = np.argmin(dist_values)
                roi = img_rot[y_values[ind_min]:int(y_values[ind_min]+sample_data['distsq']), x_values[ind_min]:int(x_values[ind_min]+sample_data['distsq'])].copy()
                im_path = folder_to_save+"\\letter_"+str(ind)+".tif"
                images_to_eval.append(im_path)
                groups_to_eval.append(ind)
                cv2.imwrite(im_path,roi)
                if df.loc[indices[0],'center_point'] == 1:
                    if sample_data['true_pattern']:
                        prediction = sample_data['e_pattern']
                        if flip:

                            y_valn = (y_values - y_values[ind_min])
                            y_valn[ind_min] = np.max(y_values)
                            select_min_coord_ind = np.argmin(y_valn)
                        else:
                            select_min_coord_ind = np.logical_and(np.array(df['cx'] == x_values[ind_min]),
                                                                  np.array(df['cy'] == y_values[ind_min]))
                        df.loc[select_min_coord_ind, 'letter'] = prediction
                        df.loc[select_min_coord_ind, 'center_point'] = 2
                        os.rename(im_path, folder_to_save + "\\" + prediction + ".tif")
                    else:
                        prediction,prob = self.predictFrom(im_path, sample_data['e_pattern'])
                        if flip:
                            y_valn = (y_values - y_values[ind_min])
                            y_valn[ind_min] = np.max(y_values)
                            select_min_coord_ind = np.argmin(y_valn)
                        else:
                            select_min_coord_ind = np.logical_and(np.array(df['cx'] == x_values[ind_min]),
                                                                  np.array(df['cy'] == y_values[ind_min]))
                        df.loc[select_min_coord_ind, 'letter'] = prediction
                        df.loc[select_min_coord_ind, 'center_point'] = 2
                        try:
                            os.rename(im_path,folder_to_save+"\\"+prediction+".tif")
                        except OSError as e:
                            print("Something went wrong with your detection, two central points were detected")
                elif predict_friend:
                        prediction, prob = self.predictFrom(im_path, sample_data['e_pattern'])
                        if flip:
                            y_valn = (y_values - y_values[ind_min])
                            y_valn[ind_min] = np.max(y_values)
                            select_min_coord_ind = np.argmin(y_valn)
                        else:
                            select_min_coord_ind = np.logical_and(np.array(df['cx'] == x_values[ind_min]),
                                                                  np.array(df['cy'] == y_values[ind_min]))
                        df.loc[select_min_coord_ind, 'letter'] = prediction
                        os.rename(im_path, folder_to_save + "\\" + prediction + ".tif")
                        predict_friend = False

        df = self.fill_letters(df,flip)
        # Now drop the duplicates
        df = df.drop_duplicates(['letter']).reset_index(drop=True)
        ## Given the image size we have to annulate every possible point outside the image
        for i in range(len(df)):
            cx = df.loc[i]['cx']
            cy = df.loc[i]['cy']
            if(cx<0 or cy<0 or cx>w or cy>h):
                df.at[i, 'valid'] = 0

        ## Draw image with text
        font = cv2.FONT_HERSHEY_SIMPLEX
        for index, row_p in df.iterrows():
            if(df.loc[index]['in']==1):
                cv2.putText(image_c, row_p.letter, (int(row_p.cx), int(row_p.cy)), font, 1, (0, 255, 255), 2)
        cv2.imwrite( folder_to_save+"\\letters.tif", image_c)
        letters = [ str(el) for el in df['letter']]
        letters =[ el[0].lower()+el[1]   for el in letters ]
        df.loc[:,'letter'] = letters
        return df





# my_pclas = PatternClassifier()
# print(my_pclas.predictFrom("./test_images/3E_4.tif"))
# import time
# date = time.strftime("%d%m%Y-%H%M")
# sample_data = {}
# sample_data['orientation'] = -89
# sample_data['true_pattern'] = False
# sample_data['e_pattern'] = '3E'
# sample_data['distsq'] = 380  # pixel size * grid_size_big
# my_pclas.predict_letters_from_picture("D:\\GOLGI\\PR_13Jun2017\\renamed\\hr\\field--X00--Y00_0001\\ld_22-Aug-2017-1807\\field--X00--Y00_0001_cutpoints.csv", \
#                             "D:\\GOLGI\\PR_13Jun2017\\renamed\\hr\\field--X00--Y00_0001\\ld_22-Aug-2017-1807\\swt_field--X00--Y00_0001.tif", \
#                             "letters_"+date, sample_data)