# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 09:20:45 2015

@author: JMS
"""
from abc import ABCMeta, abstractmethod

import json
import decimal
import socket


import numpy as np
class MicroAdapter(object):
    """
    Abstract class used to comunicate with microscope.
 
    Acts a simple adapter
    """
    __metaclass__ = ABCMeta

    connected = False    
    
    @abstractmethod    
    def connect(self):
        pass

    @abstractmethod    
    def disconnect(self):
        pass

    @abstractmethod        
    def changeIpLocal(self):
        pass    
    
    @abstractmethod        
    def getIpLocal(self):
        pass
    
    @abstractmethod    
    def changePort(self,o_port):
        pass
    
    @abstractmethod 
    def changeIp(self,o_iplm):
        pass     
    @abstractmethod
    def getCurrentStagePosition(self):
        pass
    
    @abstractmethod
    def setStageXYPosition(self,coord):
        pass
    
    def setScale(self,scale,scale_inv):
        self.scale = scale
        self.scale_inv = scale_inv
    
    @abstractmethod
    def grabImage(self,name):
        pass
    
    @abstractmethod
    def setDirImages(self,path):
        pass
    

############################################################################
#   Implement adapters
################################################33

class MicroAdapterSEM(MicroAdapter):
    """
    Adapter class for SEM microscope
    
    """
  
    iplocal = "127.0.0.1"
    ipSEM = "10.11.28.223"
    port = 8095


    def __init__(self, parent = None):
        self.currentIP = self.iplocal
        self.address = "http://"+str(self.currentIP)+":"+str(self.port)+"/"

    def changeIp(self,o_iplm):
        self.currentIP = o_iplm
        self.address = "http://"+str(self.currentIP)+":"+str(self.port)+"/"

    def changeIpLocal(self):
        self.currentIP = self.iplocal
        self.address = "http://"+str(self.currentIP)+":"+str(self.port)+"/"

    def getIpLocal(self):
        return self.iplocal

    def getIpSEM(self):
        return self.ipSEM

    def changeIpSEM(self):
        self.currentIP = self.ipSEM
        self.address = "http://"+self.currentIP+":"+str(self.port)+"/"

    def changePort(self,o_port):
        self.port = o_port
        self.address = "http://"+self.currentIP+":"+str(self.port)+"/"

    def sendMessage(self,message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        answer = ""
        try:
            client_socket.connect((self.currentIP, int(self.port)))
            client_socket.sendall(message)
            # now we reply
            answer = client_socket.recv(1024)
        except socket.error as msg:
            print(msg)
            print("Error sending message:"+message)
        client_socket.close()
        return answer

    def connect(self):
        # establish communication to microscope
        ####################################<<<<<<<<<<<<<<<<
        self.connected = True
        print("Checking if microscope is alive.")
        data = ""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.currentIP, int(self.port)))
            client_socket.sendall("{hi,Phoebe!}");
            data = client_socket.recv(64);
        except socket.error as msg:
            print(msg)
            print("Microscope is dead")
        client_socket.close()
        print(data)

    def disconnect(self):
        self.connected = False
        print("Killing connections (if any).")

    def getCurrentStagePosition(self):
        payload = {'function':'getStagePositionXYZ'}
        ans = self.sendMessage(str(payload))
        jcoord = json.loads(ans)
        coord = [0,0,0]
        coord[0] = float(jcoord['xpos'].replace(',','.'))
        coord[1] = float(jcoord['ypos'].replace(',','.'))
        coord[2] = float(jcoord['zpos'].replace(',','.'))
        coord = np.array(coord)
        return coord

    def setStageXYPosition(self,coord):
        coord = coord
        payload = {'function':'setStagePositionXY','xpos':coord[0],'ypos':coord[1]}
        ans = self.sendMessage(str(payload))
        error = json.loads(ans)['error']
        print(error)
        return error

    def grabImage(self,name):
        payload = { 'function':'grabFrame', 'frame_name':name}
        ans = self.sendMessage(str(payload))
        error = json.loads(ans)['error']
        print(error)
        return error

    def setDirImages(self,path):
        payload = {'function':'setDirFrames','dir':path}
        ans = self.sendMessage(str(payload))
        error = json.loads(ans)['error']
        print(error)

class MicroAdapterSEMTest(MicroAdapter):
    """
    Adapter class for testing

    """
    i = -1
#    coord_sem = np.array([[ 0.06555400085,  0.09088700104,0.0],
#       [ 0.06850099945,  0.09370700073, 0.0],
#       [ 0.07144499969,  0.09618000031, 0.0],
#       [ 0.07382700348,  0.09366100311, 0.0],
#       [ 0.07389199829,  0.09199199677, 0.0],
#       [ 0.06846299744,  0.0859980011, 0.0 ],
#       [ 0.06510500336,  0.09777600098, 0.0],
#       [ 0.06588999939,  0.09107299805, 0.0],
#       [ 0.06470400238,  0.09008399963, 0.0],
#       [ 0.06595500183,  0.09033899689, 0.0],
#       [ 0.06631199646,  0.09064600372, 0.0],
#       [ 0.06553199768,  0.08980899811, 0.0],
#       [ 0.06541100311,  0.09230699921, 0.0]], dtype=np.float32)

    coord_sem = np.array([[68944,90243,0.0], # 3O  #3R
    [68964,90854,0.0], # 4O #4R
    [68372,90864,0.0], # 4P   #4S
    [68357,90253,0], # 3P   #3S
    [68992,92069,0.0], # 6O
    [68415,92677,0.0], # 7P
    [67193,90875,0.0], # 4R
    [67233,926930,0.0], #7R
    [69670,95642,0.0], # cN
    [73128,91927,0.0], # 6H
    [72586,93760,0.0], # 9I
    [73824,96054,0.0], # dG
    [71892,89540,0.0] ], dtype=np.float32) #2J

    iplocal = "127.0.0.1"
    ipSEM = "10.11.28.223"
    port = 8095
    i = -1
    
    def __init__(self, parent = None):    
        self.currentIP = self.iplocal
        self.address = "http://"+str(self.currentIP)+":"+str(self.port)+"/"  

    def changeIp(self,o_iplm):
        self.currentIP = o_iplm 
        self.address = "http://"+str(self.currentIP)+":"+str(self.port)+"/"  
                      
    def changeIpLocal(self):
        self.currentIP = self.iplocal         
        self.address = "http://"+str(self.currentIP)+":"+str(self.port)+"/"
    
    def getIpLocal(self):
        return self.iplocal
    
    def getIpSEM(self):
        return self.ipSEM 

    def changeIpSEM(self):
        self.currentIP = self.ipSEM 
        self.address = "http://"+self.currentIP+":"+str(self.port)+"/"
        
    def changePort(self,o_port):
        self.port = o_port
        self.address = "http://"+self.currentIP+":"+str(self.port)+"/"
         
    def sendMessage(self,message):
        print("Sent to microscope "+ message)
        return "{}"
        
    def connect(self):
        # establish communication to microscope
        ####################################<<<<<<<<<<<<<<<<
        print("Checking if microscope is alive.")
        print("Fake FIB/SEM alive.")
        self.connected = True
        error = ""
        message = "Connected"
        return error,message
    def disconnect(self):
        print("Killing connections (if any).")
        self.connected = False
        error=""
        message="Disconnected"
        return error,message
    def getCurrentStagePosition(self):    
        self.i = self.i + 1        
        if(self.i<len(self.coord_sem)):        
            coord = self.coord_sem[self.i]
        else:
            coord = ([0,0,0])
        coord = np.array(coord)
        error = ""
        return error,coord ## mm

    def setStageXYPosition(self,coord):
        coord = coord*1e-3 ## meters      
        payload = {'function':'setStagePositionXY','xpos':coord[0],'ypos':coord[1]}
        print(payload)
        error = ""
        return error,"{}"

    def is_connected(self):
        return True

    def  grabImage(self, dwelltime,pixelsize, resolution, lineaverage, scanrotation, grabPath, tag ,shared):
        error= ""
        imagename ="E:\\test\\testing_SEM_errors\\23\\23.tif"
        return error,imagename
    
    def setDirImages(self,path):
        ## TO DO
        return ""

