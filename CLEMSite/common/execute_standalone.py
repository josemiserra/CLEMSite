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
from PyQt4 import QtGui


# import the MainWindow widget from the converted .ui files

from standalone_app import MSiteStandalone_app

# for easy debugging comment this
#class Msite():
 
# and this:   
#    def run(self):    
        # create the GUI application
app = QtGui.QApplication(sys.argv)

        # instantiate the main window
dmw = MSiteStandalone_app()
        # show it
dmw.show()
        # start the Qt main loop execution, exiting from this script
        # with the same return code of Qt application
sys.exit(app.exec_())
