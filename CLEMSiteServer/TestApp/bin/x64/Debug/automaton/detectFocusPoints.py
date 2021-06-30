
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
from skimage.segmentation import felzenszwalb,slic
from skimage.segmentation import mark_boundaries
from skimage.filters.rank import enhance_contrast_percentile #enhance_contrast
from skimage.util import img_as_float
from skimage import io
from scipy.signal  import convolve2d, convolve
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
from imutils import writeErrorFile,integral_image,integrate, blackBorderDetection
from skimage.morphology import disk
from imutils import gaussfilt


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

def SLICthresholding(img):
    rows, cols = img.shape
    #segments = felzenszwalb(img, scale=500, sigma=0, min_size=min(500, (rows * cols / 500)))
    #total_slics = np.max(segments) + 1
    #if total_slics == 1:
    segments = slic(img, n_segments=300, sigma=3, compactness=0.08)
    total_slics = np.max(segments) + 1

    med_list = []
    # Sorting of indexes speeds ups the process of calculating median values
    flat = segments.ravel()
    lin_idx = np.argsort(flat, kind='mergesort')
    sp_ind = np.split(lin_idx, np.cumsum(np.bincount(flat)[:-1]))
    im_1b_f = img.ravel()
    for i in range(total_slics):
        el_med = np.median(im_1b_f[sp_ind[i]])
        med_list.append([el_med])
    k = KMeans(n_clusters=3)
    # K-Means and get 3 clusters,
    k.fit(med_list)
    centers = k.cluster_centers_
    paint_white = np.argmax(centers)
    paint_black = np.argmin(centers)
    white_val = centers[paint_white]
    black_val = centers[paint_black]
    centers = np.delete(centers,[paint_white,paint_black])
    gray_val = centers[0]

    nimg_f = img.ravel()
    white_ind = []
    gray_ind = []
    for i in range(total_slics):
        if (k.labels_[i] == paint_white):
            white_ind.append(sp_ind[i])
            nimg_f[sp_ind[i]] = 255
        elif (k.labels_[i] == paint_black):
            nimg_f[sp_ind[i]] = 0
        else:
            gray_ind.append(i)

    w_i = np.mean(np.concatenate(white_ind))


    for i in gray_ind:
        ind = np.mean(sp_ind[i])
        if(ind<w_i):
            nimg_f[sp_ind[i]] = 255
        else:
            nimg_f[sp_ind[i]] = 0

    return img, [white_val, black_val, gray_val]

def maxOrientations(iimage, stop_point, sigmaD=1.0, sigmaI=1.5, count=125 ,top_border = 400):
    '''
    The input image
    should be a 2D numpy array.  The sigmaD and sigmaI parameters define
    the differentiation and integration scales (respectively) of the
    feature detector---the defaults are reasonable for many images.
    '''
    rimage = iimage.copy()
    ho,wo = rimage.shape
    r = 1.0
    if(ho>1024 and wo>1024):
        r = 1024.0 / wo
        dim = (1024, int(ho * r))
        # perform resizing to speed up
        rimage = cv2.resize(rimage, dim, interpolation=cv2.INTER_AREA)
        stop_point = int(r*stop_point)
    image = rimage.astype(np.float32)

    # Calculate image gradients.
    if sigmaD < 0.4:
        sigmaD = 0.4
    sze = int(np.fix(6 *sigmaD))
    if (sze % 2 == 0):
        sze = sze + 1
    h = fspecial_gauss2D((sze, sze), sigmaD)
    fx, fy = np.gradient(h)  # Gradient of Gausian.

    Gx = convolve2d(image, fx, 'same')  # Gradient of the image in x
    Gy = convolve2d(image, fy, 'same')  # ... and y

    # Estimate the local ridge orientation at each point by finding the
    # principal axis of variation in the image gradients.

    Gxx = np.multiply(Gx, Gx)  # Covariance data for the image gradients
    Gxy = np.multiply(Gx, Gy)
    Gyy = np.multiply(Gy, Gy)

    # Now smooth the covariance data to perform a weighted summation of the  data.
    if sigmaI < 0.4:
        sigmaI = 0.4

    sze = int(np.fix(6 * sigmaI))
    if (sze % 2 == 0):
        sze = sze + 1
    h = fspecial_gauss2D((sze, sze), sigmaI)
    Gxx = convolve2d(Gxx, h, 'same');
    Gxy = 2 * convolve2d(Gxy, h, 'same');
    Gyy = convolve2d(Gyy, h, 'same');

    Gxy_2 = np.multiply(Gxy, Gxy)
    # compute Harris feature strength, avoiding divide by zero
    imgH = (Gxx * Gyy - Gxy_2) / (Gxx + Gyy + 1e-8)

    # non-maximum suppression in nxn regions
    maxH = filters.maximum_filter(imgH, (20,20))
    imgH = imgH * (imgH == maxH)

    # exclude points near the image border
    border_bottom = stop_point
    if(stop_point > 30):
        border_bottom = stop_point-30

    imgH[:border_bottom,:] = 0

    border_top = stop_point+top_border
    imgH[border_top:,:] = 0
    imgH[:,:80] = 0
    imgH[:,-80:] = 0


    # sort points and find their positions
    sortIdx = np.argsort(imgH.flatten())[::-1]
    sortIdx = sortIdx[:count]
    hr,wr = imgH.shape
    yy = sortIdx / wr
    xx = sortIdx % wr
    yy = yy*(wo/(wr*1.0))
    xx = xx*(ho/(hr*1.0))
    yy = yy.astype(np.int)
    xx = xx.astype(np.int)
    return xx,yy

