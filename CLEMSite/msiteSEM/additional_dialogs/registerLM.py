# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\JMS\Documents\msite\MSite\msiteSEM\UI\registerLM.ui'
#
# Created: Sun Sep 04 12:18:07 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import pandas as pd
import os, sys, re
import cv2

from common.image_an.xcorr import findShift
from common.image_an.readers import getInfoHeader
from common.image_an.registerOk import Ui_RegisterWindow
from common.image_an.readers import imageToStageCoordinates_LM
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

class Ui_DialogRegisterLM(QtWidgets.QDialog):

    samplesList = []
    cell_position_list = []
    logger = []
    corrections = False

    def __init__(self, imainApp, logger):
        self.mainApp = imainApp
        self.total_cells = len(imainApp.m_listdir)
        self.path, _ = os.path.split(imainApp.m_listdir[0])
        self.path,_ = os.path.split(self.path)
        self.position_px_list = np.zeros((2, (len(imainApp.m_listdir))))
        self.position_stage_list = np.zeros((2, (len(imainApp.m_listdir))))
        self.tags = []
        for el in imainApp.m_listdir:
            _, tag = os.path.split(el)
            self.tags.append(tag)
        self.accepted_indices = []
        self.list_dsh = []
        self.logger = logger
        super(Ui_DialogRegisterLM, self).__init__()

    def setupUi(self, DialogRegisterLM):
        DialogRegisterLM.setObjectName(_fromUtf8("DialogRegisterLM"))
        DialogRegisterLM.resize(965, 837)
        self.gridLayout_3 = QGridLayout(DialogRegisterLM)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.buttonBox = QDialogButtonBox(DialogRegisterLM)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 1, 2, 1, 1)
        self.splitter = QSplitter(DialogRegisterLM)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)
        self.groupBox_register = QGroupBox(DialogRegisterLM)
        self.groupBox_register.setObjectName(_fromUtf8("groupBox_register"))
        self.gridLayout = QGridLayout(self.groupBox_register)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_7 = QLabel(self.groupBox_register)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout.addWidget(self.label_7)
        self.lineEdit_reference = QLineEdit(self.groupBox_register)
        self.lineEdit_reference.setObjectName(_fromUtf8("lineEdit_reference"))
        self.horizontalLayout.addWidget(self.lineEdit_reference)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_12 = QLabel(self.groupBox_register)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_3.addWidget(self.label_12)
        self.lineEdit_extraimg = QLineEdit(self.groupBox_register)
        self.lineEdit_extraimg.setText(_fromUtf8(""))
        self.lineEdit_extraimg.setObjectName(_fromUtf8("lineEdit_extraimg"))
        self.horizontalLayout_3.addWidget(self.lineEdit_extraimg)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_10 = QLabel(self.groupBox_register)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.horizontalLayout_2.addWidget(self.label_10)
        self.lineEdit_corrected = QLineEdit(self.groupBox_register)
        self.lineEdit_corrected.setObjectName(_fromUtf8("lineEdit_corrected"))
        self.horizontalLayout_2.addWidget(self.lineEdit_corrected)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_13 = QLabel(self.groupBox_register)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.horizontalLayout_4.addWidget(self.label_13)
        self.lineEdit_file = QLineEdit(self.groupBox_register)
        self.lineEdit_file.setText(_fromUtf8(""))
        self.lineEdit_file.setObjectName(_fromUtf8("lineEdit_file"))
        self.horizontalLayout_4.addWidget(self.lineEdit_file)
        self.pushButton = QPushButton(self.groupBox_register)
        self.pushButton.setText(_fromUtf8("..."))
        icon = QIcon()
        icon.addPixmap(QPixmap(_fromUtf8("../common/dialogs/res/open.png")), QIcon.Normal, QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.horizontalLayout_4, 4, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_register, 0, 1, 1, 2)

        self.retranslateUi(DialogRegisterLM)
        self.buttonBox.accepted.connect(self.checkBeforeAccept)
        self.buttonBox.rejected.connect(DialogRegisterLM.reject)
        self.pushButton.clicked.connect(self.loadPositionsFile)

        QtCore.QMetaObject.connectSlotsByName(DialogRegisterLM)

    def retranslateUi(self, DialogRegisterLM):
        DialogRegisterLM.setWindowTitle(_translate("DialogRegisterLM", "Register LM ", None))
        self.groupBox_register.setTitle(_translate("DialogRegisterLM", "Compute registration between images", None))
        self.label_7.setText(_translate("DialogRegisterLM", "Reference image \n"
"regular expression:", None))
        self.label_12.setText(_translate("DialogRegisterLM", "Additional image \n"
"regular expression :", None))
        self.label_10.setText(_translate("DialogRegisterLM", "Template image \n"
"regular expression :", None))
        self.label_13.setText(_translate("DialogRegisterLM", "Inside template position file :", None))
        self.setTabOrder(self.lineEdit_reference, self.lineEdit_corrected)
        self.setTabOrder(self.lineEdit_corrected, self.lineEdit_extraimg)
        self.setTabOrder(self.lineEdit_extraimg, self.lineEdit_file)
        self.lineEdit_reference.setText("golgi.*GFP.*10x.*")
        self.lineEdit_corrected.setText("prescan.*golgi.*")
        self.lineEdit_extraimg.setText("spot.*10x.*")

    def save(self):
        fname,_ = QFileDialog.getSaveFileName(self, 'Save file', "list_of_positions",
                                                  "Positions file (*.csv)")
        if fname:
            fname = str(fname)
        else:
            self.logger.error('Error saving file.')
            return

        dic_pos_list = {}
        dic_pos_list["Sample"]=[]
        try:
            self.registerImages(fname)
        except Exception as e:
            self.logger.info(str(e))
            return
        self.accept()

    def loadPositionsFile(self):
        """
        Loads positions of cells of interest
        :return:
        """
        fname,_ = QFileDialog.getOpenFileName(self, 'Translation file', self.path,
                                                       "Pixel Coordinate Files(*.json *.csv)")

        if (fname):
            self.lineEdit_file.setText(fname)
            self.corrections = True
            if fname[-5:]=='.json':
                table_corrections = pd.read_json(fname)
            else:
                table_corrections = pd.read_csv(fname, index_col=0)

            if 'Name' in table_corrections.columns:
                table_corrections.index = table_corrections['Name']

            table_corrections = table_corrections[['Location_Center_X','Location_Center_Y']]
            self.list_corrections = list(table_corrections.index)
            y = map(lambda s: int(s[-4::]), self.list_corrections)
            sorted_ind = [self.list_corrections[el[0]] for el in sorted(enumerate(y), key=lambda x: x[1])]
            self.table_corrections = table_corrections.loc[sorted_ind]

    def checkBeforeAccept(self):
        self.save()
        return

    def registerImages(self, filetosave):

        reference = str(self.lineEdit_reference.text())
        template = str(self.lineEdit_corrected.text())
        extra = str(self.lineEdit_extraimg.text())

        if (reference == "" or template == ""):
            self.logger.error("Warning: you have to give a regular expression or full name for each image!!")
            return

        with open(filetosave, 'w') as file:
            file.write('Name,Location_Center_X,Location_Center_Y,Location_Center_X_stage,Location_Center_Y_stage\n')

        self.options = {}
        for ind in range(self.total_cells):
            if (len(reference) > 2):
                tag = self.tags[ind]
                self.logger.info("Sample " + tag)
                accepted, position_px, tag, ref_path = self.calculateShift(ind, tag, reference, template, extra)
                # Here we calculate the units RESPECT the central image (reference)
                if accepted :
                    #First calculate position in pixels
                    info =  getInfoHeader(ref_path)
                    tpoint = [float(info['PositionX']),float(info['PositionY'])]
                    pixelSize = float(info['PixelSize'])
                    isize = cv2.imread(ref_path,0).shape
                    pxt = np.array(position_px)
                    stage_pos = imageToStageCoordinates_LM(pxt.reshape(1, 2), tpoint, isize, pixelSize)
                    stage_pos = stage_pos.reshape(2)
                    cell_position = tag+','+str(position_px[0])+','+str(position_px[1])+','+str(stage_pos[0])+','+str(stage_pos[1])+'\n'          # 'Name,Location_Center_X,Location_Center_Y,Location_Center_X_stage,Location_Center_Y_stage'
                    with open(filetosave, 'a') as file:
                        file.write(cell_position)

        return

    def calculateShift(self,ind, tag, reference_regexp, template_regexp, extraimg_regexp):

            im_reference = self.mainApp.getImageFileList(ind, str(reference_regexp))
            if (not im_reference):
                    QMessageBox.information(self, 'ERROR',
                                                  "Images with the regular expression "+reference_regexp+" could not be found. Try again.",
                                                  QMessageBox.Ok)
                    self.logger.error("Common name " + reference_regexp + " in sample " + str(ind) + "not found.")
                    return None,None,None
            im_template = self.mainApp.getImageFileList(ind, str(template_regexp))
            if (not im_template):
                    QMessageBox.information(self, 'ERROR',
                                                  "Images with the regular expression "+template_regexp+" could not be found. Try again.",
                                                  QMessageBox.Ok)
                    self.logger.error("Common name " + template_regexp + " in sample " + str(ind) + "not found.")
                    return None,None,None
            extraimg = self.mainApp.getImageFileList(ind, str(extraimg_regexp))
            if (not extraimg):
                extraimg = ""
            if (self.corrections):
                    sample_index = self.bestMatch(self.list_corrections, tag, 8)
                    correction = self.table_corrections.loc[sample_index].as_matrix()
                    self.table_corrections = self.table_corrections.drop(sample_index)
                    self.list_corrections.remove(sample_index)
            else:
                    correction = np.array([-1.0, -1.0], dtype=np.float32)

            appr = Ui_RegisterWindow(im_reference, im_template, extraimg, correction, tag+": "+str(ind+1)+" of "+str(self.total_cells), self.options)
            retCod = appr.exec_()
            self.options = appr._menu_config.copy()
            if (retCod == QDialog.Accepted):
                location_pixels = appr.centerOrg_Ref
                ref_path = im_reference[self.options['sel_box1']]
                if (not np.any(np.isinf(location_pixels))):
                    self.logger.info("Computed shift between images (in pixels):")
                    self.logger.info(str(location_pixels))
                    return True,location_pixels, tag, ref_path
                else:
                    return False,[],tag,[]


    def bestMatch(self, myList, myString, minToMatch = 6):
        for i in range(len(myString)-minToMatch):
            pattern = re.compile(myString[i:i+minToMatch])
            indices = [i for i, x in enumerate(myList) if pattern.search(x)]
            if indices:
                return myList[indices[0]]
        return []


