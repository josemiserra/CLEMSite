## 2. CLEMSite-LM

In the following section we are describing how the LM images have been adapted for a specific experiment. For images from other microscopes this might be different and would require adaptation. Some of these tools can be used for general purposes like the renaming tool.

#### 2.1   Renaming light microscopy images

A complex example of renaming images  is the one we used in the Leica SP5 microscope pipeline. 

1) Create the following folders: 

A project folder (e.g. my_cells_project_29_Jan_2089). Then inside create:

​			o  A folder called **prescan**, which will contain the images used for the software to find the selected phenotypes.

​			o  A folder called **hr** (high resolution) which will contain the rest of images (Z stack, channel for organelle, nucleus, spots, transmitted light and reflected light).

**THE STRUCTURE MUST BE**   ```folder_project\\renamed\\prescan]``` and  ```folderr_project\\renamed\\hr```. 

**DO NOT REPLACE THE NAMES** because the *regscan.py* script will searches for the directory named **renamed** .



2) Copy the .csv file containing all the information from the scans (usually in a file called *selected_cells.csv*) inside the folder *.\\renamed*. This file was produced using a Jupyter Notebook (https://github.com/josemiserra/CLEMSite_notebooks  notebook _6_feedback_light_microscopy_phenotypes_)

![img](.\imgs\clip_image002.gif)

 

3)  Now search the folder with the images stored during your microscopy acquisition. Following our feedback microscopy, there were to acquisitions, one for prescan, where all images were shown and another for high resolution jobs, where specific cell where found:



![img](.\imgs\clip_image004.gif)**



4) Open CLEM*Site » I have a LM dataset* and move to **Settings** *»* **Rename LM files**.

![img](.\imgs\clip_image008.gif)

The main goal of the Converter is to rename files from location A to location B (it's a glorified `cp` command). So the idea is, I want to name with this string, e.g."prescan--nucleus--LM--DAPI--10x--z0" all the images that match the regular expression ```.*J07.*C01.*```.    You have to give the origin folder where the regular expression will be searched, and the destination folder, where the images will be copied with the new name. 



The script will find all images having J07 and C01 in its name and it will rename it to the given name.

 You can save a profile if you plan to do this experiment multiple times (if the regular expression changes, the profile is a JSON text file that can be easily changed). You are free also to add more options to the Channel, Lens and Zoom Factor values, by modifying the _CLEMSite\msiteSEM\scripts_conv\converter.py_ . It is a one-script application and is independent of all the other scripts.

In *CLEMSite\msiteSEM\scripts_conv\converter_profiles* you will find more information about the Converter script.



5)  Rename the prescan files: the way to rename them is up to the user, but it is important to remember that prescan pictures must have the suffix prescan in front of them. The destiny folder must be [\\renamed\\prescan](about:blank) 

 Repeat for hr, again inside the renamed folder into hr. 

We need to end up with a replica of the other folders but completely renamed. 

![img](.\imgs\clip_image010.gif)



6)  In the final step prescan images have to be copied inside the **hr-folder**. This will allow later the registration script to work properly.  There is a script named `regscan.py`  in _CLEMSite\common\scripts_ .  The script will select folder names from the prescan, that match with the hr jobs. 

NOTICE: For the following execution is important to have some knowledge of python scripting. Open the script `regscan.py` and try to understand it. You will have to create a script adapted to your needs.

Import regscan.py into the folder where your original data is located. Then open an editor and change the variable main_folder. This has to be the folder that contains the "renamed" folders and the file *selected_cells.csv* :

```python
main_folder= "D:\\GOLGI\\PR_25Oct2016\\PR_04_25_10_16_GOLGI"
```

Now run

```python
regscan.copyPrescanToHR(main_folder)
```

7)  In addition, later we will have to provide a file with the center coordinates of your object of interest. This has to follow the following format:

The keywords Center_X and Center_Y followed by the folder name and the coordinates:

*Name, Location_Center_X, Location_Center_Y*

*X00--Y01_0000, 58089.0098315, 65621.3132022*

*X00--Y02_0001, 60913.38715734, 53894.93052948*

This information is inside the _selected_cells.csv_ file and has to be extracted and formatted. Similarly as before, execute:

```python
shift_folder = main_folder+”\\renamed"
Regscan.savePrescanShift(main_folder,shift_folder,separator=',', organ_name ="golgi")
```

At the end of execution, the folder *renamed* should contain two files, *center.json* and *center_golgi.json* , respectively for cell centers and golgi centers. 

TIP: check your separator (, or ;, can be indicated with the field separator="") or the syntax of your file.

 

#### 2.2 Getting ready for CLEMSite-LM

With all this preparations we are almost ready to execute CLEMSite-LM.  The conditions for using CLEMSite-LM in MatTek dishes are:

![image-20210613012807313](.\imgs\image-20210613012807313.png)

The folder naming has to be in the following format:

​		●   A general folder for the project which contains a set of folders, where each folder name contains the regular expression ```[0-9][0-9][0-9][0-9]```    (e.g. _0001, _0002 or even _0001—001, _0001—002).  Each one is one target sample.

​		●    Each folder contains a set of images in **.tif** format with stage coordinates in the metadata  X and Y  and reflected Light images  are named with the expression:  ```.*--RL.*```   . In the renaming step you likely had RL images and you used this prefix. 

Reflected light images metadata will be used as reference, which means that stage coordinates from the metadata of RL have to be parcentric with the stage coordinates of the metadata in fluorescence (in other words, they have to point to the same physical x,y position). 



#### 2.3 MSite2LM (CLEM*Site-*LM)

.

![image-20210624224416066](.\imgs\image-20210624224416066.png)





##### 2.3.1 Where to start

