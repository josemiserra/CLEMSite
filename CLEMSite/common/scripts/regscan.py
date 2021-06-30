import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import glob
import re,json
import shutil

def findTiffs(foldname):
    flist = []
    tiff_list = []
    dirs = []
    dirs.append(foldname)
    while dirs:
        fname = dirs.pop()
        fname_tif = str(fname) + '\\*.tif*'
        flist = glob.glob(fname_tif)
        if not flist:
            newdirs = ([f for f in glob.glob(fname + '\\*') if os.path.isdir(f)])
            for el in newdirs:
                dirs.append(el)
        else:
            for el in flist:
                tiff_list.append(el)
    return tiff_list


def filterPick(myList, myString):
    pattern = re.compile(myString);
    indices = [i for i, x in enumerate(myList) if pattern.search(x)]
    return indices

def copyPrescanToHR(main_folder,separator = ","):
    # Folders renamed
    hres = main_folder + "\\hr"
    prescan = main_folder+"\\prescan"

    # csv-table selected cells from tischi's htm explorer
    # read the file and replace everything
    file_cells = main_folder + "\\selected_cells.csv"
    with open(file_cells, 'r') as myfile:
        data = myfile.read().replace('\"', '')
    with open(file_cells, 'w') as myfile:
        myfile.write(data)

    table  = pd.read_csv(file_cells,separator)



    flist_hres = os.listdir(hres)
    flist_prescan = os.listdir(prescan)

    list_copied = {}
    for i in range(len(flist_hres)):
        reg_exp = "X" + str(table.ix[i]["Metadata_X"]).zfill(2)+"--"+ "Y" + str(table.ix[i]["Metadata_Y"]).zfill(2)
        # find folder

        ind = filterPick(flist_prescan, reg_exp)
        if not ind:
            print("Prescan files not found.")
            return
        prescan_folder_s = prescan + "\\"+flist_prescan[ind[0]];
        ind = filterPick(flist_hres, reg_exp)
        if(len(ind)>0):
            i=0
            file_not_found = True
            while(i<len(ind) and file_not_found):
                hres_s = hres + "\\"+flist_hres[ind[i]];
                if(hres_s in list_copied.keys()):
                    i=i+1
                else:
                    file_not_found = False
            if (prescan_folder_s):
                alltifs = findTiffs(prescan_folder_s)
                for el in alltifs:
                    shutil.copy2(el, hres_s)
                    print("Copying "+el+" to :"+hres_s)
                list_copied[hres_s]=prescan_folder_s


def savePrescanShift(main_folder,saving_folder, separator = ",",organ_name="organelle"):
    file_cells = main_folder + "\\selected_cells.csv"
    table = pd.read_csv(file_cells,separator)
    # as a shorthand, extract some columns from the data frame and give
    # them a convenient name
    loc_center = pd.DataFrame(table, columns=["Location_Center_X", "Location_Center_Y"])
    loc_golgi_mean = pd.DataFrame(table, columns=["Mean_Golgi_AreaShape_Center_X", "Mean_Golgi_AreaShape_Center_Y"])
    samples=[]
    for i in range(loc_center.shape[0]):
        samples.append("X" + str(table.ix[i]["Metadata_X"]).zfill(2) + "--" + "Y" + str(table.ix[i]["Metadata_Y"]).zfill(2)+"_"+str(i).zfill(4))

    indices = pd.Index(samples, dtype='object')
    loc_center = loc_center.set_index(indices)
    loc_golgi_mean  =loc_golgi_mean.set_index(indices)

    loc_center.to_json(saving_folder + '\\center.json')
    loc_golgi_mean.to_json(saving_folder+'\\center_'+organ_name+'.json')
    print("File center.json and center_"+organ_name+".json generated successfully.")


main_folder= "D:\\GOLGI\\15March_NOSPOTS_COPB1\\renamed"
copyPrescanToHR(main_folder, separator=",")
savePrescanShift(main_folder,main_folder, separator = ",", organ_name="golgi")


