using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;
using System.Globalization;
using Newtonsoft.Json;

namespace msite
{
    public class StateFIBSEM
    {
        public static float limit_Z = 42500;
        public double sem_beam_shift_x { get; set; }
        public double sem_beam_shift_y { get; set; }
        public double sem_fov_x { get; set; }
        public double sem_fov_y { get; set; }
        public float brightness_ESB_SEM_trench { get; set; }
        public float contrast_ESB_SEM_trench { get; set; }
        public float brightness_ESB_SEM_focus { get; set; }
        public float contrast_ESB_SEM_focus { get; set; }
        public float brightness_ESB_SEM_acq { get; set; }
        public float contrast_ESB_SEM_acq { get; set; }

        public bool isReady { get; set; } = false;
        public float brightness_sesi_SEM { get; set; }
        public float contrast_sesi_SEM { get; set; }
        public float brightness_sesi_FIB { get; set; }
        public float contrast_sesi_FIB { get; set; }
        public double sem_WD { get; set; } = 5.0;
        public double sem_stigX { get; set; }
        public double sem_stigY { get; set; } 
        public double sem_tilt_correction { get; set; }
        public double x { get; set; }
        public double y { get; set; }
        public double z { get; set; }
        public double r { get; set; }
        public double t { get; set; }
        public double m { get; set; }
        public string sem_aperture_name { get; set; }
        public double sem_voltage { get; set; }
        public double sem_current { get; set; }
        public string fib_aperture_name { get; set; }
    }

    public static class ManageState
    {
        public static bool load_json(string json_state)
        {
            StateFIBSEM deserializedProduct = JsonConvert.DeserializeObject<StateFIBSEM>(json_state);
            return true;

        }
        public static string save_json(StateFIBSEM state)
        {
            string json = JsonConvert.SerializeObject(state, Formatting.None);
            return json;
        }
    }

    public class StateImage
    {
        public double WD { get; set; } = 5.0;
        public double stigX { get; set; } = 0.0;
        public double stigY { get; set; } = 0.0;
        public double beam_shift_x { get; set; } = 0.0;
        public double beam_shift_y { get; set; } = 0.0;
        public double fov_x { get; set; } = 30.0;
        public double fov_y { get; set; } = 30.0;

        public StateImage(){}

        public StateImage(StateFIBSEM stateFIBSEM) { 

               this.stigX = stateFIBSEM.sem_stigX;
               this.stigY = stateFIBSEM.sem_stigY;
               this.beam_shift_x = stateFIBSEM.sem_beam_shift_x;
               this.beam_shift_y = stateFIBSEM.sem_beam_shift_y;

               this.WD = stateFIBSEM.sem_WD;

               this.fov_x = stateFIBSEM.sem_fov_x;
               this.fov_y = stateFIBSEM.sem_fov_y;

            }

        public StateImage(double focus, double stigx, double stigy)
        {
            this.WD = focus;
            this.stigX = stigx;
            this.stigY = stigy;
            this.beam_shift_x = 0.0;
            this.beam_shift_y = 0.0;
        }


    }



}
