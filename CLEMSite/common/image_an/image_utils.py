import cv2
import numpy as np
# from skimage.filters import threshold_otsu, threshold_adaptive
import math
from scipy.signal  import convolve2d
# import matplotlib.pyplot as plt
from collections import deque
from skimage.segmentation import slic
from skimage import morphology
from scipy.ndimage import label
from skimage import filters
from skimage.util.shape import view_as_blocks
from functools import reduce
import time
from skimage.exposure import equalize_adapthist


# def plotPoints(img,points, color = 'red', size=10):
#     implot = plt.imshow(img)
#     # put a blue dot at (10, 20)
#     points_x = points[:,0]
#     points_y = points[:,1]
#     plt.scatter([points_x], [points_y],c=color,s=size)
#     plt.show()
#
# def plotHist(img):
#     # hist,bins = np.histogram(img.flatten(),256,[0,256])
#
#     plt.hist(img.flatten(),256,[0,256], color = 'r')
#     plt.xlim([0,256])
#     plt.legend(('cdf','histogram'), loc = 'upper left')
#     plt.show()
def soft_launch(input_image, gldparams, v = False):
    return soft_proc(input_image, gldparams['sigma'], gldparams['clahe'], gldparams['canny_thresh'],
                     gldparams['strokeWidth'], gldparams['wiener'], gldparams['laplacian'],
                     gldparams['autoEdge'], inverse_stroke = gldparams['inverse_stroke'], verbose = v)

def soft_proc(input_image, sigma, clahe=True, canny_thresh=0.05, strokeWidth=20, wiener=[2, 2], laplacian=True, autoEdge = True, inverse_stroke=True, verbose = False):
    """
        Swt and Orientation Field Transform preprocessing
        Find Lines using Orientations and Projections
                    Note: +CT means, increases computation time.
        :param :K
                Number of neighbors to consider in the Orientation Field
                Transform.Each neighbor is evaluated against a candidate angle
                and then add up. The biggest the lines, the better the
                result for a bigger K. (K big,+CT)
                Default: 12.
        :param :wiener
            Two-element vector of positive integers: [M N].
            [M N] specifies the number of tile rows and
            columns.  Both M and N must be at least 2.
            The total number of image tiles is equal to M*N.
            If the lines are too thin, it is used to dilate them.
            Default: [2 2]. Use [0,0] to not execute the wiener filter.

        :param :strokeWidth
            When the Stroke Width Transform is executed, for each
            pixel, rays are created from the pixel to the next
            change of gradient. If your stroke is big, use a bigger
            width.(strokeWidth big, ++CT)
            Default: 20.

        :param :canthresh
            Automatic canny thresholding is performed using an
            iterative loop. If the percentage of white pixels is bigger than a
            threshold,then we are assuming the image is getting more and more clutter.
            Default: 0.075, means a 7.5% of the pixels is white.
        :param :sigma
            Preprocessing gaussian filter. Helps with noisy images
            of after CLAHE. Values between 0 and 2 are recommended.
            Default: 0 (not applied).
        :param :clahe
            If true, CLAHE (automatic brightness and contrast
            balance) is applied.
            Default: False.
        ##########################################
        saved values:
        :return :prepro - image after preprocessing (clahe and gaussian filter)
        :return :bwedge - image after automatic canny filtering
        :return :orientim - image with ridge orientations
        :return :reliability - probabilistic plot of orientations
        :return :FSWT = final stroke width transform

    """
    h, w = input_image.shape
    if sigma < 0:
        sigma = 1
    if canny_thresh > 1 or canny_thresh <= 0:
        canny_thresh = 0.05
    if strokeWidth < 2 or strokeWidth > min(h, w):
        # 'Invalid stroke size. Accepted values between and half the size of your image.Setting default value.'
        strokeWidth = 20

    ## PREPRO BLOCK
    PREPRO = soft_prepro(input_image, clahe, laplacian, sigma, verbose)

    ## CANNY BLOCK
    ###############################
    gradient, _, BWEDGE, E_BWEDGE = soft_canny(PREPRO, wiener, canny_thresh, autoEdge, verbose)

    ## ORIENTATION BLOCK
    ORIENTIM, RELIABILITY, R_EDGES = soft_orientation(PREPRO,E_BWEDGE, gradient, verbose)

    ## SWT block
    if verbose:
        t = time.time()
    FSWT = []
    if strokeWidth > 0:
        iSWT = SWT(PREPRO, R_EDGES, ORIENTIM, strokeWidth, angle= np.pi/6, add_invert= inverse_stroke)
        FSWT = cleanswt(iSWT, E_BWEDGE)
        if verbose:
            elapsed = time.time() - t
            print('SWT completed. Elapsed ' + str(elapsed) + ' seconds.')

    return PREPRO, E_BWEDGE, ORIENTIM, RELIABILITY, FSWT

