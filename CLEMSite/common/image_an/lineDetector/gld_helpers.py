

from common.image_an.image_utils import *
import numpy as np
import math
import cv2
import itertools
from scipy.signal  import convolve2d
from scipy.spatial.distance import pdist
from itertools import combinations
from phasepack import phasecongmono
from scipy.spatial import KDTree

class GLDException(Exception):
    pass


def getPeaks(img, img_p, gridsize, orientations = None, angle = 45, minpeaks = 2, threshold = 0.1):
    """
        getPeaks, given an image, its orientations image (can be calculated if not given), finds all
        peaks happening at certain angle. A minimum of peaks has to be given.
    """
    error = 0
    if orientations is None:
        orientations = calculateOrientations(img)


    prj_pos = projections(img_p, orientations, aspace=[angle], arange=10)
    prj_neg = projections(img_p, orientations, aspace=[-angle], arange=10)

    peaks_pos, hnew = detectPeaksNMS(prj_pos, numpeaks=minpeaks*3, threshold=threshold, nhood=None)
    peaks_neg, hnew = detectPeaksNMS(prj_neg, numpeaks=minpeaks*3, threshold=threshold, nhood=None)

    try:
        ppeaks, npeaks = discardwrongpeaks(prj_pos + prj_neg, peaks_pos, peaks_neg,
                                              gridsize, min_peaks=minpeaks)  # based on the grid definition
    except GLDException as g:
        print("In getPeaks of gld_helpers:"+str(g))
        return np.array([]), np.array([]), []

    ppeaks = np.array(ppeaks).reshape(-1, 3)
    npeaks = np.array(npeaks).reshape(-1, 3)
    if len(ppeaks)<2 or len(npeaks)<2:
        return np.array([]), np.array([]), []
    if len(ppeaks)>2 or len(npeaks)>2:
        mag_p = np.argsort(ppeaks[:, 2])
        mag_n = np.argsort(npeaks[:, 2])
        # keep only the biggest two
        ppeaks = ppeaks[mag_p[0:2],2]
        npeaks = npeaks[mag_n[0:2], 2]
    return ppeaks, npeaks, (prj_neg + prj_pos)


def projections(iswt, iorient, K=20, inc=1, aspace=None, arange=None):
    """



    :param iswt:
    :param iorient:
    :param K:
    :param inc:
    :param aspace:
    :param arange:
    :return:
    """
    if K < 4 or K > 1024:
            raise GLDException('In GLD.projections : Invalid average value. Accepted values between 4 and half the size of your image. Setting default value.')

    if inc > 90 or inc < 0:
            raise GLDException('In GLD.projections : Invalid Delta, must be positive and less than 90')

    # pad the image with zeros so we don't lose anything when we rotate.
    iLength, iWidth = iswt.shape
    iDiag = math.sqrt(iLength ** 2 + iWidth ** 2)
    LengthPad = math.ceil(iDiag - iLength)
    WidthPad = math.ceil(iDiag - iWidth)

    padIMG = np.zeros((iLength + LengthPad, iWidth + WidthPad))
    pad1 = int(math.ceil(LengthPad / 2))
    pad2 = int(math.ceil(LengthPad / 2) + iLength)

    pad3 = int(math.ceil(WidthPad / 2))
    pad4 = int(math.ceil(WidthPad / 2) + iWidth)
    padIMG[pad1:pad2, pad3:pad4] = iswt

    padIMGOR = np.zeros((iLength + LengthPad, iWidth + WidthPad))
    padIMGOR[pad1:pad2, pad3:pad4] = iorient
    #
    #  loop over the number of angles, rotate 90-theta (because we can easily sum
    #  if we look at stuff from the top), and then add up.  Don't perform any
    #  interpolation on the rotating.
    #
    #   -90 and 90 are the same, we must remove 90
    THETA = list(range(-90, 91, inc))
    th = np.zeros(len(THETA)) + np.inf
    if (arange):
        for ang in aspace:
            k = int(ang + 90)
            kplus = k + arange
            kminus = k - arange
            if kplus > 180:
                kplus = 180
            if kminus < 0:
                kminus = 0
            th[k:kplus] = THETA[k:kplus]
            th[kminus:k] = THETA[kminus:k]
    else:
        th = THETA
    th = np.array(th, dtype=np.float32) * np.pi * (1 / 180.0)

    n = len(THETA)
    PR = np.zeros((padIMG.shape[1], n))
    M = padIMG  # > 0

    iPL, iPW = padIMG.shape
    center = (iPL / 2, iPW / 2)
    for i in range(n):
        if (th[i] != np.inf):
            #if th[i]<0 :
            #    final = -oft(M, K, padIMGOR, th[i])
            #else :
            final = oft(M, K, padIMGOR, th[i])
            Mt = cv2.getRotationMatrix2D(center, -THETA[i], 1.0)
            rotated = cv2.warpAffine(final, Mt, (iPL, iPW))
            PR[:, i] = (np.sum(rotated, axis=1))
        else:
            PR[:, i] = 0

    PR[np.nonzero(PR < 0)] = 0.0
    PR = PR / iDiag
    PR = PR * 10
    PR = np.multiply(PR, PR)
    PR = PR * 0.1
    PR = PR / np.max(PR)
    return PR


def projectionsOneE(iswt, angle):
    """
    Simplified version of the projections algorithm
    :param iswt:
    :param angle:
    :return:
    """
    # pad the image with zeros so we don't lose anything when we rotate.
    iLength, iWidth = iswt.shape
    iDiag = math.sqrt(iLength ** 2 + iWidth ** 2)
    LengthPad = math.ceil(iDiag - iLength) + 1
    WidthPad = math.ceil(iDiag - iWidth) + 1

    padIMG = np.zeros((iLength + LengthPad, iWidth + WidthPad))
    pad1 = int(math.ceil(LengthPad / 2))
    pad2 = int(math.ceil(LengthPad / 2) + iLength)

    pad3 = int(math.ceil(WidthPad / 2))
    pad4 = int(math.ceil(WidthPad / 2) + iWidth)
    padIMG[pad1:pad2, pad3:pad4] = iswt

    iPL, iPW = padIMG.shape
    center = (iPL / 2, iPW / 2)

    Mt = cv2.getRotationMatrix2D(center, -angle, 1.0)
    rotated = cv2.warpAffine(padIMG, Mt, (iPL, iPW))
    PR = (np.sum(rotated, axis=1))

    PR[np.nonzero(PR < 0)] = 0.0
    PR = PR / iDiag
    PR = PR * 10
    PR = np.multiply(PR, PR)
    PR = PR * 0.1
    PR = PR / (np.max(PR) + 1e-15)
    return PR


