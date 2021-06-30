#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import cv2
import sys
import numpy as np
import math
from os import path
from sklearn.cluster import KMeans
from scipy.ndimage import filters
from skimage.segmentation import slic, felzenszwalb
from skimage.filters.rank import enhance_contrast_percentile
from skimage.morphology import disk


import matplotlib.pyplot as plt
from imutils import writeErrorFile, gaussfilt

from skimage.morphology import erosion, dilation, opening, closing, white_tophat
from skimage.morphology import black_tophat, skeletonize, convex_hull_image
from skimage.morphology import disk
from scipy.ndimage import binary_fill_holes, binary_dilation, binary_opening, binary_erosion
from sklearn.neighbors import KDTree

def SLICthresholding2(img, max_value = 50, fill_holes = False):
    """"

    """
    rows, cols = img.shape
    #segments = felzenszwalb(img, scale=500, sigma=0, min_size=min(500, (rows * cols / 500)))
    #if total_slics == 1:
    segments = slic(img, n_segments=600, sigma=3, compactness=0.08, enforce_connectivity=True)
    total_slics = np.max(segments) + 1

    med_list = []
    # Sorting of indexes speeds ups the process of calculating median values
    flat = segments.ravel()
    lin_idx = np.argsort(flat, kind='mergesort')
    sp_ind = np.split(lin_idx, np.cumsum(np.bincount(flat)[:-1]))
    im_1b_f = img.ravel()
    centroids_list = []
    for i in range(total_slics):
        el_med = np.median(im_1b_f[sp_ind[i]])
        cx, cy = np.where(segments == i)
        centroid_x = np.mean(cx)
        centroid_y = np.mean(cy)
        centroids_list.append([centroid_x,centroid_y])
        med_list.append([el_med])

    centroids_list = np.array(centroids_list)

    k = KMeans(n_clusters=3)
    # K-Means and get 3 clusters,
    k.fit(med_list)
    centers = k.cluster_centers_
    paint_white = np.argmax(centers)
    paint_black = np.argmin(centers)
    w_avg = centers[paint_white]
    b_avg = centers[paint_black]
    if b_avg > max_value :
        b_avg = max_value

    nimg_f = img.ravel()
    white_img = np.zeros(nimg_f.shape)
    black_img = np.zeros(nimg_f.shape)
    gray_img = np.zeros(nimg_f.shape)

    white_ind = []

    for i in range(total_slics):
        m_m = np.mean(nimg_f[sp_ind[i]])
        if (k.labels_[i] == paint_white):
            white_img[sp_ind[i]] = 255
        elif (k.labels_[i] == paint_black  or  m_m < max_value):
            black_img[sp_ind[i]] = 255
        else:
            gray_img[sp_ind[i]] = 255

    if fill_holes:
        gray_img = binary_fill_holes(gray_img).astype(int)
        white_img = binary_fill_holes(white_img).astype(int)
        black_img = binary_fill_holes(gray_img).astype(int)
    return black_img.reshape(img.shape), white_img.reshape(img.shape), gray_img.reshape(img.shape)


