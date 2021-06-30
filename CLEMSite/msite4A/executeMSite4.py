# -*- coding: utf-8 -*-
"""
Created on Sat Jan 10 16:24:12 2015

@author: Jose Miguel Serra Lleti lleti@embl.de

Calls the main window and start execution

Use it as
    from execute import Msite
    Msite().run()
        
"""

#!/usr/bin/env python
# used to parse files more easily


from __future__ import with_statement

# for command-line arguments
import sys

# Python Qt4 bindings for GUI objects
from PyQt5 import QtGui
from PyQt5.QtWidgets import *

# import the MainWindow widget from the converted .ui files

from msite4Acq_app import MSite4Acq_app


# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

# for easy debugging comment this
#class Msite():
 
# and this:   
#    def run(self):    
        # create the GUI application
app = QApplication(sys.argv)

        # instantiate the main window
dmw = MSite4Acq_app()
        # show it
dmw.show()
        # start the Qt main loop execution, exiting from this script
        # with the same return code of Qt application
try:
    sys.exit(app.exec_())
except:
    print("__END__")