def oft( M, K, L, ang, probabilistic=True):
    """

    :param M:
    :param K:
    :param L: orientations
    :param ang:
    :param probabilistic:
    :return:
    """
    kernel = np.zeros((K, K))
    v_cos = math.cos(ang)
    v_sin = math.sin(ang)
    Mval = np.cos(2 * (L - ang))
    if probabilistic:
        Mval = Mval * M
    count = 0
    for k in range(-int(K / 2) - 2, int(K / 2) + 2):
        ni = round(K / 2 + k * v_cos)
        nj = round(K / 2 - k * v_sin)
        if ((ni > -1 and ni < K) and (nj > -1 and nj < K)):
            kernel[nj, ni] = 1
            count += 1

    kernel = kernel / count

    cO = convolve2d(Mval, kernel, 'same')
    Or = np.zeros(M.shape)
    Or[np.nonzero(M)] = cO[np.nonzero(M)]
    return Or


def translateAngle(deg):
    """
    Translates Angle to be -180 to 180
    :param deg: angle in 0-360
    :return: angle in -180 to 180
    """
    if (deg >= 180):
        return (360 - deg)-90
    else:
        return ((360 - deg)-180)


def detectPeaksNMS(h, numpeaks=1, threshold=None, nhood=None):
    """
    FindPEAKS Identify peaks in SOFT transform.
       PEAKS = detectPeaksNMS(H,NUMPEAKS) locates peaks in projection space.
    NUMPEAKS specifies the maximum number of peaks to identify. PEAKS is
    a Q-by-2 matrix, where Q can range from 0 to NUMPEAKS. Q holds
    the row and column coordinates of the peaks. If NUMPEAKS is
    omitted, it defaults to 1.

    'Threshold' Nonnegative scalar.
               Values of H below 'Threshold' will not be considered
               to be peaks. Threshold can vary from 0 to Inf.
               Default: 0.5*max(H(:))

    'NHoodSize' Two-element vector of positive odd integers: [M N].
               'NHoodSize' specifies the size of the suppression
                neighborhood. This is the neighborhood around each
                peak that is set to zero after the peak is identified.
               Default: smallest odd values greater than or equal to
                        size(H)/50.
    H is the output of the projections function. NUMPEAKS is a positive
    integer scalar.
    """
    # Set the defaults if necessary
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    if nhood is None:
        nhood = np.array(h.shape) / (h.shape[0] * 0.05)
        nhood = 2 * np.array(nhood * 0.5, dtype=np.int32) + 1  # Make sure the nhood size is odd.
        if nhood[0] == 0: nhood[0] = 1
        if nhood[1] == 0: nhood[1] = 1

    if not threshold:
        threshold = 0.5 * np.max(h.flatten())
    # initialize the loop variables
    done = False
    hnew = h.copy()
    nhood_center = np.array((nhood - 1) / 2, dtype=np.int32) + 1
    peaks = []
    while not done:
        max_ind = np.argmax(hnew)  # ok
        p, q = np.unravel_index(max_ind, hnew.shape)
        if hnew[p, q] >= threshold:
            if (q == 179 or q == 180):
                hnew[:, 0:3] = np.flipud(hnew[:, 0:3])  # Invert -89 and -88 to be like 90
            if (q == 0 or q == 1):
                hnew[:, 179:181] = np.flipud(hnew[:, 179:181])  # Invert -89 and -88 to be like 90

            peaks.append([p, q, hnew[p, q]])  # add the peak to the list
            p1 = p - nhood_center[0]
            p2 = p + nhood_center[0]
            q1 = q - nhood_center[1]
            q2 = q + nhood_center[1]

            # Create a square around the maxima to be supressed
            qq, pp = np.meshgrid(range(q1 + 1, q2 + 1), range(max(p1 + 1, 0), min(p2 + 1, h.shape[0])), indexing='ij')
            qq = qq.flatten()
            pp = pp.flatten()

            # For coordinates that are out of bounds in the theta
            # direction, we want to consider that is circular
            # for theta = +/- 90 degrees.
            theta_too_low = np.where(qq < 0)
            if theta_too_low:
                qq[theta_too_low] = h.shape[1] + qq[theta_too_low]

            theta_too_high = np.where(qq >= h.shape[1])
            if theta_too_high:
                qq[theta_too_high] = qq[theta_too_high] - h.shape[1]
            # Convert to linear indices to zero out all the values.
            for ind, _ in enumerate(pp):
                hnew[pp[ind], qq[ind]] = 0
            if (q == 179 or q == 180):
                hnew[:, 0:3] = np.flipud(hnew[:, 0:3])  # After supress, return the signal to normality
            if (q == 0 or q == 1):
                hnew[:, 179:181] = np.flipud(hnew[:, 179:181])  # Supress the complementary too

            done = (len(peaks) == numpeaks)
        else:
            done = True

    for ind, el in enumerate(peaks):
        peaks[ind][1] = el[1] - 90

    return np.array(peaks, dtype=np.float32), hnew


def splitpeaks(peaks):
    pos_peaks = [ peak for peak in peaks if peak>-1]
    neg_peaks = [ peak for peak in peaks if peak<0]
    return pos_peaks, neg_peaks


def swap_points(changelist, visitedlist, receivinglist):
    """

    :param changelist: list of values belonging to receiving
    :param visitedlist: list examined
    :param receivinglist: if the value from changelist is in visitedlist, put it in receivinglist
    :return: updated visited and receiving lists
    """
    deleted = []
    for ind, point in enumerate(visitedlist):
        if point[1] in changelist:
            if len(receivinglist) == 0:
                receivinglist = [point]
            else:
                receivinglist = np.squeeze(np.concatenate([receivinglist, [point]]))
            deleted.append(ind)
    if len(deleted)> 0 :
        visitedlist = np.array(list(itertools.compress(visitedlist, [i not in deleted for i in range(len(visitedlist))])))
        if not np.any(visitedlist):
            visitedlist = np.array([],dtype=np.float32)
    return visitedlist, receivinglist


