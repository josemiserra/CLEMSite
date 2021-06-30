using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;



namespace msite
{
    public static class Settings
    {

        private static Dictionary<string, string> SettingsValues = new Dictionary<string, string>();
        static Settings()
        {
            Settings.Update();
        }

        public static void Update()
        {
            try
            {
                // Read file from options. Then add by order.
                JObject o1 = JObject.Parse(File.ReadAllText(
                    System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location) +
                    @"\\automaton\\fromMSite\\user.pref"));
                JObject pref = (JObject) o1["preferences"];
                string python_folder = (string) pref["server_images"][0]["python_folder"];
                SettingsValues["python_folder"] = python_folder;
                string automaton_folder = (string) pref["server_images"][0]["automaton_folder"];
                SettingsValues["automaton_folder"] = automaton_folder;
                SettingsValues["output_folder"] = (string) pref["server_images"][0]["dir_frames_output"];
            }
            catch (System.IO.FileNotFoundException e)
            {
                Console.WriteLine(e.ToString());
            }
            catch (Newtonsoft.Json.JsonReaderException e)
            {
                Console.WriteLine(e.ToString());
            }
        }

        public static string getSetting(string key_setting) {
            return SettingsValues[key_setting];
        }

        public static bool setSetting(string key_setting, string value)
        {
            if(SettingsValues.ContainsKey(key_setting))
            {
                SettingsValues[key_setting] = value;
                return true;
            }
            else return false;            
        }

        public static string asString() 
        {
            return  string.Join("", SettingsValues.Select(kv => kv.Key + " = " + kv.Value+ System.Environment.NewLine).ToArray()) ;
        }

    }


}