def soft_prepro(input_image, clahe = False, laplacian = False, sigma = 0, verbose = False):
    if verbose:
        t = time.time()

    PREPRO = input_image
    if clahe:
        if verbose:
            print('Applying CLAHE filter.')
        PREPRO = equalize_adapthist(input_image, clip_limit=0.03, nbins=64)
        PREPRO = np.uint8(PREPRO * 255.)

    if laplacian:
        if verbose:
            print('Applying Laplacian filter.')
        PREPRO = laplacianfilt(PREPRO)

    if sigma > 0:
        if verbose:
            print('Applying gaussian filter with sigma ' + str(sigma))
        PREPRO = gaussfilt(PREPRO, sigma)

    if verbose:
        elapsed = time.time() - t
        print('Preprocessing applied. Elapsed ' + str(elapsed) + ' seconds.')

    return PREPRO

def soft_canny(input_image, wiener, canny_thresh = 0.05, autoEdge = False, verbose = False):
    """
    Canny block of soft. Does automatic edges.
    :param input_image:
    :param wiener:
    :param canny_thresh:
    :param autoEdge:
    :param verbose:
    :return:
    """
    if verbose:
        t = time.time()
    gradient, orientation = canny(input_image, 2)
    nm = nonmaxsup_python(gradient, orientation, 1.5)
    print("Gradient and NMS done.")
    if autoEdge:
        BWEDGE = autoedge(nm, canny_thresh, 8, alpha_density=1.05, beta_density=0.0)
    else :
        BWEDGE = autoedge(nm, canny_thresh, 8, alpha_density=0.0, beta_density=0.0)
    if verbose:
        elapsed = time.time() - t
        print('Autoedge applied.')
        print('Elapsed ' + str(elapsed) + ' seconds.')

    E_BWEDGE= borderEnhancer(BWEDGE, wiener)

    return gradient, orientation, BWEDGE, E_BWEDGE

def soft_orientation( input_image, edges,  gradient,  verbose = False):
    if verbose:
        t = time.time()

    _, RELIABILITY = ridgeorient(gradient, 1, 3, 3)
    RELIABILITY[RELIABILITY < 0.5] = 0

    ORIENTIM = calculateOrientations(input_image, gradient)
    ORIENTIM[RELIABILITY < 0.5] = 0

    R_EDGES = np.multiply(edges, RELIABILITY)  # Enhance the bw image removing disordered regions

    if verbose:
        elapsed = time.time() - t
        print('Image Orientation completed. Elapsed ' + str(elapsed) + ' seconds.')

    return ORIENTIM, RELIABILITY, R_EDGES


#### HELPER LIBRARY METHODS

def normalise(im):
    im = np.float32(im)
    n = im - np.min(im[:])
    n = n / np.max(n[:])
    return n

def canny(i_image,isigma):
    """
    Canny filtering
    """
    image = gaussfilt(i_image,isigma)
    Ix,Iy = derivative5(image)
    Ix_2 = np.multiply(Ix,Ix)
    Iy_2 = np.multiply(Iy,Iy)
    gradient = np.sqrt(Ix_2 + Iy_2)   # Gradient magnitude.
    orientation = np.arctan2(-Iy, Ix)                # Angles -pi to + pi.
    orientation[orientation<0] = orientation[orientation<0]+np.pi           # Map angles to 0-pi.
    orientation = orientation*180/np.pi
    return gradient,orientation

def gaussfilt(img,sigma):
    sze = int(math.ceil(6*sigma))
    if(sze%2 == 0):
            sze = sze+1
    h = fspecial_gauss2D((sze,sze),sigma)
    # conv2(image, mask) is the same as filter2(rot90(mask,2), image)
    image = convolve2d(img,h,'same')
    return image

def fspecial_gauss2D(shape=(3, 3), sigma=0.5):
    """
    2D gaussian mask - should give the same result as MATLAB's
    fspecial('gaussian',[shape],[sigma])
    """
    m, n = [(ss - 1.) / 2. for ss in shape]
    y, x = np.ogrid[-m:m + 1, -n:n + 1]
    h = np.exp(-(x * x + y * y) / (2. * sigma * sigma))
    h[h < np.finfo(h.dtype).eps * h.max()] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h

