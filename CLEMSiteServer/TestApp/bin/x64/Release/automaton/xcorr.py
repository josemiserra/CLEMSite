from skimage.feature import register_translation
from skimage import data, io, filters

def getXCorrValues(slice_file,df):
    im_crop1 = []
    im_crop2 = []
    return xcorr(im_crop1,im_crop2)

def xcorr(im_crop1,im_crop2):
    image = filters.sobel(im_crop1)
    offset_image= filters.sobel(im_crop2)
    # pixel precision first
    #shift, error, diffphase = register_translation(image, offset_image)
    #print("Detected pixel offset (y, x):")
    #print(shift)
    # subpixel precision
    shift, error, diffphase = register_translation(image, offset_image, 100)
    return shift
