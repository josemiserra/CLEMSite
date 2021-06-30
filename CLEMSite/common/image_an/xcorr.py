
import matplotlib.pyplot as plt
import cv2
# http://scikit-image.org/docs/dev/auto_examples/transform/plot_register_translation.html
from skimage.feature import register_translation
# from skimage.feature.register_translation import _upsampled_dft
# from scipy.ndimage import fourier_shift
from skimage import data, io, filters
from skimage.morphology import watershed
from skimage.feature import peak_local_max
from scipy import ndimage
import numpy as np
from skimage.feature import match_template
from scipy.ndimage import fourier_shift
import os
from PyQt5 import QtCore, QtGui


from common.image_an.readers import getInfoHeader

def _tile_plot(imgs, titles, **kwargs):
    """
    Helper function
    """
    # Create a new figure and plot the three images
    fig, ax = plt.subplots(1, len(imgs))
    for ii, a in enumerate(ax):
        a.set_axis_off()
        a.imshow(imgs[ii], **kwargs)
        a.set_title(titles[ii])

    return fig

def overlay_images(img0, img1, title0='', title_mid='', title1='', fname=None):
    r""" Plot two images one on top of the other using red and green channels.
    Creates a figure containing three images: the first image to the left
    plotted on the red channel of a color image, the second to the right
    plotted on the green channel of a color image and the two given images on
    top of each other using the red channel for the first image and the green
    channel for the second one. It is assumed that both images have the same
    shape. The intended use of this function is to visually assess the quality
    of a registration result.
    Parameters
    ----------
    img0 : array, shape(R, C)
        the image to be plotted on the red channel, to the left of the figure
    img1 : array, shape(R, C)
        the image to be plotted on the green channel, to the right of the
        figure
    title0 : string (optional)
        the title to be written on top of the image to the left. By default, no
        title is displayed.
    title_mid : string (optional)
        the title to be written on top of the middle image. By default, no
        title is displayed.
    title1 : string (optional)
        the title to be written on top of the image to the right. By default,
        no title is displayed.
    fname : string (optional)
        the file name to write the resulting figure. If None (default), the
        image is not saved.
    """
    # Normalize the input images to [0,255]


    # Create the color images
    img0_red = np.zeros(shape=(img0.shape) + (3,), dtype=np.uint8)
    img1_green = np.zeros(shape=(img0.shape) + (3,), dtype=np.uint8)
    overlay = np.zeros(shape=(img0.shape) + (3,), dtype=np.uint8)

    # Copy the normalized intensities into the appropriate channels of the
    # color images
    img0_red[..., 0] = img0
    img1_green[..., 1] = img1
    overlay[..., 0] = img0
    overlay[..., 1] = img1

    fig = _tile_plot([img0_red, img1_green, overlay],
                     [title0, title1, title_mid])

    # If a file name was given, save the figure
    if fname is not None:
        fig.savefig(fname, bbox_inches='tight')

    return fig



def processNuclei(i_image):
    ## Computing threshold on the maximum intensity projection with `threshold_otsu`
    i_image = cv2.GaussianBlur(i_image, (3, 3), 1.2)  # 5,5
    ret, th = cv2.threshold(i_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # noise removal
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=2)
    # sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=2)
    sure_fg = cv2.erode(opening,kernel,iterations=2)

    # Finding sure foreground area
    # compute the exact Euclidean distance from every binary
    # pixel to the nearest zero pixel, then find peaks in this
    # distance map
    dist_transform = ndimage.distance_transform_edt(th)
    # perform a connected component analysis on the local peaks,
    # using 8-connectivity, then apply the Watershed algorithm
    markers = ndimage.label(sure_fg, structure=np.ones((3, 3)))[0]
    labels = watershed(-dist_transform, markers, mask=sure_bg)
    labels[labels>0]=255
    return labels


