using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Xml.XPath;
using System.Xml;
using System.Globalization;

namespace msite
{

    public class XMLManager
    {
        XmlDocument doc;
        
        string current_xmlfile = "";
        public XMLManager()
        {
        }

        public bool setXMLFile(string filename, ref string error)
        {
            this.doc  = new XmlDocument();
            // Create an XML reader for this file.
            try
            {
                doc.RemoveAll();
                doc.PreserveWhitespace = true;
                doc.Load(filename);
                error = "";
            }
            catch (System.Xml.XmlException e)
            {
                error = e.ToString();
                return false;
            }
            current_xmlfile = filename;
            System.Globalization.CultureInfo customCulture = (System.Globalization.CultureInfo)System.Threading.Thread.CurrentThread.CurrentCulture.Clone();
            customCulture.NumberFormat.NumberDecimalSeparator = ".";
            System.Threading.Thread.CurrentThread.CurrentCulture = customCulture;
            return true;
        }
        public bool commit()
        {
            try
            {
                // Avoid self closing tags, just in case
                foreach (XmlElement el in doc.SelectNodes("descendant::*[not(*) and not(normalize-space())]"))
                {
                    el.IsEmpty = false;
                }

                doc.Save(this.current_xmlfile);
                return true;
            }
            catch (System.Xml.XmlException)
            {
                return false;

            }
        }

        /*** IMAGING **/

        public bool getImagingDetector(out string detector)
        {

            XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/Detector");
            if (node == null)
            {
                detector = "";
                return false;
            }
            detector = node.InnerText;
            return true;
        }

        public bool getImagingDetectorB(out string detector)
        {

            XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/Detector");
            if (node == null)
            {
                detector = "";
                return false;
            }
            detector = node.InnerText;
            return true;
        }

