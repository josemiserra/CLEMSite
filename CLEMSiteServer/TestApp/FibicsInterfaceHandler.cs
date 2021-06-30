using System;
using System.Collections.Generic;
using Atlas5;
using System.Diagnostics;
using System.Threading;
using System.Windows;
using System.Collections;


namespace msite
{

    public class FibicsInterfaceHandler
    {

        // The various interfaces to the Engine we will use
        private IFibicsSystemController m_pEngine { get; set; }
        public IFibicsSEMVE m_pSEMVE { get; set; }
        public IFibicsStageController m_pStage { get; set; }
        public IFibicsATLAS3D m_pATLAS3D { get; set; }
        public IFibicsATLAS m_pATLAS { get; set; }
        public IFibicsSmartSEMInterface m_SEMApi { get; set; }
      //  public IFibicsImaging m_pImaging { get; set; }
        public IFibicsBeam m_FIB_Beam { get; set; }
        public IFibicsBeam m_SEM_Beam { get; set; }
        public Atlas5.FibicsDetectorController m_pDetector { get; set; }
        public IFibicsAFAS m_pAFAS { get; set; }
        public IFibicsATLAS3DEvents m_p3DEvents { get; set; }
        public IFibicsGIS m_GIS { get; set; }


        public static readonly object apiLock = new object();

        public readonly static string[] sem_detectors_map = new string[5]; // Maximum 5 detectors
        public readonly static string[] fib_detectors_map = new string[5]; // Maximum 5 detectors
        public static string SEM_SESI { get; private set; } = "SESI";
        public static string SEM_ESB { get; private set; } = "ESB";
        public static string FIB_imaging_aperture { get; private set; } = "30kV:50pA ref";
        public static string FIB_burning_aperture { get; private set; } = "30kV:3nA";
        public static string FIB_SESI { get; private set; } = "SESI";
        public static string FIB_ESB { get; private set; } = "ESB";
        public static string typeSEM { get; private set; } = "SEM";
        public static string typeFIB { get; private set; } = "FIB";


        public Dictionary<string, int> fib_apertures_map;

        // Original parameters before starting acquisition
        public StateFIBSEM originalState;
        public bool stateSaved = false;


        public FibicsInterfaceHandler()
        {
            originalState = new StateFIBSEM();
            fib_apertures_map = new Dictionary<string, int>();       
            EmConf.initialize();

        }
        /// <summary>
        /// Initializes the ATLAS engine.
        /// After the Atlas5 has been loaded as API in references, 
        /// it will try to initialize the ATLAS Engine. 
        /// The component classes of the library have to be instantiated and checked one by one.
        /// Some of them are commented because they are not in use (for example GIS will throw not implemented exception in many of their functions)
        /// A class controlling each beam has to be instantiated.
        /// </summary>
        /// <param name="message"> Returns information regarding the succesful connection to ATLAS5 or not</param>
        /// <returns></returns>
        public bool initializeEngine(ref string message)
        {

            lock (apiLock)
            {
                // instantiate the system controller interface to start the
                // engine initializing
                // It is a 2 step initialization, first the engine, then the library components
                // Sometimes the engine initializes but the library components have problems to start.
                // If that the case, calling this function twice should do the trick.
                if (m_pEngine == null)
                {
                    try
                    {
                        m_pEngine = new FibicsSystemController();
                    }
                    catch (System.Runtime.InteropServices.COMException e)
                    {
                        message = "ERROR " + ErrorCode.API_ENGINE_INITIALIZATION_FAILED.ToString() + ": Initialization of Engine failed. ATLAS not connected to microscope or problem \n";
                        message += e.Message;
                        return false;
                    }
                    Stopwatch sw = new Stopwatch();
                    sw.Start();
                    while (!m_pEngine.InitializationComplete) // connected and initialization is complete
                    {
                        if (sw.ElapsedMilliseconds > 15000)
                        {
                            message = "ERROR " + ErrorCode.API_ENGINE_INITIALIZATION_FAILED_TIME_EXCEEDED.ToString() + ": Initialization of Engine failed. Time exceeded!\n";
                            message += m_pEngine.SystemError;
                            m_pEngine = null;
                            return false;
                        }
                    }
                    sw.Restart();
                    while (!m_pEngine.SystemReady) // connected and initialization is complete
                    {
                        if (sw.ElapsedMilliseconds > 15000)
                        {
                            message = "ERROR " + ErrorCode.API_ENGINE_INITIALIZATION_FAILED_SYSTEM_READY_TIME_EXCEEDED.ToString() + ": Initialization of Engine failed. Time exceeded!"+ System.Environment.NewLine;
                            message += m_pEngine.SystemError;
                            m_pEngine = null;
                            return false;
                        }
                    }
                    sw.Stop();

                    // set labels appropriately
                    message += "Initialization of Engine Completed. "+ System.Environment.NewLine;
                }
                // the first time, and only once, instantiate the other interfaces
                try
                {
                    if (m_pSEMVE == null) m_pSEMVE = new Atlas5.FibicsSEMVE();
                    if (m_pStage == null) m_pStage = new Atlas5.FibicsStageController();
                    if (m_pATLAS3D == null) m_pATLAS3D = new FibicsATLAS3D();
                    if (m_pATLAS == null) m_pATLAS = new FibicsATLAS();
                    if (m_SEMApi == null) m_SEMApi = new FibicsSmartSEMInterface();
                    // if (m_GIS == null) m_GIS = new FibicsGIS();
                    // if (m_pImaging == null) m_pImaging = new FibicsImaging();
                    if (m_pAFAS == null) m_pAFAS = new FibicsAFAS();
                    if (m_FIB_Beam == null)
                    {
                        m_FIB_Beam = new FibicsBeam();
                        this.m_FIB_Beam.SetController(Atlas5.BeamControllerEnum.bcFIB);
                    }
                    if (m_SEM_Beam == null)
                    {
                        m_SEM_Beam = new FibicsBeam();
                        this.m_SEM_Beam.SetController(Atlas5.BeamControllerEnum.bcSEM);
                    }
                    m_pDetector = new Atlas5.FibicsDetectorController();
                 

                }
                catch (System.Runtime.InteropServices.COMException e)
                {
                    message = "ERROR " + ErrorCode.API_ENGINE_INITIALIZATION_FAILED_COM_COMPONENTS.ToString() + ": Initialization of ATLAS components failed. Problem with COM components initialization."+ System.Environment.NewLine;
                    message += e.Message;
                    return false;
                }

              
                message += "Initialization success. Connected."+ System.Environment.NewLine;
                return true;
            }




        }
        
