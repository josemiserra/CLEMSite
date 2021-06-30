import cv2
import sys
import numpy as np
from os import path
import time
import math
import random
# from sklearn.cluster import KMeans
from os import path
from sklearn.cluster import KMeans
from skimage.segmentation import slic

from imutils import writeErrorFile




def find_trapezoid(cnt,image_c=None):

    epsilon = 0.01 * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    alpha = 0.01
    while(len(approx)!= 4):
        epsilon = alpha * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        alpha += 0.01
        if alpha>=1.0:
            return []

    # Minimum in X corresponds to the first spike
    spike_1 = np.argmin(approx[:,0,0])
    spike_2 = np.argmax(approx[:,0,0])
    bottom_1 = np.squeeze(approx[spike_1])
    bottom_2 = np.squeeze(approx[spike_2])

    approx = np.delete(approx, [spike_1, spike_2], 0)

    # The one with small x is the top_1
    spike_1 = np.argmin(approx[:,0,0])
    spike_2 = np.argmax(approx[:,0,0])
    top_1 = np.squeeze(approx[spike_1])
    top_2 = np.squeeze(approx[spike_2])


    dista = np.abs(top_2[0] - top_1[0])
    distb = np.abs(bottom_2[0] - bottom_1[0])

    # Check conditions of trapezoid
    if(distb<dista):
        return []
    ratio = dista / (distb * 1.0 + 1e-15)

    if ratio <0.2  or ratio > 0.95: # We don't allow weird trapeziums or rectancles
        return []
    a1 = top_2[1]
    b1 = top_1[1]
    # y value must be similar
    ratio = min(a1, b1) / max(a1, b1)
    if ratio<0.85:
        return []
    a = top_1
    b = top_2


    return a,b
    #  cv2.drawContours(image_c, approx, 0, (0, 255, 0), 2)
    #  cv2.circle(image_c,(val[0],val[1]),3,(255,255,255),3)
    #  cv2.circle(image_c,(x,y),3,(255,255,255),3)


def SLICThresholding(iimg, invert = False):
    """
        It is assumed that the image is segmented in three blocks:
            background : completely dark (white for the detector)
            noise : gray values around
            foreground : contains the trench and objects, white
        We do SLIC segmentation and we cluster in 3 groups.
        Background and noise are removed.
        Since the segmentation coming from SLIC is quite rough,
        we use the minimum value - error to do a more defined threshold
    :param iimg:
    :return:
    """
    # White more white!!
    rows,cols = iimg.shape
    # clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(32, 32))
    # cl1 = clahe.apply(iimg)
    # equ = cv2.equalizeHist(cl1)
    im_1b = cv2.GaussianBlur(iimg, (11,11), 0)

    # Clustering of image
    segments = slic(im_1b, n_segments=500, sigma=3, compactness=0.01)

    total_slics = np.max(segments)+1
    # Now, for each segment we are going to
    med_list = []
    for i in range(total_slics):
        el_med = np.median(im_1b[np.where(segments == i)])
        med_list.append([el_med])

    k = KMeans(n_clusters=3)
    k.fit(med_list)

    paint_black = np.argmin(k.cluster_centers_)
    paint_white = np.argmax(k.cluster_centers_)
    paint = paint_white
    if invert:
        paint = paint_black
    th = np.zeros(im_1b.shape,dtype = np.uint8)
    for i in range(total_slics):
        if (k.labels_[i] == paint):
             th[np.where(segments == i)]=255
    return th


def getTrapezoidCandidates(img_original,img_binary):
    try:
        contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        _, contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except:
        return False

    height, width = img_original.shape
    centroids_list = []
    dist_list = []
    corners_list = []
    hulls_list = []
    tpixels = img_binary.shape[0]*img_binary.shape[1]
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # If area of square is smaller than
        if (w * h < 0.01*tpixels):
            continue
            #  if(cv2.isContourConvex(cnt)): Failed if the image is too clear
            #       continue
        if  w * h > 0.25*tpixels:
            continue
        if( w > 0.95*h and w < 1.05*h ):
            continue
            # this is a square, avoid
        hull = cv2.convexHull(cnt)
        corner = find_trapezoid(cnt,img_original)
        if (not np.any(corner)):
            continue

        M = cv2.moments(cnt)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])

        shift_cx = height / 2 - cx
        shift_cy = width / 2 - cy - 2
        dist_list.append(math.sqrt(shift_cx * shift_cx + shift_cy * shift_cy))
        centroids_list.append([shift_cx, shift_cy])
        corners_list.append(corner)
        hull = cv2.convexHull(cnt)
        hulls_list.append(hull)

    return dist_list,centroids_list,hulls_list,corners_list

