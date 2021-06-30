import cv2
import numpy as np
from matplotlib import pyplot as plt
# http://scikit-image.org/docs/dev/auto_examples/transform/plot_register_translation.html
from skimage.feature import register_translation
# from skimage.feature.register_translation import _upsampled_dft
# from scipy.ndimage import fourier_shift
from imutils import gaussfilt,getImages,canny,save_to_csv
from skimage import data, io, filters
from skimage.morphology import watershed
from skimage.feature import peak_local_max
from scipy import ndimage
from skimage.feature import match_template
from scipy.ndimage import fourier_shift
import os
# from pyflann import *
import time


MIN_MATCH_COUNT = 4
from multiprocessing.pool import ThreadPool

def plot_overlay(imageRef, template):
    overlay = np.zeros(shape=(imageRef.shape) + (3,), dtype=np.uint8)
    # cv2.circle(imageRef, (int(center[0]),int(center[1])), 5, (255, 255, 255), 2)
    # cv2.rectangle(imageRef,top_left, bottom_right, 255, 2)

    #imageTemp = np.zeros(shape=(imageRef.shape), dtype=np.uint8)
    #imageTemp[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = template
    w,h = imageRef.shape
    imageTemp = cv2.resize(template,(h,w),None)

    overlay[..., 0] = imageRef
    overlay[..., 1] =imageTemp
    fig, ax = plt.subplots()
    ax.imshow(overlay)
    plt.show()
    return fig

def xcorr(image,offset_image):
    image = filters.sobel(image)
    offset_image= filters.sobel(offset_image)
    # pixel precision first
    #shift, error, diffphase = register_translation(image, offset_image)
    #print("Detected pixel offset (y, x):")
    #print(shift)
    # subpixel precision
    shift, error, diffphase = register_translation(image, offset_image, 100)

    print("Shift computed:"+str(shift))
    print("Expected error: "+str(error))
    return shift


class RootSIFT:
    def __init__(self):
        # initialize the SIFT feature extractor
        self.sift_d= cv2.xfeatures2d.SIFT_create(contrastThreshold = 0.02,edgeThreshold = 20)

    def detectAndCompute(self, image, mask = None):
        eps = 1e-7
        image = gaussfilt(image,sigma=1.2)
        image = np.uint8(image)

        # compute SIFT descriptors
        kps, des = self.sift_d.detectAndCompute(image,mask)

        # if there are no keypoints or descriptors, return an empty tuple
        if len(kps) == 0:
            return ([], None)

        # apply the Hellinger kernel by first L1-normalizing and taking the
        # square-root
        des /= (des.sum(axis=1, keepdims=True) + eps)
        des = np.sqrt(des)
        # return a tuple of the keypoints and descriptors
        return (kps, des)


def computeShiftORB(im1,im2):
    detector = cv2.ORB_create()
    # detector = cv2.AKAZE()
    # detector = cv2.BRISK()
    # detector =  cv2.xfeatures2d.SURF(800)
    norm = cv2.NORM_HAMMING
    flann_params = dict(algorithm=6,
                        table_number=6,
                        key_size=20,
                        multi_probe_level=2)
    search_params = dict(checks=100)

    kp1, des1 = detector.detectAndCompute(im1,None)
    kp2, des2 = detector.detectAndCompute(im2,None)

    flann = cv2.FlannBasedMatcher(flann_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    good = []
    for m_n in matches:
        if len(m_n) != 2:
            continue
        (m, n) = m_n
        if m.distance < 0.6 * n.distance:
            good.append(m)


    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good])
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good])

        M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        return (-M[0, 2], -M[1, 2])
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
    return


