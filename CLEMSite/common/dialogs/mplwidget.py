#!/usr/bin/env python

# Python Qt5 bindings for GUI objects

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from common.microadapterAtlas import *

# import the Qt5Agg FigureCanvas object, that binds Figure to
# Qt5Agg backend. It also inherits from QWidget
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from common.dialogs.Mplcanvas import *

# import matplotlib.pyplot as plt
import numpy as np


class Mode:
    """
    Modes are functionality indicators.
    For each mode, the Widget shows different behavior.
    This is useful when we want to perform different functionalities in the canvas
    E.g. Click on a point and delete it in deletion mode.
         Click on a point and move to it in navigation mode.
         
      - Navigation : moves around
      - Target : Allowed to acquire positions
      - Deletion : Allowed to delete positions
      - Passive : nothing, only shows
    """
    navigation = 0
    target = 1
    deletion = 2
    passive = 3
        

class MplWidget(QWidget):
    """
    MatPlotLib Widget for plotting a grid
    
    Acts as a behavioral interface between the Canvas and the GUI.
    All the microscope or GUI behaviour that affects the Canvas painting is 
    implemented here : moving, acquiring, deleting, correcting...
    
    Requires a virtual grid map, a microscope server and a logger to add information.
    The map is passed to the canvas (containing the information to be drawn).
    
    Starts in target mode.
    
    """

    # Define a new signal called 'trigger' that has no arguments to communicate back with the GUI
    triggerUpdate = pyqtSignal()
   
    mode = Mode.target
    
    def __init__(self,parent = None):
        # initialization of Qt MainWindow widget
        QWidget.__init__(self, parent)
        # set the canvas to the Matplotlib widget
        self.parent = parent
        self.canvas = MplCanvas()
        # create a vertical box layout
        self.vbl = QVBoxLayout()
        # add mpl widget to the vertical box
        self.vbl.addWidget(self.canvas)
        # set the layout to the vertical box
        self.setLayout(self.vbl)
        self.msc_server = None
        self.vMap = None
        self.canvas.setFocusPolicy( Qt.ClickFocus )
        self.canvas.setFocus()
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.parent)
        self.canvas.mpl_connect('button_press_event', self.onbutton)
    ## This two require to be initiliazed in order to work
    ## We don't force the constructor to split GUI from
    ## logic in the main application.
    ## An empty application can be created, without maps and connection
    def setMap(self,ivMap):
        if(self.vMap):
            del self.vMap
        self.vMap = ivMap
        self.canvas.setMap(ivMap)
       
    def setConnection(self,iserver, ilogger):
        self.msc_server = iserver
        self.logger = ilogger

    def getMode(self):
        return self.mode
    
    def setMode(self,mode):
        self.mode = mode

    ######################################################
    #
    ######################################################
    def acquirePoint(self,coord_canvas=[]):   
        """
            EVENT: When user decides to acquire a point that finds interesting and he wants to add
            it to the map.
            
            1) check connection to microscope
            2) get coordinate
            3) store it in map
            4) update canvas
            
            Note : triggerUpdate sends back the signal to the GUI to update
        """
        if(self.msc_server):
            if(self.msc_server.connected):
                error,coordacq = self.msc_server.getCurrentStagePosition()
            else:
                self.logger.info("No connected to microscope. Connect and try again.")
                return
        else:
            self.logger.info("Microscope server doesn't exist. Connect first.")
            return

        if(np.any(np.array(coord_canvas))):
            point_id = self.vMap.addPoint(coord_canvas,coordacq,'ACQUIRED',None)
        else:
            point_id = self.vMap.addPoint(None,coordacq,'ACQUIRED',None)
        coord = self.vMap.getLandmark(point_id,2)  # 1 for origin, 2 for destiny

        if(coord[0]==-np.inf):
            self.logger.info("Coordinates to be updated!")
        self.logger.info("Adding point: ")
        cx = round(coord[0])
        cy = round(coord[1])
        self.logger.info("["+ str(cx)+","+str(cy)+"]" )

        coord_canvas = self.vMap.getLandmark(point_id,1)
        self.canvas.redraw()
     #   self.canvas.setSelectedPoint(coord_canvas)       
        self.triggerUpdate.emit()
        return (coordacq,coord_canvas,point_id)
       
       
