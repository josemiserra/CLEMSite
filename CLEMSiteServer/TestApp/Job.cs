using System;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
using System.Timers;
using System.Collections;
using System.Threading;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using System.IO;
using System.Drawing;

namespace msite
{

    public class Job

    {
        public static int numOfJobs = 0;
        public string tag;
        public static int MAX_PINGS = 12;
        public static int WAIT_INTERVAL = 5000; // 5 seconds
        public ROI roi;
        public static string state = "IDLE";
        public long autotune_period = 2700000; // Autotune in miliseconds, default 45 minutess
        public AtlasCom communicator;

        Queue filePendingList = new Queue();
        public bool ping_received = false;

        public bool isLast = false;

        public string job_folder;
        public string project_folder { get; set; }
        public string job_name { get; set; }
        public string file_setup_path { get; set; }
        public string alt_file_setup_path { get; set; }
        public string scale_unit { get; set; }



        public PointEM position;

        public string acquired_frames_folder = "";
        public string keyframes_folder = "";

        // Parameter to be configured, in case we want to ignore ROI.Width and use the actual trench size
        public bool fullROIWidth = false;
        public Thread startSample;
        public double slice_thickness;
        public double surf_roi_x;
        public double surf_roi_y;
        public int defaultStabilizationPeriod;
        public int af_interval;
        public bool updatePositionBeforeStart;
        private static Random rand = new Random();
        public uint jobId;
        public PointF swapCPposition = new System.Drawing.PointF();
        public PointF firstAF = new System.Drawing.PointF();

        public Job()
        {

            roi = new ROI();
            roi.Depth = 0;
            roi.Height = 0;
            roi.Width = 0;
            position = new PointEM();
            Job.state = "IDLE";
            scale_unit = "NONE";
            jobId = GenerateJobId();
            swapCPposition.X = -50.0f;
            swapCPposition.Y = 0.0f;

        }

        /// <summary>
        /// Generates Job identificator
        /// Each workflow has a job id.
        /// The Job class has a track of the steps occurring during the workflow.
        /// The JobId is used then to generate a unique identifier or the job, which
        /// can be used to reconnect from the client and keep track in case of disconnection.
        /// </summary>
        /// <returns></returns>
        public static uint GenerateJobId()
        {
            return (uint)(rand.Next(1 << 30)) << 2 | (uint)(rand.Next(1 << 2));
        }



        public bool initialize(AtlasCom communicator)
        {
            Job.state = "IDLE";
            this.communicator = communicator;
            return true;
        }

        public void start()
        {
            Job.state = "STARTING";
            string error = "";
            // You can also use an anonymous delegate to do this.
            this.startSample = new Thread(delegate ()
            {
                this.communicator.StartSample(this, ref error);
            });
            this.startSample.Start();
            Thread.Sleep(10000); //10 sec in case something is wrong immediately
            Match match = Regex.Match(error, @"ERROR");
            if (match.Success)
            {
                JObject reply = new JObject(new JProperty("Error", error));
                this.communicator.addMessage(reply.ToString());
            }

        }

        public void resume()
        {
            // Could be more threads, but we check if the start one is alive
            if (this.startSample.IsAlive)
            {
                this.startSample.Interrupt();
            }
        }

        public void cleanJob()
        {
            this.position.x = 0.0f;
            this.position.y = 0.0f;
            this.position.z = 0.0f;
            this.tag = "";
            this.filePendingList.Clear();
            this.ping_received = false;

        }
        public void setFilePending(string filenameList)
        {
            filePendingList.Enqueue(filenameList);
        }
        public void setFilesPending(string[] filenameList)
        {
            foreach (string item in filenameList)
            {
                filePendingList.Enqueue(item);
            }
        }
        public string getPendingFileName()
        {
            return (string)filePendingList.Dequeue();
        }
        public bool isFilePending()
        {
            return filePendingList.Count > 0;

        }

        public override string ToString()
        {
            //***********************************************
            JObject to_save = new JObject(new JProperty("job_number", Job.numOfJobs));
            to_save.Add("job_state", Job.state);
            to_save.Add("roi_y_length", this.roi.Height);
            to_save.Add("roi_x_length", this.roi.Width);
            to_save.Add("roi_depth", this.roi.Depth);
            to_save.Add("job_folder", this.job_folder);
            to_save.Add("job_name", this.job_name);
            to_save.Add("project_folder", this.project_folder);
            to_save.Add("local_setup_file", this.alt_file_setup_path);
            to_save.Add("tag", this.tag);
            to_save.Add("SliceThickness", this.slice_thickness);
            to_save.Add("dX", this.surf_roi_x);
            to_save.Add("dY", this.surf_roi_y);
            to_save.Add("setup_file", this.file_setup_path);
            to_save.Add("unit_scale", this.scale_unit);
            to_save.Add("x", this.position.x);
            to_save.Add("y", this.position.y);
            to_save.Add("z", this.position.z);
            to_save.Add("DefaultStabilizationDuration", this.defaultStabilizationPeriod);
            to_save.Add("AF_interval", this.af_interval);
            return to_save.ToString();
        }

        public void saveToJson(string projectFolder)
        {

            //***********************************************
            JObject to_save = new JObject(new JProperty("job_number", Job.numOfJobs));
            to_save.Add("job_state", Job.state);
            to_save.Add("roi_y_length", this.roi.Height);
            to_save.Add("roi_x_length", this.roi.Width);
            to_save.Add("roi_depth", this.roi.Depth);
            to_save.Add("job_folder", this.job_folder);
            to_save.Add("job_name", this.job_name);
            to_save.Add("project_folder", this.project_folder);
            to_save.Add("local_setup_file", this.alt_file_setup_path);
            to_save.Add("tag", this.tag);
            to_save.Add("SliceThickness", this.slice_thickness);
            to_save.Add("dX", this.surf_roi_x);
            to_save.Add("dY", this.surf_roi_y);
            to_save.Add("setup_file", this.file_setup_path);
            to_save.Add("unit_scale", this.scale_unit);
            to_save.Add("x", this.position.x);
            to_save.Add("y", this.position.y);
            to_save.Add("z", this.position.z);
            to_save.Add("DefaultStabilizationDuration", this.defaultStabilizationPeriod);
            to_save.Add("AF_interval", this.af_interval);

            //  string properties = to_save.ToString(Formatting.None);
            // write JSON to a file
            using (System.IO.StreamWriter file = File.CreateText(project_folder+"\\info_sample"+job_name+".json"))
            using (JsonTextWriter writer = new JsonTextWriter(file))
            {
               to_save.WriteTo(writer);
            }
        }
    }

}
