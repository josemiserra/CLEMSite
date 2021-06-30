using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

namespace msite
{
    public enum ErrorCode
    {
        API_E_NO_ERROR = 0,
        API_ENGINE_INITIALIZATION_FAILED = 1000,
        API_ENGINE_INITIALIZATION_FAILED_TIME_EXCEEDED = 1001,
        API_ENGINE_INITIALIZATION_FAILED_SYSTEM_READY_TIME_EXCEEDED = 1002,
        API_ENGINE_INITIALIZATION_FAILED_COM_COMPONENTS = 1003,
        API_XML_INVALID = 1004,
        API_XML_FIB_APERTURES_NOT_MATCHING = 1005,
        API_FAILURE_DIGGING_TRENCH = 1006,

        API_TRENCH_NOT_FOUND = 1010,
        API_AUTOFOCUS_ON_XSECTION_FAILED = 1011,
        API_AUTOSTIG_ON_XSECTION_FAILED = 1012,
        API_CP_FAILED = 1013,
    }

    public enum ZeissErrorCode
    {
        API_E_NO_ERROR = 0,
        // Failed to translate parameter into an id
        API_E_GET_TRANSLATE_FAIL = 1000,
        // Failed to get analogue value
        API_E_GET_AP_FAIL = 1001,
        // Failed to get digital value
        API_E_GET_DP_FAIL = 1002,
        // Parameter supplied is not analogue nor digital
        API_E_GET_BAD_PARAMETER = 1003,
        // Failed to translate parameter into an id
        API_E_SET_TRANSLATE_FAIL = 1004,
        // Failed to set a digital state 
        API_E_SET_STATE_FAIL = 1005,
        // Failed to set a float value
        API_E_SET_FLOAT_FAIL = 1006,
        // Value supplied is too low
        API_E_SET_FLOAT_LIMIT_LOW = 1007,
        // Value supplied is too high
        API_E_SET_FLOAT_LIMIT_HIGH = 1008,
        // Value supplied is is of wrong type
        API_E_SET_BAD_VALUE = 1009,
        // Parameter supplied is not analogue nor digital
        API_E_SET_BAD_PARAMETER = 1010,
        // Failed to translate command into an id
        API_E_EXEC_TRANSLATE_FAIL = 1011,
        // Failed to execute command
        API_E_EXEC_CMD_FAIL = 1012,
        // Failed to execute file macro
        API_E_EXEC_MCF_FAIL = 1013,
        // Failed to execute library macro
        API_E_EXEC_MCL_FAIL = 1014,
        // Command supplied is not implemented
        API_E_EXEC_BAD_COMMAND = 1015,
        // Value supplied is is of wrong type
        // Grab command failed
        API_E_GRAB_FAIL = 1016,
        // Get Stage position failed
        API_E_GET_STAGE_FAIL = 1017,
        // Move Stage position failed
        API_E_MOVE_STAGE_FAIL = 1018,
        // API not initialised
        API_E_NOT_INITIALISED = 1019,
        // Failed to translate parameter to an id
        API_E_NOTIFY_TRANSLATE_FAIL = 1020,
        // Set notification failed
        API_E_NOTIFY_SET_FAIL = 1021,
        // Get limits failed
        API_E_GET_LIMITS_FAIL = 1022,
        // Get multiple parameters failed
        API_E_GET_MULTI_FAIL = 1023,
        // Set multiple parameters failed
        API_E_SET_MULTI_FAIL = 1024,
        // Missing API license
        API_E_NOT_LICENSED = 1025,
        // Reserved or not implemented
        API_E_NOT_IMPLEMENTED = 1026,
        // Failed to get user name (Remoting Interface only)
        API_E_GET_USER_NAME_FAIL = 1027,
        // Failed to get user idle state (Remoting Interface only)
        API_E_GET_USER_IDLE_FAIL = 1028,
        // Failed to get the last remoting connection error string (Remoting Interface Only)
        API_E_GET_LAST_REMOTING_CONNECT_ERROR_FAIL = 1029,
        // Failed to remotely logon to the EM Server (username and password may be incorrect or EM Server is not running or User is already logged on
        API_E_EMSERVER_LOGON_FAILED = 1030,
        // Failed to start the EM Server - this may be because the Server is already running or has an internal error. 
        API_E_EMSERVER_START_FAILED = 1031,
        // The command or parameter is currently disabled (you cannot execute or set it).
        API_E_PARAMETER_IS_DISABLED = 1032,
        // Remoting incorrectly configured, use RConfigure to correct
        API_E_REMOTING_NOT_CONFIGURED = 2027,
        // Remoting did not connect to the server
        API_E_REMOTING_FAILED_TO_CONNECT = 2028,
        // Remoting could not start (unknown reason)
        API_E_REMOTING_COULD_NOT_CREATE_INTERFACE = 2029,
        // Remoting: Remote server is not running currently.
        API_E_REMOTING_EMSERVER_NOT_RUNNING = 2030,
        // Remoting: Remote server has no user logged in
        API_E_REMOTING_NO_USER_LOGGED_IN = 2031
    }

