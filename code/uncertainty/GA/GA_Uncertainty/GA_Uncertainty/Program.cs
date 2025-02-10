using System.Collections.Generic;

namespace GA_Uncertainty
{
    internal class Program
    {
        static int index = 0;
        static ConsoleColor[] _colors = { ConsoleColor.Red, ConsoleColor.Green, ConsoleColor.Blue, ConsoleColor.Yellow, ConsoleColor.White, ConsoleColor.Magenta };

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
        static void RunExperiment(string basepath, string outPath, string knownBestPath, bool[] criteriaStatus, int maxGenerations, int timeLimit, float targetFitness, int maxFunctionEvaluations, bool keepMultiple, int iteration)
        {

            Dictionary<string, string> dict = new Dictionary<string, string>();
            if (knownBestPath != "")
            {
                dict = File.ReadLines(knownBestPath).Select(line => line.Split(';')).ToDictionary(line => line[0], line => line[1]);
            }
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
                    }
                    else
                    {
                        targetFitness = 0.0f;
                    }
                }
                if (!File.Exists(outPath + instanceName + ".json"))
                {
                    PrepareFile(outPath + instanceName + ".json");
                }
                History gaResult = null; // free up memory
                Console.WriteLine(index + ": Processing: " + instanceName + " - Run #" + (iteration + 1));
                BenchmarkParser parser = new BenchmarkParser();
                //Console.WriteLine("Parsing Complete");
                Encoding encoding = parser.ParseBenchmark(instance);
                //Console.WriteLine("Encoding Complete");
                DecisionVariables variables = new DecisionVariables(encoding);
                //Console.WriteLine("Decision Variables Complete");
                GAConfiguration config = new GAConfiguration(encoding, variables);


                //Console.WriteLine("Configuration Complete");
                GA ga = new GA(config, true, encoding.Durations);
                //Console.WriteLine("GA Creation Complete");
                ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]); // TODO: change signature parameter order
                //Console.WriteLine("Starting Run");
                gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, keepMultiple);
                string[] fullPath = instance.Split("\\");
                gaResult.Name = fullPath.Last();
                gaResult.ToFile(outPath + gaResult.Name + ".json");
                DelimitRun(outPath + instanceName + ".json");
            }
        }

        class Testing
        {
            private int _a;
            private int _b;

            public Testing()
            {
                Random random = new Random();
                _a = random.Next(100);
                _b = random.Next(100);
            }

            public int A { get => _a; set => _a = value; }
            public int B { get => _b; set => _b = value; }

            public string ToString()
            {
                return "A: " + _a + " | B: " + _b;
            }
        }

        static void TestSorting()
        {
            List<Testing> testings = new List<Testing>();
            for (int i = 0; i < 100; ++i)
            {
                testings.Add(new Testing());
            }
            List<Testing> sorted = [.. testings
                        .OrderBy(a => a.A)
                        .ThenBy(b => b.B)];
            for (int i = 0; i < sorted.Count; ++i)
            {
                Console.WriteLine(sorted[i].ToString());
            }
        }

        static void Main(string[] args)
        {
            IndividualLoader.LoadResults("C:\\Users\\huda\\Downloads\\benchmarks_with_workers\\benchmarks_with_workers\\", "C:\\Users\\huda\\Documents\\ResultRewriting\\cplex_cp_results.json", true);
            /*int index = 0;
            string config = "";
            if (args.Length > 0)
            {
                for(int i = 0; i < args.Length; ++i)
                {
                    if (args[i] == "-i")
                    {
                        int.TryParse(args[++i], out index);
                        Console.ForegroundColor = _colors[(index - 1) % _colors.Length];
                    } else if (args[i] == "-c")
                    {
                        config = args[++i];
                    }
                    Console.WriteLine(args[i]);
                }
            }*/
            /*
            string path = "<insert path to benchmarks here>";
            string outPath = "<insert output path here>";
            string knownBestPath = "<insert path to best known results here>";
            int maxGenerations = 0;
            int timeLimit = 300; // in seconds
            float targetFitness = 0.0f;
            int maxFunctionEvaluations = 0;
            bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0 };
            if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
            {
                Console.WriteLine("No valid stopping criteria was set!");
                return;
            }
            int nExperiments = 1;
            bool keepMultiple = false;

            for (int i = 0; i < nExperiments; ++i)
            {
                RunExperiment(path, outPath, knownBestPath, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, keepMultiple, i);
            }
            */
        }
    }
}
