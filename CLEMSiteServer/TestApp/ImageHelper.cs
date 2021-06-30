using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Threading;


// using Emgu.CV;
// using Emgu.CV.Structure;


using System.Drawing;
using System.Text.RegularExpressions;
using System.Globalization;
using System.Data;
using Microsoft.VisualBasic.FileIO;

namespace msite
{
	class ImageHelper
	{
		private static string  automaton_folder = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location) + "\\automaton";
		private static string python_folder = "python.exe";
	 
		public static List<int> listTracked;

		private static float offset = -0.25f;


		public ImageHelper()
		{
			python_folder = Settings.getSetting("python_folder");
			string auto_folder = Settings.getSetting("automaton_folder");
			if (!auto_folder.Contains("default"))
			{
				automaton_folder = auto_folder;
			}
		}

		public bool getCenterSquare(string tag, string image_SEM_before, string image_SEM_after, string img_folder, out double center_x, out double center_y, float pixelsize)
		{

			// Prepare the process to run
			ProcessStartInfo start = new ProcessStartInfo();
			// Enter in the command line arguments, everything you would enter after the executable name itself
			string arguments = automaton_folder + "\\findCentroidSquare.py";
			arguments = arguments + " " + image_SEM_before + " " + image_SEM_after + " " + tag;
			string ExeName = python_folder;
			start.Arguments = arguments;
			// Enter the executable to run, including the complete path
			start.FileName = ExeName;
			// Do you want to show a console window?
			start.WindowStyle = ProcessWindowStyle.Hidden;
			start.CreateNoWindow = true;
			// int exitCode;
			System.Console.WriteLine("Executing GetCenterSquare :" + ExeName + " " + arguments);
			// Run the external process & wait for it to finish
			Process proc = Process.Start(start);
			{
				proc.WaitForExit();
				// Retrieve the app's exit code
				//  exitCode = proc.ExitCode;
			}
			System.Console.WriteLine("Centroid of square found "+proc.ExitCode);
			//Regex reg = new Regex(@"data_square_"+tag);
			//var files = Directory.GetFiles(img_folder, "*.csv").Where(path => reg.IsMatch(path));
			center_x = 0;
			center_y = 0;
			try
			{
				var reader = new StreamReader(File.OpenRead(img_folder + "\\data_square_" + tag + ".csv"));
				center_x = 0.0f;
				center_y = 0.0f;
				while (!reader.EndOfStream)
				{
					var line = reader.ReadLine();
					var values = line.Split(';');
					if (values.Count() > 0)
					{
						center_x = float.Parse(values[0], CultureInfo.InvariantCulture) * pixelsize; // multiply by pixelsize
						center_y = -float.Parse(values[1], CultureInfo.InvariantCulture) * pixelsize; // Coordinates from image are inverted
					}
				}
				reader.Close();
			}
			catch (System.IO.FileNotFoundException e)
			{
				Console.WriteLine(e.ToString());
				return false;
			}




			return true;
		}
	  
		public bool getCenterSquare2(string tag, string image, string img_folder, out double center_x, out double center_y, float pixelsize)
		{

			// Close everything
			center_x = 0;
			center_y = 0;
			/* this.Disconnect(ref error);
			foreach (var process in Process.GetProcessesByName("Atlas Engine"))
			{
				process.Kill();
			} */
			// Prepare the process to run
			ProcessStartInfo start = new ProcessStartInfo();
			// Enter in the command line arguments, everything you would enter after the executable name itself
			string arguments = automaton_folder +"\\findCentroidSquare2.py";
			arguments = arguments + " " + image + " " + tag;
			string ExeName = python_folder;
			start.Arguments = arguments;
			// Enter the executable to run, including the complete path
			start.FileName = ExeName;
			// Do you want to show a console window?
			start.WindowStyle = ProcessWindowStyle.Hidden;
			start.CreateNoWindow = true;
			// int exitCode;


			// Run the external process & wait for it to finish
			Process proc = Process.Start(start);
			{
				proc.WaitForExit();
				// Retrieve the app's exit code
				//  exitCode = proc.ExitCode;
			}

			//Regex reg = new Regex(@"data_square_"+tag);
			//var files = Directory.GetFiles(img_folder, "*.csv").Where(path => reg.IsMatch(path));
			try
			{
				var reader = new StreamReader(File.OpenRead(img_folder + "\\data_square_" + tag + ".csv"));
				center_x = 0.0f;
				center_y = 0.0f;
				while (!reader.EndOfStream)
				{
					var line = reader.ReadLine();
					var values = line.Split(';');
					if (values.Count() > 0)
					{
						center_x = float.Parse(values[0], CultureInfo.InvariantCulture) * pixelsize; // multiply by pixelsize
						center_y = -float.Parse(values[1], CultureInfo.InvariantCulture) * pixelsize; // Coordinates from image are inverted 
					}
				}
				reader.Close();
			}
			catch (System.IO.FileNotFoundException e)
			{
				Console.WriteLine(e.ToString());
				return false;
			}


			return true;
		}