def select_complementary_angles(positivePairs,negativePairs, deviation = 5):
    """

    :param positivePairs:
    :param negativePairs:
    :param deviation:
    :return:
    """

    anglepos = np.array([peak[1] for peak in positivePairs])
    angleneg = np.array([peak[1] for peak in negativePairs])

    pos_ang = np.unique(anglepos)
    neg_ang = np.unique(angleneg)
    good_angles_pos = set()
    good_angles_neg = set()

    # now make 90 degrees pairs
    # Combinations of positive and negative should be close to
    # 90+/-5
    for elp in pos_ang:
        for eln in neg_ang:
            nty = np.abs(elp) + np.abs(eln)
            if (nty > 90-deviation and nty < 90+deviation):  # good combination
                good_angles_pos.add(elp)
                good_angles_neg.add(eln)

    if len(good_angles_pos)<0:
        raise GLDException('The angle orientations are not close to 90 degrees.')

    good_pos = [positivePairs[ind] for ind, angle in enumerate(anglepos) if angle in good_angles_pos]
    good_neg = [negativePairs[ind] for ind, angle in enumerate(angleneg) if angle in good_angles_neg]
    return good_pos, good_neg


def filter_angles(positivePairs, negativePairs):
    """

    :param positivePairs:
    :param negativePairs:
    :return:
    """
    # We have to group angles in complementary sets:
    # -2,-1,0,1,2 go together if there is one of the following complementaries [88,89,90,-90,-89,-88]
    # And viceversa
    positive_list = [-2,-1,0,1,2]
    negative_list = [88,89,90,-90,-89,-88]

    # Polarize angles
    #negativePairs, positivePairs = swap_points(positive_list,negativePairs, positivePairs)
    #positivePairs, negativePairs = swap_points(negative_list, positivePairs, negativePairs)

    # Get only complementaries
    positivePairs, negativePairs = select_complementary_angles(positivePairs, negativePairs, 5)

    anglepos = np.array([peak[1] for peak in positivePairs])
    angleneg = np.array([peak[1] for peak in negativePairs])

    pos_ang = np.unique(anglepos)
    neg_ang = np.unique(angleneg)


    # topval = 91
    fangpos = pos_ang
    fangneg = neg_ang
    topscore = 1 # maximum score between 1 and 2
    for elp in positivePairs:
        for eln in negativePairs:
            val = np.abs(np.abs(elp[1] - eln[1]) - 90)
            score = elp[2]+eln[2]
            c_score = score + 1/np.exp(val)
            if (c_score > topscore) and val<10:
                fangpos = elp[1]
                fangneg = eln[1]
                topscore = c_score

    for i in range(len(positivePairs)):
        positivePairs[i][1] = fangpos
    for i in range(len(negativePairs)):
        negativePairs[i][1] = fangneg

    nty = fangpos - fangneg
    print('Angle sum :' + str(nty))
    return positivePairs, negativePairs


def printValues(values):
        values = np.array(values)
        print(np.array_str(values, precision=3, suppress_small=True))

def discardwrongpeaks(Rin, positivePairs, negativePairs, gridsize, min_peaks = 2):
    """  Discard wrong peaks
         Discard wrong peaks is based in the following facts:
          - In a grid you will find positive and negative angles
          - Make pairs of positive and negative angles. We group first positive, then negative
          - If we don't have enough for a square, we finish at that point.
      Otherwise,  we check that the pairs sum 90 degrees complementary, so we
      group by square. For each positive, it must exist a negative that
      complements, and vice versa.

      It seems that we are repeating twice the same, but that is not case. Let's look a two cases:
      16 peaks are input, predictPairs does nothing
      2 peaks remain of positive, and 4 for negative, after findCrossSequence
      Then predictPairs, tries to find 2 peaks more in positive.
      4 peaks positive and 4 peaks negative are final.
      -------
      2 peaks are input as positive, predictPairs predicts 4 positive and 4 negative
      findCrossSequence passes 4 positive and 4 negative,
      predictPairs does nothing
      findCrossSequence does nothing. This could be avoided because its redundant, but the function is quick, so not needed.

       ------------------------------------------------------------------------
      Function ERRORS:
      - couldn't find enough peaks fitting grid conditions
    """
    R = Rin.copy()

    positivePairs, negativePairs = filter_angles(positivePairs, negativePairs)

    print('Total of input Positive Pairs>'+str(len(positivePairs)))
    printValues(positivePairs)
    print('Total of input Negative Pairs>'+str(len(negativePairs)))
    printValues(negativePairs)

    # In case that the input number of pairs it does not reach the minimum, peaks are predicted
    positivePairs, negativePairs = predictPairs(positivePairs, negativePairs, min_peaks, R, gridsize)


    print("Trying to find a cross sequence (based on grid size) from positive pairs")
    positivePairs = findCrossSequence(positivePairs, gridsize)
    print("Positive pairs after cross sequence :")
    printValues(positivePairs)

    print("Trying to find a cross sequence (based on grid size) from negative pairs")
    negativePairs = findCrossSequence(negativePairs, gridsize)
    print("Negative pairs after cross sequence :")
    printValues(negativePairs)

    # Now are filtered and only good ones passed
    # So in case bad ones they are filtered and we get an insufficient number of peaks, we can predict them
    positivePairs, negativePairs = predictPairs(positivePairs, negativePairs, min_peaks, R, gridsize)

    error = enoughpeaks(positivePairs, negativePairs, min_peaks)
    if error < 3 :
        raise GLDException("Not enough POS and NEG pairs.")

    return positivePairs, negativePairs


def predictPairs(positivePairs, negativePairs, min_peaks, R, gridsize):
    error = enoughpeaks(positivePairs, negativePairs, min_peaks)
    if error == 1:
        print("Not enough negative pairs found, trying prediction.")
        negativePairs = predictGrid(positivePairs, R, gridsize)
    elif error == 2:
        print("Not enough positive pairs found, trying prediction.")
        positivePairs = predictGrid(negativePairs, R, gridsize)
    elif error == -1:
        print("Not enough pairs, trying prediciton on both.")
        negativePairs = predictGrid(positivePairs, R, gridsize)
        positivePairs = predictGrid(negativePairs, R, gridsize)

    return positivePairs, negativePairs


def predictGrid(best_peaks, R, gridsize=None):
    """
        Takes a group of peaks and tries
        to predict where the complementary angle peaks are
        based on the gridsize
    """

    if gridsize is None:
        return []

    best_peaks = np.squeeze(np.array(best_peaks))
    R = np.array(R)
    total_peaks = best_peaks.shape[0]
    if (total_peaks < 2):
        return []

    angle = int(best_peaks[0, 1])  # We assume that  the first is the highest signaling peak
    # normalize to same angle
    best_peaks[:, 1] = angle
    cangle = 0
    if (angle > 0):
        cangle = angle - 90
    else:
        cangle = angle + 90
    c180angle = cangle + 90

    signal = R[:, int(c180angle)].copy()  # get complementary data
    speaks = nonmaxsup1D(signal, total_peaks*3, int(gridsize[0] * 0.5), 0.01)

    if (speaks.shape[0] == 0):
        return []
    fpeaks = np.zeros((6, 3))
    for i in range(6):
        fpeaks[i, 0] = speaks[i, 1]
        fpeaks[i, 1] = cangle
        fpeaks[i, 2] = speaks[i, 0]

    goodpeaks = findCrossSequence(fpeaks, gridsize)
    total_peaks = np.squeeze(np.array(goodpeaks)).shape[0]
    if total_peaks == 0:
        # Could be that we have just one peak
        origin = fpeaks[0, 0]
        max_l = R.shape[0]
        goodpeaks = fpeaks[:2]
        if fpeaks[1, 0] < 1e-6:
            return []
        direction = fpeaks[1, 0]  # Direction is second biggest peak
        gmax = np.max(gridsize)
        if (direction > origin):
            goodpeaks[1, 0] = origin + gmax
        else:
            goodpeaks[1, 0] = origin - gmax

        if (goodpeaks[1, 0] > max_l or goodpeaks[1, 0] < 0):
            return []

    return goodpeaks


