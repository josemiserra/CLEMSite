# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\JMS\Documents\msite\MSite\msiteSEM\UI\register.ui'
#
# Created: Sat Sep 03 19:12:29 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtOpenGL import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os,sys
import cv2
import numpy as np
sys.path.append(os.getcwd()+"\\image_an")
from common.image_an.readers import getInfoHeader
from skimage.feature import register_translation
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class Ui_RegisterWindow(QtWidgets.QDialog):
    shift = []
    m_equalize = []
    _zoom = 0
    factor = 1
    pixelsize_ref = 0
    _menu_config = {}
    imRef = None
    imTemp = None

    def __init__(self, imageRef_filelist, imageTemplate_filelist, imageExtra_filelist = None, icenterorg = None, title = "Registration", menu_config = {}):

        self.imReflist = imageRef_filelist
        self.imTemplist = imageTemplate_filelist
        self.imExtralist = imageExtra_filelist
        self.centerOrg_Temp = icenterorg
        self.centerOrg_Ref = []

        self.tag = title
        self.centerTemplate = []
        self.top_left = []
        self.bottom_right = []

        super(Ui_RegisterWindow, self).__init__()
        self.setupUi(self)
        self.updateConfiguration(menu_config)
        self.setupForm()

        self.updatePixelDifferenceStatus()




    def updateConfiguration(self, menu_config):
        if len(menu_config.keys()) == 0:
            self._menu_config['sel_box1'] = 0
            self._menu_config['sel_box2'] = 0
            self._menu_config['sel_box3'] = 0
            self.resetBC()
        else:
            self._menu_config['sel_box1'] = menu_config['sel_box1']
            self._menu_config['sel_box2'] = menu_config['sel_box2']
            self._menu_config['sel_box3'] = menu_config['sel_box3']
            if 'BC' in menu_config.keys():
                self.channel_BC = self._menu_config['BC']
                self.horizontalSlider_c.blockSignals(True)
                self.horizontalSlider_b.blockSignals(True)
                self.horizontalSlider_b.setValue(self.channel_BC[0,0])
                self.horizontalSlider_c.setValue(self.channel_BC[0,1])
                self.horizontalSlider_c.blockSignals(False)
                self.horizontalSlider_b.blockSignals(False)
            else:
                self.resetBC()

        self.comboBox_image_1.blockSignals(True)
        self.comboBox_image_2.blockSignals(True)
        self.comboBox_image_3.blockSignals(True)
        self.comboBox_image_1.setCurrentIndex(int(self._menu_config['sel_box1']))
        self.comboBox_image_2.setCurrentIndex(int(self._menu_config['sel_box2']))
        self.comboBox_image_3.setCurrentIndex(int(self._menu_config['sel_box3']))
        self.comboBox_image_1.blockSignals(False)
        self.comboBox_image_2.blockSignals(False)
        self.comboBox_image_3.blockSignals(False)


    def updatePixelDifferenceStatus(self):
        h_r,w_r =self.imRef.shape
        shift_f = np.array(self.centerOrg_Ref - np.array([h_r*0.5,w_r*0.5]))
        self.label_3.setText("Pixels from the center :" + str(shift_f) + ", Position : " + str(self.centerOrg_Ref))

    def setupUi(self, RegisterWindow):
        RegisterWindow.setObjectName(_fromUtf8("RegisterWindow"))
        screen = QDesktopWidget().screenGeometry()
        RegisterWindow.resize(screen.width() * 1218.0 / 2880.0, screen.height() * 1265.0 / 1620.0)
        RegisterWindow.setWindowFlags(RegisterWindow.windowFlags() | QtCore.Qt.WindowMinMaxButtonsHint)
        self.gridLayout_2 = QGridLayout(RegisterWindow)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.formLayout = QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QLabel(RegisterWindow)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)
        self.doubleSpinBoxX = QDoubleSpinBox(RegisterWindow)
        self.doubleSpinBoxX.setMaximum(8096.0)
        self.doubleSpinBoxX.setSingleStep(0.5)
        self.doubleSpinBoxX.setObjectName(_fromUtf8("doubleSpinBoxX"))
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.doubleSpinBoxX)
        self.label_2 = QLabel(RegisterWindow)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)
        self.doubleSpinBox_2 = QDoubleSpinBox(RegisterWindow)
        self.doubleSpinBox_2.setMaximum(8096.0)
        self.doubleSpinBox_2.setSingleStep(0.5)
        self.doubleSpinBox_2.setObjectName(_fromUtf8("doubleSpinBox_2"))
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_2)
        self.gridLayout_2.addLayout(self.formLayout, 1, 0, 2, 1)
        self.label_4 = QLabel(RegisterWindow)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 1, 1, 1)
        self.horizontalSlider_b = QSlider(RegisterWindow)
        self.horizontalSlider_b.setMaximum(50)
        self.horizontalSlider_b.setMinimum(-50)
        self.horizontalSlider_b.setSingleStep(10)
        self.horizontalSlider_b.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_b.setInvertedAppearance(False)
        self.horizontalSlider_b.setInvertedControls(False)
        self.horizontalSlider_b.setObjectName(_fromUtf8("horizontalSlider_b"))
        self.gridLayout_2.addWidget(self.horizontalSlider_b, 1, 2, 1, 1)
        self.label_5 = QLabel(RegisterWindow)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 2, 1, 1, 1)
        self.horizontalSlider_c = QSlider(RegisterWindow)
        self.horizontalSlider_c.setMaximum(100)
        self.horizontalSlider_c.setMinimum(0)
        self.horizontalSlider_c.setSingleStep(10)
        self.horizontalSlider_c.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_c.setObjectName(_fromUtf8("horizontalSlider_c"))
        self.gridLayout_2.addWidget(self.horizontalSlider_c, 2, 2, 1, 1)
        self.comboBoxChannel = QComboBox(RegisterWindow)
        self.comboBoxChannel.setObjectName(_fromUtf8("comboBoxChannel"))
        self.comboBoxChannel.addItem(_fromUtf8(""))
        self.comboBoxChannel.addItem(_fromUtf8(""))
        self.comboBoxChannel.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.comboBoxChannel, 3, 2, 1, 1)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.checkBox_c1 = QCheckBox(RegisterWindow)
        self.checkBox_c1.setText(_fromUtf8(""))
        self.checkBox_c1.setObjectName(_fromUtf8("checkBox_c1"))
        self.horizontalLayout_5.addWidget(self.checkBox_c1)

        self.label_12 = QLabel(RegisterWindow)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_5.addWidget(self.label_12)
        self.comboBox_image_1 = QComboBox(RegisterWindow)
        self.comboBox_image_1.setObjectName(_fromUtf8("comboBox_image_1"))
        self.horizontalLayout_5.addWidget(self.comboBox_image_1)
        self.checkBox_equalize_1 = QCheckBox(RegisterWindow)
        self.checkBox_equalize_1.setObjectName(_fromUtf8("checkBox_equalize_1"))
        self.horizontalLayout_5.addWidget(self.checkBox_equalize_1)
        self.gridLayout.addLayout(self.horizontalLayout_5, 0, 0, 1, 1)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.checkBox_c3 = QCheckBox(RegisterWindow)
        self.checkBox_c3.setText(_fromUtf8(""))
        self.checkBox_c3.setObjectName(_fromUtf8("checkBox_c3"))
        self.horizontalLayout_4.addWidget(self.checkBox_c3)
        self.label_7 = QLabel(RegisterWindow)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_4.addWidget(self.label_7)
        self.comboBox_image_3 = QComboBox(RegisterWindow)
        self.comboBox_image_3.setObjectName(_fromUtf8("comboBox_image_3"))
        self.horizontalLayout_4.addWidget(self.comboBox_image_3)
        self.checkBox_equalize_3 = QCheckBox(RegisterWindow)
        self.checkBox_equalize_3.setObjectName(_fromUtf8("checkBox_equalize_3"))
        self.horizontalLayout_4.addWidget(self.checkBox_equalize_3)
        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.checkBox_c2 = QCheckBox(RegisterWindow)
        self.checkBox_c2.setText(_fromUtf8(""))
        self.checkBox_c2.setObjectName(_fromUtf8("checkBox_c2"))
        self.horizontalLayout_3.addWidget(self.checkBox_c2)
        self.label_6 = QLabel(RegisterWindow)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_3.addWidget(self.label_6)
        self.comboBox_image_2 = QComboBox(RegisterWindow)
        self.comboBox_image_2.setObjectName(_fromUtf8("comboBox_image_2"))
        self.horizontalLayout_3.addWidget(self.comboBox_image_2)
        self.checkBox_equalize_2 = QCheckBox(RegisterWindow)
        self.checkBox_equalize_2.setObjectName(_fromUtf8("checkBox_equalize_2"))
        self.horizontalLayout_3.addWidget(self.checkBox_equalize_2)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.label_3 = QLabel(RegisterWindow)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 4, 0, 1, 3)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton_Savepic = QPushButton(RegisterWindow)
        self.pushButton_Savepic.setObjectName(_fromUtf8("pushButton_Savepic"))
        self.horizontalLayout.addWidget(self.pushButton_Savepic)

        self.pushButton_Ok = QPushButton(RegisterWindow)
        self.pushButton_Ok.setObjectName(_fromUtf8("pushButton_Ok"))
        self.horizontalLayout.addWidget(self.pushButton_Ok)
        self.pushButton_No = QPushButton(RegisterWindow)
        self.pushButton_No.setObjectName(_fromUtf8("pushButton_No"))
        self.horizontalLayout.addWidget(self.pushButton_No)
        self.gridLayout_2.addLayout(self.horizontalLayout, 5, 1, 1, 2)
        self.graphicsView = QGraphicsView(RegisterWindow)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout_2.addWidget(self.graphicsView, 0, 0, 1, 3)

        self._zoom = 0
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.graphicsView.setScene(self._scene)
        self.graphicsView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsView.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.graphicsView.setFrameShape(QFrame.NoFrame)

        self.checkBox_c1.setChecked(True)
        self.checkBox_c2.setChecked(True)


        for ind in range(len(self.imReflist)):
            self.comboBox_image_1.addItem(_fromUtf8(""))
            self.comboBox_image_1.setItemText(ind,self.imReflist[ind])

        for ind in range(len(self.imTemplist)):
            self.comboBox_image_2.addItem(_fromUtf8(""))
            self.comboBox_image_2.setItemText(ind,self.imTemplist[ind])

        for ind in range(len(self.imExtralist)):
            self.comboBox_image_3.addItem(_fromUtf8(""))
            self.comboBox_image_3.setItemText(ind,self.imExtralist[ind])

        self.retranslateUi(RegisterWindow)
        self.checkBox_c1.stateChanged[int].connect(self.redraw)
        self.checkBox_c2.stateChanged[int].connect(self.redraw)
        self.checkBox_c3.stateChanged[int].connect(self.redraw)
        self.checkBox_equalize_1.stateChanged[int].connect(self.redraw)
        self.checkBox_equalize_2.stateChanged[int].connect(self.redraw)
        self.checkBox_equalize_3.stateChanged[int].connect(self.redraw)

        self.horizontalSlider_b.valueChanged[int].connect(self.OnChangeBrightnessContrast)
        self.horizontalSlider_c.valueChanged[int].connect(self.OnChangeBrightnessContrast)
        self.doubleSpinBoxX.valueChanged[float].connect(self.OnChangeX)
        self.doubleSpinBox_2.valueChanged[float].connect(self.OnChangeY)

        self.pushButton_Savepic.clicked.connect(self.savePic)
        self.pushButton_Ok.clicked.connect(self.ifOK)
        self.pushButton_No.clicked.connect(self.ifNO)
        self.comboBox_image_1.currentIndexChanged.connect(self.OnChange_image1)
        self.comboBox_image_2.currentIndexChanged.connect(self.OnChange_image2)
        self.comboBox_image_3.currentIndexChanged.connect(self.Onchange_image3)
        self.comboBoxChannel.currentIndexChanged.connect(self.OnChangeChannel)

        QtCore.QMetaObject.connectSlotsByName(RegisterWindow)


    def retranslateUi(self, RegisterWindow):
        RegisterWindow.setWindowTitle(_translate("RegisterWindow", "RegisterWindow", None))
        self.label.setText(_translate("RegisterWindow", "Shift X :", None))
        self.label_2.setText(_translate("RegisterWindow", "Shift Y:", None))
        self.label_4.setText(_translate("RegisterWindow", "Brightness:", None))
        self.label_5.setText(_translate("RegisterWindow", "Contrast:", None))
        self.comboBoxChannel.setItemText(0, _translate("RegisterWindow", "Channel 1", None))
        self.comboBoxChannel.setItemText(1, _translate("RegisterWindow", "Channel 2", None))
        self.comboBoxChannel.setItemText(2, _translate("RegisterWindow", "Channel 3", None))
        self.comboBoxChannel.setCurrentIndex(0)

        self.label_12.setText(_translate("RegisterWindow", "Channel 1 Red - Reference:", None))
        self.checkBox_equalize_1.setText(_translate("RegisterWindow", "Equalize", None))

        self.label_7.setText(_translate("RegisterWindow", "Channel 3 Blue :", None))
        self.checkBox_equalize_3.setText(_translate("RegisterWindow", "Equalize", None))

        self.label_6.setText(_translate("RegisterWindow", "Channel 2 Green - Template:", None))
        self.checkBox_equalize_2.setText(_translate("RegisterWindow", "Equalize", None))
        self.label_3.setText(_translate("RegisterWindow", "Pixels from the center : ", None))
        self.pushButton_Savepic.setText(_translate("RegisterWindow", "Save", None))
        self.pushButton_Ok.setText(_translate("RegisterWindow", "OK", None))
        self.pushButton_No.setText(_translate("RegisterWindow", "No", None))
        self.setTabOrder(self.pushButton_Ok, self.pushButton_No)

    def fitInView(self):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            unity = self.graphicsView.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.graphicsView.scale(1 / unity.width(), 1 / unity.height())
            self.graphicsView.centerOn(rect.center())
            self._zoom = 0

    def setupForm(self):
        self.setWindowTitle(self.tag)

        path, header = os.path.split(self.imReflist[self._menu_config['sel_box1']])
        self.path = path
        if np.any(self.centerOrg_Temp<0):
            self.centerOrg_Temp = None
        shift, self.centerOrg_Ref, self.imRef, self.imTemp = self.findShiftWindow(self.imReflist[self._menu_config['sel_box1']], self.imTemplist[self._menu_config['sel_box2']], self.centerOrg_Temp)
        self.imExtra = np.zeros(shape=(self.imRef.shape), dtype=np.uint8)
        if (self.imExtralist is not None):
            extraimg = cv2.imread(self.imExtralist[self._menu_config['sel_box3']], 0)
            if (np.all(np.array_equal(extraimg.shape, self.imRef.shape))):
                cv2.normalize(extraimg, extraimg, np.min(extraimg), np.max(extraimg), norm_type=cv2.NORM_MINMAX)
                self.imExtra = extraimg
        self.original_imExtra = self.imExtra
        self.doubleSpinBoxX.setValue(self.centerTemplate[0])
        self.doubleSpinBox_2.setValue(self.centerTemplate[1])
        self.OnChangeBrightnessContrast()
        self.drawImage(self.imRef, self.imTemp, self.centerTemplate, self.centerOrg_Ref, self.imExtra)
        self.fitInView()
        self.repaint()

    def setPhoto(self, pixmap=None):

        if pixmap and not pixmap.isNull():
            self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self.graphicsView.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())

    def zoomFactor(self):
        return self._zoom


    def wheelEvent(self, event):
        if not self._photo.pixmap().isNull():

            numDegrees = event.angleDelta()/8
            if(numDegrees):
                numSteps = numDegrees.y()/15
                if numSteps > 0:
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

    def drawImage(self,imageRef,imageTemplate,center,centerorg=None,imageExtra = None,itop_left=None,ibottom_right=None):
        # TODO:
        # Bug here:
        #     imageTemp[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = imTemp
        #     ValueError: could not broadcast input array from shape (680,680) into shape (679,679)

        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(32, 32))

        imRef = clahe.apply(imageRef)
        imTemp = clahe.apply(imageTemplate)
        if (imageExtra is None):
            imageExtra = np.zeros(shape=(imRef.shape), dtype=np.uint8)

        h_s, w_s = imTemp.shape
        h_r, w_r = imRef.shape
        top_left = itop_left
        bottom_right = ibottom_right
        if(itop_left is None and ibottom_right is None):
            top_left = np.array([int(center[0] - w_s*0.5), int(center[1] - h_s*0.5)],dtype = np.int)
            bottom_right = np.array([int(round(top_left[0] + w_s)), int(round(top_left[1] + h_s))],dtype=np.int)

        if top_left[0] < 0: top_left[0] = 0
        if top_left[1] < 0: top_left[1] = 0
        if bottom_right[0] < 0: bottom_right[0] = 0
        if bottom_right[1] < 0: bottom_right[1] = 0
        w = min(imRef.shape)
        if top_left[0] > w: top_left[0] = w
        if top_left[1] > w: top_left[1] = w
        if bottom_right[0] > w: bottom_right[0] = w
        if bottom_right[1] > w: bottom_right[1] = w

        if(centerorg is None):
            centerorg = np.array([0,0],dtype=np.uint8)
        overlay = np.zeros(shape=imRef.shape + (3,), dtype=np.uint8)

        imageTemp = np.zeros(shape=(imRef.shape), dtype=np.uint8)
        lim1 = np.abs(top_left[1]-bottom_right[1])
        lim2 = np.abs(top_left[0]-bottom_right[0])
        imageTemp[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = imTemp[0:lim1,0:lim2]

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

        cv2.circle(overlay,(int(centerorg[0]), int(centerorg[1])) , 2, (255, 50, 255), -1)
        cv2.circle(overlay, (int(center[0]), int(center[1])), 3, (0, 255, 255), 1)
        # cv2.circle(overlay, (int(h_r*0.5), int(w_r*0.5)), 2, (255, 255, 255), -1)

        cv2.rectangle(overlay, (int(top_left[0]), int(top_left[1])), (int(bottom_right[0]), int(bottom_right[1])), (0, 255, 255), 1)

        imagename2 = self.path + "\\"+self.tag.split(':')[0]+"_reg_t.jpg"
        self.currentimage = overlay
        cv2.imwrite(str(imagename2), self.currentimage)
        #   self.graphicsView.setViewport(QGLWidget())
        self.setPhoto(QPixmap(imagename2))
        if (self.factor > 0):
            self.graphicsView.scale(self.factor, self.factor)


    def OnChangeX(self, x):
        self.centerOrg_Ref = (self.centerOrg_Ref[0]-(self.centerTemplate[0]-x),self.centerOrg_Ref[1])
        self.centerTemplate = (x, self.centerTemplate[1])
        h_s, w_s = self.imTemp.shape
        self.top_left = (int(x - w_s / 2 + 1), int(self.top_left[1]))
        self.bottom_right = (int(self.top_left[0] + w_s), int(self.bottom_right[1]))
        self.drawImage(self.imRef, self.imTemp, self.centerTemplate, self.centerOrg_Ref, self.imExtra)
        self.updatePixelDifferenceStatus()

    def OnChangeY(self, y):
        self.centerOrg_Ref = (self.centerOrg_Ref[0],self.centerOrg_Ref[1] - (self.centerTemplate[1] - y))
        self.centerTemplate = (self.centerTemplate[0], y)
        w_s, h_s = self.imTemp.shape
        self.top_left = (int(self.top_left[0]), int(y - h_s / 2 + 1))
        self.bottom_right = (int(self.bottom_right[0]), int(self.top_left[1] + h_s))
        self.drawImage(self.imRef, self.imTemp, self.centerTemplate, self.centerOrg_Ref,self.imExtra)
        self.updatePixelDifferenceStatus()

    def ifOK(self):
        self._menu_config['BC'] = self.channel_BC
        self.accept()

    def ifNO(self):
        self.centerOrg_Ref = np.array([np.inf, np.inf])
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
        self.centerTemplate = (self.top_left[0] + w_s * 0.5 + shift[0], self.top_left[1] + h_s * 0.5 + shift[1])
        # plot_overlay(imageRef, template, center, top_left, bottom_right)
        # offset_image = fourier_shift(np.fft.fftn(template), shift)
        # offset_image = np.fft.ifftn(offset_image)
        # overlay_images(crop_img,offset_image.real,'Reference image','Offset image','Overlay')

        m_path, header = os.path.split(inputReference_path)
        if (center_obj is None):
            center_obj = self.centerTemplate
        else:
            # These are coordinates from the template
            # First we scale them
            center_obj = np.array(center_obj * scale_factor, dtype=np.int)
            center_obj = np.array([center_obj[0] +self.centerTemplate[0] - w_s * 0.5, center_obj[1]+self.centerTemplate[1] - h_s * 0.5], dtype=np.int)

        return shift, center_obj, imageRef, template



    def savePic(self,):
        fname,_ = QFileDialog.getSaveFileName(self, "Save picture",self.path+"\\extra_image.tif", "*.tif,.*jpg",
                                                       "Picture Files (*.tif,*.jpg)")

        if(not fname):
            return
        cv2.imwrite(str(fname), self.currentimage)

    def redraw(self):
        if self.imRef is None:
            return
        self.drawImage(self.imRef, self.imTemp, self.centerTemplate, self.centerOrg_Ref, self.imExtra)

    def OnChange_image1(self):
        self._menu_config['sel_box1'] =  self.comboBox_image_1.currentIndex()
        shift, self.centerOrg_Ref, self.imRef, self.imTemp = self.findShiftWindow(str(self.comboBox_image_1.currentText()), self.imTemplist[0], self.centerOrg_Temp)

        self.doubleSpinBox_2.blockSignals(True)
        self.doubleSpinBoxX.blockSignals(True)

        self.doubleSpinBoxX.setValue(self.centerTemplate[0])
        self.doubleSpinBox_2.setValue(self.centerTemplate[1])

        self.doubleSpinBox_2.blockSignals(False)
        self.doubleSpinBoxX.blockSignals(False)

        self.updatePixelDifferenceStatus()
        self.OnChangeBrightnessContrast()

    def OnChange_image2(self):
        self._menu_config['sel_box2'] = self.comboBox_image_2.currentIndex()
        shift, self.centerOrg_Ref, self.imRef, self.imTemp = self.findShiftWindow(
            str(self.comboBox_image_1.currentText()), self.imTemplist[0], self.centerOrg_Temp)

        self.doubleSpinBox_2.blockSignals(True)
        self.doubleSpinBoxX.blockSignals(True)

        self.doubleSpinBoxX.setValue(self.centerTemplate[0])
        self.doubleSpinBox_2.setValue(self.centerTemplate[1])

        self.doubleSpinBox_2.blockSignals(False)
        self.doubleSpinBoxX.blockSignals(False)

        self.updatePixelDifferenceStatus()
        self.OnChangeBrightnessContrast()


    def Onchange_image3(self):
        self._menu_config['sel_box3'] = self.comboBox_image_3.currentIndex()
        extraimg = cv2.imread(str(self.comboBox_image_3.currentText()), 0)
        cv2.normalize(extraimg, extraimg, np.min(extraimg), np.max(extraimg), norm_type=cv2.NORM_MINMAX)
        self.imExtra = np.zeros(shape=(self.imRef.shape), dtype=np.uint8)
        if (np.all(np.array_equal(extraimg.shape, self.imRef.shape))):
            cv2.normalize(extraimg, extraimg, np.min(extraimg), np.max(extraimg), norm_type=cv2.NORM_MINMAX)
            self.original_imExtra = extraimg
            self.imExtra = extraimg
            self.resetBC("Channel 3")
        self.OnChangeBrightnessContrast()


    def OnChangeBrightnessContrast(self):
        if (str(self.comboBoxChannel.currentText()) == "Channel 1"):
            self.channel_BC[0,0]= int(self.horizontalSlider_b.value())
            self.channel_BC[0,1] = int(self.horizontalSlider_c.value())
            iimRef = cv2.add(self.original_imRef,int(self.horizontalSlider_b.value()))
            self.imRef = cv2.multiply(iimRef,(self.horizontalSlider_c.value()*0.1))
        elif (str(self.comboBoxChannel.currentText()) == "Channel 2"):
            self.channel_BC[1, 0] = int(self.horizontalSlider_b.value())
            self.channel_BC[1, 1] = int(self.horizontalSlider_c.value())
            iimTemp = cv2.add(self.original_template, int(self.horizontalSlider_b.value()))
            self.imTemp = cv2.multiply(iimTemp,(self.horizontalSlider_c.value()*0.1))
        elif (str(self.comboBoxChannel.currentText()) == "Channel 3"):
            self.channel_BC[2, 0] = int(self.horizontalSlider_b.value())
            self.channel_BC[2, 1] = int(self.horizontalSlider_c.value())
            if(np.any(self.original_imExtra)):
                iimExtra = cv2.add(self.original_imExtra, int(self.horizontalSlider_b.value()))
                self.imExtra = cv2.multiply(iimExtra,(self.horizontalSlider_c.value()*0.1))
                self.drawImage(self.imRef, self.imTemp, self.centerTemplate, self.centerOrg_Ref, iimExtra)
                return
        self.drawImage(self.imRef, self.imTemp, self.centerTemplate, self.centerOrg_Ref, self.imExtra)
        return

    def OnChangeChannel(self):
        self.horizontalSlider_b.blockSignals(True)
        self.horizontalSlider_c.blockSignals(True)
        if (str(self.comboBoxChannel.currentText()) == "Channel 1"):
            self.horizontalSlider_b.setValue(self.channel_BC[0,0])
            self.horizontalSlider_c.setValue(self.channel_BC[0,1])
        elif (str(self.comboBoxChannel.currentText()) == "Channel 2"):
            self.horizontalSlider_b.setValue(self.channel_BC[1, 0])
            self.horizontalSlider_c.setValue(self.channel_BC[1, 1])
        elif (str(self.comboBoxChannel.currentText()) == "Channel 3"):
            self.horizontalSlider_b.setValue(self.channel_BC[2, 0])
            self.horizontalSlider_c.setValue(self.channel_BC[2, 1])
        self.horizontalSlider_b.blockSignals(False)
        self.horizontalSlider_c.blockSignals(False)
        self.redraw()


    def resetBC(self,channel = None):
        self.channel_BC = np.zeros((3, 2), dtype=np.int)
        if (channel == "Channel 1"):
           self.channel_BC[0, 0] = 0
           self.channel_BC[0, 1] = 50
        elif (channel == "Channel 2"):
            self.channel_BC[1, 0] = 0
            self.channel_BC[1, 1] = 50
        elif (channel == "Channel 3"):
            self.channel_BC[2, 0] = 0
            self.channel_BC[2, 1] = 50
        else:
            self.channel_BC[:,0] = 0
            self.channel_BC[:,1] = 50
        self.OnChangeChannel()