def laplacianfilt(img):
    """
    Should provide the same result as
    H = fspecial('laplacian');
    I = imfilter(I,H);
    :param img:
    :return:
    """
    h = np.array([[1.0,4.0,1.0],[4.0,-20.0,4.0],[1.0,4.0,1.0]], dtype = np.float32)/6
    image = convolve2d(img,h,'same')
    image[image < 0] = 0
    image = image /np.max(image)
    return np.uint8(image*255)

def derivative5(i_image):
    # 5 tap 1st derivative cofficients.  These are optimal if you are just
    # seeking the 1st derivatives
    # Copyright (c) 2010 Peter Kovesi
    p = np.array([0.037659,0.249153,0.426375,0.249153,0.037659], dtype = np.float32)
    d1 =np.array([0.109604,0.276691,0.000000,-0.276691,-0.109604],dtype = np.float32)

    a =  p[:,np.newaxis]*d1.transpose()
    b =  d1[:,np.newaxis]*p.transpose()
    Ix = convolve2d(i_image,a,'same')
    Iy = convolve2d(i_image,b,'same')
    return Ix,Iy

class Pixel:
    value = 0
    i = 0
    j = 0
    distance = 0
    label = 0

    def __init__(self,distance,i,j,label):
        self.distance = distance
        self.i = i
        self.j = j
        self.label = label

def propagate(img,mask,seeds,ilambda):
    labels_out = np.copy(seeds)
    dists = np.full(img.shape,np.inf)
    dists[seeds>0] = 0
    pq = deque([])
    total_seeds = seeds.max()+1
    for i in range(1,total_seeds):
        # Get all pixel coordinates from pixels that are seeds
        listpx, listpy = np.where(seeds==i)
        for x,y in zip(listpx,listpy):
                push_neighs_on_queue(pq,0.0,x,y ,img,ilambda,i,labels_out, mask)


    while(len(pq)>0):
        p = pq.popleft()
        if(dists[p.i,p.j]>p.distance):
            dists[p.i,p.j] = p.distance
            labels_out[p.i,p.j] = p.label
            push_neighs_on_queue(pq, p.distance,p.i,p.j, img, ilambda, labels_out[p.i,p.j], labels_out, mask)

    return dists,labels_out

def clamped_fetch(img,i,j):
    h,w = img.shape
    if i < 0:
        i = 0
    if i >= w:
        i = w-1
    if j < 0:
        j = 0
    if j >= h:
        j = h-1
    return img[j,i]

def difference(img,i1,j1,i2,j2,ilambda):
     pixel_diff = 0
     #s1 = integrate(ii,i1-1,j1-1,i1+1,j1+1)
     #s2 = integrate(ii,i2-1,j2-1,i2+1,j2+1)
     #pixel_diff = np.abs(s1-s2)
     dEucl = (i1-i2)*(i1-i2) + (j1-j2)*(j1-j2)
     #fdist =np.sqrt((pixel_diff * pixel_diff +dEucl*dEucl*ilambda*ilambda)) # / (1.0 +ilambda ))
     return  int(dEucl*ilambda)
    #return np.sqrt((pixel_diff * pixel_diff +ilambda *dEucl) / (1.0 +ilambda ))
   #return (sqrt(pixel_diff * pixel_diff + (fabs((double) i1 - i2) + fabs((double) j1 - j2)) * lambda * lambda ));

