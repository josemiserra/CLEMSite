from xml.etree import ElementTree
import numpy as np

def getInfoFromA3DSetup(info_file):
    info_dict ={}
    with open(info_file, 'rt') as f:
        tree = ElementTree.parse(f)

    path = './Settings/Options/DefaultStabilizationDuration'
    node = tree.findall(path)
    info_dict['DefaultStabilizationDuration'] = int(node[0].text)

    path = './Settings/AutoTune/AF_Interval'
    node = tree.findall(path)
    info_dict['AF_Interval'] = int(node[0].text)

    path = './Settings/Imaging/FibicsRasterInfo/Dwell'
    node = tree.findall(path)
    info_dict['Dwell']= float(node[0].text)

    path = './Settings/Imaging/FibicsRasterInfo/LineAveraging'
    node = tree.findall(path)
    info_dict['LineAveraging'] = int(node[0].text)

    path = './SamplePreparation/ATLAS3DSamplePrepSettings/TrenchDepth'
    node = tree.findall(path)
    info_dict['TrenchDepth'] = float(node[0].text)

    path = './Settings/Imaging/FibicsRasterInfo/PixelSizeX'
    node = tree.findall(path)
    info_dict['PixelSize'] = float(node[0].text)

    path = './Settings/Imaging/Interval'
    node = tree.findall(path)
    info_dict['SliceThickness'] = float(node[0].text)

    path = './SamplePreparation/ATLAS3DSamplePrepShapes/MillShape/FIBShape/Nodes'
    nodes = tree.findall(path)
    node_list = []
    for el in nodes[0].iter():
        if (el.tag == 'Node'):
            node_list.append(el)

    X_val = []
    Y_val = []
    for el in node_list:
        for val in el.iter():
            if (val.tag == 'X'):
                X_val.append(val.text)
            if (val.tag == 'Y'):
                Y_val.append(val.text)

    X_val = np.array(X_val, dtype=np.float32)
    Y_val = np.array(Y_val, dtype=np.float32)
    info_dict['dX'] = np.sqrt((X_val[0] - X_val[1]) ** 2 + (Y_val[0] - Y_val[1]) ** 2)
    info_dict['dY']= np.sqrt((X_val[1] - X_val[2]) ** 2 + (Y_val[1] - Y_val[2]) ** 2)

    return info_dict