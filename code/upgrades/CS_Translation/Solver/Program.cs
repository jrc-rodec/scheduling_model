using BenchmarkParsing;
using System.IO;
using System.Runtime.InteropServices;
using static BenchmarkParsing.BenchmarkParser;



namespace Solver
{
    internal class Program
    {
        static int index = 0;
        static ConsoleColor[] _colors = { ConsoleColor.Red, ConsoleColor.Green, ConsoleColor.Blue, ConsoleColor.Yellow, ConsoleColor.White, ConsoleColor.Magenta};
        static void RunExperiment(string basepath, bool[] criteriaStatus, int maxGenerations, int timeLimit, float targetFitness, int maxFunctionEvaluations, int iteration)
        {

            bool skip = false;
            bool keepMultiple = true;
            string outPath = "C:\\Users\\localadmin\\Desktop\\experiments\\GA_COMPARISON\\KEEP_MULTIPLE\\FJSSP\\";

            string[] instances = Directory.GetFiles(basepath);
            
            foreach (string instance in instances)
            {
                Console.ForegroundColor = _colors[index - 1];
                string instanceName = instance.Split("\\").Last();

                targetFitness = 0.0f;
                if (!File.Exists(outPath + instanceName + ".json"))
                {
                    PrepareFile(outPath + instanceName + ".json");
                }
                History gaResult = null; // free up memory
                if (!skip)
                {
                    Console.WriteLine(index + ": Processing: " + instanceName + " - Run #" + (iteration + 1));
                    BenchmarkParser parser = new BenchmarkParser();
                    //Console.WriteLine("Parsing Complete");
                    Encoding encoding = parser.ParseBenchmark(instance);
                    //Console.WriteLine("Encoding Complete");
                    DecisionVariables variables = new DecisionVariables(encoding);
                    //Console.WriteLine("Decision Variables Complete");
                    GAConfiguration config = new GAConfiguration(encoding, variables);


                    //Console.WriteLine("Configuration Complete");
                    GA ga = new GA(config, false);//, encoding.Durations);
                    //Console.WriteLine("GA Creation Complete");
                    ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]); // TODO: change signature parameter order
                    //Console.WriteLine("Starting Run");
                    gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, keepMultiple, false);
                    string[] fullPath = instance.Split("\\");
                    gaResult.Name = fullPath.Last();
                    gaResult.ToFile(outPath + gaResult.Name + ".json");
                    DelimitRun(outPath + instanceName + ".json");
                }
            }
        }

        static void PrepareFile(string filename)
        {
            File.AppendAllText(filename, "{results:[");
        }

        static void DelimitRun(string filename)
        {
            File.AppendAllText(filename, ",");
        }

        static void EndFile(string filename)
        {
            File.AppendAllText(filename, "];}");
        }
        static void RunExperimentWorkers(string basepath, bool[] criteriaStatus, int maxGenerations, int timeLimit, float targetFitness, int maxFunctionEvaluations, bool keepMultiple, bool localSearch, int iteration, bool adjustment)
        {

            bool skip = false;
            WFJSSPGA.SORT = true;
            string outPath = "C:\\Users\\localadmin\\Desktop\\experiments\\GA_COMPARISON\\KEEP_MULTIPLE\\FJSSP-W\\";


            //var dict = File.ReadLines("C:\\Users\\localadmin\\Downloads\\best_known_20250307.csv").Select(line => line.Split(';')).ToDictionary(line => line[0], line => line[1]);
            string[] instances = Directory.GetFiles(basepath);
            foreach (string instance in instances)
            {
                Console.ForegroundColor = _colors[index - 1];
                string instanceName = instance.Split("\\").Last();
                
               /* if (dict.ContainsKey(instanceName))
                {
                    bool success = float.TryParse(dict[instanceName], out targetFitness);
                    if (success)
                    {
                        criteriaStatus[2] = true;
                    } else
                    {
                        targetFitness = 0.0f;
                    }
                }*/
                if (!File.Exists(outPath+ instanceName + ".json"))
                {
                    PrepareFile(outPath + instanceName + ".json");
                }
                WorkerHistory gaResult = null; // free up memory
                if (!skip)
                {
                    Console.WriteLine(index + ": Processing: " + instanceName + " - Run #" + (iteration+1));
                    WorkerBenchmarkParser parser = new WorkerBenchmarkParser();
                    //Console.WriteLine("Parsing Complete");
                    WorkerEncoding encoding = parser.ParseBenchmark(instance);
                    //Console.WriteLine("Encoding Complete");
                    WorkerDecisionVariables variables = new WorkerDecisionVariables(encoding);
                    //Console.WriteLine("Decision Variables Complete");
                    WorkerGAConfiguration config = new WorkerGAConfiguration(encoding, variables);
                    

                    //Console.WriteLine("Configuration Complete");
                    WFJSSPGA ga = new WFJSSPGA(config, true, encoding.Durations);
                    //Console.WriteLine("GA Creation Complete");
                    ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]); // TODO: change signature parameter order
                    //Console.WriteLine("Starting Run");
                    gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, keepMultiple, localSearch, adjustment);
                    string[] fullPath = instance.Split("\\");
                    gaResult.Name = fullPath.Last();
                    gaResult.ToFile(outPath + gaResult.Name + ".json");
                    DelimitRun(outPath + instanceName + ".json");
                }
            }
        }
    


        static void Main(string[] args)
        {
            //string path = "C:\\Users\\localadmin\\Desktop\\experiments\\comparison\\benchmarks_no_workers\\"; // DEBUG
            //string path = "C:\\Users\\huda\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\benchmarks"; // DEBUG
            string path = "C:\\Users\\localadmin\\Downloads\\benchmarks_with_workers\\benchmarks_with_workers\\";
            int maxGenerations = 0;
            int timeLimit = 0;// 1200;// 300;// 1200;//1200;//300; // in seconds
            //float targetFitness = 1196.0f;
            float targetFitness = 0.0f;
            int maxFunctionEvaluations = 1000000;
            string mode = "FJSSP-W";
            if (args.Length > 0)
            {
                //path = args[0];
                int.TryParse(args[0], out index);
                Console.ForegroundColor = _colors[index-1];
                mode = args[1];
            }
            bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0};
            if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
            {
                Console.WriteLine("No valid stopping criteria was set!");
                return;
            }
            int nExperiments = 5;
            bool keepMultiple = false;
            bool localSearch = false;
            bool adjustmentStep = false;
            //int restartGenerations = 25;

            for(int i = 0; i < nExperiments; ++i) // assuming 5 instances
            {
                if (mode.Equals("FJSSP"))
                {
                    path = "C:\\Users\\localadmin\\Desktop\\experiments\\GA_COMPARISON\\benchmarks\\fjssp\\";
                    RunExperiment(path, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, i);
                } else
                {
                    path = "C:\\Users\\localadmin\\Desktop\\experiments\\GA_COMPARISON\\benchmarks\\fjssp-w\\";
                    RunExperimentWorkers(path, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, true, false, i, false);
                }
            }
        }
    }
}