def push_neighs_on_queue(pq,distance,i,j,img,ilambda,label, labels_out, mask):
  #  4-connected
  m,n = img.shape
  if (i > 0):
    val  = labels_out[i-1,j]
    if (val==0 and mask[i-1, j]>0):
        delta_d = difference(img, i, j, i-1, j, ilambda)         # if the neighbor was not labeled, do pushing
        pix = Pixel(distance + delta_d, i-1, j, label)
        pq.append(pix)
  if (j > 0):
    val = labels_out[i,j-1]
    if  val==0 and mask[i, j-1]!=0 :
        delta_d = difference(img,i,j,i,j-1,ilambda)
        pix = Pixel(distance + delta_d, i, j-1, label)
        pq.append(pix)
  if i<(n-1):
    val =  labels_out[i+1,j]
    if (val==0 and mask[i+1, j]!=0) :
        delta_d = difference(img, i, j, i+1, j , ilambda)
        pix = Pixel(distance + delta_d, i+1, j , label)
        pq.append(pix)
  if (j < (m-1)):
    val = labels_out[i,j+1]
    if val==0 and (mask[i, j+1]!=0):
        delta_d = difference(img, i, j, i, j + 1, ilambda)
        pix = Pixel(distance + delta_d, i, j + 1, label)
        pq.append(pix)
  # 8-connected
  if (i > 0) and (j > 0):
    val = labels_out[i-1,j-1]
    if(val==0 and mask[i-1, j-1]!=0):
        delta_d = difference(img, i, j, i-1, j - 1, ilambda)
        pix = Pixel(distance + delta_d, i-1, j - 1, label)
        pq.append(pix)
    if (i < (n-1) and  (j > 0)):
        val=labels_out[i+1,j-1]
        if (val==0 and (mask[i+1, j-1])!=0):
            delta_d = difference(img, i, j, i+1, j - 1, ilambda)
            pix = Pixel(distance + delta_d, i+1, j - 1, label)
            pq.append(pix)
    if (i > 0) and j < (m-1):
        val =labels_out[i-1,j+1]
        if (val==0 and mask[i-1, j+1]!=0 ):
            delta_d = difference(img, i, j, i-1, j + 1, ilambda)
            pix = Pixel(distance + delta_d, i-1, j + 1, label)
            pq.append(pix)
    if (i < (n-1) and j < (m-1)):
        val=labels_out[i+1,j+1]
        if val==0 and (mask[i+1, j+1]!=0):
            delta_d = difference(img, i, j, i+1, j + 1, ilambda)
            pix = Pixel(distance + delta_d, i+1, j + 1, label)
            pq.append(pix)
    return

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

    S += clamped_fetch(ii,r1,c1)

    if (r0 - 1 >= 0) and (c0 - 1 >= 0):
        S += clamped_fetch(ii,r0-1,c0-1)

    if (r0 - 1 >= 0):
        S -= clamped_fetch(ii,r0-1,c1)

    if (c0 - 1 >= 0):
        S -= clamped_fetch(ii,r1,c0-1)

    return S

def softmax(y):
    s = np.exp(y)
    y_prob = s / np.sum(s)
    return y_prob

def remove_borders(img,border):
    # remove borders
    img[:border, :] = 0
    img[-border:, :] = 0
    img[:, :border] = 0
    img[:, -border:] = 0
    return img

def ridgeorient(im, gradientsigma, blocksigma, orientsmoothsigma):
        # Arguments:  im                - A normalised input image.
        #             gradientsigma     - Sigma of the derivative of Gaussian
        #                                 used to compute image gradients.
        #             blocksigma        - Sigma of the Gaussian weighting used to
        #                                 sum the gradient moments.
        #             orientsmoothsigma - Sigma of the Gaussian used to smooth
        #                                 the final orientation vector field.
        #                                 Optional: if ommitted it defaults to 0

        # Returns:    orientim          - The orientation image in radians.
        #                                 Orientation values are +ve clockwise
        #                                 and give the direction *along* the
        #                                 ridges.
        #             reliability       - Measure of the reliability of the
        #                                 orientation measure.  This is a value
        #                                 between 0 and 1. I think a value above
        #                                 about 0.5 can be considered 'reliable'.
        #                                 reliability = 1 - Imin./(Imax+.001);
        #             coherence         - A measure of the degree to which the local
        #                                 area is oriented.
        #                                 coherence = ((Imax-Imin)./(Imax+Imin)).^2;
        rows, cols = im.shape

        # Calculate image gradients.
        sze = int(np.fix(6 * gradientsigma))
        if (sze % 2 == 0):
            sze = sze + 1
        h = fspecial_gauss2D((sze, sze), gradientsigma)
        fx, fy = np.gradient(h)  # Gradient of Gausian.

        Gx = convolve2d(im, fx, 'same')  # Gradient of the image in x
        Gy = convolve2d(im, fy, 'same')  # ... and y

        # Estimate the local ridge orientation at each point by finding the
        # principal axis of variation in the image gradients.

        Gxx = np.multiply(Gx, Gx)  # Covariance data for the image gradients
        Gxy = np.multiply(Gx, Gy)
        Gyy = np.multiply(Gy, Gy)

        # Now smooth the covariance data to perform a weighted summation of the  data.
        sze = int(np.fix(6 * blocksigma))
        if (sze % 2 == 0):
            sze = sze + 1
        h = fspecial_gauss2D((sze, sze), blocksigma)
        Gxx = convolve2d(Gxx, h, 'same')
        Gxy = 2 * convolve2d(Gxy, h, 'same')
        Gyy = convolve2d(Gyy, h, 'same')

        # Analytic solution of principal direction
        Gxy_2 = np.multiply(Gxy, Gxy)
        Gm = Gxx - Gyy
        Gm = np.multiply(Gm, Gm)
        denom = np.sqrt(Gxy_2 + Gm) + np.spacing(1)
        sin2theta = np.divide(Gxy, denom)  # Sine and cosine of doubled angles
        cos2theta = np.divide(Gxx - Gyy, denom)

        sze = int(np.fix(6 * orientsmoothsigma))
        if (sze % 2 == 0):
            sze = sze + 1
        h = fspecial_gauss2D((sze, sze), orientsmoothsigma)

        cos2theta = convolve2d(cos2theta, h, 'same')  # Smoothed sine and cosine of
        sin2theta = convolve2d(sin2theta, h, 'same');  # doubled angles

        orientim =  np.arctan2(sin2theta, cos2theta) / 2  # np.pi / 2 + np.arctan2(sin2theta, cos2theta) / 2; #

        # Calculate 'reliability' of orientation data.  Here we calculate the
        # area moment of inertia about the orientation axis found (this will
        # be the minimum inertia) and an axis  perpendicular (which will be
        # the maximum inertia).  The reliability measure is given by
        # 1.0-min_inertia/max_inertia.  The reasoning being that if the ratio
        # of the minimum to maximum inertia is close to one we have little
        # orientation information.

        Imin = (Gyy + Gxx) / 2
        Imin = Imin - np.multiply((Gxx - Gyy), cos2theta) / 2 - np.multiply(Gxy, sin2theta) / 2
        Imax = Gyy + Gxx - Imin

        reliability = 1 - np.divide(Imin, (Imax + .001))
        # aux = Imax+Imin
        # aux = np.multiply(aux,aux)
        # coherence = np.divide((Imax-Imin),aux)

        # Finally mask reliability to exclude regions where the denominator
        # in the orientation calculation above was small.  Here I have set
        # the value to 0.001, adjust this if you feel the need
        reliability = np.multiply(reliability, (denom > .001))
        return orientim, reliability

