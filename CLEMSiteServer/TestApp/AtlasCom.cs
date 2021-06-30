
using System;
using System.Collections.Generic;
// Insert the API namespace. You must have added a reference to the CZEMApi ActiveX control in Visual Studio before, as described in the SmartSEM Remote API Manual.
// Set the APILib properties 'Embed Interop types" to False and 'Local copy' to True. 
using Atlas5;
// Needed for using the VariantWrapper class
using System.IO;
using System.Diagnostics;
using System.Threading;
using System.Net;
using System.Text.RegularExpressions;

namespace msite
{
    public enum BC_TYPE { ESB_TRENCH, ESB_FOCUS, ESB_ACQUISITION }

    /// <summary>
    /// Atlas control class
    /// Composition of operations.
    /// It depends on FibicsInterfaceHandler, which encapsulates 
    ///  
    ///  call_function from Message Parser ----> calls Atlas Com ---> calls FibicsInterfaceHandler
    ///  
    /// - Message parser calls the function
    /// - Atlas Com is the function using the domain operations from FibicsInterfaceHandler.
    /// - FibicsInterfaceHandler encapsulates basic operations of the Atlas API and controls the state of the microscope.
    /// 
    /// 
    /// </summary>
    public class AtlasCom
    {
        
        Job m_job;
        // Define a flag to check for initialisation later
        private bool apiInitialised = false;
        private bool is_imaging = false; // Atlas is working and doing slice and view

        // Do we need tracking?
        private bool needsTrack = false;
        // Do we need AFAS
        private bool needsAFASbox = false;


        //Function to get random number
        private static readonly Random getrandom = new Random();

        private ImageHelper m_imageHelper = new ImageHelper(); // Call modules for image processing

        // Locks
        public static readonly object syncLock = new object();

        private FibicsInterfaceHandler m_fibicshandler;
        private static FileSystemWatcher black_watcher;


        private StateObjClass MessageObj;

        public XMLManager mXML = new XMLManager();

        public const double radians54 = (Math.PI / 180) * 54.0;
        public double beamfactor54;
        public double beamfactor36;
        private int _noTrack = 0;

        public StateImage acquisitionState;
        string old_log = "";

        public bool NeedsTrack
        {
            get
            {
                return needsTrack;
            }

            set
            {
                needsTrack = value;
            }
        }

        public bool NeedsAFASbox
        {
            get
            {
                return needsAFASbox;
            }

            set
            {
                needsAFASbox = value;
            }
        }

        private class StateObjClass
        {
            // Used to hold parameters for calls to TimerTask.
            // public int SomeValue;
            public System.Threading.Timer TimerReference;
            public bool TimerCanceled;
        }

        public AtlasCom()
        {
            this.beamfactor54 = Math.Cos(radians54);
            this.beamfactor36 = Math.Sin(radians54);
            this.m_fibicshandler = new FibicsInterfaceHandler();

        }
        /***** TOOLS FOR/WHEN CONNECTING ATLAS*****/
        /// <summary>
        /// Starts Atlas. This is the first call for initialization.
        /// </summary>
        /// <param name="message"></param>
        /// <returns></returns>
        public bool startAtlas(ref string message)
        {

            if (!this.m_fibicshandler.isInitialized()) // if we are not connected, connect now
            {
                if (!this.m_fibicshandler.initializeEngine(ref message))
                {
                    apiInitialised = false;
                    return false;
                }
                apiInitialised = true;
                return true;
            }
            if (this.m_fibicshandler.originalState.isReady)
            {
                this.m_fibicshandler.loadState(this.m_fibicshandler.originalState, ref message);
                this.addMessage(message);
            }
            return true;
        }
        
        /// <summary>
        /// If the api is initialised returns true.
        /// </summary>
        /// <returns>bool</returns>
        public bool isConnected()
        {
            if(apiInitialised) this.addMessage("API has been initialized \n");
            else this.addMessage("API not initialized. A client has to connect first. \n");
            return apiInitialised;
        }
        
        /// <summary>
        /// If the process of acquisition is happening, returns True.
        /// </summary>
        /// <returns></returns>
        public bool isImaging()
        {
            return this.is_imaging;
        }
        
        /// <summary>
        /// Shows the Atlas User interface.
        /// </summary>
        public void showUI()
        {
            try
            {
                if (this.m_fibicshandler.m_pSEMVE != null)
                {
                    m_fibicshandler.m_pSEMVE.HideUI();
                    m_fibicshandler.m_pSEMVE.ShowUI();
                }
            }
            catch (System.InvalidCastException)
            {
                // Console.WriteLine(e.Message);
                return;

            }

        }
        
        ///<summary>
        /// Checks the ATLAS COM components and returns a message if the connection was succesful
        ///</summary>
        public bool Connect(ref string message)
        {

            if (!this.m_fibicshandler.isInitialized()) // if we are not connected, connect now
            {
                // change labels etc to reflect the change
                message = "Connected.\n";
                if (!this.m_fibicshandler.initializeEngine(ref message))
                {
                    apiInitialised = false;
                    this.addMessage(message);
                    return false;
                }
                this.addMessage(message);
                apiInitialised = true;
                MainForm.setStatusConnected(true);
                MainForm.setStatusError(false);
            }
            return true;
        }
        
        ///<summary>
        /// Disconnects the ATLAS COM components and returns a message if the connection was succesful
        ///</summary>
        /// TODO: Use a better way to search the process using regular expressions containing ATLAS.exe
        public bool Disconnect(ref string message)
        {

            if (apiInitialised)
            {
                lock (syncLock)
                {
                    message = "Disconnected";
                    this.m_fibicshandler.closeEngine();
                    apiInitialised = false;

                    try
                    {

                        Process[] localAll = Process.GetProcesses();
                        foreach (Process proc in localAll)
                        {
                            string pname = proc.ProcessName;
                            Match match = Regex.Match(pname, @"ATLASE.*", RegexOptions.IgnoreCase);
                            if (match.Success)
                            {
                                proc.Kill();
                            }
                        }

                        foreach (Process proc in Process.GetProcessesByName("AtlasEngine"))
                        {
                            proc.Kill();
                        }

                    }
                    catch (Exception ex)
                    {
                        System.Windows.Forms.MessageBox.Show(ex.Message);
                    }
                }
                message = "Succesfully disconnected. Atlas killed.";
                MainForm.setStatusConnected(false);
                return true;
            }
            message = "Already disconnected.";
            return false;
        }
        
        /// <summary>
        /// Saves values associated to the microscope. This will be the original state
        /// to which data will be restored before starting an acquisition.
        /// </summary>
        public void Refresh()
        {
            string report = "Saving state executed ";
            this.m_fibicshandler.saveState(ref this.m_fibicshandler.originalState, ref report);
            if (this.m_fibicshandler.stateSaved)
                MainForm.setStatusSaved(true);
            this.addMessage(report);
         }

        /*********Acquisition workflow**************************************************************************************************/
        ///<summary>
        /// Start Sample
        /// 
        /// This function is the implementation of the acquisition workflow. 
        /// After some initialization of flow control variables, a job is created.
        /// The concept of job here refers to a class that stores all the information associated to the acquisition
        /// and the progress of the workflow. 
        /// 
        ///   1.- Initialization: 
        ///             - sets up a job (at the moment no queue, single job) and reads the setupfile and parameters.
        ///             - does AF 
        ///             - does coincidence point
        ///   2.- DigTrenches
        ///   
        ///   3.- Starts acquisition
        ///</summary>
        public bool StartSample(Job currentJob, ref string error)
        {

            try
            {
                this.is_imaging = false;
                this._noTrack = 0;
                this.m_job = currentJob;

                if (Job.numOfJobs == 0)
                {
                    this.acquisitionState = new StateImage(this.m_fibicshandler.originalState);
                }

                
                // The objective of phase 1 is to restore the original conditions, set up the CP and return back to the original position with CP ready.
                ErrorCode error_exp = this.InitializeSample(currentJob, ref error);
                this.addMessage(error);

                switch (error_exp)
                {
                    case ErrorCode.API_E_NO_ERROR:
                        break;
                    case ErrorCode.API_AUTOFOCUS_ON_XSECTION_FAILED:
                    case ErrorCode.API_CP_FAILED:
                    case ErrorCode.API_TRENCH_NOT_FOUND:
                        this.cancelRun();
                        return false;
                    default:
                        this.errorRun();
                        return false;
                }
             
                this.addMessage("Coincidence point and autofocus on region finished.");
                // The objective of phase 2 is dig the COARSE and polish trench, locate the trench and move the beam shift to focus on the XS face.
                // This position needs to be saved to set up the FOV of the imaging in the XS face.
                PointEM trenchPosition = new PointEM();
                error_exp = this.PrepareTrenches(ref currentJob, ref trenchPosition, ref error);
                this.addMessage(error);
                switch (error_exp)
                {
                    case ErrorCode.API_E_NO_ERROR:
                        break;
                    case ErrorCode.API_TRENCH_NOT_FOUND:
                    case ErrorCode.API_AUTOFOCUS_ON_XSECTION_FAILED:
                        this.cancelRun();
                        return false;
                    default:
                        this.errorRun();
                        return false;
                }

                this.addMessage("Trenches ready, ready to acquire.");

                // Phase 3 is start the acquisition and setting up background workers, like removing the canvas that is not necessary, finding focus points and relocating the autotune box, etc...
                error_exp = this.StartAcquisition(currentJob, trenchPosition, ref error);
                this.addMessage(error);
                switch (error_exp)
                {
                    case ErrorCode.API_E_NO_ERROR:
                        break;
                    default:
                        this.errorRun();
                        return false;
                }

                this.addMessage("STARTING ACQUISITION.");
            }
            catch (System.NullReferenceException)
            {
                return false;
            }

            return true; 
        }
        
        /// <summary>
        /// PHASE 1 Restoring conditions and coincidence point
        /// </summary>
        /// <param name="currentJob"></param>
        /// <param name="error"></param>
        /// <returns></returns>
        public ErrorCode InitializeSample(Job currentJob, ref string error)
        {

            // Start ATLAS
            if (!this.startAtlas(ref error))
            {
                // if returns false, we wait and we try again
                Thread.Sleep(10000);
                if (!this.startAtlas(ref error))
                {
                    return ErrorCode.API_ENGINE_INITIALIZATION_FAILED;
                }
                this.addMessage("Initial conditions restored: \n" + error);
            }

            PointEM nextPosition = currentJob.position;
            string jobname = currentJob.job_name + "__acq";
            string profile_path = currentJob.file_setup_path;
            string scale_unit = currentJob.scale_unit;


            /// <part1>
            /// Modify profile with basic settings
            /// </part1>
            /// 
            if (!this.checkNSetXMLFile(currentJob.file_setup_path, currentJob.alt_file_setup_path, ref error))
            {
                this.addMessage("Error Reading XML File:\n" + error);
                return ErrorCode.API_XML_INVALID;
            }
            this.mXML.setJobName(jobname);
            this.mXML.setDestinationFolder(currentJob.job_folder + "\\", "cell");
            this.mXML.disableTrackingMarks();
            // Avoid to turn off EHT and FIB
            if (currentJob.isLast)
            {
                this.mXML.setOptions(true, true, true);
            }
            else
            {
                this.mXML.setOptions(true, false, false);
            }
            // Check that Beam ID's match
            string info_apertures = "";
            if (!this.mXML.checkBeamIDs(this.m_fibicshandler.fib_apertures_map, ref info_apertures))
            {
                error = "Problem with Beam Identification. They don't match. \n";
                this.addMessage(error + info_apertures);
                return ErrorCode.API_XML_FIB_APERTURES_NOT_MATCHING;
            }
            if (Job.numOfJobs == 0)
            {

                this.addMessage(info_apertures);
                long AFint, ASint;
                this.mXML.getAFASInterval(out AFint, out ASint);
                this.m_job.autotune_period = AFint;
            }
            else
            {
                // Restore B&C before starting
                this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
                this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_trench, this.m_fibicshandler.originalState.contrast_ESB_SEM_trench);
            }
            this.mXML.commit();
            this.m_fibicshandler.m_pSEMVE.ShowUI();

