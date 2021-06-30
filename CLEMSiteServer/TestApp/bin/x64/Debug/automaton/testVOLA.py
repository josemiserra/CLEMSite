
import focus_measures as fm
import pandas as pd
from matplotlib import pyplot as plt
from automaton_utils import getInfoFromA3DSetup, send_email
import cv2

def VOLAt(itest_folder,slice_name):
    email_folder = itest_folder+"\\email_data"
    df_new = pd.DataFrame.from_csv(itest_folder+"\\runcheck.csv")
    im_crop = cv2.imread(itest_folder+"\\no_border\\"+slice_name,0)
    vola_values = list(df_new['VOLA'])
    if fm.hasQualityDrop(vola_values[0:23], 5, 5, verbose = True):
        msg = 'Warning, quality in focus down. Check if Autofocus needed.'
        img_files = []
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.plot(df_new['VOLA'])
        plot_name = email_folder + "\\" + str(slice_name) + '_VOLA.png'
        fig.savefig(plot_name, bbox_inches='tight')
        plt.close(fig)
        img_files.append(plot_name)
        ####
        h, w = im_crop.shape
        r = 1.0
        if (h > 1024 and w > 1024):
            r = 1024.0 / w
            dim = (1024, int(h * r))
            # perform resizing to speed up
            rimg = cv2.resize(im_crop, dim, interpolation=cv2.INTER_AREA)
        else:
            rimg = im_crop.copy()

        img_name = email_folder + "\\" + slice_name + "_red.jpg"
        cv2.imwrite(img_name, rimg)
        img_files.append(img_name)
        send_email('serrajosemi@gmail.com', ['serrajosemi@gmail.com'],
               'FIB-SEM Message focus Dropdown at ' + str(slice), msg,
               files=img_files, server='smtp.gmail.com', username='serrajosemi', password='CHANchofante1982')
    else:
        print("Drop not accounted")



if __name__ == "__main__":
    test_folder= "D:\\GOLGI\\13_July_2018\\My_Project_December_II\\9P_47_FAM177B_X03--Y23_0047___0009_FOCUS_failed\\9P_47_FAM177B_X03--Y23_0047___0009__acq\\"
    test_image = "slicecell__00023_z=4.3432um.tif"
    VOLAt(test_folder,test_image)