def preprocess(iimg, entropy = True):
    """
    Does SLIC segmentation


    :param iimg: Image
    :return:
    """
    # White more white!!

    img = iimg.copy()
    h,w = iimg.shape
    r = 1.0
    if(h>1024 and w>1024):
        r = 1024.0 / w
        dim = (1024, int(h * r))
        # perform resizing to speed up
        rimg = cv2.resize(iimg, dim, interpolation=cv2.INTER_AREA)
    else:
        rimg = img

    rows,cols = rimg.shape
    im_1b = cv2.GaussianBlur(rimg, (21,21), 0)
    nimg = np.array(im_1b)
    # Local contrast enhancement
    enh = enhance_contrast_percentile(nimg, disk(5), p0=.1, p1=.9)
    # Project image to find gradient. Maximum gradient change over the projection indicates the value where
    # it maximizes the white upper part and it has the biggest slope change
    projection = np.sum(enh, axis= 1)
    dsignal    = convolve(projection,np.array([-1,0,1]),mode='same')
    stop_point_1 = np.argmax(dsignal[2:len(dsignal)-20])

    val = np.median(iimg[0:stop_point_1,:])
    if(val<190): # gray value
        return iimg, 0

    nimg, _ = SLICthresholding(enh.copy())


    #This retrieves the SMALLEST stop point
    vals = [ el for el in range(0,cols,int(cols*0.25))]
    vals[0] = 30
    vals[3] = cols-30
    stop_points = []
    for x in vals:
        y = 10 # avoid border effects
        stop = False
        while(y<rows and not stop):
            if(nimg[y,x]<255):
                if(y < cols*0.8):
                    stop_points.append(y)
                stop = True
            else:
                y = y + 1
    stop_points = np.array(stop_points)
    stop_point = np.min(stop_points)

    stop_point = max(stop_point_1,stop_point)

    # This stop_point could include part of the cell. To avoid that:
    if stop_point>0 and entropy:
        stop_point = confirmStopPoint(enh[:stop_point,:],stop_point)

    final_img = cv2.GaussianBlur(iimg, (21, 21), 0)

    if stop_point>0 :
        stop_point = int(math.ceil(stop_point / r))
        final_img[0:stop_point,:]=0

    return final_img,stop_point



def nonmaxsup1D(isignal,npeaks,window, top = None):
    signal = isignal.copy()
    k = 0
    peaks = np.zeros((npeaks,2))
    num = 1.0
    sig_min = np.min(signal)
    if top is None:
        top = sig_min
    while(npeaks>0):
        num = np.max(signal)
        indx    = np.argmax(signal)
        if(num < top): break
        peaks[k,0] = num
        peaks[k,1] = indx
        for i in range(indx-window,indx+window):
            if(i>=0 and i<len(signal)):
                signal[i]= sig_min
        npeaks = npeaks-1
        k=k+1
    return peaks

