/*
*/

using System.Windows.Forms;

namespace msite
{
    partial class MainForm
    {
        /// <summary>
        /// Designer variable used to keep track of non-visual components.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Disposes resources used by the form.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                if (components != null)
                {
                    components.Dispose();
                }
            }

            writer.Close();
            outputStream.Close();
            System.Diagnostics.Trace.WriteLine(
               "Form1.Dispose " + (disposing ? "disposing " : "")
               + this.GetHashCode().ToString());
            base.Dispose(disposing);
        }

        /// <summary>
        /// This method is required for Windows Forms designer support.
        /// Do not change the method contents inside the source code editor. The Forms designer might
        /// not be able to load this method if it was changed manually.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.button_UI = new System.Windows.Forms.Button();
            this.comboBoxIP = new System.Windows.Forms.ComboBox();
            this.label2 = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.PortTextBox = new System.Windows.Forms.MaskedTextBox();
            lbLed2 = new LBSoft.IndustrialCtrls.Leds.LBLed();
            this.StartButton = new LBSoft.IndustrialCtrls.Buttons.LBButton();
            lbLed1 = new LBSoft.IndustrialCtrls.Leds.LBLed();
            this.backgroundWorker1 = new System.ComponentModel.BackgroundWorker();
            this.pictureBox1 = new System.Windows.Forms.PictureBox();
            this.folderBrowserDialog1 = new System.Windows.Forms.FolderBrowserDialog();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.optionsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.setUserPreferencesFromMSiteToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            textBoxMessages = new System.Windows.Forms.TextBox();
            lbLedStatus = new LBSoft.IndustrialCtrls.Leds.LBLed();
            this.groupBox2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).BeginInit();
            this.menuStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // groupBox2
            // 
            this.groupBox2.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.groupBox2.BackColor = System.Drawing.Color.Transparent;
            this.groupBox2.Controls.Add(lbLedStatus);
            this.groupBox2.Controls.Add(this.button_UI);
            this.groupBox2.Controls.Add(this.comboBoxIP);
            this.groupBox2.Controls.Add(this.label2);
            this.groupBox2.Controls.Add(this.label1);
            this.groupBox2.Controls.Add(this.PortTextBox);
            this.groupBox2.Controls.Add(lbLed2);
            this.groupBox2.Controls.Add(this.StartButton);
            this.groupBox2.Controls.Add(lbLed1);
            this.groupBox2.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.groupBox2.Location = new System.Drawing.Point(32, 37);
            this.groupBox2.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Padding = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.groupBox2.Size = new System.Drawing.Size(941, 182);
            this.groupBox2.TabIndex = 7;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "Server connection";
            // 
            // button_UI
            // 
            this.button_UI.BackColor = System.Drawing.Color.LightSteelBlue;
            this.button_UI.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.button_UI.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.button_UI.Location = new System.Drawing.Point(651, 112);
            this.button_UI.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.button_UI.Name = "button_UI";
            this.button_UI.Size = new System.Drawing.Size(265, 57);
            this.button_UI.TabIndex = 39;
            this.button_UI.Text = "Show ATLAS Engine UI";
            this.button_UI.UseVisualStyleBackColor = false;
            this.button_UI.Click += new System.EventHandler(this.button_UI_Click);
            // 
            // comboBoxIP
            // 
            this.comboBoxIP.BackColor = System.Drawing.SystemColors.InactiveBorder;
            this.comboBoxIP.FormattingEnabled = true;
            this.comboBoxIP.Location = new System.Drawing.Point(228, 51);
            this.comboBoxIP.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.comboBoxIP.Name = "comboBoxIP";
            this.comboBoxIP.Size = new System.Drawing.Size(181, 36);
            this.comboBoxIP.TabIndex = 7;
            this.comboBoxIP.SelectedIndexChanged += new System.EventHandler(this.comboBoxIP_SelectedIndexChanged);
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label2.Location = new System.Drawing.Point(159, 54);
            this.label2.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(41, 28);
            this.label2.TabIndex = 6;
            this.label2.Text = "IP :";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.Location = new System.Drawing.Point(159, 114);
            this.label1.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(57, 28);
            this.label1.TabIndex = 5;
            this.label1.Text = "Port:";
            // 
            // PortTextBox
            // 
            this.PortTextBox.Location = new System.Drawing.Point(228, 111);
            this.PortTextBox.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.PortTextBox.Mask = "00000";
            this.PortTextBox.Name = "PortTextBox";
            this.PortTextBox.Size = new System.Drawing.Size(92, 34);
            this.PortTextBox.TabIndex = 4;
            this.PortTextBox.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.PortTextBox_KeyPress);
            // 
            // lbLed2
            // 
            lbLed2.BackColor = System.Drawing.Color.Transparent;
            lbLed2.BlinkInterval = 500;
            lbLed2.Font = new System.Drawing.Font("Verdana", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            lbLed2.ForeColor = System.Drawing.Color.Black;
            lbLed2.Label = "Error";
            lbLed2.LabelPosition = LBSoft.IndustrialCtrls.Leds.LBLed.LedLabelPosition.Bottom;
            lbLed2.LedColor = System.Drawing.Color.Red;
            lbLed2.LedSize = new System.Drawing.SizeF(20F, 20F);
            lbLed2.Location = new System.Drawing.Point(797, 50);
            lbLed2.Margin = new System.Windows.Forms.Padding(9, 6, 9, 6);
            lbLed2.Name = "lbLed2";
            lbLed2.Renderer = null;
            lbLed2.Size = new System.Drawing.Size(137, 48);
            lbLed2.State = LBSoft.IndustrialCtrls.Leds.LBLed.LedState.Off;
            lbLed2.Style = LBSoft.IndustrialCtrls.Leds.LBLed.LedStyle.Circular;
            lbLed2.TabIndex = 2;
            // 
            // StartButton
            // 
            this.StartButton.BackColor = System.Drawing.Color.SlateGray;
            this.StartButton.ButtonColor = System.Drawing.Color.CornflowerBlue;
            this.StartButton.Font = new System.Drawing.Font("Segoe UI", 39.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.StartButton.ForeColor = System.Drawing.SystemColors.ControlText;
            this.StartButton.Label = "Start";
            this.StartButton.Location = new System.Drawing.Point(36, 54);
            this.StartButton.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.StartButton.Name = "StartButton";
            this.StartButton.Renderer = null;
            this.StartButton.RepeatInterval = 100;
            this.StartButton.RepeatState = false;
            this.StartButton.Size = new System.Drawing.Size(97, 86);
            this.StartButton.StartRepeatInterval = 500;
            this.StartButton.State = LBSoft.IndustrialCtrls.Buttons.LBButton.ButtonState.Normal;
            this.StartButton.Style = LBSoft.IndustrialCtrls.Buttons.LBButton.ButtonStyle.Rectangular;
            this.StartButton.TabIndex = 1;
            this.StartButton.Click += new System.EventHandler(this.StartButton_Click);
            // 
            // lbLed1
            // 
            lbLed1.BackColor = System.Drawing.Color.Transparent;
            lbLed1.BlinkInterval = 500;
            lbLed1.Font = new System.Drawing.Font("Verdana", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            lbLed1.ForeColor = System.Drawing.Color.Black;
            lbLed1.Label = "Connected";
            lbLed1.LabelPosition = LBSoft.IndustrialCtrls.Leds.LBLed.LedLabelPosition.Bottom;
            lbLed1.LedColor = System.Drawing.Color.Red;
            lbLed1.LedSize = new System.Drawing.SizeF(20F, 20F);
            lbLed1.Location = new System.Drawing.Point(487, 50);
            lbLed1.Margin = new System.Windows.Forms.Padding(9, 6, 9, 6);
            lbLed1.Name = "lbLed1";
            lbLed1.Renderer = null;
            lbLed1.Size = new System.Drawing.Size(137, 48);
            lbLed1.State = LBSoft.IndustrialCtrls.Leds.LBLed.LedState.Off;
            lbLed1.Style = LBSoft.IndustrialCtrls.Leds.LBLed.LedStyle.Circular;
            lbLed1.TabIndex = 0;
            // 
            // backgroundWorker1
            // 
            this.backgroundWorker1.DoWork += new System.ComponentModel.DoWorkEventHandler(this.backgroundWorker1_DoWork);
            // 
            // pictureBox1
            // 
            this.pictureBox1.Image = ((System.Drawing.Image)(resources.GetObject("pictureBox1.Image")));
            this.pictureBox1.Location = new System.Drawing.Point(32, 590);
            this.pictureBox1.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.pictureBox1.Name = "pictureBox1";
            this.pictureBox1.Size = new System.Drawing.Size(144, 57);
            this.pictureBox1.TabIndex = 23;
            this.pictureBox1.TabStop = false;
            // 
            // menuStrip1
            // 
            this.menuStrip1.ImageScalingSize = new System.Drawing.Size(20, 20);
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.optionsToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Padding = new System.Windows.Forms.Padding(8, 2, 0, 2);
            this.menuStrip1.Size = new System.Drawing.Size(989, 28);
            this.menuStrip1.TabIndex = 40;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // optionsToolStripMenuItem
            // 
            this.optionsToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.setUserPreferencesFromMSiteToolStripMenuItem});
            this.optionsToolStripMenuItem.Name = "optionsToolStripMenuItem";
            this.optionsToolStripMenuItem.Size = new System.Drawing.Size(73, 24);
            this.optionsToolStripMenuItem.Text = "Options";
            // 
            // setUserPreferencesFromMSiteToolStripMenuItem
            // 
            this.setUserPreferencesFromMSiteToolStripMenuItem.Name = "setUserPreferencesFromMSiteToolStripMenuItem";
            this.setUserPreferencesFromMSiteToolStripMenuItem.Size = new System.Drawing.Size(304, 26);
            this.setUserPreferencesFromMSiteToolStripMenuItem.Text = "Set user preferences from MSite...";
            this.setUserPreferencesFromMSiteToolStripMenuItem.Click += new System.EventHandler(this.setUserPreferencesFromMSiteToolStripMenuItem_Click);
            // 
            // textBoxMessages
            // 
            textBoxMessages.Location = new System.Drawing.Point(32, 226);
            textBoxMessages.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            textBoxMessages.Multiline = true;
            textBoxMessages.Name = "textBoxMessages";
            textBoxMessages.ReadOnly = true;
            textBoxMessages.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            textBoxMessages.Size = new System.Drawing.Size(940, 355);
            textBoxMessages.TabIndex = 41;
            // 
            // lbLedStatus
            // 
            lbLedStatus.BackColor = System.Drawing.Color.Transparent;
            lbLedStatus.BlinkInterval = 500;
            lbLedStatus.Font = new System.Drawing.Font("Verdana", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            lbLedStatus.ForeColor = System.Drawing.Color.Black;
            lbLedStatus.Label = "Status saved";
            lbLedStatus.LabelPosition = LBSoft.IndustrialCtrls.Leds.LBLed.LedLabelPosition.Bottom;
            lbLedStatus.LedColor = System.Drawing.Color.Red;
            lbLedStatus.LedSize = new System.Drawing.SizeF(20F, 20F);
            lbLedStatus.Location = new System.Drawing.Point(642, 50);
            lbLedStatus.Margin = new System.Windows.Forms.Padding(9, 6, 9, 6);
            lbLedStatus.Name = "lbLedStatus";
            lbLedStatus.Renderer = null;
            lbLedStatus.Size = new System.Drawing.Size(137, 48);
            lbLedStatus.State = LBSoft.IndustrialCtrls.Leds.LBLed.LedState.Off;
            lbLedStatus.Style = LBSoft.IndustrialCtrls.Leds.LBLed.LedStyle.Circular;
            lbLedStatus.TabIndex = 40;
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.AutoSize = true;
            this.BackColor = System.Drawing.Color.SlateGray;
            this.ClientSize = new System.Drawing.Size(989, 661);
            this.Controls.Add(textBoxMessages);
            this.Controls.Add(this.pictureBox1);
            this.Controls.Add(this.groupBox2);
            this.Controls.Add(this.menuStrip1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MainMenuStrip = this.menuStrip1;
            this.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.MaximizeBox = false;
            this.Name = "MainForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "CLEMSite Server Beta";
            this.Load += new System.EventHandler(this.MainForm_Load);
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).EndInit();
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }
        private LBSoft.IndustrialCtrls.Buttons.LBButton StartButton;
        private System.Windows.Forms.GroupBox groupBox2;
        private PictureBox pictureBox1;
        private System.ComponentModel.BackgroundWorker backgroundWorker1;
        private Label label2;
        private Label label1;
        private MaskedTextBox PortTextBox;
        private ComboBox comboBoxIP;
        private FolderBrowserDialog folderBrowserDialog1;
        private OpenFileDialog openFileDialog;
        private OpenFileDialog openFileDialogPreferences;
        private Button button_UI;
        private MenuStrip menuStrip1;
        private ToolStripMenuItem optionsToolStripMenuItem;
        private ToolStripMenuItem setUserPreferencesFromMSiteToolStripMenuItem;
        private static LBSoft.IndustrialCtrls.Leds.LBLed lbLedStatus;
        private static LBSoft.IndustrialCtrls.Leds.LBLed lbLed1;
        private static LBSoft.IndustrialCtrls.Leds.LBLed lbLed2;
        public static TextBox textBoxMessages;
    }
}
