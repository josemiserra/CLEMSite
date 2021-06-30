
import cv2
import sys
import numpy as np
from os import path
from glob import glob
import math
from skimage.filters import threshold_isodata
from imutils import writeErrorFile
from skimage.feature import register_translation
from skimage import data, io, filters
from skimage.segmentation import slic,mark_boundaries
from skimage.morphology import opening
from skimage.morphology import square


from skimage.restoration import denoise_tv_chambolle, denoise_bilateral

def SLICthresholdingSQ(img):
    rows, cols = img.shape
    n_segs = int((rows*cols)/2500)
    segments = slic(img, n_segments=n_segs, sigma=0.5, compactness=0.08)
    total_slics = np.max(segments) + 1
    # mark_boundaries(img, segments)
    med_list = []
    # Sorting of indexes speeds ups the process of calculating median values
    flat = segments.ravel()
    lin_idx = np.argsort(flat, kind='mergesort')
    sp_ind = np.split(lin_idx, np.cumsum(np.bincount(flat)[:-1]))
    imr_f = img.ravel()

    thresh = np.median(imr_f)
    candidates = []
    for i in range(total_slics):
        # Check the form factor of the square
        indexes = np.unravel_index(sp_ind[i], img.shape)
        top_left = np.min(indexes[0]),np.min(indexes[1])
        bottom_right = np.max(indexes[0]),np.max(indexes[1])
        side_x = top_left[0] - bottom_right[0]
        side_y = top_left[1] - bottom_right[1]
        form_factor = side_x/(side_y*1.0)
        if form_factor < 0.75 and form_factor > 1.25:
            continue
        if np.abs(side_x*side_y)>5000:
            continue
        el_med = np.median(imr_f[sp_ind[i]])
        if el_med < thresh:
            candidates.append(indexes)

    return candidates

def preprocess(im):
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(32, 32))
    cl1 = clahe.apply(im)
    equ = cv2.equalizeHist(cl1)
    im_1 = cv2.GaussianBlur(equ, (5, 5), 0)
    return im_1

