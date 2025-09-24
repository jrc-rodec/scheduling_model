using BenchmarkParsing;
using System.Text.Json.Nodes;
using static BenchmarkParsing.BenchmarkParser;

namespace GATesting
{
    internal class Program
    {
        static void Main(string[] args)
        {
            string inputString = args[1];
            JsonNode data = JsonArray.Parse(inputString);
            string basepath = (string)data["path"];
            int maxGenerations = (int)data["maxGenerations"];
            int timeLimit = (int)data["timeLimit"];
            float targetFitness = (float)data["targetFitness"];
            int maxFunctionEvaluations = (int)data["maxFevals"];

            bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0 };
            if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
            {
                Console.WriteLine("No valid stopping criteria was set!");
                return;
            }

            bool keepMultiple = (bool)data["keepMultiple"];
            string instance = (string)data["instanceName"];
            string experimentName = (string)data["name"];

            // legacy flags
            int iteration = Int32.Parse(args[2]);
            GA.SORT = true;
            WorkerBenchmarkParser parser = new WorkerBenchmarkParser();
            WorkerEncoding encoding = parser.ParseBenchmark(instance);
            WorkerDecisionVariables variables = new WorkerDecisionVariables(encoding);
            GAConfiguration config = new GAConfiguration(encoding, variables);
            GA ga = new GA(config, true, encoding.Durations);
            ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]);
            History gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, keepMultiple);

        }
    }
}