        public bool setInitialFocus(double focus)
        {
            if (focus < 4000.0 || focus > 7000.0)
            {
                return false;
            }

            try
            {
                string path = "/ATLAS3D-Setup/Settings/Imaging";
                XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/InitialFocusUM");
                if (node == null)
                {
                    node = doc.SelectSingleNode(path);
                    XmlElement elem = this.doc.CreateElement("InitialFocusUM");
                    elem.InnerText = focus.ToString();
                }
                else
                {
                    node.InnerText = focus.ToString();
                }
                  return true;
            
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

        }

        public bool setImagingOptions(double FOV, long Width, long Height)
        {

            

            try
            {
                string path = "/ATLAS3D-Setup/Settings/Imaging";
                XmlNode node1 = doc.SelectSingleNode(path + "/FOV");
                XmlNode node2 = doc.SelectSingleNode(path + "/FibicsRasterInfo/Width");
                XmlNode node3 = doc.SelectSingleNode(path + "/FibicsRasterInfo/Height");

                if (node1 == null || node2 == null || node3 == null)
                {
                    return false;
                }

                if(FOV>0)
                    node1.InnerText = FOV.ToString();
                if (Width > 0)
                    node2.InnerText = Width.ToString();
                if(Height > 0)
                    node3.InnerText = Height.ToString();

            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;



        }

        public bool getImagingBC(string detector_type, out double brightness, out double contrast)
        {

            brightness = 0.0f; ;
            contrast = 0.0f;
            XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/Detector");
            if (node == null)
            {
                return false;
            }
            string which_detector = node.InnerText;
            string line_B = "Brightness";
            string line_C = "Contrast";
            if (which_detector.CompareTo(detector_type) != 0)
            {
                node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/DetectorB");
                if (node == null)
                {
                    return false;
                }
                which_detector = node.InnerText;
                if (which_detector.CompareTo(detector_type) == 0)
                {
                    line_B = "BrightnessB";
                    line_C = "ContrastB";
                }
                else
                {

                    return false;
                }

            }


            string txt_b = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/" + "/" + line_B).InnerText;
            string txt_c = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/" + "/" + line_C).InnerText;
            brightness = double.Parse(txt_b, CultureInfo.InvariantCulture);
            contrast = double.Parse(txt_c, CultureInfo.InvariantCulture);


            return true;
        }

        public bool setJobName(string jobname, string jobDescription = "")
        {

            try
            {
                XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/JobName");
                if (node == null)
                {
                    return false;
                }

                node.InnerText = jobname;
                if (jobDescription.Length > 0)
                {
                    node = doc.SelectSingleNode("/ATLAS3D-Setup/JobDescription");
                    if (node == null)
                    {
                        return false;
                    }

                    node.InnerText = jobDescription;

                }

            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;


        }

        public bool setImagingDetector(string detector_type, double brightness, double contrast)
        {
            try
            {
                XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/Detector");
                if (node == null)
                {
                    return false;
                }

                node.InnerText = detector_type;
                node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/Brightness");
                node.InnerText = brightness.ToString();
                node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/Contrast");
                node.InnerText = contrast.ToString();
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;

        }

        public bool setImagingDwellTime(double dwellTime)
        {

            try
            {
                XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/FibicsRasterInfo/Dwell");
                if (node == null)
                {
                    return false;
                }

                node.InnerText = dwellTime.ToString();
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;


        }

        public bool setImagingLineAverage(int lineAveraging)
        {
            try
            {
                XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/FibicsRasterInfo/LineAveraging");
                if (node == null)
                {
                    return false;
                }

                node.InnerText = lineAveraging.ToString();
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;



        }

        public bool setImagingPixelSize(double pixelsize)
        {

            try
            {
                XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/FibicsRasterInfo/PixelSizeX");
                if (node == null)
                {
                    return false;
                }

                node.InnerText = pixelsize.ToString();
                node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/Imaging/FibicsRasterInfo/PixelSizeY");
                node.InnerText = pixelsize.ToString();
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;




        }

        /*** KeyFrame ***/

        public bool setKeyFrameDwellTime(double dwellTime)
        {

            try
            {
                XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/KeyFrame/FibicsRasterInfo/Dwell");
                if (node == null)
                {
                    return false;
                }

                node.InnerText = dwellTime.ToString();
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;


        }

        public bool setKeyFrameLineAverage(int lineAveraging)
        {
            try
            {
                XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/KeyFrame/FibicsRasterInfo/LineAveraging");
                if (node == null)
                {
                    return false;
                }

                node.InnerText = lineAveraging.ToString();
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;



        }

        public bool checkBeamIDs(Dictionary<string, int> fib_apertures_map,ref string info)
        {
            XmlNodeList listnodes = doc.SelectNodes("/ATLAS3D-Setup/SamplePreparation/ATLAS3DSamplePrepShapes/PrepShapes/FIBShape/Mill/BeamID");
            XmlNodeList listnames = doc.SelectNodes("/ATLAS3D-Setup/SamplePreparation/ATLAS3DSamplePrepShapes/PrepShapes/FIBShape/ShapeName");

            info = "Adding information from Beam ID's in shapes";
            if (listnodes == null)
            {
                return false;
            }
            List<int> arrIDs = new List<int>(fib_apertures_map.Values);
            int i = 0;
            foreach (XmlNode BeamID in listnodes)
            {

                int bid = int.Parse(BeamID.InnerText);
                XmlNode nname = listnames.Item(i);
                i++;
                if (arrIDs.Contains(bid))
                {
                   
                    info += "\n Checking shape: " + nname.InnerText;
                    string apertureKey = fib_apertures_map.FirstOrDefault(x => x.Value == bid).Key;
                    info += "\n BeamID of value " + bid + " corresponds to " + apertureKey;
                }
                else
                {
                    info += "\n  ERROR in Beam Identification. For shape in XML setup file : " + nname.InnerText;
                    info += "\n BeamID of value " + bid + " doesn't exist. Replace by one of the list : \n";
                    info += fib_apertures_map.Values.ToString();
                    return false;
                }
            }
            XmlNodeList listnodes2 = doc.SelectNodes("/ATLAS3D-Setup/SamplePreparation/ATLAS3DSamplePrepShapes/MillShape/FIBShape/Mill/BeamID");
            i = 0;
            foreach (XmlNode BeamID in listnodes2)
            {

                int bid = int.Parse(BeamID.InnerText);
                XmlNode nname = listnames.Item(i);
                if (arrIDs.Contains(bid))
                {               
                    info += "\n Checking shape: " + nname.InnerText;
                    string apertureKey = fib_apertures_map.FirstOrDefault(x => x.Value == bid).Key;
                    info += "\n BeamID of value " + bid + " corresponds to " + apertureKey;
                }
                else
                {
                    info += "\n  For shape : " + nname.InnerText;
                    info += "\n BeamID of value " + bid + " doesn't exist. Replace by one of the list \n";
                   
                    System.Console.WriteLine("FIB Apertures ID:Name");
                    foreach (KeyValuePair<string, int> entry in fib_apertures_map)
                    {
                        info = info+("\n Aperture #"+entry.Value+" - "+entry.Key);
                    }
                    return false;
                }
            }
            return true;
        }

        public bool setKeyFramePixelSize(double pixelsize)
        {

            try
            {
                XmlNode node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/KeyFrame/FibicsRasterInfo/PixelSizeX");
                if (node == null)
                {
                    return false;
                }

                node.InnerText = pixelsize.ToString();
                node = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/KeyFrame/FibicsRasterInfo/PixelSizeY");
                node.InnerText = pixelsize.ToString();
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;




        }


        /*** AutoTune ***/
        // Interval in MILLIseconds
        public bool setAFASInterval(long AF_Interval, long AS_Interval, bool AFafterAS)
        {

            try
            {
                XmlNode nodeAFI = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoTune/AF_Interval");
                XmlNode nodeASI = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoTune/AS_Interval");
                XmlNode nodeAFafterAS = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoTune/AFAFterAS");
                if (nodeAFI == null || nodeASI == null || nodeAFafterAS == null)
                {
                    return false;
                }

                nodeAFI.InnerText = AF_Interval.ToString();
                nodeASI.InnerText = AS_Interval.ToString();
                if (AFafterAS)
                {
                    nodeAFafterAS.InnerText = "true";
                }
                else
                {
                    nodeAFafterAS.InnerText = "false";
                }
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;

        }

        public bool getAFASInterval(out long AF_Interval,out long AS_Interval)
        {
            AF_Interval = 0;
            AS_Interval = 0;
            try
            {
                XmlNode nodeAFI = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoTune/AF_Interval");
                XmlNode nodeASI = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoTune/AS_Interval");

                if (nodeAFI == null || nodeASI == null)
                {
                    return false;
                }

                AF_Interval = long.Parse(nodeAFI.InnerText, CultureInfo.InvariantCulture);
                AS_Interval = long.Parse(nodeASI.InnerText, CultureInfo.InvariantCulture);
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;

        }


        /* Autotune FOV, PixelSize, Dwelltime, LineAvg, 
        // You specify the FOV you intend to image, and the auto-focus/auto-stig happens in a smaller area at the center of the FOV.
        // For example you might want a final image with FOV = 300 um, Pixel Size = 30nm, and therefore might specify and AFAS PixelSize = 30nm
        // This means that the AFAS will perform a coarse pass at twice the provided pixel size (i.e. PixelSize = 60nm) at a fixed 256x256 px, centered in the current FOV.
        * This is followed by a fine pass at the provided pixel size (i.e. PixelSize = 30nm) at a fixed 256x256 px, centered in the current FOV.
        */

        public bool setAutotuneImaging(double FOV, double PixelSize, double dwelltime, double lineAveraging)
        {

            try
            {
                XmlNode nodeFOV = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoTune/AutoStigAndFocus/FOV");
                XmlNode nodePixelSize = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoTune/AutoStigAndFocus/PixelSize");
                XmlNode nodeDwellTime = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoStigAndFocus/DwellTime");
                XmlNode nodeLA = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoStigAndFocus/LineAvg");
                if (nodeFOV == null || nodePixelSize == null || nodeDwellTime == null || nodeLA == null)
                {
                    return false;
                }

                nodeFOV.InnerText = FOV.ToString();
                if (PixelSize > 0)
                {
                    nodePixelSize.InnerText = PixelSize.ToString();
                }
                if (dwelltime > 0)
                {
                    nodeDwellTime.InnerText = dwelltime.ToString();
                }
                if (lineAveraging > 0)
                {
                    nodeLA.InnerText = lineAveraging.ToString();
                }
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;



        }

        // ROI Left,Right,Top,Bottom
        public bool setAutoTuneROI(double Left, double Right, double Top, double Bottom)
        {

             // <ROILeft>0.226586669683456</ROILeft>
             // <ROIRight>0.332971274852753</ROIRight>
             // <ROITop>0.205083131790161</ROITop>
             // <ROIBottom>0.0956645458936691</ROIBottom>

            try
            {
                XmlNode nodeLeft = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoTune/AutoStigAndFocus/ROILeft");
                XmlNode nodeRight = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoTune/AutoStigAndFocus/ROIRight");
                XmlNode nodeTop = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoStigAndFocus/ROITop");
                XmlNode nodeBottom = doc.SelectSingleNode("/ATLAS3D-Setup/Settings/AutoStigAndFocus/ROIBottom");
                if (nodeLeft == null || nodeRight == null || nodeTop == null || nodeBottom == null)
                {
                    return false;
                }

                nodeLeft.InnerText = Left.ToString();
                nodeRight.InnerText = Right.ToString();
                nodeTop.InnerText = Top.ToString();
                nodeBottom.InnerText = Bottom.ToString();
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;

        }
        // Detector: 0,1
        public bool setAutoTuneDetector(int signal, string Name, double B, double C)
        {
            string det_signal = "";
            if (signal == 0)
            {
                det_signal = "/ATLAS3D-Setup/Settings/AutoTune/AutoStigAndFocus/SystemDetectorSettings/Det0";
            }
            else
            {
                det_signal = "/ATLAS3D-Setup/Settings/AutoTune/AutoStigAndFocus/SystemDetectorSettings/Det1";
            }


            try
            {
                XmlNode nodeName = doc.SelectSingleNode(det_signal + "/Name");
                XmlNode nodeB = doc.SelectSingleNode(det_signal + "/B");
                XmlNode nodeC = doc.SelectSingleNode(det_signal + "/C");

                if (nodeName == null || nodeB == null || nodeC == null)
                {
                    return false;
                }

                nodeName.InnerText = Name;
                nodeB.InnerText = B.ToString();
                nodeC.InnerText = C.ToString();
            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;

        }
        // FocusStep, FocusRange, FocusMaxAttempts
        public bool setAutoFocus(double step, double range, double maxAttempts)
        {
            try
            {
                string path = "/ATLAS3D-Setup/Settings/AutoTune/AutoStigAndFocus/Focus";
                XmlNode node1 = doc.SelectSingleNode(path + "/FocusStep");
                XmlNode node2 = doc.SelectSingleNode(path + "/FocusRange");
                XmlNode node3 = doc.SelectSingleNode(path + "/FocusMaxAttempts");

                if (node1 == null || node2 == null || node3 == null)
                {
                    return false;
                }

                node1.InnerText = step.ToString();
                node2.InnerText = range.ToString();
                node3.InnerText = maxAttempts.ToString();

            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;
        }
        // StigStep, StigConvergence, StigMaxAttempts
        public bool setAutoStig(double step, double convergence, double maxAttempts)
        {
            try
            {
                string path = "/ATLAS3D-Setup/Settings/AutoTune/AutoStigAndFocus/Stig";
                XmlNode node1 = doc.SelectSingleNode(path + "/StigStep");
                XmlNode node2 = doc.SelectSingleNode(path + "/StigConvergence");
                XmlNode node3 = doc.SelectSingleNode(path + "/StigMaxAttempts");

                if (node1 == null || node2 == null || node3 == null)
                {
                    return false;
                }

                node1.InnerText = step.ToString();
                node2.InnerText = convergence.ToString();
                node3.InnerText = maxAttempts.ToString();

            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;
        }
        /** Options **/
        // Destination folder
        public bool setDestinationFolder(string folderToSave, string image_name)
        {
            try
            {
                string path = "/ATLAS3D-Setup/Settings/Options";
                folderToSave = folderToSave.Replace(@"\\", @"\");
                XmlNode node1 = doc.SelectSingleNode(path + "/DestinationFolder");
                XmlNode node2 = doc.SelectSingleNode(path + "/ImageFileName");
                if (node1 == null || node2 == null)
                {
                    return false;
                }

                node1.InnerText = folderToSave;
                node2.InnerText = "slice" + image_name + "_";

            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;
        }
        // Track WD - check that is ok, EHT_Off, FIBGun_Off
        public bool setOptions(bool trackWD, bool EHTOff, bool FIBGunOff)
        {
            try
            {
                string path = "/ATLAS3D-Setup/Settings/Options";
                XmlNode node1 = doc.SelectSingleNode(path + "/TrackWD");
                XmlNode node2 = doc.SelectSingleNode(path + "/EHT_Off");
                XmlNode node3 = doc.SelectSingleNode(path + "/FIBGun_Off");
                if (node1 == null || node2 == null)
                {
                    return false;
                }

                if (trackWD)
                {
                    node1.InnerText = "true";
                }
                else
                {
                    node1.InnerText = "false";
                }
                if (EHTOff)
                {
                    node2.InnerText = "true";
                }
                else
                {
                    node2.InnerText = "false";
                }
                if (FIBGunOff)
                {
                    node3.InnerText = "true";
                }
                else
                {
                    node3.InnerText = "false";
                }

            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;

        }

        public bool setStageState(double x, double y, double z, double t, double r, double m)
        {
            try
            {
                string path = "/ATLAS3D-Setup/SamplePreparation/ATLAS3DSamplePrepShapes/Stage_State";
                XmlNode node1 = doc.SelectSingleNode(path + "/X");
                XmlNode node2 = doc.SelectSingleNode(path + "/Y");
                XmlNode node3 = doc.SelectSingleNode(path + "/Z");
                XmlNode node4 = doc.SelectSingleNode(path + "/T");
                XmlNode node5 = doc.SelectSingleNode(path + "/R");
                XmlNode node6 = doc.SelectSingleNode(path + "/M");

                if (node1 == null || node2 == null || node3 == null)
                {
                    return false;
                }

                node1.InnerText = x.ToString();
                node2.InnerText = y.ToString();
                node3.InnerText = z.ToString();
                node4.InnerText = t.ToString();
                node5.InnerText = r.ToString();
                node6.InnerText = m.ToString();

            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;

        }

        public bool disableTrackingMarks()
        {
            // Change sample prep TrenchDepth 
            try
            {
                string path = "/ATLAS3D-Setup/SamplePreparation/ATLAS3DSamplePrepShapes/ATLAS3DSamplePrepSettings";
                XmlNode node1 = doc.SelectSingleNode(path + "/DoRegistrationMarks");
                XmlNode node2 = doc.SelectSingleNode(path + "/DoTrackingMarks");
                XmlNode node3 = doc.SelectSingleNode(path + "/DoAutoTuneMarks");

                if (node1 == null || node2 == null || node3 == null)
                {
                    return false;
                }

                node1.InnerText = "false";
                node2.InnerText = "false";
                node3.InnerText = "false";

            }
            catch (System.Xml.XPath.XPathException e)
            {
                Console.WriteLine(e.ToString());
                return false;
            }

            return true;

        }

        public bool setROI(double roiX, double roiY, double depth)
        {

            return true; // This is not trivial!!
            /*
            // Change sample prep TrenchDepth 
           try
               {
                   string path = "/ATLAS3D-Setup/SamplePreparation/ATLAS3DSamplePrepShapes/ATLAS3DSamplePrepSettings/";
                   XmlNode node1 = doc.SelectSingleNode(path + "/TrenchDepth");        

                   if (node1 == null)
                   {
                       return false;
                   }

                   node1.InnerText = roidepth.ToString();
               

               }
               catch (System.Xml.XPath.XPathException e)
               {
                   Console.WriteLine(e.ToString());
                   return false;
               }

               return true;
        
           }
               */

        }

    }
}