            if (!findCoincidencePoint(ref nextPosition, scale_unit, currentJob.job_folder, currentJob.swapCPposition, ref error))
            {
                this.addMessage(error);
                this.addMessage("Swapping CP position and trying again.");
                currentJob.swapCPposition.X = 100.0f; // Update the CP distance to try again.
                if (!findCoincidencePoint(ref nextPosition, scale_unit, currentJob.job_folder, currentJob.swapCPposition, ref error))
                {
                    this.addMessage(error);
                    this.addMessage("Error in CP. Moving to next cell.");
                    error = "";
                    this.m_fibicshandler.loadState(this.m_fibicshandler.originalState,ref error); // Restore original state. 
                    this.addMessage("ERROR:" + error + System.Environment.NewLine + ErrorCode.API_CP_FAILED.ToString() + ": CP not found.");

                    return ErrorCode.API_CP_FAILED; // End here, without the CP we will not dig in the right position.
                }              
            }
            this.addMessage("Coincidence point finished.");
            // Now, it is possible to update the position. CP calculations can mess up some microns previous calculations
            // It is possible to recalculate the position and start again.

            this.updatePosition(currentJob);
            this.addMessage("Updating position finished");

            return ErrorCode.API_E_NO_ERROR;
        }
        
        /// <summary>
        /// PHASE 2
        /// Digging trenches and finding them
        /// </summary>
        /// <param name="currentJob"></param>
        /// <param name="trenchPosition"></param>
        /// <param name="error"></param>
        /// <returns></returns>
        public ErrorCode PrepareTrenches(ref Job currentJob, ref PointEM trenchPosition, ref string error,bool AFASXFace = true, bool standalone = false)
        {
            string parentFolder = currentJob.job_folder;
            string profile_path = currentJob.file_setup_path;
            string scale_unit = currentJob.scale_unit;
            this.addMessage("Preparing trenches.");

            // Grab image in ESB BEFORE the trench
            int counter = 0;
            string c_time = string.Format("-{0:yyyy-MM-dd_hh-mm-ss-tt}", DateTime.Now);
            string tag = "ESB_" + counter.ToString() + c_time;

            string image_before_Trench = this.grabTrenchImage(parentFolder, tag, ref error);

            this.addMessage("Digging trenches for " + currentJob.job_name);
            if (!this.digTrenches(ref error, profile_path))
            {
                this.addMessage(error);
                return ErrorCode.API_FAILURE_DIGGING_TRENCH;
            }

            /// <part2> 
            ///  Find Trench
            ///  Detectors calibration and Autotune set up
            /// </part2>
            /// 
            // This position must be SAVED
            this.GetStagePosition(ref trenchPosition, ref error);

            this.addMessage("Detecting trench.");
            // Locate the trench
            Dictionary<string, System.Drawing.PointF> trenchPoints = new Dictionary<string, System.Drawing.PointF>();

            if (!findTrench(image_before_Trench, parentFolder, ref error, ref trenchPoints))
            {
                if (Job.numOfJobs == 0)
                {
                    this.addMessage("Prompting user B&C for trench finding.");
                    this.BnC_user("TRENCH BRIGHTNESS and CONTRAST: \n Set up your B&C until you differentiate the shape of the trench, and then press OK. \n If necessary, adjust focus and stigmators.", BC_TYPE.ESB_TRENCH);
                    counter++;
                    c_time = string.Format("-{0:yyyy-MM-dd_hh-mm-ss-tt}", DateTime.Now);
                    tag = "ESB_" + counter.ToString() + c_time;
                    image_before_Trench = this.grabTrenchImage(parentFolder, tag, ref error);
                    if (!findTrench(image_before_Trench, parentFolder, ref error, ref trenchPoints))
                    {
                        return ErrorCode.API_TRENCH_NOT_FOUND;
                    }
                }
                else
                {
                    this.addMessage("ERROR:" + error + System.Environment.NewLine + ErrorCode.API_TRENCH_NOT_FOUND.ToString() + ": Trench not found.");
                    return ErrorCode.API_TRENCH_NOT_FOUND;
                }

            }

            // center my FOV
            this.centerFOV(ref error, ref trenchPosition, trenchPoints, currentJob.roi);
           
            // Restore stigmators 
            if (Job.numOfJobs !=0 && !standalone)
            {
                this.m_fibicshandler.setStigs(this.acquisitionState.stigX, this.acquisitionState.stigY);
            }

            if (AFASXFace)  // Execute autofocus in the cross section face
            {
                ROI roi = new ROI(currentJob.roi);
                ErrorCode error_exp = this.AFASXFace(parentFolder, profile_path, ref roi, ref trenchPoints, ref error, ref currentJob.firstAF);
                
                this.addMessage(error);
                switch (error_exp)
                {
                    case ErrorCode.API_E_NO_ERROR:
                        break;
                    default:
                        return error_exp;
                }
                roi.offsetX = 0.0;
                roi.offsetY = 0.0;
                currentJob.roi = roi;
            }
                return ErrorCode.API_E_NO_ERROR;
        }
        
        /// <summary>
        /// PHASE 3, Starting acquisition 
        /// Phase 3 can run as independent module:
        ///     To provide: job object defined
        ///                 trenchPosition
        /// </summary>
        /// <param name="currentJob"></param>
        /// <param name="trenchPosition"></param>
        /// <param name="error"></param>
        /// <returns></returns>
        public ErrorCode StartAcquisition(Job currentJob, PointEM trenchPosition, ref string error)
        {
            this.addMessage("Starting acquisition of " + currentJob.job_name);
            PointEM nextPosition = currentJob.position;
            string scale_unit = currentJob.scale_unit;
            // Restore original position. Don't restore by moving the stage or the focus gets screwed
            this.m_fibicshandler.setBeamShift((float)trenchPosition.bsx, (float)trenchPosition.bsy);
            this.m_fibicshandler.setTiltCorrection(-36 * Math.PI / 180);
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_acq, this.m_fibicshandler.originalState.contrast_ESB_SEM_acq);
            /* Now we start imaging */
            this.m_fibicshandler.m_pATLAS3D.MillImageSetup(currentJob.file_setup_path);
            this.addMessage(currentJob.ToString());
            // currentJob.roi.offsetY = currentJob.roi.offsetY  - currentJob.roi.Height*0.05;
            this.m_fibicshandler.m_pATLAS3D.MillImageStartMillImage((float)currentJob.roi.Width, (float)currentJob.roi.Height, (float)currentJob.roi.offsetX, (float)currentJob.roi.offsetY + 1.5f);
            this.addMessage("ROI " + currentJob.roi.ToString());
            lock (syncLock) // Avoid cancellations and Job state changes during this period of initialization.
            {
                this.is_imaging = true;
                this.m_fibicshandler.m_pATLAS3D.MillImageUpdatePositionAutoTune(currentJob.firstAF.X, currentJob.firstAF.Y);

                /** BACKGROUND WORKERS **/

                this.MessageObj = new StateObjClass();
                this.MessageObj.TimerCanceled = false;
                System.Threading.TimerCallback TimerDelegate = new System.Threading.TimerCallback(TimerTask);


                // Create a timer that calls a procedure every 5 seconds
                // Note: There is no Start method; the timer starts running as soon as  the instance is created.
                System.Threading.Timer TimerItem = new System.Threading.Timer(TimerDelegate, this.MessageObj, 5000, 5000);

                // Save a reference for Dispose.
                this.MessageObj.TimerReference = TimerItem;
                this.addMessage("Message timer active.");
                Job.numOfJobs++;

                Thread.Sleep(60000); // Wait one minute before grab path
                                     // Create a file watcher to check each time a slice is added.
                string final_folder = currentJob.job_folder + "\\" + currentJob.job_name + "__acq";
                final_folder = AtlasCom.NormalizePath(final_folder);
                AtlasCom.black_watcher = new FileSystemWatcher();

                AtlasCom.black_watcher.Path = final_folder;
                AtlasCom.black_watcher.NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.FileName;
                AtlasCom.black_watcher.Filter = "*.tif*";
                // Add event handlers.
                AtlasCom.black_watcher.Renamed += new RenamedEventHandler(OnChanged);
                AtlasCom.black_watcher.EnableRaisingEvents = true;
                this.addMessage("Blackwatcher is active.");
                ImageHelper.listTracked = new List<int>();

            }

