using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;
using System.Security.Cryptography;
using System.IO;
using Newtonsoft.Json;
using System.Text.RegularExpressions;
using System.Threading;

namespace msite
{ 
    /**
     * CLASS MessageParser : Decodes string into specific functionality
     * 
     * **/
    public class MessageParser
    {
        Dictionary<string, Delegate> dicf = new Dictionary<string, Delegate>();
        private AtlasCom communicator;
        private string projectFolder { get; set; }
        public Job currentJob;


        public MessageParser()
        {
            this.dicf["connect"] = new Func<JObject, string>(_connect);
            this.dicf["disconnect"] = new Func<JObject, string>(_disconnect);
            this.dicf["refresh"] = new Func<JObject, string>(_refresh);
            this.dicf["startAtlas"] = new Func<JObject, string>(_startAtlas);
            this.dicf["startSample"] = new Func<JObject, string>(_startSample);
            this.dicf["initializeSample"] = new Func<JObject, string>(_initializeSample);
            this.dicf["cancelSample"] = new Func<JObject, string>(_cancelSample);
            this.dicf["getStatus"] = new Func<JObject, string>(_getStatus);
            this.dicf["getStatusAlert"] = new Func<JObject, string>(_getStatusAlert);
            this.dicf["incomingFile"] = new Func<JObject, string>(_incomingFile);
            this.dicf["getStagePositionXYZ"] = new Func<JObject, string>(_getStagePositionXYZ);
            this.dicf["setStagePositionXYZ"] = new Func<JObject, string>(_setStagePositionXYZ);
            this.dicf["grabFrame"] = new Func<JObject, string>(_grabFrame);
            this.dicf["SmartSEMcmd"] = new Func<JObject, string>(_SmartSEMcmd);
            this.dicf["autoFocusSurface"] = new Func<JObject, string>(_autoFocusSurface); // Later we will have autofocus on Face, which will be different
            this.dicf["autoFocusEmergency"] = new Func<JObject, string>(_autoFocusEmergency);
            this.dicf["resume"] = new Func<JObject, string>(_resume);
            this.dicf["resume_server_request"] = new Func<JObject, string>(_resume_server_request);
            this.dicf["updateJobStagePositionXY"] = new Func<JObject, string>(_updateJobStagePositionXY);
            this.dicf["pause"] = new Func<JObject, string>(_pause);
            this.dicf["showUI"] = new Func<JObject, string>(_showUI);
            this.dicf["saveState"] = new Func<JObject, string>(_saveState);
            this.dicf["loadState"] = new Func<JObject, string>(_loadState);
            this.dicf["pushBC"] = new Func<JObject, string>(_pushBC);
            /////////#################### Experimental (not tested)
            this.dicf["FIBMark"] = new Func<JObject, string>(_FIBMark);
            this.dicf["autoCP"] = new Func<JObject, string>(_autoCP);
            this.dicf["doDeposition"] = new Func<JObject, string>(_doDeposition);
            this.dicf["getMasterFolder"] = new Func<JObject, string>(_getMasterFolder);
            this.dicf["autoTracking"] = new Func<JObject, string>(_autoTracking);
            this.dicf["makeTrenchRecipe"] = new Func<JObject, string>(_makeTrenchRecipe);
            this.projectFolder = Settings.getSetting("output_folder");



            this.communicator = new AtlasCom();
        }


        //  Manage
        /// <summary>
        /// When a new message is coming, parses the uri and consults the dictionary of functions
        /// </summary>
        public string manage(JObject message)
        {
            string function = (string)message["uri"];
            var answer = this.dicf[function].DynamicInvoke(message);
            return (string)answer;
        }

        //  Manage
        /// <summary>
        /// When a new message is coming, parses the uri and consults the dictionary of functions
        /// This allows to call the function without using JSON message with a dictionary to encode the name of the function
        /// </summary>
        public string manage(string uri_function,JObject values)
        {
            var answer = this.dicf[uri_function].DynamicInvoke(values);
            return (string)answer;
        }