######################################################
    def correctPoint(self,point_id):
        """
            Given a point_id, gets the current stage position and it replaces it
            Remember that maps are done by landmarks. A landmark is defined by 
            ID + coordinates. However it is possible for one ID to store a set of coordinates
            to assess the uncertainty of the landmark.
            That is why we use updateLastLandmark
            
        """
        point_id = str(point_id)
        if(self.msc_server):
            if(self.msc_server.connected):
                error,new_coordacq = self.msc_server.getCurrentStagePosition()
            else:
                self.logger.info("No connected to microscope. Connect and try again.")
                return  
        else:
            self.logger.info("Microscope server doesn't exist. Connect first.")
            return
        
        self.vMap.updateLastLandmark([],new_coordacq,point_id, protect=True)
        coord = self.vMap.getLandmark(point_id,1)
        self.logger.info("Correcting point: ")
        cx = round(coord[0])
        cy = round(coord[1])
        self.logger.info("["+ str(cx)+","+str(cy)+"]")
        
        self.canvas.setSelectedPoint(coord)
        self.triggerUpdate.emit()
        return new_coordacq

######################################################
    def moveToPosition(self,coord_canvas):
        """
        Moves to a given position
        
        :param coord_canvas: 
        :return: 
        """

        if(not self.vMap.ready()):
            self.logger.info("Not enough calibration points to predict.")
            return
        coord = self.vMap.point_to_Destiny([coord_canvas[0],coord_canvas[1]])
        self.logger.info("Going to coordinate: ")
        cx = coord[0]
        cy = coord[1]
        if(cx==-np.inf or cy == -np.inf):
            self.logger.info("Cannot move, bad coordinates.")
            self.logger.info("[" + str(cx) + "," + str(cy) + "]")
            return

        self.logger.info("["+ str(cx)+","+str(cy)+"]")
        self.canvas.setSelectedPoint(coord_canvas)      
        self.msc_server.setStageXYPosition(coord)

    def moveToPoint(self, point_id):
        """
        Moves to a point given an id
        :param point_id: Landmark ID
        :return: 
        """
        coordStage = self.vMap.getPoint(point_id, 1)
        coordCanvas = self.vMap.getPoint(point_id, 2)

        if (self.msc_server):
            if (self.msc_server.connected):
                self.msc_server.setStageXYPosition(coordStage)
            else:
                self.logger.info("No connected to microscope. Connect and try again.")
                return
        else:
            self.logger.info("Microscope server doesn't exist. Connect first.")
            return

        self.logger.info('Moving to ' + point_id)
        self.logger.info(coordStage)

        self.canvas.setSelectedPoint(coordCanvas)


class MplWidgetSEM(MplWidget):
    """
    MatPlotLib Widget for plotting a grid in a SEM microscope (CLEM)
       In vMap Origin is SEM
               Destiny is Canvas
    """
    triggerDelete = pyqtSignal(str)
    triggerAddCalibration = pyqtSignal(str)
    
    def __init__(self,parent = None):
           super(MplWidgetSEM, self).__init__(parent)          
           self.canvas.mirrorImage()
           self.canvas.blocksize = 50


    #########################################################################    
    def getReference(self,point_id):
        """
            Add references to your map.
        
        :param point_id: ID of map without reference
        :return: New position of reference in SEM coordinates
        """
        point_id = str(point_id)
        error,coords_stage = self.msc_server.getCurrentStagePosition()
        coords_canvas = self.vMap.getLandmark(point_id,1)
        self.vMap.addPoint(coords_canvas,coords_stage,'CALIBRATED',point_id)
        self.logger.info("Reference point added to UI Map ")
        self.logger.info(str(coords_canvas))
        self.logger.info("Reference point added to Stage ")
        self.logger.info(coords_stage)
        self.logger.info("------------------------------------")
        self.canvas.setSelectedPoint(coords_canvas)
        return coords_stage
        
    def onbutton(self,event):

        if(self.msc_server==None):
            self.logger.info("No connection to microscope available.")
            return
        if(self.vMap==None):
            self.logger.info("No map available.")
            return
        if event.dblclick:
            if event.button == 3: # Move stage to grid position
            #transfer grid coordinate into stage coordinate using homography for clicked point, then move there
                if (event.inaxes is not None) and (self.msc_server.connected):
                    self.moveToPosition([event.xdata,event.ydata])
       