		public bool DetectTrench(string image_path_before,string image_path,string tag, ref Dictionary<string,System.Drawing.Point> trenchPoints)
		{

			// Close everything
			/* this.Disconnect(ref error);
			foreach (var process in Process.GetProcessesByName("Atlas Engine"))
			{
				process.Kill();
			} */
			// Prepare the process to run
			ProcessStartInfo start = new ProcessStartInfo();
			// Enter in the command line arguments, everything you would enter after the executable name itself
			string arguments = automaton_folder+"\\ESB_findTrench.py";
			arguments = arguments + " " + image_path_before+" "+image_path + " " + tag;
			string ExeName = python_folder;
			start.Arguments = arguments;
			// Enter the executable to run, including the complete path
			start.FileName = ExeName;
			// Do you want to show a console window?
			start.WindowStyle = ProcessWindowStyle.Hidden;
			start.CreateNoWindow = true;
			// int exitCode;

			// Run the external process & wait for it to finish
			Process proc = Process.Start(start);
			{
				proc.WaitForExit();
			}
			string img_folder = Path.GetDirectoryName(image_path);
			Regex reg = new Regex(@"data_trench_" +tag+".csv");
			// Regex reg2 = new Regex(@"failure_"+tag);
			string[] files = Directory.GetFiles(img_folder).Where(path => reg.IsMatch(path)).ToArray();        
			if (files.Length==0)
			{
				 return false;
			}
			bool exist = Directory.EnumerateFiles(img_folder, "failed*").Any();
			if (exist)
			{
				return false;
			}
			try
			{
				var reader = new StreamReader(File.OpenRead(img_folder + "\\data_trench_" + tag + ".csv"));
				while (!reader.EndOfStream)
				{
					var line = reader.ReadLine();
					var values = line.Split(';');
					if (values.Count() > 0)
					{
						var value1 = 0;
						int.TryParse(values[1], out value1);
						var value2 = 0;
						int.TryParse(values[2], out value2);
						trenchPoints.Add(values[0],new Point(value1,-value2));
					}
				}
				reader.Close();
			}
			catch (System.IO.FileNotFoundException e)
			{
				Console.WriteLine(e.ToString());
				return false;
			}
			return true;
		}

		public bool DetectFocusPoints(string image_path, string tag, ref List<System.Drawing.Point> hotPoints)
		{

			// Close everything
			/* this.Disconnect(ref error);
			foreach (var process in Process.GetProcessesByName("Atlas Engine"))
			{
				process.Kill();
			} */
			// Prepare the process to run
			ProcessStartInfo start = new ProcessStartInfo();
			// Enter in the command line arguments, everything you would enter after the executable name itself
			string arguments = automaton_folder +"\\detectFocusPoints.py";
			arguments = arguments + " " + image_path + " " + tag;
			string ExeName = python_folder;
			start.Arguments = arguments;
			// Enter the executable to run, including the complete path
			start.FileName = ExeName;
			// Do you want to show a console window?
			start.WindowStyle = ProcessWindowStyle.Hidden;
			start.CreateNoWindow = true;
			// int exitCode;

			// Run the external process & wait for it to finish
			Process proc = Process.Start(start);
			{
				proc.WaitForExit();
			}
			string img_folder = Path.GetDirectoryName(image_path);
			Regex reg = new Regex(tag + ".csv");
			// Regex reg2 = new Regex(@"failure_"+tag);
			string[] files = Directory.GetFiles(img_folder).Where(path => reg.IsMatch(path)).ToArray();
			if (files.Length==0)
			{
				return false;
			}
			try
			{
				var reader = new StreamReader(File.OpenRead(img_folder + "\\"+tag + ".csv"));
				while (!reader.EndOfStream)
				{
					var line = reader.ReadLine();
					var values = line.Split(';');
					if (values.Count() > 0)
					{
						hotPoints.Add(new System.Drawing.Point(int.Parse(values[1], CultureInfo.InvariantCulture), -int.Parse(values[2], CultureInfo.InvariantCulture))); // multiply by pixelsize
					}
				}
				reader.Close();
			}
			catch (System.IO.FileNotFoundException e)
			{
				Console.WriteLine(e.ToString());
				return false;
			}

			return true;
		}