        //  showUI
        /// <summary>
        /// Shows ATLAS interface
        /// </summary>
        public string _showUI(JObject message)
        {
            if (this.communicator.isConnected())
            {
                this.communicator.showUI();
            }
            return "";
        }

        //  Connect
        /// <summary>
        /// Connect
        ///  Connects to the system.
        /// 1. Obtain the value of Sec-Socket-Key request header without any leading and trailing whitespace
        /// 2. Concatenate it with "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        /// 3. Compute SHA-1 and Base64 code of it
        /// 4. Write it back as value of Sec-Socket-Accept response header as part of the response.
        ///
        ///</summary>
        public string _connect(JObject message)
        { 
           
           // Check if the engine is available
           string log="";
           // If is imaging return status
           if (this.communicator.isImaging())
           {
              JObject reply = new JObject(new JProperty("Connection", "Accepted"),
                            new JProperty("Status", "Imaging"));
              this.communicator.addMessage("Someone called connect, but we are busy imaging. Reply:" + reply.ToString());
              return reply.ToString(Formatting.None);
            }

           if (this.communicator.isConnected())
           {
                JObject reply = new JObject(new JProperty("Connection", "Accepted"),
                            new JProperty("Status", "Connected."));
            Console.WriteLine("Method Connect. Reply:" + reply.ToString());
            return reply.ToString(Formatting.None);
           } 
           else{

              if(!this.communicator.Connect(ref log)) // Try to connect
              {
               
                JObject reply_error = new JObject(new JProperty("Connection", "Denied"),
                                new JProperty("Status", log));
                return reply_error.ToString(Formatting.None);
              }
                JObject reply = new JObject(new JProperty("Connection", "Accepted"),
                          new JProperty("Status", "Connected"));
                Console.WriteLine("Method Connect. Reply:" + reply.ToString());
                return reply.ToString(Formatting.None);
            }
          
            
        }

        //  startAtlas
        /// <summary>
        /// Starts ATLAS software
        /// </summary>
        public string _startAtlas(JObject message)
        {
            string minfo="";
            JObject reply;
            if (!this.communicator.isImaging())
            {
                // Refresh values
                this.communicator.startAtlas(ref minfo);
                reply = new JObject(new JProperty("Status", minfo)); ;
            }
            else
            {
                reply = new JObject(new JProperty("Error", "Connection Rejected. Not able to start Atlas."));
            }
            return reply.ToString(Formatting.None);
        }

        // Refresh
        /// <summary>
        /// Saves the state of current microscope. To look which parameters are saved, look into Atlas Communicator class.
        /// </summary>
        /// <param name="version"></param>
        public string _refresh(JObject message)
        {
           
           JObject reply;
           if (!this.communicator.isImaging())
           {
                // Refresh values
                this.communicator.Refresh();
                reply = new JObject( new JProperty("Status", "Settings refreshed."));;
           }
           else
           {
                 reply = new JObject( new JProperty("Error", "Connection Rejected. Not able to refresh."));
           }
           return reply.ToString(Formatting.None);
        }


        //  Disconnect
        /// <summary>
        /// Closes communication of client with ATLAS. ATLAS is killed. This function is called from the server itself.
        /// </summary>
        public string _disconnect()
        {
            string log = "";
            this.communicator.Disconnect(ref log);
            return log;
        }

        //  Disconnect
        /// <summary>
        /// Disconnect
        ///  Closes communication of client with ATLAS. ATLAS is killed. This function can be called remotely.
        /// </summary>
        /// <param name="version"></param>
        public string _disconnect(JObject message)
        {
            JObject reply;
            string log = "";
            if (this.communicator.Disconnect(ref log))
            {
                    reply = new JObject(new JProperty("Log", log));
                    return reply.ToString(Formatting.None);
             }
            reply = new JObject(new JProperty("Error", "Not possible to disconnect :" + log)); 
            return reply.ToString(Formatting.None);
        }

