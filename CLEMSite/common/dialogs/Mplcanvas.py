# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 12:14:20 2015

@author: JMS
"""
#!/usr/bin/env python

# Python Qt4 bindings for GUI objects

import math

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib import collections  as mc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from common.virtualGridMap import PointType, State


class MplCanvas(FigureCanvas):
    """
    Class to represent the FigureCanvas widget.

    """
    pickedx=np.array([])
    pickedy=np.array([])

    pickedIndNC = np.array([])
    pickedIndC = np.array([])
    pickedIndT = np.array([])
    pickedIndAcq = np.array([])
    pickedIndBlocked = np.array([])

    selectedx= []
    selectedy= [] 
    
    pickedId = []
    radius = []    
    scatters = []
    scatter_annotations = []

    circle = 0
    spacing = 10    
    angle = 0
    blocksize  = 40

    flip = False
        
    def __init__(self,ivMap=None):
        """
               Canvas initialization.
               The Figure canvas is given to matplotlib.
               
        """
        # setup Matplotlib Figure and Axis       
        #fig, ax1 = plt.subplots(1,1)
        plt.rc("figure", facecolor="white")
        self.fig = Figure(figsize=(50, 50), dpi=100)
        
        self.fig.frameon = False
        self.sp = self.fig.add_axes([0, 0, 1, 1])

        plt.rc('font', family='sans-serif') 
        plt.rc('font', serif='Helvetica Neue') 
        plt.rc('text', usetex='false') 
        plt.rcParams.update({'font.size': 18})

        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)
        self.vmap = None
        if ivMap is not None:
            self.setMap(ivMap)

        # rotate a bit for better orientation
        # tr_rotate = Affine2D().rotate_deg(-45, 0)


    def initialize_grid(self,space=10):
        self.spacing = space

        self.nlx = self.max_xticks
        self.nly = self.max_yticks

        self.annotations = []
        self.major_ticks_x = []
        self.major_ticks_y = []
        xticks = (self.max_xticks-1)* self.spacing # 16*10 = 160
        yticks = (self.max_yticks-1)* self.spacing
        
        self.img_limx = [0,xticks]        
        self.img_limy = [yticks,0]
        self.x = np.arange(xticks+1)
        self.y = np.arange(yticks+1)
        self.xv, self.yv= np.meshgrid(self.x,self.y)
        ctx = 0
        cty = 0
        for i in self.x:
            for j in self.y:
                if ((i%self.spacing==0) and (j%self.spacing==0)):
                    trd = np.float32([i,j,1.0])
                    self.major_ticks_x.append(round(trd[0]))
                    self.major_ticks_y.append(round(trd[1]))
                    cty=(cty+1)%self.max_yticks
            if(i%self.spacing==0):  
                ctx=(ctx+1)%self.max_xticks   

        self.sp.set_xlim((-5.0,self.blocksize))
        self.sp.set_ylim((self.blocksize,-5.0))

    def setMap(self,ivMap):
        if self.vmap is not None:
            del self.vmap
        self.vmap = ivMap
        self.colors_list = self.vmap.grid_map.colors_list
        self.spacing = self.vmap.grid_map.spacing
        self.blocksize = self.vmap.grid_map.blocksize
        self.max_xticks = self.vmap.grid_map.cols
        self.max_yticks = self.vmap.grid_map.rows
        self.picture_grid_folder = self.vmap.grid_map.template_picture
        self.initializeLook(0)

    def initializeLook(self,rotang):
        self.fig.delaxes(self.sp)
        self.sp = self.fig.add_axes([0, 0, 1, 1])
        self.angle = rotang
        self.img = plt.imread(self.picture_grid_folder)

        self.initialize_grid()

        self.grid_draw()


        if(self.flip):
            self.sp.invert_xaxis()
        self.redraw()

    def grid_draw(self,space = 10):
        """
            Refresh the canvas with the updated list of points
            
        """

        self.annotations = []
        self.sp.set_autoscale_on(False)

        lines = []        
   
        for i in np.arange(0,self.nlx):
            lines.append([(self.major_ticks_x[i*self.nly],self.major_ticks_y[i*self.nly]),(self.major_ticks_x[i*self.nly+self.nly-1],self.major_ticks_y[i*self.nly+self.nly-1])])

        for j in np.arange(0,self.nly):
            lines.append([(self.major_ticks_x[j],self.major_ticks_y[j]),(self.major_ticks_x[j+self.nly*(self.nlx-1)],self.major_ticks_y[j+self.nly*(self.nlx-1)])])  
        
        lc = mc.LineCollection(lines,color='0.1',alpha=0.2, linewidths=1)
        self.sp.add_collection(lc)
        self.sp.get_xaxis().set_ticklabels([])
        self.sp.get_yaxis().set_ticklabels([])

        self.scatter = self.sp.scatter(self.major_ticks_x,self.major_ticks_y, picker=10, s=2,  color='black',marker="o")

        self.sp.imshow(self.img, extent=[self.img_limx[0], self.img_limx[1], self.img_limy[0], self.img_limy[1]],aspect='auto')

    def update_from_Map(self):
        if(not self.vmap):
            return
        canvas_points,lm_points, point_ids = self.vmap.getAllLandmarkCoordinates()
        self.pickedx =np.array([],dtype=np.float32)
        self.pickedy =np.array([],dtype=np.float32)
        self.pickedIndNC = np.array([],dtype=int)
        self.pickedIndC = np.array([],dtype=int)
        self.pickedIndT = np.array([],dtype=int)
        self.pickedIndAcq = np.array([],dtype=int)
        self.pickedIndBlocked = np.array([], dtype=int)
        self.pickedId = []
        if(canvas_points.size<1):
            return
        i=0
        for el in canvas_points:
            if(el.size>0):
                self.pickedx = np.append(self.pickedx,el[0])
                self.pickedy = np.append(self.pickedy,el[1])
                self.pickedId.append(point_ids[i])
            i = i+1

        get_indices,_ = self.vmap.getTypeIndices()
        states, _ = self.vmap.getStateIndices()

        i = 0
        for el,st in zip(get_indices,states):
            if st == State.blocked:
                self.pickedIndBlocked = np.append(self.pickedIndBlocked, i)
                i = i+1
            elif(el== PointType.calibrated):
                self.pickedIndC = np.append(self.pickedIndC,i)
                i = i+1
            elif(el== PointType.non_calibrated):
                self.pickedIndNC = np.append(self.pickedIndNC,i)
                i = i+1
            elif(el== PointType.acquired):
                self.pickedIndAcq = np.append(self.pickedIndAcq,i)
                i = i+1
            elif(el == PointType.target):
                self.pickedIndT = np.append(self.pickedIndT,i)
                i = i+1
            else:
                i = i+1


        self.radius = self.vmap.getRadii(1) # canvas is map id 1
        return


    def redraw(self,update=True):
        # update data       
        if(update): 
            self.update_from_Map();
        # Draw the squares first with the tags

        if len(self.scatters)>0:
            for el in self.scatters:
                el.remove()
            for el in self.annotations:
                el.remove()

            self.scatters = []
            self.annotations = []

        scatter = self.sp.scatter(self.major_ticks_x, self.major_ticks_y, picker=10, s=2, color='black', marker="o")
        self.scatters.append(scatter)

        plt.rcParams.update({'font.size': 10})
        if(self.pickedIndNC.size>0):     
            scatter = self.sp.scatter(self.pickedx[self.pickedIndNC],self.pickedy[self.pickedIndNC], s=80, alpha=0.5, color = self.colors_list[0])
            self.scatters.append(scatter)
            for i in range(len(self.pickedIndNC)):
                self.annotations.append(self.sp.annotate(self.pickedId[self.pickedIndNC[i]],(self.pickedx[self.pickedIndNC[i]],self.pickedy[self.pickedIndNC[i]]),color = self.colors_list[0]))
        if(self.pickedIndC.size>0):
            scatter = self.sp.scatter(self.pickedx[self.pickedIndC],self.pickedy[self.pickedIndC], s=80, alpha=0.5, color = self.colors_list[1])
            self.scatters.append(scatter)
            for i in range(len(self.pickedIndC)):
                self.annotations.append(self.sp.annotate(self.pickedId[self.pickedIndC[i]],(self.pickedx[self.pickedIndC[i]],self.pickedy[self.pickedIndC[i]]),color = self.colors_list[1]))

        if(self.pickedIndT.size>0):
            tarea = np.pi * (15) ** 2
            scatter = self.sp.scatter(self.pickedx[self.pickedIndT],self.pickedy[self.pickedIndT], s=tarea, alpha=0.5, color = self.colors_list[2])
            self.scatters.append(scatter)
            for i in range(len(self.pickedIndT)):
                indx = self.pickedIndT[i]
                pid = self.pickedId[indx]
                xc = self.pickedx[indx]
                yc = self.pickedy[indx]
                self.annotations.append(self.sp.annotate(pid,(xc,yc),color = self.colors_list[2]))
        if(self.pickedIndAcq.size>0):
            scatter = self.sp.scatter(self.pickedx[self.pickedIndAcq],self.pickedy[self.pickedIndAcq], s=80, alpha=0.5, color = self.colors_list[3])
            self.scatters.append(scatter)
            for i in range(len(self.pickedIndAcq)):
                indx = self.pickedIndAcq[i]
                pid = self.pickedId[indx]
                xc = self.pickedx[indx]
                yc = self.pickedy[indx]
                self.annotations.append(self.sp.annotate(pid,(xc,yc),color = self.colors_list[3]))
        if(self.selectedx):
            scatter = self.sp.scatter(self.selectedx[-1],self.selectedy[-1], s=1500, alpha=0.75, color ='skyblue',marker = "*")
            self.scatters.append(scatter)

        if(self.pickedIndBlocked.size>0):
            area = np.pi * (20) ** 2  # 15 point radii
            scatter = self.sp.scatter(self.pickedx[self.pickedIndBlocked], self.pickedy[self.pickedIndBlocked], s=area, alpha=0.5,
                            color=self.colors_list[4])
            self.scatters.append(scatter)
            for i in range(len(self.pickedIndBlocked)):
                indx = self.pickedIndBlocked[i]
                pid = self.pickedId[indx]
                xc = self.pickedx[indx]
                yc = self.pickedy[indx]
                self.annotations.append(self.sp.annotate(pid, (xc, yc), color=self.colors_list[4]))

        self.draw()
        plt.rcParams.update({'font.size': 18})
    
    
    def mirrorImage(self):
        self.flip = True
 


    def setFlip(self,flip):
        self.flip = flip

    def selectPoint(self,coord):
        """ 
            Given point coordinates, it selects the point from the corresponding list and
            it is highlighted. It doesn't redraw and focus in the point
        
        """
        self.selectedx = []
        self.selectedy = []
        if(np.any(np.array(coord))):
            if(self.angle== 270 or self.angle == 90):
                self.selectedx.append(coord[1])
                self.selectedy.append(coord[0])
            else:
                self.selectedx.append(coord[0])
                self.selectedy.append(coord[1]) 
    
    def setSelectedPoint(self,coord):
        """ 
            Given coordinates of a point, it selects the point from the corresponding list and
            it is highlighted. It draws a star and then focus in the exact place where the 
            the star is (it redraws the canvas)
        
        """
        self.selectedx = []
        self.selectedy = []

        self.selectedx.append(coord[0])
        self.selectedy.append(coord[1])
        
         # get the current x and y limits
        cur_xlim = self.sp.get_xlim()
        cur_ylim = self.sp.get_ylim()

        # set the range
        cur_xrange =  round(math.fabs(cur_xlim[1] - cur_xlim[0])*0.5)
        cur_yrange =  round(math.fabs(cur_ylim[1] - cur_ylim[0])*0.5)
        if(self.flip and self.angle!= 270):
            self.sp.set_xlim((coord[0]+cur_xrange,coord[0]-cur_xrange))
        else:
            self.sp.set_xlim((coord[0]-cur_xrange, coord[0]+cur_xrange))
        self.sp.set_ylim((coord[1]-cur_yrange, coord[1]+cur_yrange))
        if(self.angle != 180):
            self.sp.invert_yaxis()
        self.redraw()
                    
    @staticmethod
    def dist(x,y):   
            return np.sqrt(np.sum((x-y)**2))
    
    def clean(self):

        self.pickedx = np.array([])
        self.pickedy = np.array([])
        
        self.pickedIndC = np.array([])
        self.pickedIndNC = np.array([])
        self.pickedIndT = np.array([]) 
        self.pickedIndAcq = np.array([])
        self.pickedType = np.array([])
        self.pickedId = []
      
        self.selectedx = []
        self.selectedy = []

        self.redraw()
        
    def drawRadius(self,rad,ind):

        if(rad>0.0):
            if(rad<self.circle):
                mcolor = 'blue'
                malpha = 0.1
            else:
                mcolor = '#00FFFF'
                malpha = 0.075
            circ = plt.Circle((self.pickedx[ind],self.pickedy[ind]),rad,color=mcolor,alpha=malpha,ec='black')
            self.fig.gca().add_artist(circ)
            self.circle = rad;
            
        self.draw()