        /// <summary>
        /// Saves the state of the current microscope.
        /// </summary>
        /// <param name="report"> String with values of all parameters saved</param>
        /// <returns></returns>
        public void saveState(ref string report)
        {
            this.saveState(ref this.originalState,ref report);
        }

        /// <summary>Save values to a state variable</summary> 
        public void saveState(ref StateFIBSEM state, ref string report)
        {
            report = "Saving FIB-SEM state:\n";
            if (!isInitialized())
            {
                report += "From Save State: ATLAS not initialized. Initialize first.\n";
            }

            
                // Naming and necessary initializations.
                typeSEM = this.m_SEM_Beam.GetBeamType();
                typeFIB = this.m_FIB_Beam.GetBeamType();
                string detec_name = "";
                /********************FIB**********************************/
                this.m_FIB_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcFIB;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcFIB;
                Thread.Sleep(500);
                
                for (int i = 0; i < this.m_pDetector.NumDetectors; i++)
                {

                    detec_name = this.m_pDetector.getDetectorName(i);
                    FibicsInterfaceHandler.fib_detectors_map[i] = detec_name;

                    if (detec_name.Contains("SE"))
                    {
                        FibicsInterfaceHandler.FIB_SESI = detec_name;
                    }
                    else if (detec_name.Contains("ESB"))
                    {
                        FibicsInterfaceHandler.FIB_ESB = detec_name;
                    }

                }

                int numOfApertures = this.m_FIB_Beam.GetApertureCount();

                string ap_name;
                int ap_id, ap_id_2;
                report += "FIB Apertures ID:Name " + System.Environment.NewLine;
                for (int i = 0; i < numOfApertures; i++)
                {
                    ap_name = this.m_FIB_Beam.GetApertureName(i);
                    ap_id = this.m_FIB_Beam.GetApertureID(i);
                    if (fib_apertures_map.TryGetValue(ap_name, out ap_id_2))
                    {
                       report+="Repeated:" + ap_name;
                    }
                    else
                    {
                        fib_apertures_map.Add(ap_name, ap_id);
                    }
                    if (ap_name.Contains("50pA"))
                    {
                        FIB_imaging_aperture = ap_name;
                    }
                    else if (ap_name.Contains("3nA"))
                    {
                        FIB_burning_aperture = ap_name;
                    }

                    report+= "-FIB aperture number "+ i +", ID: "+ ap_id+","+ ap_name+ System.Environment.NewLine;
                   
                }

                this.m_FIB_Beam.SetSelectedApertureID(fib_apertures_map[FIB_imaging_aperture]);
                state.fib_aperture_name = FIB_imaging_aperture;
                report += "-FIB aperture selected for imaging: " + FIB_imaging_aperture + System.Environment.NewLine;
                report += "-FIB aperture selected for burning a mark: " + FIB_burning_aperture + System.Environment.NewLine;

                m_pDetector.setChannelDetector(0, FIB_SESI);
                state.brightness_sesi_FIB = m_pDetector.getChannelBrightness(0);
                state.contrast_sesi_FIB = m_pDetector.getChannelContrast(0);

                report+="FIB SESI B&C: "+state.brightness_sesi_FIB+" B,"+state.contrast_sesi_FIB+" C"+ System.Environment.NewLine;

                /*************************SEM*****************************************************************/

                this.setDetector(typeSEM);
                this.m_SEM_Beam.SelectBeam(); // Select SEM
                this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                Thread.Sleep(500);

                this.m_SEM_Beam.ZeroScanRotation();
                this.m_SEM_Beam.ZeroBeamShift();
                // Search for SESI and ESB
                for (int i=0; i < this.m_pDetector.NumDetectors; i++)
                {

                    detec_name = this.m_pDetector.getDetectorName(i);
                    FibicsInterfaceHandler.sem_detectors_map[i] = detec_name;

                    if (detec_name.Contains("SE"))
                    {
                        FibicsInterfaceHandler.SEM_SESI = detec_name;
                    }
                    else if (detec_name.Contains("ESB"))
                    {
                        FibicsInterfaceHandler.SEM_ESB = detec_name;
                    }

                }
                         
                numOfApertures = this.m_SEM_Beam.GetApertureCount();

                state.sem_aperture_name = this.m_SEM_Beam.GetApertureName(0);
                report+=" Current state SEM using aperture:"+state.sem_aperture_name+System.Environment.NewLine; ;

                double voltage, beamCurrent;
                this.m_SEM_Beam.GetSelectedApertureVI(out voltage, out beamCurrent);
                state.sem_current = beamCurrent;
                state.sem_voltage = voltage;

                double StigX, StigY;
                this.m_SEM_Beam.GetStig(out StigX, out StigY);
                state.sem_stigX = StigX;
                state.sem_stigY = StigY;

                double ShiftX, ShiftY;
                this.m_SEM_Beam.GetBeamShift(out ShiftX, out ShiftY);
                state.sem_beam_shift_x = ShiftX;
                state.sem_beam_shift_y = ShiftY;
                state.sem_WD = this.m_SEM_Beam.GetWDum();
                float brightness, contrast;

                this.getBnC(typeSEM, SEM_SESI, out brightness, out contrast);
                state.brightness_sesi_SEM = brightness;
                state.contrast_sesi_SEM = contrast;

                report+="SEM SESI B&C: " + state.brightness_sesi_SEM + " B," + state.contrast_sesi_SEM + " C"+ System.Environment.NewLine;
                this.getBnC(typeSEM, SEM_ESB, out brightness, out contrast);
                state.brightness_ESB_SEM_trench = brightness;
                state.contrast_ESB_SEM_trench = contrast;
                report+="Getting SEM ESB for detecting trench B&C :"+ state.brightness_ESB_SEM_trench+" B,"+state.contrast_ESB_SEM_trench+" C"+ System.Environment.NewLine;

                state.brightness_ESB_SEM_focus = brightness*1.5f;
                state.contrast_ESB_SEM_focus = contrast * 0.95f;
                state.brightness_ESB_SEM_acq = brightness - 2f;
                state.contrast_ESB_SEM_acq = contrast-1f;
                report += "Original SEM ESB for acquisition (to be changed later) B&C :" + state.brightness_ESB_SEM_acq + " B," + state.contrast_ESB_SEM_acq + " C"+ System.Environment.NewLine;
                report += "Original SEM ESB for focus during acquisition (to be changed later) B&C :"+ System.Environment.NewLine + state.brightness_ESB_SEM_focus + " B," + state.contrast_ESB_SEM_focus + " C"+ System.Environment.NewLine;

                double fovx, fovy;
                this.m_SEM_Beam.GetFOV(out fovx, out fovy);
                state.sem_fov_x = fovx;
                state.sem_fov_y = fovy;
                state.sem_tilt_correction = this.m_SEM_Beam.GetTiltCorrection();
                report += "FOV :" + state.sem_fov_x + " x," + state.sem_fov_y + " y "+System.Environment.NewLine; 
                report += "Tilt correction:" + state.sem_tilt_correction+ System.Environment.NewLine; 
                // Change back to SESI
                this.setBnC(typeSEM, SEM_SESI, state.brightness_sesi_SEM, state.contrast_sesi_SEM);

                // STAGE POSITION
                PointEM iposition = new PointEM();
                string message = "";
                this.GetStagePosition(ref iposition, ref message);
                state.x = iposition.x;
                state.y = iposition.y;
                state.z = iposition.z;
                state.r = iposition.r;
                state.t = iposition.t;
                state.m = iposition.m;

                this.stateSaved = true;
                state.isReady = true;
                report += "Status saved in position:" + iposition.ToString();
                report += "\n Status saved "+System.Environment.NewLine;
        }