        //  InitializeSample
        /// <summary>
        /// InitializeSample
        /// 
        /// </summary>
        /// <param name="version"></param>
        public string _initializeSample(JObject message)
        {
            JObject reply;
            if (Job.state == "RUNNING")
            {
                string error = "";
                error = "Cannot initialize Rejected : Job is currently running, cannot be started again until is finished or cancelled.";
                reply = new JObject(new JProperty("Error", error));
                return reply.ToString();
            }

            this.currentJob = new Job();
            this.currentJob.initialize(this.communicator);
            // Decode incoming information
            //*****************************************
            // ATLAS folder information
            this.currentJob.job_folder = this.projectFolder + "\\" + (string)message["atlas_folder"];
            this.currentJob.project_folder = this.projectFolder;
            this.currentJob.alt_file_setup_path = (string)message["local_setup_file"];
            // ********************************************
            // ROI information

            this.currentJob.job_name = (string)message["job_name"];
            this.currentJob.tag = (string)message["tag"];

            this.currentJob.roi.Width = Double.Parse((string)message["roi_x_length"], CultureInfo.InvariantCulture);
            this.currentJob.roi.Height = Double.Parse((string)message["roi_y_length"], CultureInfo.InvariantCulture);
            this.currentJob.roi.Depth = Double.Parse((string)message["roi_depth"], CultureInfo.InvariantCulture);

            this.currentJob.slice_thickness = Double.Parse((string)message["SliceThickness"], CultureInfo.InvariantCulture);
            this.currentJob.surf_roi_x = Double.Parse((string)message["dX"], CultureInfo.InvariantCulture);
            this.currentJob.surf_roi_y = Double.Parse((string)message["dY"], CultureInfo.InvariantCulture);
            this.currentJob.defaultStabilizationPeriod = Int32.Parse((string)message["DefaultStabilizationDuration"], CultureInfo.InvariantCulture);
            this.currentJob.af_interval = Int32.Parse((string)message["AF_Interval"], CultureInfo.InvariantCulture);
            this.currentJob.swapCPposition.X = (float)Double.Parse((string)message["cp_x"], CultureInfo.InvariantCulture);
            this.currentJob.swapCPposition.Y = (float)Double.Parse((string)message["cp_y"], CultureInfo.InvariantCulture);

            //***********************************************
            // Folder of setup_file
            //***********************************************
            // 
            this.currentJob.file_setup_path = this.currentJob.job_folder + "\\" + (string)message["setup"]; // saved in the same place as the job is running
            this.currentJob.updatePositionBeforeStart = bool.Parse((string)message["updatePositionsBeforeStart"]);
            //***********************************************
            this.currentJob.scale_unit = (string)message["unit_scale"];
            this.currentJob.position.x = Double.Parse((string)message["x"], CultureInfo.InvariantCulture);
            this.currentJob.position.y = Double.Parse((string)message["y"], CultureInfo.InvariantCulture);
            this.currentJob.position.z = Double.Parse((string)message["z"], CultureInfo.InvariantCulture);
            this.currentJob.setFilePending(this.currentJob.file_setup_path);
            Job.state = "INITIALIZED";
            this.currentJob.saveToJson(this.currentJob.job_folder); // Needed for run_checker.
            reply = new JObject(new JProperty(new JProperty("Connection", "Accepted"))); // anyway, the reply is just an ACK

            return reply.ToString(Formatting.None);
        }
        
        //  StartSample 
        /// <summary>
        /// 
        /// 
        /// </summary>
        /// <param name="version"></param>
        public string _startSample(JObject message)
        {
            JObject reply;
            // check if any pending file and that we have a proper Setup file.
            if (currentJob.isFilePending())
            {
                reply = new JObject(new JProperty("Error", "Task Rejected : File pending to be received."));
                return reply.ToString();
            }
            if (Job.state == "INITIALIZED")
            {
                this.currentJob.start();
            }
            else
            {
                string error = "";
                if (Job.state != "INITIALIZED") error = "Task rejected : Job not initialized.";
                if (Job.state == "RUNNING") error += "Task Rejected : Job is currently running, cannot be started again.";
                reply = new JObject(new JProperty("Error", error));
                return reply.ToString();

            }

            reply = new JObject(new JProperty(new JProperty("Connection", "Accepted"))); // anyway, the reply is just an ACK
           
            return reply.ToString(Formatting.None);
        }
       
