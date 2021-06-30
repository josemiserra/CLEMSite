
import sys
import time
import math
from scipy.signal  import convolve2d
from scipy.ndimage import label,sum
from scipy.misc import imrotate
from matplotlib import pyplot as plt
from skimage import morphology
from skimage.segmentation import slic
# from bwmorph import bwmorph_thin
from collections import deque
import glob
import re
import csv
from time import gmtime, strftime
import cv2
import matplotlib.pyplot as plt
import numpy as np
from readers import getInfoHeader,getInfoHeaderAtlas
import math
from scipy.signal  import convolve2d
from os import path
import os
import re


def save_to_csv(file_path,my_list):
    with open(file_path, 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(my_list)

def writeErrorFile(message,folder_to_save):
    cdate = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
    file_data = folder_to_save + "\\error"+cdate+".txt"
    with open(file_data, 'w') as f:
        f.write(message)

def gaussfilt(img, sigma):
    sze = int(math.ceil(6 * sigma))
    if (sze % 2 == 0):
        sze = sze + 1
    h = fspecial_gauss2D((sze, sze), sigma)
    # conv2(image, mask) is the same as filter2(rot90(mask,2), image)
    image = convolve2d(img, h, 'same')
    return image

def fspecial_gauss2D(shape=(3,3),sigma=0.5):
    """
        2D gaussian mask - should give the same result as MATLAB's
        fspecial('gaussian',[shape],[sigma])
    """
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
            h /= sumh
    return h

def getImages(folder,pattern):
    directories = glob.glob(folder + '\*')
    xd = filterPick(directories, pattern)
    return [ directories[el] for el in xd ]

def derivative5(i_image):
        # 5 tap 1st derivative cofficients.  These are optimal if you are just
        # seeking the 1st derivatives
        # Copyright (c) 2010 Peter Kovesi
        p = np.array([0.037659, 0.249153, 0.426375, 0.249153, 0.037659], dtype=np.float32)
        d1 = np.array([0.109604, 0.276691, 0.000000, -0.276691, -0.109604], dtype=np.float32)

        a = p[:, np.newaxis] * d1.transpose()
        b = d1[:, np.newaxis] * p.transpose()
        Ix = convolve2d(i_image, a, 'same')
        Iy = convolve2d(i_image, b, 'same')
        return Ix, Iy

def canny(i_image, isigma):
        image = gaussfilt(i_image, isigma)
        Ix, Iy = derivative5(image)
        Ix_2 = np.multiply(Ix, Ix)
        Iy_2 = np.multiply(Iy, Iy)
        gradient = np.sqrt(Ix_2 + Iy_2)  # Gradient magnitude.
        orientation = np.arctan2(-Iy, Ix)  # Angles -pi to + pi.
        orientation[orientation < 0] = orientation[orientation < 0] + np.pi;  # Map angles to 0-pi.
        orientation = orientation * 180 / np.pi;
        return gradient, orientation



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
            return ""
    # List of files
    files_to_check = []
    for el in x:
        files_to_check.append(path.join(m_folder,onlyfiles[el]))
        # Get the filename of the image
    files_to_check.sort(key=lambda x: os.path.getmtime(x))
    return files_to_check


def integral_image(x):
    """Integral image / summed area table.

    The integral image contains the sum of all elements above and to the
    left of it, i.e.:

    .. math::

       S[m, n] = \sum_{i \leq m} \sum_{j \leq n} X[i, j]

    Parameters
    ----------
    x : ndarray
        Input image.

    Returns
    -------
    S : ndarray
        Integral image / summed area table.

    References
    ----------
    .. [1] F.C. Crow, "Summed-area tables for texture mapping,"
           ACM SIGGRAPH Computer Graphics, vol. 18, 1984, pp. 207-212.

    """
    return x.cumsum(1).cumsum(0)

def integrate(ii, r0, c0, r1, c1):
    """Use an integral image to integrate over a given window.

    Parameters
    ----------
    ii : ndarray
        Integral image.
    r0, c0 : int
        Top-left corner of block to be summed.
    r1, c1 : int
        Bottom-right corner of block to be summed.

    Returns
    -------
    S : int
        Integral (sum) over the given window.

    """
    S = 0

    S += ii[r1, c1]

    if (r0 - 1 >= 0) and (c0 - 1 >= 0):
        S += ii[r0 - 1, c0 - 1]

    if (r0 - 1 >= 0):
        S -= ii[r0 - 1, c1]

    if (c0 - 1 >= 0):
        S -= ii[r1, c0 - 1]

    return S


def plotHist(img):
    # hist,bins = np.histogram(img.flatten(),256,[0,256])

    plt.hist(img.flatten(),256,[0,256], color = 'r')
    plt.xlim([0,256])
    plt.legend(('cdf','histogram'), loc = 'upper left')
    plt.show()

def blackBorderDetection(im_slice):
    """


    :return:
    """
    if isinstance(im_slice,str):
        im_1 = cv2.imread(im_slice, cv2.IMREAD_GRAYSCALE)
    else:
        im_1 = im_slice

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
    im_crop = im_1[y:y + h, x:x + w]
    return im_crop,[x, y, w, h]

def getPixelSize(inputReference_path, atlas= False):
    if(atlas):
        infoRef = getInfoHeaderAtlas(inputReference_path)
    else:
        infoRef = getInfoHeader(inputReference_path)
    return infoRef['PixelSize']


def kuwahara_filter(input, winsize):
    # Kuwahara filters an image using the Kuwahara filter
    """
    filtered = Kuwahara(original, windowSize)
    filters the image with a given windowSize and yielsd the result in filtered
    It uses = variance = (mean of squares) - (square of mean).
    filtered = Kuwahara(original, 5);
    Description : The kuwahara filter workds on a window divide into 4 overlapping subwindows
    In each subwindow the mean and hte variance are computed. The output value (locate at the center of the window)
    is set to the mean of the subwindow with the smallest variance
    References:
    http: // www.ph.tn.tudelft.nl / DIPlib / docs / FIP.pdf
    http: // www.incx.nec.co.jp / imap - vision / library / wouter / kuwahara.html
    :param input:
    :param winsize:
    :return:
    """
    input = np.array(input, dtype=np.float64)
    m, n = input.shape
    if (winsize % 4) != 1:
        return

    tmpAvgKerRow = np.concatenate((np.ones((1, (winsize - 1) / 2 + 1)), np.zeros((1, (winsize - 1) / 2))), axis=1)
    tmpPadder = np.zeros((1, winsize));
    tmpavgker = np.matlib.repmat(tmpAvgKerRow, (winsize - 1) / 2 + 1, 1)
    tmpavgker = np.concatenate((tmpavgker, np.matlib.repmat(tmpPadder, (winsize - 1) / 2, 1)))
    tmpavgker = tmpavgker / np.sum(tmpavgker)

    # tmpavgker is a 'north-west'
    t1, t2 = tmpavgker.shape
    avgker = np.zeros((t1, t2, 4))
    avgker[:, :, 0] = tmpavgker  # North - west(a)
    avgker[:, :, 1] = np.fliplr(tmpavgker)  # North - east(b)
    avgker[:, :, 3] = np.flipud(tmpavgker)  # South - east(c)
    avgker[:, :, 2] = np.fliplr(np.flipud(tmpavgker))  # South - west(d)

    squaredImg = input ** 2
    avgs = np.zeros((m, n, 4))
    stddevs = np.zeros((m, n, 4))

    ## Calculation of averages and variances on subwindows
    for k in range(0, 4):
        avgs[:, :, k] = convolve2d(input, avgker[:, :, k], 'same')  # mean
        stddevs[:, :, k] = convolve2d(squaredImg, avgker[:, :, k], 'same')  # mean
        stddevs[:, :, k] = stddevs[:, :, k] - avgs[:, :, k] ** 2  # variance

    # minima = np.min(stddevs, axis=2)
    indices = np.argmin(stddevs, axis=2)
    filtered = np.zeros(input.shape)
    for k in range(m):
        for i in range(n):
            filtered[k, i] = avgs[k, i, indices[k, i]]

    return filtered