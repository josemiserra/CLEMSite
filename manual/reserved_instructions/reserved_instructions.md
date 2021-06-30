

<span style="color:red"> The instructions here expressed are in good faith and while every care has been taken in preparing this document, the authors make no representations and gives no warranties of whatever nature in respect of this document, including  the instructions or any description of the usage of the software and hardware contained herein. The authors cannot be held liable for the reliance and execution of the instructions described in this document. </span>



# 1.  Setting up a new computer

Usual PC configurations inside a microscope room, have a CrossBeam connected to a Zeiss SmartSEM computer, then a white box connected to an ATLAS 5 computer.

**IMPORTANT: We encourage to use an additional computer which should be a clone of the ATLAS 5 computer. This will protect you from problems derived from updates in the original software, and it is also advised that users that will not use CLEMSite, use the original PC and not this one.**

For the alternative PC/laptop, it is recommended to have the same or better specifications that the ATLAS 5 computer, and come with at least 3 independent USB 3.0 ports. Install ATLAS 5 on it. You should follow the ATLAS 5 instructions to do a proper installation, which do not require special technical skills: just an installation of the corresponding installers (drivers, Atlas Engine and ATLAS 5) and a proper license (See [section 4](#_Install/upgrade_the_software)). ATLAS 5 should work in the same way as the original ATLAS 5 computer. Do not forget to copy the microscopy personality and the stored configurations for milling from the old PC to the new PC.

 

To exchange from the original ATLAS 5 PC to the alternative PC it is as simple as to connect all three USB-cables coming from the original Atlas-PC ( and you will see them coming from the Atlas- white-box) to the alternative PC/laptop. Turn off the white box (of course the microscope should not be operating), annotate the corresponding USB input in the original PC and connect the cables to the alternative PC. Then go to Preferences and register the COM API.

It is very important to remember the order and position of USB plugs, since the connections are remembered when they are reconnected, otherwise you will cause problems with your original microscope set up. If you accidentally mixed them up, or they are not properly recognized, close everything, reset the box and try to register and deregister the software inside Atlas-Engine.

\> Re-register them inside Atlas Engine : Misc. » Preferences » General » Unregister COM API then Register COM API:

![img](.\imgs\clip_image004x.gif)

​																		**Registering the COM API in Atlas Engine.**

  

If you try this installation and you observe problems or malfunctioning, stop it, uninstall the Fibics Server version here proposed, and connect the original ATLAS PC.

## 1.1   On the existing SmartSEM computer

1)   We recommend you to backup the SMARTSEM PC and original/production ATLAS PC before you start.

2)   Disconnect the production ATLAS-PC.

3)   You have a Fibics server running on this computer.

a.    Click on the Fibics Server icon in the task bar, If you try this installation and you observe problems or malfunctioning, stop it, uninstall the Fibics Server version here proposed, and connect the original ATLAS PC.

## 1.2   On the existing SmartSEM computer

1)   We recommend you to backup the SMARTSEM PC and original/production ATLAS PC before you start.

2)   Disconnect the production ATLAS-PC.

3)   You have a Fibics server running on this computer.

a.    Click on the Fibics Server icon in the task bar,  and shut it down. Click on the 'Exit' button (do not click on the X in the right upper corner, this just closes the window).

4)   Run *Fibics Server for ZEISS Microscopes 5.2 installer: (5.2.1.157 is the version used in the article, but until 5.2.2.170 should work fine.)*

This server is a simple executable (.exe), so you can install and reinstall versions without affecting the SMART SEM installation. 

![img](.\imgs\clip_image004.gif)

​																									**Fibics Server on SmartSEM-PC**

Shut it down. Click on the 'Exit' button (do not click on the X in the right upper corner, this just closes the window).

5) Restart the SmartSEM PC.

6) Confirm that the Fibics server has been started automatically and the version is right. When running Atlas Engine later, check in the verbose that messages are getting in. Maintain the verbose always so the log is saved. It could be important for service technicians.



## 1.3   On the Atlas computer

**If you are trying to upgrade:** 

1) You do not need to uninstall the previous version of the Atlas Engine, only the ***Atlas Client\***. Uninstall any current *'Atlas Client'*

Windows » Control Panel » Programs and Features » Uninstall Atlas Client

2) In the Atlas PC run the Atlas Engine installer ( version used : *5.2.2.83*)

**If the PC is new:**

1) Run Atlas Audit Tool to get specifications of the microscope and software 

“Save Computer Info” » send to Fibics to get license

2) After receiving the license from Fibics, run Atlas Audit Tool to import the license

 

![img](.\imgs\clip_image002z.gif)

​                                  





**Figure 5: Atlas 5 Upgrade Audit Tool**

 

3) Run the Atlas Engine Installer. ![image-20210615154921667](.\imgs\image-20210615154921667.png)

4) Register the COM API following the steps described under “2. Setting up Computer”

5) Install the Client ![image-20210615155005094](.\imgs\image-20210615155005094.png):  *Atlas Client 5.2 upgrade installer: (5.2.1.157)*

6) Run the latest Atlas Client upgrade installer. 

7) Tell Atlas Engine the local IP address of the SmartSEM computer:

Atlas Engine » Misc. » Preferences » SmartSEM (SEM)

![img](.\imgs\clip_image002s.gif)

**Atlas 5 Preferences and SmartSEM connection setup**

 

Copy the Atlas Personality File (Recipes, Parameters for Atlas runs) and HKLM-file from the computer normally connected to the microscope (the production PC) to the same destination on the new computer. Having a backup of these files is recommended as well. These are important files and need to be saved.

![img](.\imgs\clip_image002w.gif)

**Microscope personality file**

The ProgramData folder is usually hidden under C:\. Change the Folder options if you cannot find it. 

8) Select Content Panel 

Windows start menu » Folder options » View » Show hidden files, folders and drives.

9) Confirm that the Fibics server has been started an check in the verbose that messages are getting in. 



 





