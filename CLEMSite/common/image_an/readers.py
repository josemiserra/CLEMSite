import os
import re
import sys

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

from common.image_an.tifftest import TiffFile,TiffWriter
import xml.etree.ElementTree as ET
import numpy as np

def getInfoHeader(fname):
    xml_info, pixel_size = getInfoTiffOME(fname)
    if(not xml_info):
        return
    try:
        root = ET.fromstring(xml_info)
    except ET.ParseError as err:
        return

    first_tag = []
    second_tag = []
    for child in root:
        m = re.match('.*Image.*', child.tag)
        if m:
            first_tag = m.group(0)
    if (first_tag):
        data = {}
        for child in root.findall(first_tag):
            for gch in child:
                m = re.match('.*Pixels.*', gch.tag)
                if m:
                    second_tag = m.group(0)
    if (second_tag):
        child = root.findall(first_tag + '//' + second_tag)
        for gch in child[0]:
            planetag = re.match('.*Plane.*', gch.tag)
        child2 = root.findall(first_tag + '//' + second_tag + '//' + planetag.group(0))
        for gch in child2[0]:
            stagepositiontag = re.match('.*StagePosition.*', gch.tag)
        child2 = root.findall(
            first_tag + '//' + second_tag + '//' + planetag.group(0) + '//' + stagepositiontag.group(0))
        mydict = child2[0].attrib;
        data['PositionX'] = float(mydict['PositionX']) * 1e6;
        data['PositionY'] = float(mydict['PositionY']) * 1e6;
        data['PositionZ'] = float(mydict['PositionZ']) * 1e6;
        mydict = child[0].attrib;

        data['PixelSize'] = pixel_size*1e3; # in micrometers!!  # float(mydict['PhysicalSizeX'])*1e-3;
        #                data['PhysicalSizeY'] = mydict['PhysicalSizeY']
        #                data['PhysicalSizeZ'] = mydict['PhysicalSizeZ']
        data['PyxelType'] = mydict['PixelType']

    return data

def saveInfoTiffOME(tifname_original,tifname_empty,image_np):
    metadata = {}
    with TiffFile(tifname_original) as tif:
        with TiffWriter(tifname_empty) as tif2:
            tif2.save(image_np,description=tif[0].image_description, resolution=(tif[0].x_resolution,tif[0].y_resolution,'cm'))

def getInfoTiffOME(tifname):
    """ Get info from tiff header """
    pixel_size = 0
    res_unit = 0
    xml_info = []
    with TiffFile(tifname) as tif:
        for page in tif:
            for tag in page.tags.values():
                if (tag.name == 'image_description'):
                    xml_info = tag.value
                if (tag.name == 'resolution_unit'):
                    res_unit = tag.value
                if (tag.name == 'x_resolution'):  # we assume the same x and y resolution
                    res_size = tag.value
                if (tag.name == 'image_length'):
                    im_length = tag.value
    if (int(res_unit) == 3):  # dots per cm
        tpx = float(res_size[0]) / float(res_size[1])  # pixels per 1 cm
        pixelsize = 1.0 / tpx  # length of the image e.g. 1024 pixels/ tpx
        pixel_size = pixelsize * 10  # change to meters

    return (xml_info, pixel_size)

def getInfoHeaderZeiss(fname):
    csv_info = getInfoTiffZeiss(fname);
    zinfo = [s.strip() for s in csv_info.splitlines()]
    data = {}
    ind = filterPick(zinfo, ".*Image Pixel Size.*")[0]
    aux = zinfo[ind]
    data['PixelSize'] = float(aux[19:-3]) * 1e-3
    ind = filterPick(zinfo, ".*Stage at X.*")[0]
    aux = zinfo[ind]
    data['PositionX'] = float(aux[13:-3])
    ind = filterPick(zinfo, ".*Stage at Y.*")[0]
    aux = zinfo[ind]
    data['PositionY'] = float(aux[13:-3])
    ind = filterPick(zinfo, ".*Stage at Z.*")[0]
    aux = zinfo[ind]
    data['PositionZ'] = float(aux[13:-3])
    data['PyxelType'] = "uint8"
    return data;

