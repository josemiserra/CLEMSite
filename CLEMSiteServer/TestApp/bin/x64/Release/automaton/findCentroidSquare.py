
import numpy as np
import cv2
import sys

from os import path
from imutils import writeErrorFile
import math


def findSquare(file_before,file_after,tag):
    # Get folder
    folder_store,file = path.split(file_before)

    im_before = cv2.imread(file_before,cv2.IMREAD_GRAYSCALE)
    im_after  = cv2.imread(file_after,cv2.IMREAD_GRAYSCALE)

    im_before_b = cv2.GaussianBlur(im_before,(5,5),0)
    im_after_b = cv2.GaussianBlur(im_after,(5,5),0)

    # Here is the trick why works.
    im_difference = []
    im_difference = cv2.absdiff( im_after_b,im_before_b)
    cv2.normalize(im_difference,im_difference, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    blur = cv2.GaussianBlur(im_difference,(7,7),0)
    # blur = 255 - blur;

    ret,th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((5,5),np.uint8)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

    #cv2.imshow('image',th)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    try:
        contours,_ = cv2.findContours(opening,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        _,contours,_ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except:
        return False
    height, width = opening.shape
    centroids_list = []
    dist_list = []
    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        # If area of square is smaller than
        # We know that the square size should be around 50 by 50 pixels.
        # It would be better to configure a fixed size box in pixelsize, not pixels, but for now is ok
        # Then, we will remove squares bigger than 90*90 or smaller than 30*30
        if w*h<1000 or w*h>8000:
            continue
        ratio = w / (h * 1.0)
        if (ratio < 0.75 or ratio > 1.25):  # this is not a square!!!
                continue
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        # print cx
        # print cy
        shift_cx = height/2 - cx
        shift_cy =  width/2 - cy
        side = np.min(np.array([w,h]))
        dist_list.append(math.sqrt(shift_cx*shift_cx+shift_cy*shift_cy))
        centroids_list.append([side-1,x,y,shift_cx,shift_cy])

    # Closest to center
    indexes = [i[0] for i in sorted(enumerate(dist_list), key=lambda x:x[1])]
    val = centroids_list[indexes[0]]

    image_c = cv2.cvtColor(im_after,cv2.COLOR_GRAY2BGR)
    cv2.rectangle(image_c,(val[1],val[2]),(val[1]+val[0],val[2]+val[0]),(0,0,255),1)
    cv2.circle(image_c,(int(val[1]+val[0]/2),int(val[2]+val[0]/2)),2,(255,0,0),2)

    # to_file = time.strftime("%Y_%m_%d-%H_%M")
    cv2.imwrite(folder_store+"\\square_processed_"+tag+".png", image_c)
    # Compute shift in relation to the center
    im_after = im_after[(val[2]-10):(val[2]+val[0]+10),(val[1]-10):(val[1]+val[0]+10)]
    cv2.imwrite(folder_store+"\\square_template"+tag+".tif",im_after)

    file_data = folder_store+"\\data_square_"+tag+".csv"
    with open(file_data, 'w') as f:
        f.write(str(val[3])+";"+str(val[4])+"\n")
    return True



try:
    file_before = sys.argv[1]
    file_after = sys.argv[2]
    tag = sys.argv[3]
    if (not findSquare(file_before, file_after, tag)):
        folder_store, file = path.split(file_before)
        writeErrorFile("ERROR;0;0",folder_store)
except SystemExit:
    pass
except:
   writeErrorFile("In findCentroidSquare : NO ARGUMENTS PROVIDED or ERROR DURING EXECUTION",".")