        /// <summary>Loads a state previously saved</summary>
        public bool loadState(StateFIBSEM state, ref string report)
        {
            if (this.stateSaved == false) 
            {
                report += " Initializing current values."+System.Environment.NewLine;
                this.saveState(ref report);
                report += "--- Now loading state.";
            }

            /********************FIB**********************************/
            this.m_FIB_Beam.SelectBeam();
            this.m_pATLAS.BeamController = BeamControllerEnum.bcFIB;
            this.m_pSEMVE.ActiveController = BeamControllerEnum.bcFIB;
            Thread.Sleep(500);
            this.m_FIB_Beam.SetSelectedApertureID(fib_apertures_map[FIB_imaging_aperture]);

            report += "\n Changing B&C FIB in SESI mode: B -" + state.brightness_sesi_FIB + " - C -" + state.contrast_sesi_FIB;
            this.setBnC(typeFIB, FIB_SESI, state.brightness_sesi_FIB, state.contrast_sesi_FIB);


            /*****************SEM********************************/
            this.m_SEM_Beam.SelectBeam();
            this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
            this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
            Thread.Sleep(500);

            report = ("Current state SEM using aperture:"+state.sem_aperture_name);
            // To be implemented to change to the Voltage and current. However not necessary.

            this.m_SEM_Beam.SetStig(state.sem_stigX, state.sem_stigY);
            this.m_SEM_Beam.SetBeamShift(state.sem_beam_shift_y, state.sem_beam_shift_y);
            this.m_SEM_Beam.SetWDum(state.sem_WD);
            report += " Stigmators X,Y" + state.sem_stigX + "," + state.sem_stigY+ System.Environment.NewLine; ;
            report += " Beam shift at X,Y" + state.sem_beam_shift_x + "," + state.sem_beam_shift_y+ System.Environment.NewLine; ;
            report += " WD at" + state.sem_WD + " um"+ System.Environment.NewLine; ;
            this.m_SEM_Beam.SetFOV(state.sem_fov_x, state.sem_fov_y);
            this.m_SEM_Beam.SetTiltCorrection(state.sem_tilt_correction);
            this.setBnC(typeSEM, SEM_SESI, state.brightness_sesi_SEM, state.contrast_sesi_SEM);

            report += " Changing B&C SEM in SESI mode: B -" + state.brightness_sesi_SEM.ToString() + " - C -" + state.contrast_sesi_SEM+ System.Environment.NewLine; ;

            /*************************************************************/
            this.loadStatePosition(state, ref report, false);
            report += "State loaded.";
            return true;
        }

        /// <summary>
        /// Returns aperture id given an id, -1 if the name is not found.
        /// Used to find FIB apertures.
        /// </summary>
        /// <param name="ap_name"></param>
        /// <returns></returns>
        public int getAperture(string ap_name)
        {
            
            int ap_id;
            if (fib_apertures_map.TryGetValue(ap_name, out ap_id))
            {
                return  ap_id;
            }
            
            return -1;
       }

   /// <summary>
   ///  Given a position saved in a state, it moves to it.
   /// </summary>
   /// <param name="state"></param>
   /// <param name="report"></param>
   /// <param name="stageXY"></param>
   /// <returns></returns>
        public bool loadStatePosition(StateFIBSEM state, ref string report, bool stageXY = true)
        {
            PointEM newPosition = new PointEM(state.x,state.y,state.z,state.r,state.t,state.m);
            PointEM currentPosition = new PointEM();
            if (stageXY == false) // Don't move X and Y
            {
                
                string message = "";
                this.GetStagePosition(ref currentPosition,ref message);
                newPosition.x = currentPosition.x;
                newPosition.y = currentPosition.y;
            }
            
            this.MoveTo(newPosition);
            report += "Restoring position to" + newPosition.ToString();
            return true;
        }

        // If any of the COM objects failed during initialization, then is null, then return false.
        public bool isInitialized()
        {

            return ((m_pSEMVE != null) && (m_pStage != null) && (m_pATLAS3D != null) && (m_pATLAS != null) && (m_SEMApi != null) && (m_pAFAS != null) && (m_FIB_Beam != null));
        }

        public void closeEngine()
        {
            // to shut down the engine, just release all the interfaces
            // you should wait 5-10 seconds before trying to connect again
           
            lock (apiLock)
            {
                m_pSEMVE.HideUI();
                m_pSEMVE = null;
                m_pStage = null;
                m_pEngine = null;
                m_pATLAS3D = null;
                m_pATLAS = null;
                m_SEMApi = null;
                m_FIB_Beam = null;
                m_SEM_Beam = null;
                m_pDetector = null;
                //m_pImaging = null;
                m_pAFAS = null;
                GC.Collect();
                System.Threading.Thread.Sleep(10000);
            }
        }