def getInfoHeaderAtlas(tifname):
    xml_info = ""
    data = {}
    with TiffFile(tifname) as tif:
        for page in tif:
            for tag in page.tags.values():
                if (tag.name == '51023' or tag.name =='fibics_xml'):
                    xml_info = tag.value
    if (not xml_info):
        raise ValueError("NO INFO HEADER for ATLAS picture")
    root = ET.fromstring(xml_info)
    first_tag = [];
    second_tag = [];
    third_tag = [];
    for child in root:
        m = re.match('Scan', child.tag)
        m2 = re.match('.*Stage.*', child.tag)
        m3 = re.match('.*Image$', child.tag)
        if m:
            first_tag = m.group(0)
        elif m2:
            second_tag = m2.group(0)
        elif m3:
            third_tag = m3.group(0)
    #### Scan
    if (first_tag):
        child = root.findall(first_tag)
        for el in child[0]:
            if (el.tag == 'Ux'):
                data['PixelSize'] = float(el.text)
            elif (el.tag == 'Dwell'):
                data['DwellTime'] = float(el.text)
            elif (el.tag == 'FOV_X'):
                data['FOV_X'] = float(el.text)
            elif (el.tag == 'FOV_Y'):
                data['FOV_Y'] = float(el.text)
            elif (el.tag == 'Focus'):
                data['WD'] = float(el.text)
    ######## Stage
    if (second_tag):
        child = root.findall(second_tag)
        for el in child[0]:
            if (el.tag == 'X'):
                data['PositionX'] = float(el.text)
            elif (el.tag == 'Y'):
                data['PositionY'] = float(el.text)
            elif (el.tag == 'Z'):
                data['PositionZ'] = float(el.text)
    ######## Image
    if (third_tag):
        child = root.findall(third_tag)
        for el in child[0]:
            if (el.tag == 'Detector'):
                data['Detector'] = el.text
            elif (el.tag == 'Aperture'):
                data['Aperture'] = el.text
            elif (el.tag == 'Width'):
                data['Width'] = int(el.text)
            elif (el.tag == 'Height'):
                data['Height'] = int(el.text)
            elif (el.tag == 'Brightness'):
                data['Brightness'] = float(el.text)
            elif (el.tag == 'Contrast'):
                data['Contrast'] = float(el.text)
            elif (el.tag == 'Beam'):
                data['Beam'] = el.text
    return data

def getInfoTiffZeiss(tifname):
    """ Get SmartSEM info from picture"""
    with TiffFile(tifname) as tif:
        for page in tif:
            for tag in page.tags.values():
                if (tag.name == '34118'):
                    file_info = tag.value
                    break;
    return file_info

def filterPick(self, myList, myString):
    pattern = re.compile(myString);
    indices = [i for i, x in enumerate(myList) if pattern.search(x)]
    return indices



# This should be a factory driven by settings
def imageToStageCoordinates_LM(fpoints, tpoint, size, pixelSize):
    # fpoints lisf of coordinates in pixels
    # tpoint, middle point in stage coordinates
    # size and pixelsize of Image
    return imageToStageLeicaSP5(fpoints, tpoint, size, pixelSize)

def imageToStageLeicaSP5(fpoints, tpoint, size, pixelSize):
    ## Leica SP5 inverted type coordinates
    iLength, iWidth = size
    icx = round(iWidth / 2)
    icy = round(iLength / 2)
    tPoints = np.array(fpoints.copy(),dtype = np.float32)
    # Considered orientation of microscope Direction in ++ and --
    tPoints[:, 0] = (fpoints[:, 0] - icx) * pixelSize + tpoint[1]
    tPoints[:, 1] = -(fpoints[:, 1] - icy) * pixelSize + tpoint[0]
    return tPoints

def imageToStageCoordinates_SEM(fpoints, tpoint, size, pixelSize):
    iLength, iWidth = size
    icx = round(iWidth / 2)
    icy = round(iLength / 2)
    tPoints = np.array(fpoints.copy(), dtype=np.float32)
    # Considered orientation of microscope Direction in ++ and --
    tPoints[:, 0] = (fpoints[:, 0] - icx) * pixelSize + tpoint[0]
    tPoints[:, 1] = -(fpoints[:, 1] - icy) * pixelSize + tpoint[1]
    return tPoints