def nonmaxsup1D(signal, npeaks, window, bottom = 0.0):
    """
    Nonmaxsup for POSITIVE signals
    :param signal: Signal to find peaks
    :param npeaks: Number of max peaks to find in signal
    :param window: space around the peak to suppress when found
    :param bottom: limit of the maximum, if we go lower than this, there no more peaks to find
    :return:
    """
    k = 0
    peaks = np.zeros((npeaks, 2))
    num = 1.0
    while (npeaks > 0):
        num = np.max(signal)
        indx = np.argmax(signal)
        if (num < bottom): break
        peaks[k, 0] = num
        peaks[k, 1] = indx
        for i in range(indx - window, indx + window):
            if (i > 0 and i < len(signal)):
                signal[i] = 0
        npeaks = npeaks - 1
        k = k + 1
    return peaks


def enoughpeaks(pospeaks,negpeaks, min_peaks = 2):
    """
    -1,-2,-3 if pos and neg are 0
         2 if neg good and pos bad
         1 if pos good and neg bad
         3 if both good
    """
    total_pos = np.squeeze(np.array(pospeaks)).shape[0]
    total_neg = np.squeeze(np.array(negpeaks)).shape[0]

    if total_pos<min_peaks and total_neg>=min_peaks: return 2
    if total_pos>=min_peaks and total_neg<min_peaks: return 1
    if(total_pos==0 or total_neg==0): return -2
    if total_pos<min_peaks and total_neg< min_peaks : return -1
    return 3


def findCrossSequence(ipeaks, gridsize=None, best = False):
    # Checks which is the best combination of peaks that fits the gridsize
    # The allowed grid sequence can be one strike after another
    # or just one line.
    # Peaks need to be tuples [position,angle,X]
    # Grid size must be in pixels. This findCrossSequence expects a separation of n pixels  ------------*----*--------
    # If we need n,m pixels (periodical)  ---*--*--------*--*------ needs modification
    # If gridsize is None, the pairing is omitted
    # Always return [] if error
    def addG(g, ngroup):
        key1 = str(g[0, 0]) + str(g[1, 0])
        if key1 in ngroup.keys():
            grp = ngroup[key1]
            g[0, 2] = np.maximum(g[0, 2], grp[0, 2])
            g[1, 2] = np.maximum(g[1, 2], grp[1, 2])
        ngroup[key1] = g
    def delG(g, ngroup):
        key = str(g[0, 0]) + str(g[1, 0])
        if key in ngroup.keys():
            del ngroup[key]

    if gridsize is None: return []

    # Get all possible combinations of peaks
    possible_pairs = list(itertools.combinations(ipeaks, 2))
    error = []
    saved_group = []
    for pair in possible_pairs:
        pair = np.array(pair)
        total_p = pair[pair.argsort(axis=0)[:, 0]] # Sort pairs by distance
        dist_p = np.abs(total_p[0, 0] - total_p[1, 0])
        dif_error = np.abs(dist_p - gridsize[0]) / gridsize[0] # They have to fit the small size of the grid
        # first test, distance of spacing
        if dif_error < 0.35:
            saved_group.append(total_p)
            error.append(dif_error)

    if len(saved_group) == 0:
        return []
    # For each group check that they are not competing in the same distances
    if (len(saved_group) == 1): return saved_group

    gmax = np.max(gridsize)

    # Collapse similar ones
    old_group = {}
    for g in saved_group:
        addG(g,old_group)

    bup_groups = old_group.copy()

    for k1, g1 in old_group.items():
        for k2, g2 in old_group.items():
            if (k1 in bup_groups.keys() and k2 in bup_groups.keys()) and  k1 != k2 :
                # Two groups, g1 and g2. How far away are from each other each peak?
                err_dif = (np.abs(g1[0,0] - g2[0,0]) + np.abs(g1[1,0] - g2[1,0]))*0.5
                # If the distance between them is less than 0.75 gmax, we have to get rid of one of the groups
                if err_dif < (gmax*0.8):  # If they are smaller than the maximum gmax, we need to collapse them
                    c1 = [g1[0,2],g2[0,2]]
                    c2 = [g1[1,2],g2[1,2]]
                    v1 = np.argmax(c1)
                    v2 = np.argmax(c2)
                    if v1+v2 == 2 : # We have to delete this one, we have found one better
                        delG(g1, bup_groups)
                    elif v1+v2 == 0:
                        delG(g2, bup_groups)
                    else : # v1 == v2
                        if c1[v1] == c2[v2]:
                            if (c1[0]+c1[1]) < (c2[0]+c2[1]) :
                                delG(g1, bup_groups)
                            else:
                                delG(g2, bup_groups)
                        elif c1[v1]<c2[v2]:
                            delG(g1, bup_groups)
                        else:
                            delG(g2, bup_groups)

    if len(bup_groups) == 0:
        return []

    # Now is time to select the BEST candidate
    # Is going to be the one that sums up the most
    if best:
        sg = []
        pairs = []
        for k,g in bup_groups.items():
            pairs.append(g)
            sg.append(np.sum(g[:, 2]))
        maxind = np.argsort(np.array(sg))[::-1]
        return np.array([ el  for el in pairs[maxind[0]]])
    else:
        pairs = []
        for k,g in bup_groups.items():
            pairs.append(g[0])
            pairs.append(g[1])
        return np.squeeze(np.array(pairs))


def alternativePeaks(R,ipeaks):
    """
    Try to get the weak peaks based on the grid distance.
    First all peaks already existing are supressed.
    We get only the line corresponding to the main degrees
    positive and negative.
    :param R:
    :param ipeaks: are supossed to be good peaks. We can try now to get the weak peaks
    :return:
    """
    angles = np.unique(ipeaks[:, 1])
    for ang in  angles:
        newpeaks = searchNewPeaksForAngle(R.copy(), ipeaks, ang)
        if len(newpeaks)>0:
            ipeaks = np.concatenate([ipeaks,newpeaks])
    return ipeaks