def findTemplate(file_im,file_temp):

    folder_store, _ = path.split(file_im)
    im_1or = cv2.imread(file_im, cv2.IMREAD_GRAYSCALE)
    im_1 = cv2.GaussianBlur(im_1or, (5, 5), 0)

    im_2 = cv2.imread(file_temp, cv2.IMREAD_GRAYSCALE)
    offset_image = cv2.GaussianBlur(im_2, (5, 5), 0)

    #image = filters.sobel(im_1)
    #offset_image = filters.sobel(im_2)

    #image = cv2.convertScaleAbs(im_1, alpha=255)
    #offset_image = cv2.convertScaleAbs(im_2,alpha = 255)

    res = cv2.matchTemplate(im_1, offset_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val < 0.9 : # We need high correlation to work with this
        return [],[],[]
    top_left = (max_loc[0] + 10, max_loc[1] + 10)

    side = np.min(offset_image.shape)
    shape = (side - 20, side - 20)  # Offset that was given to the template
    center = (int(top_left[0] + shape[0] * 0.5), int(top_left[1] + shape[1] * 0.5))

    # for debugging purposes
    image_c = cv2.cvtColor(im_1or, cv2.COLOR_GRAY2BGR)
    #
    cv2.rectangle(image_c, top_left,(top_left[0]+shape[0],top_left[1]+shape[1]), (0, 0, 255), 2)
    cv2.circle(image_c,center, 1, (255, 0, 0), 3)
    cv2.imwrite(folder_store + "\\xcorr_.png", image_c)

    return top_left, shape, center

def findSquare2(file_im,file_template, tag):

    folder_store, _ = path.split(file_im)
    im_1 = cv2.imread(file_im, cv2.IMREAD_GRAYSCALE)

    # Detect black images and discard them. Happened with the FIB column more frequently
    if np.mean(im_1)<5:
        return

    height, width = im_1.shape
    top_left, shape, center = findTemplate(file_im, file_template)

    if(top_left):
        rval = (height / 2 - center[0], width / 2 - center[1])
        val = (center[0], center[1], shape[0], shape[1], top_left[0], top_left[1], rval[0], rval[1])
        return rval

    im_1 = denoise_tv_chambolle(im_1, weight= 0.05, multichannel=False)
    # If template matching was not good enough, we have apply brute force thresholding
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(32, 32))
    im_1 = cv2.normalize(im_1,im_1,0,255,cv2.NORM_MINMAX)
    im_1 = np.array(im_1,dtype=np.uint8)
    cl1 = clahe.apply(im_1)

    # equ = cv2.equalizeHist(cl1)
    im_1b = cv2.GaussianBlur(cl1, (5, 5), 0)
    candidates = SLICthresholdingSQ(im_1b)

    # Now we have a selection of possible squares
    width, height = im_1b.shape
    centroids_list = []
    dist_list = []
    contours_list = []
    for candidate in candidates:
        c_image = np.zeros(im_1b.shape)
        # Convert to image
        c_image[candidate[0],candidate[1]]=255
        opening_im = np.uint8(opening(c_image,square(7)))
        try:
            contours, _ = cv2.findContours(opening_im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        except ValueError:
            _, contours, _ = cv2.findContours(opening_im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        except:
            return False

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # If area of square is smaller than
            if (w * h < 1000 or w * h > 5000):  # change to perfect squared pixel size.
                continue
            ratio = w / (h * 1.0)
            if (ratio < 0.75 or ratio > 1.25):
                continue
            side = np.min([w,h])
            M = cv2.moments(cnt)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            shift_cx = height / 2 - cx
            shift_cy = width / 2 - cy
            dist_list.append(math.sqrt(shift_cx * shift_cx + shift_cy * shift_cy))
            centroids_list.append([cx, cy, side, side, x, y, shift_cx, shift_cy])
            contours_list.append(cnt)

    imageC = cv2.cvtColor(im_1b,cv2.COLOR_GRAY2BGR)
    imageC = cv2.drawContours(imageC, contours_list, -1, (0,255,0), 3)

    if(not centroids_list):
        return []
    # Sort by distance to the center
    indexes = [i[0] for i in sorted(enumerate(dist_list), key=lambda x:x[1])]
    centroids_list = [centroids_list[i] for i in indexes]
    val = centroids_list[0]

    # And this the final result
    image_c = cv2.cvtColor(im_1,cv2.COLOR_GRAY2BGR)
    cv2.rectangle(imageC, (val[4], val[5]), (val[4] + val[2], val[5] + val[3]), (0, 0, 255), 3)
    cv2.imwrite(folder_store + "\\contours_" + tag + ".png", imageC)
    cv2.rectangle(image_c,(val[4],val[5]),(val[4]+val[2],val[5]+val[3]),(0,0,255),1)
    cv2.circle(image_c,(int(round(val[4]+val[2]/2)),int(round(val[5]+val[3]/2))),2,(255,0,0),1)

    # to_file = time.strftime("%Y_%m_%d-%H_%M")
    cv2.imwrite(folder_store+"\\square_processed_"+tag+".png", image_c)

    return (val[6],val[7])



try:
    file_im = sys.argv[1]
    tag = sys.argv[2]
    folder_store,file = path.split(file_im)
    # Get the template file from the folder
    template_file = glob(folder_store+"\\square_template*.tif")
    if(not template_file):
        raise SystemExit
    val = findSquare2(file_im,template_file[0],tag)
    if(val):
        file_data = folder_store + "\\data_square_" + tag + ".csv"
        with open(file_data, 'w') as f:
            f.write(str(val[0]) + ";" + str(val[1]) + "\n")
    else:
        writeErrorFile("ERROR detecting SQUARE in FIB",folder_store)
except SystemExit:
    pass
except:
    writeErrorFile("In findCentroidSquare2: ARGUMENTS NOT GIVEN or EXECUTION ERROR",".")
