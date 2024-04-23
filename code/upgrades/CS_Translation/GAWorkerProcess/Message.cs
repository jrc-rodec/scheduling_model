using NetMQ;
using Newtonsoft.Json.Linq;
using Solver;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.Serialization;
using System.Text;
using System.Threading.Tasks;

namespace GAWorkerProcess
{
    public class Message
    {
        public static int MESSAGE_ID = 0;
        public int id = MESSAGE_ID++;

    }

    public class ResponseMessage : Message
    {
        public History history;
        public string senderTopic;
    }

    public class RequestMessage : Message
    {
        public int[,] durations;
        public int timeLimit = 0;
        public int fevalLimit = 0;
        public float targetFitness = 0.0f;
        public int maxGenerations = 0;
    }

    public class MessageConverter<T> where T : Message
    {
        public byte[] ToByteArray(T message)
        {
            TypeConverter obj = TypeDescriptor.GetConverter(message.GetType());
            byte[] bt = (byte[])obj.ConvertTo(message, typeof(byte[]));
            return bt;
        }

        public T FromByteArray(byte[] data)
        {
            MemoryStream ms = new MemoryStream(data);
            DataContractSerializer dvs;
            dvs = new DataContractSerializer(typeof(T));
            T msg = (T)dvs.ReadObject(ms);
            ms.Close();
            return msg;
        }
    }

}