        public bool setFIBAperture(string ap_name)
        {
            try
            {
                this.m_FIB_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcFIB;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcFIB;
                Thread.Sleep(500);
                int ap_id;
                if (fib_apertures_map.TryGetValue(ap_name, out ap_id))
                {
                    return this.m_FIB_Beam.SetSelectedApertureID(fib_apertures_map[ap_name]);
                }
                else
                {
                    return false;
                }
            }
            catch (System.NullReferenceException)
            {
                return false;
            }
        }

        public bool setDetector(string beam, string detector ="")
        {
            try
            {
                Console.WriteLine("Setting beam " + beam);
                if (beam.CompareTo(typeSEM) == 0)
                {
                    Console.WriteLine("Beam set to SEM");
                    if (this.m_pATLAS.BeamController != Atlas5.BeamControllerEnum.bcSEM)
                    {
                        this.m_SEM_Beam.SelectBeam();
                        this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                        this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                        Thread.Sleep(500);

                    }
                    if (detector.Length > 0)
                    {
                        Console.WriteLine("Detector "+detector+" set to channel 0.");
                        m_pDetector.setChannelDetector(0, detector);
                        Thread.Sleep(500);
                        m_pDetector.setChannelDetector(0, detector);
                    }
                    return true;
                }
                if (beam.CompareTo(typeFIB) == 0)
                {
                    Console.WriteLine("Beam set to FIB");
                    if (this.m_pATLAS.BeamController != Atlas5.BeamControllerEnum.bcFIB)
                    {
                        this.m_FIB_Beam.SelectBeam();
                        this.m_pATLAS.BeamController = BeamControllerEnum.bcFIB;
                        this.m_pSEMVE.ActiveController = BeamControllerEnum.bcFIB;
                        Thread.Sleep(500);
                    }
                    if (detector.Length > 0)
                    {
                        Console.WriteLine("Detector " + detector + " set to channel 0.");
                        m_pDetector.setChannelDetector(0, detector);
                        Thread.Sleep(500);
                        m_pDetector.setChannelDetector(0, detector);
                    }
                    return true;
                }
            }
            catch (System.NullReferenceException) 
            {
                return false;
            }
            return false;
        }

        public bool setBnC(string beam, string detector, float brightness, float contrast)
        {
            if(this.setDetector(beam, detector))
            {
                Console.WriteLine("Channel 0 set B&C to:{0},{1}",brightness, contrast);
                m_pDetector.setChannelBrightness(0, brightness);
                m_pDetector.setChannelContrast(0, contrast);
                return true;
            }
            return false;
        }

        public bool getBnC(string beam, string detector, out float brightness, out float contrast)
        {
            brightness = 0;
            contrast = 0;
            if (this.setDetector(beam, detector))
            {
                brightness = m_pDetector.getChannelBrightness(0); 
                contrast = m_pDetector.getChannelContrast(0);
                return true;
            }
            return false;
        }
        /// <summary>
        ///  Get, set stigmators
        /// </summary>
        /// <param name="stx"></param>
        /// <param name="sty"></param>
        public void getStigs(out double stx, out double sty)
        {
            try
            {
                this.m_SEM_Beam.GetStig(out stx, out sty);
            }
            catch (System.NullReferenceException)
            {
                stx = 0.0;
                sty = 0.0;
                return;
            }
            return;
        }
        public void setStigs(double stx, double sty)
        {
            try
            {
                this.m_SEM_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                Thread.Sleep(500);
                this.m_SEM_Beam.SetStig(stx, sty);
            }
            catch (System.NullReferenceException)
            {
                return;
            }
            return;
        }

        /// <summary>
        /// Get, set BeamShift
        /// </summary>
        /// <param name="bsx"></param>
        /// <param name="bsy"></param>
        public void getBeamShift(out double bsx, out double bsy)
        {
            try
            {
                this.m_SEM_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                Thread.Sleep(500);
                this.m_SEM_Beam.GetBeamShift(out bsx, out bsy);
                return;
            }
            catch (System.NullReferenceException)
            {
                bsx = 0.0;
                bsy = 0.0;
            }
            return;
        }
        public void setBeamShift(double bsx,double bsy)
        {
            try
            {
                this.m_SEM_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                Thread.Sleep(500);
                this.m_SEM_Beam.SetBeamShift(bsx, bsy);
            }
            catch (System.NullReferenceException)
            {
                bsx = 0.0;
                bsy = 0.0;
            }
        }

        /// <summary>
        /// Get, set WD
        /// </summary>
        /// <param name="WD"></param>
        public double getWD()
        {
            try
            {
                return this.m_SEM_Beam.GetWDum();
            }
            catch (System.NullReferenceException)
            {
                return 0.0;
            }
        }
        public void setWD(float WD)
        {
            this.m_SEM_Beam.SetWDum(WD);  
        }

        public void setTiltCorrection(double tilt_angle)
        {
            try
            {
                this.m_SEM_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                Thread.Sleep(500);
                this.m_SEM_Beam.SetTiltCorrection(tilt_angle);
            }
            catch (System.NullReferenceException)
            {
                return;
            }
        }

        public void setFOV(double fovx, double fovy)
        {
            try
            {
                this.m_SEM_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                Thread.Sleep(500);
                this.m_SEM_Beam.SetFOV(fovx, fovy);
            }
            catch (System.NullReferenceException)
            {
                return;
            }
        }

        public void getFOV(out double fovx, out double fovy)
        {
            try
            {
                this.m_SEM_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                Thread.Sleep(500);
                this.m_SEM_Beam.GetFOV(out fovx, out fovy);
            }
            catch (System.NullReferenceException)
            {
                fovx = 0.0;
                fovy = 0.0;
                return;
            }

        }


        // Saves Beam Shift, WD, and stigmators
        public void saveImageState(ref StateImage state)
        {
            try
            {
                this.m_SEM_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                Thread.Sleep(500);
                double StigX, StigY;
                this.m_SEM_Beam.GetStig(out StigX, out StigY);
                state.stigX = StigX;
                state.stigY = StigY;

                double ShiftX, ShiftY;
                this.m_SEM_Beam.GetBeamShift(out ShiftX, out ShiftY);
                state.beam_shift_x = ShiftX;
                state.beam_shift_y = ShiftY;

                state.WD = this.m_SEM_Beam.GetWDum();
            }
            catch (System.NullReferenceException)
            {
                return;
            }
        }

