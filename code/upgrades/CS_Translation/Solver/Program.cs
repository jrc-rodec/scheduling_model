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
            string outPath = "C:\\Users\\localadmin\\Desktop\\experiments\\FJSSP_5\\ga_sorted\\";

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
                if (instance.EndsWith("6_Fattahi_14_workers.fjs"))
                {
                    skip = false;
                }
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
                    gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, false, false);
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
            File.AppendAllText(filename, "];");
        }
        static void RunExperimentWorkers(string basepath, bool[] criteriaStatus, int maxGenerations, int timeLimit, float targetFitness, int maxFunctionEvaluations, bool keepMultiple, bool localSearch, int iteration, bool adjustment)
        {

            bool skip = false;
            WFJSSPGA.SORT = true;
            string outPath = "C:\\Users\\localadmin\\Desktop\\experiments\\SORTED_GA\\";
            if (index == 1)
            {
                outPath = "C:\\Users\\localadmin\\Desktop\\experiments\\FJSSP_5\\GA_SORTING_TEST\\unsorted\\";
                WFJSSPGA.SORT = false;
            } 
            //if (localSearch)
            //{
            //if(iteration == 0)
            //{
            //    outPath += "dissimilarity\\";
            //    WFJSSPIndividual.UseDissimilarity = true;
            //} else
            //{
            //    outPath += "no_dissimilarity\\";
            //    WFJSSPIndividual.UseDissimilarity = false;
            //}
            //outPath += ((iteration+1)*50).ToString()+"_populationSize\\";
            //} else
            //{
            //    outPath += "nolocal\\";
            //}
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

            var dict = File.ReadLines("<insert path to best known results here>").Select(line => line.Split(';')).ToDictionary(line => line[0], line => line[1]);
            string[] instances = Directory.GetFiles(basepath);
            foreach (string instance in instances)
            {
                Console.ForegroundColor = _colors[index - 1];
                string instanceName = instance.Split("\\").Last();
                
                if (dict.ContainsKey(instanceName))
                {
                    bool success = float.TryParse(dict[instanceName], out targetFitness);
                    if (success)
                    {
                        criteriaStatus[2] = true;
                    } else
                    {
                        targetFitness = 0.0f;
                    }
                }
                if (!File.Exists(outPath+ instanceName + ".json"))
                {
                    PrepareFile(outPath + instanceName + ".json");
                }
                WorkerHistory gaResult = null; // free up memory
                if (instance.EndsWith("6_Fattahi_14_workers.fjs"))
                {
                    skip = false;
                }
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
            int timeLimit = 1200;// 300;// 1200;//1200;//300; // in seconds
            //float targetFitness = 1196.0f;
            float targetFitness = 0.0f;
            int maxFunctionEvaluations = 0;
            if (args.Length > 0)
            {
                //path = args[0];
                int.TryParse(args[0], out index);
                Console.ForegroundColor = _colors[index-1];
            }
            bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0};
            if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
            {
                Console.WriteLine("No valid stopping criteria was set!");
                return;
            }
            int nExperiments = 1;
            bool keepMultiple = false;
            bool localSearch = false;
            bool adjustmentStep = false;
            //int restartGenerations = 25;

            for(int i = 0; i < nExperiments; ++i) // assuming 5 instances
            {
                //if (mode.Equals("FJSSP"))
                //{
                    //RunExperiment(path, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, i);
                //} else
                //{
                RunExperimentWorkers(path, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, false, false, i, adjustment);
                //}
            }
        }
    }
}