		public bool runChecker(string tag, string filename,long AFperiod, ref System.Drawing.PointF af_point,ref bool trackOrNot,ref bool AboxOrNot, ref System.Drawing.PointF trackingOffset,ref int iremslices, ref bool cancel)
		{
			/**
			 * In a broad range this is the algorithm
			 * When Image is produced:
					Find interface line (SLICthresholding)
					Find relative shift (using SIFT features) between images 
					Get time from incoming autofocus 
					
					If relative shift > threshold
						Compensate in X,Y in the desired direction
					
					If for two consecutive images margins are off
							Compensate in Y direction with +/-0.5 µm
					
					If Autofocus incoming in the next section:
						Compute Autofocus points candidates
						Move box to one of the candidate points	
			 * 
			 * 
			 * */
			List<double> newValues = new List<double>();
			// Prepare the process to run
			ProcessStartInfo start = new ProcessStartInfo();
			// Enter in the command line arguments, everything you would enter after the executable name itself
			string arguments = automaton_folder +"\\Reporter.py";
			arguments = arguments + " " + filename + " " + tag; // + im_an_enabled
			string ExeName = python_folder;
			start.Arguments = arguments;
			// Enter the executable to run, including the complete path
			start.FileName = ExeName;
			// Do you want to show a console window?
			start.WindowStyle = ProcessWindowStyle.Hidden;
			start.CreateNoWindow = true;
			iremslices = 0;

			// Run the external process & wait for it to finish
			Process proc = Process.Start(start);
			{
				proc.WaitForExit();
			}

			string ifolder = Path.GetDirectoryName(filename);
			string fn = Path.GetFileNameWithoutExtension(filename);
			try
			{
				// Get Tracking values in array of the last 5 values
				DataTable checkData = GetDataTableFromCSVFile(ifolder+@"\\runcheck.csv");
				Dictionary<int, List<double>> trackValues = new Dictionary<int, List<double>>();
				if (checkData.Rows.Count > 5)
				{
					for (int i = 5; i > 1; i--)
					{
						DataRow row = checkData.Rows[checkData.Rows.Count - i];
						string valueImNo = row["ImageNo"].ToString();
						int imageval = int.Parse(valueImNo, CultureInfo.InvariantCulture);
						List<double> new_trackValues_List = new List<double>();
						string valueStop = row["stop"].ToString();
						new_trackValues_List.Add(Double.Parse(valueStop, CultureInfo.InvariantCulture));
						string valueSX = row["shift_x"].ToString();
						new_trackValues_List.Add(Double.Parse(valueSX, CultureInfo.InvariantCulture));
						string valueSY = row["shift_y"].ToString();
						new_trackValues_List.Add(Double.Parse(valueSY, CultureInfo.InvariantCulture));
						trackValues.Add(imageval, new_trackValues_List);
					}
					DataRow lastRow = checkData.Rows[checkData.Rows.Count - 1];
					string remSlices = lastRow["s_to_AF"].ToString();
					iremslices = (int)(Double.Parse(remSlices, CultureInfo.InvariantCulture));

					// Do we need tracking??
					trackOrNot = this.trackEvaluation(trackValues, ref trackingOffset);

					// If we are going to track, all elements already tracked go into the list
					if (trackOrNot)
					{
						foreach (DataRow row in checkData.Rows)
						{
							string valueImNo = row["ImageNo"].ToString();
							int isdone = int.Parse(valueImNo, CultureInfo.InvariantCulture);
							if (!ImageHelper.listTracked.Contains(isdone))
							{
								ImageHelper.listTracked.Add(isdone);
							}
						}
					}
				}

				/////////////////// Second part, focus points ///////////////////
				//// Get the last file with focus points
				fn = this.getFileStartingBy(ifolder, "fp_");
				var reader = new StreamReader(File.OpenRead(fn));
				while (!reader.EndOfStream)
				{
					var line = reader.ReadLine();
					var values = line.Split(';').ToArray();
					if (values.Count() > 0)
					{
						newValues.Add(Double.Parse(values[1], CultureInfo.InvariantCulture));
						newValues.Add(-Double.Parse(values[2], CultureInfo.InvariantCulture));
					}
				}
				reader.Close();
				// For each value, check if it is reasonable, and return the first, otherwise return false
				// our estimation is that the point cannot be more than 10 um away from the center.
			   
				af_point.X = (float)newValues[0];
				af_point.Y = (float)newValues[1]+offset;
				if (Math.Abs(af_point.X) > 10 || Math.Abs(af_point.Y) > 10)
				{
					af_point.X = (float)newValues[2];
					af_point.Y = (float)newValues[3];
					if (Math.Abs(af_point.X) > 10 || Math.Abs(af_point.Y) > 10)
					{
						AboxOrNot = false;
					}
					AboxOrNot = true;
				}
				else
				{
					AboxOrNot = true;
				}              
			}
			catch (System.IO.FileNotFoundException)
			{
				Console.WriteLine("File runcheck.csv Not found. Cancelling Automaton actions.");
				return true;  
			}
			catch (System.IO.DirectoryNotFoundException)
			{
				return false;
			}
			return true;
		}