def suppress(isignal,indx,window):
    signal = isignal.copy()
    for i in range(int(indx-window),int(indx+window)):
        if(i>0 and i<len(signal)) :
                signal[i]= 0
    return signal


def supress_comp(isignal, indx, window):
    signal = isignal.copy()
    for i in range(0,int(indx - window)):
        if (i > 0 and i < len(signal)):
            signal[i] = 0
    for i in range(int(indx+window),len(signal)):
        if (i > 0 and i < len(signal)):
            signal[i] = 0
    return signal


def searchNewPeaksForAngle(R, ipeaks, iangle):
    """
    Search for alternative peaks with lower magnitudes
    :param R:
    :param ipeaks:
    :param iangle:
    :return:
    """
    t_peaks = ipeaks[ipeaks[:, 1] == iangle]
    signal_ang = R[:, int(90 + iangle)]
    npeaks = []
    if len(t_peaks)==0 : # if we have dont have peaks in that angle return
        return []
    sorted_peaks = t_peaks[t_peaks[:,0].argsort()]
    ## take the distances between the found lines to known
    ## where to search up and down.
    ## this could be also provided, but we calculate them based
    ## on the pattern.
    distances = pdist(sorted_peaks[:,0:2])
    mindist = np.min(distances)
    # Minimum is the distance between two close
    # peaks ^ mindist__ ^ ____distances_____ ^ __ ^
    distances = distances[distances > 3 * mindist]
    if len(distances)==0 :
        return ipeaks
    distances = distances[distances.argsort()]
    md_pos = distances[0] + mindist
    ##  supress the peaks already found and 100 px around.
    window = 100
    for j in range(len(t_peaks)):
        indx = t_peaks[j, 0]
        signal_ang = suppress(signal_ang, indx, window)
        ## Start searching up. I take the first point suppress everything that is not up
        #  Original: ____ ^ __ ^ ________ ^ ___ ^ ________ ^ ___ ^ ____
        #  After:    ____ ^ __ ^ ______________________________________
    pos_1 = sorted_peaks[0, 0]
    # Look at the left
    if pos_1 - md_pos > 0:
        window = np.round(mindist * 2.25)
        signal_1 = supress_comp(signal_ang, pos_1 - md_pos, window)
        # Take 2 possible peaks by NMS
        peaks_pos = nonmaxsup1D(signal_1, 2, 15, 0.05 * np.max(sorted_peaks[:, 2]))
        if (peaks_pos[0,0] > 0 and peaks_pos[0,1] > 0):
            npeaks.append([peaks_pos[0, 1], iangle, peaks_pos[0, 0]])
            npeaks.append([peaks_pos[1, 1], iangle, peaks_pos[1, 0]])

    # I take the second point, look at the right
    pos_1 = sorted_peaks[-1, 0]
    if pos_1+md_pos < R.shape[0]:
        # suppress everything that is not down
        # Original: ____ ^ __ ^ ________ ^ ___ ^ ________ ^ ___ ^ ____
        # After: _____________________________ ^ ___ ^ _____
        window = np.round(mindist * 2.25)
        signal_1 = supress_comp(signal_ang, pos_1 + md_pos, window)
        # Take 2 possible peaks
        peaks_pos = nonmaxsup1D(signal_1, 2, 15, 0.05 * max(sorted_peaks[:, 2]))
        if (peaks_pos[0,0] > 0 and peaks_pos[1,0] > 0):
            npeaks.append([peaks_pos[0, 1], iangle, peaks_pos[0, 0]])
            npeaks.append([peaks_pos[1, 1], iangle, peaks_pos[1, 0]])
    return npeaks


def findIntersectionPoints(goodlines):
    """
    Important: order of returned points is x, y
    :param goodlines:
    :return:
    """
    goodlines = np.array(goodlines, dtype=np.float32)
    tl = goodlines.shape[0]
    # Find inner square intersection points for each line
    slopes = []
    intercepts = []
    for k in range(0, tl):
        # take all points related to that line
        line = goodlines[k]
        p1 = line[0]
        p2 = line[1]
        slope = (p2[1] - p1[1]) / ((p2[0] - p1[0]) + 1e-18)
        slope = np.round(np.rad2deg(np.arctan(slope)))
        if np.isnan(slope): slope = 0
        if slope == -90 or slope == 90:
            ind = np.argmin([np.abs(p1[0] - p2[0]), np.abs([p1[1] - p2[1]])])
            intercept = (p1[ind] + p2[ind]) * 0.5
        else:
            intercept = np.round((p1[1] - np.tan(np.deg2rad(slope)) * p1[0]))
        slopes.append(slope)
        intercepts.append(intercept)
    # Now I have all my lines analytically, find the intersections
    ipoints = {}
    for i in range(len(slopes)):
        for j in range(i, len(slopes), 1):
            if slopes[i] != slopes[j]:
                if ((slopes[i] == 90 and slopes[j] == -90) or (slopes[j] == -90 and slopes[j] == 90)):
                    continue
                elif slopes[i] == 90 or slopes[i] == -90:
                    xp = intercepts[i]
                    yp = (np.tan(np.deg2rad(slopes[j])) * xp) + intercepts[j]
                elif slopes[j] == 90 or slopes[j] == -90:
                    xp = intercepts[j]
                    yp = (np.tan(np.deg2rad(slopes[i])) * xp) + intercepts[i]
                else:
                    xp = (intercepts[j] - intercepts[i]) / (
                            np.tan(np.deg2rad(slopes[i])) - np.tan(np.deg2rad(slopes[j])))
                    yp = (np.tan(np.deg2rad(slopes[i])) * xp) + intercepts[i]

                key = str(np.round(xp))+'_'+str(np.round(yp))
                if key not in ipoints.keys():
                    ipoints[key]=(np.array([np.round(xp), np.round(yp)],dtype=np.float32),(i, j))

    ips = [ el[0] for el in ipoints.values() ]
    iorder = [ el[1] for el in ipoints.values() ]
    return np.array(ips, dtype = np.float32), iorder


def checkpoint(ic, point, limit = 10 ):
    iLength = ic.shape[0]
    iWidth = ic.shape[1]
    checked = 1
    if (point[0] < limit): return 0
    if (point[1] < limit): return 0
    if (point[0] > iWidth - 1 - limit): return 0
    if (point[1] > iLength - 1 - limit): return 0
    return checked