        //  CancelSample
        /// <summary>
        /// CancelSample
        /// 
        /// </summary>
        /// <param name="version"></param>
        public string _cancelSample(JObject message)
        {
            JObject reply;
            string log = "Run cancelled by user";
            this.communicator.cancelRun();
            reply = new JObject(new JProperty("Log", log));
            return reply.ToString(Formatting.None);
        }
        
        
        //  Get Status
        /// <summary>
        /// Get Status
        /// 
        /// </summary>
        public string _getStatusAlert(JObject message)
        {
            lock (AtlasCom.syncLock)
            {
                
                JObject reply;
                string status = "";
                // In which state are we?
                if (Job.state == "STARTING" || Job.state == "RUNNING" || Job.state == "IDLE") // Preparing sample, it is not possible to pause in this case
                {

                    if (BufferRun.messageAvailable())
                    {
                        status = "MESSAGE_READY";
                    }
                    else
                    {
                        status = "OK";
                    }
                    reply = new JObject(new JProperty("Alert", status));
                    return reply.ToString(Formatting.None);

                }
                if (Job.state == "PAUSED")
                {
                    status = "PAUSED";
                    reply = new JObject(new JProperty("Alert", status));
                    return reply.ToString(Formatting.None);


                }
                if (Job.state == "COMPLETED")
                {
                    status = "COMPLETED";
                    Job.state = "IDLE";
                    reply = new JObject(new JProperty("Alert", status));
                    return reply.ToString(Formatting.None);

                }
                if (Job.state == "CANCELLED")
                {
                    status = "CANCELLED";
                    Job.state = "IDLE";
                    reply = new JObject(new JProperty("Alert", status));
                    return reply.ToString(Formatting.None);
                }

                status = Job.state;
                reply = new JObject(new JProperty("Alert", status));
                return reply.ToString(Formatting.None);


            }
        }       
        
        public string _getStatus(JObject message) {
            JObject reply;
            string status = "";
            string smessage = "";
            if (BufferRun.messageAvailable())
            {
                status = "MESSAGE_DELIVERED";
                smessage = this.communicator.getMessage();
            }
            else
            {
                status = "NO MESSAGES AVAILABLE";
            }
            reply = new JObject(new JProperty("Alert", status), new JProperty("Message", smessage));
            return reply.ToString(Formatting.None);    
        }

        public string _resume_server_request(JObject message)
        {
           
            JObject reply;
            this.currentJob.resume();
            reply = new JObject(new JProperty("Error", ""));
            return reply.ToString(Formatting.None);
        }

        public string _resume(JObject message)
        {        
            JObject reply;
            this.communicator.resumeRun();
            reply = new JObject(new JProperty("Error", ""));
            return reply.ToString(Formatting.None);
        }

        public string _pause(JObject message)
        {
           
            JObject reply;
            this.communicator.pauseRun();
            reply = new JObject(new JProperty("Error", ""));
            return reply.ToString(Formatting.None);
        }
                
        public string _incomingFile(JObject message)
        {
                     
            string data = (string)message["data"];
            JObject reply;
            if (this.currentJob.isFilePending())
            {
                    // Find name of pending file
                    
                    string filename = this.currentJob.getPendingFileName();
                    // This text is added only once to the file.
                    try
                    {
                        string mpath = Path.GetDirectoryName(filename);
                        if (!Directory.Exists(mpath))
                        {
                         Directory.CreateDirectory(mpath);
                        }
                        data = data.Replace("\0", string.Empty); // Remove Null characters from buffer
                        System.IO.File.WriteAllText(filename, data);
                        // save it in the right place
                        // We should check that everything is alright
                    }
                    catch (IOException e)
                    {
                        Console.WriteLine(
                            "{0}: The write operation could not " +
                            "be performed.",
                            e.GetType().Name);
                            reply = new JObject(new JProperty("Error", "Error writing file."));
                            this.currentJob.setFilePending(filename);
                            return reply.ToString();
                    }
                        
                        reply = new JObject(new JProperty("Connection", "Accepted"));
                }
                else
                {
                    reply = new JObject(new JProperty("Error", "Server is not expecting any file."));
                }
            
            return reply.ToString(Formatting.None);
        }

