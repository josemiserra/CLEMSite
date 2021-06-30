## 5.  CLEMSite-EM : using the Navigator



![image-20210615085256067](.\imgs\image-20210615085256067.png)



### 5.1. Loading landmarks

Check box **2**  - *Input file buttons.*  The red button shows a dialog to input the .xml file with landmarks (red) and the target coordinates file .xml  (green). Load the the landmarks first, you will see in **3** and **4** that positions in red show up in the grid representation. 

In the list **3**, each tab shows the coordinates of one system, Light Microscope stage coordinates and SEM stage coordinates, where each row corresponds to one each other. You can change the tab between LM positions and SEM stage positions,  SEM stage positions should be gray and empty.

Perform the steps 3,4,5,6 below, and then, only then, load the targets (green).

The _Flag buttons_ can be used for manual assignment of positions. If a position from LM is found by moving in SEM manually (stage movement, do not use beam shift), the operator can assign set position in the center of the screen and then click on the red flag. 

Pay attention to the following:

- Red row indicates that the point is a landmark that has LM but not SEM stage coordinates (red in LM, gray in SEM list)

- Blue row indicates that the point is a landmark that has LM and SEM stage coordinates 

- Green row indicates a target position, they show up only after loading the targets and in the list, below the landmarks

- Orange row indicates positions that have SEM stage coordinates but no correspondences in LM.  They are usually positions recorded by the user that have an interest. If the user finds an interesting position, it can be added as a target using the green flag. You can convert them to target points. 

  

  **To move to one specific point**

  * Click on the row of the point and then into the button Move to point.
  * Double-click on the number in front of the desired location.

  ![img](.\imgs\clip_image089.gif)

  - If the map is calibrated (3.2), you can also use the right click button in the grid map to move to a position in the grid:

  ![image-20210615161426418](.\imgs\image-20210615161426418.png)

  

  **Manually adding points**. 

  If manual points are acquired, they need to be changed to be “Target points”. In the SEM part of CLEM*Site*, add points using the orange or green flag.

![img](.\imgs\clip_image006.gif)

​			

![img](.\imgs\clip_image002asdfxxx.gif)



Turn them into targets by selecting the point you want to change and select “Target”. The point should turn green, if not, select in the “Convert Point Type to” “- -“ and then “Target” again.

You can go back to any position of interest just double clicking on the list. 



**Shielding**

If one of the points needs to be corrected (i.e. you want to rewrite the position), you can also delete the point (garbage can) and acquire it again. 

Another possibility is to correct and shield. A shielded point cannot be change unless is unshielded. 

Usually happens that we move to a position, we correct it, and we don't this position to be changed for any posterior computed transformation. We can use shielding in that case.

-  Move to position of the row, correct manually with stage position.
-  Click on shield and the position will be saved. A shield icon will show up in the side. 
- The point will remain always in this SEM stage saved positions unless you click on the row, and in the shield again to unshielded it.

![image-20210615181124053](.\imgs\image-20210615181124053.png)

**Blocking**

Some regions of the sample can be damaged. If that is the case is convenient to block the stage positions surrounding them so they are not used in any computation. After clicking in a row, use the block point command in the menu for it or the Convert type to Blocked. You can Unblock it using the Unblock point from the menu.  

![image-20210615165349497](.\imgs\image-20210615165349497.png)

![image-20210615165642176](.\imgs\image-20210615165642176.png)



### 5.2 Doing a calibration LM-EM

There are two ways of doing calibrations in EM. One is manual, the other is automatic. Use the automatic for automation experiments and the manual for local navigation around the sample.

#### 5.2.1 Manual calibration 

This can be done with or without landmarks file preloaded.

If the navigator is connected, then move using SmartSEM or AtlasEngine to a move to crossing position ONLY BY STAGE POSITIONS (disable beam shift). 

![image-20210615161126171](.\imgs\image-20210615161126171.png)

Then click on the Compass button (Navigate).  The following menu will show up. You will have to pick up three different corners of a square. You can use the button Show UI from the server and manipulate around using ATLAS.

![image-20210615180959613](.\imgs\image-20210615180959613.png)



Once you have recognized a corner with a distinctive pattern an letter, select it from the list and click on Add. This will associate the coordinates of the microscope of your current position with the pattern name inside the grid square. 

 Repeat the same for 3 more points and click on OK. You can also delete the last point that you have acquired clicking on Delete.

It is possible to ignore the full process even if you acquired some points by clicking on cancel.

The model will allow you move along the grid and generate a map.

NOTE: It is possible to not do the navigation without using the assisted menu. Move to the crossing position, click on the orange flag and save the point. Then go to the row, and rename it to the codename of the grid (like 7R or 0P). It will automatically update itself. If landmarks have been already loaded, use the red flag to make the row assignment to the position. 





#### 5.2.2 Automatic calibration

First load a landmarks LM file.  First, position your sample in the middle of a grid square using Atlas. It is not important which square, but the pattern must be clearly readable by eye (see the picture below) .  Go to the scan button :

![image-20210615223730865](.\imgs\image-20210615223730865.png)

1)  The bullseye is used for starting the surface scan. If the process starts, then use square to stop it. 

A menu will show up and you can provide a menu where the Scanning images will be saved. 

If no file with light microscopy coordinates has been load it you still can do an automatic scan (and load the file later or use it for travelling around the grid.)

![image-20210615234422781](.\imgs\image-20210615234422781.png)



2)  If a manual initial map is computed (recommended), the user is prompted if he wants to use that map. If the answer is Yes the process will start automatically.  Otherwise, a menu will show up.

![image-20210615234608664](C:\Users\serra\Desktop\CLEMSite Paper\Latest\clemsite-master\imgs\image-20210615234608664.png)

