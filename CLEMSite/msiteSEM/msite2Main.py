# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\QtDesigns\UI\msite2Main.ui'
#
# Created: Wed Feb 18 21:02:47 2015
#      by: PyQt5 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import  *
import shutil
import sys, os
from msiteSEM.msite2LM_app import MSite2SEM_p1_app
from msiteSEM.msite2SEM_app  import MSite2SEM_app
from msite4A.msite4Acq_app import MSite4Acq_app
from common.MsiteHelper import getPreferencesFile
from common.notepad import TextEdit

sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

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

from keras import backend as K
import os
from importlib import reload

def set_keras_backend(backend):
    if K.backend() != backend:
        os.environ['KERAS_BACKEND'] = backend
        reload(K)
        assert K.backend() == backend

class Ui_MainWindow(object):

    preferences_file = getPreferencesFile()
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        resolution = QDesktopWidget().screenGeometry()
        MainWindow.resize(int(resolution.width()*(310.0/1920.0)), int(resolution.height()*(270.0/1080.0)))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/msite2.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(int(resolution.width()*(50.0/1920.0)), int(resolution.height()*(50.0/1080.0)), int(resolution.width()*(211.0/1920.0)), int(resolution.height()*(151.0/1080.0))))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0,0,0,0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.toLM = QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.toLM.setFont(font)
        self.toLM.setObjectName(_fromUtf8("toLM"))
        self.verticalLayout.addWidget(self.toLM)
        self.toFIBSEM = QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.toFIBSEM.setFont(font)
        self.toFIBSEM.setObjectName(_fromUtf8("toFIBSEM"))
        self.verticalLayout.addWidget(self.toFIBSEM)
        self.toFIBSEMAcq = QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.toFIBSEMAcq.setFont(font)
        self.toFIBSEMAcq.setObjectName(_fromUtf8("toFIBSEM"))
        self.verticalLayout.addWidget(self.toFIBSEMAcq)


        self.changeOptions = QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.changeOptions.setFont(font)
        self.changeOptions.setObjectName(_fromUtf8("changeOptions"))
        self.verticalLayout.addWidget(self.changeOptions)

        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(int(resolution.width()*(50.0/1920.0)), int(resolution.height()*(20.0/1080.0)), int(resolution.width()*(220.0/1920.0)), 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(int(resolution.width()*(10.0/1920.0)), int(resolution.height()*(200.0/1080.0)), 101, 41))
        self.label_2.setText(_fromUtf8(""))
        self.label_2.setPixmap(QtGui.QPixmap(_fromUtf8(":/res/embl_logo2.png")))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 288, 21))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuOptions = QMenu(self.menuBar)
        self.menuOptions.setObjectName(_fromUtf8("menuOptions"))
        MainWindow.setMenuBar(self.menuBar)
        self.retranslateUi(MainWindow)

        self.toLM.clicked.connect(self.openLM)
        self.toFIBSEM.clicked.connect(self.openFIBSEM)
        self.toFIBSEMAcq.clicked.connect(self.openFIBSEMAcq)
        self.changeOptions.clicked.connect(self.changeOptionsDialog)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        set_keras_backend('tensorflow')
        self.maintextEditor = TextEdit(self)

    def openFIBSEM(self):
        self.uiSEM = MSite2SEM_app()
        self.uiSEM.setWindowModality(QtCore.Qt.NonModal)
        self.uiSEM.show()
        self.close()
        pass


    def openFIBSEMAcq(self):
        self.uiFSEM = MSite4Acq_app()
        self.uiFSEM.setWindowModality(QtCore.Qt.NonModal)
        self.uiFSEM.show()
        self.close()


    def openLM(self):
        self.uiLM =  MSite2SEM_p1_app(ipreferences=self.preferences_file)
        self.uiLM.setWindowModality(QtCore.Qt.NonModal)
        self.uiLM.show()
        self.close()

    def changeOptionsDialog(self):
        self.maintextEditor.openFile("preferences\\user.pref")
        self.maintextEditor.show()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "CLEMSite", None))
        self.toLM.setText(_translate("MainWindow", "I have a LM dataset", None))
        self.toFIBSEM.setText(_translate("MainWindow", "To SEM microscope", None))
        self.toFIBSEMAcq.setText(_translate("MainWindow", "To FIB SEM acquisition", None))
        self.changeOptions.setText(_translate("MainWindow", "Change Configuration", None))
        self.label.setText(_translate("MainWindow", "CLEM Tool options:", None))

            
import common.dialogs.resources_rc
