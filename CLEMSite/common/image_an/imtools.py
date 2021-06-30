import glob
import os
import re
import sys

import cv2
import numpy as np
from matplotlib import pyplot as plt
import warnings

from common.image_an.readers import getInfoHeader,getInfoHeaderAtlas

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )


def mad(data):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variabililty of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation
    """
    data = np.ma.array(data).compressed()  # should be faster to not use masked arrays.
    med = np.median(data)
    return np.median(np.abs(data - med))

def getPixelSize(inputReference_path, atlas= False):
    if(atlas):
        infoRef = getInfoHeaderAtlas(inputReference_path)
    else:
        infoRef = getInfoHeader(inputReference_path)
    return infoRef['PixelSize']

def getFOV(inputReference_path, atlas= False):
    if(atlas):
        infoRef = getInfoHeaderAtlas(inputReference_path)
    else:
        infoRef = getInfoHeader(inputReference_path)
        infoRef['FOV_X'] = infoRef['PixelSize']*1024 # get image size
    return infoRef['FOV_X']

def blendImagesFile(im1_f,im2_f):

    # Get metadata from images
    info1 = getInfoHeader(im1_f)
    info2 = getInfoHeader(im2_f)
    im1 = cv2.imread(im1_f)
    im2 = cv2.imread(im2_f)
    h,w,c = im1.shape
    pixsize1 = float(info1['PixelSize'])
    pixsize2 = float(info2['PixelSize'])

    if(pixsize1 < pixsize2):
        scale_factor = float(info1['PixelSize']) / float(info2['PixelSize'])
        w_s = int(w*scale_factor)
        h_s = int(h*scale_factor)
        crop_img = im2[int(w*0.5-w_s*0.5):int(w*0.5+w_s*0.5), int(h*0.5-h_s*0.5):int(h*0.5+h_s*0.5)]
        im2= cv2.resize(crop_img, (w, h))
    elif (pixsize1 > pixsize2):
        scale_factor = float(info2['PixelSize']) / float(info1['PixelSize'])
        w_s = int(w*scale_factor)
        h_s = int(h*scale_factor)
        crop_img = im1[int(w*0.5-w_s*0.5):int(w*0.5+w_s*0.5), int(h*0.5-h_s*0.5):int(h*0.5+h_s*0.5)]
        im1= cv2.resize(crop_img, (w, h))
    else:
       pass
    # Auto BC im1
    im1= cv2.convertScaleAbs(im1, alpha=(255.0 / np.max(im1)))
    # Auto BC im2
    im2 = cv2.convertScaleAbs(im2, alpha=(255.0 / np.max(im2)))
    # blend channels
    # create image to save
    img_out = []
    img_out = cv2.addWeighted(im1, 0.5, im2, 0.5, 1)
    im3 = cv2.convertScaleAbs(img_out, alpha=(255.0 / np.max(img_out)))

    return im3

def blendImages(im1,im2):
    h,w,c = im1.shape
    # Auto BC im1
    im1 = cv2.convertScaleAbs(im1, alpha=(255.0 / np.max(im1)))
    # Auto BC im2
    im2 = cv2.convertScaleAbs(im2, alpha=(255.0 / np.max(im2)))
    # blend channels
    # create image to save
    img_out = []
    img_out = cv2.addWeighted(im1, 0.5, im2, 0.5, 1)
    im3 = cv2.convertScaleAbs(img_out, alpha=(255.0 / np.max(img_out)))
    return im3

def saveImageSEM(new_image_name,im2):
    # flip
    rimg = cv2.flip(im2, 1)
    # save
    cv2.imwrite(new_image_name,rimg)

def getFiles(folder,pattern):
    directories = glob.glob(folder + '\*')
    xd = filterPick(directories, pattern)
    return [ directories[el] for el in xd ]


def getImages(folder,pattern):
    warnings.warn("Function getImages deprecated", DeprecationWarning)
    return getFiles(folder, pattern)

def filterPick(myList, myString):
    pattern = re.compile(myString);
    indices = [i for i, x in enumerate(myList) if pattern.search(x)]
    return indices

def max_int_Z_projection(listimages):
    im1 = cv2.imread(listimages[0])
    final_im = np.zeros(im1.shape,dtype=np.uint8)
    if (len(listimages) > 2):
        for ind in range(0,len(listimages)):
            im2 = cv2.imread(listimages[ind])
            cv2.max(im1,im2, final_im)
            im1 = final_im.astype(np.uint8)
    # Preserve metadata

    return final_im

def filterImg(img):
    img = img - np.mean(img)
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    # magnitude_spectrum = 20*np.log(np.abs(fshift))
    im_rc = fshift.shape
    center = [im_rc[0]*0.5,im_rc[1]*0.5]
    top_x = [center[1] - 0.05 * im_rc[0], center[1] + 0.05 * im_rc[0]]
    top_y = [center[0] - 0.05 * im_rc[1], center[0] + 0.05 * im_rc[1]]
    fshift[0:top_x[0], :]=0
    fshift[top_x[1]:im_rc[0],:]=0
    fshift[:,0:top_y[0]]=0
    fshift[:,top_y[1]:im_rc[1]]=0

    # shift back (we shifted the center before)
    f_ishift = np.fft.ifftshift(fshift)
    # inverse fft to get the image back
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back) + np.mean(img)
    img_back = cv2.equalizeHist(np.array(img_back,dtype = np.uint8))
    plt.subplot(121),plt.imshow(img, cmap = 'gray')
    plt.title('Input Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(img_back, cmap = 'gray')
    plt.title('After filter'), plt.xticks([]), plt.yticks([])
    plt.show()

#imagefile ="C:\\Projects\\Correlative\\Confocal Experiments\\20160803_golgi_phenotypes\\renamed\hr\\field--X00--Y10_0004\\grid_0004_3--LM--RL - Reflected Light--10x--z1.tif"
#img = cv2.imread(imagefile,0)
#filterImg(img)

#numer = "0003"
#date = "2016_05_02_09_10_13_"
#im1 = "C:\\Test\\auto_final\\auto-mai\\experiment--"+date+numer+"\\auto_april_golgi_"+numer+"_1--LM--GFP--10x--z2.tif"
#im2 = "C:\\Test\\auto_final\\auto-mai\\experiment--"+date+numer+"\\auto_april_nucleus_"+numer+"_1--LM--DAPI--10x--z2.tif"
#im3 = "C:\\Test\\auto_final\\auto-mai\\experiment--"+date+numer+"\\auto_april_grid_"+numer+"_1--LM--RL - Reflected Light--10x--z2.tif"
#im3 = "C:\\Test\\auto_final\\auto-mai\\experiment--"+date+numer+"\\SEMt.tif"

#im13 = blendImagesFile(im3,im1)
#im2c = cv2.imread(im2)
#im12 = blendImages(im13,im2c)
#im12 = blendImages(im1,im2)
#im123 = blendImages(im12,im3)
#im123_f = "C:\\Test\\auto_final\\auto-mai\\experiment--"+date+numer+"\\auto_golgi_"+numer+"_inverted_composite.tif"
#im123_f = "C:\\Test\\auto_final\\auto-mai\\experiment--"+date+numer+"\\auto_golgi_"+numer+"_inverted_composite_SEM.tif"
#saveImageSEM(im123_f,im123)
#
# folder = "C:\\Users\\JMS\\Documents\\msite\\MSite\\msiteSEM\\image_an\\"
# pattern ="image--L0000--S00--U00--V00--J20--E02--O00--X00--Y00--T0000--Z.*--C01.ome.tif"
# im_list = getImages(folder,pattern)
# image = max_int_Z_projection(im_list)
# new_image_name = folder+"\\Z_stack.tif"
# cv2.imwrite(new_image_name,image)
