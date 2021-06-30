# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\JMS\Documents\msite\MSite\msiteSEM\UI\lineDetectorLM_v2.ui'
#
# Created: Wed Sep 07 17:32:29 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtOpenGL import *
import cv2,os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
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

class Ui_DetectionLMDialog(QtWidgets.QDialog):
    xlabels = "0123456789abcdefghij"
    ylabels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    path_files = []
    ##  Orientation code (90 deg counterclockwise)
    ##  -1. None 1. Up 2. Right 3. Down 4. Left
    orientation = "Up"
    angle = 0
    letter = "0A"
    index = 0
    def setupUi(self, DetectionLMDialog):
        DetectionLMDialog.setObjectName(_fromUtf8("DetectionLMDialog"))
        screen = QDesktopWidget().screenGeometry()
        DetectionLMDialog.resize(screen.width() * 965.0 / 2880.0, screen.height() * 1205.0 / 1620.0)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DetectionLMDialog.sizePolicy().hasHeightForWidth())
        DetectionLMDialog.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(11)
        DetectionLMDialog.setFont(font)
        DetectionLMDialog.setModal(True)
        self.gridLayout = QGridLayout(DetectionLMDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.comboBox_select_RL = QComboBox(DetectionLMDialog)
        self.comboBox_select_RL.setObjectName(_fromUtf8("comboBox_select_RL"))
        self.verticalLayout.addWidget(self.comboBox_select_RL)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.labelOrientation = QLabel(DetectionLMDialog)
        self.labelOrientation.setObjectName(_fromUtf8("labelOrientation"))
        self.horizontalLayout_2.addWidget(self.labelOrientation)
        self.spinBox_angle = QDoubleSpinBox(DetectionLMDialog)
        self.spinBox_angle.setMaximum(360.0)
        self.spinBox_angle.setSingleStep(1)
        self.spinBox_angle.setDecimals(1)
        self.spinBox_angle.setObjectName(_fromUtf8("spinBox_angle"))
        self.horizontalLayout_2.addWidget(self.spinBox_angle)
        self.label = QLabel(DetectionLMDialog)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QPixmap(_fromUtf8(":/res/fontRec.png")))
        self.label.setScaledContents(True)
        self.label.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.label.setMaximumWidth(100)
        self.label.setMaximumHeight(100)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_letter = QLabel(DetectionLMDialog)
        self.label_letter.setObjectName(_fromUtf8("label_letter"))
        self.horizontalLayout.addWidget(self.label_letter)
        self.comboBox = QComboBox(DetectionLMDialog)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.horizontalLayout.addWidget(self.comboBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout_2, 1, 0, 1, 1)
        self.buttonBox = QDialogButtonBox(DetectionLMDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.graphicsView = QGraphicsView(DetectionLMDialog)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)

        self.retranslateUi(DetectionLMDialog)
        self.buttonBox.accepted.connect(self.allSelected)
        self.buttonBox.rejected.connect(self.reject)
        self.comboBox.currentIndexChanged[int].connect(self.changeLetter)
        self.spinBox_angle.valueChanged[float].connect(self.rotateImage)
        self.comboBox_select_RL.currentIndexChanged[int].connect(self.replaceFile)

        QtCore.QMetaObject.connectSlotsByName(DetectionLMDialog)

    def retranslateUi(self, DetectionLMDialog):
        i = 0
        for elx in self.xlabels:
            for ely in self.ylabels:
                self.comboBox.addItem(_fromUtf8(""))
                self.comboBox.setItemText(i, _translate("EditGrid", str(elx) + str(ely), None))
                i = i + 1

        DetectionLMDialog.setWindowTitle(_translate("DetectionLMDialog", "Detection", None))
        self.labelOrientation.setText(_translate("DetectionLMDialog", "Rotate until the letter is facing up :", None))
        self.label_letter.setText(_translate("DetectionLMDialog", "Now, please indicate the letter in the center square:", None))

        if (self.path_files):
            self.loadPic(self.path_files[0])
            self.comboBox_select_RL.addItems(self.path_files)
    def setValues(self, listFiles):
        self.path_files = listFiles

    def rotateImage(self, val):
        rotate_val = val - self.angle
        self.angle = val
        self.graphicsView.rotate(rotate_val)
        self.graphicsView.show()

    def loadPic(self, path):
        img = cv2.imread(path, 0)
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(32, 32))
        cl1 = clahe.apply(img)
        cl1 = cv2.blur(cl1, (3, 3))
        cl1 = cv2.equalizeHist(cl1)
        folder, file = os.path.split(path)
        imagename2 = folder + "\\reflected_show_t.jpg"
        cv2.imwrite(imagename2, cl1)
        self.graphicsView.setViewport(QGLWidget())
        scene = QGraphicsScene()
        pxmap = QPixmap(imagename2)

        scene.addPixmap(pxmap)
        pen = QPen(QtCore.Qt.green, 2, QtCore.Qt.SolidLine)
        plus = 0.05 * pxmap.width()
        scene.addLine(int(pxmap.width() / 2), int(pxmap.height() / 2 - plus), int(pxmap.width() / 2),
                      int(pxmap.height() / 2 + plus), pen);
        scene.addLine(int(pxmap.width() / 2 - plus), int(pxmap.height() / 2), int(pxmap.width() / 2 + plus),
                      int(pxmap.height() / 2), pen);
        self.graphicsView.setScene(scene)

        self.graphicsView.show()

    def changeLetter(self, ind):
        self.letter = self.comboBox.currentText();

    def allSelected(self):
        quit_msg = " Your letter is " + self.letter + " and your letter is straight. \n Are these two parameters right?"
        reply = QMessageBox.question(self, "Attention! This step is very important.",
                                           quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.orientation = 360 - self.angle
            self.accept()

    def replaceFile(self):
        self.loadPic(str(self.comboBox_select_RL.currentText()))
        self.index = self.comboBox_select_RL.currentIndex()
import common.dialogs.resources_rc
