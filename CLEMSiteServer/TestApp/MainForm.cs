using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;
using LBSoft.IndustrialCtrls;
using LBSoft.IndustrialCtrls.Meters;
using LBSoft.IndustrialCtrls.Utils;

using System.ComponentModel;
using System.Data;
using System.Linq;
using System.Text;
using Microsoft.VisualBasic;
using System.IO;


// Insert the API namespace. You must have added a reference to the CZEMApi ActiveX control in Visual Studio before, as described in the SmartSEM Remote API Manual.
// Set the APILib properties 'Embed Interop types" to False and 'Local copy' to True. 

// Needed for using the VariantWrapper class
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace msite
{
    /// <summary>
    /// Description of MainForm.
    /// </summary>
    public partial class MainForm : Form
    {

        // Create adapter and place a request
        private AsynchronousSocketListener mylistener;
        private delegate void SafeCallDelegate(string text, bool value);
        public static FileStream outputStream;
        public static StreamWriter writer;
        public static TextWriter oldOut;
        private string format = "MMM_ddd_d_HH";
        public bool isFolderReady { get; set; }
        public static readonly object UILock = new object();

        public MainForm()
        {
            //
            // The InitializeComponent() call is required for Windows Forms designer support.
            //

            this.openFileDialog = new System.Windows.Forms.OpenFileDialog();
            this.openFileDialogPreferences = new System.Windows.Forms.OpenFileDialog();

            oldOut = Console.Out;
            try
            {
                outputStream = new FileStream("log_" + DateTime.Now.ToString(format) + ".txt", FileMode.OpenOrCreate,
                    FileAccess.Write);
                writer = new StreamWriter(outputStream);

            }
            catch (Exception e)
            {
                Console.WriteLine("Cannot open LOG file for writing");
                Console.WriteLine(e.Message);
                Console.SetOut(oldOut);
                writer.Close();
                outputStream.Close();
            }

            Console.SetOut(writer);
            InitializeComponent();
            mylistener = new AsynchronousSocketListener();
            MainForm.Log("Server on wait. Click Start to connect to ATLAS.");
            backgroundWorker1.WorkerSupportsCancellation = (true);
            this.isFolderReady = false;

            this.comboBoxIP.Items.Add("127.0.0.1");

            foreach (var element in AsynchronousSocketListener.LocalIPAddresses())
            {
                Regex ip = new Regex(@"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b");
                MatchCollection result = ip.Matches(element.ToString());
                if (result.Count != 0)
                {
                    this.comboBoxIP.Items.Add(result[0]);
                }
            }

            this.comboBoxIP.SelectedIndex = 0;
            this.PortTextBox.Text = AsynchronousSocketListener.port.ToString();
        }

        protected override void OnShown(EventArgs e)
        {
            base.OnShown(e);
        }


        private void StartButton_Click(object sender, EventArgs e)
        {

            Settings.Update();
            if (lbLed1.State == LBSoft.IndustrialCtrls.Leds.LBLed.LedState.Off)
            {
                MainForm.Log("Starting server for CLEMSite clients.");
                this.StartButton.ButtonColor = System.Drawing.Color.LightGreen;
                lbLed1.State = LBSoft.IndustrialCtrls.Leds.LBLed.LedState.On;
                lbLedStatus.State = LBSoft.IndustrialCtrls.Leds.LBLed.LedState.On;
                MainForm.Log("CURRENT SETTINGS: Check that you agree with these settings.\n If not, click on Start again to stop the services, change the .pref file (use a text editor and save) and click on Start button again." + System.Environment.NewLine);
                MainForm.Log(Settings.asString(), false);
                if (backgroundWorker1.IsBusy == false)
                {
                    backgroundWorker1.RunWorkerAsync(null);
                }
                MainForm.Log("Server is listening.");
            }
            else
            {
                lbLed1.State = LBSoft.IndustrialCtrls.Leds.LBLed.LedState.Off;
                this.StartButton.ButtonColor = System.Drawing.Color.IndianRed;
                this.Refresh();
                this.backgroundWorker1.CancelAsync();
                this.mylistener.StopListening();
                JObject arguments = new JObject();
                this.mylistener.myMessageParser.manage("disconnect", arguments);
                MainForm.Log("All connections closed.");
            }
        }


        private void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
        {
            this.mylistener.StartListening();
            while (!this.backgroundWorker1.CancellationPending)
            {
                this.mylistener.Listen(); // We could return values and feed them to Progress Changed
            }

            e.Cancel = true;


        }

        private void PortTextBox_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (PortTextBox.Text != AsynchronousSocketListener.port.ToString())
            {
                AsynchronousSocketListener.port = (short) int.Parse(PortTextBox.Text);
            }
        }

        private void comboBoxIP_SelectedIndexChanged(object sender, EventArgs e)
        {
            AsynchronousSocketListener.ipAddress =
                (System.Net.IPAddress.Parse(this.comboBoxIP.SelectedItem.ToString()));
        }

        public static void Log(string logMessage, bool dateIn = true)
        {

                string m_timeStamp = "";
                if (dateIn)
                {
                    m_timeStamp = DateTime.Now.ToLongTimeString();
                    logMessage = "_ " + m_timeStamp + "--" + logMessage + System.Environment.NewLine;
                }
                if (MainForm.textBoxMessages.InvokeRequired)
                {
                    var d = new SafeCallDelegate(Log);
                    MainForm.textBoxMessages.Invoke(d, new object[] { logMessage, false });
                }
                else
                {
                lock (UILock)
                {
                    MainForm.textBoxMessages.AppendText(logMessage);
                    if ((MainForm.textBoxMessages.TextLength) > 65536)
                    {
                        MainForm.textBoxMessages.Clear();
                        Console.WriteLine("TextBox Message Buffer cleaned.");
                    }
                    Console.Write("\r Entry : ");
                    Console.WriteLine("{0} {1}", DateTime.Now.ToLongTimeString(),
                        DateTime.Now.ToLongDateString());
                    Console.WriteLine("  :{0}", logMessage);
                    Console.WriteLine("-------------------------------");
                }
            }
        }


        private bool hasWriteAccessToFolder(string folderPath)
        {
            try
            {
                // Attempt to get a list of security permissions from the folder. 
                // This will raise an exception if the path is read only or do not have access to view the permissions. 
                System.Security.AccessControl.DirectorySecurity ds = Directory.GetAccessControl(folderPath);
                return true;
            }
            catch (UnauthorizedAccessException)
            {
                return false;
            }
            catch (System.IO.DirectoryNotFoundExpection)
            {
                return false;
            }
        }

        private void button_UI_Click(object sender, EventArgs e)
        {
            if (this.StartButton.ButtonColor == System.Drawing.Color.LightGreen)
            {
                JObject arguments = new JObject();
                mylistener.myMessageParser.manage("showUI", arguments);
            }
            else
            {
                Log("Start the Server (push button Start). Then a client has to connect to initialize ATLAS.\n");
            }
        }

        internal static void setStatusConnected(bool v)
        {
            if (v)
            {
                lbLed1.LedColor = System.Drawing.Color.Lime;

            }
            else
            {

                lbLed1.LedColor = System.Drawing.Color.Red;
            }
        }

        internal static void setStatusError(bool v)
        {
            if (v)
            {
                lbLed2.LedColor = System.Drawing.Color.Red;

            }
            else
            {

                lbLed2.LedColor = System.Drawing.Color.Gray;
            }
        }


        internal static void setStatusSaved(bool v)
        {
            if (v)
            {
                lbLedStatus.LedColor = System.Drawing.Color.Lime;

            }
            else
            {

                lbLedStatus.LedColor = System.Drawing.Color.Red;
            }
        }


        private void setUserPreferencesFromMSiteToolStripMenuItem_Click(object sender, EventArgs e)
        {
            // Display the openFile dialog.
            DialogResult result = openFileDialogPreferences.ShowDialog();

            // OK button was pressed.
            if (result == DialogResult.OK)
            {
                string user_preferences = openFileDialogPreferences.FileName;
                string user_pref_local_copy = ".\\automaton\\fromMSite\\" + Path.GetFileName(user_preferences);
                if (!File.Exists(user_pref_local_copy))
                {
                    File.Copy(user_preferences, user_pref_local_copy);
                }
                else
                {
                    File.Delete(user_pref_local_copy);
                    File.Copy(user_preferences, user_pref_local_copy);
                }
                Settings.Update();
                MainForm.Log("Settings updated");
                MainForm.Log(Settings.asString(), false);
            }
        }

        private void MainForm_Load(object sender, EventArgs e)
        {

        }
    }

}
