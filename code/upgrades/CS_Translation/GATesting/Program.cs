using BenchmarkParsing;
using System;
using System.Globalization;
using System.Security;
using System.Text.Json;
using System.Text.Json.Nodes;
using static BenchmarkParsing.BenchmarkParser;

namespace GATesting
{
    internal class Program
    {

        static void PrintOne(string test)
        {
            Console.WriteLine("1");
        }

        static void PrintTwo()
        {
            Console.WriteLine("2");
        }

        static void Test(int[] values)
        {
            for(int i = 0; i < values.Length; i++)
            {
                Console.Write(values[i]);
            }
            Console.WriteLine();
            Random random = new Random();
            int pA = random.Next(values.Length - 1);
            int pB = random.Next(pA, values.Length);
            Console.WriteLine(pA + " | " + pB);
            while (pA < pB)
            {
                int tmp = values[pA];
                values[pA] = values[pB];
                values[pB] = tmp;
                ++pA;
                --pB;
            }
            for (int i = 0; i < values.Length; i++)
            {
                Console.Write(values[i]);
            }
            Console.WriteLine();
        }

        public static void PrintArray(int[] values)
        {
            for (int i = 0; i < values.Length; i++)
            {
                Console.Write(values[i]);
            }
            Console.WriteLine();
        }

        public static void CopyTest(int[] parentA, int[] parentB)
        {
            Random random = new Random();
            int pA = random.Next(parentA.Length+1);
            int[] target = new int[parentA.Length];
            PrintArray(parentA);
            PrintArray(parentB);
            Console.WriteLine(pA);
            Array.Copy(parentA, 0, target, 0, pA);
            Array.Copy(parentB, pA, target, pA, target.Length - pA);
            PrintArray(target);

            pA = random.Next(parentA.Length - 1);
            int pB = random.Next(pA, parentB.Length + 1);
            Console.WriteLine(pA + " | " + pB);
            Array.Copy(parentA, 0, target, 0, pA);
            Array.Copy(parentB, pA, target, pA, pB - pA);
            Array.Copy(parentA, pB, target, pB, target.Length - pB);
            PrintArray(target);
        }
        static void PrepareFile(string filename)
        {
            File.AppendAllText(filename, "{\"results\":[");
        }

        static void DelimitRun(string filename)
        {
            File.AppendAllText(filename, ",");
        }

        static void EndFile(string filename)
        {
            File.AppendAllText(filename, "];");
        }

        static void Main(string[] args)
        {
            /*int[] testing = new int[0];
            int[] values = { 1, 2, 3, 4, 5, 6, 7, 8, 9 };
            Test(values);
            int[] parentA = { 1, 2, 3, 4, 5};
            int[] parentB = { 6, 7, 8, 9, 0 };
            CopyTest(parentA, parentB);*/
            try { 
                string inputString = args[0];
                FileStream stream = File.OpenRead(inputString);
                Dictionary<string, string> data = JsonSerializer.Deserialize<Dictionary<string, string>>(stream);
                //JsonNode data = JsonArray.Parse(inputString);
                string basepath = (string)data["path"];
                int maxGenerations = (int)int.Parse(data["maxGenerations"]);
                int timeLimit = (int)int.Parse(data["timeLimit"]);
                float targetFitness = (float)float.Parse(data["targetFitness"]);
                int maxFunctionEvaluations = (int)int.Parse(data["maxFevals"]);

                bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0 };
                if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
                {
                    Console.WriteLine("No valid stopping criteria was set!");
                    return;
                }

                bool keepMultiple = (bool)bool.Parse(data["keepMultiple"]);
                string instance = (string)data["instanceName"];
                string experimentName = (string)data["name"];

                string outPath = (string)data["outputPath"];
                int nExperiments = (int)int.Parse(data["nExperiments"]);

                int iteration = int.Parse(args[1]);

                int populationSize = (int)int.Parse(data["populationSize"]);
                int offspringAmount = (int)int.Parse(data["offspringAmount"]);
                float populationSizeGrowthRate = (float)float.Parse(data["populationGrowthRate"]);
                int maxPopulationSize = (int)int.Parse(data["maxPopulationSize"]);
                float offspringRate = (float)float.Parse(data["offspringRate"]);
                float mutationProbability = (float)float.Parse(data["mutationProbability"]);
                bool adaptMutationProbability = (bool)bool.Parse(data["adaptMutationProbability"]);
                float maxMutationProbability = (float)float.Parse(data["maxMutationProbability"]);
                float elitismRate = (float)float.Parse(data["elitismRate"]);
                int tournamentSize = (int)int.Parse(data["tournamentSize"]);
                //bool adaptRates = (bool)data["adaptRates"];
                bool adaptTournamentSize = (bool)bool.Parse(data["adaptTournamentSize"]);
                bool adaptElitismRate = (bool)bool.Parse(data["adaptElitismRate"]);
                float maxElitism = (float)float.Parse(data["maxElitism"]);
                float maxTournament = (float)float.Parse(data["maxTournamentRate"]);
                bool doRestarts = (bool)bool.Parse(data["doRestarts"]);
                int restartGenerations = (int)int.Parse(data["restartGenerations"]);

                string mutationMethod = (string)data["mutationMethod"];
                string recombinationMethod = (string)data["recombinationMethod"];
                string mutationGrowthMethod = (string)data["mutationGrowthMethod"];

                GA.SORT = true;
                WorkerBenchmarkParser parser = new WorkerBenchmarkParser();
                WorkerEncoding encoding = parser.ParseBenchmark(basepath);
                WorkerDecisionVariables variables = new WorkerDecisionVariables(encoding);

                GAConfiguration config = new GAConfiguration(encoding, variables);
                config.PopulationSize = populationSize;
                config.OffspringAmount = offspringAmount;
                config.PopulationSizeGrowthRate = populationSizeGrowthRate;
                config.MaxPopulationSize = maxPopulationSize;
                config.OffspringRate = offspringRate;
                config.MutationProbability = mutationProbability;
                config.MaxMutationProbability = maxMutationProbability;
                config.ElitismRate = elitismRate;
                config.TournamentSize = tournamentSize;
                config.MaxElitismRate = maxElitism;
                config.MaxTournamentRate = maxTournament;
                config.RestartGenerations = restartGenerations;

                config.AdaptMutationProbability = adaptMutationProbability;
                config.AdaptTournamentSize = adaptTournamentSize;
                config.AdaptElitismRate = adaptElitismRate;
                //config.AdaptRates = adaptRates;
                config.DoRestarts = doRestarts;

                GA ga = new GA(config, true, encoding.Durations, recombinationMethod: recombinationMethod, mutationMethod: mutationMethod, mutationRateChangeMethod: mutationGrowthMethod);
                ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]);
                History gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, keepMultiple);

                gaResult.Name = experimentName;
                string filename = outPath + gaResult.Name + ".json";
                gaResult.ToFile(filename);
                if(iteration == 0)
                {
                    PrepareFile(filename);
                }
                if(iteration != nExperiments)
                {
                    DelimitRun(filename);
                } else
                {
                    EndFile(filename);
                }
            } catch (Exception e)
            {
                Console.WriteLine("Error during input parsing or GA execution: " + e.Message);
            }

        }
    }
}
