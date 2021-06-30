import csv
import glob
import os

import numpy as np

import common.MsiteHelper as msite_helper


def getCrossPoint(output_dir,c_name):
    directories = glob.glob(output_dir + '\*')
    xd = msite_helper.filterPick(directories, 'cross_det_.*'+str(c_name)+'.*')
    if (not xd):
        print ("Directory with files not found.")
        return
    xdir = directories[xd[0]]
    xfiles = glob.glob(xdir + '\*')
    x = msite_helper.filterPick(xfiles, '_fpoints.csv')
    if (not x):
        return

    pointsfile = xfiles[x[0]]
    p_coords =[0, 0]
    with open(pointsfile, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            p_coords[0] = float(row[0])
            if (p_coords[0] < 0):
                p_coords[0] = -p_coords[0]
            p_coords[1] = float(row[1])
            if (p_coords[1] < 0):
                p_coords[1] = -p_coords[1]
    return p_coords


def gather(xdir):

    xfiles = glob.glob(xdir + '\*')
    x = msite_helper.filterPick(xfiles, 'p.*')
    for el in x:
        my_edir = xfiles[el]
        if(os.path.isdir(my_edir)):
            # find calibration file
            in_files = glob.glob(my_edir + '\*')
            xd1 = msite_helper.filterPick(in_files, '_fcoordinates_calibrate.xml')
            if( not xd1):
                continue
            file_calibrate_coords = in_files[xd1[0]]
            ## Read points
            datasem, tags, datamap = msite_helper.readXML(file_calibrate_coords )
            # read tags
            datasem_purged = np.zeros((4,2))
            for ind,elt in enumerate(tags):
                new_point = getCrossPoint(my_edir, elt)
                if (new_point[0] > 0.0):
                    # Substitute coordinates
                    datasem_purged[ind,:] = new_point
                else:
                    datasem_purged[ind,:] = [-1, -1]
            datasem_aux = list(datasem_purged)
            datamap_aux = list(datamap)
            tags_aux = list(tags)
            for ind, el in enumerate(datasem):
                if (el[0] == -1):  # and el[1] = -1
                    datasem_aux.remove(el)
                    datamap_aux.remove(datamap[ind])
                    tags_aux.remove(tags[ind])
            datasem_purged = datasem_aux
            datamap = datamap_aux
            tags = tags_aux
            file_calibrate_coords = file_calibrate_coords[:-4]+"_2.xml"
            msite_helper.saveXML(file_calibrate_coords, tags, datasem_purged, datamap)
            print "Saving :"+file_calibrate_coords
    return


mdir = "E:\\test\\"

gather(mdir)