def plot_overlay(imageRef, template, center, top_left, bottom_right,fname = None):
    overlay = np.zeros(shape=(imageRef.shape) + (3,), dtype=np.uint8)
    cv2.circle(imageRef, (int(center[0]),int(center[1])), 5, (255, 255, 255), 2)
    cv2.rectangle(imageRef,top_left, bottom_right, 255, 2)
    imageTemp = np.zeros(shape=(imageRef.shape), dtype=np.uint8)
    imageTemp[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = template
    overlay[..., 0] = imageRef
    overlay[..., 1] =imageTemp
    plt.ion()
    fig, ax = plt.subplots()
    ax.imshow(overlay)
    if fname is not None:
        fig.savefig(fname, bbox_inches='tight')

    return fig


def findShift(inputReference_path, inputShifted_path, center_obj=None, tag=None, extraimg_path=None):
    # Get metadata from images
    infoRef = getInfoHeader(inputReference_path)
    infoCorr = getInfoHeader(inputShifted_path)
    # Check the biggest
    if (infoRef['PixelSize'] > infoCorr['PixelSize']):
        # Crop image from center of BIG
        imageRef = cv2.imread(inputReference_path, 0)
        cv2.normalize(imageRef, imageRef, np.min(imageRef), np.max(imageRef), norm_type=cv2.NORM_MINMAX)
        imageCorr = cv2.imread(inputShifted_path, 0)
        cv2.normalize(imageCorr, imageCorr, np.min(imageCorr), np.max(imageCorr), norm_type=cv2.NORM_MINMAX)
    else:
        # Crop image from center of BIG
        imageRef = cv2.imread(inputShifted_path, 0)
        cv2.normalize(imageRef, imageRef, np.min(imageRef), np.max(imageRef), norm_type=cv2.NORM_MINMAX)
        imageCorr = cv2.imread(inputReference_path, 0)
        cv2.normalize(imageCorr, imageCorr, np.min(imageCorr), np.max(imageCorr), norm_type=cv2.NORM_MINMAX)

    h, w = imageCorr.shape
    scale_factor = float(infoCorr['PixelSize']) / float(infoRef['PixelSize'])
    w_s = int(w * scale_factor)
    h_s = int(h * scale_factor)
    template = cv2.resize(imageCorr, (w_s, h_s))
    res = cv2.matchTemplate(imageRef, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w_s, top_left[1] + h_s)
    # crop_img = imageRef[top_left[1]:bottom_right[1],top_left[0]:bottom_right[0]]  # Crop from x, y, w, h -> 100, 200, 300, 400
    # shift, error, diffphase = register_translation(crop_img, template, int(1 / scale_factor))
    shift = np.array([0.0, 0.0], dtype=np.float32)
    center = (top_left[0] + w_s * 0.5 + shift[0], top_left[1] + h_s * 0.5 + shift[1])
    # plot_overlay(imageRef, template, center, top_left, bottom_right)
    hr, wr = imageRef.shape

    scale_shift = shift * infoRef['PixelSize']
    return shift, scale_shift;

def xcorr(image1_path,image2_path):
    image = cv2.imread(image1_path,0)
    image = filters.sobel(image)
    offset_image = cv2.imread(image2_path,0)
    offset_image= filters.sobel(offset_image)
    # pixel precision first
    #shift, error, diffphase = register_translation(image, offset_image)
    # print("Detected pixel offset (y, x):")
    #print(shift)
    # subpixel precision
    shift, error, diffphase = register_translation(image, offset_image, 100)

    print("Shift computed:"+str(shift))
    print("Expected error: "+str(error))
    return shift

def findShiftWindow(inputReference_path, inputTemplate_path, extraimg_path = None, center_obj=None ):
    # Get metadata from images
    infoRef = getInfoHeader(inputReference_path)
    infoTemp = getInfoHeader(inputTemplate_path)
    # Check the biggest
    if (infoRef['PixelSize'] > infoTemp['PixelSize']):
        # Crop image from center of BIG
        imageRef = cv2.imread(inputReference_path, 0)
        imageRef = cv2.normalize(imageRef, imageRef, np.min(imageRef), np.max(imageRef), norm_type=cv2.NORM_MINMAX)
        imageTemp = cv2.imread(inputTemplate_path, 0)
        imageTemp = cv2.normalize(imageTemp, imageTemp, np.min(imageTemp), np.max(imageTemp), norm_type=cv2.NORM_MINMAX)
    else:
        return -1

    h, w = imageTemp.shape
    scale_factor = float(infoTemp['PixelSize']) / float(infoRef['PixelSize'])
    w_s = int(w * scale_factor)
    h_s = int(h * scale_factor)
    template = cv2.resize(imageTemp, (w_s, h_s))
    res = cv2.matchTemplate(imageRef, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w_s, top_left[1] + h_s)
    crop_img = imageRef[top_left[1]:bottom_right[1],
               top_left[0]:bottom_right[0]]  # Crop from x, y, w, h -> 100, 200, 300, 400
    shift, error, diffphase = register_translation(crop_img, template, int(1 / scale_factor))
    # print("Detected extra pixel offset (y, x):")
    if (extraimg_path):
        extraimg = cv2.imread(extraimg_path, 0)
        crop_img = extraimg[top_left[1]:bottom_right[1],top_left[0]:bottom_right[0]]  # Crop from x, y, w, h -> 100, 200, 300, 400

    bbox_template = [top_left[1],bottom_right[1],top_left[0],bottom_right[0]]
    center = (top_left[0] + w_s * 0.5 + shift[0], top_left[1] + h_s * 0.5 + shift[1])
    # plot_overlay(imageRef, template, center, top_left, bottom_right)


   # offset_image = fourier_shift(np.fft.fftn(template), shift)
   # offset_image = np.fft.ifftn(offset_image)
   # overlay_images(crop_img,offset_image.real,'Reference image','Offset image','Overlay')

    if (center_obj is None):
        center_obj = center
    else:
        # These are coordinates from the template
        # First we scale them
        center_obj = np.array(center_obj * scale_factor, dtype=np.int)
        center_obj = np.array([center_obj[0] + center[0] - w_s * 0.5, center_obj[1] + center[1] - h_s * 0.5],
                              dtype=np.int)

    return shift, center_obj, bbox_template, crop_img

def main():
        #im1_path ="C:\\Test\\auto_final\\auto_april\\experiment--2016_04_21_14_04_10_0019\\auto_april_golgi_0019_1--LM--GFP--10x--z2.tif"
        #im2_path ="C:\\Test\\auto_final\\auto_april\\experiment--2016_04_21_14_04_10_0019\\auto_april_golgi_0019_1--LM--GFP--40x--z5.tif"

#        im1_path = "C:\\Test\\auto_final\\auto_april\\experiment--2016_04_21_13_19_37_0011\\auto_april_golgi_0011_1--LM--GFP--10x--z2.tif"
#        im2_path = "C:\\Test\\auto_final\\auto_april\\experiment--2016_04_21_13_19_37_0011\\auto_april_golgi_0011_1--LM--GFP--40x--z5.tif"

        im1_path = "C:\\Users\\Schwab\\AppData\\Local\\Temp\\tmpil62iq\\pic_1_0_201703131126248922.tif"
        im2_path = "C:\\Users\\Schwab\\AppData\\Local\\Temp\\tmpil62iq\\pic_2_0_201703131126464064.tif"

        shift = xcorr(im1_path, im2_path)



if __name__ == "__main__":
            main()