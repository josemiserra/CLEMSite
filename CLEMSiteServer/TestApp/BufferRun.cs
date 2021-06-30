using System.Collections.Generic;

namespace msite
{
    public static class BufferRun
    {

        private static Queue<string> messages_list = new Queue<string>();
        public static int message_counter = 0;
        public static bool isPaused = false;
        public static bool Stop = false;
        public static int last_index = 0;
        public static string lastMessage = "";
        

        public static bool messageAvailable()
        {
            return (messages_list.Count > 0);
        }
        public static string getLastMessage()
        {
            if (messages_list.Count > 1)
            {
                shrinkToOne();
            }
            return BufferRun.messages_list.Dequeue();
        }
        public static void addMessage(string message)
        {
            messages_list.Enqueue(message);
            if (messages_list.Count == 2048)
            {
                messages_list.Clear();
            }
        }
        public static void shrinkToOne()
        {
            string one = "";
            if (messages_list != null && messages_list.Count > 0)
            {
                int i = 0;
                while (messages_list.Count > 0 || i<100)
                {
                    one = one + messages_list.Dequeue() + System.Environment.NewLine;
                    i++;
                }
                messages_list.Clear();
                messages_list.Enqueue(one);
            }
        }

    }
}