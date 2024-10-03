using BenchmarkParsing;
using System.IO;
using System.Runtime.InteropServices;
using static BenchmarkParsing.BenchmarkParser;
using static System.Net.Mime.MediaTypeNames;


namespace Solver
{
    internal class Program
    {

        static void RunExperiment(string basepath, bool[] criteriaStatus, int maxGenerations, int timeLimit, float targetFitness, int maxFunctionEvaluations)
        {
            // TODO
            bool skip = false;
            bool skipSource = false;
            string[] sources = Directory.GetDirectories(basepath);
            foreach (string source in sources)
            {
                History gaResult = null;
                //Console.WriteLine(source);
                if (source.EndsWith("6_Fattahi"))
                {
                    skipSource = false;
                }
                if (!skipSource)
                {

                    string[] instances = Directory.GetFiles(source);
                    foreach (string instance in instances)
                    {
                        if (instance.EndsWith("Fattahi4.fjs"))
                        {
                            skip = false;
                        }
                        if (!skip)
                        {
                            Console.WriteLine("Processing: " + instance);
                            BenchmarkParser parser = new BenchmarkParser();
                            Console.WriteLine("Parsing Complete");
                            Encoding result = parser.ParseBenchmark(instance);
                            Console.WriteLine("Encoding Complete");
                            DecisionVariables variables = new DecisionVariables(result);
                            Console.WriteLine("Decision Variables Complete");
                            GAConfiguration configuration = new GAConfiguration(result, variables);
                            Console.WriteLine("Configuration Complete");
                            GA ga = new GA(configuration, true);
                            Console.WriteLine("GA Creation Complete");
                            ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]); // TODO: change signature parameter order
                            Console.WriteLine("Starting Run");
                            gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
                            string[] fullPath = instance.Split("\\");
                            gaResult.Name = fullPath.Last();
                            gaResult.ToFile("C:\\Users\\localadmin\\Desktop\\experiments\\GA\\results_1_second.json");
                        }
                    }
                }
                //Console.ReadLine();
            }


            /*
            BenchmarkParser parser = new BenchmarkParser();
            Encoding result = parser.ParseBenchmark(path);
            DecisionVariables variables = new DecisionVariables(result);
            GAConfiguration configuration = new GAConfiguration(result, variables);
            GA ga = new GA(configuration, true);
            ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]); // TODO: change signature parameter order
            History gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
            // TODO
            gaResult.ToFile("test.json");
            Console.WriteLine(gaResult.Result.ToString());*/
        }

        static void PrepareFile(string filename)
        {
            File.AppendAllText(filename, "results=[");
        }

        static void DelimitRun(string filename)
        {
            File.AppendAllText(filename, ",");
        }

        static void EndFile(string filename)
        {
            File.AppendAllText(filename, "];");
        }
        static void RunExperimentWorkers(string basepath, bool[] criteriaStatus, int maxGenerations, int timeLimit, float targetFitness, int maxFunctionEvaluations)
        {
            // TODO
            basepath = "C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model\\code\\reworked_data_model\\benchmarks_with_workers\\";
            bool skip = false;
            //bool skipSource = true;
            //string[] sources = Directory.GetDirectories(basepath);
            //foreach (string source in sources)
            //{
            //Console.WriteLine(source);
            //    if (source.EndsWith("6_Fattahi"))
            //    {
            //        skipSource = false;
            //    }
            //    if (!skipSource)
            //    {

            string[] instances = Directory.GetFiles(basepath);
            foreach (string instance in instances)
            {
                //string path = "C:\\Users\\localadmin\\Desktop\\experiments\\worker_results\\ga_results\\with_localsearch\\" + gaResult.Name + ".json";
                if (!File.Exists(instance+".json"))
                {
                    PrepareFile(instance + ".json");
                }
                WorkerHistory gaResult = null; // free up memory
                //if (instance.EndsWith("Fattahi4.fjs"))
                //{
                //    skip = false;
                //}
                if (!skip)
                {
                    DelimitRun(instance + ".json");
                    Console.WriteLine("Processing: " + instance);
                    WorkerBenchmarkParser parser = new WorkerBenchmarkParser();
                    Console.WriteLine("Parsing Complete");
                    WorkerEncoding encoding = parser.ParseBenchmark(instance);
                    Console.WriteLine("Encoding Complete");
                    WorkerDecisionVariables variables = new WorkerDecisionVariables(encoding);
                    Console.WriteLine("Decision Variables Complete");
                    WorkerGAConfiguration config = new WorkerGAConfiguration(encoding, variables);
                    Console.WriteLine("Configuration Complete");
                    WFJSSPGA ga = new WFJSSPGA(config, true, encoding.Durations);
                    Console.WriteLine("GA Creation Complete");
                    ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]); // TODO: change signature parameter order
                    Console.WriteLine("Starting Run");
                    gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
                    string[] fullPath = instance.Split("\\");
                    gaResult.Name = fullPath.Last();
                    gaResult.ToFile("C:\\Users\\localadmin\\Desktop\\experiments\\worker_results\\ga_results\\with_localsearch_again\\"+ gaResult.Name + ".json");
                }
            }
        }
    


            static void Main(string[] args)
        {
            //string path = "C:\\Users\\huda\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\benchmarks_with_workers\\6_Fattahi_1_workers.fjs"; // DEBUG
            string path = "C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\external_test_data\\FJSSPinstances"; // DEBUG
            int maxGenerations = 0;
            int timeLimit = 1200;//1200;//300; // in seconds
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
            //RunExperiment(path, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
            for(int i = 0; i < 3; ++i) // assuming 5 instances
            {
                RunExperimentWorkers(path, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
            }
            /*
            bool worker = false;
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
            */
        }
    }
}