def _SWT(i_img, edgeImage, orientim, stroke_width=20, angle=np.pi / 6):
    """
    Adapted version of Stroke Width transform to fill edges. In general provides better results if
    the image has double edges and gradients.
    :param i_img:
    :param edgeImage:
    :param orientim:
    :param stroke_width:
    :param angle:
    :return:
    """
    # np.seterr(divide='ignore', invalid='ignore')
    eps = np.finfo(float).eps
    if np.max(orientim)> np.pi :
        orientim = np.radians(orientim)
    im = gaussfilt(i_img, 1)
    Ix, Iy = derivative5(im)
    Ix_2 = np.multiply(Ix, Ix)
    Iy_2 = np.multiply(Iy, Iy)
    g_mag = np.sqrt(Ix_2 + Iy_2)  # Gradient magnitude.
    Ix = np.divide(Ix, g_mag+eps)
    Iy = np.divide(Iy, g_mag+eps)

    prec = 0.4
    mSWT = -np.ones(i_img.shape)

    h_stroke = stroke_width * 0.5
    rows, cols = i_img.shape

    cy, cx = np.nonzero(edgeImage)
    cgrad_x = Ix[cy, cx] * prec
    cgrad_y = Iy[cy, cx] * prec

    ang_minus = orientim - angle
    # ang_minus[ang_minus<0] = 0
    ang_plus = orientim + angle
    # ang_plus[ang_minus>np.pi] = np.pi

    coords = zip(cy, cx)

    for ind, coord in enumerate(coords):
                i, j = coord
                points_x = []
                points_y = []
                points_x.append(j)
                points_y.append(i)
                curX = j + 0.5
                curY = i + 0.5
                tpoints = 1
                while tpoints < stroke_width:
                    curX = curX + cgrad_x[ind]  # find directionality increments x or y
                    curY = curY + cgrad_y[ind]
                    tpoints = tpoints + 1
                    curPixX = int(curX)
                    curPixY = int(curY)
                    if (curPixX < 0 or curPixX > cols - 1 or curPixY < 0 or curPixY > rows - 1):
                        break
                    points_x.append(curPixX)
                    points_y.append(curPixY)

                    if (edgeImage[curPixY, curPixX] > 0 and tpoints > h_stroke ):
                        ang_plus_v = ang_plus[i, j]
                        ang_minus_v = ang_minus[i, j]
                        if ((orientim[curPixY, curPixX] < ang_plus_v) and (orientim[curPixY, curPixX] > ang_minus_v)):
                            mSWT[points_y, points_x] = 1
                            break
    return mSWT

def SWT(i_image, edges, orientation, stroke_width, angle=np.pi / 3, add_invert = False):
    inv_iim = 255 - i_image  # needed for shadowing

    swtim = _SWT(i_image, edges, orientation, stroke_width, angle)  # one image
    swtim[np.nonzero(swtim < 0)] = 0
    swt_end = swtim
    if add_invert:
        swtinv_im = _SWT(inv_iim, edges, orientation, stroke_width, angle)  # the inverse
        swtinv_im[np.nonzero(swtinv_im < 0)] = 0

        indexes = np.nonzero(swtim == 0)
        swt_end[indexes] = swtinv_im[indexes]

    return swt_end