    public class ROI
    {
        public ROI() { }
        public ROI(ROI iroi)
        {
            this.Width = iroi.Width;
            this.Depth = iroi.Depth;
            this.offsetX = iroi.offsetX;
            this.offsetY = iroi.offsetY;
            this.Height = iroi.Height;
        }
        public double Width = 0;
        public double Height = 0;
        public double Depth = 0;
        public double offsetX = 0;
        public double offsetY = 0;

        public override string ToString()
        {
            return "Width: " + this.Width + ", Height:" + this.Height+"\n OffsetX :"+this.offsetX+", OffsetY :"+this.offsetY;
        }
    };
    public class AFAS_settings
    {
        public float range_focus;
        public float range_stig;

        public Image_settings focus = new Image_settings();
        public Image_settings stigs = new Image_settings();
    }
    public class Image_settings
    {
        public float dwell_time;
        public int line_average;
        public float pixel_size;
    }

    public struct EmConf
    {

        /*************************************************/
        public static float ESB_trench_screenshot_pixel_size = 0.45f; // 400 nm pixel size for finding trench
        public static float ESB_trench_screenshot_image_dwell_time = 6f;
        public static float ESB_trench_zoom_pixel_size = 0.03f;
        public static float ESB_balance_contrast = 2;
        public static float ESB_balance_brightness = -0.5f;


        // FOCUSING

        // ON SAMPLE
        public static AFAS_settings onSample_COARSE = new AFAS_settings();
        public static AFAS_settings onSample_MEDIUM = new AFAS_settings();
        public static AFAS_settings onSample_FINE = new AFAS_settings();

        // FOR ESB
        public static AFAS_settings onESB_COARSE = new AFAS_settings();

        // XS_FACE
        public static AFAS_settings onFace_COARSE = new AFAS_settings();
        public static AFAS_settings onFace_MEDIUM = new AFAS_settings();
        public static AFAS_settings onFace_MEDIUM_2 = new AFAS_settings();
        public static AFAS_settings onFace_FINE = new AFAS_settings();


        // AUTO CP
        public static Image_settings cp_im = new Image_settings();
        // FEATURES for FOCUS
        public static Image_settings focus_im = new Image_settings();
        // FOCUS analysis
        public static Image_settings focus_an_im = new Image_settings();
        // ESB XS face
        public static Image_settings esb_xs = new Image_settings();

        public static Image_settings focus_CORR = new Image_settings();

