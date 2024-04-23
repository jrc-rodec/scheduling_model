using BenchmarkParsing;
using NetMQ;
using NetMQ.Sockets;
using Solver;
using System.ComponentModel;
using System.Runtime.Serialization;


namespace GAWorkerProcess
{
    internal class Program
    {



        static ResponseSocket _server;
        static void SendFinishedMessage(ResponseMessage message)
        {
            MessageConverter<ResponseMessage> messageConverter = new MessageConverter<ResponseMessage>();
            _server.SendFrame(messageConverter.ToByteArray(message));
        }

        static string GetPath(string file)
        {
            string basePath = "C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model\\code\\upgrades\\benchmarks\\";
            if (file.StartsWith("Be"))
            {
                basePath += "0_BehnkeGeiger\\";
            }
            else if (file.StartsWith("Br"))
            {
                basePath += "1_Brandimarte\\";
            }
            else if (file.StartsWith("HurinkS"))
            {
                basePath += "2a_Hurink_sdata\\";
            }
            else if (file.StartsWith("HurinkE"))
            {
                basePath += "2b_Hurink_edata\\";
            }
            else if (file.StartsWith("HurinkR"))
            {
                basePath += "2c_Hurink_rdata\\";
            }
            else if (file.StartsWith("HurinkV"))
            {
                basePath += "2d_Hurink_vdata\\";
            }
            else if (file.StartsWith("DP"))
            {
                basePath += "3_DPpaulli\\";
            }
            else if (file.StartsWith("Ch"))
            {
                basePath += "4_ChambersBarnes\\";
            }
            else if (file.StartsWith("Ka"))
            {
                basePath += "5_Kacem\\";
            }
            else if(file.StartsWith("Fa"))
            {
                basePath += "6_Fattahi\\";
            }
            else
            {
                basePath += "Generated\\";
            }
            return basePath + "file"+".fjs";
        }

        static void Main(string[] args)
        {
            string topic = args[0];
            string benchmarkFile = GetPath(args[1]);
            BenchmarkParser parser = new BenchmarkParser();
            Encoding result = parser.ParseBenchmark(benchmarkFile);
            _server = new ResponseSocket();
            _server.Bind("tcp://*:5557");
            SubscriberSocket _subscriber = new SubscriberSocket();
            _subscriber.Connect("tcp://127.0.0.1:5556");
            _subscriber.Subscribe(topic);
            MessageConverter<RequestMessage> messageConverter = new MessageConverter<RequestMessage>();
            while (true)
            {
                string senderTopic = _subscriber.ReceiveFrameString(); // needed ?
                byte[] msg = _subscriber.ReceiveFrameBytes();

                // parse message
                RequestMessage requestMessage = messageConverter.FromByteArray(msg);
                int[,] durations = requestMessage.durations;

                // replace duration matrix
                result.Durations = durations;

                DecisionVariables variables = new DecisionVariables(result);
                GAConfiguration configuration = new GAConfiguration(result, variables);

                int maxGenerations = requestMessage.maxGenerations;
                float targetFitness = requestMessage.targetFitness;
                int maxFunctionEvaluations = requestMessage.fevalLimit;
                int timeLimit = requestMessage.timeLimit;
                bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0 };


                // start optimization
                GA ga = new GA(configuration, false);
                ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]); // TODO: change signature parameter order
                
                History history = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
                // done
                ResponseMessage resultMessage = new ResponseMessage();
                resultMessage.history = history;
                resultMessage.senderTopic = topic;
                SendFinishedMessage(resultMessage);
            }
            _server.Close();
        }
    }
}