def hysthresh(image,T1,T2):
        if T1 < T2 :    # T1 and T2 reversed - swap values
            tmp = T1
            T1 = T2
            T2 = tmp

        aboveT2 = image > T2             # Edge points above lower threshold.
        [aboveTy, aboveTx] = np.nonzero(image > T1) # Row and colum coords of points above upper threshold.
        # Obtain all connected regions in aboveT2 that include a point that has a
        # value above T1
        bw = floodfill(aboveT2, aboveTy, aboveTx, 8)
        return bw

def cleanswt(swt,edges):
    """

    :param swt: Stroke Width Transform image
    :param edges: Edges image
    :return:
    """
    mask = swt[swt > 0]
    labeled,nr_objects = label(mask)
    h, w = swt.shape
    max_pix = (0.05 * w)
    for i in range(nr_objects):
        numpix = len(np.where(labeled == i))
        if(numpix < max_pix):
            swt[np.where(labeled==i)] = 0
    swt[edges > 0] = np.max(swt)
    return swt

def autoedge(nm, canthresh, blocksize, alpha_density = 1.25, beta_density = 0.25):
    """
    Generates automatic thresholding based on a percentage of expected white pixels.
    The idea is to move by patches evaluating density.
    :param nm:
    :param canthresh:
    :param blocksize:
    :return:
    """

    nm  = remove_borders(nm, 2)

    h, w = nm.shape
    patch_size = np.array([h,w]) / blocksize
    patch_size = np.uint16(patch_size)
    # size_pixels = patch_size[0] * patch_size[1]

    msize = h * w
    beta = 0.4

    max_pix = int(msize * canthresh)
    max_factor = np.max(nm)
    norm_nm = np.uint8((nm / max_factor) * 32.)
    hist, bin = np.histogram(norm_nm.ravel(), 32, [0, 32])
    hist = hist[::-1]
    cumsum = 0
    for ind, el in enumerate(hist):
        cumsum += el
        if cumsum > max_pix:
            min_factor_a = ((31 - ind + 1) / 32.) * max_factor
            break

    min_factor_a = min_factor_a + 0.1
    val_otsu = filters.threshold_otsu(nm)
    med = float(np.median(nm[nm > 0]))
    factor_b_p = beta * med

    max_factor_a = np.max([val_otsu, med, min_factor_a])

    expected_density = (msize * canthresh) / (blocksize*blocksize) # Expected

    edge_patches = nm.copy()

    if alpha_density > 0 :
        patches = view_as_blocks(nm, block_shape=(int(patch_size[0]), int(patch_size[1])))
        for i in range(blocksize):
            for j in range(blocksize):
                patch = patches[i,j,:,:]
                factor_a = max_factor_a
                edge_patch = hysthresh(patch, factor_a, factor_b_p)
                patch_density = np.sum(edge_patch)
                dense_enough = (patch_density < alpha_density*expected_density) and (patch_density >  beta_density*expected_density)
                while not dense_enough :
                    alpha = np.abs(patch_density - expected_density) / expected_density
                    if patch_density > alpha_density*expected_density :
                        factor_a = factor_a * (1.0 + alpha)
                    else:
                        factor_a = factor_a *(1-alpha)
                    if factor_a < min_factor_a :
                        factor_a = min_factor_a
                        edge_patch = hysthresh(patch, factor_a, factor_b_p)
                        break
                    patch_density_old = patch_density
                    edge_patch = hysthresh(patch, factor_a, factor_b_p)
                    patch_density = np.sum(edge_patch)
                    dense_enough = (patch_density < alpha_density*expected_density) and (patch_density > beta_density * expected_density) or patch_density == patch_density_old
                edge_patches[i * patch_size[0]:(i + 1) * patch_size[0],j * patch_size[1]:(j + 1) * patch_size[1]] = edge_patch
    else:
       edge_patches =  hysthresh(nm, min_factor_a*1.2, factor_b_p)
    return edge_patches

