import sys
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from os import path


class TimedMessageBox(QMessageBox):
    message =""
    title = "WAIT"
    def __init__(self, parent=None, timeout=3, imessage=""):
        super(TimedMessageBox, self).__init__(parent)
        self.setWindowTitle(self.title)
        self.time_to_wait = timeout
        self.message = imessage
        self.setText(self.message+"\n Closing automatically in {0} seconds.".format(timeout))
        self.setStandardButtons(QMessageBox.NoButton)

        mpath = path.dirname(path.abspath(__file__))
        head,tail = path.split(mpath)
        self.setIconPixmap(QtGui.QPixmap(path.join(head, 'res\\clock.png')))
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

    def changeContent(self):
        self.setText(self.message+"\n Closing automatically in {0} seconds.".format(self.time_to_wait))
        self.time_to_wait -= 1
        if self.time_to_wait <= 0:
            self.close()

    def setMessage(self, imessage="", ititle="WAIT"):
        self.message = imessage
        self.title = ititle

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()


class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        btn = QPushButton('Button', self)
        btn.resize(btn.sizeHint())
        btn.move(50, 50)
        self.setWindowTitle('Example')
        btn.clicked.connect(self.warning)

    @pyqtSlot()
    def warning(self):
        messagebox = TimedMessageBox(self,5,"HELLO")
        messagebox.exec_()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()