        public void restoreImageState(StateImage state,bool bs=true)
        {

            this.m_SEM_Beam.SelectBeam();
            this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
            this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
            Thread.Sleep(500);
            try
            {
                this.m_SEM_Beam.SetStig(state.stigX, state.stigY);
                this.m_SEM_Beam.SetWDum(state.WD);
                if (bs)
                {
                    this.m_SEM_Beam.SetBeamShift(state.beam_shift_x, state.beam_shift_y);
                }
            }
            catch (System.NullReferenceException)
            {
                return;
            }
        }



        public Atlas5.FibicsAFASEnum doAutoFocus( float ipixelSize, float irange, float idwelltime, int ilineAverage, double iFOV=100, int complete = 1)
        {

            lock (apiLock)
            {
                if (this.isInitialized())
                {
                    this.setFOV(iFOV, iFOV);
                    this.m_pAFAS.SetController(BeamControllerEnum.bcSEM);

                    int pixelcount = (int)(iFOV / ipixelSize);
                    this.m_pAFAS.SetParameters(pixelcount, idwelltime, ilineAverage);
                    this.m_pAFAS.SetAFRange(irange);

                    if (complete == 1)
                    {
                        bool af_success = this.m_pAFAS.StartAFAS(FibicsAFASModeEnum.AutoFocusOnly);
                    }
                    else
                    {
                        bool af_success = this.m_pAFAS.StartAFAS(FibicsAFASModeEnum.AutoFocusFineOnly);
                    }
                    Stopwatch stopwatch = Stopwatch.StartNew();
                    long millisecondsToWait = 300000; // 5 minutes...which is a lot
                    Atlas5.FibicsAFASEnum status = this.m_pAFAS.GetAFASStatus();
                    while (stopwatch.ElapsedMilliseconds < millisecondsToWait && Atlas5.FibicsAFASEnum.afsBusy == status)
                    {
                        Thread.Sleep(1000);
                        status = this.m_pAFAS.GetAFASStatus();
                        switch (status)
                        {
                            case (Atlas5.FibicsAFASEnum.afsTimedOut):
                            case (Atlas5.FibicsAFASEnum.afsUnknownError):
                            case (Atlas5.FibicsAFASEnum.afsFailed):
                            case (Atlas5.FibicsAFASEnum.afsIdle):
                            case (Atlas5.FibicsAFASEnum.afsError):
                            case (Atlas5.FibicsAFASEnum.afsNotInitialized):
                                return status;
                        }
                    }

                    return status;
                }
                else
                {
                    return Atlas5.FibicsAFASEnum.afsNotInitialized;
                }
            }
        }


        public Atlas5.FibicsAFASEnum doAutoStig(float ipixelSize, float irange, float idwelltime, int ilineAverage, double iFOV = 100,int complete =1)
        {
            lock (apiLock)
            {
                if (this.isInitialized())
                {
                    this.setFOV(iFOV, iFOV);
                    this.m_pAFAS.SetController(BeamControllerEnum.bcSEM);
                    int pixelcount = (int)(iFOV / ipixelSize);
                    this.m_pAFAS.SetParameters(pixelcount, idwelltime, ilineAverage);
                    this.m_pAFAS.SetAFRange(irange);
                    if (complete == 1)
                    {
                        bool af_success = this.m_pAFAS.StartAFAS(FibicsAFASModeEnum.AutoStigXYOnly);
                    }
                    else
                    {
                        bool af_success = this.m_pAFAS.StartAFAS(FibicsAFASModeEnum.AutoFocusStigXYFine);
                    }
                    Stopwatch stopwatch = Stopwatch.StartNew();
                    long millisecondsToWait = 300000; // 5 minutes...which is a lot
                    Atlas5.FibicsAFASEnum status = this.m_pAFAS.GetAFASStatus();
                    while (stopwatch.ElapsedMilliseconds < millisecondsToWait && Atlas5.FibicsAFASEnum.afsBusy == status)
                    {
                        Thread.Sleep(1000);
                        status = this.m_pAFAS.GetAFASStatus();
                        switch (status)
                        {
                            case (Atlas5.FibicsAFASEnum.afsTimedOut):
                            case (Atlas5.FibicsAFASEnum.afsUnknownError):
                            case (Atlas5.FibicsAFASEnum.afsFailed):
                            case (Atlas5.FibicsAFASEnum.afsIdle):
                            case (Atlas5.FibicsAFASEnum.afsError):
                            case (Atlas5.FibicsAFASEnum.afsNotInitialized):
                                return status;
                        }
                    }
                    return status;
                }
                else {
                    return FibicsAFASEnum.afsNotInitialized;
                }
                
            }
        }

        /*** STAGE ***/

