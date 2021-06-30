using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;


// #define DEBUG

namespace msite
{
    
    // State object for reading client data asynchronously
    public class StateObject
    {
        // Client  socket.
        public Socket workSocket = null;
        // Size of receive buffer.
        public const int BufferSize = 1024;
        // Receive buffer.
        public byte[] buffer = new byte[BufferSize];
        // Received data string.
        public StringBuilder sb = new StringBuilder();
    }
    public class mPacket
    {
        public IEnumerable<byte> data = null;
        public byte fin = 0;
        public byte opcode = 0;
        public uint payload = 0;
    }

    public class AsynchronousSocketListener
    {
        // Thread signal.
        public static ManualResetEvent allDone = new ManualResetEvent(false);
        public static bool killMe = false;
        public MessageParser myMessageParser = new MessageParser();
        public static System.Net.IPAddress ipAddress = AsynchronousSocketListener.LocalIPAddress();
        public static short port = 8098;
        private Socket listener;
        private IPEndPoint localEndPoint;
        public static mPacket currentPacket = new mPacket();
        public const int header_size = 10;

        public AsynchronousSocketListener()
        {
            killMe = false;
        }

        public void StopListening()
        {
            killMe = true;
            allDone.Set(); // Thread continues
#if DEBUG_CONNECTIONS
                Console.WriteLine(this.myMessageParser._disconnect()); // Close all open things
#endif
            if (this.listener!=null)
                this.listener.Close();
        }


