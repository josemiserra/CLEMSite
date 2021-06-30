

from imtools import getFOV, getPixelSize
import cv2
import numpy as np
import math


em = "D:\\GOLGI\\PR_27Mar2017\\PR_27Mar\\4Q_field--X03--Y28_0041--001___0002\\4Q_field--X03--Y28_0041--001_sFOV_201704211045298624.tif"
lm_golgi = "D:\\GOLGI\\PR_27Mar2017\\renamed\hr\\field--X03--Y24_0040\\reg_t.jpg"
lm_rl = "D:\GOLGI\PR_27Mar2017\\renamed\hr\\field--X03--Y24_0040\\grid_0040_4--LM--RL - Reflected Light--10x--z1.tif"

fov_um = getFOV(em,atlas=True)
pixel_size_EM =getPixelSize(em,atlas=True)
img_out_EM = cv2.imread(em,0)
center_obj_EM = img_out_EM.shape
center_obj_EM =np.array(center_obj_EM)*0.5

img_rl_LM = cv2.imread(lm_rl,0)
pixel_size_LM =getPixelSize(lm_rl,atlas=False)
img_golgi_LM = cv2.imread(lm_golgi,0)

iclahe = cv2.createCLAHE(clipLimit=0.01, tileGridSize=(32, 32))
img_rl_LM = iclahe.apply(np.uint8(img_rl_LM))
img_rl_LM = cv2.convertScaleAbs(img_rl_LM, alpha=(255.0 / np.max(img_rl_LM)))
overlay = np.zeros(shape=img_rl_LM.shape + (3,), dtype=np.uint8)
overlay[..., 2] = img_rl_LM
overlay[..., 1] = img_rl_LM + img_golgi_LM
overlay[...,0]  = img_rl_LM


# Flip the point
w, h = img_golgi_LM.shape
img_out_LM = cv2.flip(img_golgi_LM, 1)

scale_factor = float(pixel_size_LM / pixel_size_EM)

w_s = int(w * scale_factor)
h_s = int(h * scale_factor)
scaled_LM = cv2.resize(img_out_LM, (w_s, h_s))
# pad image to be same size as img_out_SEM
w_sem, h_sem = img_out_EM.shape

### PAD SEM image
nh_sem = max(h_sem,h_s) + 200
nw_sem = max(w_sem,w_s) + 200

LengthPad = nh_sem - h_sem
WidthPad = nw_sem - w_sem

pad1 = int(math.ceil(LengthPad / 2))
pad2 = int(math.ceil(LengthPad / 2) + h_sem)
pad3 = int(math.ceil(WidthPad / 2))
pad4 = int(math.ceil(WidthPad / 2) + w_sem)

fscaled_SEM = np.zeros((nh_sem, nw_sem))
fscaled_SEM[pad1:pad2, pad3:pad4] = img_out_EM

w_sem, h_sem = fscaled_SEM.shape
fscaled_LM = np.zeros(fscaled_SEM.shape)

LengthPad = h_sem - h_s
WidthPad = w_sem - w_s

pad1 = int(math.ceil(LengthPad / 2))
pad2 = int(math.ceil(LengthPad / 2) + h_s)
pad3 = int(math.ceil(WidthPad / 2))
pad4 = int(math.ceil(WidthPad / 2) + w_s)

fscaled_LM[pad1:pad2, pad3:pad4] = scaled_LM

#center_obj_LM = center_obj_LM * scale_factor
#center_obj_LM[:, 0] = LengthPad * 0.5 + center_obj_LM[:, 0]
#center_obj_LM[:, 1] = WidthPad * 0.5 + center_obj_LM[:, 1]

w_s, h_s = fscaled_LM.shape



