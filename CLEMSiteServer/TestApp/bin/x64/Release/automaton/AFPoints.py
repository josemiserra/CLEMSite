from threading import Timer
from os import path
import os, sys
from shutil import copyfile
import numpy as np
import cv2
from datetime import datetime
from detectFocusPoints import detectPoints,writeErrorFile,preprocess
from imutils import blackBorderDetection, getPixelSize, getFiles

def executeAF(main_folder):
    """
    Automatic execution of autofocus
    - First, searches for slice Files with .tif
    - Reads the timestamp of the last one
    - Crops the blackBorder
    - Detects points for AFAS with nice features and generates positions file
    - removes the blocking file af.pid used to prevent execution of AF
    """
    try:
            # Get last slice file image path
            files = getFiles(main_folder,".*slice.*um.tif$")
            latest_file = max(files, key=os.path.getmtime)
            #time_files = [np.datetime64(datetime.fromtimestamp(os.path.getctime(file)), 'ms') for file in files]
            #ind =np.argsort(time_files)
            im_path = latest_file
            # Get last one in time
            _, slice_name = path.split(im_path)
            # Get slice name
            slice_name = slice_name[:-4]
            # crop it
            im_crop, _ = blackBorderDetection(im_path)
            pixelSize = getPixelSize(im_path,True)
            if (not detectPoints(im_crop, main_folder, "fp_" + slice_name, tpoints=3, pixelsize=pixelSize)):
                raise SystemExit
            # Remove PID
            files = getFiles(main_folder, ".*af.pid")
            for el in files:
                os.remove(el)
    except SystemExit:
            writeErrorFile("No points detected or unexpected ERROR", main_folder)
            return

    # Remove


if __name__ == "__main__":
    """
    This script executes the following workflow:
        1 - Checks if a file with AF positions exists
        2 - If exist, checks the creation timestamp in milliseconds
        3 - If the timestamp of the file is previous to the current AF time (given as parameter with timeAF)
            the files are moved to the f_data folder
        4 - Then a blocking file is generated af.pid. This will prevent from producing more AF position files.
        5 - A timer is scheduled to produce the AF positions just before the execution of the AF.
        6 - Unfortunately, there is no other way that leaving the thread on wait until the executeAF is executed
            so the process keeps the timer counting until the time arrives.
            
    """
    # prints python_script.py
    main_folder = sys.argv[3] # prints var1
    timeAF = np.datetime64(sys.argv[2]) # prints var2
    timeAF = np.datetime64(timeAF,'ms')
    e_AF = np.int64(sys.argv[1])
    # First check if AF point file has been already produced
    files = getFiles(main_folder, "fp_.*")
    if files:
        # check if its time is before the last AF, if that's the case, move it to af_folder
        time_creation = np.datetime64(datetime.fromtimestamp(os.path.getctime(files[0])), 'ms')
        # time_creation = timeAF - 15000
        if time_creation < timeAF:
            for el in files:
                _, filename = path.split(el)
                copyfile(el, main_folder + "\\f_data\\" + filename)
                os.remove(el)
    files = getFiles(main_folder, "fp_.*")
    if not files:
        # Create blocker
        with open(main_folder+"\\block_af.pid","w") as f:
            f.write("blocking at "+str(datetime.now))

        eAF_seconds = int(e_AF*1e-3)
        t = Timer(eAF_seconds,executeAF, [main_folder])
        t.start()
        activeWait = 1
        while activeWait:
            if t.isAlive():
             pass
            else:
             activeWait = 0
        t.cancel()




