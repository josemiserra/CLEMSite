# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\JMS\Documents\msite\MSite\msiteSEM\UI\GrabFrame.ui'
#
# Created: Fri Apr 08 21:13:24 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import common.dialogs.resources_rc
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

class Ui_DialogGrab(QDialog):

    resolution = 0
    dwelltime = 5
    pixelsize = 800
    lineaverage = 1
    scanrotation = 0
    folderToSave = ""
    imagename = ""
    grab_with_acquire = False;

    def setupUi(self, DialogGrab):
        DialogGrab.setObjectName(_fromUtf8("DialogGrab"))
        DialogGrab.resize(702, 681)
        icon =QIcon()
        icon.addPixmap(QPixmap(_fromUtf8("../common/dialogs/res/msite.png")),QIcon.Normal,QIcon.Off)
        DialogGrab.setWindowIcon(icon)
        self.buttonBox =QDialogButtonBox(DialogGrab)
        self.buttonBox.setGeometry(QtCore.QRect(50, 610, 461, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label_2 =QLabel(DialogGrab)
        self.label_2.setGeometry(QtCore.QRect(330, 50, 151, 27))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.dial_pixelsize =QDial(DialogGrab)
        self.dial_pixelsize.setGeometry(QtCore.QRect(30, 30, 291, 231))
        self.dial_pixelsize.setMinimum(5)
        self.dial_pixelsize.setMaximum(2500)
        self.dial_pixelsize.setPageStep(100)
        self.dial_pixelsize.setProperty("value", 800)
        self.dial_pixelsize.setTracking(True)
        self.dial_pixelsize.setOrientation(QtCore.Qt.Horizontal)
        self.dial_pixelsize.setInvertedAppearance(True)
        self.dial_pixelsize.setInvertedControls(True)
        self.dial_pixelsize.setWrapping(False)
        self.dial_pixelsize.setNotchesVisible(False)
        self.dial_pixelsize.setObjectName(_fromUtf8("dial_pixelsize"))
        self.layoutWidget =QWidget(DialogGrab)
        self.layoutWidget.setGeometry(QtCore.QRect(60, 270, 611, 170))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout_2 =QGridLayout(self.layoutWidget)
        self.gridLayout_2.setContentsMargins(0,0,0,0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalSlider_dwellTime =QSlider(self.layoutWidget)
        self.horizontalSlider_dwellTime.setMaximum(100)
        self.horizontalSlider_dwellTime.setProperty("value", 5)
        self.horizontalSlider_dwellTime.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_dwellTime.setObjectName(_fromUtf8("horizontalSlider_dwellTime"))
        self.gridLayout_2.addWidget(self.horizontalSlider_dwellTime, 2, 3, 1, 1)
        self.spinBox_scanRotation =QDoubleSpinBox(self.layoutWidget)
        self.spinBox_scanRotation.setDecimals(1)
        self.spinBox_scanRotation.setMaximum(360.0)
        self.spinBox_scanRotation.setObjectName(_fromUtf8("spinBox_scanRotation"))
        self.gridLayout_2.addWidget(self.spinBox_scanRotation, 3, 2, 1, 1)
        self.SpinBox_pixelSize =QDoubleSpinBox(self.layoutWidget)
        self.SpinBox_pixelSize.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.SpinBox_pixelSize.setInputMethodHints(QtCore.Qt.ImhFormattedNumbersOnly)
        self.SpinBox_pixelSize.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.SpinBox_pixelSize.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.SpinBox_pixelSize.setMinimum(5.0)
        self.SpinBox_pixelSize.setMaximum(2500.0)
        self.SpinBox_pixelSize.setProperty("value", 800.0)
        self.SpinBox_pixelSize.setObjectName(_fromUtf8("SpinBox_pixelSize"))
        self.gridLayout_2.addWidget(self.SpinBox_pixelSize, 0, 1, 1, 2)
        self.label_3 =QLabel(self.layoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 2)
        self.label_5 =QLabel(self.layoutWidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 3, 0, 1, 2)
        self.label_4 =QLabel(self.layoutWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 2)
        self.SpinBox_LineAverage =QSpinBox(self.layoutWidget)
        self.SpinBox_LineAverage.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.SpinBox_LineAverage.setMaximum(50)
        self.SpinBox_LineAverage.setProperty("value", 3)
        self.SpinBox_LineAverage.setObjectName(_fromUtf8("SpinBox_LineAverage"))
        self.gridLayout_2.addWidget(self.SpinBox_LineAverage, 1, 2, 1, 1)
        self.SpinBox_dwellTime =QDoubleSpinBox(self.layoutWidget)
        self.SpinBox_dwellTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.SpinBox_dwellTime.setProperty("value", 5.0)
        self.SpinBox_dwellTime.setObjectName(_fromUtf8("SpinBox_dwellTime"))
        self.gridLayout_2.addWidget(self.SpinBox_dwellTime, 2, 2, 1, 1)
        self.label =QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalSlider_LAVG =QSlider(self.layoutWidget)
        self.horizontalSlider_LAVG.setMaximum(50)
        self.horizontalSlider_LAVG.setProperty("value", 3)
        self.horizontalSlider_LAVG.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_LAVG.setObjectName(_fromUtf8("horizontalSlider_LAVG"))
        self.gridLayout_2.addWidget(self.horizontalSlider_LAVG, 1, 3, 1, 1)
        spacerItem =QSpacerItem(40, 20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 3, 1, 1)
        spacerItem1 =QSpacerItem(40, 20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 3, 3, 1, 1)
        self.layoutWidget1 =QWidget(DialogGrab)
        self.layoutWidget1.setGeometry(QtCore.QRect(50, 480, 621, 93))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.gridLayout_3 =QGridLayout(self.layoutWidget1)
        self.gridLayout_3.setContentsMargins(0,0,0,0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lineEditFolder_2 =QLineEdit(self.layoutWidget1)
        self.lineEditFolder_2.setObjectName(_fromUtf8("lineEditFolder_2"))
        self.gridLayout_3.addWidget(self.lineEditFolder_2, 0, 1, 1, 1)
        self.label_load =QLabel(self.layoutWidget1)
        self.label_load.setObjectName(_fromUtf8("label_load"))
        self.gridLayout_3.addWidget(self.label_load, 0, 0, 1, 1)
        self.pushButtonFolder =QPushButton(self.layoutWidget1)
        sizePolicy =QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonFolder.sizePolicy().hasHeightForWidth())
        self.pushButtonFolder.setSizePolicy(sizePolicy)
        self.pushButtonFolder.setText(_fromUtf8(""))
        icon1 =QIcon()
        icon1.addPixmap(QPixmap(_fromUtf8(":/res/open.ico")),QIcon.Normal,QIcon.Off)
        self.pushButtonFolder.setIcon(icon1)
        self.pushButtonFolder.setIconSize(QtCore.QSize(24, 24))
        self.pushButtonFolder.setObjectName(_fromUtf8("pushButtonFolder"))
        self.gridLayout_3.addWidget(self.pushButtonFolder, 0, 2, 1, 1)

        self.lineEditImageName =QLineEdit(self.layoutWidget1)
        self.lineEditImageName.setObjectName(_fromUtf8("lineEditImageName"))
        self.gridLayout_3.addWidget(self.lineEditImageName, 0, 1, 2, 1)
        self.label_name =QLabel(self.layoutWidget1)
        self.label_name.setObjectName(_fromUtf8("label_name"))
        self.gridLayout_3.addWidget(self.label_name, 0, 0, 2, 1)


        self.checkBoxAcquire =QCheckBox(DialogGrab)
        self.checkBoxAcquire.setObjectName(_fromUtf8("checkBoxAcquire"))
        self.checkBoxAcquire.setGeometry(QtCore.QRect(50,550, 461, 50))

        self.layoutWidget2 =QWidget(DialogGrab)
        self.layoutWidget2.setGeometry(QtCore.QRect(330, 90, 314, 164))
        self.layoutWidget2.setObjectName(_fromUtf8("layoutWidget2"))
        self.gridLayout =QGridLayout(self.layoutWidget2)
        self.gridLayout.setContentsMargins(0,0,0,0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pushButton_512 =QPushButton(self.layoutWidget2)
        self.pushButton_512.setCheckable(True)
        self.pushButton_512.setObjectName(_fromUtf8("pushButton_512"))
        self.gridLayout.addWidget(self.pushButton_512, 0, 0, 1, 1)
        self.pushButton_2048 =QPushButton(self.layoutWidget2)
        self.pushButton_2048.setCheckable(True)
        self.pushButton_2048.setObjectName(_fromUtf8("pushButton_2048"))
        self.gridLayout.addWidget(self.pushButton_2048, 1, 1, 1, 1)
        self.pushButton_1200 =QPushButton(self.layoutWidget2)
        self.pushButton_1200.setCheckable(True)
        self.pushButton_1200.setObjectName(_fromUtf8("pushButton_1200"))
        self.gridLayout.addWidget(self.pushButton_1200, 1, 0, 1, 1)
        self.pushButton_4096 =QPushButton(self.layoutWidget2)
        self.pushButton_4096.setCheckable(True)
        self.pushButton_4096.setObjectName(_fromUtf8("pushButton_4096"))
        self.gridLayout.addWidget(self.pushButton_4096, 2, 0, 1, 1)
        self.pushButton_1024 =QPushButton(self.layoutWidget2)
        self.pushButton_1024.setCheckable(True)
        self.pushButton_1024.setFlat(False)
        self.pushButton_1024.setObjectName(_fromUtf8("pushButton_1024"))
        self.gridLayout.addWidget(self.pushButton_1024, 0, 1, 1, 1)
       # spacerItem2 =QSpacerItem(40, 20,QSizePolicy.Expanding,QSizePolicy.Minimum)
       # self.gridLayout.addItem(spacerItem2, 2, 1, 1, 1)



        self.retranslateUi(DialogGrab)
        self.buttonBox.accepted.connect(self.pressedOK)
        self.buttonBox.rejected.connect(DialogGrab.reject)
        self.SpinBox_dwellTime.valueChanged[float].connect(self.changeDwellTimeSpin)
        self.SpinBox_pixelSize.valueChanged[float].connect(self.changePixelSizeSpin)
        self.SpinBox_LineAverage.valueChanged[int].connect(self.changeLineAverage)
        self.dial_pixelsize.valueChanged[int].connect(self.changePixelSizeDial)
        self.spinBox_scanRotation.valueChanged[float].connect(self.changeScanRotation)
        self.horizontalSlider_LAVG.valueChanged[int].connect(self.changeLineAverage)
        self.horizontalSlider_dwellTime.valueChanged[int].connect(self.changeDwellTimeSlider)
        self.pushButtonFolder.clicked.connect(self.folderDialog)
        self.pushButton_512.clicked.connect(self.changeResolution512)
        self.pushButton_1024.clicked.connect(self.changeResolution1024)
        self.pushButton_1200.clicked.connect(self.changeResolution1200)
        self.pushButton_2048.clicked.connect(self.changeResolution2048)
        self.pushButton_4096.clicked.connect(self.changeResolution4096)
        self.checkBoxAcquire.stateChanged[int].connect(self.grabNacquire)

        QtCore.QMetaObject.connectSlotsByName(DialogGrab)

    def retranslateUi(self, DialogGrab):
        DialogGrab.setWindowTitle(_translate("DialogGrab", "Grab Frame", None))
        self.label_2.setText(_translate("DialogGrab", "Resolution:", None))
        self.label_3.setText(_translate("DialogGrab", "Line Average:", None))
        self.label_5.setText(_translate("DialogGrab", "Scan Rotation (deg):", None))
        self.label_4.setText(_translate("DialogGrab", "Dwell Time (us):", None))
        self.label.setText(_translate("DialogGrab", "Pixel Size (nm):", None))
        self.label_load.setText(_translate("DialogGrab", "Folder to save :", None))
        self.label_name.setText(_translate("DialogGrab", "Image name :", None))
        self.pushButton_512.setText(_translate("DialogGrab", "512", None))
        self.pushButton_2048.setText(_translate("DialogGrab", "2048", None))
        self.pushButton_1200.setText(_translate("DialogGrab", "1200", None))
        self.pushButton_4096.setText(_translate("DialogGrab", "4096", None))
        self.pushButton_1024.setText(_translate("DialogGrab", "1024", None))
        self.lineEditImageName.setText(_translate("DialogGrab", "grabbed", None))
        self.checkBoxAcquire.setText(_translate("DialogGrab", "Launch DummyCLEM with acquisition.", None))

    def setInitialValues(self,idt,ipxsize,ilavg,ires,iscan,ifolder):
        self.dwelltime = idt
        self.horizontalSlider_dwellTime.setProperty("value", idt)
        self.pixelsize = ipxsize
        self.dial_pixelsize.setProperty("value", ipxsize)
        self.lineaverage = ilavg
        self.SpinBox_LineAverage.setProperty("value", ilavg)
        self.scanrotation = iscan
        self.folderToSave = ifolder
        self.lineEditFolder_2.setText(ifolder)
        self.resolution = ires
        if(ires == 0):
            self.changeResolution512()
        elif(ires ==1):
            self.changeResolution1024()
        elif (ires == 6):
            self.changeResolution1200()
        elif (ires == 2):
            self.changeResolution2048()
        else:
            self.changeResolution4096()

    def changeDwellTimeSlider(self,idwellTime):
        self.dwelltime = (idwellTime)*1.0
        self.SpinBox_dwellTime.setValue(self.dwelltime)
    def changeDwellTimeSpin(self,idwellTime):
        dt = int(idwellTime)
        self.horizontalSlider_dwellTime.setValue(dt)

    def changeLineAverage(self,ilineaverage):
        self.lineaverage = ilineaverage
        self.horizontalSlider_LAVG.setValue(ilineaverage)
        self.SpinBox_LineAverage.setValue(ilineaverage)

    def grabNacquire(self,int):
        if(self.checkBoxAcquire.isChecked()):
            self.grab_with_acquire = True
        else:
            self.grab_with_acquire = False

    def changeResolution512(self):
        self.pushButton_512.setChecked(True)
        self.pushButton_1024.setChecked(False)
        self.pushButton_1200.setChecked(False)
        self.pushButton_2048.setChecked(False)
        self.pushButton_4096.setChecked(False)
        self.resolution = 0



    def changeResolution1024(self):
        self.pushButton_512.setChecked(False)
        self.pushButton_1024.setChecked(True)
        self.pushButton_1200.setChecked(False)
        self.pushButton_2048.setChecked(False)
        self.pushButton_4096.setChecked(False)
        self.resolution = 1



    def changeResolution1200(self):
        self.pushButton_512.setChecked(False)
        self.pushButton_1024.setChecked(False)
        self.pushButton_1200.setChecked(True)
        self.pushButton_2048.setChecked(False)
        self.pushButton_4096.setChecked(False)
        self.resolution = 6


    def changeResolution2048(self):
        self.pushButton_512.setChecked(False)
        self.pushButton_1024.setChecked(False)
        self.pushButton_1200.setChecked(False)
        self.pushButton_2048.setChecked(True)
        self.pushButton_4096.setChecked(False)
        self.resolution = 2



    def changeResolution4096(self):
        self.pushButton_512.setChecked(False)
        self.pushButton_1024.setChecked(False)
        self.pushButton_1200.setChecked(False)
        self.pushButton_2048.setChecked(False)
        self.pushButton_4096.setChecked(True)
        self.resolution = 3

    def changePixelSizeDial(self,ipixelsize):
        self.pixelsize = ipixelsize*1.0
        self.SpinBox_pixelSize.setValue(ipixelsize)

    def changePixelSizeSpin(self,ipixelsize):
        self.pixelsize = ipixelsize
        self.dial_pixelsize.setValue(int(ipixelsize))

    def changeScanRotation(self,iscanrot):
        self.scanrotation = iscanrot

    def pressedOK(self):
        if (self.dwelltime==0.0):
            self.dwelltime = 1.0
        if (self.pixelsize<5):
            self.pixelsize = 3.0
        if (self.lineaverage ==0):
            self.lineaverage = 1
        if (self.folderToSave == ''):
           print ("Please, set up first the frame output directory.")
           return
        self.imagename =str(self.lineEditImageName.text())
        self.accept()


    def folderDialog(self):
        directory =QFileDialog.getExistingDirectory(self, "Directory to save images", QtCore.QDir.currentPath(),
                                                          QFileDialog.ShowDirsOnly)
        directory = str(directory)
        if (not directory):
            print("Directory not found.")
        self.lineEditFolder_2.setText(directory)
        self.folderToSave = directory

    def setPath(self,ipath):
        self.lineEditFolder_2.setText(ipath)
        self.folderToSave = ipath