        public string _getStagePositionXYZ(JObject message)
        {
            float xp, yp, zp, rp, tp, mp;
            xp = yp = zp = rp = tp = mp = 0.0f;
            PointEM pointEM = new PointEM();
            pointEM.x = xp;
            pointEM.y = yp;
            pointEM.z = zp;
            pointEM.r = rp;
            pointEM.t = tp;
            pointEM.m = mp;
            string e = "";
            this.communicator.GetStagePosition(ref pointEM, ref e);
            // answer SEM_getStagePosition(xp, yp, zp, rpos, tpos, mpos);
            JObject reply = new JObject(new JProperty("xpos",pointEM.x.ToString()),
                                        new JProperty("ypos", pointEM.y.ToString()),
                                        new JProperty("zpos", pointEM.z.ToString()),
                                        new JProperty("error", e));
            return reply.ToString(Formatting.None);
        }

        private string _updateJobStagePositionXY(JObject message)
        {
            JObject reply;
            if (this.communicator.isConnected())
            {
               var xpos = (string)message["xpos"];
               var ypos = (string)message["ypos"];
               try
               {
                    currentJob.position.x = float.Parse(xpos, CultureInfo.InvariantCulture.NumberFormat);
                    currentJob.position.y = float.Parse(ypos, CultureInfo.InvariantCulture.NumberFormat);
               }
               catch (System.FormatException)
               {
                    reply = new JObject(new JProperty("Error", "Formatting problem."));
                    return reply.ToString(Formatting.None);
               }
              
                reply = new JObject(new JProperty("Error", ""));
                return reply.ToString(Formatting.None);
            }
            else
            {
                reply = new JObject(new JProperty("Error", "Connection Rejected : Not connected to microscope."));
                return reply.ToString(Formatting.None);
            }

        }

        public string _setStagePositionXYZ(JObject message)
        {
            if (this.communicator.isConnected())
            { 
            string current_scale = "";
            JObject reply;
            // Either you get the scale from the message or you set it up previously for the whole run
            foreach (JProperty property in message.Properties())
            {
                if (property.Name.CompareTo("scale") == 0)
                {
                    current_scale = (string)property.Value;
                    break;
                }
            }
            if (current_scale.Length == 0)
            {
                if (this.currentJob.scale_unit.CompareTo("NONE") == 0)
                {
                    reply = new JObject(new JProperty("Error", "NO SCALE units specified."));
                    return reply.ToString(Formatting.None);
                }
                current_scale = this.currentJob.scale_unit;
            }

            string xpos = (string)message["xpos"];
            string ypos = (string)message["ypos"];
            string zpos = (string)message["zpos"];
            float xp, yp, zp, rp, tp, mp;
            xp = yp = zp = rp = tp = mp = 0.0f;
            PointEM pointEM = new PointEM();

            pointEM.r = rp;
            pointEM.t = tp;
            pointEM.m = mp;

            string e = "";
                // this.communicator.GetStagePosition(ref coords, ref e);
                try
                {
                    pointEM.x = float.Parse(xpos, CultureInfo.InvariantCulture.NumberFormat);
                    pointEM.y = float.Parse(ypos, CultureInfo.InvariantCulture.NumberFormat);
                    pointEM.z = float.Parse(zpos, CultureInfo.InvariantCulture.NumberFormat);
                }
                catch (System.FormatException exc)
                {
                    reply = new JObject(new JProperty("error", exc.ToString()));
                    return reply.ToString(Formatting.None);
                }
            this.communicator.safeMove(pointEM, current_scale, ref e);
            reply = new JObject(
                                 new JProperty("xpos", pointEM.x.ToString()),
                                 new JProperty("ypos", pointEM.y.ToString()),
                                 new JProperty("zpos", pointEM.z.ToString()),
                                 new JProperty("error", e));
            return reply.ToString(Formatting.None);
        }
            else
            {
                JObject reply = new JObject(new JProperty("Error", "Connection Rejected : Not connected to microscope."));
                return reply.ToString(Formatting.None);
            }

        }
                