def confirmStopPoint(iimg, stop_point):
    # If the minimum y is bigger than 100 pixels in height
    # we have to repeat to decide if we have the following:
    # - Uniform data, belonging upper part, coating. Low entropy
    # - Non - uniform data, belonging to a cell. High entropy value
    # - Uniform data, black part. Low entropy data.
    img_prob = np.zeros(iimg.shape)
    dict_hist = []
    # Quantize image to 50 levels
    n = 100  # Number of levels of quantization
    indices = np.arange(0, 256)  # List of all colors
    divider = np.linspace(0, 255, n + 1)[1]  # we get a divider
    quantiz = np.uint8(np.linspace(0, 255, n))  # we get quantization colors
    levels = np.clip(np.uint8(indices / divider), 0, n - 1)
    palette = quantiz[levels]  # Creating the palette
    iimg = palette[iimg]  # Applying palette on image

    hist, _ = np.histogram(iimg, bins=256, range=(0, 256))
    for i in range(iimg.shape[0]):
        for j in range(iimg.shape[1]):
            img_prob[i,j] = hist[iimg[i,j]]+1e-15

    entropy = -np.log2(np.mean(np.array((img_prob), dtype=np.float32), axis=1))
    # ent2 = savitzky_golay(entropy, 101, 3) Only used for long samples
    # this return the stop_point
    if np.mean(iimg)<40: # We are touching black
        return 0

    if(np.mean(entropy[0:10])>3.4) : # We are touching cell
        return 0

    # Otherwise we have a mix or just interface
    window = int(iimg.shape[0] * 0.25)
    if window < 1: window = 1
    pt_stop_point = nonmaxsup1D(np.gradient(entropy), 1, int(window))
    # Three possibilities : interface, interface+cell or cell
    # If interface, then the entropy is very low, regions are ordered, close to 0
    # score = np.mean(np.gradient(entropy[:int(pt_stop_point[0][1]-iimg.shape[0]*0.25)]))
    if pt_stop_point[0][1] < stop_point*0.9 : # We give x pix margin
        ntop = int(pt_stop_point[0][1])
        if ntop == 0:
            return stop_point
        else:
            return ntop
        #nsignal = entropy[:ntop]
        #nsignal = nsignal[::-1]
        #stop_point = ntop - np.argmin(nsignal)*0.5

    return stop_point

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    from math import factorial


    window_size = np.abs(np.int(window_size))
    order = np.abs(np.int(order))
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')



from skimage.feature import local_binary_pattern

def kullback_leibler_divergence(p, q):
    p = np.asarray(p)
    q = np.asarray(q)
    filt = np.logical_and(p != 0, q != 0)
    return np.sum(p[filt] * np.log2(p[filt] / q[filt]))

# Compare images
def match(img, radius = 3, n_points = 24):
    cell = cv2.imread('cell.png',0)
    surface = cv2.imread('surface.png')

    refs = {
        'cell': local_binary_pattern(cell, n_points, radius, 'uniform'),
        'surface': local_binary_pattern(surface, n_points, radius, 'uniform')
    }

    best_score = 10
    best_name = None
    lbp = local_binary_pattern(img, n_points, radius, 'uniform')
    n_bins = int(lbp.max() + 1)
    hist, _ = np.histogram(lbp, normed=True, bins=n_bins, range=(0, n_bins))
    for name, ref in refs.items():
        ref_hist, _ = np.histogram(ref, normed=True, bins=n_bins,
                                   range=(0, n_bins))
        score = kullback_leibler_divergence(hist, ref_hist)
        if score < best_score:
            best_score = score
            best_name = name
    return best_name

def calculateEntropy(iimg, total = False):
    # - Uniform data, black part. Low entropy data.
    img_prob = np.zeros(iimg.shape)
    dict_hist = []
    # Quantize image to 50 levels
    n = 100  # Number of levels of quantization
    indices = np.arange(0, 256)  # List of all colors
    divider = np.linspace(0, 255, n + 1)[1]  # we get a divider
    quantiz = np.uint8(np.linspace(0, 255, n))  # we get quantization colors
    levels = np.clip(np.uint8(indices / divider), 0, n - 1)
    palette = quantiz[levels]  # Creating the palette
    iimg = palette[iimg]  # Applying palette on image

    hist, _ = np.histogram(iimg, normed=True, bins=256, range=(0, 256))
    for i in range(iimg.shape[0]):
        for j in range(iimg.shape[1]):
            img_prob[i, j] = hist[iimg[i, j]] + 1e-15

    entropy = -np.log2(np.mean(np.array((img_prob), dtype=np.float32), axis=1))
    if total:
        entropy = -np.log2(np.mean(np.array(entropy, dtype=np.float32), axis=0))
    return entropy


