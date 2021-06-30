import os
from datetime import datetime
import numpy as np
import time, subprocess
from subprocess import PIPE

timeAF = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000) #
folder_store = "D:\\GOLGI\\PR_13Jun2017\\before_fixing\\s13JunTrial2\\4H_field--X03--Y08_0026___0004\\4H_field--X03--Y08_0026___0004__acq"

#values = "/C C:\\Users\\Schwab\\Anaconda3\\envs\\msite36\\python.exe C:\\Users\\Schwab\\Documents\\msite\\MSite4Aserver_shutdown\\automaton\\AFPoints.py 1000 "+str(timeAF)+" "+folder_store
values = "/C C:\\Users\\Schwab\\Anaconda3\\envs\\msite36\\python.exe C:\\Users\Schwab\Documents\msite\MSite4Aserver_shutdown\\automaton\\AFPoints.py 1828 2017-09-07T18:17:59.000 D:\\GOLGI\\PR_13Apr17_GOOD\Project13April\\9M_field--X00--Y23_0007--001___0001\\9M_field--X00--Y23_0007--001___0001__acq"
# measure wall time
CREATE_NEW_PROCESS_GROUP = 0x00000200
DETACHED_PROCESS = 0x00000008
t0 = time.time()
subprocess.Popen(["cmd.exe",values],stdin=PIPE, stdout=PIPE, stderr=PIPE,  creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
print(time.time() - t0, "seconds wall time")