# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 14:42:35 2015

@author: JMS
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 14:42:31 2015

@author: JMS
"""

import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure


class Window(QDialog):
    data = []
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.fig = Figure(figsize = (12,12), dpi=100)

        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button 
        # self.button = QtGui.QPushButton('Save error file')

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        # layout.addWidget(self.button)
        self.setLayout(layout)
        self.setWindowTitle('Show Error')

    def setErrorData(self,vMap):
        self.map = vMap

    def showGrid(self):
        self.plot()
        self.show()

    def plot(self):
        self.xlabels = self.map.grid_map.xlabels
        self.ylabels = self.map.grid_map.ylabels

        x = np.arange(len(self.xlabels))
        y = np.arange(len(self.ylabels))

        mpl.rc('font', serif='Helvetica Neue')
        mpl.rc('text', usetex='false')
        mpl.rcParams.update({'font.size': 20})
        mpl.rcParams['grid.linestyle'] = "-"
        ax = self.fig.add_subplot(111)
        # discards the old graph
        ax.set_title('Grid map retroprojection error',fontsize=12)
        list_error = []
        for el in self.map.list_errorDestiny.values():
            list_error.append(el[-1:])

        self.errorvals = np.full((len(self.ylabels), len(self.xlabels)),-1, dtype=np.float32)

        for el in list(self.map.grid_map.map_labels.keys()):
            if(el in list(self.map.list_errorDestiny.keys())):
                errors = self.map.list_errorDestiny[el]
                coord = self.map.grid_map.map_labels[el]
                coord = coord/10
                if(errors):
                    cerror = errors[-1:][0]
                    if(cerror<100):
                        self.errorvals[int(coord[1]),int(coord[0])] = cerror*1000

        # make a color map of fixed colors
        # cmap = mpl.colors.ListedColormap(['green','yellow','red','grey'])
        bounds= range(0,int(np.max(self.errorvals)),100)
         #norm = mpl.colors.BoundaryNorm(bounds, cm.coolwarm)
        # tell imshow about color map so that only set colors are used
        v_max = np.max(list_error)
        v_max = v_max*1000
        img = ax.imshow(self.errorvals,interpolation='nearest', cmap = cm.coolwarm) #, norm = LogNorm())
        # img = ax.imshow(self.errorvals, cmap = cm.coolwarm )
        # make a color bar
        ax2 = self.fig.add_axes([0.9, 0.025, 0.025, 0.9])

        cbar = self.fig.colorbar(img, cax=ax2, cmap=cm.coolwarm, boundaries=bounds, ticks=([0, v_max*0.25, v_max*0.5,v_max*0.75,v_max])) #, norm = LogNorm())
        cbar.ax.set_yticklabels(['0',str(v_max*0.00025), str(v_max*0.0005),str(v_max*0.00075),str(v_max*0.001)])
        cbar.set_label('Expected error', rotation=270)
        ax.grid(True,color='black',which='both')
        ax.set_xticks(x)
        ax.set_xticks(x+0.5)
        ax.set_yticks(y)
        ax.set_yticks(y+0.5)
        ax.get_xaxis().set_ticklabels([])
        ax.get_yaxis().set_ticklabels([])
        ax.grid(which='minor', alpha=0.8)
        ax.grid(which='major', alpha=0.8)

        ax.set_xlim([len(self.xlabels)/2-5,len(self.xlabels)/2+5])
        ax.set_ylim([len(self.ylabels)/2+5,len(self.ylabels)/2-5])

        # Draw quadrant coordinates (Number+Letter)
        for i in x:
            for j in y:
                ax.annotate(self.xlabels[i]+self.ylabels[j], (i-0.35, j+0.35),annotation_clip=True)


      #  ax2 = self.fig.add_subplot(212)
      #  ax2.hold(False)
      #  xl = np.arange(0,len(self.errorvals))
      # ax2.errorbar(x,self.data,yerr=self.data1,fmt='-o')
      #  ax2.get_xaxis().set_ticklabels(xl)
      #  ax2.set_title('Progression of retroprojection error',fontsize=10)

        self.canvas.draw()
    