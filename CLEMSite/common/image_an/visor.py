# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\JMS\Documents\msite\MSite\msiteSEM\UI\register.ui'
#
# Created: Sat Sep 03 19:12:29 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4 import QtCore, QtGui
from PyQt4.QtOpenGL import *
import os,sys
import cv2
import numpy as np
sys.path.append(os.getcwd()+"\\image_an")
from xcorr import findShift
from readers import getInfoHeader
from skimage.feature import register_translation
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_VisorWindow(QtGui.QDialog):
    shift = []
    m_equalize = []
    _zoom = 0
    factor = 1
    pixelsize_ref = 0
    def __init__(self, image_ref_path):

        self.channel_BC = np.zeros((2),dtype = np.int)
        self.channel_BC[:,1] = 10
        path,header = os.path.split(image_ref_path)
        self.path = path

        super(Ui_VisorWindow, self).__init__()
        self.setupUi(self)

        self.setupForm()
        self.drawImage(self.imRef,self.imTemp,self.center,self.centerOrg_Ref,self.imExtra)

        h_r,w_r =self.imRef.shape
        self.shift_units_f = np.array([(self.centerOrg_Ref[0] - w_r * 0.5) * self.pixelsize_ref,
                                       -(self.centerOrg_Ref[1] - h_r * 0.5) * self.pixelsize_ref], dtype=np.float32)
        self.shift_f = self.centerOrg_Ref
        self.label_3.setText("Micrometers from the center :" + str(self.shift_units_f) + ", Position : " + str(self.centerOrg_Ref))


        self.fitInView()
        self.repaint()

    def setupUi(self, VisorWindow):
        VisorWindow.setObjectName(_fromUtf8("VisorWindow"))
        screen = QtGui.QDesktopWidget().screenGeometry()
        VisorWindow.resize(screen.width() * 1218.0 / 2880.0, screen.height() * 1265.0 / 1620.0)
        VisorWindow.setWindowFlags(VisorWindow.windowFlags() | QtCore.Qt.WindowMinMaxButtonsHint)
        self.gridLayout_2 = QtGui.QGridLayout(VisorWindow)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))

        self.gridLayout_2.addLayout(self.formLayout, 1, 0, 2, 1)
        self.label_4 = QtGui.QLabel(VisorWindow)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 1, 1, 1)
        self.horizontalSlider_b = QtGui.QSlider(VisorWindow)
        self.horizontalSlider_b.setMaximum(50)
        self.horizontalSlider_b.setMinimum(-50)
        self.horizontalSlider_b.setSingleStep(10)
        self.horizontalSlider_b.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_b.setInvertedAppearance(False)
        self.horizontalSlider_b.setInvertedControls(False)
        self.horizontalSlider_b.setObjectName(_fromUtf8("horizontalSlider_b"))
        self.gridLayout_2.addWidget(self.horizontalSlider_b, 1, 2, 1, 1)
        self.label_5 = QtGui.QLabel(VisorWindow)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 2, 1, 1, 1)
        self.horizontalSlider_c = QtGui.QSlider(VisorWindow)
        self.horizontalSlider_c.setMaximum(100)
        self.horizontalSlider_c.setMinimum(0)
        self.horizontalSlider_c.setSingleStep(10)
        self.horizontalSlider_c.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_c.setObjectName(_fromUtf8("horizontalSlider_c"))
        self.gridLayout_2.addWidget(self.horizontalSlider_c, 2, 2, 1, 1)
        self.comboBoxChannel = QtGui.QComboBox(VisorWindow)
        self.comboBoxChannel.setObjectName(_fromUtf8("comboBoxChannel"))
        self.comboBoxChannel.addItem(_fromUtf8(""))
        self.comboBoxChannel.addItem(_fromUtf8(""))
        self.comboBoxChannel.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.comboBoxChannel, 3, 2, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.checkBox_c1 = QtGui.QCheckBox(VisorWindow)
        self.checkBox_c1.setText(_fromUtf8(""))
        self.checkBox_c1.setObjectName(_fromUtf8("checkBox_c1"))
        self.horizontalLayout_5.addWidget(self.checkBox_c1)

        self.label_12 = QtGui.QLabel(VisorWindow)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_5.addWidget(self.label_12)
        self.comboBox_image_1 = QtGui.QComboBox(VisorWindow)
        self.comboBox_image_1.setObjectName(_fromUtf8("comboBox_image_1"))
        self.horizontalLayout_5.addWidget(self.comboBox_image_1)
        self.checkBox_equalize_1 = QtGui.QCheckBox(VisorWindow)
        self.checkBox_equalize_1.setObjectName(_fromUtf8("checkBox_equalize_1"))
        self.horizontalLayout_5.addWidget(self.checkBox_equalize_1)
        self.gridLayout.addLayout(self.horizontalLayout_5, 0, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.checkBox_c3 = QtGui.QCheckBox(VisorWindow)
        self.checkBox_c3.setText(_fromUtf8(""))
        self.checkBox_c3.setObjectName(_fromUtf8("checkBox_c3"))
        self.horizontalLayout_4.addWidget(self.checkBox_c3)
        self.label_7 = QtGui.QLabel(VisorWindow)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_4.addWidget(self.label_7)
        self.comboBox_image_3 = QtGui.QComboBox(VisorWindow)
        self.comboBox_image_3.setObjectName(_fromUtf8("comboBox_image_3"))
        self.horizontalLayout_4.addWidget(self.comboBox_image_3)
        self.checkBox_equalize_3 = QtGui.QCheckBox(VisorWindow)
        self.checkBox_equalize_3.setObjectName(_fromUtf8("checkBox_equalize_3"))
        self.horizontalLayout_4.addWidget(self.checkBox_equalize_3)
        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.checkBox_c2 = QtGui.QCheckBox(VisorWindow)
        self.checkBox_c2.setText(_fromUtf8(""))
        self.checkBox_c2.setObjectName(_fromUtf8("checkBox_c2"))
        self.horizontalLayout_3.addWidget(self.checkBox_c2)
        self.label_6 = QtGui.QLabel(VisorWindow)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_3.addWidget(self.label_6)
        self.comboBox_image_2 = QtGui.QComboBox(VisorWindow)
        self.comboBox_image_2.setObjectName(_fromUtf8("comboBox_image_2"))
        self.horizontalLayout_3.addWidget(self.comboBox_image_2)
        self.checkBox_equalize_2 = QtGui.QCheckBox(VisorWindow)
        self.checkBox_equalize_2.setObjectName(_fromUtf8("checkBox_equalize_2"))
        self.horizontalLayout_3.addWidget(self.checkBox_equalize_2)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(VisorWindow)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 4, 0, 1, 3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton_Savepic = QtGui.QPushButton(VisorWindow)
        self.pushButton_Savepic.setObjectName(_fromUtf8("pushButton_Savepic"))
        self.horizontalLayout.addWidget(self.pushButton_Savepic)


        self.gridLayout_2.addLayout(self.horizontalLayout, 5, 1, 1, 2)
        self.graphicsView = QtGui.QGraphicsView(VisorWindow)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout_2.addWidget(self.graphicsView, 0, 0, 1, 3)

        self._zoom = 0
        self._scene = QtGui.QGraphicsScene(self)
        self._photo = QtGui.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.graphicsView.setScene(self._scene)
        self.graphicsView.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsView.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.graphicsView.setFrameShape(QtGui.QFrame.NoFrame)

        self.horizontalSlider_c.setValue(10)

    

        QtCore.QObject.connect(self.checkBox_c1, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.redraw)
        QtCore.QObject.connect(self.checkBox_c2, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.redraw)
        QtCore.QObject.connect(self.checkBox_c3, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.redraw)
        QtCore.QObject.connect(self.checkBox_equalize_1, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.redraw)
        QtCore.QObject.connect(self.checkBox_equalize_2, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.redraw)
        QtCore.QObject.connect(self.checkBox_equalize_3, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.redraw)

        QtCore.QObject.connect(self.horizontalSlider_b, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.OnChangeBrightnessContrast)
        QtCore.QObject.connect(self.horizontalSlider_c, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.OnChangeBrightnessContrast)
        QtCore.QObject.connect(self.doubleSpinBoxX, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.OnChangeX)
        QtCore.QObject.connect(self.doubleSpinBox_2, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.OnChangeY)

        QtCore.QObject.connect(self.pushButton_Savepic, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               self.savePic)

        QtCore.QObject.connect(self.pushButton_Ok, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               self.ifOK)
        QtCore.QObject.connect(self.pushButton_No, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               self.ifNO)

        QtCore.QObject.connect(self.comboBox_image_1, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(const QString&)")),
                               self.OnChange_image1)
        QtCore.QObject.connect(self.comboBox_image_2, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(const QString&)")),
                               self.OnChange_image2)
        QtCore.QObject.connect(self.comboBox_image_3, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(const QString&)")),
                               self.Onchange_image3)

        QtCore.QObject.connect(self.comboBoxChannel, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(const QString&)")),
                               self.OnChangeChannelBC)

        QtCore.QMetaObject.connectSlotsByName(VisorWindow)
        self.retranslateUi(VisorWindow)

    def retranslateUi(self, VisorWindow):
        VisorWindow.setWindowTitle(_translate("VisorWindow", "VisorWindow", None))
        self.label.setText(_translate("VisorWindow", "Shift X :", None))
        self.label_2.setText(_translate("VisorWindow", "Shift Y:", None))
        self.label_4.setText(_translate("VisorWindow", "Brightness:", None))
        self.label_5.setText(_translate("VisorWindow", "Contrast:", None))
        self.comboBoxChannel.setItemText(0, _translate("VisorWindow", "Channel 1", None))
        self.comboBoxChannel.setItemText(1, _translate("VisorWindow", "Channel 2", None))
        self.comboBoxChannel.setItemText(2, _translate("VisorWindow", "Channel 3", None))

        self.label_12.setText(_translate("VisorWindow", "Channel 1 Red - Reference:", None))
        self.checkBox_equalize_1.setText(_translate("VisorWindow", "Equalize", None))


        self.label_7.setText(_translate("VisorWindow", "Channel 3 Blue :", None))
        self.checkBox_equalize_3.setText(_translate("VisorWindow", "Equalize", None))

        self.label_6.setText(_translate("VisorWindow", "Channel 2 Green - Template:", None))
        self.checkBox_equalize_2.setText(_translate("VisorWindow", "Equalize", None))
        self.label_3.setText(_translate("VisorWindow", "Micrometers from the center : ", None))
        self.pushButton_Savepic.setText(_translate("VisorWindow", "Save", None))
        self.pushButton_Ok.setText(_translate("VisorWindow", "OK", None))
        self.pushButton_No.setText(_translate("VisorWindow", "No", None))
        self.setTabOrder(self.pushButton_Ok, self.pushButton_No)

    def fitInView(self):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            unity = self.graphicsView.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.graphicsView.scale(1 / unity.width(), 1 / unity.height())
            # viewrect = self.graphicsView.viewport().rect()
            #scenerect = self.graphicsView.transform().mapRect(rect)
            #factor = min(viewrect.width() / scenerect.width(),
            #             viewrect.height() / scenerect.height())
            #self.graphicsView.scale(factor, factor)
            self.graphicsView.centerOn(rect.center())
            self._zoom = 0


    def setupForm(self):
        self.setWindowTitle(self.tag)

    def setPhoto(self, pixmap=None):

        if pixmap and not pixmap.isNull():
            self.graphicsView.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self.graphicsView.setDragMode(QtGui.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    def zoomFactor(self):
        return self._zoom

    def wheelEvent(self, event):
        if not self._photo.pixmap().isNull():
            if event.delta() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.graphicsView.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def drawImage(self,imageRef,imageTemplate,center,centerorg=None,imageExtra = None,top_left=None,bottom_right=None):

        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(32, 32))

        imRef = clahe.apply(imageRef)
        imTemp = clahe.apply(imageTemplate)
        if (imageExtra is None):
            imageExtra = np.zeros(shape=(imRef.shape), dtype=np.uint8)

        h_s, w_s = imTemp.shape
        h_r, w_r = imRef.shape
        if(top_left is None and bottom_right is None):
            top_left = (int(center[0] - w_s / 2) + 1, int(center[1] - h_s / 2) + 1)
            bottom_right = (int(top_left[0] + w_s), int(top_left[1] + h_s))

        if(centerorg is None):
            centerorg = np.array([0,0],dtype=np.uint8)
        overlay = np.zeros(shape=imRef.shape + (3,), dtype=np.uint8)

        imageTemp = np.zeros(shape=(imRef.shape), dtype=np.uint8)
        imageTemp[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = imTemp
        if(self.checkBox_equalize_1.isChecked()):
            imRef = cv2.equalizeHist(imRef)
        if (self.checkBox_equalize_2.isChecked()):
            imageTemp = cv2.equalizeHist(imageTemp)
        if(self.checkBox_equalize_3.isChecked()):
            imageExtra = cv2.equalizeHist(imageExtra)

        if(self.checkBox_c1.isChecked()):
            overlay[..., 2] = imRef
        if(self.checkBox_c2.isChecked()):
            overlay[..., 1] = imageTemp
        if(self.checkBox_c3.isChecked()):
            overlay[..., 0] = imageExtra

        cv2.circle(overlay,(int(centerorg[0]), int(centerorg[1])) , 3, (255, 125, 180), -1)
        cv2.circle(overlay, (int(center[0]), int(center[1])), 3, (0, 255, 255), 1)
        cv2.circle(overlay, (int(h_r*0.5), int(w_r*0.5)), 2, (255, 255, 255), -1)


        cv2.rectangle(overlay, top_left, bottom_right, (0, 255, 255), 1)

        imagename2 = self.path + "\\reg_t.jpg"
        cv2.imwrite(imagename2, overlay)
        #   self.graphicsView.setViewport(QGLWidget())
        self.setPhoto(QtGui.QPixmap(imagename2))
        if (self.factor > 0):
            self.graphicsView.scale(self.factor, self.factor)
        self.currentimage = overlay


    def OnChangeX(self, x):
        self.centerOrg_Ref = (self.centerOrg_Ref[0]-(self.center[0]-x),self.centerOrg_Ref[1])
        self.center = (x, self.center[1])
        h_s, w_s = self.imTemp.shape
        self.top_left = (int(x - w_s / 2 + 1), int(self.top_left[1]))
        self.bottom_right = (int(self.top_left[0] + w_s), int(self.bottom_right[1]))
        self.drawImage(self.imRef, self.imTemp, self.center, self.centerOrg_Ref, self.imExtra)

        h_r, w_r = self.imRef.shape
        self.shift_units_f = np.array([(self.centerOrg_Ref[0] - w_r * 0.5) * self.pixelsize_ref,
                                       -(self.centerOrg_Ref[1] - h_r * 0.5) * self.pixelsize_ref], dtype=np.float32)
        self.shift_f = self.centerOrg_Ref
        self.label_3.setText(
            "Micrometers from the center :" + str(self.shift_units_f) + ", Position : " + str(self.centerOrg_Ref))

    def OnChangeY(self, y):
        self.centerOrg_Ref = (self.centerOrg_Ref[0],self.centerOrg_Ref[1] - (self.center[1] - y))
        self.center = (self.center[0], y)
        w_s, h_s = self.imTemp.shape
        self.top_left = (int(self.top_left[0]), int(y - h_s / 2 + 1))
        self.bottom_right = (int(self.bottom_right[0]), int(self.top_left[1] + h_s))
        self.drawImage(self.imRef, self.imTemp, self.center, self.centerOrg_Ref,self.imExtra)
        h_r, w_r = self.imRef.shape
        self.shift_units_f = np.array([(self.centerOrg_Ref[0] - w_r * 0.5) * self.pixelsize_ref,
                                       -(self.centerOrg_Ref[1] - h_r * 0.5) * self.pixelsize_ref], dtype=np.float32)
        self.shift_f = self.centerOrg_Ref
        self.label_3.setText(
            "Micrometers from the center :" + str(self.shift_units_f) + ", Position : " + str(self.centerOrg_Ref))

    def ifOK(self):
        self.shift_f = self.centerOrg_Ref
        self.accept()

    def ifNO(self):
        self.shift_f = np.array([np.inf, np.inf])
        self.shift_unit_f = np.array([np.inf, np.inf])
        self.accept()


    def findShiftWindow(self,inputReference_path, inputShifted_path,center_obj = None):
        # Get metadata from images
        infoRef = getInfoHeader(inputReference_path)
        infoCorr = getInfoHeader(inputShifted_path)
        self.pixelsize_ref = infoRef['PixelSize']
        # Check the biggest
        if (infoRef['PixelSize'] > infoCorr['PixelSize']):
            # Crop image from center of BIG
            imageRef = cv2.imread(inputReference_path, 0)
            cv2.normalize(imageRef, imageRef, np.min(imageRef), np.max(imageRef), norm_type=cv2.NORM_MINMAX)
            self.original_imRef = imageRef
            imageCorr = cv2.imread(inputShifted_path, 0)
            cv2.normalize(imageCorr, imageCorr, np.min(imageCorr), np.max(imageCorr), norm_type=cv2.NORM_MINMAX)
        else:
            # Crop image from center of BIG
            imageRef = cv2.imread(inputShifted_path, 0)
            cv2.normalize(imageRef, imageRef, np.min(imageRef), np.max(imageRef), norm_type=cv2.NORM_MINMAX)
            self.original_imRef = imageRef
            imageCorr = cv2.imread(inputReference_path, 0)
            cv2.normalize(imageCorr, imageCorr, np.min(imageCorr), np.max(imageCorr), norm_type=cv2.NORM_MINMAX)

        h, w = imageCorr.shape
        scale_factor = float(infoCorr['PixelSize']) / float(infoRef['PixelSize'])
        w_s = int(w * scale_factor)
        h_s = int(h * scale_factor)
        template = cv2.resize(imageCorr, (w_s, h_s))
        self.original_template = template
        res = cv2.matchTemplate(imageRef, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        self.top_left = max_loc
        self.bottom_right = (self.top_left[0] + w_s, self.top_left[1] + h_s)
        crop_img = imageRef[self.top_left[1]:self.bottom_right[1],self.top_left[0]:self.bottom_right[0]]  # Crop from x, y, w, h -> 100, 200, 300, 400
        shift, error, diffphase = register_translation(crop_img, template, int(1 / scale_factor))
        print("Detected extra pixel offset (y, x):")
        print(shift)
        self.center = (self.top_left[0] + w_s * 0.5 + shift[0], self.top_left[1] + h_s * 0.5 + shift[1])
        # plot_overlay(imageRef, template, center, top_left, bottom_right)


        # offset_image = fourier_shift(np.fft.fftn(template), shift)
        # offset_image = np.fft.ifftn(offset_image)
        # overlay_images(crop_img,offset_image.real,'Reference image','Offset image','Overlay')



        m_path, header = os.path.split(inputReference_path)
        if (center_obj is None):
            center_obj = self.center
        else:
            # These are coordinates from the template
            # First we scale them
            center_obj = np.array(center_obj * scale_factor, dtype=np.int)
            center_obj = np.array([center_obj[0] +self.center[0] - w_s * 0.5, center_obj[1]+self.center[1] - h_s * 0.5], dtype=np.int)


        return shift, center_obj, imageRef, template



    def OnChangeBrightnessContrast(self):
        if (str(self.comboBoxChannel.currentText()) == "Channel 1"):
            self.channel_BC[0,0]= int(self.horizontalSlider_b.value())
            self.channel_BC[0,1] = int(self.horizontalSlider_c.value())
            iimRef = cv2.add(self.original_imRef,int(self.horizontalSlider_b.value()))
            self.imRef = cv2.multiply(iimRef,(self.horizontalSlider_c.value()/10.0))
        elif (str(self.comboBoxChannel.currentText()) == "Channel 2"):
            self.channel_BC[1, 0] = int(self.horizontalSlider_b.value())
            self.channel_BC[1, 1] = int(self.horizontalSlider_c.value())
            iimTemp = cv2.add(self.original_template, int(self.horizontalSlider_b.value()))
            self.imTemp = cv2.multiply(iimTemp,(self.horizontalSlider_c.value()/10.0))

        elif (str(self.comboBoxChannel.currentText()) == "Channel 3"):
            self.channel_BC[2, 0] = int(self.horizontalSlider_b.value())
            self.channel_BC[2, 1] = int(self.horizontalSlider_c.value())
            iimExtra = cv2.add(self.original_imExtra, int(self.horizontalSlider_b.value()))
            self.imExtra = cv2.multiply(iimExtra,(self.horizontalSlider_c.value()/10.0))
            self.drawImage(self.imRef, self.imTemp, self.center, self.centerOrg_Ref, iimExtra)
            return
        self.drawImage(self.imRef, self.imTemp, self.center, self.centerOrg_Ref, self.imExtra)
        return
    def savePic(self,):
        fname = QtGui.QFileDialog.getSaveFileName(self, "Save picture",self.path+"\\image.tif", "*.tif,.*jpg",
                                                       "Picture Files (*.tif,*.jpg)")
        cv2.imwrite(str(fname), self.currentimage)

    def redraw(self):
        self.drawImage(self.imRef, self.imTemp, self.center, self.centerOrg_Ref, self.imExtra)

    def OnChange_image1(self):
        self.shift, self.centerOrg_Ref, self.imRef, self.imTemp = self.findShiftWindow(str(self.comboBox_image_1.currentText()), self.imTemplist[0], self.centerOrg_Temp)
        self.doubleSpinBoxX.setValue(self.center[0])
        self.doubleSpinBox_2.setValue(self.center[1])
        h_r, w_r = self.imRef.shape
        self.shift_units_f = np.array([(self.centerOrg_Ref[0] - w_r * 0.5) * self.pixelsize_ref ,-(self.centerOrg_Ref[1] - h_r * 0.5)* self.pixelsize_ref],dtype = np.float32)
        self.shift_f = self.centerOrg_Ref
        self.label_3.setText("Micrometers from the center :" + str(self.shift_units_f )+", Position : "+str(self.centerOrg_Ref))
        self.resetBC("Channel 1")
        self.redraw()
    def OnChange_image2(self):
        self.shift, self.shift_unit, self.centerOrg_Ref, self.imRef, self.imTemp = self.findShiftWindow(
            str(self.comboBox_image_1.currentText()), self.imTemplist[0], self.centerOrg_Temp)
        self.doubleSpinBoxX.setValue(self.center[0])
        self.doubleSpinBox_2.setValue(self.center[1])
        h_r, w_r = self.imRef.shape
        self.shift_units_f = np.array([(self.centerOrg_Ref[0] - w_r * 0.5) * self.pixelsize_ref,
                                       -(self.centerOrg_Ref[1] - h_r * 0.5) * self.pixelsize_ref], dtype=np.float32)
        self.shift_f = self.centerOrg_Ref
        self.label_3.setText(
            "Micrometers from the center :" + str(self.shift_units_f) + ", Position : " + str(self.centerOrg_Ref))
        self.resetBC("Channel 2")
        self.redraw()
    def Onchange_image3(self):
        extraimg = cv2.imread(str(self.comboBox_image_3.currentText()), 0)
        cv2.normalize(extraimg, extraimg, np.min(extraimg), np.max(extraimg), norm_type=cv2.NORM_MINMAX)
        self.imExtra = np.zeros(shape=(self.imRef.shape), dtype=np.uint8)
        if (np.all(np.array_equal(extraimg.shape, self.imRef.shape))):
            cv2.normalize(extraimg, extraimg, np.min(extraimg), np.max(extraimg), norm_type=cv2.NORM_MINMAX)
            self.original_imExtra = extraimg
            self.imExtra = extraimg
            self.resetBC("Channel 3")
        self.redraw()

    def OnChangeChannelBC(self):
        if (str(self.comboBoxChannel.currentText()) == "Channel 1"):
            self.horizontalSlider_b.setValue(self.channel_BC[0,0])
            self.horizontalSlider_c.setValue(self.channel_BC[0,1])
        elif (str(self.comboBoxChannel.currentText()) == "Channel 2"):
            self.horizontalSlider_b.setValue(self.channel_BC[1, 0])
            self.horizontalSlider_c.setValue(self.channel_BC[1, 1])
        elif (str(self.comboBoxChannel.currentText()) == "Channel 3"):
            self.horizontalSlider_b.setValue(self.channel_BC[2, 0])
            self.horizontalSlider_c.setValue(self.channel_BC[2, 1])

    def resetBC(self,channel):
        if (channel == "Channel 1"):
           self.channel_BC[0, 0] = 0
           self.channel_BC[0, 1] = 10
        elif (channel == "Channel 2"):
            self.channel_BC[1, 0] = 0
            self.channel_BC[1, 1] = 10
        elif (channel == "Channel 3"):
            self.channel_BC[2, 0] = 0
            self.channel_BC[2, 1] = 10
        self.OnChangeChannelBC()