def findRegions(iimg, max_value = 50, gsigma = 1.5):
    # White more white!!
    rows,cols = iimg.shape

    img = iimg.copy()
    h, w = iimg.shape
    r = 1.0
    if (h > 1024 and w > 1024):
        r = 1024.0 / w
        dim = (1024, int(h * r))
        # perform resizing to speed up
        rimg = cv2.resize(iimg, dim, interpolation=cv2.INTER_AREA)
    else:
        rimg = img

    rows, cols = rimg.shape
    im_1b = cv2.GaussianBlur(rimg, (21, 21), 0)
    nimg = np.array(im_1b)
    # Local contrast enhancement
    enh = enhance_contrast_percentile(nimg, disk(5), p0=.1, p1=.9)
    bim,wim,gim = SLICthresholding2(enh.copy(), max_value = max_value)


    th = binary_fill_holes(gim).astype(int)
    th = binary_opening(th,disk(2),iterations=1).astype(int)
    th = binary_dilation(th, disk(3), iterations=1).astype(int)
    th = binary_fill_holes(th).astype(int)*255
    # get centroid

    centers = []
    area = 0
    try:
        contours,_ = cv2.findContours(np.uint8(th), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        _,contours,_ = cv2.findContours(np.uint8(th), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    except:
        return False

    for contour in contours:
        area = cv2.contourArea(contour)
        m = cv2.moments(contour)
        center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
        centers.append(center)

    #    x, y = contour.T
    #    # Convert from numpy arrays to normal arrays
    #    x = x.tolist()[0]
    #    y = y.tolist()[0]
    #   tck, u = splprep([x, y], u=None, s=1.0, per=1)
    #    u_new = np.linspace(u.min(), u.max(), 2000)
    #    x_new, y_new = splev(u_new, tck, der=0)
        # Convert it back to numpy format for opencv to be able to display it
    #    res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
    #    smoothened.append(np.asarray(res_array, dtype=np.int32))
    # Overlay the smoothed contours on the original image
    #fimg = np.zeros(th.shape)
    #cv2.drawContours(fimg, smoothened, -1, (255, 255, 255), -1)

    bim = np.uint8((255 - th) * bim) * 255

    th = (cv2.resize(np.uint8(th), (w, h), interpolation=cv2.INTER_CUBIC)>100)*255

    img = cv2.bitwise_or(img, img, mask=np.uint8(th))
    # stop_point = preprocess2(img)
    if gsigma == 0:
        fimg = img
    else:
        fimg = gaussfilt(img, gsigma)
    return fimg, 0 # stop_point



def findRegions2(iimg):
    # White more white!!
    rows,cols = iimg.shape
    # clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(32, 32))
    # cl1 = clahe.apply(iimg)
    # equ = cv2.equalizeHist(cl1)
    im_1b = cv2.GaussianBlur(iimg, (21,21), 0)
    nimg = np.array(iimg)
    # Clustering of image
    segments = slic(im_1b, n_segments=300, sigma=3, compactness=0.08)
    #segments = felzenszwalb(im_1b, scale=300, sigma=2, min_size=500)

    total_slics = np.max(segments)+1
    # Now, for each segment we are going to
    med_list = []
    for i in range(total_slics):
        el_med = np.median(im_1b[np.where(segments == i)])
        med_list.append([el_med])

    k = KMeans(n_clusters=3)
    k.fit(med_list)

    paint_black_1 = np.argmin(k.cluster_centers_)
    paint_black_2 = np.argmax(k.cluster_centers_)


    for i in range(total_slics):
        el_med = np.median(im_1b[np.where(segments == i)])
        if (k.labels_[i] == paint_black_1 or k.labels_[i]==paint_black_2):
            nimg[np.where(segments == i)] = 0

    # If the image has a cell, then we can return the centroid of the biggest connected component
    nimg_mask = nimg.copy()
    nimg_mask[nimg>0] = 255
    output = cv2.connectedComponentsWithStats(nimg_mask, 8, cv2.CV_32S)
    if(output):
        stats = output[2]
        centroids = output[3]
        # I need to get the top left up and the top bottom right and the centroid of this box
        left_corner = np.min(stats[1:,cv2.CC_STAT_LEFT])
        top_corner = np.min(stats[1:,cv2.CC_STAT_TOP])
        right_corner = np.max(stats[1:,cv2.CC_STAT_LEFT]+stats[1:,cv2.CC_STAT_WIDTH])
        down_corner = np.max(stats[1:,cv2.CC_STAT_TOP]+stats[1:,cv2.CC_STAT_HEIGHT])
        areas = stats[1:,cv2.CC_STAT_AREA]
        # the centroid must be weighted by the area
        centroid = np.zeros(2)
        centroid[0] = np.sum(centroids[1:,1]*areas)/np.sum(areas)
        centroid[1] = np.sum(centroids[1:,0]*areas)/np.sum(areas)
        # We will return, centroid, roi.Width, roi.Height, cell_image
        return nimg, centroid, np.array([left_corner, top_corner]) , np.array([right_corner,down_corner])
def getCell(file_im):
    im_crop = cv2.imread(file_im, cv2.IMREAD_GRAYSCALE)
    folder_store, file = path.split(file_im)
    if (im_crop.size == 0):
        writeErrorFile("In DetectPoints : Image NOT FOUND", folder_store)
        return False

    img, _ = findRegions(im_crop)
    print("Stop")

def main():
    try:
        file_im = "Z:\\lleti\\AUTOCLEM\\13072018_automation_spots\\EM\\My_Project_halloween\\5K_field--X01--Y13_0020___0019\\5K_field--X01--Y13_0020___0019__acq\\no_border\\slicecell__00008_z=1.3494um.tif"#sys.argv[1]
        tag = "whatever" #sys.argv[2]
        folder_store, _= path.split(file_im)
        if(not getCell(file_im)):
            writeErrorFile("No points detected or unexpected ERROR",folder_store)
    except SystemExit:
        pass
    except :
        print("CONTINUE DETECT CELL")

if __name__ == "__main__":
    main()