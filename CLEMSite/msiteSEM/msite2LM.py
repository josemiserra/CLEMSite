# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\JMS\Documents\msite\MSite\msiteSEM\UI\MSite3SEM_p1v2.ui'
#
# Created: Sat Jul 30 13:44:46 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
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

class Ui_MSite2p1(QMainWindow):
    def setupUi(self, MSite2p1):
        MSite2p1.setObjectName(_fromUtf8("MSite2p1"))
        MSite2p1.setWindowModality(QtCore.Qt.WindowModal)
        screen = QDesktopWidget().screenGeometry()
        MSite2p1.resize(screen.width() * 1655.0 / 2880.0, screen.height() * 1130.0 / 1620.0)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MSite2p1.sizePolicy().hasHeightForWidth())
        MSite2p1.setSizePolicy(sizePolicy)
        MSite2p1.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        MSite2p1.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/msite2.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MSite2p1.setWindowIcon(icon)
        MSite2p1.setStyleSheet(_fromUtf8("color:rgb(0, 0, 127)"))
        MSite2p1.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        MSite2p1.setDocumentMode(False)
        self.centralwidget = QWidget(MSite2p1)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.gridLayout_2.addLayout(self.horizontalLayout_4, 0, 1, 1, 1)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushButton_All = QPushButton(self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_All.sizePolicy().hasHeightForWidth())
        self.pushButton_All.setSizePolicy(sizePolicy)
        self.pushButton_All.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/do_all.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_All.setIcon(icon1)
        self.pushButton_All.setIconSize(QtCore.QSize(48, 48))
        self.pushButton_All.setObjectName(_fromUtf8("pushButton_All"))
        self.horizontalLayout_2.addWidget(self.pushButton_All)
        self.pushButton_One = QPushButton(self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_One.sizePolicy().hasHeightForWidth())
        self.pushButton_One.setSizePolicy(sizePolicy)
        self.pushButton_One.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/one.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_One.setIcon(icon2)
        self.pushButton_One.setIconSize(QtCore.QSize(48, 48))
        self.pushButton_One.setObjectName(_fromUtf8("pushButton_One"))
        self.horizontalLayout_2.addWidget(self.pushButton_One)
        self.pushButton_Delete = QPushButton(self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_Delete.sizePolicy().hasHeightForWidth())
        self.pushButton_Delete.setSizePolicy(sizePolicy)
        self.pushButton_Delete.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/collapse.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Delete.setIcon(icon3)
        self.pushButton_Delete.setIconSize(QtCore.QSize(48, 48))
        self.pushButton_Delete.setObjectName(_fromUtf8("pushButton_Delete"))
        self.horizontalLayout_2.addWidget(self.pushButton_Delete)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)


        self.pushButton_Reject = QPushButton(self.centralwidget)
        self.pushButton_Reject.setSizePolicy(sizePolicy)
        self.pushButton_Reject.setText(_fromUtf8(""))
        icon31 = QtGui.QIcon()
        icon31.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/cross.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Reject.setIcon(icon31)
        self.pushButton_Reject.setIconSize(QtCore.QSize(48, 48))
        self.pushButton_Reject.setObjectName(_fromUtf8("pushButton_Reject"))
        self.horizontalLayout_2.addWidget(self.pushButton_Reject)


        self.horizontalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))

        self.pushButton_GridMap = QPushButton(self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_GridMap.sizePolicy().hasHeightForWidth())
        self.pushButton_GridMap.setSizePolicy(sizePolicy)
        self.pushButton_GridMap.setText(_fromUtf8(""))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/2x2_grid.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_GridMap.setIcon(icon4)
        self.pushButton_GridMap.setIconSize(QtCore.QSize(48, 48))
        self.pushButton_GridMap.setObjectName(_fromUtf8("pushButton_GridMap"))
        self.horizontalLayout_3.addWidget(self.pushButton_GridMap)
        self.horizontalLayout_2.addLayout(self.horizontalLayout_3)
        self.pushButton_ErrorMap = QPushButton(self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_ErrorMap.sizePolicy().hasHeightForWidth())
        self.pushButton_ErrorMap.setSizePolicy(sizePolicy)
        self.pushButton_ErrorMap.setText(_fromUtf8(""))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/chart_line_2.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_ErrorMap.setIcon(icon5)
        self.pushButton_ErrorMap.setIconSize(QtCore.QSize(48, 48))
        self.pushButton_ErrorMap.setObjectName(_fromUtf8("pushButton_ErrorMap"))
        self.horizontalLayout_2.addWidget(self.pushButton_ErrorMap)
        spacerItem2 = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.horizontalLayout_2.addItem(spacerItem2)
        spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.pushButton_Export = QPushButton(self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_Export.sizePolicy().hasHeightForWidth())
        self.pushButton_Export.setSizePolicy(sizePolicy)
        self.pushButton_Export.setText(_fromUtf8(""))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/load_point.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_Export.setIcon(icon6)
        self.pushButton_Export.setIconSize(QtCore.QSize(48, 48))
        self.pushButton_Export.setObjectName(_fromUtf8("pushButton_Export"))
        self.horizontalLayout_2.addWidget(self.pushButton_Export)
        spacerItem4 = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.tableWidget_Samples = QTableWidget(self.centralwidget)
        self.tableWidget_Samples.setGridStyle(QtCore.Qt.DashLine)
        self.tableWidget_Samples.setObjectName(_fromUtf8("tableWidget_Samples"))
        self.tableWidget_Samples.setColumnCount(4)
        self.tableWidget_Samples.setRowCount(0)
        item = QTableWidgetItem()
        self.tableWidget_Samples.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.tableWidget_Samples.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.tableWidget_Samples.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        self.tableWidget_Samples.setHorizontalHeaderItem(3, item)
        self.tableWidget_Samples.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidget_Samples.horizontalHeader().setMinimumSectionSize(36)
        self.tableWidget_Samples.verticalHeader().setDefaultSectionSize(60)
        self.tableWidget_Samples.verticalHeader().setMinimumSectionSize(30)
        self.verticalLayout_2.addWidget(self.tableWidget_Samples)
        self.gridLayout_2.addLayout(self.verticalLayout_2, 1, 1, 1, 1)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lineEdit_2 = QLineEdit(self.centralwidget)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 3, 0, 1, 1)
        self.horizontalLayout_1 = QHBoxLayout()
        self.horizontalLayout_1.setObjectName(_fromUtf8("horizontalLayout_1"))
        self.splitter_2 = QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.label_load = QLabel(self.splitter_2)
        self.label_load.setObjectName(_fromUtf8("label_load"))
        self.lineEditFolder = QLineEdit(self.splitter_2)
        self.lineEditFolder.setObjectName(_fromUtf8("lineEditFolder"))
        self.pushButtonFolder = QPushButton(self.splitter_2)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonFolder.sizePolicy().hasHeightForWidth())
        self.pushButtonFolder.setSizePolicy(sizePolicy)
        self.pushButtonFolder.setText(_fromUtf8(""))
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonFolder.setIcon(icon7)
        self.pushButtonFolder.setIconSize(QtCore.QSize(38, 38))
        self.pushButtonFolder.setObjectName(_fromUtf8("pushButtonFolder"))
        self.horizontalLayout_1.addWidget(self.splitter_2)
        self.gridLayout_2.addLayout(self.horizontalLayout_1, 0, 0, 1, 1)
        self.treeView = QTreeView(self.centralwidget)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.gridLayout_2.addWidget(self.treeView, 1, 0, 2, 1)
        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout_2.addWidget(self.progressBar, 3, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        MSite2p1.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MSite2p1)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1655, 38))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(_fromUtf8("menuSettings"))
        MSite2p1.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MSite2p1)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MSite2p1.setStatusBar(self.statusbar)
        self.actionSettings = QAction(MSite2p1)
        self.actionSettings.setObjectName(_fromUtf8("actionSettings"))
        self.actionPreferences = QAction(MSite2p1)
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))
        self.actionLoad_experiment = QAction(MSite2p1)
        self.actionLoad_experiment.setObjectName(_fromUtf8("actionLoad_experiment"))
        self.actionSave_experiment = QAction(MSite2p1)
        self.actionSave_experiment.setObjectName(_fromUtf8("actionSave_experiment"))
        self.actionSave_experiment_as = QAction(MSite2p1)
        self.actionSave_experiment_as.setObjectName(_fromUtf8("actionSave_experiment_as"))
        self.actionRename_Light_M_files = QAction(MSite2p1)
        self.actionRename_Light_M_files.setObjectName(_fromUtf8("actionRename_Light_M_files"))
        self.actionClear_all_computed_data = QAction(MSite2p1)
        self.actionClear_all_computed_data.setObjectName(_fromUtf8("actionClear_all_computed_data"))

        self.actionZstack = QAction(MSite2p1)
        self.actionZstack.setObjectName(_fromUtf8("Zstack"))

        self.actionCompute_Registration_Shift = QAction(MSite2p1)
        self.actionCompute_Registration_Shift.setObjectName(_fromUtf8("actionCompute_Registration_Shift"))

        self.actionLoad_Registration_Shift = QAction(MSite2p1)
        self.actionLoad_Registration_Shift.setObjectName(_fromUtf8("actionLoad_Registration_Shift"))

        self.actionGenerateFileCoordinates = QAction(MSite2p1)
        self.actionGenerateFileCoordinates.setObjectName(_fromUtf8("actionGenerateFileCoordinates"))

        self.menuEdit.addAction(self.actionLoad_experiment)
        self.menuEdit.addAction(self.actionSave_experiment)
        self.menuSettings.addAction(self.actionPreferences)
        self.menuSettings.addAction(self.actionRename_Light_M_files)
        self.menuSettings.addAction(self.actionClear_all_computed_data)
        self.menuSettings.addAction(self.actionZstack)
        self.menuSettings.addAction(self.actionCompute_Registration_Shift)
        self.menuSettings.addAction(self.actionLoad_Registration_Shift)
        self.menuSettings.addAction(self.actionGenerateFileCoordinates)
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())

        self.retranslateUi(MSite2p1)
        QtCore.QMetaObject.connectSlotsByName(MSite2p1)

    def retranslateUi(self, MSite2p1):
        MSite2p1.setWindowTitle(_translate("MSite2p1", "MSite LM-SEM", None))
        item = self.tableWidget_Samples.horizontalHeaderItem(0)
        item.setText(_translate("MSite2p1", "Sample Name", None))
        item = self.tableWidget_Samples.horizontalHeaderItem(1)
        item.setText(_translate("MSite2p1", "Letter", None))
        item = self.tableWidget_Samples.horizontalHeaderItem(2)
        item.setText(_translate("MSite2p1", "Accepted", None))
        item = self.tableWidget_Samples.horizontalHeaderItem(3)
        item.setText(_translate("MSite2p1", "Message", None))
        self.label.setText(_translate("MSite2p1", "File name:", None))
        self.label_2.setText(_translate("MSite2p1", "Path:", None))
        self.label_load.setText(_translate("MSite2p1", "Load your targets sample folder :", None))
        self.menuEdit.setTitle(_translate("MSite2p1", "File", None))
        self.menuSettings.setTitle(_translate("MSite2p1", "Settings", None))
        self.actionSettings.setText(_translate("MSite2p1", "Settings", None))
        self.actionPreferences.setText(_translate("MSite2p1", "Preferences", None))
        self.actionLoad_experiment.setText(_translate("MSite2p1", "Load folder", None))
        self.actionSave_experiment.setText(_translate("MSite2p1", "Save log as...", None))
        self.actionSave_experiment.setShortcut(_translate("MSite2p1", "Ctrl+S", None))
        self.actionSave_experiment_as.setText(_translate("MSite2p1", "Save experiment as...", None))
        self.actionRename_Light_M_files.setText(_translate("MSite2p1", "Rename LM files", None))
        self.actionClear_all_computed_data.setText(_translate("MSite2p1", "Clear all computed data", None))
        self.actionZstack.setText(_translate("MSite2p1", "Z projection from z stacks", None))
        self.actionCompute_Registration_Shift.setText(_translate("MSite2p1", "Compute registration shift", None))
        self.actionLoad_Registration_Shift.setText(_translate("MSite2p1", "Load file of positions from a file", None))
        self.actionGenerateFileCoordinates.setText(_translate("MSite2p1", "Generate file of positions from metadata", None))

import common.dialogs.resources_rc