        public string _grabFrame(JObject message)
        {
            JObject reply;
           
            string tag = (string)message["tag"];
            string share = (string)message["in_shared_folder"];
            String timeStamp = DateTime.Now.ToString("yyyyMMddHHmmssffff");
            string imagename = tag + "_" + timeStamp;
            float dwellTime = (float)message["dwell_time"];
            float pixelSize = (float)message["pixel_size"];
            int resolution = (int)message["resolution"];
            int lineavg = (int)message["line_average"];
            int scanrotation = (int)message["scan_rotation"];


            
            bool sharing_folder = (share.CompareTo("True") == 0);
            bool tmp_dir = false;

            string frame_directory="";
            if (sharing_folder)
            {
                frame_directory = (string)message["shared_folder"];
            }
            else
            {
                    if (currentJob != null)
                    {
                        frame_directory = this.currentJob.job_folder;
                        this.currentJob.acquired_frames_folder = frame_directory;
                    }
                    else
                    {
                        // Create tmp folder
                        frame_directory = this.GetTemporaryDirectory();
                         tmp_dir = true;
                    }
            }

           
           // This text is added only once to the file.
           try
           {

                frame_directory = MessageParser.NormalizePath(frame_directory);
                if (!Directory.Exists(frame_directory))
                {
                    Directory.CreateDirectory(frame_directory);
                }
                // GRABFRAME
                string error = "";
                this.communicator.GrabFrameSEM(frame_directory, imagename, resolution, pixelSize, dwellTime, lineavg, scanrotation, ref error);
            }
            catch (DirectoryNotFoundException)
            {
                reply = new JObject(new JProperty("Error", "Directory not found."));
                return reply.ToString(Formatting.None);
            }
            catch (IOException e)
            {
                Console.WriteLine(
                    "{0}: The write operation could not be performed.", e.GetType().Name);
                reply = new JObject(new JProperty("Error", "Error writing file."));
                return reply.ToString(Formatting.None);
            }


            if (!sharing_folder)
            {
                // Get the file from the picture and send it back
                string inputFilename = frame_directory + "\\" + imagename + ".tif";

                string encoded = this.EncodeWithString(inputFilename);
                // byte[] fileBytes = File.ReadAllBytes(inputFilename);

                reply = new JObject(new JProperty("filename", imagename), new JProperty("Connection", "Accepted"), new JProperty("imagefile", encoded));
                if (tmp_dir)
                {
                    DeleteDir(frame_directory);
                }

                return reply.ToString(Formatting.None);

            }
            reply = new JObject(new JProperty("filename", imagename), new JProperty("Connection", "Accepted"));

            return reply.ToString(Formatting.None);
        }

        public string _pushBC(JObject message)
        {
            JObject reply;
           
                if (Job.state == "PAUSED")
                {
                    this.communicator.pushBC();
                    reply = new JObject(new JProperty("Error", "BC values pushed"));
                }
                else
                {
                    reply = new JObject(new JProperty("Error", "Status has to be paused before pushing B&C"));
                }
            return reply.ToString(Formatting.None);
        }

        public static string NormalizePath(string path)
        {
            return Path.GetFullPath(new Uri(path).LocalPath)
                       .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                       .ToUpperInvariant();
        }

        public string GetTemporaryDirectory()
        {
            string tempFolder = Path.GetTempFileName();
            File.Delete(tempFolder);
            Directory.CreateDirectory(tempFolder);

            return tempFolder;
        }

        public static void DeleteDir(string dir)
        {
            System.IO.DirectoryInfo directory = new DirectoryInfo(dir);
            foreach (System.IO.FileInfo file in directory.GetFiles()) file.Delete();
            foreach (System.IO.DirectoryInfo subDirectory in directory.GetDirectories()) subDirectory.Delete(true);
            directory.Delete(true);
        }