def kuwahara_filter(input,winsize):
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
     input = np.array(input,dtype = np.float64)
     m,n = input.shape
     if (winsize%4) != 1 :
        return

     tmpAvgKerRow = np.concatenate((np.ones( (1, (winsize - 1) / 2 + 1)), np.zeros((1, (winsize - 1) / 2))),axis=1)
     tmpPadder = np.zeros((1, winsize));
     tmpavgker = np.matlib.repmat(tmpAvgKerRow, (winsize - 1) / 2 + 1, 1)
     tmpavgker = np.concatenate((tmpavgker, np.matlib.repmat(tmpPadder, (winsize - 1) / 2, 1)))
     tmpavgker = tmpavgker / np.sum(tmpavgker)

     # tmpavgker is a 'north-west'
     t1,t2 = tmpavgker.shape
     avgker = np.zeros((t1,t2,4))
     avgker[:,:, 0] = tmpavgker # North - west(a)
     avgker[:,:, 1] = np.fliplr(tmpavgker) # North - east(b)
     avgker[:,:, 3] = np.flipud(tmpavgker) # South - east(c)
     avgker[:,:, 2] = np.fliplr(np.flipud(tmpavgker)) # South - west(d)

     squaredImg = input**2
     avgs = np.zeros((m,n,4))
     stddevs =  np.zeros((m,n,4))

     ## Calculation of averages and variances on subwindows
     for k in range(0,4):
        avgs[:,:, k] = convolve2d(input, avgker[:,:, k], 'same') # mean
        stddevs[:,:, k] = convolve2d(squaredImg, avgker[:,:, k], 'same') # mean
        stddevs[:,:, k] = stddevs[:,:, k]-avgs[:,:, k]**2 # variance

     # minima = np.min(stddevs, axis=2)
     indices = np.argmin(stddevs,axis = 2)
     filtered = np.zeros(input.shape)
     for k in range(m) :
        for i in range(n):
            filtered[k, i] = avgs[k, i, indices[k, i]]

     return filtered

def nonmaxsup_python(gradient,orientation,radius = 1.2):
        """
        # Input:
        #   inimage - Image to be non-maxima suppressed.

        #   orient  - Image containing feature normal orientation angles in degrees
        #             (0-180), angles positive anti-clockwise.
        #   radius  - Distance in pixel units to be looked at on each side of each
        #             pixel when determining whether it is a local maxima or not.
        #             This value cannot be less than 1.
        #             (Suggested value about 1.2 - 1.5)
        #    Returns:
        #   im        - Non maximally suppressed image.
        #
        # Notes:
        # The suggested radius value is 1.2 - 1.5 for the following reason. If the
        # radius parameter is set to 1 there is a chance that a maxima will not be
        # identified on a broad peak where adjacent pixels have the same value.  To
        # overcome this one typically uses a radius value of 1.2 to 1.5.  However
        # under these conditions there will be cases where two adjacent pixels will
        # both be marked as maxima.  Accordingly there is a final morphological
        # thinning step to correct this.

        # This function is slow.  It uses bilinear interpolation to estimate
        # intensity values at ideal, real-valued pixel locations on each side of
        #  pixels to determine if they are local maxima.

        # Function extracted from Copyright (c) 1996-2013 Peter Kovesi
        """

        if(radius<1):
            return


        # Precalculate x and y offsets relative to centre pixel for each orientation angle
        angle = range(0,181,1)
        angle = (np.array(angle)*np.pi)/180    # Array of angles in 1 degree increments (but in radians).
        xoff = radius*np.cos(angle)   # x and y offset of points at specified radius and angle
        yoff = radius*np.sin(angle)   # from each reference position.

        hfrac = xoff - np.floor(xoff) # Fractional offset of xoff relative to integer location
        vfrac = yoff - np.floor(yoff)    # Fractional offset of yoff relative to integer location

        orient = np.fix(orientation)    # Orientations start at 0 degrees but arrays start
                                        #  with index 1.
        orient = np.array(orient,dtype=np.int16)
        #  Now run through the image interpolating grey values on each side
        # of the centre pixel to be used for the non-maximal suppression.
        [h,w] = gradient.shape
        # iradius = int(math.ceil(radius))
        # nrow = range(iradius+1,rows - iradius)
        # ncol = range(iradius+1,cols - iradius)


        xoff_or = np.cos(orient*np.pi/180)*radius
        yoff_or = np.sin(orient*np.pi/180)*radius

        ind_x, ind_y = np.meshgrid(range(w), range(h))

        x_shift = ind_x + xoff_or
        y_shift = ind_y - yoff_or

        fx  = np.int16(np.floor(x_shift))
        cx = np.int16(np.ceil(x_shift))
        fy = np.int16(np.floor(y_shift))
        cy = np.int16(np.ceil(y_shift))

        top = np.minimum(w,h)
        fx[fx >  top-1] = 0
        cx[cx > top-1] = 0
        fy[fy >  top-1] = 0
        cy[cy > top-1] = 0

        fx[fx < 0 ] = 0
        cx[cx < 0 ] = 0
        fy[fy < 0 ] = 0
        cy[cy < 0 ] = 0

        gradient[0,0] = 0

        tl = gradient[fy, fx]  # Value at top left integer pixel location.
        tr = gradient[fy, cx]  # top right
        bl = gradient[cy, fx]  # bottom left
        br = gradient[cy, cx]  # bottom right

        upperavg = tl + hfrac[orient] * (tr - tl)  # Now use bilinear interpolation to
        loweravg = bl + hfrac[orient] * (br - bl)  # estimate value at x,y
        v1 = upperavg + vfrac[orient] * (loweravg - upperavg)

        ngrad = gradient.copy()

        ngrad[gradient < v1] = 0

        x_shift = ind_x - xoff_or
        y_shift = ind_y + yoff_or

        fx = np.int16(np.floor(x_shift))
        cx = np.int16(np.ceil(x_shift))
        fy = np.int16(np.floor(y_shift))
        cy = np.int16(np.ceil(y_shift))

        top = np.minimum(w, h)
        fx[fx > top-1] = 0
        cx[cx > top-1] = 0
        fy[fy > top-1] = 0
        cy[cy > top-1] = 0

        fx[fx < 0] = 0
        cx[cx < 0] = 0
        fy[fy < 0] = 0
        cy[cy < 0] = 0

        tl = gradient[fy, fx]  # Value at top left integer pixel location.
        tr = gradient[fy, cx]  # top right
        bl = gradient[cy, fx]  # bottom left
        br = gradient[cy, cx]  # bottom right

        upperavg = tl + hfrac[orient] * (tr - tl)  # Now use bilinear interpolation to
        loweravg = bl + hfrac[orient] * (br - bl)  # estimate value at x,y
        v2 = upperavg + vfrac[orient] * (loweravg - upperavg)

        ngrad[gradient < v2] = 0

        im = ngrad

        #  Finally thin the 'nonmaximally suppressed' image by pointwise
        #  multiplying itself with a morphological skeletonization of itself.
        #  I know it is oxymoronic to thin a nonmaximally supressed image but
        #  fixes the multiple adjacent peaks that can arise from using a radius
        #  value > 1.
        #
        # skel = bwmorph(im>0,'skel',Inf);
        #
        im2 = (im>0).astype(np.uint8)
        skel= morphology.skeletonize(im2)
        im = np.multiply(im,skel)
        return im