def checkpoints(ic, points):
    checked = [ checkpoint(ic, el) for el in points ]
    return np.sum(np.array(checked))==4


def selectGridPoints(iimg, ipeaks_pos, ipeaks_neg):
    """
        This  function takes all the lines from an image
        and calculate the intersection between lines
        and the crossing point.
        A folder can be given optionally to save the image of the lines.
    """
    # iLength, iWidth = iimg.shape
    # angpos = ipeaks_pos[0, 1]
    # angneg = ipeaks_neg[0, 1]

    pixel_lines, imglines = findLines(iimg, ipeaks_pos, ipeaks_neg)

    fpoints, spoints = findIntersectionPoints(pixel_lines)
    fpoints = np.array(fpoints, dtype=np.int32)
    if fpoints.shape[0]<4:
        return [],[],[],[]

    fpoints = fpoints[fpoints[:, 0].argsort()]
    cpoints, _ = findIntersectionPoints(np.array((fpoints[1:3], [fpoints[0], fpoints[3]])))  # middle point
    iimgc = cv2.cvtColor(iimg, cv2.COLOR_GRAY2RGB)
    for i in range(len(fpoints)):
        if checkpoint(iimg, fpoints[i, :]):
            cv2.circle(iimgc, (fpoints[i, 0], fpoints[i, 1]), 2, (255, 0, 0), -1)

    cpoints = np.array(cpoints[0], dtype=np.int32)
    if checkpoint(iimg, cpoints):
        cv2.circle(iimgc, (cpoints[0], cpoints[1]), 2, (255, 255, 0), -1)

    return cpoints, fpoints, iimgc, imglines


def findLines(iimg_or, ipeaks_pos, ipeaks_neg):
    """ This function takes an image and a set of peaks
    # It locates the peaks inside the function and it translate them
    # to lines in the image (slope and intercept)
    # (0,0) up left corner

    # Get image size, value of diagonal,value of padding, and angle relation
    # between Lenght and Width.

    """
    #from matplotlib import pyplot as plt
    iLength, iWidth = iimg_or.shape
    iDiag = np.sqrt(iLength * iLength + iWidth * iWidth)
    LengthPad = int(np.ceil(iDiag - iLength))
    WidthPad = int(np.ceil(iDiag - iWidth))

    iimg = (iimg_or > 0).copy()+1 # Make it totally binary

    padIMG = np.full((iLength + LengthPad, iWidth + WidthPad), -1, dtype=np.float32)
    padIMG[int(LengthPad / 2):(int(LengthPad / 2) + iLength), int(WidthPad / 2):(int(WidthPad / 2) + iWidth)] = iimg
    top = padIMG.shape[1]

    tIMG = np.full((iLength + LengthPad, iWidth + WidthPad), 0, dtype=np.float32)
    tIMG[int(LengthPad / 2):(int(LengthPad / 2) + iLength), int(WidthPad / 2):(int(WidthPad / 2) + iWidth)] = normalise(iimg_or)
    tIMG = cv2.cvtColor(np.uint8(tIMG*255), cv2.COLOR_GRAY2RGB)

    # lines = np.array([ipeaks_pos[:, 0], ipeaks_neg[:, 0]]).flatten()
    peaks = np.vstack([ipeaks_pos, ipeaks_neg])
    i = 0
    m = 0
    iPL, iPW = padIMG.shape
    center = (iPL / 2, iPW / 2)
    rlines = []
    for k in range(len(peaks)):
        Mt = cv2.getRotationMatrix2D(center, -peaks[k, 1], 1.0)
        rotated = cv2.warpAffine(padIMG, Mt, (iPL, iPW),flags=cv2.INTER_AREA)  # USE NEAREST, crop
        rotated = rotated > 0
        #rotatedColor = cv2.warpAffine(tIMG,Mt,(iPL,iPW),flags=cv2.INTER_NEAREST)
        j = 0
        posx1 = 0
        posx2 = top
        while (j < top):
            if rotated[int(peaks[k,0]),j] > 0:
                posx1 = j
                break
            j = j + 1
        while (j < top):
            if rotated[int(peaks[k,0]),j] < 1:
                posx2 = j-1
                break
            j = j + 1
        if (j > top):
            posx2 = top-1

        # Use for debug
        #cv2.line(rotatedColor, (int(posx1),int(peaks[k,0])), (int(posx2),int(peaks[k,0])), (255, 0, 0), 1)
        #plt.imshow(rotatedColor)
        # plt.pause(1)  # <-------
        # plt.waitforbuttonpress(0)
        # plt.close()
        Mt2 = cv2.getRotationMatrix2D(center, peaks[k, 1], 1.0)
        p1x = np.dot(Mt2,(int(posx1),int(peaks[k,0]),1))
        p2x = np.dot(Mt2,(int(posx2),int(peaks[k,0]),1))
        p1x[0] = np.round(p1x[0] - WidthPad / 2)
        p1x[1] = np.round(p1x[1] - LengthPad / 2)
        p2x[0] = np.round(p2x[0] - WidthPad / 2)
        p2x[1] = np.round(p2x[1] - LengthPad / 2)
        rlines.append([p1x, p2x])
    iimg_or = normalise(iimg_or)
    iimgf = cv2.cvtColor(np.uint8(iimg_or*255), cv2.COLOR_GRAY2BGR)
    for p in rlines:
        p1 = np.array(p[0], dtype=np.int32)
        p2 = np.array(p[1], dtype=np.int32)

        cv2.line(iimgf, (p1[0], p1[1]), (p2[0], p2[1]), (0, 0, 255), 1)

    return rlines, iimgf


def m_pdist(x):
    [rows, cols] = x.shape
    if (rows < 2):
        D = x
    order = np.array(list(combinations(range(rows),2)))
    Xi = order[:, 0]
    Yi = order[:, 1]
    diff = x[Xi]-x[Yi]
    D = np.sqrt(np.sum(diff**2,axis=1))
    Xi = Xi[D.argsort()]
    Yi = Yi[D.argsort()]
    return D, x[Xi],x[Yi]