		public string getFileStartingBy(string path_to_search,string reg_exp )
		{
			Regex reg = new Regex(@reg_exp+".*$");
			var files = Directory.GetFiles(path_to_search, "*.csv").Where(fn => reg.IsMatch(fn)).ToArray();
			if (files.Length > 0)
			{
				return files[0];
			}
			else {

				throw new System.IO.FileNotFoundException();
			}

		}


		private bool trackEvaluation(Dictionary<int,List<double>> trackValues, ref PointF Offset)
		{
			/** 
			 * Tracking is done in two independent ways. 
			* First evaluation is by SIFT features. If SIFT is disabled, then the corresponding shifts 
			* are 0.
			* The second evaluation is by STOP point. We evaluate from top until ROI how much offset exist
			* If the offset is too big we proceed to move, i.e., if the stop point is 0 we have to add some margin
			* and if the stop point is bigger of 1.5 um, we have to rectify it to be 1.5 or less.
			* 

			 */
			// Get last two values
			if (trackValues.Count < 2)
			{
				return false;
			}
			List<int> list_values = new List<int>(trackValues.Keys);

			// First of all get all two shifts
			int last_ind = list_values.Last();
			var lastValues = trackValues[last_ind];
			
			// WE forbid shifts bigger than 8 um in any of the directions
			if (Math.Abs(lastValues[1]) < 10 && Math.Abs(lastValues[2]) < 10)
			{
				Offset.X = (float) lastValues[1];
				Offset.Y = (float) lastValues[2];
				return true;
			}

			return false;
		}

		private static DataTable GetDataTableFromCSVFile(string csv_file_path)
		{
			DataTable csvData = new DataTable();
			try
			{
				using(TextFieldParser csvReader = new TextFieldParser(csv_file_path))
				{
					csvReader.SetDelimiters(new string[] { "," });
					csvReader.HasFieldsEnclosedInQuotes = true;
					string[] colFields = csvReader.ReadFields();

			foreach (string column in colFields)
			{
				DataColumn datecolumn = new DataColumn(column);
				datecolumn.AllowDBNull = true;
				csvData.Columns.Add(datecolumn);
			}
			while (!csvReader.EndOfData)
			{
				string[] fieldData = csvReader.ReadFields();
				//Making empty value as null
				for (int i = 0; i < fieldData.Length; i++)
				{
					if (fieldData[i] == "")
					{
						fieldData[i] = null;
					}
				}
				csvData.Rows.Add(fieldData);
			 }  
			}
			}catch (Exception){}
			return csvData;
}


	}
}
