#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLEMSite . This software was build for correlative microscopy using FIB SEM.
 
 Density map to find proximity between a cloud of 2D points.

# @Title			: Map
# @Project			: CLEMSite
# @Description		: Software for correlation 
# @Author			: Jose Miguel Serra Lleti
# @Email			: lleti (at) embl.de
# @Copyright		: Copyright (C) 2018 Jose Miguel Serra Lleti
# @License			: MIT Licence
# @Developer		: Jose Miguel Serra Lleti
# 					  EMBL, Cell Biology and Biophysics
# 					  Department of Molecular Structural Biology
# @Date				: 2020/03
# @Version			: 1.2
# @Python_version	: 3.6

 Source: http://stackoverflow.com/questions/6652671/efficient-method-of-calculating-density-of-irregularly-spaced-points
 
 Example of usage:
    x = np.random.uniform(40, 60, 50)
    y = np.random.uniform(40, 60, 50)
    my_map = DensityMap(x,y)
    z = my_map.compute_density()
    my_map.plot_density_map(z)
    pt,vec = my_map.obtainMostDensePoint(z)
"""
# ======================================================================================================================

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LogNorm
import numpy as np
# from matplotlib.mlab import griddata
# import math
from scipy.spatial import KDTree
# import time
import scipy.ndimage as ndi
from scipy.spatial.distance import pdist
import itertools
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class DensityMap(QDialog):
    hasData = False
    def __init__(self,parent=None):
        super(DensityMap, self).__init__(parent)

        self.fig = Figure(figsize=(12, 12), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        # layout.addWidget(self.button)
        self.setLayout(layout)
        self.setWindowTitle('Show Density')
        self.hasData = False


    def set_data(self,x,y):
        x   = [ str(el).replace('.','') for el in x]
        y   = [ str(el).replace('.','') for el in y]
        x   = [ float(el[:2]+'.'+el[2:]) for el in x]
        y   = [ float(el[:2]+'.'+el[2:]) for el in y]
        self.x = np.array(x,dtype=np.float32)
        self.y = np.array(y,dtype=np.float32)
        self.list_points = []
        self.hasData = True

    def grid_density_gaussian_filter(self,x0, y0, x1, y1, w, h, data):
        kx = (w - 1) / (x1 - x0)
        ky = (h - 1) / (y1 - y0)
        r = 20
        border = r
        imgw = (w + 2 * border)
        imgh = (h + 2 * border)
        img = np.zeros((imgh,imgw))
        for x, y in data:
            ix = int((x - x0) * kx) + border
            iy = int((y - y0) * ky) + border
            if 0 <= ix < imgw and 0 <= iy < imgh:
                img[iy][ix] += 1
        return ndi.gaussian_filter(img, (r,r))  ## gaussian convolution

    def boxsum(self,img, w, h, r):
        st = [0] * (w+1) * (h+1)
        for x in range(w):
            st[x+1] = st[x] + img[x]
        for y in range(h):
            st[(y+1)*(w+1)] = st[y*(w+1)] + img[y*w]
            for x in range(w):
                st[(y+1)*(w+1)+(x+1)] = st[(y+1)*(w+1)+x] + st[y*(w+1)+(x+1)] - st[y*(w+1)+x] + img[y*w+x]
        for y in range(h):
            y0 = max(0, y - r)
            y1 = min(h, y + r + 1)
            for x in range(w):
                x0 = max(0, x - r)
                x1 = min(w, x + r + 1)
                img[y*w+x] = st[y0*(w+1)+x0] + st[y1*(w+1)+x1] - st[y1*(w+1)+x0] - st[y0*(w+1)+x1]

    def grid_density_boxsum(self,x0_d,y0_d,r, w, h, data):
        border = r * 2
        imgw = (w + 2 * border)
        imgh = (h + 2 * border)
        img = [0] * (imgw * imgh)

        for x, y in data:
            ix = int(x - x0_d) + border
            iy = int(y - y0_d) + border
            if 0 <= ix < imgw and 0 <= iy < imgh:
               img[iy * imgw + ix] += 1
               self.list_points.append(np.array([ix-border,iy-border],dtype=np.int64))

        for p in range(4):
            self.boxsum(img, imgw, imgh, r)
        a = np.array(img).reshape(imgh,imgw)
        b = a[border:(border+h),border:(border+w)]
        return b


    def plot_density_map(self,zd,tags):
        # TODO: check if we pass only valid cells
        self.show()
        # Calculate distance matrix
        distances = pdist(list(zip(self.x,self.y)))
        minv = np.min(distances)
        maxv = np.max(distances)

        mv = (minv/maxv)
        # data points range
        data_ymin =  np.min(self.y)-minv*2
        data_ymax =  np.max(self.y)+minv*2
        data_xmin =  np.min(self.x)-minv*2
        data_xmax =  np.max(self.x)+minv*2


        ax = self.fig.add_subplot(111)
        ax.scatter(self.x, self.y, color='violet')

        for ind,el in enumerate(tags):
            ax.annotate(el, (self.x[ind] - 0.01, self.y[ind] + 0.01), annotation_clip=True)

        mdp, vec = self.obtainMostDensePoint(zd)
        ax.scatter(mdp[0],mdp[1],color='black')

       # for el in self.list_points:
       #     plt.scatter(el[0], el[1], color='violet')
       # plt.scatter(vec[0],vec[1],color='black')
        ax.imshow(zd, extent=(data_xmin, data_xmax, data_ymax, data_ymin), cmap=cm.jet)
        # plt.imshow(zd,cmap = cm.jet)
        # plt.colorbar()

        self.canvas.draw()


    def compute_density(self,factor=10):
        """
        The factor depends on your data and how
        the density needs to be evaluated.
        """
        x = self.x*factor
        y = self.y*factor
        m_combos = list(itertools.combinations(range(len(x)),2))
        # Calculate distance matrix
        distances = pdist(list(zip(x,y)))
        minv = np.min(distances)
        medv = np.median(distances)
        maxv = np.max(distances)
        mv = (medv/maxv)
        # data points range
        data_ymin =  np.min(y)-minv*2
        data_ymax =  np.max(y)+minv*2
        data_xmin =  np.min(x)-minv*2
        data_xmax =  np.max(x)+minv*2

        m_y = abs(data_ymax - data_ymin)
        m_x = abs(data_xmax - data_xmin)

        zd = self.grid_density_boxsum(data_xmin,data_ymin,8, int(m_x),int(m_y), zip(x, y))
        return zd

    def obtainMax(self,zd):
        ind_max = np.argmax(zd)
        ind_mat = np.unravel_index(ind_max,zd.shape)
        return ind_mat

    def obtainMostDensePoint(self,zd):
        if zd.shape[0]<3:
            return (self.x[0],self.y[0]),0
        ind_max = np.argmax(zd)
        ind_mat = np.unravel_index(ind_max,zd.shape)
        distance,m_dind = self.find_nearest(self.list_points,np.array([ind_mat[1],ind_mat[0]]))
        return (self.x[m_dind],self.y[m_dind]),m_dind

    def find_nearest(self,a,pt):
        distance,index = KDTree(a).query(pt)
        return distance,index

    def computeDensityList(self,m_list_px, m_list_py, factor = 10):

        self.set_data(m_list_px,m_list_py)
        zd = self.compute_density(factor)
        pt, ind_pt = self.obtainMostDensePoint(zd)

        m_list_non_computed = list(range(len(m_list_px)))
        m_list_computed = []
        m_list_computed.append(ind_pt)
        m_list_non_computed.remove(ind_pt)

        m_apx = np.array(m_list_px, dtype=np.float32)
        m_apy = np.array(m_list_py, dtype=np.float32)

        while (len(m_list_non_computed) > 0):
            m_ncpx = np.array(m_apx[m_list_non_computed], dtype=np.float32)
            m_ncpy = np.array(m_apy[m_list_non_computed], dtype=np.float32)
            nc_list = list(zip(m_ncpx, m_ncpy))
            m_cpx = np.array(m_apx[m_list_computed], dtype=np.float32)
            m_cpy = np.array(m_apy[m_list_computed], dtype=np.float32)
            c_list = list(zip(m_cpx, m_cpy))
            distances, indices = KDTree(nc_list).query(c_list)
            ind_min = np.argmin(distances)
            ind_ncpt = indices[ind_min]
            ind_pt = m_list_non_computed[ind_ncpt]
            # add it to the computed
            m_list_computed.append(ind_pt)
            # remove it from the non_computed
            m_list_non_computed.remove(ind_pt)
        return m_list_computed