It is important that first you go and do a folder where to save the first shot of the image. Then grab an image clicking on the record button.

3)  The user must to indicate which alphanumeric pattern is present in the center of the image (the user will select 4T for the present image in the combo box), and the other one to rotate the image until the pattern is straight. Thus, the general orientation of the grid can be obtained and used internally to narrow down the space search in the line detection algorithm. The smaller letter/number is always the first in the name of the square, otherwise it will not be recognized. After clicking OK in the previous form, the line detection algorithm detects the lines forming the grid (in red, right image). The landmark 4T is assigned to the proper square crossing (top right if image is straight, green spot in the image). 

 

![img](.\imgs\clip_image009.jpg)

If this message shows:

![image-20210615234943274](.\imgs\image-20210615234943274.png)

then try with manual acquisition of the four landmarks (manual calibration) and start again the procedure.

4) A small pop will ask for the percentage of grid positions to scan. Usually you have to provide a percentage of scanning. 30-50 percent. The process of automatic acquisition will start after a while, the process will finish and then positions will be satisfactorily acquired (you will see the lists updated). 

4) It is convenient to make a revision of positions by clicking on them and validate the landmark assignment. You can block o delete points. It might be that some points have been detected as blocked. If this is wrong you also can unblock them.

5) Now you can load the target landmarks .xml (**Load coordinates Target**) and the positions will be loaded too.  Once loaded, again, do a revision to see if there is a correspondence, with at least one cell. Again, you can delete some cells that you are not interested or that are out of limits. 

6)  **Save your session to continue it later**. Click on **File->Save session**. This will save the microscope state, the coordinates from the drawing map and the coordinates that you have acquired. That will allow you to retake again your job later using **File->Load session**. It will save two files, a .json and .xml. The first is for saving the microscope state, the second are the coordinates.

It allows you also to save your coordinates for targeting (use a session later in CLEM*Site* _Multisite_ ). 



#### 5.3  Description of menu options

![image-20210615231531216](.\imgs\image-20210615231531216.png)

**File menu:**

●    **Load Coordinates Calibration:** Loading the list of landmarks from a xml-file computed in CLEM*Site-*LM.

●    **Load Coordinates Target:** Loading the list of targets from a xml-file computed in CLEM*Site-*LM.

●    **Save Coordinates SEM:** Saving SEM coordinates of targets and landmarks after scanning the surface and running the line detection algorithm.

●    **Save Coordinates SEM as…:** Saving SEM coordinates (at a specific location) of targets and landmarks after scanning the surface and running the line detection algorithm.

●    **Load Session:** Instead of loading just the xml file, the full project is loaded.

●    **Save Session:** Instead of saving just a xml file, the full project is saved.

●    **Load coordinates LM from text file:** Not implemented 

●    **Save coordinates SEM from text file:** Not implemented 

●    **Change settings:** Preferences file (text file) can be changed concerning the grid features (size) and the line detection algorithm (similar as for CLEM*Site* LM-SEM, Settings -> Preferences).



 ![image-20210615231606275](.\imgs\image-20210615231606275.png)



**Actions menu:**

●    **Give Reference:** When a calibration point (references from LM) is found, click on this button or the red flag to assign the current position in SEM to LM.

●    **Correct Position:** When a point already assigned in the SEM needs to be corrected by the current position, click here or the ruler button.

●    **Acquire:** Get the current position of the microscope and store its coordinate as a coordinate of interest (no relation with LM).

●    **Block point:** Do not use landmarks for any computation e.g. crack in the sample.

●    **Unblock point:** Take the blocked point again under consideration.

●    **Convert to calibrated:** Acquire a landmark manually and convert it to a calibrated point (you have LM and EM, even though it was not used in the LM analysis).

●    **Convert to target:** Select cell in the SEM and it will be acquired (even though no LM data exist or are specifically assigned).

●    **Delete:** Removes the point selected from the list

●    **Scan for references and find their SEM positions:** Scanning of the sample surface giving a grid structure provided in the preferences file.

●    **Reset calibrated coordinates:** values of calibrated coordinates are reset

●    **Show image of cell** – Not implemented. 

●    **Navigate:** Guides the user towards manual acquisition of landmarks and creating a system for moving around in the SEM. 

●    **Align Scan:** If a process with a previously scanned sample surface is stopped and restarted. The old scan can be realigned to the slightly altered positions using 3 landmarks to compute the change avoiding to redo all the computations.

●    **Load folder with previous Scan:** If the surface of the sample has been scanned previously with the SEM, the scan can be loaded again.

●    **Correct By RANSAC:** After a scan is completed, the list of calibration points can be evaluated by local transformations to find the error. The procedure extracts one point and then predicts its position. If the error is bigger than the error the user provided (e.g. 10 µm), the point is blocked. 

●    **Automatic coincidence point:** Runs the routine for the automatic coincidence point at the indicated position.

●    **Make a trench based on recipe:** A trench is milled in the current position based on the parameters set by the recipe (depth, width, FIB current).

 ![image-20210615231738813](.\imgs\image-20210615231738813.png)



**Plot Menu:**  

●   **Grab:** Acquire a single image with the SEM**.**

 **Grabbing images**

If you wish to save an image from the region of interest each time that you grab a position, click on the red recording button named as grab. It shows a menu where you can select different image conditions (resolutions, dwell time, line average). Write the conditions of your imaging. Check the button “*Save picture with acquisition* ”

Note: Your imaging conditions can be changed in the same way at any time.

![img](.\imgs\clip_image0050.jpg)

●   **Plot tiles map:** Not implemented.

**Edit:**

●    **Options:** Shows current preferences file.