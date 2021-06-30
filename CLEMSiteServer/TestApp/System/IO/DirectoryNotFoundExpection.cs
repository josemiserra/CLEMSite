using System.Runtime.Serialization;

namespace System.IO
{
    [Serializable]
    internal class DirectoryNotFoundExpection : Exception
    {
        public DirectoryNotFoundExpection()
        {
        }

        public DirectoryNotFoundExpection(string message) : base(message)
        {
        }

        public DirectoryNotFoundExpection(string message, Exception innerException) : base(message, innerException)
        {
        }

        protected DirectoryNotFoundExpection(SerializationInfo info, StreamingContext context) : base(info, context)
        {
        }
    }
}