            return ErrorCode.API_E_NO_ERROR;

        }

        /**** WORKFLOW functions  ****/
        /// <summary>
        /// Find coincidence point based on a mark done using a high current in FIB.
        /// TODO: Refactoring in small functional units
        /// </summary>
        /// <param name="nextPosition">Position where to move (CP will be calculated relative to this position) and UPDATED accordingly</param>
        /// <param name="scale_unit">um, meters</param>
        /// <param name="im_folder">folder where to save all temporary files generated by the routine</param>
        /// <param name="m_error"></param>
        /// <returns></returns>
        public bool findCoincidencePoint(ref PointEM nextPosition, string scale_unit, string im_folder,System.Drawing.PointF cp_position, ref string m_error)
        {
            string cp_folder = im_folder + "\\coincidence_point_checks";
            bool exists = System.IO.Directory.Exists(cp_folder);
            if (!exists)
                System.IO.Directory.CreateDirectory(cp_folder);

            // Normalize to ATLAS -,- 
            if (nextPosition.x > 0)
                nextPosition.x = -nextPosition.x;
            if (nextPosition.y > 0)
                nextPosition.y = -nextPosition.y;

            // Move 50 um away from your sample to perform autofocus and CP. CP starts to change around 70 um away.            
            this.m_fibicshandler.setBeamShift(0f, 0f);
            PointEM currentPosition = new PointEM(nextPosition);

            currentPosition.x = currentPosition.x + cp_position.X;
            currentPosition.y = currentPosition.y + cp_position.Y;


            if (!this.m_fibicshandler.safeMove(currentPosition, scale_unit, ref m_error))
            {
                this.addMessage(m_error);
                return false;
            }


            this.addMessage("Moved to position: " + currentPosition.ToString());
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
            this.m_fibicshandler.setTiltCorrection(54 * Math.PI / 180);

            /////*********************** STEP 1: Set UP proper WD ***********************
            //  Continuous autofocus will unstabilize, so its good to keep it closer as 5 as much as possible


            if (!this.autoFocusOnSample(ref m_error, FibicsInterfaceHandler.SEM_SESI, ref currentPosition))
            {
                this.addMessage("ERROR 001: Autofocus on Sample FAILED.\n.");
                this.addMessage(this.m_fibicshandler.m_pSEMVE.GetAFASError());
                this.setFOV(ref m_error,450f);
                if (!this.autoFocusOnSample(ref m_error, FibicsInterfaceHandler.SEM_SESI, ref currentPosition))
                {
                    this.addMessage("ERROR 001: Autofocus on Sample FAILED.\n.");
                    this.addMessage(this.m_fibicshandler.m_pSEMVE.GetAFASError());
                    this.addMessage(m_error);
                    return false;
                }
            } 
            double WD = this.m_fibicshandler.getWD();
            double dfWD = WD - this.m_fibicshandler.originalState.sem_WD;
            if (dfWD > 800)
            {
                m_error = "ERROR 0020: problems with working distance. Too high.\n.";
                return false;
            }
            // add difference to Z
            PointEM mp1 = new PointEM();
            this.GetStagePosition(ref mp1, ref m_error);
            mp1.z = mp1.z + (dfWD);

            if (!this.m_fibicshandler.safeMove(mp1, scale_unit, ref m_error))
            {
                this.addMessage(m_error);
                return false;
            }
            // now set up original WD
            if (dfWD > 100) // For bigger differences, more than 100 micrometers up, redo autofocus
            {
                this.m_fibicshandler.setWD((float)this.m_fibicshandler.originalState.sem_WD);
                if (!this.autoFocusOnSample(ref m_error, FibicsInterfaceHandler.SEM_SESI, ref mp1))
                {
                    m_error = "ERROR 001: Autofocus on Sample FAILED.\n.";
                    return false;
                }
            } 
            /*********************************STEP 2: Leave your mark *****************************/
            string c_time = string.Format("-{0:yyyy-MM-dd_hh-mm-ss-tt}", DateTime.Now);
            string sem_before = "SEM_1st_original_" + c_time;
            string sem_after = "SEM_1st_square_burned_" + c_time;
            string fib_burn = "fib_burn" + c_time;
            // Grab sem image
            this.m_fibicshandler.GrabFrameSEM(cp_folder, sem_before, 0, EmConf.cp_im.pixel_size, EmConf.cp_im.dwell_time, EmConf.cp_im.line_average, 0.0, ref m_error);

            // Grab image FIB
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeFIB,FibicsInterfaceHandler.FIB_SESI, this.m_fibicshandler.originalState.brightness_sesi_FIB, this.m_fibicshandler.originalState.contrast_sesi_FIB);
            this.m_fibicshandler.setFIBAperture(FibicsInterfaceHandler.FIB_burning_aperture);
            this.m_fibicshandler.GrabFrameFIB(cp_folder, fib_burn, 2, 0, EmConf.cp_im.pixel_size * 0.1, 12, 3, 0.0, ref m_error); // mark square 3 times

            // Go back to SEM
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
            this.m_fibicshandler.GrabFrameSEM(cp_folder, sem_after, 0, EmConf.cp_im.pixel_size, EmConf.cp_im.dwell_time, EmConf.cp_im.line_average, 0.0, ref m_error);

            string image_SEM_before = cp_folder + "\\" + sem_before + ".tif";
            string image_SEM_after = cp_folder + "\\" + sem_after + ".tif";

            double center_x, center_y;

            if (!this.m_imageHelper.getCenterSquare(c_time, image_SEM_before, image_SEM_after, cp_folder, out center_x, out center_y, (float)EmConf.cp_im.pixel_size))
            {
                m_error = "ERROR 002:Imaging error, square not detected. Cancelling auto CP.";
                return false;
            }

            /*********************************STEP 3: Move to the center of your square in SEM and in Z with FIB *****************************/
            // Now we have the center, we need to shift, Z needs to be moved the difference in Y
            // If Y is down, means we need to add to Z
            float z_compensation_X = (float)center_x;
            float z_compensation_Y = (float)center_y;


            PointEM mp2 = new PointEM();
            this.GetStagePosition(ref mp2, ref m_error);

            double shift_projection_z = 0.0;
            double shift_projection_y = 0.0;
            shift_projection_z = center_y / Math.Sin(radians54);
            shift_projection_y = center_y;
            mp2.z = mp2.z + shift_projection_z;
            mp2.y = mp2.y - shift_projection_y;  // CHECK, should put y at the center of the image

            if (!this.m_fibicshandler.safeMove(mp2, scale_unit, ref m_error))
            {
                this.addMessage(m_error);
                return false;
            }

            // Now we are in focus and everything is alright BUT(never use BUT, use ands), the SEM needs to move with BeamShift
            double beam_shift_x, beam_shift_y;
            this.m_fibicshandler.getBeamShift(out beam_shift_x, out beam_shift_y);
            // Perfect, now guessing that the Y in FIB is not screwed, we need to fix the X using in the beam shift
            if (Math.Abs(beam_shift_x - (float)center_x) < 100)  // We need to check here that the beam shift is not more than 50 um away or we are f****d!!
            {
                beam_shift_x = beam_shift_x - (float)center_x;
                this.m_fibicshandler.setBeamShift(beam_shift_x, beam_shift_y);
            }
            /**************************************STEP 4: Refocus and BS in X*******************************************************************/
            // this is alright now for our friend the FIB, but the SEM now is crying because lost focus, so let's focus again
            if (!this.autoFocusOnSample(ref m_error, FibicsInterfaceHandler.SEM_SESI, ref currentPosition))
            {
                m_error = "ERROR 004: Autofocus on Sample FAILED.\n.";
                return false;
            }

            /*********************************STEP 5: REFINEMENT by SEM and FIB *****************************/

            // Grab the image to refine beam shift.
            string img_after_SEM_tag = "SEM_2nd" + c_time;

            center_x = 0.0;
            center_y = 0.0;
            this.m_fibicshandler.GrabFrameSEM(cp_folder, img_after_SEM_tag, 0, EmConf.cp_im.pixel_size, EmConf.cp_im.dwell_time, 1, 0.0, ref m_error);
            string img_after_SEM = cp_folder + "\\" + img_after_SEM_tag + ".tif";
            if (!this.m_imageHelper.getCenterSquare2(img_after_SEM_tag, img_after_SEM, cp_folder, out center_x, out center_y, (float)EmConf.cp_im.pixel_size))
            {
                m_error = "ERROR 005:Problem with Coincidence point refinement.";
                return false;
            }
            // If the square is away, we do one refinement step in Beam Shift.
            // The idea is to put the square in the center and use the square again as reference
            this.m_fibicshandler.getBeamShift(out beam_shift_x, out beam_shift_y);

            System.Drawing.PointF non_refined_bs = new System.Drawing.PointF((float)beam_shift_x, (float)beam_shift_y);

            if (Math.Abs(beam_shift_x - (float)center_x) < 100 && Math.Abs(beam_shift_y - (float)center_y) < 100)  // We need to check here that the beam shift is not more than 50 um away or we are fucked!!
            {
                beam_shift_x = beam_shift_x - (float)center_x;
                beam_shift_y = beam_shift_y - (float)(center_y * beamfactor54);
                this.m_fibicshandler.setBeamShift(beam_shift_x, beam_shift_y);
            }

            // Optional refinement (gives better results), 
            // Now we grab a FIB image and calculate the distance between squares.
            string img_after_FIB_tag = "FIB_2nd" + c_time;
            center_x = 0.0;
            center_y = 0.0;
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeFIB, FibicsInterfaceHandler.FIB_SESI, this.m_fibicshandler.originalState.brightness_sesi_FIB, this.m_fibicshandler.originalState.contrast_sesi_FIB);
            this.m_fibicshandler.setFIBAperture(FibicsInterfaceHandler.FIB_imaging_aperture);
            this.m_fibicshandler.GrabFrameFIB(cp_folder, img_after_FIB_tag, 0, 0, EmConf.cp_im.pixel_size, 10, 1, 0.0, ref m_error);
            string img_after_FIB = cp_folder + "\\" + img_after_FIB_tag + ".tif";
            if (!this.m_imageHelper.getCenterSquare2(img_after_FIB_tag, img_after_FIB, cp_folder, out center_x, out center_y, (float)EmConf.cp_im.pixel_size))
            {
                m_error += "ERROR 006: FIB image grabbing wrong. CP refinement not accomplished.";
                this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
                this.m_fibicshandler.setBeamShift(non_refined_bs.X, non_refined_bs.Y);
                return false;
            }
            // Change back to SEM, careful grabbin BS if we are in FIB mode
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
            this.m_fibicshandler.getBeamShift(out beam_shift_x, out beam_shift_y);

            if (Math.Abs(beam_shift_x - (float)center_x) < 100 && Math.Abs(beam_shift_y - (float)center_y) < 100)  // We need to check here that the beam shift is not more than 50 um away or we are fucked!!
            {
                    beam_shift_x = beam_shift_x + (float)center_x;
                    beam_shift_y = beam_shift_y + (float)(center_y * beamfactor54);
                    this.m_fibicshandler.setBeamShift(beam_shift_x, beam_shift_y);
            }

            // End FIB refinement
            // GRAB for comparison purposes
            string finalSEM = "finalPositionSEM";
            this.m_fibicshandler.GrabFrameSEM(cp_folder, finalSEM, 0, EmConf.cp_im.pixel_size, EmConf.cp_im.dwell_time - 1, 1, 0.0, ref m_error);
            string finalFIB = "finalPositionFIB";
            this.m_fibicshandler.GrabFrameFIB(cp_folder, finalFIB, 0, 0, EmConf.cp_im.pixel_size, EmConf.cp_im.dwell_time - 1, 1, 0.0, ref m_error);

            /****** STEP 7: Finding back original point****/
            // Change back to SEM, careful grabbin BS if we are in FIB mode
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
            // Take FIB as reference position and calculate back my original position
            // Now we move to the real position ONLY in x and y because z has been modified
            PointEM squarePosition = new PointEM();
            this.GetStagePosition(ref squarePosition, ref m_error);
            string img_final = cp_folder + "\\" + finalSEM + ".tif";
            center_x = 0;
            center_y = 0;
            if (!this.m_imageHelper.getCenterSquare2(finalSEM, img_final, cp_folder, out center_x, out center_y, (float)EmConf.cp_im.pixel_size))
            {
                m_error = "ERROR 005:Problem with Coincidence point.";
                return false;
            }
            // Get center square position
            squarePosition.x = squarePosition.x - center_x;
            squarePosition.y = squarePosition.y - center_y;

            // Position 1 : original is nextPosition
            // Position 2 :
            PointEM pos2 = new PointEM(currentPosition);

            pos2.x = pos2.x - z_compensation_X;
            pos2.y = pos2.y - z_compensation_Y;

            // Calculate final position
            double dx = pos2.x - nextPosition.x;
            double dy = pos2.y - nextPosition.y;
            nextPosition.x = squarePosition.x - dx;
            nextPosition.y = squarePosition.y - dy;
            // Finally compensate for Beam Shift
            nextPosition.x = -Math.Abs(nextPosition.x) + this.m_fibicshandler.originalState.sem_beam_shift_x;
            nextPosition.y = -Math.Abs(nextPosition.y) + this.m_fibicshandler.originalState.sem_beam_shift_y;
            nextPosition.z = 0.0;

            return true;
        }

        private void updatePosition(Job currentJob)
        {

            double bs_x_start, bs_y_start;
            double FOVx, FOVy;
            string error = "";
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
            this.m_fibicshandler.getBeamShift(out bs_x_start, out bs_y_start);
            this.m_fibicshandler.getFOV(out FOVx, out FOVy);
            // All positioning should be done with 0 beam shift
            this.m_fibicshandler.setBeamShift(0.0, 0.0);

            if (currentJob.updatePositionBeforeStart)
            {

                this.addMessage("REQUEST:update_position");
                try
                {
                    Thread.Sleep(Timeout.Infinite);
                }
                catch (ThreadInterruptedException)
                {
                    this.addMessage("Resuming operations after position updated.");
                }
            }
            // We assume the new positions POSITIVE
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
            this.m_fibicshandler.setFOV(FOVx, FOVy);
            currentJob.position.x = System.Math.Abs(currentJob.position.x)*-1.0 - bs_x_start;
            currentJob.position.y = System.Math.Abs(currentJob.position.y)*-1.0 - bs_y_start;
            if (!this.m_fibicshandler.safeMove(currentJob.position, currentJob.scale_unit, ref error))
            {
                this.addMessage(error);
                return;
            }
            this.m_fibicshandler.setBeamShift(bs_x_start, bs_y_start);  // Restore Beam Shift

            this.m_fibicshandler.GrabFrameSEM(currentJob.job_folder, "initialPosition_snapshot", 0, EmConf.cp_im.pixel_size, EmConf.cp_im.dwell_time, 1, 0.0, ref error);
            this.mXML.setStageState(currentJob.position.x, currentJob.position.y, currentJob.position.z, currentJob.position.t, currentJob.position.r, currentJob.position.m);
            this.mXML.commit();
            this.addMessage("Corrected position to:" + currentJob.position.ToString());

            return;
        }


        /// <summary>
        /// digTrenches 
        /// </summary>
        /// <param name="error"></param>
        /// <param name="profile_path"></param>
        /// <returns></returns>                  
        public bool digTrenches(ref string error, string profile_path)
        {
            /// <part1>
            // START COARSE TRENCH AND POLISH TRENCH
            //  TODO : Send pong to client, that everything is fine.
            //  This could go in a separated thread in which the status of the trench and 
            //  the polish can be polled via GetStatus questions from the client/s
            // 
            /// <part1>
            /// 
            this.m_fibicshandler.m_FIB_Beam.SelectBeam();

            bool bsuccess = this.m_fibicshandler.m_pATLAS3D.MillImageSetup(profile_path);
            if (!bsuccess)
            {
                string message_error = "MillImageSetup failed: " + this.m_fibicshandler.m_pATLAS3D.MillImageLastErrorMsg();
                this.addMessage(message_error);
            }
            this.m_fibicshandler.m_FIB_Beam.SetFOV(300, 300);
            Thread.Sleep(2000); // Wait 2 seconds
            this.addMessage("Starting COARSE trench.");
            bsuccess = this.m_fibicshandler.m_pATLAS3D.MillImageStartCoarseTrench();
            if (!bsuccess)
            {
                string message_error = "MillImageStartCoarse failed: " + this.m_fibicshandler.m_pATLAS3D.MillImageLastErrorMsg();
                this.addMessage(message_error);
            }
            Thread.Sleep(30000); // Wait 30 seconds

            if (!isMillStatus("COMPLETE", ref error, 50000000))
            {
                this.addMessage("MillImageStartCoarse failed: " + this.m_fibicshandler.m_pATLAS3D.MillImageLastErrorMsg());
                this.addMessage("ERROR in digtrenches:" + error);
                return false;
            }
            this.addMessage("COARSE trench job completed.");
            Thread.Sleep(2000); // Wait 2 seconds
            this.addMessage("Starting fine trench.");

            this.m_fibicshandler.m_FIB_Beam.SelectBeam();
            this.m_fibicshandler.m_pATLAS3D.MillImageSetup(profile_path);
            this.m_fibicshandler.m_FIB_Beam.SetFOV(300, 300); // To fix
            this.m_fibicshandler.m_pATLAS3D.MillImageStartFineTrench();
            Thread.Sleep(30000); // Wait 30 seconds
            if (!isMillStatus("COMPLETE", ref error, 50000000))
            {
                this.addMessage("MillImageStartCoarse failed: " + this.m_fibicshandler.m_pATLAS3D.MillImageLastErrorMsg());
                this.addMessage("ERROR in dig trenches:" + error);
                return false;
            }
            this.addMessage("FINE trench job completed");
            Thread.Sleep(5000); // Wait 5 seconds

            return true;

        }
        public string grabTrenchImage(string imfolder, string tag, ref string terror) {

            this.m_fibicshandler.setTiltCorrection(-36 * Math.PI / 180);
            this.addMessage("View changed to -36 degrees");

            string image_name = imfolder + "\\" + tag + ".tif";
            this.m_fibicshandler.setFOV(EmConf.ESB_trench_screenshot_pixel_size * 512, EmConf.ESB_trench_screenshot_pixel_size * 512);
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_trench, this.m_fibicshandler.originalState.contrast_ESB_SEM_trench);
            this.GrabFrameSEM(imfolder, tag, 0, EmConf.ESB_trench_screenshot_pixel_size, EmConf.ESB_trench_screenshot_image_dwell_time, 1, 0, ref terror);

            return image_name;
        }
        public bool findTrench(string image_name_before, string imfolder, ref string terror, ref Dictionary<string, System.Drawing.PointF> trenchPoints)
        {

            /* 
                1.- Take image of the cross section with ESB and analyze the picture at big pixel size
                *        
                *       1) is there something in the picture?
                *          TRUE - FALSE
                *          If false, its all black or all white, set up detector to original values and repeat
                */
            int counter = 0;
            string c_time = string.Format("-{0:yyyy-MM-dd_hh-mm-ss-tt}", DateTime.Now);
            string tag = "ESB_" + counter.ToString() + c_time;

            string image_name = this.grabTrenchImage(imfolder, tag, ref terror);

            /**
                * 1) Detect the thrench
                * 
                * 2) If the trench is found, get the BB where trench is
                *    Starting from the top, get the depth of the ROI and create
                *    a square for the FOV
                *
                * 3) Modify the SETUP 3D XML FOV according to the position detected on the image and reload it.
                * 
                * 
                * */
            Dictionary<string, System.Drawing.Point> trenchPoints_image = new Dictionary<string, System.Drawing.Point>();
            if (!this.m_imageHelper.DetectTrench(image_name_before, image_name, tag, ref trenchPoints_image))
            {
                // Remove failed file
                string filesToDelete = @"*failed*";
                string[] fileList = System.IO.Directory.GetFiles(imfolder, filesToDelete);
                foreach (string file in fileList)
                {
                    System.IO.File.Delete(file);
                }
                // Try with SESI
                this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
                tag = "Trench_2nd_" + c_time;
                image_name = imfolder + "\\" + tag + ".tif";
                this.m_fibicshandler.setFOV(EmConf.ESB_trench_screenshot_pixel_size * 512, EmConf.ESB_trench_screenshot_pixel_size * 512);
                this.GrabFrameSEM(imfolder, tag, 0, EmConf.ESB_trench_screenshot_pixel_size, EmConf.ESB_trench_screenshot_image_dwell_time + 2, 1, 0, ref terror);
                if (!this.m_imageHelper.DetectTrench(image_name_before, image_name, tag, ref trenchPoints_image))
                {
                    terror = "ERROR: Trench couldn't be detected.";
                    return false;
                }
                this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_trench, this.m_fibicshandler.originalState.contrast_ESB_SEM_trench);
            }
            this.addMessage("Trench detected.");
            foreach (var pair in trenchPoints_image)
            {
                System.Drawing.Point point = (System.Drawing.Point)pair.Value;
                trenchPoints[pair.Key] = new System.Drawing.PointF(point.X * EmConf.ESB_trench_screenshot_pixel_size, point.Y * EmConf.ESB_trench_screenshot_pixel_size);
            }
            return true;
        }
        public bool centerFOV(ref string error, ref PointEM trenchPosition, Dictionary<string, System.Drawing.PointF> trenchPoints, ROI roi)
        {
            // In theory now we got the trench values
            double beam_shift_x, beam_shift_y;
            this.m_fibicshandler.getBeamShift(out beam_shift_x, out beam_shift_y);

            // Get trench points
            System.Drawing.PointF shift_top = trenchPoints["top"];
            System.Drawing.PointF center = trenchPoints["center_shift"];
            System.Drawing.PointF corner_1 = trenchPoints["corner1"];
            System.Drawing.PointF corner_2 = trenchPoints["corner2"];

            float c_x, c_y;
            //c_x = (float)roi.Width*0.6f;
            //c_y = hotPointsF[0].Y * (float)beamfactor36; // First focus point is the stopPoint
            c_x = Math.Abs(corner_1.X - center.X) * 0.75f;
            c_y = Math.Abs(corner_1.Y - 1);
            float dist_trench = Math.Abs(corner_1.X) + Math.Abs(corner_2.X);


            // Move to the center in X
            beam_shift_x = beam_shift_x - shift_top.X;
            // Move to the center in y of the interface and then lower down half of it, but leaving a margin of 1 micrometer up

            beam_shift_y = beam_shift_y - (float)(shift_top.Y * beamfactor36) + 1f - (float)(roi.Height * 0.5); // Nice approximation to the center

            this.m_fibicshandler.setBeamShift(beam_shift_x, beam_shift_y);
            trenchPosition.bsx = beam_shift_x;
            trenchPosition.bsy = beam_shift_y;

            this.m_fibicshandler.setFOV(EmConf.ESB_trench_zoom_pixel_size * 512, EmConf.ESB_trench_zoom_pixel_size * 512);
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_trench, this.m_fibicshandler.originalState.contrast_ESB_SEM_trench);
            var status = this.m_fibicshandler.doAutoFocus(0.1f, EmConf.onESB_COARSE.range_focus, EmConf.onESB_COARSE.focus.dwell_time, EmConf.onESB_COARSE.focus.line_average);

            // Calibration of ESB B&C for acquisition
            if (!this.ESB_fineBC(ref error))
            {
                error = "\n In ESB B&C : " + error;
                return false;
            }

            // Setup autotune box and B&C for focus
            this.setAutotune(c_x, c_y, dist_trench - 4f); // we add some margin
            return true;
        }
        /// ESB  User Input 
        public bool ESB_fineBC(ref string error)
        {

            float newb, newc;
            if (Job.numOfJobs == 0)
            {
                this.BnC_user("ACQUISITION BRIGHTNESS and CONTRAST: \n Set up your B&C for ACQUISITION, and then press OK. \n If necessary, adjust focus and stigmators.", BC_TYPE.ESB_ACQUISITION);
            }
            else
            {
                this.mXML.setAutoTuneDetector(0, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_focus, this.m_fibicshandler.originalState.contrast_ESB_SEM_focus);
                this.mXML.commit();
            }
            newb = this.m_fibicshandler.originalState.brightness_ESB_SEM_acq;
            newc = this.m_fibicshandler.originalState.contrast_ESB_SEM_acq;
            this.mXML.setImagingDetector(FibicsInterfaceHandler.SEM_ESB, newb, newc);
            this.mXML.commit();
            this.addMessage("ESB final values:" + newb.ToString() + "," + newc.ToString());

            return true;

        }
        /// <summary>
        /// Autotune box setup
        /// </summary>
        /// <param name="cx"></param>
        /// <param name="cy"></param>
        /// <param name="FOV"></param>
        /// <param name="shiftx"></param>
        /// <param name="shifty"></param>
        /// <returns></returns>
        public bool setAutotune(float cx, float cy, float FOV, float shiftx = 0.3f, float shifty = 0.3f)// System.Drawing.PointF offset)
        {

            if (cx + shiftx > FOV) { cx = FOV * 0.15f; }
            if (cy + shifty > FOV) { cy = FOV * 0.15f; }

            shiftx = FOV * shiftx;
            shifty = FOV * shifty;
            double FOVdiv = 1 / FOV;
            double Bottom = (cy - shifty * 1.4) * FOVdiv; // 1.2
            double Top = (cy - shifty * 0.1) * FOVdiv; // 0.4
            double Right = (cx + shiftx) * FOVdiv;
            double Left = (cx + shiftx * 0.5) * FOVdiv;

            this.mXML.setAutoTuneROI(Left, Right, Top, Bottom);
            this.mXML.setAutotuneImaging(FOV, 0, 0, 0);
            if (Job.numOfJobs == 0)
            {
                this.BnC_user("AUTOFOCUS and AUTOSTIG BRIGHTNESS and CONTRAST: \n Set up your B&C for FOCUS and then press OK.", BC_TYPE.ESB_FOCUS);
            }
            this.mXML.setAutoTuneDetector(0, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_focus, this.m_fibicshandler.originalState.contrast_ESB_SEM_focus);
            this.mXML.commit();
            return true;
        }
        public bool Focus_user()
        {
            double bs_x_start, bs_y_start;
            double FOVx, FOVy;
            this.m_fibicshandler.getBeamShift(out bs_x_start, out bs_y_start);
            this.m_fibicshandler.getFOV(out FOVx, out FOVy);
            this.addMessage("PROMPT MESSAGE: Set up your focus and press ok.");
            try
            {
                Thread.Sleep(Timeout.Infinite);
            }
            catch (ThreadInterruptedException)
            {
                // this.addMessage("Resuming operations after FOCUS.");
                // Console.WriteLine("Acquisition '{0}' awoken.", Thread.CurrentThread.Name);
                // We assume the user has moved the BeamShift around
                double bs_x, bs_y;
                this.m_fibicshandler.getBeamShift(out bs_x, out bs_y);
                bs_x = bs_x - bs_x_start;
                bs_y = bs_y - bs_y_start;
                double fovx, fovy;
                this.m_fibicshandler.getFOV(out fovx, out fovy);
                // this.setAutotune((float)bs_x,(float) bs_y, (float)(fovx)); // without parameters, which will take the last beam shift as the position where to put the autotune box
                this.m_fibicshandler.setFOV(FOVx, FOVy);
                this.m_fibicshandler.setBeamShift(bs_x_start, bs_y_start);
            }
            return true;
        }
        public bool BnC_user(string message, BC_TYPE type)
        {
            double bs_x_start, bs_y_start;
            double FOVx, FOVy;
            this.m_fibicshandler.getBeamShift(out bs_x_start, out bs_y_start);
            this.m_fibicshandler.getFOV(out FOVx, out FOVy);
            this.addMessage("PROMPT MESSAGE: Set up your Brightness and Contrast and press ok." + message);
            try
            {
                Thread.Sleep(Timeout.Infinite);
            }
            catch (ThreadInterruptedException)
            {
                float newb, newc;
                this.m_fibicshandler.getBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_ESB, out newb, out newc);
                // by now we will only update ESB
                switch (type)
                { 
                    case BC_TYPE.ESB_FOCUS:
                        this.m_fibicshandler.originalState.brightness_ESB_SEM_focus = newb;
                        this.m_fibicshandler.originalState.contrast_ESB_SEM_focus = newc;
                        break;
                    case BC_TYPE.ESB_ACQUISITION:
                        this.m_fibicshandler.originalState.brightness_ESB_SEM_acq = newb;
                        this.m_fibicshandler.originalState.contrast_ESB_SEM_acq = newc;
                        break;
                    case BC_TYPE.ESB_TRENCH:
                        this.m_fibicshandler.originalState.brightness_ESB_SEM_trench = newb;
                        this.m_fibicshandler.originalState.contrast_ESB_SEM_trench = newc;
                        break;
                    default:
                        break;
                }
                this.m_fibicshandler.setFOV(FOVx, FOVy);
                this.m_fibicshandler.setBeamShift(bs_x_start, bs_y_start);
                this.addMessage("Resuming operations after setting BnC.");
            }
            return true;
        }
        public void pushBC()
        {
            string messages_event = "";
            int iChannel = 0;
            float newb, newc;
            for(int ndetector=0; ndetector<this.m_fibicshandler.m_pDetector.NumDetectors; ndetector++)
            {
                if (FibicsInterfaceHandler.SEM_ESB == this.m_fibicshandler.m_pDetector.getDetectorName(ndetector))
                {
                    iChannel = ndetector;
                }
            }
            
            newb = this.m_fibicshandler.m_pDetector.getChannelBrightness(iChannel);
            newc = this.m_fibicshandler.m_pDetector.getChannelContrast(iChannel);
            this.m_fibicshandler.originalState.brightness_ESB_SEM_acq = newb;
            this.m_fibicshandler.originalState.contrast_ESB_SEM_acq = newc;

            bool replaced = this.m_fibicshandler.m_pATLAS3D.MillImageUpdateDetectorROI(iChannel, newb, newc);

            if (replaced)
            {
                messages_event += "B&C replaced to new values :" + newb.ToString() + ","+newc.ToString()+"\n";

            }
        }
        /// <summary>
        /// Finds ideal starting focus
        /// </summary>
        /// <param name="imfolder"></param>
        /// <param name="setup_file_path"></param>
        /// <param name="roi"></param>
        /// <param name="trenchPoints"></param>
        /// <param name="terror"></param>
        /// <returns></returns>
        public ErrorCode AFASXFace(string imfolder, string setup_file_path, ref ROI roi, ref Dictionary<string, System.Drawing.PointF> trenchPoints, ref string terror, ref System.Drawing.PointF firstAFregion)
        {

            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_acq, this.m_fibicshandler.originalState.contrast_ESB_SEM_acq);

            // We need to be sure this condition is saved in case something goes wrong
            if (Job.numOfJobs == 0)
            {
                // this.Focus_user();
                StateImage original_state_image = new StateImage();
                this.m_fibicshandler.saveImageState(ref original_state_image);
                this.m_fibicshandler.originalState.sem_stigX = original_state_image.stigX;
                this.m_fibicshandler.originalState.sem_stigY = original_state_image.stigY;
                this.m_fibicshandler.originalState.sem_WD = original_state_image.WD;
            }

            // Grab points from the trench detected previously
            System.Drawing.PointF corner_1 = trenchPoints["corner1"];
            System.Drawing.PointF corner_2 = trenchPoints["corner2"];

            float dist_trench = Math.Abs(corner_1.X - corner_2.X);
            dist_trench = Math.Max(dist_trench, (float)roi.Width);
            // In case we want the full trench size as ROI. 
            if (this.m_job.fullROIWidth && (dist_trench - 6 > roi.Width)) //               
                this.mXML.setImagingOptions(dist_trench, 0, 0);
            roi.Width = dist_trench - 6; // 3 um left side by side to avoid see parts of the trench

            List<System.Drawing.PointF> fPoints = new List<System.Drawing.PointF>();
            string focus_imfolder = imfolder + "\\focus_f";
            bool exists = System.IO.Directory.Exists(focus_imfolder);
            if (!exists)
                System.IO.Directory.CreateDirectory(focus_imfolder);

            if (!this.detectFocusArea(dist_trench, imfolder, "ESB_1_", roi, ref fPoints, ref terror))
            {
                fPoints.Add(new System.Drawing.PointF(0f,corner_1.Y));
                fPoints.Add(new System.Drawing.PointF(-10f, corner_1.Y));
                fPoints.Add(new System.Drawing.PointF(+10f, corner_1.Y));
            }

            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_focus, this.m_fibicshandler.originalState.contrast_ESB_SEM_focus);
            System.Drawing.PointF[] regions = new System.Drawing.PointF[3];
            // Select a fixed quantity
            for (int i = 0; i < 3; i++)
            {
                regions[i] = fPoints[i];
            }
            firstAFregion = regions[0];

            
            if (!this.FocusOnXSRegions(regions, focus_imfolder, "1st_attempt", ref terror))
            {
                terror = terror + "\n Focus failed in first attempt.";
                this.addMessage(terror);
                // Now repeat but change close to the border with SESI 
                this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
                fPoints.Clear();
                // fPoints.Add(new System.Drawing.PointF(0f, -corner_1.Y*0.9f));
                // fPoints.Add(new System.Drawing.PointF(-10f, -corner_1.Y*0.9f));
                // fPoints.Add(new System.Drawing.PointF(+10f, -corner_1.Y*0.9f));
                detectFocusArea(dist_trench, imfolder, "SESI_2_", roi, ref fPoints, ref terror);
                try
                {
                    for (int i = 0; i < 3; i++)
                    {
                        regions[i] = fPoints[i];
                        regions[i].Y = regions[i].Y + 0.25f * regions[i].Y;
                    }
                    firstAFregion = regions[0];
                }
                catch (ArgumentOutOfRangeException)
                {
                    terror = terror + "\n Focus failed on cross section face points not found.";
                    this.addMessage(terror);
                    return ErrorCode.API_AUTOFOCUS_ON_XSECTION_FAILED;  // There were no AF points
                }

                if (!this.FocusOnXSRegions(regions, focus_imfolder, "2nd_attempt", ref terror))
                {
                    terror = terror + "\n Focus failed on cross section face at 2nd attempt. Cancelling auto AFAS.";
                    this.addMessage(terror);
                    this._end_AFASXFace(true);
                    return ErrorCode.API_AUTOFOCUS_ON_XSECTION_FAILED;
                }
            }

            this._end_AFASXFace(false);
            return ErrorCode.API_E_NO_ERROR;
        }
        public bool _end_AFASXFace(bool user_focus = false)
        {
            // Set ESB
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_ESB, this.m_fibicshandler.originalState.brightness_ESB_SEM_focus, this.m_fibicshandler.originalState.contrast_ESB_SEM_focus);
            // Save with the best state
            if (Job.numOfJobs == 0)
            {
                if (user_focus)
                {
                    this.Focus_user();
                    this.addMessage("Job will continue with user values.");
                }
                StateImage original_state_image = new StateImage();
                this.m_fibicshandler.saveImageState(ref original_state_image);
                this.m_fibicshandler.originalState.sem_stigX = original_state_image.stigX;
                this.m_fibicshandler.originalState.sem_stigY = original_state_image.stigY;
                this.m_fibicshandler.originalState.sem_WD = original_state_image.WD;
                return true;
            }
            else
            {
                if (user_focus)
                {
                    this.addMessage("ERROR:" + System.Environment.NewLine + ErrorCode.API_AUTOFOCUS_ON_XSECTION_FAILED.ToString() + ": AFAS not found.");
                    return false;
                }
            }
            return true;
        }


        /// <summary>
        /// Calls to a python routine that will identify Focus regions.
        /// </summary>
        /// <param name="dist_trench"></param>
        /// <param name="imfolder"></param>
        /// <param name="id_tag"></param>
        /// <returns></returns>
        public bool detectFocusArea(float dist_trench, string imfolder, string id_tag, ROI roi, ref List<System.Drawing.PointF> iPoints, ref string terror)
        {
            // Generate picture tags for quality control
            string c_time = string.Format("-{0:yyyy-MM-dd_hh-mm-ss-tt}", DateTime.Now);
            string tag = "focus_regions_" + id_tag + c_time;
            string image_name = imfolder + "\\" + tag + ".tif";

            // Grab images
            EmConf.focus_im.pixel_size = dist_trench * 0.001f;
            this.GrabFrameSEM(imfolder, tag, 1, EmConf.focus_im.pixel_size, EmConf.focus_im.dwell_time, EmConf.focus_im.line_average, 0, ref terror);

            // Detect all the points in the interface with high variance
            List<System.Drawing.Point> focusPoints = new List<System.Drawing.Point>();
            bool detected = false;
            // Detect points calling python routine
            detected = (this.m_imageHelper.DetectFocusPoints(image_name, tag, ref focusPoints));
            if (detected)
            {
                foreach (System.Drawing.Point hotpoint in focusPoints)
                {
                    // Calculate the shifting respect middle in pixel size
                    System.Drawing.PointF new_fp = new System.Drawing.PointF(EmConf.focus_im.pixel_size * hotpoint.X, EmConf.focus_im.pixel_size * hotpoint.Y);
                    if ((new_fp.Y < roi.Height *2) && (new_fp.X < roi.Width))
                    {
                        iPoints.Add(new_fp);
                    }
                }
                if (iPoints.Count < 3)
                {
                    return false;
                }
            }
            else
            {
                return false;
            }
            return true;
        }
        public bool FocusOnXSRegions(System.Drawing.PointF[] regions, string imfolder, string itag, ref string t_error)
        {
            // Save original state wd, stigs, and bs.
            StateImage original_state = new StateImage();
            StateImage afterAFAS_state = new StateImage();
            this.m_fibicshandler.saveImageState(ref original_state);

            string report = "";
            // Move to point
            float bs_x = (float)original_state.beam_shift_x + regions[0].X;
            float bs_y = (float)original_state.beam_shift_y + (float)(regions[0].Y * beamfactor36 * 0.9);
            this.m_fibicshandler.setBeamShift(bs_x, bs_y);
            //////////////////////////////////////////////////////////////
            // COARSE AFAS
            ////////////////////////////////////////////////////////////
            report = "Original wd is :" + original_state.WD;
            report += "\n  Original stigs are:" + original_state.stigX + "," + original_state.stigY;
            this.addMessage(report);
            if (!this._AFASXF(ref t_error, EmConf.onFace_COARSE, true, true, false))
            {
                this.m_fibicshandler.restoreImageState(original_state,true);
                t_error += "\n COARSE AFAS failed.";
                return false;
            }
            this.m_fibicshandler.saveImageState(ref afterAFAS_state);
            report = "AFAS first attempt COARSE, new wd:" + afterAFAS_state.WD;
            report += "\n AFAS success first attempt COARSE, new stigmators are:" + afterAFAS_state.stigX + "," + afterAFAS_state.stigY;
            this.addMessage(report);

            int ftimes = 1;
            string tag = "focus_coarse" + itag + ftimes;
            this.GrabFrameSEM(imfolder, tag, 0, EmConf.focus_CORR.pixel_size, EmConf.focus_CORR.dwell_time, 1, 0, ref t_error);
            ftimes++;
            //////////////////////////////////////////////////////////////
            // MEDIUM  
            ////////////////////////////////////////////////////////////
            float bs_x_1 = (float)original_state.beam_shift_x + regions[1].X;
            float bs_y_1 = (float)original_state.beam_shift_y + (float)(regions[1].Y * beamfactor36);
            this.m_fibicshandler.setBeamShift(bs_x_1, bs_y_1);
            if (!this._AFASXF(ref t_error, EmConf.onFace_MEDIUM, true, true, false))
            {
                this.m_fibicshandler.restoreImageState(afterAFAS_state, true); // after is still the previous one
                t_error += "\n MEDIUM AFAS failed.";
                return false;
            }
            this.m_fibicshandler.saveImageState(ref afterAFAS_state);
            report = "AFAS first attempt MEDIUM, new wd:" + afterAFAS_state.WD;
            report += "\n AFAS success first attempt MEDIUM, new stigmators are:" + afterAFAS_state.stigX + "," + afterAFAS_state.stigY;
            this.addMessage(report);
            //////////////////////////////////////////////////////////////
            // MEDIUM 2  
            ////////////////////////////////////////////////////////////
            if (!this._AFASXF(ref t_error, EmConf.onFace_MEDIUM_2))
            {
                this.m_fibicshandler.restoreImageState(afterAFAS_state); // after is still the previous one
                t_error += "MEDIUM 2nd AFAS failed.";
                return false;
            }
            this.m_fibicshandler.saveImageState(ref afterAFAS_state);
            report = "AFAS first attempt MEDIUM 2nd part, new wd:" + afterAFAS_state.WD;
            report += "\n AFAS success first attempt MEDIUM 2nd part, new stigmators are:" + afterAFAS_state.stigX + "," + afterAFAS_state.stigY;
            this.addMessage(report);

            tag = "focus_medium" + itag + ftimes;
            this.GrabFrameSEM(imfolder, tag, 0, EmConf.focus_CORR.pixel_size, EmConf.focus_CORR.dwell_time, 1, 0, ref t_error);
            ftimes++;
            //////////////////////////////////////////////////////////////
            // FINE  Don't need to move after coarse
            ////////////////////////////////////////////////////////////
            float bs_x_2 = (float)original_state.beam_shift_x + regions[2].X;
            float bs_y_2 = (float)original_state.beam_shift_y + (float)(regions[2].Y * beamfactor36);
            this.m_fibicshandler.setBeamShift(bs_x_2, bs_y_2);

            if (!this._AFASXF(ref t_error, EmConf.onFace_FINE))
            {
                this.m_fibicshandler.restoreImageState(afterAFAS_state);
                this.m_fibicshandler.setBeamShift((float)original_state.beam_shift_x, (float)original_state.beam_shift_y);
                this.mXML.setInitialFocus(afterAFAS_state.WD);
                this.mXML.commit();
                return true; // We hope resolution is good enough with MEDIUM
            }
            this.m_fibicshandler.saveImageState(ref afterAFAS_state);
            report = "AFAS first attempt FINE, new wd:" + afterAFAS_state.WD;
            report += "\n AFAS success first attempt FINE, new stigmators are:" + afterAFAS_state.stigX + "," + afterAFAS_state.stigY;
            this.addMessage(report);
            tag = "focus_fine" + itag + ftimes;
            this.GrabFrameSEM(imfolder, tag, 0, EmConf.focus_CORR.pixel_size, EmConf.focus_CORR.dwell_time, 1, 0, ref t_error);
            ftimes++;

            this.m_fibicshandler.setBeamShift((float)original_state.beam_shift_x, (float)original_state.beam_shift_y);
            this.mXML.setInitialFocus(afterAFAS_state.WD);
            this.mXML.commit();
            return true;


        }
        public bool _AFASXF(ref string m_error, AFAS_settings settings, bool f1 = true, bool f2 = true, bool f3 = true, bool retry = true)
        {
            Atlas5.FibicsAFASEnum status;
            if (f1)
            {
                status = this.m_fibicshandler.doAutoFocus(settings.focus.pixel_size, settings.range_focus, settings.focus.dwell_time, settings.focus.line_average);
                switch (status)
                {
                    case (Atlas5.FibicsAFASEnum.afsRejected):
                    case (Atlas5.FibicsAFASEnum.afsUnknownError):
                        this.addMessage("Focus Failed in first attempt.");
                        if (retry)
                        {
                            status = this.m_fibicshandler.doAutoFocus(settings.focus.pixel_size, settings.range_focus * 2, settings.focus.dwell_time + 1, settings.focus.line_average + 1);
                            if (status == Atlas5.FibicsAFASEnum.afsRejected)
                            {
                                m_error = "We were not able to focus. Focus manually or move to the next sample.";
                                return false;
                            }

                        }
                        else
                        {
                            return false;
                        }
                        break;
                    default:
                        break;
                }
            }
            if (f2)
            {
                status = this.m_fibicshandler.doAutoStig(settings.stigs.pixel_size, settings.range_stig, settings.stigs.dwell_time, settings.stigs.line_average);
                switch (status)
                {
                    case (Atlas5.FibicsAFASEnum.afsRejected):
                    case (Atlas5.FibicsAFASEnum.afsUnknownError):
                        this.addMessage("Stig Failed in first attempt.");
                        if (retry)
                        {
                            status = this.m_fibicshandler.doAutoFocus(settings.focus.pixel_size, settings.range_focus * 2, settings.focus.dwell_time + 1, settings.focus.line_average + 1);
                            status = this.m_fibicshandler.doAutoStig(settings.stigs.pixel_size, settings.range_stig * 2, settings.stigs.dwell_time + 1, settings.stigs.line_average + 1);
                            if (status == Atlas5.FibicsAFASEnum.afsRejected)
                            {
                                m_error = "We were not able to autostig. Focus manually or move to the next sample.";
                                return false;
                            }
                        }
                        else
                        {
                            return false;
                        }
                        break;
                    default:
                        break;
                }
            }
            if (f3)
            {
                status = this.m_fibicshandler.doAutoFocus(settings.focus.pixel_size, settings.range_focus, settings.focus.dwell_time, settings.focus.line_average);
                switch (status)
                {
                    case (Atlas5.FibicsAFASEnum.afsRejected):
                    case (Atlas5.FibicsAFASEnum.afsUnknownError):
                        {
                            m_error = "We were not able to focus. Focus manually or move to the next sample.";
                            return false;
                        }
                    default:
                        break;
                }
            }
            return true;
        }

        /****On surface sample*********/
        public bool autoFocusOnSample(ref string m_error, string detector, ref PointEM currentPosition, int trials = 2)
        {
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
            double old_wd = this.m_fibicshandler.getWD();
            double old_stigx, old_stigy, stigx, stigy, new_wd;
            this.m_fibicshandler.getStigs(out old_stigx, out old_stigy);

            var status = this.m_fibicshandler.doAutoFocus(EmConf.onSample_MEDIUM.focus.pixel_size, EmConf.onSample_MEDIUM.range_focus, EmConf.onSample_MEDIUM.focus.dwell_time, EmConf.onSample_MEDIUM.focus.line_average);

            switch (status)
            {
                case (Atlas5.FibicsAFASEnum.afsRejected):
                    this.addMessage("Focus Failed in first attempt.");
                    status = this.m_fibicshandler.doAutoFocus(EmConf.onSample_COARSE.focus.pixel_size, EmConf.onSample_COARSE.range_focus, EmConf.onSample_COARSE.focus.dwell_time + 1, 2);
                    if (status == Atlas5.FibicsAFASEnum.afsRejected)
                    {
                        if (trials == 1)
                        {
                            this.addMessage("We were not able to focus. Focus manually or move to the next sample.");
                            m_error = "Focus not achieved in autoFocusOnSample.";
                            return false;
                        }
                        // Make a small fib mark and try again, generating a black feature...
                        // Grab image FIB
                        // TO DO: Check if FIB is open first
                        this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeFIB, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_FIB, this.m_fibicshandler.originalState.contrast_sesi_FIB);
                        this.m_fibicshandler.setFIBAperture("30kV:3nA");
                        string tmp_folder = Path.GetTempPath();
                        string c_time = string.Format("-{0:yyyy-MM-dd_hh-mm-ss-tt}", DateTime.Now);
                        string fib_burn = "s_fib_burn" + c_time;
                        this.m_fibicshandler.GrabFrameFIB(tmp_folder, fib_burn, 2, 0, 0.3 * 0.1, 12, 3, 0.0, ref m_error); // mark square 3 times
                        // Go back to SEM
                        this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);

                        // Second refinement
                        status = this.m_fibicshandler.doAutoFocus(EmConf.onSample_COARSE.focus.pixel_size, EmConf.onSample_COARSE.range_focus, EmConf.onSample_COARSE.focus.dwell_time + 1, 2);
                        if (status == Atlas5.FibicsAFASEnum.afsRejected)
                        {
                            this.addMessage("We were not able to focus. Focus manually or move to the next sample.");
                            m_error = "Focus not achieved in autoFocusOnSample.";
                            return false;
                        }
                    }

                    new_wd = this.m_fibicshandler.getWD();
                    this.m_fibicshandler.getStigs(out stigx, out stigy);
                    m_error = "Autofocus success: old wd was :" + old_wd + ", new wd is now:" + new_wd;
                    //  m_error += "Autostig success: old x,y were:" + old_stigx + "," + old_stigy + ", new stig x and stig y are now:" + stigx + "," + stigy;
                    return true;
                case (Atlas5.FibicsAFASEnum.afsSuccess):
                    new_wd = this.m_fibicshandler.getWD();
                    this.m_fibicshandler.getStigs(out stigx, out stigy);
                    m_error = "Autofocus success: old wd was :" + old_wd + ", new wd is now:" + new_wd;
                    //  m_error += "Autostig success: old x,y were:" + old_stigx + "," + old_stigy + ", new stig x and stig y are now:" + stigx + "," + stigy;

                    return true;
            }
            m_error = "UNKNOWN error in autofocus on sample.";
            return false;
        }

        
               
        /**** Emergency AFAS****/
        public bool AFASEmergency(ref string m_error, string detector, ref PointEM currentPosition)
        {
            string terror = "";
            // Save state
            this.m_fibicshandler.setDetector(FibicsInterfaceHandler.typeSEM, detector);
            // get current FOV
            double fovx, fovy;
            this.m_fibicshandler.getFOV(out fovx, out fovy);

            if (!this._AFASXF(ref terror, EmConf.onFace_COARSE, true, true, false, false))
            {
                terror += "EMERGENCY on Face AFAS failed.";
                terror += "Trying with COARSE.";
                if (!this.autoFocusOnSample(ref terror, FibicsInterfaceHandler.SEM_SESI, ref currentPosition))
                {
                    return false;
                }
            }
            this.m_fibicshandler.setDetector(FibicsInterfaceHandler.typeSEM, detector);
            this.m_fibicshandler.setFOV(fovx, fovy);
            
string report = "AFAS Emergency successfuly executed, new wd:" + this.m_fibicshandler.getWD();
            double sx, sy;
            this.m_fibicshandler.getStigs(out sx, out sy);
            report += "\n New stigmators are:" + sx + "," + sy;
            this.addMessage(report);
            return true;
        }

        
        /***** Status Reporting *****/
        /// <summary>
        /// getMessage
        /// </summary>
        /// <returns></returns>
        public string getMessage()
        {
            string message = "NO MESSAGES";
            lock (syncLock)
            {
                if (BufferRun.messageAvailable())
                {
                    return BufferRun.getLastMessage();
                }

            }
            return message;

        }
        /// <summary>
        /// addMessage
        /// </summary>
        /// <param name="message"></param>
        public void addMessage(string message)
        {
            lock (syncLock)
            {
                String timeStamp = DateTime.Now.ToString();             
                MainForm.Log(message);
                message = timeStamp + " " + message;
                BufferRun.addMessage(message);
            }

        }
        public void reduceMessages()
        {
            lock (syncLock)
            {
                BufferRun.shrinkToOne();
            }
        }
        public bool isResumed(ref string error, float msToWait = 500000)
        {
            AtlasMillImageStatusEnum Status = 0;
            Stopwatch sw = new Stopwatch();
            sw.Start();

            while (Status != AtlasMillImageStatusEnum.MillImageisExecuting && sw.ElapsedMilliseconds < msToWait)
            {
                this.m_fibicshandler.m_pATLAS3D.MillImageResume();
                Status = this.m_fibicshandler.m_pATLAS3D.MillImageStatus();
                switch (Status)
                {
                    case AtlasMillImageStatusEnum.MillImageisCancelled:
                        error = "FUNCTION Milling isResumed: ERROR Cancelled.";
                        return false;
                    case AtlasMillImageStatusEnum.MillImageisError:
                        error = "FUNCTION Milling isResumed: ERROR during Milling.";
                        error += this.m_fibicshandler.m_pATLAS3D.MillImageLastErrorMsg();
                        return false;
                    case AtlasMillImageStatusEnum.MillImageisComplete:
                    case AtlasMillImageStatusEnum.MillImageisIdle:
                    case AtlasMillImageStatusEnum.MillImageisMilling:
                        return true;
                    case AtlasMillImageStatusEnum.MillImageisPaused:
                        Thread.Sleep(100); // Release some load and check every second
                        continue;
                    default:
                        continue;
                }

            }
            sw.Stop();
            if (sw.ElapsedMilliseconds > msToWait)
            {
                error += "FUNCTION Milling isResumed: ERROR Timed out.";
                return false;
            }
            return true;
        }
        public bool isPaused(ref string error, float msToWait = 500000)
        {
            AtlasMillImageStatusEnum Status = 0;
            Stopwatch sw = new Stopwatch();
            sw.Start();

            while (Status != AtlasMillImageStatusEnum.MillImageisPaused && sw.ElapsedMilliseconds < msToWait)
            {
                Status = this.m_fibicshandler.m_pATLAS3D.MillImageStatus();

                switch (Status)
                {
                    case AtlasMillImageStatusEnum.MillImageisCancelled:
                        error = "FUNCTION Milling isPaused: ERROR Cancelled.";
                        return false;
                    case AtlasMillImageStatusEnum.MillImageisError:
                        error = "FUNCTION Milling isPaused: ERROR during Milling.";
                        error += this.m_fibicshandler.m_pATLAS3D.MillImageLastErrorMsg();
                        return false;
                    case AtlasMillImageStatusEnum.MillImageisComplete:
                    case AtlasMillImageStatusEnum.MillImageisIdle:
                    case AtlasMillImageStatusEnum.MillImageisExecuting:
                    case AtlasMillImageStatusEnum.MillImageisMilling:
                        Thread.Sleep(100); // Release some load and check every second
                        continue;
                    default:
                        continue;
                }
            }
            sw.Stop();
            if (sw.ElapsedMilliseconds > msToWait)
            {
                error += "FUNCTION Milling isPaused: ERROR Timed out.";
                return false;
            }
            return true;
        }
        public bool isMillStatus(string query, ref string error, float msToWait = 500000)
        {
            AtlasMillImageStatusEnum Status = 0;
            Stopwatch sw = new Stopwatch();
            sw.Start();
            AtlasMillImageStatusEnum desired_status = AtlasMillImageStatusEnum.MillImageisIdle;

            if (query.CompareTo("READY") == 0)
            {
                desired_status = AtlasMillImageStatusEnum.MillImageisIdle;
            }

            if (query.CompareTo("COMPLETE") == 0)
            {
                desired_status = AtlasMillImageStatusEnum.MillImageisComplete;
            }


            while (Status != desired_status && sw.ElapsedMilliseconds < msToWait)
            {
                Status = this.m_fibicshandler.m_pATLAS3D.MillImageStatus();

                switch (Status)
                {
                    case AtlasMillImageStatusEnum.MillImageisCancelled:
                        error = "FUNCTION during is isMillStatus: ERROR Cancelled.";
                        return false;
                    case AtlasMillImageStatusEnum.MillImageisError:
                        error = "FUNCTION is isMillStatus: ERROR during Milling.";
                        error += this.m_fibicshandler.m_pATLAS3D.MillImageLastErrorMsg();
                        return false;
                    case AtlasMillImageStatusEnum.MillImageisComplete:
                        sw.Stop();
                        return true;
                    case AtlasMillImageStatusEnum.MillImageisIdle:
                        break;
                    case AtlasMillImageStatusEnum.MillImageisPaused:
                    case AtlasMillImageStatusEnum.MillImageisExecuting:
                        break;
                    case AtlasMillImageStatusEnum.MillImageisMilling:
                        continue;
                    default:
                        error = "FUNCTION MillImageStatus:ERROR Unsuccesful operational state. Check the microscope state.";
                        error += "-- ERROR code: " + Status.ToString();
                        return false;
                }
            }
            sw.Stop();
            if (sw.ElapsedMilliseconds > msToWait)
            {
                error += "FUNCTION MillImageStatus: ERROR Timed out.";
                return false;
            }
            return true;
        }
        public bool isStatusReady(ref string error)
        {
            int Status = 0;
            Stopwatch sw = new Stopwatch();
            sw.Start();

            // this call writes an integer into Status
            // if the worker thread earlier failed with an error, it instead raises an excpetion with that message
            // once that exception is raised the worker error message is erased 
            // subsequent calls will not raise an exception until the worker thread encounters a new error
            // I realize this one isn't a super interface, but it works for now.

            // 0 = The Atlas3D GUI has not yet been launched
            // 1 = The Atlas3D GUI has been closed.
            // 2 = Worker is ready. SetupRun has been successfully called.
            // 3 = Worker is busy with Prep
            // 4 = Worker is busy with A3D Run
            // 5 = Worker is in an unexpected state

            while (Status != 2 && sw.ElapsedMilliseconds < 500000)
            {
                Status = this.m_fibicshandler.m_pATLAS3D.Status;
                switch (Status)
                {
                    case 0:
                        error = "FUNCTION StartSample: ERROR GUI has not been launched.";
                        return false;
                    case 1:
                        error = "FUNCTION StartSample: ERROR GUI closes.";
                        return false;
                    case 2:
                        break;
                    case 3:
                    case 4:
                        continue;
                    case 5:
                    default:
                        error = "FUNCTION StartSample:ERROR Unsuccesful operational state. Check the microscope state.";
                        return false;
                }
            }
            sw.Stop();
            if (sw.ElapsedMilliseconds > 5000000)
            {
                error = "FUNCTION StartSample:Unsuccesful operational state. ERROR Check the microscope state.";
                return false;
            }
            return true;
        }
        public void AcquisitionStatus()
        {
            AtlasMillImageStatusEnum c_status;

            lock (syncLock)
            {
                if (this.apiInitialised)
                {

                    c_status = this.m_fibicshandler.m_pATLAS3D.MillImageStatus();
                }
                else
                {
                    return;
                }
            }

            string error = "";
            switch (c_status)
            {
                case AtlasMillImageStatusEnum.MillImageisCancelled:
                    {
                        this.cancelRun();
                        return;
                    }
                case AtlasMillImageStatusEnum.MillImageisError:
                    {
                        this.addMessage(this.m_fibicshandler.m_pATLAS3D.MillImageLastErrorMsg());
                        this.errorRun();
                        break;
                    }
                case AtlasMillImageStatusEnum.MillImageisComplete:
                    {
                        this.completeRun();

                        return;
                    }
                case AtlasMillImageStatusEnum.MillImageisIdle:
                    return;
                case AtlasMillImageStatusEnum.MillImageisPaused:
                    this.pauseRun();
                    break;
                case AtlasMillImageStatusEnum.MillImageisExecuting:
                case AtlasMillImageStatusEnum.MillImageisMilling:
                    break;
                default:
                    {
                        error = "FUNCTION AcquisitionStatus:ERROR Unsuccesful operational state. Check the microscope state.";
                        error = error + "-- ERROR code: " + c_status.ToString();
                        error += this.m_fibicshandler.m_pATLAS3D.MillImageLastErrorMsg();
                        this.addMessage(error);
                        this.errorRun();
                        break;
                    }
            }
            string log = this.m_fibicshandler.getMessageLog();
            try
            {
                string[] messages = log.Split(new char[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
                if ((messages.Length == 0)||(log == old_log))   return; 
                else
                {
                    this.addMessage(log);
                    old_log = log;
                }
            }
            catch (System.NullReferenceException e)
            {
                this.addMessage("ERROR acquiring message from LOG!!! \n" + e.ToString());
                return;
            }
        }


        /*** CONTROLS ***/
        public void completeRun()
        {
            lock (syncLock)
            { // synchronize
                string error = "";
                if (this.isImaging())
                {

                    this.m_fibicshandler.m_pATLAS3D.MillImageStop();
                    if (!isMillStatus("READY", ref error, 50000000))
                    {
                        this.addMessage(error);
                        return;
                    }
                    Thread.Sleep(30000);
                    this.NeedsTrack = false;
                    this.NeedsAFASbox = false;
                    this.MessageObj.TimerCanceled = true; // Request Dispose of the timer object.
                                                          // Stop other tasks
                    this.is_imaging = false;
                    AtlasCom.black_watcher.EnableRaisingEvents = false;
                    AtlasCom.black_watcher.Renamed -= new RenamedEventHandler(OnChanged);
                    this.m_fibicshandler.m_pATLAS3D.closeRun();
                }

                this.reduceMessages();
                Job.state = "COMPLETED";

                this.Disconnect(ref error);
            }
            this.addMessage("Job completed.");
        }
        public void pauseRun()
        {
            lock (syncLock)
            { // synchronize
                this.m_fibicshandler.m_pATLAS3D.MillImagePause();
                Job.state = "PAUSED";
            }
            this.addMessage("Mill Image PAUSED.");
        }
        public void resumeRun()
        {
            string terror = "";
            lock (syncLock)
            { // synchronize
                this.m_fibicshandler.m_pATLAS3D.MillImageResume();
                this.isResumed(ref terror);
                Job.state = "RUNNING";
            }
            this.addMessage(terror + "Mill Image Resumed.");
        }
        public void cancelRun()
        {
            lock (syncLock)
            { // synchronize
                string error = "";
                if (this.isImaging())
                {

                    this.m_fibicshandler.m_pATLAS3D.MillImageStop();

                    if (!isMillStatus("READY", ref error, 50000000))
                    {
                        return;
                    }

                    Job.state = "CANCELLED";
                    // Request Dispose of the timer object.
                    this.MessageObj.TimerCanceled = true;
                    // Stop the Filewatcher
                    // Stop other tasks
                    this.is_imaging = false;
                    this.NeedsTrack = false;
                    this.NeedsAFASbox = false;
                    AtlasCom.black_watcher.EnableRaisingEvents = false;
                    AtlasCom.black_watcher.Renamed -= new RenamedEventHandler(OnChanged);
                    this.m_fibicshandler.m_pATLAS3D.cancelRun();

                }
                else
                {
                    Job.state = "CANCELLED";

                }
                this.addMessage("RUN CANCELLED.");
                this.reduceMessages();
                this.Disconnect(ref error);
            }
            return;
        }
        public void errorRun()
        {
            lock (syncLock)
            { // synchronize
                if (this.isImaging())
                {

                    this.MessageObj.TimerCanceled = true; // Request Dispose of the timer object.                                                  
                    this.is_imaging = false;
                    AtlasCom.black_watcher.EnableRaisingEvents = false;
                    AtlasCom.black_watcher.Renamed -= new RenamedEventHandler(OnChanged);
                    this.m_fibicshandler.m_pATLAS3D.cancelRun();
                }
                this.reduceMessages();
                Thread.Sleep(20000);
                Job.state = "ERROR";
                string error = "";
                MainForm.setStatusError(true);
                this.Disconnect(ref error);
            }
        }

        /* BACKGROUND TASKS during RUN*/

        private void TimerTask(object StateObj)
        {
            StateObjClass State = (StateObjClass)StateObj;
            this.AcquisitionStatus();
            if (State.TimerCanceled)
            // Dispose Requested.
            {
                State.TimerReference.Dispose();
                System.Diagnostics.Debug.WriteLine("Acquisition Done  " + DateTime.Now.ToString());
            }
        }

        public static bool IsFileReady(String sFilename)
        {
            // If the file can be opened for exclusive access it means that the file
            // is no longer locked by another process.
            try
            {
                using (FileStream inputStream = File.Open(sFilename, FileMode.Open, FileAccess.Read, FileShare.None))
                {
                    if (inputStream.Length > 0)
                    {
                        return true;
                    }
                    else
                    {
                        return false;
                    }

                }
            }
            catch (Exception)
            {
                return false;
            }
        }


        /*****************************************/

        public static int GetRandomNumber(int min, int max)
        {
            lock (syncLock)
            { // synchronize
                return getrandom.Next(min, max);
            }
        }

        /***** Interface methods to protect the FIBICS handler ***/
        public StateFIBSEM getState()
        {
            return this.m_fibicshandler.originalState;
        }
        public void GetStagePosition(ref PointEM position, ref string m)
        {
            this.m_fibicshandler.GetStagePosition(ref position, ref m);
            return;
        }
        public void safeMove(PointEM position, string scale, ref string m)
        {
            this.m_fibicshandler.safeMove(position, scale, ref m);
            return;
        }

        /************Independent Modules******************/
        /*** NOT IMPLEMENTED**/
        public void doDeposition()
        {

            // OutGassing of Platinum
            // Close FIB Valve
            // Close SEM EHT
            // Call SMARTSEM to close valve FIB
            // Call SMARTSEM to close valve SEM 

            Thread.Sleep(500);
            // Select Platinum

            int numOfGasses = this.m_fibicshandler.m_GIS.GetGasCount();

            string gas_name;
            int gas_id, gas_id_2;
            Dictionary<string, int> gas_apertures_map = new Dictionary<string, int>();
            for (int i = 0; i < numOfGasses; i++)

            {
                gas_name = this.m_fibicshandler.m_GIS.GetGasName(i);
                gas_id = this.m_fibicshandler.m_GIS.GetGasID(i);
                if (gas_apertures_map.TryGetValue(gas_name, out gas_id_2))
                {
                    Console.WriteLine("Repeated:" + gas_name);
                }
                else
                {
                    gas_apertures_map.Add(gas_name, gas_id);
                }

                System.Console.WriteLine("Gas #{0}:{1},{2}", i, gas_id, gas_name);
                System.Console.WriteLine();

            }
            //  Select Platinum
            // if (!this.m_fibicshandler.m_GIS.IsGasReady(gas_apertures_map["Platinum"]))
            // {
            //    this.m_fibicshandler.m_GIS.PrepareGas(gas_apertures_map["Platinum"]);
            // }
           

            // Do a loop 5 times
            //      this.m_fibicshandler.m_GIS.OpenValve()
            //      Thread.Sleep(10000);
            //      this.m_fibicshandler.m_GIS.CloseValve()   
            
            // Insert Nozzle and check if needs initialization or what
            //if (this.m_fibicshandler.m_GIS.IsNozzleParked())
            // {   
            //    Insert Nozzle SetNozzlePosition(gasID)
            // }


            // Run deposition
            // Potentially the patterning class FibicsPatterningClass can do it.
            // I could guess, I would probably though, need instructions. 
        }


        // Generates a Mark using the FIB that can be used to compute shifts between kV's or to mark the position for detection
        public void FIBMark(string frame_directory, float distance_x, float distance_y )
        {
            bool exists = System.IO.Directory.Exists(frame_directory);
            if (!exists)
                System.IO.Directory.CreateDirectory(frame_directory);
            string m_error = "";
            // Get current stage position 
            PointEM currentPosition = new PointEM();
            this.m_fibicshandler.GetStagePosition(ref currentPosition, ref m_error);
            PointEM nextPosition = new PointEM(currentPosition);
            // Invert positions (ATLAS uses negative coordinates)
            if (nextPosition.x > 0)
                nextPosition.x = -nextPosition.x;
            if (nextPosition.y > 0)
                nextPosition.y = -nextPosition.y;

            nextPosition.x = nextPosition.x - distance_x;
            nextPosition.y = nextPosition.y - distance_y;

            if (!this.m_fibicshandler.safeMove(currentPosition, "micrometer", ref m_error))
            {
                this.addMessage(m_error);
                return;
            }
            // Create temporary folder
            string c_time = string.Format("-{0:yyyy-MM-dd_hh-mm-ss-tt}", DateTime.Now);
            string sem_before = "SEM_1st_original_" + c_time;
            string sem_after = "SEM_1st_square_burned_" + c_time;
            string fib_burn = "fib_burn" + c_time;
            
            // Grab sem image
            this.m_fibicshandler.GrabFrameSEM(frame_directory, sem_before, 0, EmConf.cp_im.pixel_size, EmConf.cp_im.dwell_time, EmConf.cp_im.line_average, 0.0, ref m_error);

            // Grab image FIB
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeFIB, FibicsInterfaceHandler.FIB_SESI, this.m_fibicshandler.originalState.brightness_sesi_FIB, this.m_fibicshandler.originalState.contrast_sesi_FIB);
            this.m_fibicshandler.setFIBAperture("30kV:3nA");
            this.m_fibicshandler.GrabFrameFIB(frame_directory, fib_burn, 2, 0, EmConf.cp_im.pixel_size * 0.1, 12, 3, 0.0, ref m_error); // mark square 3 times

            // Go back to SEM
            this.m_fibicshandler.setBnC(FibicsInterfaceHandler.typeSEM, FibicsInterfaceHandler.SEM_SESI, this.m_fibicshandler.originalState.brightness_sesi_SEM, this.m_fibicshandler.originalState.contrast_sesi_SEM);
            this.m_fibicshandler.GrabFrameSEM(frame_directory, sem_after, 0, EmConf.cp_im.pixel_size, EmConf.cp_im.dwell_time, EmConf.cp_im.line_average, 0.0, ref m_error);

            string image_SEM_before = frame_directory + "\\" + sem_before + ".tif";
            string image_SEM_after = frame_directory + "\\" + sem_after + ".tif";

            return;
        }

        // EXPERIMENTAL: for standalone set up of CLEMSite
        // Activates tracking and autotune box positioning
        public void autoTracking(Job currentJob)

        {
            // Generate Job class
            //  we consider already everything in proper position
            //  Call Phase 3 
            this.m_job = currentJob;
            string error = "";
            PointEM cpos = new PointEM();
            this.GetStagePosition(ref cpos, ref error);
            this.StartAcquisition(currentJob, cpos, ref error);
        }

        // Grab SEM images
        public void GrabFrameSEM(string frame_directory, string imagename, int resolution, float pixelSize, float dwellTime, int lineavg, int scanrotation, ref string error)
        {
            this.m_fibicshandler.GrabFrameSEM(frame_directory, imagename, resolution, pixelSize, dwellTime, lineavg, scanrotation, ref error);
        }
        public void doSmartSEMCommand(string v1, string v2, ref float fvalue, ref string e)
        {
            this.m_fibicshandler.doSmartSEMCommand(v1, v2, ref fvalue, ref e);
        }
        public void setFOV(ref string message, float newFOV)
        {
            this.m_fibicshandler.m_pSEMVE.FOV = newFOV;

        }

        private void OnChanged(object source, FileSystemEventArgs e)
        {
            // Specify what is done when a file is changed, created, or deleted.
            this.addMessage("File: " + e.FullPath + " " + e.ChangeType);
            string messages_event = "";
            String timeStamp = DateTime.Now.ToString();
            messages_event += timeStamp;
            string ifolder = Path.GetDirectoryName(e.FullPath);

            // Point to focus
            System.Drawing.PointF pointAFAS = new System.Drawing.PointF();
            // Offset to move for tracking
            System.Drawing.PointF pointOffset = new System.Drawing.PointF();

            int remslices = 0;

            // Counter of slices, in case we want to disable tracking for a certain period
            // this is needed, so we don't do tracking after tracking just happened (we always have 1 slice delay) 

            if (this._noTrack > 0) this._noTrack--;

            double Width = this.m_job.roi.Width;
            double Height = this.m_job.roi.Height;
            bool cancel = false;
            bool mtrack = false;
            bool mafasbox = false;
         
            this.m_imageHelper.runChecker("r" + this.m_job.jobId, e.FullPath, this.m_job.autotune_period, ref pointAFAS, ref mtrack, ref mafasbox, ref pointOffset, ref remslices,ref cancel);

            this.NeedsAFASbox = mafasbox;
            this.NeedsTrack = mtrack;

            lock (syncLock) // Avoid other threads to came in
            {
                if (!this.apiInitialised)
                {
                    // Avoid problems with closing after completion
                    return;
                }
                if (cancel)
                {
                    this.completeRun();
                    this.addMessage("RUN Automatically finished by Runchecker.");
                    return;
                }

                try
                {
                    if (this.NeedsTrack || this.NeedsAFASbox)
                    {
                        // First priority, move the AFASbox
                        if (NeedsAFASbox)
                        {
                            bool replaced =
                                this.m_fibicshandler.m_pATLAS3D.MillImageUpdatePositionAutoTune(pointAFAS.X,
                                    pointAFAS.Y);
                            if (replaced)
                            {
                                messages_event += "AutotuneBox replaced to position :" + pointAFAS.ToString() + "\n";
                                this._noTrack =
                                    1; // Leave a buffer of slices before tracking again so we prevent moving the AFAS position
                            }
                        }
                    }

                    if (NeedsTrack && this._noTrack < 1)
                    {
                        messages_event += "Changing FOV box.\n";
                        bool success =
                            this.m_fibicshandler.m_pATLAS3D.MillImageUpdateROI(pointOffset.X, pointOffset.Y, Width,
                                Height);
                        if (success)
                        {
                            messages_event += "FOV moved to position :" + pointOffset.ToString();
                        }
                    }
                }
                catch (System.Runtime.InteropServices.COMException)
                {
                    return;
                }

                messages_event += ("Check Succeeded for " + e.FullPath);
            }
            this.addMessage(messages_event);
            return;
        }
        private void changeAFAS(double focus, double stigx, double stigy)
        {
            StateImage afas_state = new StateImage(focus, stigx, stigy);
            this.m_fibicshandler.restoreImageState(afas_state, false); // after is still the previous one
        }
    
        /** MISC Functions **/
        /// <summary>
    /// Returns a normalized path for windows with a corrected separator
    /// </summary>
    /// <param name="path"></param>
    /// <returns></returns>
        public static string NormalizePath(string path)
    {
        return Path.GetFullPath(new Uri(path).LocalPath)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                .ToUpperInvariant();
    }

        /// checkNSet XML File
        /// <summary>
        /// Checks XML File if it is well-formed otherwise tries to access to the local source 
        /// NOTE: This function was done to avoid a possible bug with XML corruption, already corrected.
        /// However has been left for safety reasons.
        /// </summary>
        /// <param name="setup_path"></param>
        /// <param name="alt_setup_path"></param>
        /// <param name="error"></param>
        /// <returns></returns>
        public bool checkNSetXMLFile(string setup_path, string alt_setup_path, ref string error)
    {
        if (!this.mXML.setXMLFile(setup_path, ref error))
        {
            // We have transmission error of the setup file
            // Then we can check if we are in local...
            if (IPAddress.IsLoopback(AsynchronousSocketListener.ipAddress)) //we are in local
            {
                if (File.Exists(setup_path))
                    File.Delete(setup_path);
                // get address of file 
                // copy it to the profile path
                File.Copy(alt_setup_path, setup_path);
                this.addMessage("ERROR 0020: There was an error during the transmission of file.\n Since we are in local, the file has been directly copied.");
                return true;
            }
            return false;
        }
        return true;
    }

}

}