using BenchmarkParsing;
using static BenchmarkParsing.BenchmarkParser;


namespace Solver
{
    internal class Program
    {
        static void Main(string[] args)
        {
            string path = "C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model\\code\\reworked_data_model\\benchmarks_with_workers\\6_Fattahi_1_workers.fjs"; // DEBUG
            int maxGenerations = 0;
            int timeLimit = 60; // in seconds
            //float targetFitness = 1196.0f;
            float targetFitness = 0.0f;
            int maxFunctionEvaluations = 0;
            if(args.Length > 0)
            {
                path = args[0];
                if(args.Length > 1)
                {
                    int.TryParse(args[1], out maxGenerations);
                    int.TryParse(args[2], out timeLimit);
                    float.TryParse(args[3], out targetFitness);
                    int.TryParse(args[4], out maxFunctionEvaluations);
                }
            }
            bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0};
            if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
            {
                Console.WriteLine("No valid stopping criteria was set!");
                return;
            }
            bool worker = true;
            if (!worker)
            {
                BenchmarkParser parser = new BenchmarkParser();
                Encoding result = parser.ParseBenchmark(path);
                DecisionVariables variables = new DecisionVariables(result);
                GAConfiguration configuration = new GAConfiguration(result, variables);
                GA ga = new GA(configuration, true);
                ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]); // TODO: change signature parameter order
                History gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
                gaResult.ToFile("test.json");
                Console.WriteLine(gaResult.Result.ToString());
            } else
            {
                WorkerBenchmarkParser parser = new WorkerBenchmarkParser();
                WorkerEncoding encoding = parser.ParseBenchmark(path);
                WorkerDecisionVariables variables = new WorkerDecisionVariables(encoding);
                WorkerGAConfiguration config = new WorkerGAConfiguration(encoding, variables);
                WFJSSPGA ga = new WFJSSPGA(config, true, encoding.Durations);
                ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]);
                WorkerHistory gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
                gaResult.ToFile("test.json");
                Console.WriteLine(gaResult.Result.ToString());
            }
            Console.ReadLine();
        }
    }
}
