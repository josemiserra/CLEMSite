import numpy as np
import cv2
import sys
from os import path
#from matplotlib import pyplot as plt
from imutils import integrate, integral_image

def isGood(q,p,img):
    nhood = np.array([30,30])
    nhood[0] = np.max([2 * np.ceil(nhood[0] * 0.5) + 1, 0])  # Make sure the nhood size is odd.
    nhood[1] = np.max([2 * np.ceil(nhood[1] * 0.5) + 1, 0])
    nhood_center = (nhood - 1) / 2

    # Suppress this maximum and its close   neighbors.
    p1 = int(p) - nhood_center[0]
    p2 = int(p) + nhood_center[0]
    q1 = int(q) - nhood_center[1]
    q2 = int(q) + nhood_center[1]

    p1 = int(np.max([p1, 0]))
    p2 = int(np.min([p2, img.shape[1]-1]))
    q1 = int(np.max([q1, 0]))
    q2 = int(np.min([q2, img.shape[0]-1]))
    # Create a square around the maxima to be supressed
    x = [ val for val in range(q1,q2)]
    y = [ val for val in range(p1,p2)]
    [qq, pp] = np.meshgrid(x, y)  # 'xy' default, can return i,j
    patch = img[qq, pp]

    intimg = integral_image(img)
    img_2 = np.array(img, dtype=np.uint64)
    intimg_2 = integral_image(np.multiply(img_2, img_2))
    # Calculate Variance inside the patch
    S1 = integrate(intimg, q1, p1, q2, p2)
    S2 = integrate(intimg_2, q1, p1, q2, p2)
    n = (nhood[0] * nhood[1])
    mean_S = S1/n
    variance = (S2- S1*S1/n)/n
    sd = np.sqrt(variance)
    if(sd<30):  # Low variance, remove point
        return False
    else:
        return True

def hasFeaturesImage(img):
    h, w = img.shape
    r = 1.0
    if (h > 1024 and w > 1024):
        r = 1024.0 / w
        dim = (1024, int(h * r))
        # perform resizing to speed up
        rimg = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    else:
        rimg = img.copy()
    gray = cv2.GaussianBlur(rimg, (11, 11), 3)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(32, 32))
    cl1 = clahe.apply(gray)

    corners = cv2.goodFeaturesToTrack(cl1, 50, 0.1, 30)
    corners = np.int0(corners)

    h, w = rimg.shape
    img2 = cv2.cvtColor(rimg, cv2.COLOR_GRAY2BGR)

    count = 0
    for i in corners:
        x, y = i.ravel()
        if (x > 20 and x < (w - 20) and y > 20 and y < (h - 20)):
            if isGood(y, x, rimg):
                count += 1
                cv2.circle(img2, (x, y), 3, 255, -1)

    if (count < 10):
        return False
    else:
        return True


def checkFeatures(file_im,tag):
    img = cv2.imread(file_im, 0)
    if(img.size==0):
        return False
    folder_store, features_fn = path.split(file_im)
    features_fn2 = file_im[:-4]+"_ft.tif"
    gray = cv2.GaussianBlur(img, (11, 11),3)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(32, 32))
    cl1 = clahe.apply(gray)

    corners = cv2.goodFeaturesToTrack(cl1, 50, 0.1, 30)
    if(corners.size == 0):
        return False
    corners = np.int0(corners)

    h, w = img.shape
    img2 = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    count = 0
    for i in corners:
        x, y = i.ravel()
        if (x > 20 and x < (w - 20) and y > 20 and y < (h - 20)):
            if isGood(y,x, img):
                count += 1
                cv2.circle(img2, (x, y), 3, 255, -1)

    cv2.imwrite(features_fn2,img2)
    if (count < 10):
        file_data = folder_store + "\\features_failed_" + tag
        with open(file_data, 'w') as f:
            f.write("FALSE")
        return False
    else:
        file_data = folder_store + "\\features_success_" + tag
        with open(file_data, 'w') as f:
            f.write("TRUE")
        return True

#try:
#    file_im = sys.argv[1]
#    tag = sys.argv[2]
#    checkFeatures(file_im,tag)
#except SystemExit:
#    pass
#except:
#    pass