def floodfill(bw, r, c, N=8):
    filled = np.zeros(bw.shape)
    theStack = deque(zip(r, c))

    h, w = bw.shape
    while len(theStack) > 0:
        y, x = theStack.pop()
        if x < 0:
            x = 0
        if x >= w:
            x = w - 1
        if y < 0:
            y = 0
        if y >= h:
            y = h - 1
        if filled[y, x] == 1:
            continue
        if bw[y, x] == 0:
            continue
        filled[y, x] = 1

        theStack.append((y, x + 1))  # right
        theStack.append((y, x - 1))  # left
        theStack.append((y + 1, x))  # down
        theStack.append((y - 1, x))  # up
        if (N == 8):
            theStack.append((y + 1, x + 1))  # d right
            theStack.append((y - 1, x - 1))  # d left
            theStack.append((y + 1, x - 1))  # down
            theStack.append((y - 1, x + 1))  # up

    return filled

def borderEnhancer(img,filtersize):
    """
    Given an skeletonize image, enhances edges by the filtersize
    :param img:
    :param filtersize:
    :return:
    """
    # Estimate the local mean of f.
    prod_fs  = reduce(lambda x, y: x * y, filtersize, 1)
    localMean = convolve2d(img,np.ones(filtersize),'same') / prod_fs
    #  Estimate of the local variance of f.
    img_2 = np.multiply(img,img)
    localMean_2 = localMean*localMean
    localVar =  convolve2d(img_2,np.ones(filtersize),'same') / prod_fs - localMean_2
    localVar = localVar>0
    return localVar

def calculateOrientations(img, gradient = None):
    if gradient is None:
        gradient, _ = canny(img, 2)
    ORIENTIM, _ = ridgeorient(gradient, 1, 5, 5)
    segments = slic(img / 255., n_segments=2500, sigma=1.5, compactness=0.08)
    num_labels = np.max(segments) + 1
    orientim_slic = np.copy(ORIENTIM)
    for i in range(num_labels):
            orientim_slic[np.where(segments == i)] = np.median(ORIENTIM[np.where(segments == i)])
    return orientim_slic


#import matplotlib.pyplot as plt
#image = cv2.imread("D:/TESTS\\p0_20180506_162915\\ref_0_8W_201805061635068188.tif",0)
#soft(image)
