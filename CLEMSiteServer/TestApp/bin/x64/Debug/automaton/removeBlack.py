from tifftest import TiffFile,imsave


import cv2
import re
import numpy as np
from os import path,remove
import time
import sys
from os import listdir
from os.path import isfile, join

def remove_all_inDirectory(folder):
    onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
    for el in onlyfiles:
        if (is_slice_file(el)):
            save_no_black(folder+"\\"+el)

def getInfoHeaderAtlas(tifname):
    xml_info = ""
    data = {}
    with TiffFile(tifname) as tif:
        for page in tif:
            data = page.tags
            break
    return data

def is_slice_file(file):
    p = re.compile(r'.*um.*tif$')
    # if name has slice and um
    if(p.match(file)):
        return True
    return False

def save_no_black(file_im,dir_to_save):
    im_1 = cv2.imread(file_im, cv2.IMREAD_GRAYSCALE)
    height, width = im_1.shape

    ret, th = cv2.threshold(im_1, 0, 1, cv2.THRESH_BINARY)
    # Find corners of picture
    # if not possible, leave it like this
    th = th * 255
    try:
        contours, hierarchy = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        image, contours, hierarchy = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except:
        return False

    # imageC = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
    # imageC = cv2.drawContours(imageC, contours, -1, (0,255,0), 3)

    centroids_list = []
    dist_list = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # If area of square is smaller than
        if (w * h < 1000):  # avoid errors.
            continue
        else:
            break
    # otherwise, take the corners and crop
    # image cropping borders
    im_crop = im_1[y:y + h, x:x + w]
    # Read original header and take metadata
    header = getInfoHeaderAtlas(file_im)

    metadata = {}
    # for el in header:
    #    metadata[el] = header[el].value
    # Delete the old file
    # Take the metadata
#    remove(file_im)
    metadata['software'] = header['software'].value.decode('ascii', errors="ignore")
    data = header['fibics_xml'].value
    data = data.decode('ascii', errors="ignore")
    data = data.replace('\x00','')
    metadata['fibics_xml'] = data.encode('ascii','replace')
    header,tail = path.split(file_im)
    image_to_save = dir_to_save +"\\"+ tail
    imsave(image_to_save, im_crop, compress=0, metadata=metadata)




#file_im = sys.argv[1]
#folder_store = "Z:\\lleti\\Binuc_3\\b2\\"

#  Get folder
#folder_store,file = path.split(file_im)

#remove_all_inDirectory(folder_store)
#if(is_slice_file(file)):
#    save_no_black(file_im)














