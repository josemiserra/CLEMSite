# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\JMS\Documents\msite\MSite\msiteSEM\UI\FastCalibration.ui'
#
# Created: Sat Jan 16 19:04:32 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import tempfile
import shutil
import cv2
import numpy as np
from common.image_an.xcorr import xcorr

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

class Ui_fastCalibration(QDialog):
    xlabels=""
    ylabels=""
    counter_points = 0
    points_list = []
    points_names = []
    messages = ["4 POINTS TO GO!!!","3 POINTS TO GO!!!","2 POINTS TO GO!!!","1 POINT TO GO!!!","READY!","ERROR: Avoid colinearity between points."]
    M_navigational = np.array([])


    def __init__(self, mainDialog):
        self.mainDialog = mainDialog

        self.xlabels = self.mainDialog.vMap.grid_map.xlabels
        self.ylabels = self.mainDialog.vMap.grid_map.ylabels

        super(Ui_fastCalibration, self).__init__()

    def setupUi(self, fastCalibration):
        fastCalibration.setObjectName(_fromUtf8("fastCalibration"))
        fastCalibration.resize(1500, 950)
        self.layoutWidget = QWidget(fastCalibration)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 30, 1450, 900))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout_4 = QGridLayout(self.layoutWidget)
        self.gridLayout_4.setContentsMargins(0,0,0,0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_Points = QLabel(self.layoutWidget)
        self.label_Points.setObjectName(_fromUtf8("label_Points"))
        self.verticalLayout_2.addWidget(self.label_Points)
        self.tableViewPoints = QTableWidget(self.layoutWidget)
        self.tableViewPoints.setObjectName(_fromUtf8("tableViewPoints"))
        self.verticalLayout_2.addWidget(self.tableViewPoints)
        self.gridLayout_3.addLayout(self.verticalLayout_2, 4, 0, 1, 1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.horizontalLayout_3.addItem(spacerItem)
        self.checkBox_p1 = QCheckBox(self.layoutWidget)
        self.checkBox_p1.setEnabled(True)
        font = QFont()
        font.setPointSize(12)
        self.checkBox_p1.setFont(font)
        # self.checkBox_p1.setCheckable(False)
        self.checkBox_p1.setObjectName(_fromUtf8("checkBox_p1"))
        self.horizontalLayout_3.addWidget(self.checkBox_p1)
        self.checkBox_p2 = QCheckBox(self.layoutWidget)
        self.checkBox_p2.setEnabled(True)
        font = QFont()
        font.setPointSize(12)
        self.checkBox_p2.setFont(font)
        # self.checkBox_p2.setCheckable(False)
        self.checkBox_p2.setObjectName(_fromUtf8("checkBox_p2"))
        self.horizontalLayout_3.addWidget(self.checkBox_p2)
        self.checkBox_p3 = QCheckBox(self.layoutWidget)
        self.checkBox_p3.setEnabled(True)
        font = QFont()
        font.setPointSize(12)
        self.checkBox_p3.setFont(font)
        # self.checkBox_p3.setCheckable(False)
        self.checkBox_p3.setObjectName(_fromUtf8("checkBox_p3"))
        self.horizontalLayout_3.addWidget(self.checkBox_p3)
        self.checkBox_p4 = QCheckBox(self.layoutWidget)
        self.checkBox_p4.setEnabled(True)
        font = QFont()
        font.setPointSize(12)
        self.checkBox_p4.setFont(font)
        # self.checkBox_p3.setCheckable(False)
        self.checkBox_p4.setObjectName(_fromUtf8("checkBox_p4"))
        self.horizontalLayout_3.addWidget(self.checkBox_p4)

        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 3, 0, 1, 1)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.gridLayout_3.addLayout(self.horizontalLayout_2, 5, 0, 1, 1)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_Announce = QLabel(self.layoutWidget)
        font = QFont()
        font.setPointSize(16)
        self.label_Announce.setFont(font)
        self.label_Announce.setObjectName(_fromUtf8("label_Announce"))
        self.gridLayout.addWidget(self.label_Announce, 0, 0, 1, 1)
        self.pushButton_add = QPushButton(self.layoutWidget)
        self.pushButton_add.setObjectName(_fromUtf8("pushButton_add"))
        self.gridLayout.addWidget(self.pushButton_add, 2, 1, 1, 1)
        self.comboBox = QComboBox(self.layoutWidget)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.gridLayout.addWidget(self.comboBox, 2, 0, 1, 1)
        self.pushButton_delete = QPushButton(self.layoutWidget)
        self.pushButton_delete.setObjectName(_fromUtf8("pushButton_delete"))
        self.gridLayout.addWidget(self.pushButton_delete, 3, 1, 1, 1)
        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 1, 1, 1)
        self.label = QLabel(self.layoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setMinimumSize(800,430)
        self.label.setSizePolicy(sizePolicy)
        self.label.setText(_fromUtf8(""))
        pixmap = QPixmap(_fromUtf8(":/res/Instructions.png"))
        self.label.setPixmap(pixmap.scaled(self.label.size(),QtCore.Qt.KeepAspectRatio))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)
        self.buttonBox_Skip = QDialogButtonBox(self.layoutWidget)
        self.buttonBox_Skip.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox_Skip.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox_Skip.setCenterButtons(False)
        self.buttonBox_Skip.setObjectName(_fromUtf8("buttonBox_Skip"))
        self.gridLayout_4.addWidget(self.buttonBox_Skip, 1, 1, 1, 1)

        self.tableViewPoints .setRowCount(4)
        self.tableViewPoints.setColumnCount(4)
        item = QTableWidgetItem()
        self.tableViewPoints.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.tableViewPoints.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.tableViewPoints.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        self.tableViewPoints.setHorizontalHeaderItem(3, item)
        self.retranslateUi(fastCalibration)
        
        self.buttonBox_Skip.accepted.connect(self.acceptFirst)
        self.buttonBox_Skip.rejected.connect(self.reject)
        self.pushButton_add.clicked.connect(self.add_point)
        self.pushButton_delete.clicked.connect(self.delete_point)
        self.comboBox.currentIndexChanged[int].connect(self.letter_selected)
        # self.label.mouseDoubleClickEvent[]connect(self.mhelp)
        QtCore.QMetaObject.connectSlotsByName(fastCalibration)

    def retranslateUi(self, fastCalibration):
        fastCalibration.setWindowTitle(_translate("fastCalibration", "Calibrate Points", None))
        i = 0
        for elx in self.xlabels:
            for ely in self.ylabels:
                self.comboBox.addItem(_fromUtf8(""))
                self.comboBox.setItemText(i, _translate("EditGrid", str(elx)+str(ely), None))
                i = i + 1

        self.checkBox_p1.setText(_translate("fastCalibration", "1", None))
        self.checkBox_p2.setText(_translate("fastCalibration", "2", None))
        self.checkBox_p3.setText(_translate("fastCalibration", "3", None))
        self.checkBox_p4.setText(_translate("fastCalibration", "4", None))
        self.pushButton_delete.setText(_translate("fastCalibration", "Delete", None))
        self.label_Announce.setText(_translate("fastCalibration", self.messages[0], None))
        self.pushButton_add.setText(_translate("fastCalibration", "Add", None))
        self.label_Points.setText(_translate("fastCalibration", "Points :", None))
        item = self.tableViewPoints.horizontalHeaderItem(0)
        item.setText(_translate("fastCalibration", "Name", None))
        item = self.tableViewPoints.horizontalHeaderItem(1)
        item.setText(_translate("fastCalibration", "X", None))
        item = self.tableViewPoints.horizontalHeaderItem(2)
        item.setText(_translate("fastCalibration", "Y", None))
        item = self.tableViewPoints.horizontalHeaderItem(3)
        item.setText(_translate("fastCalibration", "Z", None))
        self.label_2.setText(_translate("fastCalibration", "Go to your point and select your letter here:", None))
        self.counter_points = 0
        self.points_list = []
        self.points_names = []

    def acceptFirst(self):
        if(self.counter_points<3):
            ret = QMessageBox.question(self, 'Finishing already?',
            "No enough points to navigational map. \n Do you want to cancel 3 point calibration?",
            QMessageBox.Ok, QMessageBox.Cancel)
            if ret == QMessageBox.Ok:
                    self.reject()
                    return
            else:
                return

        if(self.collinear(self.points_list[0]['position'],self.points_list[1]['position'],self.points_list[2]['position'])):
                ret = QMessageBox.critical(self, "Repeat", "The three points are colinear. Replace one of the points.", QMessageBox.Ok)
                return
        self.accept()
        return


    def modifyComboBox(self,itags):
        i = 0
        self.comboBox.clear()
        for elx in self.xlabels:
            for ely in self.ylabels:
                letter = str(elx) + str(ely)
                if letter in itags:
                    self.comboBox.addItem(_fromUtf8(""))
                    self.comboBox.setItemText(i, _translate("EditGrid",letter, None))
                    i = i + 1



    def mhelp(self):
        QMessageBox.information(self, 'NAVIGATIONAL MODE', "Find the letter from the actual position shown in the microscope(top cross corner) and press the GO button. \n \
        After 4 clicks you will be able to move inside your sample clicking in the grid map.", QMessageBox.Ok)

    def add_point(self):
        point_id = str(self.comboBox.currentText())
        if(point_id in self.points_names): # Avoid nonsense selection
            self.letter_selected()
            return
        m_index = self.counter_points

        point = {}
        point['id'] = point_id
        error,point['position'] = self.mainDialog.msc_server.getCurrentStagePosition()
        coords_canvas_xy = self.mainDialog.vMapCanvas.getLandmark(point_id, 1)
        if coords_canvas_xy[0] == -np.inf:
            coords_canvas_xy = self.mainDialog.vMap.grid_map.getCoordinatesFromLabel(point_id)
        coords_canvas_xyz = (coords_canvas_xy[0],coords_canvas_xy[1],0.0)
        point['canvas'] = coords_canvas_xyz

        self.points_list.append(point)
        self.points_names.append(point_id)

        item = QTableWidgetItem(point_id)
        self.tableViewPoints.setItem(m_index,0, item)
        item = QTableWidgetItem(str(point['position'][0]))
        self.tableViewPoints.setItem(m_index,1, item)
        item = QTableWidgetItem(str(point['position'][1]))
        self.tableViewPoints.setItem(m_index,2, item)
        item = QTableWidgetItem(str(point['position'][2]))
        self.tableViewPoints.setItem(m_index,3, item)

        self.counter_points = self.counter_points +1
        if(self.counter_points == 1):
            self.label_Announce.setText(_translate("fastCalibration", self.messages[1], None))
            self.checkBox_p1.setChecked(True)
        elif(self.counter_points == 2):
            self.label_Announce.setText(_translate("fastCalibration", self.messages[2], None))
            self.checkBox_p2.setChecked(True)
        elif(self.counter_points == 3):
            self.label_Announce.setText(_translate("fastCalibration", self.messages[3], None))
            self.checkBox_p3.setChecked(True)
        else:
            self.label_Announce.setText(_translate("fastCalibration", self.messages[4], None))
            self.checkBox_p4.setChecked(True)

    def delete_point(self):
        x = self.tableViewPoints.currentIndex()
        row = x.row()
        if(row>-1):
            self.points_list[row]['position'] = []
            self.points_list[row]['canvas']=[]
            self.points_list.remove(self.points_list[row])
            self.points_names.remove(self.points_names[row])
            m_index = row
            self.tableViewPoints.removeRow(row)
            self.tableViewPoints.setRowCount(4)
            self.counter_points = self.counter_points-1
            if(self.counter_points == 1):
                self.label_Announce.setText(_translate("fastCalibration", self.messages[1], None))
                self.checkBox_p1.setChecked(True)
                self.checkBox_p2.setChecked(False)
                self.checkBox_p3.setChecked(False)
                self.checkBox_p4.setChecked(False)
            elif(self.counter_points == 2):
                self.label_Announce.setText(_translate("fastCalibration", self.messages[2], None))
                self.checkBox_p1.setChecked(True)
                self.checkBox_p2.setChecked(True)
                self.checkBox_p3.setChecked(False)
                self.checkBox_p4.setChecked(False)
            elif(self.counter_points == 3):
                self.label_Announce.setText(_translate("fastCalibration", self.messages[3], None))
                self.checkBox_p1.setChecked(True)
                self.checkBox_p2.setChecked(True)
                self.checkBox_p3.setChecked(True)
                self.checkBox_p4.setChecked(False)
            else:
                self.label_Announce.setText(_translate("fastCalibration", self.messages[0], None))
                self.checkBox_p1.setChecked(False)
                self.checkBox_p2.setChecked(False)
                self.checkBox_p3.setChecked(False)
                self.checkBox_p4.setChecked(False)

    def letter_selected(self):
        point_id = str(self.comboBox.currentText())

        if(point_id in self.points_names):
            ret = QMessageBox.critical(self, "Repeat",
              '''This point has been already introduced.''', QMessageBox.Ok)
            return
        if(len(self.points_names)==3):
            point_1 = self.points_names[0]
            point_2 = self.points_names[1]
            if((point_id[0]==point_1[0] and point_id[0]==point_2[0]) \
                or (point_id[1]==point_1[1] and point_id[1]==point_2[1])):
                ret = QMessageBox.critical(self, "Repeat",
                '''This point is collinear.''', QMessageBox.Ok)
                return

    def collinear(self,p0, p1, p2):
         x1, y1 = p1[0] - p0[0], p1[1] - p0[1]
         x2, y2 = p2[0] - p0[0], p2[1] - p0[1]
         return abs(x1 * y2 - x2 * y1) < 1e-9

    def getRank(a, rtol=1e-5):
        u, s, v = np.linalg.svd(a)
        rank = (s > rtol*s[0]).sum()
        return rank




import common.dialogs.resources_rc