Click on **File > Load folder** or in the icon in **1** showing the folder.

●    Load your `project\renamed`

![image-20210624224811859](.\imgs\image-20210624224811859.png)

 Load your sample folder where the information of the LM images prescan and hr are.

![image-20210615130611499](.\imgs\image-202106151255111743.png)



Once the folder is selected the tree view  **3** and list view  **4**  display  all the target cell samples present the folder.  You will see all the rows in white. 

You can click on each cell of the list will make the folder corresponding to it open. In the folder tree view clicking on one image shows the image in a viewer. 

The usual follow up sequence is the following

- Click the button [All] computes landmarks from reflected light (RL) images inside the folder. It will take around 30-40 minutes. Once computed, they will turn green,  meaning the detection of the crossing has been successfully computed. Red means no crossings couldn’t be detected.
- Yellow rows means that some problem occurred in the detection. If that is so, explore the folder and if you are not satisfied with what you see (the lines look badly detected), click on the cross to remove the selected row from the computation. You can also click on [x] to delete the computation, and  [1] to repeat the computation again on that specific row, which works well in some occasions that the detection failed.

In summary:

●    **All icon:** Compute detection of landmarks for all folders (line detection and alphanumeric letter recognition).

●    **1 icon:** Select one folder and do detection in this folder (line detection and alphanumeric letter recognition).

●    **Dash icon:** If a cell is computed but you think something is wrong, maybe with the detection of landmarks, this will remove the cell from the final list.

●    **Cross icon:** If a cell is not wanted, all data will be removed.

![img](.\imgs\clip_image003.jpg)

#### 2.4 Image registration. When do I need to register images?

Imagine a cell of interest is imaged with a 10x dry objective, the cell is at the position 50, 50. However, changing to a 40x objective if the microscope objectives are not mechanically aligned (no parcentricity) , the same cell will show up at the position 55, 54 instead of 50,50. The position of the stage is the same, but the images are misaligned between objectives.

Your file of targets (computed with `regscan.py`) used the prescan data, but your stage position landmarks are going to be computed using the RL images with an objective lens different from the prescan.  That will mean that you will have a shift between your expected cell position and what you  will compute. Thus, you can use the script Compute registration shift to save a file that computes shifts between 2 types of images and then save this file. 

**If your images are  NOT aligned between objectives:** you have to register your prescan with your reference image (e.g. 20x prescan with 10x fluorescence for dapi channel):

- **Compute registration shift:** Shift between differently acquired images e.g. 10x and 40x objective can be computed.

  

###### Pay attention to the stage coordinates!!

NOTE: Unfortunately, each microscope brand uses a different coordinate system orientation (X and Y can be inverted). If you have the microscope stage position X and Y of the center image stored in the metadata and the pixel size (you can check your metadata loading it with bioformats in Fiji and ticking the option show metadata), then it is possible to easily program a script to compute the image coordinates in stage coordinates relative to the center of the image, or to modify the code inside CLEMSite-LM.



#### 2.5 The final output of CLEMSite-LM 

<img src=".\imgs\mfig4_4.png" alt="mfig4_4" style="zoom:80%;" />

Once you see that the computation is done (it will take around 20-30 minutes), click on **Settings:**

​	●   Use the option **Generate file of positions from metadata** and save the file (.csv)

​    ●    Use the option **Load file of positions** to load the corresponding positions file.

 If you computed a registration between objectives,  use the option **Load shift from a file**  where shift between images , computed previously, can be loaded.



Finally  the button [=>.] exports the results in .xml format. 

Have a look to the format. You don't need to use the CLEMSite-LM, you can mimic the output format to use it in the Navigator.

####   2.6 Other options

![image-20210624224701017](.\imgs\image-20210624224701017.png)

Optionally you can:

●    **Save log as**…: A log-file about the process can be saved at any defined location. 

●    **Preferences:** Shows a text file with all preferences concerning the grid features (size) and the line detection algorithm.

●    **Rename LM files:** Converter dialog is opened to rename LM images for further processing.

●    **Clear all computed data:** After processing LM images, all files can be cleared, if the full process needs to be redone (mainly used in the software development phase).

●    **Z projection from z stacks:** Performs maximum intensity projection to generate a 2D projection of the z-stack.

●    **Blend images:** Overlaying different images e.g. DAPI and GFP. This is done for all folders in the directory.

Other icons:

●    **4 black square icon:** Show map of positions of neighboring cells with regard to density on the surface (heat map). 

●    **Error plot icon:** The error of accuracy of the transformation is calculated and the size of the error of prediction is estimated.  



#### 2.7 Computation of acquisition order for targets

 The targets have to be sorted from more to less dense regions. This will be later related to the coincidence point and the initial focus conditions. When the microscope moves from one target to another, all initial parameters need to be adjusted accordingly, and it is better to jump to closer cells instead of moving to the bottom and the again to the top. When the next target is closer in space, parameters will have closer values and adjustments will be easier to set automatically. 

 The density is relative to the number of points per area. We consider a scale of 100 µm to compute density. Right, in the workflow, a 2D kd-tree implementation is used to sort points and calculate distances between them.  This information is used to compute the density map, and also to mark points that are close to each other given a threshold (200 µm).

Thus, cells within a 200 µm radius have to be marked: when two cells are closer than 200 µm, it is likely that the trench surface of the first acquired cell will interfere with the other cell. These cells are marked in orange in the list of LM targets and the user can decide whether they should be included in the run or not. However, it is also possible to manually select another list order. The GUI allows rows to be dragged and dropped. 

![image-20210624224735704](.\imgs\image-20210624224735704.png)

​											**Density map and algorithm schematic followed  internally to sort cells.**