        public static void initialize()
        {
            Dictionary<string, float> AFASValues = new Dictionary<string, float>();
            // Read file .csv file from options. Then add by order.
            try
            {
                var reader = new StreamReader(File.OpenRead("settings_AFAS.txt"));
                while (!reader.EndOfStream)
                {

                    var line = reader.ReadLine();
                    var values = line.Split(';');
                    if (values.Count() > 0)
                    {
                        AFASValues.Add(values[0], float.Parse(values[1], CultureInfo.InvariantCulture));
                    }
                }
            }
            catch (System.IO.FileNotFoundException e)
            {
                Console.WriteLine(e.ToString());
            }
            // AFAS file follows the same order than here. 
            // More sophisticated assignments are possible, but for this prototype version, subsequent order 
            // of the file with the classes is more than enough
            // AFAS on Sample
            EmConf.onSample_COARSE.focus.dwell_time = AFASValues["onSample_COARSE.focus.dwell_time"];
            EmConf.onSample_COARSE.focus.line_average = (int)AFASValues["onSample_COARSE.focus.line_average"];
            EmConf.onSample_COARSE.focus.pixel_size = AFASValues["onSample_COARSE.focus.pixel_size"];
            EmConf.onSample_COARSE.range_focus = AFASValues["onSample_COARSE.range_focus"];
            EmConf.onSample_COARSE.stigs.dwell_time = AFASValues["onSample_COARSE.stigs.dwell_time"];
            EmConf.onSample_COARSE.stigs.line_average = (int)AFASValues["onSample_COARSE.stigs.line_average"];
            EmConf.onSample_COARSE.stigs.pixel_size = AFASValues["onSample_COARSE.stigs.pixel_size"];
            EmConf.onSample_COARSE.range_stig = AFASValues["onSample_COARSE.range_stig"];


            EmConf.onSample_MEDIUM.focus.dwell_time = AFASValues["onSample_MEDIUM.focus.dwell_time"];
            EmConf.onSample_MEDIUM.focus.line_average = (int)AFASValues["onSample_MEDIUM.focus.line_average"];
            EmConf.onSample_MEDIUM.focus.pixel_size = AFASValues["onSample_MEDIUM.focus.pixel_size"];
            EmConf.onSample_MEDIUM.range_focus = AFASValues["onSample_MEDIUM.range_focus"];
            EmConf.onSample_MEDIUM.stigs.dwell_time = AFASValues["onSample_MEDIUM.stigs.dwell_time"];
            EmConf.onSample_MEDIUM.stigs.line_average = (int)AFASValues["onSample_MEDIUM.stigs.line_average"];
            EmConf.onSample_MEDIUM.stigs.pixel_size = AFASValues["onSample_MEDIUM.stigs.pixel_size"];
            EmConf.onSample_MEDIUM.range_stig = AFASValues["onSample_MEDIUM.range_stig"];


            EmConf.onSample_FINE.focus.dwell_time = AFASValues["onSample_FINE.focus.dwell_time"];
            EmConf.onSample_FINE.focus.line_average = (int)AFASValues["onSample_FINE.focus.line_average"];
            EmConf.onSample_FINE.focus.pixel_size = AFASValues["onSample_FINE.focus.pixel_size"];
            EmConf.onSample_FINE.range_focus = AFASValues["onSample_FINE.range_focus"];
            EmConf.onSample_FINE.stigs.dwell_time = AFASValues["onSample_FINE.stigs.dwell_time"];
            EmConf.onSample_FINE.stigs.line_average = (int)AFASValues["onSample_FINE.stigs.line_average"];
            EmConf.onSample_FINE.stigs.pixel_size = AFASValues["onSample_FINE.stigs.pixel_size"];
            EmConf.onSample_FINE.range_stig = AFASValues["onSample_FINE.range_stig"];

            // ESB
            EmConf.onESB_COARSE.focus.dwell_time = AFASValues["onESB_COARSE.focus.dwell_time"];
            EmConf.onESB_COARSE.focus.line_average = (int)AFASValues["onESB_COARSE.focus.line_average"];
            EmConf.onESB_COARSE.focus.pixel_size = AFASValues["onESB_COARSE.focus.pixel_size"];
            EmConf.onESB_COARSE.range_focus = AFASValues["onESB_COARSE.range_focus"];
            EmConf.onESB_COARSE.stigs.dwell_time = AFASValues["onESB_COARSE.stigs.dwell_time"];
            EmConf.onESB_COARSE.stigs.line_average = (int)AFASValues["onESB_COARSE.stigs.line_average"];
            EmConf.onESB_COARSE.stigs.pixel_size = AFASValues["onESB_COARSE.stigs.pixel_size"];
            EmConf.onESB_COARSE.range_stig = AFASValues["onESB_COARSE.range_stig"];

            // On XS face focus 0.025f, 7f, 3, 1, stigs 
            EmConf.onFace_COARSE.focus.dwell_time = AFASValues["onFace_COARSE.focus.dwell_time"]; //15
            EmConf.onFace_COARSE.focus.line_average = (int)AFASValues["onFace_COARSE.focus.line_average"];
            EmConf.onFace_COARSE.focus.pixel_size = AFASValues["onFace_COARSE.focus.pixel_size"];
            EmConf.onFace_COARSE.range_focus = AFASValues["onFace_COARSE.range_focus"];
            EmConf.onFace_COARSE.stigs.dwell_time = AFASValues["onFace_COARSE.stigs.dwell_time"]; //15
            EmConf.onFace_COARSE.stigs.line_average = (int)AFASValues["onFace_COARSE.stigs.line_average"];
            EmConf.onFace_COARSE.stigs.pixel_size = AFASValues["onFace_COARSE.stigs.pixel_size"];
            EmConf.onFace_COARSE.range_stig = AFASValues["onFace_COARSE.range_stig"];

            // MEDIUM
            // 0.01f, 1f, 7, 2
            EmConf.onFace_MEDIUM.focus.dwell_time = AFASValues["onFace_MEDIUM.focus.dwell_time"]; //12
            EmConf.onFace_MEDIUM.focus.line_average = (int) AFASValues["onFace_MEDIUM.focus.line_average"];
            EmConf.onFace_MEDIUM.focus.pixel_size = AFASValues["onFace_MEDIUM.focus.pixel_size"];
            EmConf.onFace_MEDIUM.range_focus = AFASValues["onFace_MEDIUM.range_focus"];
            EmConf.onFace_MEDIUM.stigs.dwell_time = AFASValues["onFace_MEDIUM.stigs.dwell_time"]; //12
            EmConf.onFace_MEDIUM.stigs.line_average = (int)AFASValues["onFace_MEDIUM.stigs.line_average"];
            EmConf.onFace_MEDIUM.stigs.pixel_size = AFASValues["onFace_MEDIUM.stigs.pixel_size"];
            EmConf.onFace_MEDIUM.range_stig = AFASValues["onFace_MEDIUM.range_stig"];

            EmConf.onFace_MEDIUM_2.focus.dwell_time = AFASValues["onFace_MEDIUM_2.focus.dwell_time"];//14
            EmConf.onFace_MEDIUM_2.focus.line_average = (int)AFASValues["onFace_MEDIUM_2.focus.line_average"];
            EmConf.onFace_MEDIUM_2.focus.pixel_size = AFASValues["onFace_MEDIUM_2.focus.pixel_size"];
            EmConf.onFace_MEDIUM_2.range_focus = AFASValues["onFace_MEDIUM_2.range_focus"];
            EmConf.onFace_MEDIUM_2.stigs.dwell_time = AFASValues["onFace_MEDIUM_2.stigs.dwell_time"]; // 14
            EmConf.onFace_MEDIUM_2.stigs.line_average = (int) AFASValues["onFace_MEDIUM_2.stigs.line_average"];
            EmConf.onFace_MEDIUM_2.stigs.pixel_size = AFASValues["onFace_MEDIUM_2.stigs.pixel_size"];
            EmConf.onFace_MEDIUM_2.range_stig = AFASValues["onFace_MEDIUM_2.range_stig"];



            // FINE focus 0.005f, 0.1f, 9, 3
            // stigs 0.005f, 0.1f, 9, 3
            EmConf.onFace_FINE.focus.dwell_time = AFASValues["onFace_FINE.focus.dwell_time"]; // 12
            EmConf.onFace_FINE.focus.line_average = (int) AFASValues["onFace_FINE.focus.line_average"];
            EmConf.onFace_FINE.focus.pixel_size = AFASValues["onFace_FINE.focus.pixel_size"];
            EmConf.onFace_FINE.range_focus = AFASValues["onFace_FINE.range_focus"];
            EmConf.onFace_FINE.stigs.dwell_time = AFASValues["onFace_FINE.stigs.dwell_time"];// 12
            EmConf.onFace_FINE.stigs.line_average = (int) AFASValues["onFace_FINE.stigs.line_average"];
            EmConf.onFace_FINE.stigs.pixel_size = AFASValues["onFace_FINE.stigs.pixel_size"];
            EmConf.onFace_FINE.range_stig = AFASValues["onFace_FINE.range_stig"];


            // Image settings
            EmConf.cp_im.dwell_time = AFASValues["cp_im.dwell_time"]; // 8
            EmConf.cp_im.line_average = (int) AFASValues["cp_im.line_average"];
            EmConf.cp_im.pixel_size = AFASValues["cp_im.pixel_size"];

            EmConf.focus_im.dwell_time = AFASValues["focus_im.dwell_time"]; // 8
            EmConf.focus_im.line_average = (int) AFASValues["focus_im.line_average"];
            EmConf.focus_im.pixel_size = AFASValues["focus_im.pixel_size"];

            EmConf.focus_an_im.dwell_time = AFASValues["focus_an_im.dwell_time"];// 7
            EmConf.focus_an_im.line_average = (int) AFASValues["focus_an_im.line_average"];
            EmConf.focus_an_im.pixel_size = AFASValues["focus_an_im.pixel_size"];

            EmConf.esb_xs.pixel_size = AFASValues["esb_xs.pixel_size"];
            EmConf.esb_xs.dwell_time = AFASValues["esb_xs.dwell_time"]; //


            EmConf.focus_CORR.pixel_size = AFASValues["focus_CORR.pixel_size"];
            EmConf.focus_CORR.dwell_time = AFASValues["focus_CORR.dwell_time"]; //7

        }

    }

}