def saveTrenchPoints(file_before, file_im,tag):
    # Get folder
    folder_store, file = path.split(file_im)
    file_data = folder_store + "\\data_trench_" + tag + ".csv"

    im_1 = cv2.imread(file_im, cv2.IMREAD_GRAYSCALE)
    im_1 = cv2.GaussianBlur(im_1, (3, 3), 1.2)  # 5,5
    im_before_b = cv2.imread(file_before, cv2.IMREAD_GRAYSCALE)
    im_before_b = cv2.GaussianBlur(im_before_b, (3, 3), 1.2)  # 5,5
    if(im_1.size==0):
        writeErrorFile("Image couldn't be read.",folder_store)
        return

    im_difference = cv2.absdiff(im_before_b, im_1)
    cv2.normalize(im_difference, im_difference, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    height, width = im_1.shape

    im_b= cv2.GaussianBlur(im_difference, (3, 3), 1.2)
    ret, th = cv2.threshold(im_b, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
   # kernel = np.ones((3, 3), np.uint8) #5,5
   # opening = cv2.morphologyEx(opening, cv2.MORPH_DILATE, kernel)

    #epsilon = 0.1 * cv2.arcLength(cnt, True)
    #approx = cv2.approxPolyDP(cnt, epsilon, True)


    dist_list,centroids_list,hulls_list,corners_list = getTrapezoidCandidates(im_1,opening)
    # if fail now try with SLICThresholding
    if not dist_list :
        th = SLICThresholding(im_1,True)
        opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
        dist_list,centroids_list,hulls_list,corners_list = getTrapezoidCandidates(im_1, opening)

    if (dist_list):
        indexes = [i[0] for i in sorted(enumerate(dist_list), key=lambda x: x[1])]
        shift = centroids_list[indexes[0]]
        hull = hulls_list[indexes[0]]
        x, y, w, h = cv2.boundingRect(hull)
        image_c = cv2.cvtColor(im_1, cv2.COLOR_GRAY2BGR)
        corner = corners_list[indexes[0]]
        a = corner[0]
        b = corner[1]

        cv2.drawContours(image_c, [hull], 0, (0, 255, 0), 2)
        cv2.circle(image_c, (a[0], a[1]-2), 3, (0, 0, 255), 2)
        cv2.circle(image_c, (b[0], b[1]-2), 3, (0, 0, 255), 2)

        top_c = [0, 0]
        top_c[1] = a[1]-2
        if(a[0]<x+w/2 and b[0]>x+w/2):
            top_c[0] = int(a[0] + np.abs(a[0] - b[0]) * 0.5)
        else:
            top_c[0] = x+w/2

        a[0] -= height / 2
        b[0] -= width / 2
        a[1] -= height / 2-2
        b[1] -= width / 2-2
        # cv2.rectangle(image_c,(val[4],val[5]),(val[4]+val[2],val[5]+val[3]),(0,0,255),2)

        cv2.circle(image_c, (int(top_c[0]), int(top_c[1])), 3, (255, 0, 0), 2)
        cv2.circle(image_c, (int(x + w / 2),int(y + h / 2)), 3, (255, 255, 0), 2)

        cv2.imwrite(folder_store + "\\trench_" + tag + ".png", image_c)
        with open(file_data, 'w') as f:
            shift = np.array(shift,dtype=np.int32)
            f.write("center_shift;" + str(shift[0]) + ";" + str(shift[1]) + "\n")
            f.write("centroid;" + str(int(x + w / 2)) + ";" + str(int(y + h / 2)) + "\n")
            shift_top_x = height / 2 - top_c[0]
            shift_top_y = width / 2 - top_c[1] # correction for thickness of border
            f.write("top;" + str(int(shift_top_x)) + ";" + str(int(shift_top_y)) + "\n")
            f.write("corner1;" + str(a[0]) + ";" + str(a[1]) + "\n")
            f.write("corner2;" + str(b[0]) + ";" + str(b[1]) + "\n")
        return True
    else:
        file_data = folder_store + "\\failed_" + tag
        with open(file_data, 'w') as f:
            f.write("FALSE")
        return False


def detectorWorks(file_im,tag):
    folder_store, file = path.split(file_im)

    im_1 = cv2.imread(file_im, cv2.IMREAD_GRAYSCALE)
    if(im_1 is None):
        return False
    #  All white points out
    im_1[np.nonzero(im_1 == 255)] = 0
    # Gaussian smoothing
    im_1b = cv2.GaussianBlur(im_1, (5, 5), 1.2)

    height, width = im_1.shape
    # image cropping borders (100 px)
    # im_1b = im_1b[100:height-100,100:width-100]

    # Threshold image using OTSU
    ret, th = cv2.threshold(im_1b, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((7, 7), np.uint8)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

    # Add up all the white pixels
    total = np.sum(opening > 0)

    cv2.imwrite(folder_store + "\\ESB_detection_" + tag + ".png", opening)
    # If the number of pixels is bigger than 0.01% means that is detecting something...
    if (total / (height * width * 1.0) < 0.005):
        file_data = folder_store + "\\failed_" + tag
        with open(file_data, 'w') as f:
            f.write("FALSE")
        return False
    else:
        file_data = folder_store + "\\success_" + tag
        with open(file_data, 'w') as f:
            f.write("TRUE")
        return True

try:
    file_im_before = sys.argv[1]
    file_im = sys.argv[2]
    tag = sys.argv[3]
    if(detectorWorks(file_im,tag)):
        saveTrenchPoints(file_im_before,file_im,tag)
    else:
        folder_store, file = path.split(file_im)
        file_data = folder_store + "\\data_trench_" + tag + ".csv"
        with open(file_data, 'w') as f:
            f.write("ERROR;0;0")
except SystemExit:
    pass
except:
    writeErrorFile("In ESB findTrench ARGUMENTS NOT GIVEN or ERROR",".")