        public string EncodeWithString(string inputFileName)
        {
            System.IO.FileStream inFile;
            byte[] binaryData;
            try
            {
                inFile = new System.IO.FileStream(inputFileName,
                                     System.IO.FileMode.Open,
                                     System.IO.FileAccess.Read);
                binaryData = new Byte[inFile.Length];
                long bytesRead = inFile.Read(binaryData, 0,
                              (int)inFile.Length);
                inFile.Close();
            }
            catch (System.Exception exp)
            {
                // Error creating stream or reading from it.
                return(exp.Message);
            }

            // Convert the binary input into Base64 UUEncoded output.
            string base64String;
            try
            {
                base64String = System.Convert.ToBase64String(binaryData,
                                          0,
                                          binaryData.Length);
            }
            catch (System.ArgumentNullException)
            {
                return ("Binary data array is null.");
            }
            return base64String;
        }

        public string _autoFocusSurface(JObject message)
        {
            JObject reply;
            string error = "";
            PointEM currentpos = new PointEM();
            this.communicator.GetStagePosition(ref currentpos,ref error);
            if (!this.communicator.autoFocusOnSample(ref error, "SESI", ref currentpos,1))
            {
              
                    reply = new JObject(new JProperty("ERROR", error));
                    return reply.ToString(Formatting.None);
            }
            reply = new JObject(new JProperty("Status", error));
            return reply.ToString(Formatting.None);
        }

        public string _autoFocusEmergency(JObject message)
        {
            JObject reply;
            string error = "";
            PointEM currentpos = new PointEM();
            this.communicator.GetStagePosition(ref currentpos, ref error);
            if (!this.communicator.AFASEmergency(ref error, "ESB", ref currentpos))
            {

                reply = new JObject(new JProperty("ERROR", error));
                return reply.ToString(Formatting.None);
            }
            reply = new JObject(new JProperty("Status", error));
            return reply.ToString(Formatting.None);
        }

        public string _SmartSEMcmd(JObject message)
        {
           JObject reply;

        string command = (string)message["command"];
        string value = (string)message["value"];
        string e = "";
        switch (command)
        {
            case ("EHT_KV"):
                {
                    // Value is in volts, cames in KV
                    float fvalue = float.Parse(value, CultureInfo.InvariantCulture);
                    fvalue = fvalue * 1000f;
                    if (fvalue > 10 && fvalue < 30000)
                    {
                        this.communicator.doSmartSEMCommand("SET", "AP_MANUALKV", ref fvalue, ref e);
                        Thread.Sleep(2000);
                    }
                    else
                    {
                        e = "ERROR: KV too high or too low";
                    }
                    break;
                }
            default:
                {
                    e = "COMMAND UNKNOWN";
                    break;
                }

        }
           
            reply = new JObject( new JProperty("error", e));
            return reply.ToString(Formatting.None);

        }

        public string _loadState(JObject message)
        {
           
            JObject reply;
            if (Job.state == "RUNNING")
            {
                string error = "";
                error = "Cannot initialize Rejected : Job is currently running, cannot be started again until is finished or cancelled.";
                reply = new JObject(new JProperty("Error", error));
                return reply.ToString();
            }

                // Decode incoming information
                //*****************************************
                // Decode state variables
                StateFIBSEM m_state = new StateFIBSEM();
                if (ManageState.load_json(message.ToString(Formatting.None)))
                {
                    // ********************************************
                    reply = new JObject(new JProperty(new JProperty("Status", "State loaded succesfully"))); // anyway, the reply is just an ACK
                }
                else
                {
                    reply = new JObject(new JProperty("Error", "Information of state couldn't be read"));
                }
            
            return reply.ToString(Formatting.None);
        }

        public string _saveState(JObject message)
        {
           
            JObject reply;
            if (Job.state == "RUNNING")
            {
                string error = "";
                error = "Cannot initialize Rejected : Job is currently running, cannot be started again until is finished or cancelled.";
                reply = new JObject(new JProperty("Error", error));
                return reply.ToString();
            }
                // Decode incoming information
                //*****************************************
                // Decode state variables
                StateFIBSEM cstate = this.communicator.getState();
                string json_state = ManageState.save_json(cstate);
                {
                    // ********************************************
                    reply = new JObject(new JProperty(new JProperty("state", json_state))); // anyway, the reply is just an ACK
                }

            
                reply = new JObject(new JProperty("Error", "Connection Rejected : User not identified"));
            return reply.ToString(Formatting.None);
        }