def computeShiftSIFT(im1,im2):
    """
     Given two images computes a translation shift between both.
     
     1) Compute set of points
     2) Get best matches
     3) Feed them and find homography
     4) Force the homography to be translation only
     5) return shift between images 
    :param im1: 
    :return: 
    """

    # Match features by FLANN
    rs = RootSIFT()

    pool = ThreadPool(processes=cv2.getNumberOfCPUs())

    result_list = pool.starmap(affine_detect,[(rs,im1),(rs,im2)])

    kp1,des1 = result_list[0]
    kp2,des2 = result_list[1]
    #kp1, des1 = rs.compute(im1)
    #kp2, des2 = rs.compute(im2)


    M = []
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    #flann = FLANN()
    #set_distance_type('euclidean')
    #result,dist1 = flann.nn(des1, des2, 1, algorithm="kdtree", trees=5, checks=100)

    # Apply ratio test
    good = []
    #p_std = np.std(dist1)
    #for ind in range(len(dist1)):
    #    if dist1[ind]< np.median(dist1)*0.75 :   # 1.5*p_std:
    #        good.append(ind)

    for m, n in matches:
       if m.distance < 0.9 * n.distance:
                good.append(m)

    if len(good) > MIN_MATCH_COUNT:
            #src_pts = np.float32([kp1[result[m]].pt for m in good]).reshape(-1, 1, 2)
            #dst_pts = np.float32([kp2[m].pt for m in good]).reshape(-1, 1, 2)
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
           # M = cv2.estimateRigidTransform(src_pts, dst_pts, fullAffine=False)
            return  (-M[0,2],-M[1,2])
    else:
            print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
            matchesMask = None

    return



def computeShiftFiles(fileim1,fileim2, bin = 0.5):
    img = cv2.imread(fileim1,0) #
    img2 = cv2.imread(fileim2,0)
    # return np.array([0.0, 250.0]), img, img2
    shape1 =np.array(np.array((img.shape))*bin,dtype=np.int32)
    img = cv2.resize(img, (shape1[1],shape1[0]))
    shape2 = np.array(np.array((img2.shape))*bin,dtype=np.int32)
    img2 = cv2.resize(img2, (shape2[1],shape2[0]))
    shift= computeShiftSIFT(img,img2)
    return shift,img,img2


def computeShiftImages(im1,im2,logger):


    shape1 =np.array(im1.shape,dtype=np.int32)
    h,w = shape1
    shape2 = np.array(im2.shape, dtype=np.int32)
    h2, w2 = shape2

    if(w!=w2):
        shift = np.array([0.0, 0.0], dtype=np.float32)
        return shift, im1, im2

    if (w > 1024):
        r = 1024.0 / w
        dim = (1024, int(h * r))
        # perform resizing to speed up
        img = cv2.resize(im1, dim, interpolation=cv2.INTER_AREA)
        r2 = 1024.0 / w2
        dim2 = (1024, int(h2 * r2))
        img2 = cv2.resize(im2, dim, interpolation=cv2.INTER_AREA)
    else:
        img = im1
        img2 = im2

    shift= computeShiftSIFT(img,img2)
    #
    #  shift in x and y is returned as a percentage of the image 1
    fshift = (shift[0]*w/dim[0],shift[1]*h/dim[1])
    return fshift,img,img2




def computeShiftFilesXCORR(fileim1,fileim2):
    img = cv2.imread(fileim1,0) #
    img2 = cv2.imread(fileim2,0)
    shape1 =np.array(np.array((img.shape))*0.5,dtype=np.int32)
    img = cv2.resize(img, (shape1[1],shape1[0]))
    img2 = cv2.resize(img2, (shape1[1],shape1[0]))
    shift =  xcorr(img, img2)
    return (shift[1],shift[0]),img,img2