from skimage.filters import threshold_minimum
def removeLowVariancePoints(iimg,imgor,finalx,finaly,border_x = 200, border_y = 200, variance_thresh = 12):
    """

    :param img: Image from where the integral image is computed
    :param imgor: Image where selected points will be shown
    :param finalx: list of points  x coordinates
    :param finaly: list of points  y coordinates
    :param border_x: Border to consider points (points outside borders will not be considered
    :param border_y: Same with Height
    :param variance_thresh: Variance of gray levels allowed
    :return:
    """
    h, w = iimg.shape
    # max min normalization for thresholds
    min_im = np.min(iimg[iimg>0])
    img =  np.uint8(((imgor-min_im)/(np.max(imgor)-min_im))*255)
    img = gaussfilt(img,1.5)
    img[iimg==0]=0
    nhood_s = np.min([h,w])
    # For each point assess the variance. If variance is small the value is discarded
    # First calculate integral image
    nhood = np.array([nhood_s,nhood_s])*0.1
    nhood[0] = np.max([2 * np.ceil(nhood[0] * 0.5) + 1, 0])  # Make sure the nhood size is odd.
    nhood[1] = np.max([2 * np.ceil(nhood[1] * 0.5) + 1, 0])
    nhood_center = (nhood-1)/2

    intimg = integral_image(img)
    img_2 = np.array(img,dtype = np.uint64)
    intimg_2 = integral_image(np.multiply(img_2,img_2))

    # n = (nhood[0] * nhood[1])
    # p is y
    # q is x
    limit1 = img.shape[1] - border_x  #  CAREFUL
    limit2 = img.shape[0] - border_y

    count = 0
    non_valid = []
    variance_list = []
    for q,p in zip(finalx,finaly):
        if(q>limit1 or p>limit2):
            non_valid.append(count)
            print("Non valid point detected at:"+str(p)+","+str(q))
            count += 1
            continue
        # Suppress this maximum and its close   neighbors.
        p1 = int(p) - nhood_center[0]
        p2 = int(p) + nhood_center[0]
        q1 = int(q) - nhood_center[1]
        q2 = int(q) + nhood_center[1]

        p1 = int(np.max([p1, 0]))
        p2 = int(np.min([p2, img.shape[0]-1]))
        q1 = int(np.max([q1, 0]))
        q2 = int(np.min([q2, img.shape[1]-1]))


        # Create a square around the maxima to be supressed
        x = range(q1,q2)
        y = range(p1,p2)
        [qq, pp] = np.meshgrid(x, y)  # 'xy' default, can return i,j
        patch = img[pp, qq]
        n = patch.shape[0]*patch.shape[1]
        # Calculate Variance inside the patch
        S1 = integrate(intimg, p1, q1, p2, q2)
        S2 = integrate(intimg_2, p1, q1, p2, q2)

        mean_S = S1/n
        variance = np.abs(((S1/n)*(S1/n))-S2/n)
        sd = np.sqrt(variance)
        # entropy = calculateEntropy(np.uint8(patch),total=True)
        if sd < variance_thresh or mean_S < 35 : # or entropy>-1.5:  # Low variance and mean values small. Darkness is around 25, remove point
            non_valid.append(count)
        else:
            variance_list.append(variance)
        count += 1

    fx = np.delete(finalx, np.array(non_valid))
    fy = np.delete(finaly, np.array(non_valid))
    return fx,fy,np.array(variance_list,dtype=np.float32),imgor

def detectPointsFile(file_im, tag, remove_black = False, tpoints = 6):
    imgor = cv2.imread(file_im,0)
    if(remove_black):
        imgor, _ = blackBorderDetection(imgor)

    folder_store, file = path.split(file_im)
    if imgor.size == 0:
        writeErrorFile("In DetectPoints : Image NOT FOUND",folder_store)
        return False
    return detectPoints(imgor, folder_store,tag, tpoints)

