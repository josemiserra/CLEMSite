import numpy as np
import cv2
from matplotlib import pyplot as plt

# Initiate STAR detector
star = cv2.FeatureDetector_create("STAR")

# Initiate BRIEF extractor
brief = cv2.DescriptorExtractor_create("BRIEF")


# print brief.getInt('bytes')

img = cv2.imread('D:\\DENMARK_PR\\SAMPLE_ONE_LM\\cell1\\EMBL_p1\\slicecell__00000_z=0.0000um.tif',0)
img2 = cv2.imread('D:\\DENMARK_PR\\SAMPLE_ONE_LM\\cell1\\EMBL_p1\\slicecell__00001_z=0.0048um.tif',0)



# find the keypoints with STAR
kp1 = star.detect(img,None)
kp2 = star.detect(img2,None)

# compute the descriptors with BRIEF
kp1, des1 = brief.compute(img, kp1)
kp2, des2 = brief.compute(img2, kp2)

#orb = cv2.ORB_create(patchSize = 101)
# find the keypoints and descriptors
# kp1, des1 = orb.detectAndCompute(img,None)
# kp2, des2 = orb.detectAndCompute(img2,None)


# FLANN parameters
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)   # or pass empty dictionary

flann = cv2.FlannBasedMatcher(index_params,search_params)

matches = flann.knnMatch(np.float32(des1),np.float32(des2),k=2)

# Need to draw only good matches, so create a mask
matchesMask = [[0,0] for i in xrange(len(matches))]

# ratio test as per Lowe's paper
for i,(m,n) in enumerate(matches):
    if m.distance < 0.7*n.distance:
        matchesMask[i]=[1,0]

draw_params = dict(matchColor = (0,255,0),
                   singlePointColor = (255,0,0),
                   matchesMask = matchesMask,
                   flags = 0)

img3 = cv2.drawMatchesKnn(img,kp1,img2,kp2,matches,None,**draw_params)

plt.imshow(img3,),plt.show()