      /// <summary>
        /// safeMove
        /// </summary>
        /// <param name="nextPosition"></param>
        /// <param name="scale_unit"></param>
        /// <param name="message"></param>
        /// <returns></returns>
        public bool safeMove(PointEM nextPosition, string scale_unit, ref string message)
        {
            switch (scale_unit)
            {
                case ("meter"):
                    nextPosition.x = 1e6 * nextPosition.x;
                    nextPosition.y = 1e6 * nextPosition.y;
                    nextPosition.z = 1e6 * nextPosition.z;
                    break;
                case ("milimeter"):
                    nextPosition.x = 1e3 * nextPosition.x;
                    nextPosition.y = 1e3 * nextPosition.y;
                    nextPosition.z = 1e3 * nextPosition.z;
                    break;
                case ("micrometer"):
                    break;
                default:
                    message = "ERROR: scale unit not accepted";
                    return false;
            }
            if (this.m_pStage == null) // In case the stage control is not initialized
            {
                try
                {
                    if (m_pStage == null) m_pStage = new Atlas5.FibicsStageController();
                }
                catch (System.Runtime.InteropServices.COMException e)
                {
                    message = "ERROR:Initialization of Engine failed. Problem with COM components.\n";
                    message += e.Message;
                    return false;
                }

            }


            if ((Math.Floor(nextPosition.x / 1000.0) == 0) || (Math.Floor(nextPosition.y / 1000.0) == 0) || nextPosition.x > 500000 || nextPosition.y > 500000)
            {
                message = "ERROR: coordinates NOT in microns.";
                return false;
            }

            PointEM currentPosition = new PointEM();

            double vXValue;
            double vYValue;
            double vZValue;
            double vTValue;
            double vRValue;
            double vMValue;
            this.m_pStage.getPosition(out vXValue, out vYValue, out vZValue, out vRValue, out vTValue, out vMValue);

            currentPosition.x = vXValue;
            currentPosition.y = vYValue;
            currentPosition.z = vZValue;
            currentPosition.t = vTValue;
            currentPosition.r = vRValue;
            currentPosition.m = vMValue;
            // Since only x and y values are taken, the other ones must be filled
            if (nextPosition.m == 0.0 || nextPosition.t == 0.0)
            {
                nextPosition.r = vRValue;  // radians
                nextPosition.t = vTValue;  // radians
                nextPosition.m = vMValue;  // millimeters
            }
            if (nextPosition.z < 1000) nextPosition.z = vZValue;
            if (nextPosition.x > 0.0) nextPosition.x = -nextPosition.x;
            if (nextPosition.y > 0.0) nextPosition.y = -nextPosition.y;
            // Coordinates X and Y in ATLAS are considered negative

            // Check that we respect the safety margin in Z
            if (nextPosition.z > StateFIBSEM.limit_Z)
            {
                nextPosition.z = StateFIBSEM.limit_Z;

            }

            // move to position
            // Check if there is difference between the current position in Y and the new position
            if (Math.Abs(currentPosition.y - nextPosition.y) > 1500) // bigger than 1500 microns
            {
                // two steps movement
                // First lower Z
                currentPosition.z -= 2000;
                if (!MoveTo(currentPosition))
                {
                    message = "ERROR: Problems with stage movement!\n";
                    return false;
                }
                PointEM intermediatePosition = new PointEM(nextPosition);
                intermediatePosition.z = currentPosition.z;
                if (!MoveTo(intermediatePosition))
                {
                    message = "ERROR: Problems with stage movement!\n";
                    return false;
                }
                if (!MoveTo(nextPosition))
                {
                    message = "ERROR: Problems with stage movement!\n";
                    return false;
                }
            }
            else
            {
                if (!MoveTo(nextPosition))
                {
                    message = "ERROR: Problems with stage movement!\n";
                    return false;
                }

            }
            return true;

        }
        public bool MoveTo(PointEM position)
        {
            int WaitForCompletion = m_pStage.gotoPosition(position.x, position.y, position.z, position.r, position.t, position.m, true, false);// To be fixed not use true, true
            Stopwatch sw = new Stopwatch();
            sw.Start();
            while (!m_pStage.isAtPosition(position.x, position.y, position.z, position.r, position.t, position.m))
            { 
                System.Threading.Thread.Sleep(100);
                if (sw.ElapsedMilliseconds > 60000) // wait 60 seconds
                {
                    return false;
                }
            }
            sw.Stop();
            

            /*     Stopwatch sw = new Stopwatch();
            sw.Start();
            while (m_pStage.isBusy())
            {
                System.Threading.Thread.Sleep(100);
                if (sw.ElapsedMilliseconds > 5000) // wait 5 seconds
                {
                    return false;
                }
            }
            sw.Stop(); 
            System.Threading.Thread.Sleep(100);
            if (!m_pStage.isAtPosition(position.x, position.y, position.z, position.r, position.t, position.m))
            {
                m_pStage.halt();
                return false;
            } */
            return true;
        }
        public void GetStagePosition(ref PointEM currentPosition, ref string message)
        {
            if (this.m_pStage == null) // In case the stage control is not initialized
            {
                try
                {
                    if (m_pStage == null) m_pStage = new Atlas5.FibicsStageController();
                }
                catch (System.Runtime.InteropServices.COMException e)
                {
                    message = "ERROR:Initialization of Engine failed. Problem with COM components.\n";
                    message += e.Message;
                    return;
                }

            }

            double vXValue;
            double vYValue;
            double vZValue;
            double vTValue;
            double vRValue;
            double vMValue;
            this.m_pStage.getPosition(out vXValue, out vYValue, out vZValue, out vRValue, out vTValue, out vMValue);

            currentPosition.x = vXValue;
            currentPosition.y = vYValue;
            currentPosition.z = vZValue;
            currentPosition.t = vTValue;
            currentPosition.r = vRValue;
            currentPosition.m = vMValue;

            message = "Success";

        }
        