def affine_skew(tilt, phi, img, mask=None):
    '''
    affine_skew(tilt, phi, img, mask=None) -> skew_img, skew_mask, Ai

    Ai - is an affine transform matrix from skew_img to img
    '''
    h, w = img.shape[:2]
    if mask is None:
        mask = np.zeros((h, w), np.uint8)
        mask[:] = 255
    A = np.float32([[1, 0, 0], [0, 1, 0]])
    if phi != 0.0:
        phi = np.deg2rad(phi)
        s, c = np.sin(phi), np.cos(phi)
        A = np.float32([[c,-s], [ s, c]])
        corners = [[0, 0], [w, 0], [w, h], [0, h]]
        tcorners = np.int32( np.dot(corners, A.T) )
        x, y, w, h = cv2.boundingRect(tcorners.reshape(1,-1,2))
        A = np.hstack([A, [[-x], [-y]]])
        img = cv2.warpAffine(img, A, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    if tilt != 1.0:
        s = 0.8*np.sqrt(tilt*tilt-1)
        img = cv2.GaussianBlur(img, (0, 0), sigmaX=s, sigmaY=0.01)
        img = cv2.resize(img, (0, 0), fx=1.0/tilt, fy=1.0, interpolation=cv2.INTER_NEAREST)
        A[0] /= tilt
    if phi != 0.0 or tilt != 1.0:
        h, w = img.shape[:2]
        mask = cv2.warpAffine(mask, A, (w, h), flags=cv2.INTER_NEAREST)
    Ai = cv2.invertAffineTransform(A)
    return img, mask, Ai


def affine_detect(detector, img, mask=None):
    '''
    affine_detect(detector, img, mask=None, pool=None) -> keypoints, descrs

    Apply a set of affine transormations to the image, detect keypoints and
    reproject them into initial image coordinates.
    See http://www.ipol.im/pub/algo/my_affine_sift/ for the details.

    '''
    params = [(1.0, 0.0)]
    for t in 2**(0.5*np.arange(1,6)):
        for phi in np.arange(0, 180, 72.0 / t):
            params.append((t, phi))

    def f(p):
        t, phi = p
        timg, tmask, Ai = affine_skew(t, phi, img)
        keypoints, descrs = detector.detectAndCompute(timg, tmask)
        for kp in keypoints:
            x, y = kp.pt
            kp.pt = tuple( np.dot(Ai, (x, y, 1)) )
        if descrs is None:
            descrs = []
        return keypoints, descrs

    keypoints, descrs = [], []
    ires = list(map(f, params))

    for i, (k, d) in enumerate(ires):
        # print('Affine sampling: %d / %d\r' % (i+1, len(params)), end='')
        keypoints.extend(k)
        descrs.extend(d)

    print()
    return keypoints, np.array(descrs)


# # TEST
#do_XCORR = 1
#if do_XCORR:
#     shift,im1,im2 = computeShiftFilesXCORR("C:\\Users\\Schwab\\Documents\\msite\\MSite4Aserver_shutdown\\automaton\\test_images\\coincidence_point_checks_t1\\SEM_1st_square.tif", \
#                                        "C:\\Users\\Schwab\\Documents\\msite\\MSite4Aserver_shutdown\\automaton\\test_images\\coincidence_point_checks_t1\\SEM_2nd.tif")
#     print(shift)
#     M = np.float32([[1, 0, shift[0]], [0, 1, shift[1] ]])
#     final_LM = cv2.warpAffine(im2, M, (im2.shape[1],im2.shape[0]))
#     plot_overlay(im1, final_LM)
#
# shift,im1,im2 = computeShiftFiles("C:\\Users\\Schwab\\Documents\\msite\\MSite4Aserver_shutdown\\automaton\\test_images\\coincidence_point_checks_t1\\SEM_1st_square.tif", \
#                                        "C:\\Users\\Schwab\\Documents\\msite\\MSite4Aserver_shutdown\\automaton\\test_images\\coincidence_point_checks_t1\\SEM_2nd.tif", bin = 1)
#print(shift)
#M = np.float32([[1, 0, shift[0]], [0, 1, shift[1] ]])
#final_LM = cv2.warpPerspective(im2, M, (im2.shape[1],im2.shape[0]))
#final_LM = cv2.warpAffine(im2, M, (im2.shape[1],im2.shape[0]))
#plot_overlay(im1, final_LM)


# images = getImages('Z:\\lleti\\BINUC_PROJECT\\Binuc_1\\cell1\\EMBL_p1\\',"slice")
# shift_list = []
# shift_list_pixels = []
# times_list = []
# #
# count = 0
# step = 1
# for ind in range(50,len(images)-50,step):
#      start = time.time()
#      #shift,im1,im2 = computeShiftFilesXCORR(images[ind-step],images[ind])
#      shift,im1,im2 = computeShiftFiles(images[ind],images[ind+1])
#      M = np.float32([[1, 0, shift[0]], [0, 1, shift[1] ]])
#      final_LM = cv2.warpAffine(im2, M, (im2.shape[1],im2.shape[0]))
#      #plot_overlay(im1, final_LM)
#      print("%"+str(count))
#      end = time.time()
#      times_list.append(end - start)
#      shift_list.append((shift[0]*0.005,shift[1]*0.005))
#      shift_list_pixels.append(shift)
#      if(count>800):
#         break
#      count = count+1

#
# save_to_csv("C:\\Users\\Schwab\\Pictures\\capt\\sec_5nm_ASIFT_pixels",shift_list_pixels)
# save_to_csv("C:\\Users\\Schwab\\Pictures\\capt\\sec_5nm_ASIFTum",shift_list)
# save_to_csv("C:\\Users\\Schwab\\Pictures\\capt\\sec_5nm_ASIFTtimes",times_list)
# print("END")