def detectPoints(imgor, folder_store, tag, tpoints, top_border = 300, pixelsize = 1.0):

    go_down = 20
    if(pixelsize<0.025):
        go_down = int(1/(2*pixelsize))

    img,stop_point = preprocess(imgor)
    im2, stop_point2 = preprocess(img[stop_point:,:],entropy=False)
    # Avoid lack of coating... If the coat goes away, the entropy will detect the upper part as part of a cell
    # To avoid this we use again preprocessing but now without entropy detection, so the cell is thresholded again in 3 groups
    if(stop_point2 > 10):
        stop_point = stop_point+stop_point2

    xx,yy = maxOrientations(img,stop_point,top_border=top_border)

    k = KMeans(n_clusters=25)
    # K-Means and get 30 clusters, from each cluster, get the three closest to center and from them get the maximum value
    values = [ val for val in  zip(xx,yy)]
    k.fit(values)
    centers = k.cluster_centers_

    xx_c = centers[:,0]
    yy_c = centers[:,1]

    # Sort in distance from the center
    h,w = img.shape
    distance_ind = np.sqrt((xx_c-w/2)*(xx_c-w/2) + (yy_c-stop_point+20)*(yy_c-stop_point+20))
    sortIdx2 = np.argsort(distance_ind)

    finaly = yy_c[sortIdx2]
    finalx = xx_c[sortIdx2]

    # Check for each point that in y is smaller than half, y has to be lowered to the stop_point
    find = [ind for ind,el in enumerate(finaly) if el > (stop_point+h*0.5)]
    non_valid = set(find)
    non_valid = list(non_valid)
    finalx = np.delete(finalx,np.array(non_valid,dtype = np.int32))
    finaly = np.delete(finaly,np.array(non_valid, dtype = np.int32))

    for ind, el in enumerate(finaly) :
        if el < (stop_point + go_down):
            finaly[ind] = stop_point+go_down

    finalx,finaly,varianceValues,img_t = removeLowVariancePoints(img,imgor,finalx,finaly,variance_thresh=15)

    # Repeat analysis of variance for selected points
    if finaly.size == 0:
        return False

    # Sort in distance from the center AGAIN, weighted by variance
    h, w = img.shape
    eps = 1e-15
    distance_ind = varianceValues/(((finalx - w / 2) * (finalx - w / 2) + (finaly - (stop_point + h/5) ) * (finaly - (stop_point + h/5)))+eps)
    sortIdx2 = np.argsort(-distance_ind)

    finaly = finaly[sortIdx2]
    finalx = finalx[sortIdx2]


    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    ax.imshow(img_t, cmap='gray', interpolation='none')
    ax.set_axis_off()
    tpoints = min(tpoints,len(finalx))
    finalx = finalx[:tpoints]
    finaly = finaly[:tpoints]
    for i, txt in enumerate(finalx):
        ax.annotate(i+1, (finalx[i], finaly[i]),color="white")
    plt.scatter(xx,yy,c='red',edgecolors='black', s=5, zorder = 1)
    plt.scatter(centers[:,0], centers[:,1],c='green',edgecolors='black', zorder=1)
    plt.scatter(finalx,finaly,c='blue',edgecolors='black', zorder =1)


    plt.axis('off')
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                    hspace=0, wspace=0)

    plt.gca().xaxis.set_major_locator(NullLocator())
    plt.gca().yaxis.set_major_locator(NullLocator())
    plt.margins(0, 0)

    fig.savefig(folder_store+'\\'+tag+'.png', dpi=300,bbox_inches='tight',pad_inches = 0)   # save the figure to file
    plt.close(fig)    # close the figure

    # For each point get patch around the centroid.
    h, w = imgor.shape
    finalx = finalx - w * 0.5
    finaly = finaly - h * 0.5

    if(finalx.size == 0):
        return False
    finalx *= pixelsize
    finaly *= pixelsize
    file_data = folder_store+"\\"+tag+".csv"
    with open(file_data, 'w') as f:
        counter = 0;
        for el in zip(finalx,finaly):
            if pixelsize == 1:
                f.write("c_"+str(counter)+";"+str(int(el[0]))+";"+str(int(el[1]))+"\n")
            else:
                f.write("c_" + str(counter) + ";" + str(float(el[0])) + ";" + str(float(el[1])) + "\n")
            counter += 1
    return True

def main():
    try:
        file_im = sys.argv[1]
        tag = sys.argv[2]
        folder_store, _= path.split(file_im)
        if(not detectPointsFile(file_im,tag)):
            writeErrorFile("No points detected or unexpected ERROR",folder_store)
    except SystemExit:
        pass
    except :
        pass

if __name__ == "__main__":
    main()