        /************* GRABBERS**********************************************/
        public virtual void GrabFrameFIB(string filepath, string imagename, int delay, int res, double iPixelSize,
            float dwelltime, int lineavg, double iScanRotation, ref string e)
        {
            int width, height;
            // TODO: this should be adequated to the aperture
            this.setBnC(typeFIB, FIB_SESI, originalState.brightness_sesi_FIB, originalState.contrast_sesi_FIB);
            width = 1024;
            height = 768;
            switch (res)
            {
                case (0):
                    width = 512;
                    height = 512;
                    break;
                case (1):
                    width = 1024;
                    height = 1024;
                    break;
                case (2):
                    width = 2048;
                    height = 2048;
                    break;
                case (3):
                    width = 4096;
                    height = 4096;
                    break;
                case (4):
                    width = 8192;
                    height = 8192;
                    break;
                case (5):
                    width = 10240;
                    height = 10240;
                    break;
                case (6):
                    width = (int) Math.Round(1024 * (1 / iPixelSize));
                    height = (int) Math.Round(1024 * (1 / iPixelSize));
                    break; // for grid squares
                default: break;
            }

            double pxs = (iPixelSize * width);
            try
            {
                this.m_FIB_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcFIB;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcFIB;
                Thread.Sleep(500);
                this.m_FIB_Beam.SetFOV(pxs, pxs);
                m_pATLAS.BeamController = Atlas5.BeamControllerEnum.bcFIB;
                m_pATLAS.SetImagingParameters(iPixelSize, dwelltime, lineavg);

                ArrayList plist = new ArrayList();
                float s_value = ((float) iPixelSize * width) / 2;
                Point p1 = new Point();
                p1.X = s_value;
                p1.Y = s_value;
                Point p2 = new Point();
                p2.X = -s_value;
                p2.Y = s_value;
                Point p3 = new Point();
                p3.X = -s_value;
                p3.Y = -s_value;
                Point p4 = new Point();
                p4.X = s_value;
                p4.Y = -s_value;
                plist.Add(p1);
                plist.Add(p2);
                plist.Add(p3);
                plist.Add(p4);
                Array pVertices = createSafeArray(plist);
                m_pATLAS.DefineMosaic(pVertices, iScanRotation);
                m_pATLAS.AcquireMosaic2(imagename, filepath, true, width, height);


                // We should be able to set the PixelSize
                Stopwatch stopwatch = Stopwatch.StartNew();
                long millisecondsToWait = 300000; // 5 minutes...which is a lot
                while (this.m_pATLAS.Busy && stopwatch.ElapsedMilliseconds < millisecondsToWait) ;

                if (delay > 0)
                {
                    delay = (int) ((width * height) * dwelltime * lineavg * delay);
                    int delay_milisec = delay / 1000; // microseconds to milliseconds
                    m_pSEMVE.StartContinuousImaging(width, height, dwelltime, lineavg);
                    Thread.Sleep(delay_milisec);
                    m_pSEMVE.Cancel();
                }

                Thread.Sleep(5000);
                return;
            }
            catch (System.NullReferenceException)
            {
                return;
            }
        }
        public virtual void GrabFrameSEM(string filepath, string imagename, int res, double iPixelSize, float dwelltime, int lineavg, double iScanRotation, ref string err)
        {

            try
            {
                this.m_SEM_Beam.SelectBeam();
                this.m_pATLAS.BeamController = BeamControllerEnum.bcSEM;
                this.m_pSEMVE.ActiveController = BeamControllerEnum.bcSEM;
                Thread.Sleep(500);

                int width, height;
                width = 1024;
                height = 768;
                switch (res)
                {
                    case (0):
                        width = 512;
                        height = 512;
                        break;
                    case (1):
                        width = 1024;
                        height = 1024;
                        break;
                    case (2):
                        width = 2048;
                        height = 2048;
                        break;
                    case (3):
                        width = 4096;
                        height = 4096;
                        break;
                    case (4):
                        width = 8192;
                        height = 8192;
                        break;
                    case (5):
                        width = 10240;
                        height = 10240;
                        break;
                    case (6):
                        width = (int) Math.Round(1280 * (1 / iPixelSize));
                        height = (int) Math.Round(1280 * (1 / iPixelSize));
                        break; // for grid squares
                    default: break;
                }

                double pxs = (iPixelSize * width);
                this.m_SEM_Beam.SetFOV(pxs, pxs);
                m_pATLAS.BeamController = Atlas5.BeamControllerEnum.bcSEM;
                m_pATLAS.SetImagingParameters(iPixelSize, dwelltime, lineavg);
                ArrayList plist = new ArrayList();
                float s_value = ((float) iPixelSize * width) / 2;
                Point p1 = new Point();
                p1.X = s_value;
                p1.Y = s_value;
                Point p2 = new Point();
                p2.X = -s_value;
                p2.Y = s_value;
                Point p3 = new Point();
                p3.X = -s_value;
                p3.Y = -s_value;
                Point p4 = new Point();
                p4.X = s_value;
                p4.Y = -s_value;
                plist.Add(p1);
                plist.Add(p2);
                plist.Add(p3);
                plist.Add(p4);
                Array pVertices = createSafeArray(plist);
                m_pATLAS.DefineMosaic(pVertices, iScanRotation);
                m_pATLAS.AcquireMosaic2(imagename, filepath, true, width, height); //+200


                // We should be able to set the PixelSize
                Stopwatch stopwatch = Stopwatch.StartNew();
                long millisecondsToWait = 300000; // 5 minutes...which is a lot
                try
                {
                    while (this.m_pATLAS.Busy && stopwatch.ElapsedMilliseconds < millisecondsToWait) ;
                }
                catch (System.NullReferenceException)
                {
                    return;
                }

                Thread.Sleep(10000);
            }
            catch (System.NullReferenceException)
            {
                // If user cancels run
                return;
            }
            catch (System.Runtime.InteropServices.COMException e)
            {
                err =
                    "When Grabbing a Frame in SEM. Something happened with the COM component. Please, check the connection with the microscope. \n" +
                    e.ToString();
                return;
            }



            return;

        }

        public Array createSafeArray(ArrayList pMask)
        {
            int[] alengths = new int[2];
            int[] alowerBounds = new int[2];
            double xc, yc;
            int idx;

            alowerBounds[0] = 0;
            alengths[0] = pMask.Count;

            alowerBounds[1] = 0;
            alengths[1] = pMask.Count;

            Array result = Array.CreateInstance(typeof(double), alengths, alowerBounds);

            int[] aNdx = new int[2];
            idx = 0;
            foreach (Point p in pMask)
            {
                aNdx[0] = 0;
                aNdx[1] = idx;
                xc = p.X;
                result.SetValue(xc, aNdx);
                aNdx[0] = 1;
                aNdx[1] = idx;
                idx = idx + 1;
                yc = p.Y;
                result.SetValue(yc, aNdx);
            }
            return result;
        }

        /***SMART SEM direct interactions**/

