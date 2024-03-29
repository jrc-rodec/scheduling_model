using BenchmarkParsing;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Solver;

namespace Experiments
{
    public class Program
    {

        static string GetPath(string source, int instance)
        {
            string basePath = "C:\\Users\\dhutt\\Desktop\\SCHEDULING_MODEL\\code\\upgrades\\code\\benchmarks\\";
            if (source.StartsWith("0"))
            {
                basePath += "0_BehnkeGeiger\\Behnke"+instance+".fjs";
            } else if (source.StartsWith("1"))
            {
                basePath += "1_Brandimarte\\BrandimarteMk"+instance+".fjs";
            } else if (source.StartsWith("2a")) 
            {
                basePath += "2a_Hurink_sdata\\HurinkSData"+instance+".fjs";
            } else if (source.StartsWith("2b"))
            {
                basePath += "2b_Hurink_edata\\HurinkEData"+instance+".fjs";
            } else if (source.StartsWith("2c"))
            {
                basePath += "2c_Hurink_rdata\\HurinkRData"+instance+".fjs";
            } else if (source.StartsWith("2d"))
            {
                basePath += "2d_Hurink_vdata\\HurinkVData"+instance+".fjs";
            } else if (source.StartsWith("3"))
            {
                basePath += "3_DPpaulli\\DPpaulli"+instance+".fjs";
            } else if (source.StartsWith("4"))
            {
                basePath += "4_ChambersBarnes\\ChambersBarnes"+instance+".fjs";
            } else if (source.StartsWith("5"))
            {
                basePath += "5_Kacem\\Kacem"+instance+".fjs";
            } else
            {
                basePath += "6_Fattahi\\Fattahi"+instance+".fjs";
            }
            return basePath;
        }

        static History RunExperiment(GAConfiguration configuration, bool[] stoppingCriteria, int maxGenerations, int timeLimit, float targetFitness, int maxFunctionEvaluations)
        {
            GA ga = new GA(configuration, false);
            ga.SetStoppingCriteriaStatus(stoppingCriteria[0], stoppingCriteria[1], stoppingCriteria[3], stoppingCriteria[2]); // TODO: change signature parameter order
            return ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
        }

        static void Main(string[] args)
        {
            // NOTE: this could easily be parallelized
            int nExperiments = 20;
            int maxParallel = 5;
            // Testing
            string path = @"C:\Users\dhutt\Downloads\ga_results.json";
            StreamReader reader = new StreamReader(path);
            string json = reader.ReadToEnd();
            reader.Close();
            JObject data = JObject.Parse(json);
            foreach(KeyValuePair<string, JToken> run in data)
            {
                string key = run.Key;
                JToken value = run.Value;
                float minFitness = (float)value[0];
                float maxFitness = (float)value[1];
                float minRuntime = (float)value[2];
                float maxRuntime = (float)value[3];
                float averageFitness = (float)value[4];
                float averageRuntime = (float)value[5];
                string source = (string)value[6];
                int instance = (int)value[7];

                string benchmarkPath = GetPath(source, instance);
                BenchmarkParser parser = new BenchmarkParser();
                Encoding result = parser.ParseBenchmark(benchmarkPath);
                DecisionVariables variables = new DecisionVariables(result);
                GAConfiguration configuration = new GAConfiguration(result, variables);
                int maxGenerations = 0;
                int timeLimit = 3600;
                float targetFitness = minFitness;
                int maxFunctionEvaluations = 0;
                bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0 };
                if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
                {
                    Console.WriteLine("No valid stopping criteria was set!");
                    return;
                }
                Console.WriteLine("Starting " + nExperiments + " experiments for " + source + "-" + instance);
                int finished = 0;
                for(int j = 0; j < nExperiments / maxParallel; ++j)
                {

                    Task<History>[] experiments = new Task<History>[maxParallel];
                    for (int i = 0; i < maxParallel; ++i)
                    {
                        experiments[i] = Task<History>.Factory.StartNew(() => RunExperiment(configuration, criteriaStatus, maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations));
                        Console.WriteLine("Started experiment #" + (i + 1) + "/" + nExperiments);
                    }
                    Task.WaitAll(experiments);
                    for(int i = 0; i < experiments.Length; ++i)
                    {
                        History gaResult = experiments[i].Result;
                        ++finished;
                        gaResult.ToFile(source + "_" + instance + "_" + finished + ".json");
                    }
                }
            }
        }
    }
}