        /****
         * EXPERIMENTAL. Not fully implemented or not fully tested functions that provide extra services
         * 
        */
        /// <summary>
        /// Launches the Reporter from the automaton and throws a service to automatically shift the windows of acquisition
        /// It is not fully implemented yet because the dependencies with ATLAS.
        /// 
        /// </summary>
        /// <param name="message"></param>
        /// <returns></returns>
        public string _autoTracking(JObject message)
        {
           
            JObject reply;
            if (Job.state == "RUNNING")
            {
                string error = "";
                error = "Cannot initialize Rejected : Job is currently running, cannot be started again until is finished or cancelled.";
                reply = new JObject(new JProperty("Error", error));
                return reply.ToString();
            }

                this.communicator.autoTracking(this.currentJob);
                reply = new JObject(new JProperty(new JProperty("status","Sample tracking engaged."))); // anyway, the reply is just an ACK
            
            return reply.ToString(Formatting.None);
        }

        /// <summary>
        /// Not implemented in ATLAS library, so cannot be executed
        /// </summary>
        /// <param name="message"></param>
        /// <returns></returns>
        public string _doDeposition(JObject message)
        {
           
            JObject reply= new JObject(new JProperty("Error", "Connection Rejected : User not identified"));
            if (Job.state != "INITIALIZED")
            {
                throw new NotImplementedException();
            }
            else
            {
                throw new NotImplementedException();
            }
            return reply.ToString(Formatting.None);
        }
        /// <summary>
        /// Create a FIB Mark. Useful, for example, to see misalignments between kVs or modalities.
        /// </summary>
        /// <param name="message"></param>
        /// <returns></returns>

        public string _FIBMark(JObject message)
        {         
        JObject reply;
        string frame_directory = (string)message["shared_folder"];
        float distance_x = (float)message["distance_x"];
        float distance_y = (float)message["distance_y"];
        this.communicator.FIBMark(frame_directory, distance_x, distance_y);
        reply = new JObject(new JProperty("Status", "Mark in progress."));
        return reply.ToString(Formatting.None);
        }
        /// <summary>
        /// Automatic coincidence point independent of the workflow
        /// </summary>
        /// <param name="message"></param>
        /// <returns></returns>

        public string _autoCP(JObject message)
        {
           
            JObject reply;
             string scale_unit = (string)message["unit_scale"];
                PointEM mp = new PointEM();
                string m_error = "";
                float shift_cp_x = (float)message["cp_x"];
                float shift_cp_y = (float)message["cp_y"];
                this.communicator.GetStagePosition(ref mp,ref m_error);
                string frame_directory = (string)message["shared_folder"];
                this.communicator.findCoincidencePoint(ref mp, scale_unit, frame_directory,new System.Drawing.PointF(-50.0f,0.0f), ref m_error);
                reply = new JObject(new JProperty("Status", "Coincidence point in completed."));
            return reply.ToString(Formatting.None);
        }



        public string _makeTrenchRecipe(JObject message)
        {
           
            JObject reply;
              
                PointEM mp = new PointEM();
                string m_error = "";
                currentJob = new Job();
                currentJob.job_folder = (string)message["shared_folder"];
                currentJob.file_setup_path = (string)message["profile_path"];
                currentJob.scale_unit = (string)message["unit_scale"];
                currentJob.roi = new ROI();
                currentJob.roi.Height = 10;

                this.communicator.PrepareTrenches(ref currentJob, ref mp, ref m_error, false, true);
                reply = new JObject(new JProperty("Status", "Trench completed."));
             return reply.ToString(Formatting.None);
        }



        /// <summary>
        /// Obtain folder where images of acquisition are stored
        /// </summary>
        /// <param name="message"></param>
        /// <returns></returns>
        public string _getMasterFolder(JObject message)
        {
           
            JObject reply;
           
                reply = new JObject(new JProperty("folder_name", this.projectFolder));
            
            return reply.ToString(Formatting.None);
        }


    }
}



