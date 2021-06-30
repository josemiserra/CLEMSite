#!/usr/bin/env python

# GNU All-Permissive License
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

import sys
import os
import xml.dom.minidom


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class TextEdit(QMainWindow):

 def __init__(self, parent=None):
  super(TextEdit, self).__init__(parent)

  self.filename = ""
  self.saved = False
  self.Ui()

 def Ui(self):
  newFile = QAction('New', self)
  openFile = QAction('Open', self)
  saveFile = QAction('Save', self)
  quitApp = QAction('Quit', self)

  copyText = QAction('Copy', self)
  pasteText = QAction('Yank', self)

  newFile.setShortcut('Ctrl+N')
  newFile.triggered.connect(self.newFile)
  openFile.setShortcut('Ctrl+O')
  openFile.triggered.connect(self.openFile)
  saveFile.setShortcut('Ctrl+S')
  saveFile.triggered.connect(self.saveFile)
  quitApp.setShortcut('Ctrl+Q')
  quitApp.triggered.connect(self.close)
  copyText.setShortcut('Ctrl+K')
  copyText.triggered.connect(self.copyFunc)
  pasteText.setShortcut('Ctrl+Y')
  pasteText.triggered.connect(self.pasteFunc)

  menubar = self.menuBar()
  menubar.setNativeMenuBar(True)

  menuFile = menubar.addMenu('&File')
  menuFile.addAction(newFile)
  menuFile.addAction(openFile)
  menuFile.addAction(saveFile)
  menuFile.addAction(quitApp)

  menuEdit = menubar.addMenu('&Edit')
  menuEdit.addAction(copyText)
  menuEdit.addAction(pasteText)

  self.text = QTextEdit(self)
  self.setCentralWidget(self.text)
  self.setMenuWidget(menubar)
  self.setMenuBar(menubar)
  self.setGeometry(200,200,480,320)
  self.setWindowTitle('Text Information')
  self.functor = None

 def copyFunc(self):
  self.text.copy()

 def pasteFunc(self):
  self.text.paste()

 def attachCallback(self, func):
   self.functor = func

 def unSaved(self):
  modified = self.text.document().isModified()
  if modified:
   detour = QMessageBox.question(self,
       "Guey!",
       "File has unsaved changes. Save now?",
       QMessageBox.Yes|QMessageBox.No|
       QMessageBox.Cancel)
   if detour == QMessageBox.Yes:
    self.saveFile()
    return True
  return False

 def saveFile(self):
  self.saved = True
  if len(self.filename)==0:
   self.filename,_ = QFileDialog.getSaveFileName(self, 'Save File', os.path.expanduser('~'))
  else:
   with open(self.filename, 'w') as f:
        filedata = self.text.toPlainText()
        f.write(filedata)
   if self.functor is not None:
     self.functor()
   self.text.document().setModified(False)

 def newFile(self):
  if not self.unSaved():
   self.text.clear()

 def openFile(self, ifilename = None):

  if ifilename:
   self.filename = ifilename
   self.setWindowTitle(self.filename)
  else:
   self.filename, _ = QFileDialog.getOpenFileName(self, 'Open File', os.path.expanduser("~"))
   self.setWindowTitle(self.filename)

  with open(self.filename, 'r+') as f:
    filedata = f.read()
  self.text.clear()
  self.text.setText(filedata)


 def showImageInfo(self,info,info2):
   font = QFont("Arial", 14)
   self.setFont(font)
   xml_data =  xml.dom.minidom.parseString(info2[0])
   pretty_xml_as_string = xml_data.toprettyxml()
   my_data = ""
   for key,val in sorted(info.iteritems()):
     my_data= my_data+"\n -\t"+key+" :\t" +str(val)

   print(my_data)
   self.text.setText(my_data+"\n\n "+pretty_xml_as_string)

 def closeEvent(self, event):
  if self.unSaved():
   event.ignore()
  else:
   self.functor = None
   exit

def main():
 app = QApplication(sys.argv)
 editor = TextEdit()
 editor.show()
 sys.exit(app.exec_())

if __name__ == '__main__':
 main()