        public string ErrorToString(long lError)
        {
            string strError;

            switch ((ZeissErrorCode)lError)
            {
                case 0:
                    strError = ("_ ");
                    break;
                case ZeissErrorCode.API_E_GET_TRANSLATE_FAIL:
                    strError = ("Failed to translate parameter into an ID");
                    break;
                case ZeissErrorCode.API_E_GET_AP_FAIL:
                    strError = ("Failed to get analogue value");
                    break;
                case ZeissErrorCode.API_E_GET_DP_FAIL:
                    strError = ("Failed to get digital value");
                    break;
                case ZeissErrorCode.API_E_GET_BAD_PARAMETER:
                    strError = ("Parameter supplied is neither analogue nor digital");
                    break;
                case ZeissErrorCode.API_E_SET_TRANSLATE_FAIL:
                    strError = ("Failed to translate parameter into an ID");
                    break;
                case ZeissErrorCode.API_E_SET_STATE_FAIL:
                    strError = ("Failed to set a digital state");
                    break;
                case ZeissErrorCode.API_E_SET_FLOAT_FAIL:
                    strError = ("Failed to set a float value");
                    break;
                case ZeissErrorCode.API_E_SET_FLOAT_LIMIT_LOW:
                    strError = ("Value supplied is too low");
                    break;
                case ZeissErrorCode.API_E_SET_FLOAT_LIMIT_HIGH:
                    strError = ("Value supplied is too high");
                    break;
                case ZeissErrorCode.API_E_SET_BAD_VALUE:
                    strError = ("Value supplied is of wrong type");
                    break;
                case ZeissErrorCode.API_E_SET_BAD_PARAMETER:
                    strError = ("Parameter supplied is not analogue nor digital");
                    break;
                case ZeissErrorCode.API_E_EXEC_TRANSLATE_FAIL:
                    strError = ("Failed to translate command into an ID");
                    break;
                case ZeissErrorCode.API_E_EXEC_CMD_FAIL:
                    strError = ("Failed to execute command");
                    break;
                case ZeissErrorCode.API_E_EXEC_MCF_FAIL:
                    strError = ("Failed to execute file macro");
                    break;
                case ZeissErrorCode.API_E_EXEC_MCL_FAIL:
                    strError = ("Failed to execute library macro");
                    break;
                case ZeissErrorCode.API_E_EXEC_BAD_COMMAND:
                    strError = ("Command supplied is not implemented");
                    break;
                case ZeissErrorCode.API_E_GRAB_FAIL:
                    strError = ("Grab command failed");
                    break;
                case ZeissErrorCode.API_E_GET_STAGE_FAIL:
                    strError = ("Get Stage position failed");
                    break;
                case ZeissErrorCode.API_E_MOVE_STAGE_FAIL:
                    strError = ("Move Stage position failed");
                    break;
                case ZeissErrorCode.API_E_NOT_INITIALISED:
                    strError = ("API not initialised");
                    break;
                case ZeissErrorCode.API_E_NOTIFY_TRANSLATE_FAIL: // 1020L
                    strError = ("Failed to translate parameter to an ID");
                    break;
                case ZeissErrorCode.API_E_NOTIFY_SET_FAIL:
                    strError = ("Set notification failed");
                    break;
                case ZeissErrorCode.API_E_GET_LIMITS_FAIL:
                    strError = ("Get limits failed");
                    break;
                case ZeissErrorCode.API_E_GET_MULTI_FAIL:
                    strError = ("Get multiple parameters failed");
                    break;
                case ZeissErrorCode.API_E_SET_MULTI_FAIL:
                    strError = ("Set multiple parameters failed");
                    break;
                case ZeissErrorCode.API_E_NOT_LICENSED:
                    strError = ("Missing API license");
                    break;
                case ZeissErrorCode.API_E_NOT_IMPLEMENTED:
                    strError = ("Reserved or not implemented");
                    break;
                case ZeissErrorCode.API_E_GET_USER_NAME_FAIL:
                    strError = ("Failed to get user name");
                    break;
                case ZeissErrorCode.API_E_GET_USER_IDLE_FAIL:
                    strError = ("Failed to get user idle state");
                    break;
                case ZeissErrorCode.API_E_GET_LAST_REMOTING_CONNECT_ERROR_FAIL:
                    strError = ("Failed to get the last remoting connection error string");
                    break;
                case ZeissErrorCode.API_E_EMSERVER_LOGON_FAILED:
                    strError = ("Failed to remotely logon to the EM Server. Username and password may be incorrect or EM Server is not running or User is already logged on");
                    break;
                case ZeissErrorCode.API_E_EMSERVER_START_FAILED:
                    strError = ("Failed to start the EM Server. This may be because the Server is already running or has an internal error.");
                    break;
                case ZeissErrorCode.API_E_REMOTING_NOT_CONFIGURED:
                    strError = ("Remoting incorrectly configured, use RConfigure to correct");
                    break;
                case ZeissErrorCode.API_E_REMOTING_FAILED_TO_CONNECT:
                    strError = ("Remoting did not connect to the server");
                    break;
                case ZeissErrorCode.API_E_REMOTING_COULD_NOT_CREATE_INTERFACE:
                    strError = ("Remoting could not start (unknown reason)");
                    break;
                case ZeissErrorCode.API_E_REMOTING_EMSERVER_NOT_RUNNING:
                    strError = ("EMServer is not running on the remote machine");
                    break;
                case ZeissErrorCode.API_E_REMOTING_NO_USER_LOGGED_IN:
                    strError = ("No user is logged into EM Server on the remote machine");
                    break;
                default:
                    strError = ("Unknown error code ") + lError;
                    break;
            }
            return strError;
        }

        public bool doSmartSEMCommand(string option, string command, ref float ivalue, ref string error)
        {
            float mv = 0.0f;
            object Value = mv;
            error = "";
            int lerror = 0;
            switch (option)
            {
                case ("COMMAND"):
                    lerror = this.m_SEMApi.Execute(command);
                    if (lerror > 0)
                    {
                        error = this.ErrorToString((long)lerror);
                        return false;
                    }
                    break;
                case ("GET"):
                    lerror = this.m_SEMApi.Get(command, ref Value);
                    if (lerror > 0)
                    {
                        error = this.ErrorToString((long)lerror);
                        return false;
                    }
                    ivalue = Convert.ToSingle(Value);
                    break;
                case ("SET"):
                    Value = ivalue;
                    lerror = this.m_SEMApi.Set(command, Value);
                    if (lerror > 0)
                    {
                        error = this.ErrorToString((long)lerror);
                        return false;
                    }
                    ivalue = Convert.ToSingle(Value);
                    break;
                default:
                    return false;
            }

            return true;
        }

        public void changeMode(string Mode)
        {
            string error = "";
            float mv;
            switch (Mode)
            {
                case "HR":
                    mv = 0.0f;
                    doSmartSEMCommand("SET", "DP_CROSSOVER_MODE", ref mv, ref error);
                    doSmartSEMCommand("SET", "DP_GEMINI_FISHEYE", ref mv, ref error);
                    doSmartSEMCommand("SET", "DP_ULTRA_ANALYTIC_DEPTH_MODE", ref mv, ref error);
                    break;
                case "DoF":
                    mv = 0.0f;
                    doSmartSEMCommand("SET", "DP_CROSSOVER_MODE", ref mv, ref error);
                    doSmartSEMCommand("SET", "DP_GEMINI_FISHEYE", ref mv, ref error);
                    mv = 1.0f;
                    doSmartSEMCommand("SET", "DP_ULTRA_ANALYTIC_DEPTH_MODE", ref mv, ref error);
                    break;
                case "FishEye":
                    break;
                case "Analytical":
                    mv = 1.0f;
                    doSmartSEMCommand("SET", "DP_ULTRA_ANALYTIC_DEPTH_MODE", ref mv, ref error);
                    mv = 0.0f;
                    doSmartSEMCommand("SET", "DP_CROSSOVER_MODE", ref mv, ref error);
                    doSmartSEMCommand("SET", "DP_GEMINI_FISHEYE", ref mv, ref error);
                    break;
                default:
                    break;


            }
        }

        public string getMessageLog()
        {
            if (m_pATLAS3D == null)
            {
                return "";
            }
            return m_pATLAS3D.MillImageToolMessages();
        }
    }



}