def _adjustLines(window, wd, avx, avy, iim, bwedge, angles, laplacian_apply, windowSize = 3):
    m_points = []
    hw = window * 0.5
    top = np.int32([np.round(avy - hw),round(avx - hw)])
    h,w = iim.shape
    top[top<0] = 0
    if top[0]>h : top[0] = h
    if top[1]>w : top[1] = w
    # this needs to be changed relative to the image magnification
    ic = iim[top[0]:int(top[0]+window),top[1]:int(top[1]+window)] # crops the image I.rect is a four - element position vector[xmin ymin width height]
    bwic = bwedge[top[0]:int(top[0]+window),top[1]:int(top[1]+window)]
    #####
    ic = normalise(ic) # exposure.equalize_hist(ic)
    I = gaussfilt(ic, 1.2)
    if laplacian_apply :
        It = laplacianfilt(I)
        I = normalise(It) * 255
    PC, orient, _, _ = phasecongmono(I)
    nm = nonmaxsup_python(PC,orient,1.5)
    bw = hysthresh(nm, 0.005, 0.1)
    # Sometimes all this sophistication is for nothing because the  image is empty of features.
    r,c = ic.shape
    if (np.sum(bw[:]) / (r*c)) < 0.01:
        bw = bwic

    bw2 = borderEnhancer(bw, [2,2])
    bw = np.logical_or(bw,(np.logical_and(bw2,bwic)))
    bw = np.uint8(bw)

    if angles[0]>-1:
        angpos = angles[0]
        angneg = angles[1]
    else:
        angpos = angles[1]
        angneg = angles[0]

    a = projectionsOneE(bw, angpos)
    b = (1 / windowSize) * np.ones((1, windowSize))

    # a = np.r_[PR1[windowSize-1:0:-1],PR1,PR1[-2:-windowSize-1:-1]]
    PR1 = np.convolve(b[0],a,mode='valid')
    len_pos1 = int(PR1.shape[0] / 2)
    PR1 = supress_comp(PR1, len_pos1, wd)
    mp1 = nonmaxsup1D(PR1, 2, int(wd * 0.25))

    a = projectionsOneE(bw, angneg)
    # a = np.r_[PR2[windowSize - 1:0:-1], PR2, PR2[-2:-windowSize - 1:-1]]
    PR2 = np.convolve(b[0], a, mode='valid')
    len_pos2 = int(PR2.shape[0] / 2)
    PR2 = supress_comp(PR2, len_pos2, wd)
    mp2 = nonmaxsup1D(PR2, 2, int(wd * 0.25))

    peaks_pos = np.zeros((2,2))
    peaks_pos[0,0]  = mp1[0, 1]
    peaks_pos[0,1] =  angpos
    peaks_pos[1,0]  = mp1[1, 1]
    peaks_pos[1,1] =  angpos
    peaks_neg = np.zeros((2, 2))
    peaks_neg[0,0]  = mp2[0, 1]
    peaks_neg[0,1] =  angneg
    peaks_neg[1,0]  = mp2[1, 1]
    peaks_neg[1,1] =  angneg

    rlines, imglines = findLines(ic,peaks_pos, peaks_neg)
    m_ipoints, _ = findIntersectionPoints(rlines)
    # In case that angles are a little bit moved, we need to remove outliers
    if  m_ipoints.shape[0] > 3:
        m_points = m_ipoints
        # distances, mpoints_a, mpoints_b = m_pdist(m_ipoints)
    return m_points, imglines


def squareTest(m_ipoints, wo, w, avx, avy, iim, distp):
    rows, cols = iim.shape
    if (np.abs(distp[1] - distp[2]) > 0.25 * wo): # must be a square (more or less) wo * wo for elements 1 and 2
        return False
    for i in range(1,4):
        axp = m_ipoints[i, 0]
        ayp = m_ipoints[i, 1]
        wh = w*0.5
        dc = np.sqrt((wh - axp)**2 + (wh - ayp)**2)
        if ((avx - wh) < 0): # get distance to center
            dist_test = np.round(dc - np.abs(avx - wh))
        elif((avy - wh) < 0):
            dist_test = np.round(dc - np.abs(avy - wh))
        elif((avx + wh) > cols):
            dist_test = np.round(dc - np.abs(cols - (avx + wh)))
        elif((avy + wh) > rows):
            dist_test = np.round(dc - abs(rows - (avy + wh)));
        else :
            dist_test = np.round(dc)

        if (distp[i] < wo * 0.5 or distp[i] > wo * 2 or dist_test > wo * 1.5):
            # try again with a bigger distance squared
            return False

    return True


def _getAdjustedPoints(wo,wscale, avx, avy, iim, bwedge, angles, apply_laplacian):
    """

    :param wo:
    :param alpha: size of
    :param avx:
    :param avy:
    :param iim:
    :param bwedge:
    :param angles:
    :param imfolder:
    :param apply_laplacian:
    :return: m_ipoints
    """
    wd = wo * 2
    w = wo * wscale
    m_ipoints, ic = _adjustLines(w, wd, avx, avy, iim, bwedge, angles, apply_laplacian)


    xp = m_ipoints[0, 0]
    yp = m_ipoints[0, 1]
    distp = []
    for point in m_ipoints:
        xpi = point[0]
        ypi = point[1]
        distp.append(np.round(np.sqrt((xp - xpi) ** 2 + (yp - ypi) ** 2)))
    # Sort by distance
    distp = np.array(distp)
    indp = distp.argsort()
    distp = distp[indp]
    m_ipoints = m_ipoints[indp]
    # Now we need to check that these points, if by chance the  distance between them is much more LESS or much MORE than the
    # original, we cancel the adjustment. No matter the choice, original points cannot be
    # ]0.5 * wo, 1.5 * wo[far away from the original centroid of points, since it is a fine calibration
    if not squareTest(m_ipoints, wo, w, avx, avy, iim, distp):
        return [],[]

    cpoints = [0, 0]
    # Last and first are opposite
    p = m_ipoints
    for i in range(4):
        if checkpoint(ic, p[i]):
            cv2.circle(ic, (int(p[i][0]), int(p[i][1])), 1, (255, 255, 0), -1)

    cpoints[0] = p[0][0] + np.round((p[3][0] - p[0][0]) / 2)
    cpoints[1] = p[0][1] + np.round((p[3][1] - p[0][1]) / 2)
    # m_ipoints = np.concatenate([m_ipoints,np.array([cpoints])])
    cv2.circle(ic, (int(cpoints[0]), int(cpoints[1])), 1, (0, 255, 0), -1)

    # Grow up points
    hw = w * 0.5
    tx = np.round(avx - hw - 1)
    ty = np.round(avy - hw - 1)
    if (tx < 0):
        tx = 0
    if (ty < 0):
        ty = 0
    fpoints = []
    for i in range(4):
        fpoints.append(np.array([p[i, 0] + tx, p[i, 1] + ty]))
    fpoints.append(np.array([cpoints[0] + tx, cpoints[1] + ty]))

    return np.array(fpoints), ic


