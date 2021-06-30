# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\JMS\Documents\msite\MSite\msiteSEM\UI\lineDetectorSEM_v2.ui'
#
# Created: Mon May 16 10:44:43 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from common.microadapterAtlas import *
import datetime
import time
from common.MsiteHelper import MsiteHelper
import os
import glob
import cv2


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding =QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class Ui_DetectionSEMDialog(QDialog):
    xlabels="0123456789abcdefghij"
    ylabels="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ipath = ""
    imagename = ""
    angle = 0.0
    orientation = 0.0
    letter = "0A"
    dwelltime = 1
    folderToSave = ""
    lineaverage = 1
    orientation = 0.0

    def setupUi(self, DetectionSEMDialog):
        DetectionSEMDialog.setObjectName(_fromUtf8("DetectionSEMDialog"))
        screen =QDesktopWidget().screenGeometry()
        px = int(screen.width() * (820.0 / 1920))
        py = int(screen.height() * (920.0 / 1080))
        DetectionSEMDialog.resize(px, py)
        sizePolicy =QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DetectionSEMDialog.sizePolicy().hasHeightForWidth())
        DetectionSEMDialog.setSizePolicy(sizePolicy)
        font =QFont()
        font.setPointSize(11)
        DetectionSEMDialog.setFont(font)
        DetectionSEMDialog.setModal(True)
        self.graphicsView =QGraphicsView(DetectionSEMDialog)
        px = int(screen.width() * (10.0 / 1920))
        py = int(screen.height() * (10.0 / 1080))
        pxe = int(screen.width() * (800.0 / 1920))
        pye = int(screen.height() * (600.0 / 1080))
        self.graphicsView.setGeometry(QtCore.QRect(px, py, pxe, pye))
        sizePolicy =QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.label =QLabel(DetectionSEMDialog)
        px = int(screen.width() * (720.0 / 1920))
        py = int(screen.height() * (630.0 / 1080))
        pxe = int(screen.width() * (80.0 / 1920))
        pye = int(screen.height() * (80.0 / 1080))
        self.label.setGeometry(QtCore.QRect(px, py, pxe, pye))
        sizePolicy =QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QPixmap(_fromUtf8("./common/dialogs/res/fontRec.png")))
        self.label.setScaledContents(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.buttonBox =QDialogButtonBox(DetectionSEMDialog)
        px = int(screen.width() * (500.0 / 1920))
        py = int(screen.height() * (850.0 / 1080))
        pxe = int(screen.width() * (312.0 / 1920))
        pye = int(screen.height() * (49.0 / 1080))
        self.buttonBox.setGeometry(QtCore.QRect(px, py, pxe, pye))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.widget =QWidget(DetectionSEMDialog)
        px = int(screen.width() * (20.0 / 1920))
        py = int(screen.height() * (700.0 / 1080))
        pxe = int(screen.width() * (670.0 / 1920))
        pye = int(screen.height() * (155.0 / 1080))
        self.widget.setGeometry(QtCore.QRect(px, py, pxe, pye))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 =QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0,0,0,0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_3 =QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.labelGrab =QLabel(self.widget)
        self.labelGrab.setObjectName(_fromUtf8("labelGrab"))
        self.horizontalLayout_3.addWidget(self.labelGrab)
        self.pushButtonGrab =QPushButton(self.widget)
        self.pushButtonGrab.setText(_fromUtf8(""))
        icon =QIcon()
        icon.addPixmap(QPixmap(_fromUtf8("./common/dialogs/res/grab.png")),QIcon.Normal,QIcon.Off)
        self.pushButtonGrab.setIcon(icon)
        self.pushButtonGrab.setIconSize(QtCore.QSize(32, 32))
        self.pushButtonGrab.setCheckable(False)
        self.pushButtonGrab.setObjectName(_fromUtf8("pushButtonGrab"))
        self.horizontalLayout_3.addWidget(self.pushButtonGrab)
        self.gridLayout_2 =QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 =QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 2)
        self.SpinBox_dwellTime =QDoubleSpinBox(self.widget)
        self.SpinBox_dwellTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.SpinBox_dwellTime.setProperty("value", 12.0)
        self.SpinBox_dwellTime.setObjectName(_fromUtf8("SpinBox_dwellTime"))
        self.gridLayout_2.addWidget(self.SpinBox_dwellTime, 2, 2, 1, 1)
        self.horizontalSlider_dwellTime =QSlider(self.widget)
        self.horizontalSlider_dwellTime.setMaximum(100)
        self.horizontalSlider_dwellTime.setProperty("value", 12)
        self.horizontalSlider_dwellTime.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_dwellTime.setObjectName(_fromUtf8("horizontalSlider_dwellTime"))
        self.gridLayout_2.addWidget(self.horizontalSlider_dwellTime, 2, 3, 1, 1)
        self.label_4 =QLabel(self.widget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 2)
        self.horizontalSlider_LAVG =QSlider(self.widget)
        self.horizontalSlider_LAVG.setMaximum(50)
        self.horizontalSlider_LAVG.setProperty("value", 1)
        self.horizontalSlider_LAVG.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_LAVG.setObjectName(_fromUtf8("horizontalSlider_LAVG"))
        self.gridLayout_2.addWidget(self.horizontalSlider_LAVG, 0, 3, 1, 1)
        self.SpinBox_LineAverage =QSpinBox(self.widget)
        self.SpinBox_LineAverage.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.SpinBox_LineAverage.setMaximum(50)
        self.SpinBox_LineAverage.setProperty("value", 1)
        self.SpinBox_LineAverage.setObjectName(_fromUtf8("SpinBox_LineAverage"))
        self.gridLayout_2.addWidget(self.SpinBox_LineAverage, 0, 2, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout_2)
        spacerItem =QSpacerItem(20, 50,QSizePolicy.Minimum,QSizePolicy.Fixed)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.gridLayout_3 =QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.toolButton =QToolButton(self.widget)
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.gridLayout_3.addWidget(self.toolButton, 1, 2, 1, 1)
        self.lineEditFolder_2 =QLineEdit(self.widget)
        self.lineEditFolder_2.setObjectName(_fromUtf8("lineEditFolder_2"))
        self.gridLayout_3.addWidget(self.lineEditFolder_2, 1, 1, 1, 1)
        self.label_load =QLabel(self.widget)
        self.label_load.setObjectName(_fromUtf8("label_load"))
        self.gridLayout_3.addWidget(self.label_load, 1, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_3)
        self.widget1 =QWidget(DetectionSEMDialog)
        px = int(screen.width() * (20.0 / 1920))
        py = int(screen.height() * (620.0 / 1080))
        pxe = int(screen.width() * (670.0 / 1920))
        pye = int(screen.height() * (96.0 / 1080))
        self.widget1.setGeometry(QtCore.QRect(px, py, pxe, pye))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.gridLayout =QGridLayout(self.widget1)
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_letter =QLabel(self.widget1)
        self.label_letter.setObjectName(_fromUtf8("label_letter"))
        self.gridLayout.addWidget(self.label_letter, 0, 0, 1, 1)
        self.comboBox =QComboBox(self.widget1)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.label_letter_2 =QLabel(self.widget1)
        self.label_letter_2.setObjectName(_fromUtf8("label_letter_2"))
        self.gridLayout.addWidget(self.label_letter_2, 1, 0, 1, 1)
        self.spinBox_angle =QSpinBox(self.widget1)
        self.spinBox_angle.setMaximum(360)
        self.spinBox_angle.setObjectName(_fromUtf8("spinBox_angle"))
        self.gridLayout.addWidget(self.spinBox_angle, 1, 1, 1, 1)

        self.retranslateUi(DetectionSEMDialog)

        self.buttonBox.accepted.connect(self.allSelected)
        self.buttonBox.rejected.connect(self.reject)
        self.comboBox.currentIndexChanged[int].connect(self.changeLetter)
        self.SpinBox_LineAverage.valueChanged[int].connect(self.changeLineAverage)
        self.SpinBox_dwellTime.valueChanged[float].connect(self.changeDwellTimeSpin)
        self.horizontalSlider_LAVG.valueChanged[int].connect(self.changeLineAverage)
        self.horizontalSlider_dwellTime.valueChanged[int].connect(self.changeDwellTimeSlider)
        self.spinBox_angle.valueChanged[int].connect(self.rotateImage)
        self.toolButton.clicked.connect(self.folderDialog)
        self.pushButtonGrab.clicked.connect(self.loadPic)
        QtCore.QMetaObject.connectSlotsByName(DetectionSEMDialog)

    def retranslateUi(self, DetectionSEMDialog):
        i = 0
        for elx in self.xlabels:
            for ely in self.ylabels:
                self.comboBox.addItem(_fromUtf8(""))
                self.comboBox.setItemText(i, _translate("EditGrid", str(elx) + str(ely), None))
                i = i + 1


        self.graphicsView.setViewport(QGLWidget())
        scene =QGraphicsScene()
        # head,_ = os.path.split(os.getcwd())
        pxmap =QPixmap('.\\common\\dialogs\\res\\black_800_600.bmp')
        scene.addPixmap(pxmap)
        pen =QPen(QtCore.Qt.green, 2, QtCore.Qt.SolidLine)
        plus = 0.05*pxmap.width()
        scene.addLine( int(pxmap.width()/2),int(pxmap.height()/2-plus), int(pxmap.width()/2), int(pxmap.height()/2+plus),pen);
        scene.addLine( int(pxmap.width()/2-plus),int(pxmap.height()/2), int(pxmap.width()/2+plus), int(pxmap.height()/2),pen);
        self.graphicsView.setScene(scene)
        self.graphicsView.show()
        DetectionSEMDialog.setWindowTitle(_translate("DetectionSEMDialog", "Detection", None))
        self.labelGrab.setText(_translate("DetectionSEMDialog", "GRAB : ", None))
        self.label_3.setText(_translate("DetectionSEMDialog", "Line Average:", None))
        self.label_4.setText(_translate("DetectionSEMDialog", "Dwell Time (us):", None))
        self.toolButton.setText(_translate("DetectionSEMDialog", "...", None))
        self.label_load.setText(_translate("DetectionSEMDialog", "Folder to save :", None))
        self.label_letter.setText(_translate("DetectionSEMDialog", "Please indicate the pattern in the center square (1st small- 2nd big):", None))
        self.label_letter_2.setText(_translate("DetectionSEMDialog", "Now rotate the pattern until you see it straight:", None))
        self.lineEditFolder_2.setText(self.folderToSave)


    def changeDwellTimeSlider(self, idwellTime):
        self.dwelltime = (idwellTime) * 1.0
        self.SpinBox_dwellTime.setValue(self.dwelltime)

    def changeDwellTimeSpin(self, idwellTime):
        dt = int(idwellTime)
        self.horizontalSlider_dwellTime.setValue(dt)

    def changeLineAverage(self, ilineaverage):
        self.lineaverage = ilineaverage
        self.horizontalSlider_LAVG.setValue(ilineaverage)
        self.SpinBox_LineAverage.setValue(ilineaverage)

    def folderDialog(self):
        directory =QFileDialog.getExistingDirectory(self, "Directory to save images",
                                                               QtCore.QDir.currentPath(),
                                                              QFileDialog.ShowDirsOnly)
        directory = str(directory)
        if (not directory):
            print("Directory not found.")
            return
        self.lineEditFolder_2.setText(directory)
        self.folderToSave = directory
        # Check if already NAV images exist
        res = MsiteHelper.getFile(directory,'nav')
        ret = QMessageBox.critical(self, "Previous detected.",
                                   'Would you like to reload your image?',
                                   QMessageBox.Yes, QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.addImage(res)

        return


    def setValues(self, inpath, outpath, server):
        """ inpath = path where the images are stored.
        """
        self.server = server
        inpath = inpath.replace('\\\\', '\\')
        outpath = outpath.replace('\\\\', '\\')
        self.ipath = str(inpath)
        self.folderToSave = str(outpath)
        self.lineEditFolder_2.setText(self.folderToSave)

    def loadPic(self):
        """
            Check parameters are right
        """
        if (self.dwelltime==0.0):
            self.dwelltime = 1.0
        if (self.lineaverage ==0):
            self.lineaverage = 1
        if (self.folderToSave == ''):
           print ("Please, set up first the frame output directory.")
           return


        ## 1. Connect to the microscope and grab the image
        self.dwelltime = self.SpinBox_dwellTime.value()
        self.lineaverage = self.SpinBox_LineAverage.value()

        #  ts = time.time()
        #  st = datetime.datetime.fromtimestamp(ts).strftime('%d_%m_%Y_%H_%M_%S')
        files = glob.glob(self.folderToSave + '\*.tif')
        # Remove previous file in case of regrab
        for f in files:
            if ('nav_' in f):
                head, tail = os.path.split(f)
                os.rename(f, self.folderToSave + '\pre' + tail[4:])

        error, imagename = self.server.grabImage(self.dwelltime, 1.2, 1, self.lineaverage, 0, self.folderToSave, "nav_", shared=True)
        if (error):
            raise ValueError("Unknown error grabbing frame.")

        print("Frame grabbed:" + imagename)
        self.addImage(imagename)



    def addImage(self,imagename):
        from common.image_an.image_utils import gaussfilt
        self.imagename = imagename
        img = cv2.imread(imagename,0)
        img = gaussfilt(img, 1.5)
        #img = cv2.equalizeHist(img)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img = clahe.apply(np.uint8(img))
        dir,_ = os.path.split(imagename)
        imagename2 = os.path.join(dir,"show_t.tif")
        if os.path.isfile(imagename2):
            os.remove(imagename2)
        cv2.imwrite(imagename2,img)
        scene =QGraphicsScene()
        pxmap =QPixmap(imagename2)
        scene.addPixmap(pxmap)

        pen =QPen(QtCore.Qt.green, 2, QtCore.Qt.SolidLine)
        plus = 0.05 * pxmap.width()
        scene.addLine(int(pxmap.width() / 2), int(pxmap.height() / 2 - plus), int(pxmap.width() / 2),
                      int(pxmap.height() / 2 + plus), pen)
        scene.addLine(int(pxmap.width() / 2 - plus), int(pxmap.height() / 2), int(pxmap.width() / 2 + plus),
                      int(pxmap.height() / 2), pen)
        self.graphicsView.setScene(scene)
        self.graphicsView.update()
        self.graphicsView.show()


    def rotateImage(self, val):
            rotate_val = val - self.angle
            self.angle = val
            self.graphicsView.rotate(rotate_val)
            self.graphicsView.show()

    def changeLetter(self, ind):
        self.letter = self.comboBox.currentText();

    def allSelected(self):
        quit_msg = " Your letter is " + self.letter + " and your letter is straight. \n Are these two parameters right?"
        reply =QMessageBox.question(self, "Attention! This step is very important.",
                                           quit_msg,QMessageBox.Yes,QMessageBox.No)

        if reply ==QMessageBox.Yes:
            self.letter = str(self.letter)
            self.orientation = 360 - self.angle
            self.accept()

import common.dialogs.resources_rc
