# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Schwab\Documents\msite\MSite\common\UI\standalone.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_CLEMSite_Dialog(object):
    def setupUi(self, CLEMSite_Dialog):
        CLEMSite_Dialog.setObjectName(_fromUtf8("CLEMSite_Dialog"))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CLEMSite_Dialog.sizePolicy().hasHeightForWidth())
        CLEMSite_Dialog.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.LinkVisited, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.LinkVisited, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.LinkVisited, brush)
        CLEMSite_Dialog.setPalette(palette)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/picture_icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        CLEMSite_Dialog.setWindowIcon(icon)
        CLEMSite_Dialog.setAutoFillBackground(False)
        CLEMSite_Dialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.layoutWidget_8 = QtGui.QWidget(CLEMSite_Dialog)
        self.layoutWidget_8.setGeometry(QtCore.QRect(30, 20, 327, 48))
        self.layoutWidget_8.setObjectName(_fromUtf8("layoutWidget_8"))
        self.horizontalLayout_10 = QtGui.QHBoxLayout(self.layoutWidget_8)
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        self.pushButton_Connect = QtGui.QPushButton(self.layoutWidget_8)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_Connect.setFont(font)
        self.pushButton_Connect.setDefault(False)
        self.pushButton_Connect.setFlat(False)
        self.pushButton_Connect.setObjectName(_fromUtf8("pushButton_Connect"))
        self.horizontalLayout_10.addWidget(self.pushButton_Connect)
        self.pushButton_Disconnect = QtGui.QPushButton(self.layoutWidget_8)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_Disconnect.setFont(font)
        self.pushButton_Disconnect.setObjectName(_fromUtf8("pushButton_Disconnect"))
        self.horizontalLayout_10.addWidget(self.pushButton_Disconnect)
        self.layoutWidget = QtGui.QWidget(CLEMSite_Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(30, 80, 431, 511))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.line = QtGui.QFrame(self.layoutWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lineEdit_SetupName = QtGui.QLineEdit(self.layoutWidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.lineEdit_SetupName.setPalette(palette)
        self.lineEdit_SetupName.setObjectName(_fromUtf8("lineEdit_SetupName"))
        self.horizontalLayout.addWidget(self.lineEdit_SetupName)
        self.pushButton_SetupFile = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_SetupFile.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.pushButton_SetupFile.setObjectName(_fromUtf8("pushButton_SetupFile"))
        self.horizontalLayout.addWidget(self.pushButton_SetupFile)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.groupBox_4 = QtGui.QGroupBox(self.layoutWidget)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_lx = QtGui.QLabel(self.groupBox_4)
        self.label_lx.setObjectName(_fromUtf8("label_lx"))
        self.gridLayout_2.addWidget(self.label_lx, 0, 0, 1, 1)
        self.checkBox_grab_um = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox_grab_um.setObjectName(_fromUtf8("checkBox_grab_um"))
        self.gridLayout_2.addWidget(self.checkBox_grab_um, 1, 0, 2, 4)
        self.label_umx = QtGui.QLabel(self.groupBox_4)
        self.label_umx.setObjectName(_fromUtf8("label_umx"))
        self.gridLayout_2.addWidget(self.label_umx, 1, 4, 2, 1)
        self.checkBox_grab_sections = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox_grab_sections.setObjectName(_fromUtf8("checkBox_grab_sections"))
        self.gridLayout_2.addWidget(self.checkBox_grab_sections, 3, 0, 1, 2)
        self.spinBox_sections = QtGui.QSpinBox(self.groupBox_4)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.spinBox_sections.setPalette(palette)
        self.spinBox_sections.setMaximum(100000)
        self.spinBox_sections.setProperty("value", 10)
        self.spinBox_sections.setObjectName(_fromUtf8("spinBox_sections"))
        self.gridLayout_2.addWidget(self.spinBox_sections, 3, 2, 1, 1)
        self.label_umx_2 = QtGui.QLabel(self.groupBox_4)
        self.label_umx_2.setObjectName(_fromUtf8("label_umx_2"))
        self.gridLayout_2.addWidget(self.label_umx_2, 3, 4, 1, 1)
        self.checkBox_go = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox_go.setObjectName(_fromUtf8("checkBox_go"))
        self.gridLayout_2.addWidget(self.checkBox_go, 4, 0, 1, 4)
        self.doubleSpinBox_um = QtGui.QDoubleSpinBox(self.groupBox_4)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.doubleSpinBox_um.setPalette(palette)
        self.doubleSpinBox_um.setDecimals(3)
        self.doubleSpinBox_um.setMaximum(10000.0)
        self.doubleSpinBox_um.setSingleStep(0.1)
        self.doubleSpinBox_um.setProperty("value", 0.5)
        self.doubleSpinBox_um.setObjectName(_fromUtf8("doubleSpinBox_um"))
        self.gridLayout_2.addWidget(self.doubleSpinBox_um, 2, 2, 1, 2)
        self.checkBox_grab_um.raise_()
        self.label_lx.raise_()
        self.label_umx.raise_()
        self.doubleSpinBox_um.raise_()
        self.label_umx_2.raise_()
        self.checkBox_grab_sections.raise_()
        self.spinBox_sections.raise_()
        self.checkBox_go.raise_()
        self.gridLayout.addWidget(self.groupBox_4, 6, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.layoutWidget)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.checkBox_abox_placement = QtGui.QCheckBox(self.groupBox_3)
        self.checkBox_abox_placement.setGeometry(QtCore.QRect(40, 20, 211, 17))
        self.checkBox_abox_placement.setObjectName(_fromUtf8("checkBox_abox_placement"))
        self.checkBox_abox_placement.raise_()
        self.gridLayout.addWidget(self.groupBox_3, 4, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.layoutWidget)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.checkBox_SIFT = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_SIFT.setGeometry(QtCore.QRect(30, 20, 70, 17))
        self.checkBox_SIFT.setObjectName(_fromUtf8("checkBox_SIFT"))
        self.checkBox_Border_limits = QtGui.QCheckBox(self.groupBox_2)
        self.checkBox_Border_limits.setGeometry(QtCore.QRect(30, 50, 111, 17))
        self.checkBox_Border_limits.setObjectName(_fromUtf8("checkBox_Border_limits"))
        self.gridLayout.addWidget(self.groupBox_2, 3, 0, 1, 1)
        self.groupBox_5 = QtGui.QGroupBox(self.layoutWidget)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.widget = QtGui.QWidget(self.groupBox_5)
        self.widget.setGeometry(QtCore.QRect(40, 30, 132, 22))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.checkBox_black_after = QtGui.QCheckBox(self.widget)
        self.checkBox_black_after.setObjectName(_fromUtf8("checkBox_black_after"))
        self.horizontalLayout_3.addWidget(self.checkBox_black_after)
        self.doubleSpinBox_black_after = QtGui.QDoubleSpinBox(self.widget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 121, 64))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.doubleSpinBox_black_after.setPalette(palette)
        self.doubleSpinBox_black_after.setDecimals(1)
        self.doubleSpinBox_black_after.setMinimum(0.0)
        self.doubleSpinBox_black_after.setMaximum(100.0)
        self.doubleSpinBox_black_after.setProperty("value", 85.0)
        self.doubleSpinBox_black_after.setObjectName(_fromUtf8("doubleSpinBox_black_after"))
        self.horizontalLayout_3.addWidget(self.doubleSpinBox_black_after)
        self.label_umx_3 = QtGui.QLabel(self.widget)
        self.label_umx_3.setObjectName(_fromUtf8("label_umx_3"))
        self.horizontalLayout_3.addWidget(self.label_umx_3)
        self.gridLayout.addWidget(self.groupBox_5, 5, 0, 1, 1)
        self.widget1 = QtGui.QWidget(CLEMSite_Dialog)
        self.widget1.setGeometry(QtCore.QRect(30, 610, 421, 28))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.widget1)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.pushButton_Send = QtGui.QPushButton(self.widget1)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_Send.setFont(font)
        self.pushButton_Send.setDefault(False)
        self.pushButton_Send.setFlat(False)
        self.pushButton_Send.setObjectName(_fromUtf8("pushButton_Send"))
        self.horizontalLayout_2.addWidget(self.pushButton_Send)
        self.pushButton_Start = QtGui.QPushButton(self.widget1)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_Start.setFont(font)
        self.pushButton_Start.setDefault(False)
        self.pushButton_Start.setFlat(False)
        self.pushButton_Start.setObjectName(_fromUtf8("pushButton_Start"))
        self.horizontalLayout_2.addWidget(self.pushButton_Start)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.pushButton_Cancel = QtGui.QPushButton(self.widget1)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_Cancel.setFont(font)
        self.pushButton_Cancel.setDefault(False)
        self.pushButton_Cancel.setFlat(False)
        self.pushButton_Cancel.setObjectName(_fromUtf8("pushButton_Cancel"))
        self.horizontalLayout_4.addWidget(self.pushButton_Cancel)
        self.layoutWidget.raise_()
        self.layoutWidget.raise_()
        self.layoutWidget_8.raise_()
        self.pushButton_Cancel.raise_()

        self.retranslateUi(CLEMSite_Dialog)
        QtCore.QMetaObject.connectSlotsByName(CLEMSite_Dialog)

    def retranslateUi(self, CLEMSite_Dialog):
        CLEMSite_Dialog.setWindowTitle(_translate("CLEMSite_Dialog", "CLEMSite Control", None))
        self.pushButton_Connect.setText(_translate("CLEMSite_Dialog", "Connect ", None))
        self.pushButton_Disconnect.setText(_translate("CLEMSite_Dialog", "Disconnect", None))
        self.pushButton_SetupFile.setText(_translate("CLEMSite_Dialog", "Setup file", None))
        self.groupBox_4.setTitle(_translate("CLEMSite_Dialog", "Go! Button", None))
        self.label_lx.setText(_translate("CLEMSite_Dialog", "Monitoring frames:", None))
        self.checkBox_grab_um.setText(_translate("CLEMSite_Dialog", "Grab image every :", None))
        self.label_umx.setText(_translate("CLEMSite_Dialog", "??m", None))
        self.checkBox_grab_sections.setText(_translate("CLEMSite_Dialog", "Grab image every :", None))
        self.label_umx_2.setText(_translate("CLEMSite_Dialog", "sections", None))
        self.checkBox_go.setText(_translate("CLEMSite_Dialog", " GO!", None))
        self.groupBox_3.setTitle(_translate("CLEMSite_Dialog", "Autotune box", None))
        self.checkBox_abox_placement.setText(_translate("CLEMSite_Dialog", "Automatic placement of Autotune box", None))
        self.groupBox_2.setTitle(_translate("CLEMSite_Dialog", "Tracking", None))
        self.checkBox_SIFT.setText(_translate("CLEMSite_Dialog", "SIFT", None))
        self.checkBox_Border_limits.setText(_translate("CLEMSite_Dialog", "Top Border limits", None))
        self.groupBox_5.setTitle(_translate("CLEMSite_Dialog", "Stop if black cross section", None))
        self.checkBox_black_after.setText(_translate("CLEMSite_Dialog", " After :", None))
        self.label_umx_3.setText(_translate("CLEMSite_Dialog", "%", None))
        self.pushButton_Send.setText(_translate("CLEMSite_Dialog", "Send", None))
        self.pushButton_Start.setText(_translate("CLEMSite_Dialog", "Start", None))
        self.pushButton_Cancel.setText(_translate("CLEMSite_Dialog", "Cancel", None))

import resources_rc