def calibrateIntersections(iim, bwedge, ipeaks, goodLines, imfolder, apply_laplacian = True, ignore_calibration = False):
    """

    :param goodLines:
    :param ipeaks:
    :param iim:
    :return:
    """

    ipoints, indxpoints = findIntersectionPoints(goodLines)
    angles = np.unique(np.concatenate([ gpeaks[:,1]   for gpeaks in ipeaks]))

    mytree = KDTree(np.array(ipoints)[:,0:2])
    ipoints_copy = ipoints.copy()
    rows,cols = ipoints.shape

    total_quartets = math.floor(rows / 4)
    pc = 0
    gpoints = {}
    for k in range(total_quartets):
        for m in range(rows):
            if (ipoints_copy[m, 0] > -np.inf):
                break
        distances,pNN = mytree.query(ipoints_copy[m, 0:2],k=4)
        ipoints_copy[pNN] = -np.inf # Mark points already used
        # average x and y
        avx = np.mean(ipoints[pNN, 0])
        avy = np.mean(ipoints[pNN, 1])
        xp = ipoints[pNN[0], 0]
        yp = ipoints[pNN[0], 1]
        xpi = ipoints[pNN[1], 0]
        ypi = ipoints[pNN[1], 1]
        # Check if the group is inside or outside the image
        is_in = checkpoints(iim, ipoints[pNN,:])
        # if is_inside the image and we want to check extra calibrations
        keep_original_point = True # By default we keep it
        if is_in and not ignore_calibration:
            keep_original_point = False
            wo = np.round(np.sqrt((xp - xpi)**2 + (yp - ypi)**2))
            m_ipoints, ic = _getAdjustedPoints(wo, 5, avx, avy, iim, bwedge, angles, apply_laplacian)
            if len(m_ipoints)==0:
                print('First test failed for '+str(avy)+" "+str(avx))
                # Duplicate distance of crop
                m_ipoints, ic = _getAdjustedPoints(wo, 7, avx, avy, iim, bwedge, angles, apply_laplacian)
                if len(m_ipoints)==0:
                    print('Second test failed for ' + str(avy) + " " + str(avx))
                    print('Keeping original point.')
                    keep_original_point = True
            if not keep_original_point:
                fname = imfolder+'\\cross_'+str(int(m_ipoints[4,0]))+"_"+str(int(m_ipoints[4,1]))+".tiff"
                cv2.imwrite(fname, np.uint8(ic))
                gpoints[k] = (m_ipoints, is_in)
        if keep_original_point:
            fpoints = []
            for i in range(4):
                fpoints.append(np.array([ipoints[pNN[i],0],ipoints[pNN[i],1]]))

            cpointx = int(np.round(np.mean(ipoints[pNN, 0])))
            cpointy = int(np.round(np.mean(ipoints[pNN, 1])))

            fpoints.append(np.array([cpointx, cpointy]))
            gpoints[k] = (fpoints, is_in)

    if len(gpoints)==0:
        return {}
    iimgc = cv2.cvtColor(iim, cv2.COLOR_GRAY2RGB)
    for key, points in gpoints.items():
        fpoints = points[0]
        for point in fpoints:
            if checkpoint(iim, point):
                cv2.circle(iimgc, (int(point[0]), int(point[1])), 1, (0, 255, 255), -1)
        point = fpoints[4]
        cv2.circle(iimgc,(int(point[0]), int(point[1])), 1, (0, 255, 0), -1)

    sketch_fname = imfolder+"\\sketch.jpg"
    cv2.imwrite(sketch_fname, iimgc)
    return gpoints


def is_insquare(points, cp):
    is_in = 0
    # get order of points by proximity, so we are sure a contour is followed
    sorted_square = sortPolyPoints(points)
    # calculate area of the polygon
    n_points = np.vstack([points, cp])
    sorted_polygon = sortPolyPoints(n_points)
    a1 = polyarea(sorted_square)
    a2 = polyarea(sorted_polygon)
    if (a2 < a1):
        is_in = 1
    return is_in


def sortPolyPoints(points):
    auxpoints = np.array(points.copy(), dtype = np.float32)
    # for each point get the closest
    sorted_points =[]
    iter = 0
    i = 0
    while len(auxpoints)>0 and iter<500:
        points_set = auxpoints[i]
        sorted_points.append(points_set)
        auxpoints = np.delete(auxpoints, i, axis=0)
        xa = auxpoints[:,0]
        ya = auxpoints[:,1]
        old_dist = np.inf
        for j in range(len(xa)):
            mdist = np.sqrt((points_set[0]-xa[j])**2+(points_set[1]-ya[j])**2)
            if(mdist<old_dist) and mdist>np.finfo(np.float32).eps:
                i = j
                old_dist = mdist

    return np.array(sorted_points)


def polyarea(corners):
        n = len(corners)  # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1]
            area -= corners[j][0] * corners[i][1]
        area = abs(area) / 2.0
        return area


def cutSquares(gpoints, inputim, gridsize):
    """
    Takes image points, and evaluates combinations
    that can form a square pattern with the grid dimensions
    and crops the square from the image.
    Additionally, indicates in which square is the center of the image
    :param fpoints:
    :param inputim:
    :param gridsize:
    :return:
    """
    iLength = inputim.shape[0]
    iWidth = inputim.shape[1]
    cpoints = []

    g_is_in = []
    for k,group in gpoints.items():
        g = group[0]
        cpoints.append(g[4])
        g_is_in.append(group[1])

    ## Select points
    cpoints = np.array(cpoints)
    cpoints = cpoints[cpoints[:,0].argsort()] # order by x coordinate
    # take distance of closest points(minimum distance must be a square
    distsq = np.max(gridsize)
    combos = np.array(list(combinations(range(len(cpoints)),4)))
    # Select from the inner points the one closest to the center.
    cxp = iWidth / 2
    cyp = iLength / 2
    all_cutpoints = []
    m = 0
    tolerance = 0.2 * distsq
    for c in combos:
        set1 = cpoints[c]
        cdist = pdist(set1)
        j = 0
        for distance in cdist:
            if ((distsq - tolerance) < distance and distance < (distsq + tolerance)):
                j = j + 1
        if j == 4:
            mcombo = np.append(set1, np.ones((4, 1)) * m, axis=1)
            if checkpoints(inputim,set1):
                mcombo = np.append(mcombo, np.ones((4, 1)), axis=1)
            else:
                mcombo = np.append(mcombo, np.zeros((4, 1)), axis=1)

            if is_insquare(set1, [cxp, cyp]):
                mcombo = np.append(mcombo, np.ones((4, 1)), axis=1)
            else:
                mcombo = np.append(mcombo, np.zeros((4, 1)), axis=1)
            m = m+1
            all_cutpoints.append(mcombo)
    return np.array(all_cutpoints)


