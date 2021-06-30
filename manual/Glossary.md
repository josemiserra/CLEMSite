# Definitions

## 1.1   Definitions 

**Bounding box –** two-dimensional rectangle inside an image which encloses a region. It is defined by 4 numbers (2 coordinates or 1 coordinate and width/height), which can be: top left and bottom right coordinates (Pascal VOC format), top left corner plus width and height (COCO format) , or center position coordinates of the rectangle its width and height (Yolo format). CLEMSite uses the Yolo format, and Pascal VOC in some internal cases.

**Coincidence point (CP) –** intersection position of the SEM and the FIB beam at the sample surface.

**Contour –** small set of pixels that delineates the edges of a ROI. We will use it as a synonym of convex hull.

**Deposition** – assisted process that deposits material on a selected sample surface. 

**EM Server** – a network server that implements the internal communication between the control software and microscope hardware. 

**Grid –** a sequence of geometric patterns (lattice formed by evenly spaced squares) and symbolic patterns (alpha-numeric or symbolic characters in order) etched in glass bottom dishes.

**Grid square** **–** single 600 µm x 600 µm square from the full grid pattern with a unique alphanumeric identifier.

**Landmark** **–** identifies a common location identified by a unique set of features recognizable in both LM and EM with its corresponding coordinates. A landmark, inside the software, is a data structure formed by UID (unique identifier) and a set of coordinates that indicate a location using one specific modality (e.g. SEM). In this software, the crossing points of the grid are used to determine the landmarks. 

![image-20210624222017779](.\imgs\image-20210624222017779.png)

**Figure 1. Checkerboard with landmarks.** We consider landmarks as identifiable points in any microscopy modality. One typical example is the checkerboard used for camera calibration between different perspectives, in this case, the landmarks will be the red circles indicating the crossing points of the checkerboard. (https://commons.wikimedia.org/wiki/File:Harris_corners_detected_on_chessboard.png) 

 

**Map** – a data structure containing landmarks of one microscopy modality. For instance, a SEM map is a data structure containing landmarks located using SEM images and its stage coordinates. The same applies for LM.

**Region of Interest (ROI)** – area in pixels from the image, which contains information of interest for the user. During the document, we will refer to the *ROI target* and the *ROI FOV*. The ***ROI target\*** refers to the bounding box on the surface area of the sample that encloses the volume to be acquired, in the *x*, *z* plane (see Figure 2). The ***ROI FOV\*** is the portion of the Field of View (FOV) which is imaged when a sub-volume is acquired from the total FOV, in this case in the *x*, *y* plane. 

**Reflected light** – a modality of imaging in fluorescent microscopes that adds a small percentage of laser light (20-30 %) to the transmitted light, resulting in an image that shows the surface reflection of the focal plane.

**Sample** – prepared resin block containing the cells and mounted on one stub. 

**Stub –** formed piece of metal which holds the sample on the SEM sample holder.

**Sample holder** – metal platform inserted into the microscope which holds several stubs and secures mechanical movement from the sample (linked to the stage).

**Stage** – platform inside the scanning electron microscope where the sample holder is mounted. All movements inside the microscope are referred to the stage.

**System** – the program or set of programs that acquires the inputs coming from the operator. The system is formed by the GUI, for data display and user input and the backend for data processing and analysis.

**Target cell** – stage coordinates that indicate the center of the ROI target, in our case a cell. 

**Use case** **–** a list of steps, typically defining interactions between an operator and a system, to achieve a goal. It is always initiated by a human or an external system which performs an action in the system.



![image-20210624222038265](.\imgs\image-20210624222038265.png)

​                         

**Figure 2: Definition of ROI to be acquired**. A) The schematic represents a cell (cylinder) to be acquired by the FIB-SEM. The volume of acquisition is the cuboid surrounding the cylinder. B) Example image of a FIB-SEM sample prepared for data acquisition. A trench milled is represented by the trapezoid, which exposes the face of the cuboid, which is the cross-section face to be imaged. The yellow cross marks the center of the cell (target cell) as projected onto the x/z plane, which is parallel to the surface of the sample and its position is indicated using stage coordinates. A) The target cell position can be used to define a 2D bounding box (ROI target 20 x 50 µm), and with the depth (30 µm), the total volume to be acquired. Before starting to mill, the user needs to define two regions: first, the Field of View (FOV, 100 µm x 100 µm), which is the total observable region, and the second, the ROI FOV (15 µm x 12 µm), which is a portion of the FOV where the cross-section is imaged, defined by width and height.