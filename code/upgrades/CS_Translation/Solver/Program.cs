using BenchmarkParsing;
using System.Collections;
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
            string outPath = "C:\\Users\\dhutt\\Desktop\\experiment\\results\\restart_tracking\\fjssp\\";

            string[] instances = Directory.GetFiles(basepath);
            
            foreach (string instance in instances)
            {
                Console.ForegroundColor = _colors[index - 1];
                string instanceName = instance.Split("\\").Last();

                targetFitness = 0.0f;
                string filename = outPath + instanceName + maxFunctionEvaluations + ".json";
                if (!File.Exists(filename))
                {
                    PrepareFile(filename);
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
                    gaResult.ToFile(outPath + gaResult.Name + maxFunctionEvaluations + ".json");
                    DelimitRun(filename);
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
            string outPath = "C:\\Users\\dhutt\\Desktop\\experiment\\results\\restart_tracking\\fjssp-w\\";

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

            //var dict = File.ReadLines("<insert path to best known results here>").Select(line => line.Split(';')).ToDictionary(line => line[0], line => line[1]);
            string[] instances = Directory.GetFiles(basepath);
            foreach (string instance in instances)
            {
                Console.ForegroundColor = _colors[index - 1];
                string instanceName = instance.Split("\\").Last();

                /*if (dict.ContainsKey(instanceName))
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
                string filename = outPath + instanceName + maxFunctionEvaluations + ".json";
                if (!File.Exists(filename))
                {
                    PrepareFile(filename);
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
                    gaResult.ToFile(outPath + gaResult.Name + maxFunctionEvaluations + ".json");
                    DelimitRun(filename);
                }
            }
        }

        private class TestObject
        {
            public List<int> a;
            public List<int> b;
            public string name;


            public TestObject(List<int> c, List<int> d, string n)
            {
                a = c;
                b = d;
                name = n;
            }

            public override bool Equals(object? other)
            {
                TestObject o = (TestObject)other;
                if (a.Count != o.a.Count() || b.Count != o.b.Count() || name != o.name)
                {
                    return false;
                }
                for (int i = 0; i < a.Count; ++i)
                {
                    if (a[i] != o.a[i])
                    {
                        return false;
                    }
                }
                for (int i = 0; i < b.Count; ++i)
                {
                    if (b[i] != o.b[i])
                    {
                        return false;
                    }
                }
                return true;
                //return GetHashCode() == other.GetHashCode();
            }

            public override int GetHashCode()
            {
                return 0;//a[0] * 10 + b[b.Count - 1] + name.GetHashCode();//a.AsReadOnly().GetHashCode() ^ b.AsReadOnly().GetHashCode() ^ name.GetHashCode();
            }
        }

        static void Main(string[] args)
        {
            /*HashSet<int> list = new HashSet<int>();
            List<int> a = new(){ 1, 2, 3, 4, 5 };
            List<int> b = new() { 4, 5, 6, 7, 8 };
            List<int> c = new() { 1, 5, 6, 9, 0 };

            list.UnionWith(a);
            list.UnionWith(b);
            list.UnionWith(c);
            for(int i = 0; i < list.Count; ++i)
            {
                Console.Write(list.ElementAt(i));
            }

            HashSet<TestObject> list1 = new HashSet<TestObject>();
            TestObject ta = new TestObject(a, b, "a");
            TestObject tb = new TestObject(b, a, "b");
            TestObject tc = new TestObject(a, b, "a");
            TestObject td = new TestObject(a, c, "c");
            TestObject te = new TestObject(b, c, "d");
            TestObject tf = new TestObject(c, b, "e");
            TestObject tg = new TestObject(c, b, "f");

            list1.Add(ta);
            list1.Add(tb);
            list1.Add(tc);
            list1.Add(td);
            list1.Add(te);
            list1.Add(tf);
            list1.Add(tg);
            Console.WriteLine();

            for (int i = 0; i < list1.Count; ++i)
            {
                Console.Write(list1.ElementAt(i).name);
            }
            
            Dictionary<TestObject, int> testDict = new Dictionary<TestObject, int>();
            if (!testDict.ContainsKey(ta))
            {
                testDict.Add(ta, 1);
            }
            if (!testDict.ContainsKey(tb))
            {
                testDict.Add(tb, 1);
            }
            if (!testDict.ContainsKey(tc))
            {
                testDict.Add(tc, 1);
            }
            if (!testDict.ContainsKey(td))
            {
                testDict.Add(td, 1);
            }
            if (!testDict.ContainsKey(te))
            {
                testDict.Add(te, 1);
            }
            if (!testDict.ContainsKey(tf))
            {
                testDict.Add(tf, 1);
            }
            if (!testDict.ContainsKey(tg))
            {
                testDict.Add(tg, 1);
            }

            Console.WriteLine();

            foreach(TestObject t in testDict.Keys)
            {
                Console.Write(t.name);
            }
            */

            //string path = "C:\\Users\\localadmin\\Desktop\\experiments\\comparison\\benchmarks_no_workers\\"; // DEBUG
            //string path = "C:\\Users\\huda\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\benchmarks"; // DEBUG
            string path = "C:\\Users\\localadmin\\Downloads\\benchmarks_with_workers\\benchmarks_with_workers\\";
            int maxGenerations = 0;
            int timeLimit = 0;// 300;// 1200;//1200;//300; // in seconds
            //float targetFitness = 1196.0f;
            float targetFitness = 0.0f;
            int maxFunctionEvaluations = 0;
            string mode = "FJSSP";
            if (args.Length > 0)
            {
                //path = args[0];
                int.TryParse(args[0], out index);
                Console.ForegroundColor = _colors[index-1];
                string criteria = args[1];
                if (criteria == "feval")
                {
                    int.TryParse(args[2], out maxFunctionEvaluations);
                } else if (criteria == "target")
                {
                    float.TryParse(args[2], out targetFitness);
                }
                mode = args[3];
            }
            bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0};
            if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
            {
                Console.WriteLine("No valid stopping criteria was set!");
                return;
            }
            int nExperiments = 1;
            bool keepMultiple = true;
            bool localSearch = false;
            bool adjustmentStep = false;
            //int restartGenerations = 25;

            for(int i = 0; i < nExperiments; ++i) // assuming 5 instances
            {
                if (mode == "FJSSP") 
                {
                    path = "C:\\Users\\dhutt\\Desktop\\experiment\\no_worker\\";
                    RunExperiment(path, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, i);
                }
                //if (mode.Equals("FJSSP"))
                //{
                //RunExperiment(path, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, i);
                //} else
                //{
                else {
                    path = "C:\\Users\\dhutt\\Desktop\\experiment\\worker\\";
                    RunExperimentWorkers(path, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, keepMultiple, localSearch, i, adjustmentStep);
                }
            }
        }
    }
}
