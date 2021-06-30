# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\JMS\Documents\msite\MSite\msiteSEM\UI\register.ui'
#
# Created: Mon Sep 19 20:46:22 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!


# TODO
# Fix B&C unbalance when move slider (recover after switching of channels)
# Adjust if images with differences sizes are selected
# First picture passed is not the one being shown
# Zoom in doesn't work
#########
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os,sys
import cv2
import numpy as np

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

class Ui_VisorWindow(QtWidgets.QDialog):
    shift = []
    m_equalize = []
    _zoom = 0
    factor = 1
    pixelsize_ref = 0

    def __init__(self, imageRefPath, imRefList):
        path, header = os.path.split(imageRefPath)
        self.path = path
        self.tag = header
        self.currentImagePath = ""
        self.imageRefPath = imageRefPath
        self.imReflist = imRefList
        self.imRef = cv2.imread(imageRefPath, 0)
        self.imTemp = cv2.imread(imageRefPath, 0)
        self.imExtra = cv2.imread(imageRefPath, 0)
        self.channel_BC = np.zeros((3,2),dtype = np.int)
        self.channel_BC[:,1] = 10

        super(Ui_VisorWindow, self).__init__()
        self.setupUi(self)

        self.setupForm()
        self.drawImage(self.imRef,self.imTemp,self.imExtra)
        self.fitInView()
        sind = 0

        for ind, el in enumerate(self.imReflist):
            _,hel = os.path.split(el)
            if(hel==header):
                sind = ind
        self.comboBox_image_1.setCurrentIndex(sind)
        self.comboBox_image_2.setCurrentIndex(sind)
        self.comboBox_image_3.setCurrentIndex(sind)
        self.repaint()

    def setupUi(self, VisorWindow):
        VisorWindow.setObjectName(_fromUtf8("VisorWindow"))
        VisorWindow.resize(1218, 1265)
        screen = QDesktopWidget().screenGeometry()
        VisorWindow.resize(screen.width() * 1200.0 / 2880.0, screen.height() * 1250.0 / 1620.0)
        VisorWindow.setWindowFlags(VisorWindow.windowFlags() | QtCore.Qt.WindowMinMaxButtonsHint)

        self.gridLayout_2 = QGridLayout(VisorWindow)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.pushButton = QPushButton(VisorWindow)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout_2.addWidget(self.pushButton, 4, 0, 1, 1)
        self.label_4 = QLabel(VisorWindow)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 1, 1, 1)
        self.label_5 = QLabel(VisorWindow)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 2, 1, 1, 1)
        self.horizontalSlider_c = QSlider(VisorWindow)
        self.horizontalSlider_c.setMaximum(100)
        self.horizontalSlider_c.setMinimum(0)
        self.horizontalSlider_c.setSingleStep(10)
        self.horizontalSlider_c.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_c.setObjectName(_fromUtf8("horizontalSlider_c"))
        self.gridLayout_2.addWidget(self.horizontalSlider_c, 2, 2, 1, 1)
        self.formLayout = QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QLabel(VisorWindow)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)
        self.doubleSpinBoxX = QDoubleSpinBox(VisorWindow)
        self.doubleSpinBoxX.setMaximum(360.0)
        self.doubleSpinBoxX.setSingleStep(0.5)
        self.doubleSpinBoxX.setObjectName(_fromUtf8("doubleSpinBoxX"))
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.doubleSpinBoxX)
        self.pushButton_flipH = QPushButton(VisorWindow)
        self.pushButton_flipH.setObjectName(_fromUtf8("pushButton_flipH"))
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.pushButton_flipH)
        self.pushButton_flipV = QPushButton(VisorWindow)
        self.pushButton_flipV.setObjectName(_fromUtf8("pushButton_flipV"))
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.pushButton_flipV)
        self.gridLayout_2.addLayout(self.formLayout, 1, 0, 2, 1)
        self.horizontalSlider_b = QSlider(VisorWindow)
        self.horizontalSlider_b.setMaximum(50)
        self.horizontalSlider_b.setMinimum(-50)
        self.horizontalSlider_b.setSingleStep(10)
        self.horizontalSlider_b.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_b.setInvertedAppearance(False)
        self.horizontalSlider_b.setInvertedControls(False)
        self.horizontalSlider_b.setObjectName(_fromUtf8("horizontalSlider_b"))
        self.gridLayout_2.addWidget(self.horizontalSlider_b, 1, 2, 1, 1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 1, 1, 2)
        self.graphicsView = QGraphicsView(VisorWindow)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout_2.addWidget(self.graphicsView, 0, 0, 1, 3)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.checkBox_c1 = QCheckBox(VisorWindow)
        self.checkBox_c1.setText(_fromUtf8(""))
        self.checkBox_c1.setObjectName(_fromUtf8("checkBox_c1"))
        self.horizontalLayout_5.addWidget(self.checkBox_c1)
        self.checkBox_c1_gray = QCheckBox(VisorWindow)
        self.checkBox_c1_gray.setText(_fromUtf8(""))
        self.checkBox_c1_gray.setObjectName(_fromUtf8("checkBox_c1_gray"))

        self.horizontalLayout_5.addWidget(self.checkBox_c1_gray)
        self.label_12 = QLabel(VisorWindow)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_5.addWidget(self.label_12)
        self.comboBox_image_1 = QComboBox(VisorWindow)
        self.comboBox_image_1.setObjectName(_fromUtf8("comboBox_image_1"))
        self.horizontalLayout_5.addWidget(self.comboBox_image_1)

        self.checkBox_equalize_1 = QCheckBox(VisorWindow)
        self.checkBox_equalize_1.setObjectName(_fromUtf8("checkBox_equalize_1"))
        self.horizontalLayout_5.addWidget(self.checkBox_equalize_1)
        self.gridLayout.addLayout(self.horizontalLayout_5, 0, 0, 1, 1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.checkBox_c2 = QCheckBox(VisorWindow)
        self.checkBox_c2.setText(_fromUtf8(""))
        self.checkBox_c2.setObjectName(_fromUtf8("checkBox_c2"))
        self.horizontalLayout_3.addWidget(self.checkBox_c2)
        self.checkBox_c2_gray = QCheckBox(VisorWindow)
        self.checkBox_c2_gray.setText(_fromUtf8(""))
        self.checkBox_c2_gray.setObjectName(_fromUtf8("checkBox_c2_gray"))
        self.horizontalLayout_3.addWidget(self.checkBox_c2_gray)
        self.label_6 = QLabel(VisorWindow)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_3.addWidget(self.label_6)
        self.comboBox_image_2 = QComboBox(VisorWindow)
        self.comboBox_image_2.setObjectName(_fromUtf8("comboBox_image_2"))
        self.horizontalLayout_3.addWidget(self.comboBox_image_2)
        self.checkBox_equalize_2 = QCheckBox(VisorWindow)
        self.checkBox_equalize_2.setObjectName(_fromUtf8("checkBox_equalize_2"))
        self.horizontalLayout_3.addWidget(self.checkBox_equalize_2)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.checkBox_c3 = QCheckBox(VisorWindow)
        self.checkBox_c3.setText(_fromUtf8(""))
        self.checkBox_c3.setObjectName(_fromUtf8("checkBox_c3"))
        self.horizontalLayout_4.addWidget(self.checkBox_c3)
        self.checkBox_c3_gray = QCheckBox(VisorWindow)
        self.checkBox_c3_gray.setText(_fromUtf8(""))
        self.checkBox_c3_gray.setObjectName(_fromUtf8("checkBox_c3_gray"))
        self.horizontalLayout_4.addWidget(self.checkBox_c3_gray)
        self.label_7 = QLabel(VisorWindow)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_4.addWidget(self.label_7)
        self.comboBox_image_3 = QComboBox(VisorWindow)
        self.comboBox_image_3.setObjectName(_fromUtf8("comboBox_image_3"))
        self.horizontalLayout_4.addWidget(self.comboBox_image_3)
        self.checkBox_equalize_3 = QCheckBox(VisorWindow)
        self.checkBox_equalize_3.setObjectName(_fromUtf8("checkBox_equalize_3"))
        self.horizontalLayout_4.addWidget(self.checkBox_equalize_3)
        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 3, 0, 1, 3)

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


        self.retranslateUi(VisorWindow)

        self.checkBox_c1.stateChanged[int].connect(self.redraw)
        self.checkBox_c2.stateChanged[int].connect(self.redraw)
        self.checkBox_c3.stateChanged[int].connect(self.redraw)

        self.checkBox_c1_gray.stateChanged[int].connect(self.redraw)
        self.checkBox_c2_gray.stateChanged[int].connect(self.redraw)
        self.checkBox_c3_gray.stateChanged[int].connect(self.redraw)

        self.checkBox_equalize_1.stateChanged[int].connect(self.redraw)
        self.checkBox_equalize_2.stateChanged[int].connect(self.redraw)
        self.checkBox_equalize_3.stateChanged[int].connect(self.redraw)

        self.horizontalSlider_b.valueChanged[int].connect(self.OnChangeBrightnessContrast)
        self.horizontalSlider_c.valueChanged[int].connect(self.OnChangeBrightnessContrast)
        self.doubleSpinBoxX.valueChanged[float].connect(self.OnChangeRotation)

        self.pushButton.clicked.connect(self.savePic)
        self.pushButton_flipH.clicked.connect(self.OnFlipH)

        self.pushButton_flipV.clicked.connect(self.OnFlipV)

        self.comboBox_image_1.currentIndexChanged.connect(self.OnChange_image1)
        self.comboBox_image_2.currentIndexChanged.connect(self.OnChange_image2)
        self.comboBox_image_3.currentIndexChanged.connect(self.OnChange_image3)

        QtCore.QMetaObject.connectSlotsByName(VisorWindow)



    def retranslateUi(self, VisorWindow):
        VisorWindow.setWindowTitle(_translate("VisorWindow", "VisorWindow", None))
        self.pushButton.setText(_translate("VisorWindow", "Save", None))
        self.label_4.setText(_translate("VisorWindow", "Brightness:", None))
        self.label_5.setText(_translate("VisorWindow", "Contrast:", None))
        self.label.setText(_translate("VisorWindow", "Rotate:", None))
        self.pushButton_flipH.setText(_translate("VisorWindow", "Flip H", None))
        self.pushButton_flipV.setText(_translate("VisorWindow", "Flip V", None))
        self.label_12.setText(_translate("VisorWindow", "Channel 1:", None))
        self.checkBox_equalize_1.setText(_translate("VisorWindow", "Equalize", None))
        self.label_6.setText(_translate("VisorWindow", "Channel 2:", None))
        self.checkBox_equalize_2.setText(_translate("VisorWindow", "Equalize", None))
        self.label_7.setText(_translate("VisorWindow", "Channel 3:", None))
        self.checkBox_equalize_3.setText(_translate("VisorWindow", "Equalize", None))
        self.checkBox_c1.setChecked(True)
        self.checkBox_c2.setChecked(True)
        self.checkBox_c3.setChecked(True)
        self.horizontalSlider_c.setValue(10)
        sind = 0
        for ind in range(len(self.imReflist)):
            self.comboBox_image_1.addItem(_fromUtf8(""))
            self.comboBox_image_1.setItemText(ind, self.imReflist[ind])
            self.comboBox_image_2.addItem(_fromUtf8(""))
            self.comboBox_image_2.setItemText(ind, self.imReflist[ind])
            self.comboBox_image_3.addItem(_fromUtf8(""))
            self.comboBox_image_3.setItemText(ind, self.imReflist[ind])


    def closeEvent(self, event):
        # do stuff
        if(self.currentImagePath!=""):
            os.remove(self.currentImagePath)
        event.accept()  # let the window close

    def drawImage(self,im1,im2=None,im3=None):


        overlay = np.zeros(shape=im1.shape + (3,), dtype=np.uint8)
        imRef = im1
        if (self.checkBox_equalize_1.isChecked()):
            imRef = cv2.equalizeHist(imRef)
        if(self.checkBox_c1.isChecked()):
            overlay[..., 0] = imRef

        if(np.any(im2)):
            imageTemp = im2
            if (self.checkBox_equalize_2.isChecked()):
                imageTemp = cv2.equalizeHist(imageTemp)

            if(self.checkBox_c2.isChecked()):
                overlay[..., 1] = imageTemp

        if(np.any(im3)):
            imageExtra = im3
            if (self.checkBox_equalize_3.isChecked()):
                imageExtra = cv2.equalizeHist(imageExtra)

            if (self.checkBox_c3.isChecked()):
                overlay[..., 2] = imageExtra


        if (self.checkBox_c1_gray.isChecked()):
            overlay[..., 0] += imRef
            overlay[..., 1] += imRef
            overlay[..., 2] += imRef
        if (self.checkBox_c3_gray.isChecked()):
            overlay[..., 0] += imageExtra
            overlay[..., 1] += imageExtra
            overlay[..., 2] += imageExtra
        if (self.checkBox_c3_gray.isChecked()):
            overlay[..., 0] += imageTemp
            overlay[..., 1] += imageTemp
            overlay[..., 2] += imageTemp

        self.currentImagePath = self.path + "\\tmp.jpg"
        cv2.imwrite(self.currentImagePath, overlay)
        self.setPhoto(QPixmap(self.currentImagePath))
        if (self.factor > 0):
            self.graphicsView.scale(self.factor, self.factor)
        self.currentimage = overlay

    def OnChangeBrightnessContrast(self):
        self.updateBC()

    def updateBC(self):
        self.channel_BC[0,0]= int(self.horizontalSlider_b.value())
        self.channel_BC[0,1] = int(self.horizontalSlider_c.value())
        iimRef = cv2.add(self.imRef,int(self.horizontalSlider_b.value()))
        iimRef = cv2.multiply(iimRef,(self.horizontalSlider_c.value()/10.0))

        self.channel_BC[1, 0] = int(self.horizontalSlider_b.value())
        self.channel_BC[1, 1] = int(self.horizontalSlider_c.value())
        iimTemp = cv2.add(self.imTemp, int(self.horizontalSlider_b.value()))
        iimTemp = cv2.multiply(iimTemp,(self.horizontalSlider_c.value()/10.0))


        self.channel_BC[2, 0] = int(self.horizontalSlider_b.value())
        self.channel_BC[2, 1] = int(self.horizontalSlider_c.value())
        iimExtra = cv2.add(self.imExtra, int(self.horizontalSlider_b.value()))
        iimExtra = cv2.multiply(iimExtra,(self.horizontalSlider_c.value()/10.0))
        self.drawImage(iimRef, iimTemp, iimExtra)
        return

    def savePic(self,):
        fname = QFileDialog.getSaveFileName(self, "Save picture",self.path+"\\image.tif", ".*",
                                                       "Picture Files (*.tif,*.jpg)")
        cv2.imwrite(str(fname), self.currentimage)

    def OnChangeChannelBC(self):
        if (self.checkBox_c1.isChecked()):
            self.horizontalSlider_b.setValue(self.channel_BC[0, 0])
            self.horizontalSlider_c.setValue(self.channel_BC[0, 1])
        elif (self.checkBox_c2.isChecked()):
            self.horizontalSlider_b.setValue(self.channel_BC[1, 0])
            self.horizontalSlider_c.setValue(self.channel_BC[1, 1])
        elif (self.checkBox_c3.isChecked()):
            self.horizontalSlider_b.setValue(self.channel_BC[2, 0])
            self.horizontalSlider_c.setValue(self.channel_BC[2, 1])

    def resetBC(self, channel):
        if (self.checkBox_c1.isChecked()):
            self.channel_BC[0, 0] = 0
            self.channel_BC[0, 1] = 10
        elif (self.checkBox_c2.isChecked()):
            self.channel_BC[1, 0] = 0
            self.channel_BC[1, 1] = 10
        elif (self.checkBox_c3.isChecked()):
            self.channel_BC[2, 0] = 0
            self.channel_BC[2, 1] = 10
        self.OnChangeChannelBC()


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

    def setupForm(self):
        self.setWindowTitle(self.tag)

    def setPhoto(self, pixmap=None):

        if pixmap and not pixmap.isNull():
            self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self.graphicsView.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())

    def fitInView(self):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            unity = self.graphicsView.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.graphicsView.scale(1 / unity.width(), 1 / unity.height())
            # viewrect = self.graphicsView.viewport().rect()
            # scenerect = self.graphicsView.transform().mapRect(rect)
            # factor = min(viewrect.width() / scenerect.width(),
            #             viewrect.height() / scenerect.height())
            # self.graphicsView.scale(factor, factor)
            self.graphicsView.centerOn(rect.center())
            self._zoom = 0

    def redraw(self):
        self.updateBC()

    def OnChangeRotation(self):
        self.graphicsView.resetTransform()
        self.graphicsView.rotate(float(self.doubleSpinBoxX.value()))

    def OnFlipV(self):
        self.imRef = cv2.flip(self.imRef, 0)
        self.imTemp = cv2.flip(self.imTemp, 0)
        self.imExtra = cv2.flip(self.imExtra, 0)
        self.updateBC()

    def OnFlipH(self):
        self.imRef = cv2.flip(self.imRef, 1)
        self.imTemp = cv2.flip(self.imTemp, 1)
        self.imExtra = cv2.flip(self.imExtra, 1)
        self.updateBC()


    def OnChange_image1(self):
        self.graphicsView.resetTransform()
        self.imRef = cv2.imread(str(self.comboBox_image_1.currentText()),0)
        self.updateBC()
    def OnChange_image2(self):
        self.graphicsView.resetTransform()
        self.imTemp = cv2.imread(str(self.comboBox_image_2.currentText()),0)
        self.updateBC()
    def OnChange_image3(self):
        self.graphicsView.resetTransform()
        self.imExtra = cv2.imread(str(self.comboBox_image_3.currentText()),0)
        self.updateBC()