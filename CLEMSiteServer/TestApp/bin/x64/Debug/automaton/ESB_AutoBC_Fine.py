
import cv2
import sys
import numpy as np
from os import path
import time
import math
from scipy.stats import norm
from scipy.stats import expon
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab



def calculateSaturation(im_1):
    # Sample the diagonal of the image without the borders
    h, w = im_1.shape
    diag = math.sqrt(h * h + w * w)
    start = 0.2 * diag
    end = diag - start
    im_crop = im_1[start:end, start:end]
    h1, w1 = im_crop.shape
    m_signal = []
    for i, j in zip(range(0, h1), range(0, w1)):
        if(i==j):
            m_signal.append(im_crop[i, j])

    # Find number of saturations in white
    count = 0
    n_sat_white = []
    n_sat_black = []
    for pixel in m_signal:
        if (pixel == 255 or pixel == 254):
            count += 1
        else:
            if (count > 0):
                n_sat_white.append(count)
            count = 0

    # Find number of saturations in black
    count = 0
    for pixel in m_signal:
        if (pixel == 0 or pixel == 1):
            count += 1
        else:
            if (count > 0):
                n_sat_black.append(count)
            count = 0

    plt.plot(m_signal)
    plt.show()
    print("WHITE")
    print(str(np.mean(n_sat_white),np.var(n_sat_white)))
    print("BLACK")
    print(np.mean(n_sat_black),np.var(n_sat_black))
    print("**-**")



# Two ways of calculating histograms
#hist = cv2.calcHist([img],[0],None,[256],[0,256])
# hist,bins = np.histogram(img.ravel(),256,[0,256])

from math import log

def get_histogram_dispersion(histogram):
    log2 = lambda x:log(x)/log(2)

    total = len(histogram)
    counts = {}
    for item in histogram:
        counts.setdefault(item,0)
        counts[item]+=1

    ent = 0
    for i in counts:
        p = float(counts[i])/total
        ent-=p*log2(p)
    return -ent*log2(1/ent)

# file_im = sys.argv[1]
#tag = sys.argv[2]
file_im = "C:\\Users\\JMS\\Desktop\\Planets_v2\\My_Project_Hulk\\NO_ID_9091___0000\\bc_esb\\ESB_Trench_0-2016-06-29_11-59-58-.tif"
file_im2 = "grabbed__201605111747140590.tif"
#0file_im3 = "tESBBC_47_47.tif"
tag = "image"
# Get folder
folder_store,file = path.split(file_im)



im_1 = cv2.imread(file_im,cv2.IMREAD_GRAYSCALE)
ret,th = cv2.threshold(im_1,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)


gray = np.float32(im_1)
dst = cv2.cornerHarris(gray,2,3,0.04)

#result is dilated for marking the corners, not important
dst = cv2.dilate(dst,None)

# Threshold for an optimal value, it may vary depending on the image.
im_1[dst>0.01*dst.max()]=[0,0,255]

cv2.imshow('dst',im_1)
# calculateSaturation(im_1)
im_2 = cv2.imread(file_im2,cv2.IMREAD_GRAYSCALE)
#calculateSaturation(im_2)
#im_3 = cv2.imread(file_im3,cv2.IMREAD_GRAYSCALE)
#calculateSaturation(im_3)

hist1,bins = np.histogram(im_1.ravel(),256,[0,256])


n, bins, patches = plt.hist(im_1.ravel(),256,fc='k', ec='k')
plt.show()

data1 = get_histogram_dispersion(im_1.ravel())

hist2,bins = np.histogram(im_2.ravel(),256,[0,256])

n, bins, patches = plt.hist(im_2.ravel(),256,fc='k', ec='k')
plt.show()

data2 = get_histogram_dispersion(im_2.ravel())

hist3,bins = np.histogram(im_3.ravel(),256,[0,256])

n, bins, patches = plt.hist(im_3.ravel(),256,fc='k', ec='k')
plt.show()

hist_A = hist1-hist2
hist_B = hist3-hist2
# (mu,sigma)= norm.fit(hist_B)

# the histogram of the data
n, bins, patches = plt.hist(hist_A,100,facecolor='green', alpha=0.75)
plt.show()
n, bins, patches = plt.hist(hist_B,100,facecolor='blue', alpha=0.75)
# add a 'best fit' line
#y = mlab.normpdf( bins, mu, sigma)
#l = plt.plot(255, y, 'r--', linewidth=2)

plt.show()
# param1=expon.fit(im_1b.ravel())
# mean, var = expon.stats(loc=param[0],scale=param[1],moments='mv')