        public void StartListening()
        {
            // Establish the local endpoint for the socket.
            // The DNS name of the computer
            // running the listener
            killMe = false;
            this.localEndPoint = new IPEndPoint(ipAddress, port);

            // DUMP
            // Create a TCP/IP socket.
            this.listener = new Socket(AddressFamily.InterNetwork,
                SocketType.Stream, ProtocolType.Tcp);

            try // Bind the socket to the local endpoint and listen for incoming connections.
            {
                this.listener.Bind(localEndPoint);
                this.listener.Listen(100);
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }

        public void Listen()
        {
            try
            {
                // Set the event to nonsignaled state.
                allDone.Reset();

                // Start an asynchronous socket to listen for connections.
#if DEBUG_CONNECTIONS
                    Console.WriteLine("Waiting for a connection...");
#endif
                this.listener.BeginAccept(
                      new AsyncCallback(AcceptCallback),
                      this.listener);

                // Wait until a connection is made before continuing.
                allDone.WaitOne();
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }

        }

        /*** Connection accepted and a response is triggered **/
        public void AcceptCallback(IAsyncResult ar)
        {
            // Signal the main thread to continue.
            allDone.Set();
            if (killMe) return;
#if DEBUG_CONNECTIONS
                Console.WriteLine("Connection accepted...");
#endif
            // Get the socket that handles the client request.
            Socket listener = (Socket)ar.AsyncState;
            Socket handler = listener.EndAccept(ar);

            // Create the state object.
            StateObject state = new StateObject();
            state.workSocket = handler;


            var my_asyncCallback = new AsyncCallback(ReadCallback);
            handler.BeginReceive(state.buffer, 0, StateObject.BufferSize, 0, my_asyncCallback, state);
        }

        public void ReadCallback(IAsyncResult ar)
        {
            String content = String.Empty;

            // Retrieve the state object and the handler socket
            // from the asynchronous state object.
            StateObject state = (StateObject)ar.AsyncState;
            Socket handler = state.workSocket;
            bool success = ar.AsyncWaitHandle.WaitOne(5000, true);
            if (!success)
            {
                handler.Close();
                Console.WriteLine("Connection lost with " + handler.RemoteEndPoint.ToString());
            }
            try
            {
                // Read data from the client socket. 
                int bytesRead = handler.EndReceive(ar);
                #if DEBUG_CONNECTIONS
                    Console.WriteLine("Connected to " + handler.RemoteEndPoint.ToString());
                #endif
                if (bytesRead > 0)
                {
#if DEBUG_CONNECTIONS
                        Console.WriteLine("A total of " + bytesRead + " byte Received.");
#endif
                    if (bytesRead > header_size-1) // Our minimal com frames are 10 bytes
                    {
                        // There  might be more data, so store the data received so far.
                        // Get the stream

                        var header = state.buffer.Take(10);
                        uint payload = 0;
                        byte opcode = 0x0;
                        byte fin = 0;

                        ReadFrame(header, ref fin, ref opcode, ref payload);

                        if (payload == (bytesRead - header_size))  // Need to be sure I read all my data
                        {
                            state.sb.Append(Encoding.ASCII.GetString(state.buffer, header_size, (int)payload));
                            content = state.sb.ToString();
#if DEBUG_CONNECTIONS
                            Console.WriteLine("Read " + content.Length + " bytes from socket. \n Data :" + content);
#endif
                            byte[] reply = Operate(opcode, content);
                            // Convert the string data to byte data using ASCII encoding.
                            string s1 = Encoding.UTF8.GetString(reply);
#if DEBUG_CONNECTIONS
                            Console.WriteLine("Replying to the sender:" + s1);
#endif
                            // send the data back to the client.
                            Send(handler, reply);

                        }
                        else
                        {
                            if ((int)payload > StateObject.BufferSize)
                            {
                                AsynchronousSocketListener.currentPacket.data = header.ToList();
                                AsynchronousSocketListener.currentPacket.fin = fin;
                                AsynchronousSocketListener.currentPacket.opcode = opcode;
                                AsynchronousSocketListener.currentPacket.payload = (uint)payload;
                                state.sb.Append(Encoding.ASCII.GetString(state.buffer), header_size, StateObject.BufferSize - header_size)
                                    ;
                                int rest = (int)payload - (StateObject.BufferSize - header_size);
                                if (rest > (StateObject.BufferSize - header_size))
                                {
                                    state.buffer = new byte[rest]; // Just to be sure, reserve some extra memory
                                }

                                handler.BeginReceive(state.buffer, 0, (int)rest, 0,
                                    new AsyncCallback(ReadCallbackBigSize), state);
                                return;
                            }
                            state.sb.Append(Encoding.ASCII.GetString(state.buffer, header_size, (int)payload));
                            content = state.sb.ToString();
                            byte[] reply = Operate(opcode, content);
                            // Convert the string data to byte data using ASCII encoding.
                            string s1 = Encoding.UTF8.GetString(reply);
#if DEBUG_CONNECTIONS
                                Console.WriteLine("Replying to the sender:" + s1);
#endif
                            // send the data back to the client.
                            Send(handler, reply);
                        }
                    }
                    else
                    {
                        // Not all data received. Get more.
                        handler.BeginReceive(state.buffer, 0, StateObject.BufferSize, 0,
                        new AsyncCallback(ReadCallback), state);
                    }

                }
            }
            catch (System.Net.Sockets.SocketException e)
            {
                Console.WriteLine(e);
                return;
            }
        }

        public void ReadCallbackBigSize(IAsyncResult ar)
        {

            String content = String.Empty;

            // Retrieve the state object and the handler socket
            // from the asynchronous state object.
            StateObject state = (StateObject)ar.AsyncState;
            Socket handler = state.workSocket;
            bool success = ar.AsyncWaitHandle.WaitOne(5000, true);
            if (!success)
            {
                handler.Close();
                Console.WriteLine("Connection lost with " + handler.RemoteEndPoint.ToString());
            }
            try
            {
                // Read data from the client socket. 
                int bytesRead = handler.EndReceive(ar);
#if DEBUG_CONNECTIONS
                    Console.WriteLine("Connected to " + handler.RemoteEndPoint.ToString());
#endif
                if (bytesRead > 0)
                {
#if DEBUG_CONNECTIONS
                        Console.WriteLine("A total of " + bytesRead + " byte Received.");
#endif
                    uint payload = AsynchronousSocketListener.currentPacket.payload;
                    byte opcode = AsynchronousSocketListener.currentPacket.opcode;
                    byte fin = AsynchronousSocketListener.currentPacket.fin;

                    ReadFrame(AsynchronousSocketListener.currentPacket.data, ref fin, ref opcode, ref payload);
                    state.sb.Append(Encoding.ASCII.GetString(state.buffer));
                    content = state.sb.ToString();
                    byte[] reply = Operate(opcode, content);
                    state.buffer = new byte[StateObject.BufferSize]; // Restore original size
                                                                     // Convert the string data to byte data using ASCII encoding.
                    string s1 = Encoding.UTF8.GetString(reply);
#if DEBUG_CONNECTIONS
                        Console.WriteLine("Replying to the sender:" + s1);
#endif
                    // send the data back to the client.
                    Send(handler, reply);

                }

            }
            catch (System.Net.Sockets.SocketException e)
            {
                Console.WriteLine(e);
                return;
            }
        }

        private static void Send(Socket handler, byte[] byteData)
        {
            // Begin sending the data to the remote device.
            handler.BeginSend(byteData, 0, byteData.Length, 0,
                new AsyncCallback(SendCallback), handler);
        }
        public static IPAddress LocalIPAddress()
        {
            if (!System.Net.NetworkInformation.NetworkInterface.GetIsNetworkAvailable())
            {
                return null;
            }

            IPHostEntry host = Dns.GetHostEntry(Dns.GetHostName());

            return host
                .AddressList
                .FirstOrDefault(ip => ip.AddressFamily == AddressFamily.InterNetwork);
        }
        public static IPAddress[] LocalIPAddresses()
        {
            if (!System.Net.NetworkInformation.NetworkInterface.GetIsNetworkAvailable())
            {
                return null;
            }

            return Dns.GetHostAddresses(Dns.GetHostName());
        }
        private static void SendCallback(IAsyncResult ar)
        {
            try
            {
                // Retrieve the socket from the state object.
                Socket handler = (Socket)ar.AsyncState;

                // Complete sending the data to the remote device.
                int bytesSent = handler.EndSend(ar);
#if DEBUG_CONNECTIONS
                    Console.WriteLine("Sent {0} bytes to client.", bytesSent);
#endif
                handler.Shutdown(SocketShutdown.Both);
                handler.Close();

            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }

        private void ReadFrame(IEnumerable<byte> data, ref byte fin, ref byte opcode, ref uint payload)
        {
            byte[] header = data.ToArray();
            fin = (byte)(header[0] & (byte)(128));
            fin = (byte)(fin >> 7);
            opcode = (byte)(header[0] & (byte)(31));
            if (header[1] < 126)
            {
                payload = (uint)header[1];
            }
            else
            {
                if (header[1] == 126)
                {
                    int result = header[2];
                    result += ((byte)header[3] << 8);// 7
                    payload = (uint)result;
                }
                else if (header[1] == 127)
                {
                    int result = header[9] << 56;//1
                    result += header[8] << 48;   // 2
                    result += header[7] << 40;// 3
                    result += header[6] << 32;// 4
                    result += header[5] << 24;// 5
                    result += header[4] << 16;  // 6
                    result += header[3] << 8;// 7
                    result += header[2];  //  8
                    payload = (uint)result;
                }
            }
        }

        static byte[] GetBytes(string str)
        {
            byte[] bytes = new byte[str.Length * sizeof(char)];
            System.Buffer.BlockCopy(str.ToCharArray(), 0, bytes, 0, bytes.Length);
            return bytes;
        }

        private byte[] Operate(byte opcode, string content)
        {
            // Operate only works in case of:
            //  - pings
            //  - pongs
            //  - open connection
            //  - close connection
            byte[] reply = new byte[] { 0 };
            try
            {

                switch (opcode)
                {
                    case 0x9: // ping
                        {

                            JObject o = new JObject(new JProperty("uri", "getStatusAlert"));
                            string payload = this.myMessageParser.manage(o);
                            JObject m_reply = JObject.Parse(payload);
                            byte first = 0x8A; // 1 - 000 - 1010 pong nothing
                            string status = m_reply["Alert"].ToString();
                            switch (status)
                            {
                                case "MESSAGE_READY":
                                    first = 0x9A; // 1 - 001 - 1010 pong message waiting
                                    break;
                                case "OK": // nothing waiting
                                    first = 0x8A;
                                    break;
                                case "CANCELLED":
                                    first = 0xBA;
                                    break;
                                case "PAUSED":
                                    first = 0xCA; // paused
                                    break;
                                case "IDLE":
                                    first = 0xDA; // nothing to do
                                    break;
                                case "INITIALIZED":
                                    first = 0xAA; // nothing to do
                                    break;
                                case "COMPLETED":
                                    first = 0xEA; // nothing to do
                                    break;
                                default:
                                    first = 0xFA;
                                    break;
                            }
                            reply = PackFrame(first, payload);
                            break;
                        }
                    case (0xB): // open connection
                        {
                            byte first = 0x8C;
                            JObject o = new JObject(new JProperty("uri", "connect"));
                            string payload = this.myMessageParser.manage(o);
                            reply = PackFrame(first, payload);
                            break;
                        }
                    case (0x8):
                        { // cancel sample
                            byte first = 0x8C;                            
                            JObject o = new JObject(new JProperty("uri", "cancelSample"));
                            string payload = this.myMessageParser.manage(o);
                            reply = PackFrame(first, payload);
                            break;
                        }
                    case (0x1):
                        {
                            // getting files
                            byte first = 0x8C;
                            JObject o = new JObject();
                            o.Add("data", content);
                            o.Add("uri", "incomingFile");
                            string payload = this.myMessageParser.manage(o);
                            // If payload says error
                            Match match = Regex.Match(payload, @"Error");
                            if (!match.Success)
                            {
                                reply = PackFrame(first, payload);
                            }
                            else
                            {
                                // otherwise send error payload
                                first = 0x8F;
                                reply = PackFrame(first, payload);  // no need to send
                            }
                            break;
                        }
                    case (0x3):
                        {
                            // Possible functions so far in uri
                            byte first = 0x8C;
                            JObject o = JObject.Parse(content);
                            string payload = this.myMessageParser.manage(o);
                            // If payload says error
                            Match match = Regex.Match(payload, @"Error");
                            if (!match.Success)
                            {
                                reply = PackFrame(first, payload);  // no need to send
                            }
                            else
                            {
                                // otherwise send the error 
                                first = 0x8F;
                                reply = PackFrame(first, payload);
                            }
                            break;
                        }
                    default:
                        break;
                }
                return reply;
            }
            catch (Newtonsoft.Json.JsonReaderException e)
            {
                Console.WriteLine("Error parsing function:" + e.ToString());
                return reply;
            }

        }


        private byte[] PackFrame(byte f_byte, string payload)
        {
            byte[] reply = new byte[32];
            reply[0] = f_byte;

            if (payload.Length > 0)
            {
                byte[] payload_bytes = GetBytes(payload);

                if (payload_bytes.Length < 126)
                {
                    reply[1] = (byte)payload.Length;
                }
                else
                {
                    if (payload_bytes.Length < 65535)
                    {
                        reply[1] = (byte)126;
                        reply[2] = (byte)0;
                        reply[3] = (byte)0;
                        byte[] intBytes = BitConverter.GetBytes(payload_bytes.Length);
                        // Array.Reverse(intBytes);
                        int total_bytes = intBytes.Length;
                        for (int i = 2; i < total_bytes + 2; i++)
                        {
                            reply[i] = (byte)intBytes[i - 2];
                        }
                    }
                    else
                    {
                        reply[1] = (byte)127;
                        for (int i = 2; i < 10; i++)
                        {
                            reply[i] = (byte)0;
                        }
                        byte[] intBytes = BitConverter.GetBytes(payload_bytes.Length);
                        int total_bytes = intBytes.Length;
                        for (int i = 2; i < total_bytes + 2; i++)
                        {
                            reply[i] = intBytes[i - 2];
                        }
                    }
                }

                byte[] payl_s = GetBytes(payload);
                byte[] rv = new byte[payl_s.Length + reply.Length];
                System.Buffer.BlockCopy(reply, 0, rv, 0, reply.Length);
                System.Buffer.BlockCopy(payl_s, 0, rv, reply.Length, payl_s.Length);
                return rv;
            }
            else
            {
                byte[] rv = new byte[reply.Length];
                System.Buffer.BlockCopy(reply, 0, rv, 0, reply.Length);
                return rv;
            }
        }




    }



}