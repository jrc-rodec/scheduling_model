using BenchmarkParsing;
using System;
using System.Globalization;
using System.Security;
using System.Text.Json;
using System.Text.Json.Nodes;
using static BenchmarkParsing.BenchmarkParser;

namespace ReactionStrategy
{
    internal class Program
    {


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
            //Test();

            //try
            //{
            string inputString = args[0];
            FileStream stream = File.OpenRead(inputString);
            Dictionary<string, string> data = JsonSerializer.Deserialize<Dictionary<string, string>>(stream);
            //JsonNode data = JsonArray.Parse(inputString);
            string basepath = (string)data["path"];
            int maxGenerations = 0;//(int)int.Parse(data["maxGenerations"]);
            int timeLimit = 60;// (int)int.Parse(data["timeLimit"]);
            float targetFitness = 0.0f;// (float)float.Parse(data["targetFitness"]);
            int maxFunctionEvaluations = 0;// (int)int.Parse(data["maxFevals"]);

            bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0 };
            if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
            {
                Console.WriteLine("No valid stopping criteria was set!");
                return;
            }

            bool keepMultiple = false;// (bool)bool.Parse(data["keepMultiple"]);
            //string instance = (string)data["instanceName"];
            //string experimentName = (string)data["name"];

            string outPath = (string)data["outputPath"];
            int nExperiments = 1;// (int)int.Parse(data["nExperiments"]);

            //int iteration = int.Parse(args[1]);

            int populationSize = 5;// (int)int.Parse(data["populationSize"]);
            int offspringAmount = 20;// (int)int.Parse(data["offspringAmount"]);
            float populationSizeGrowthRate = 1.1f;// (float)float.Parse(data["populationGrowthRate"]);
            int maxPopulationSize = 100;// (int)int.Parse(data["maxPopulationSize"]);
            float offspringRate = 4.0f;//;(float)float.Parse(data["offspringRate"]);
            bool adaptMutationProbability = true;// (bool)bool.Parse(data["adaptMutationProbability"]);
            float maxMutationProbability = 1.0f;// (float)float.Parse(data["maxMutationProbability"]);
            float elitismRate = 0.1f;// (float)float.Parse(data["elitismRate"]);
            int tournamentSize = 2;// (int)int.Parse(data["tournamentSize"]);
            //bool adaptRates = (bool)data["adaptRates"];
            bool adaptTournamentSize = true;//(bool)bool.Parse(data["adaptTournamentSize"]);
            bool adaptElitismRate = true;// (bool)bool.Parse(data["adaptElitismRate"]);
            float maxElitism = 2;// (float)float.Parse(data["maxElitism"]);
            float maxTournament = 5;// (float)float.Parse(data["maxTournamentRate"]);
            bool doRestarts = true;// (bool)bool.Parse(data["doRestarts"]);
            int restartGenerations = 10;// (int)int.Parse(data["restartGenerations"]);

            string mutationMethod = "sr";// (string)data["mutationMethod"];
            string recombinationMethod = "u";// (string)data["recombinationMethod"];
            string mutationGrowthMethod = "s";// (string)data["mutationGrowthMethod"];

            string fixedIndices = (string)data["fixedIndices"];
            string[] fI = fixedIndices.Split(',');
            bool[] fixedOperations = new bool[fI.Length];
            int count = 0;
            for(int i = 0; i < fI.Length; i++)
            {
                fixedOperations[i] = fI[i].Contains("True");
                if (fixedOperations[i])
                {
                    count++;
                }
            }
            float mutationProbability = 1.0f / count;// (float)float.Parse(data["mutationProbability"]);
            string startSequence = (string)data["sequence"];
            string[] sS = startSequence.Split(",");
            string startAssignments = (string)data["assignments"];
            string[] sA = startAssignments.Split(",");
            string startWOrkers = (string)data["workers"];
            string[] sW = startWOrkers.Split(",");
            int[] sequence = new int[sS.Length];
            int[] assignments = new int[sA.Length];
            int[] workers = new int[sW.Length];
            for(int i = 0; i < sS.Length; i++)
            {
                sequence[i] = int.Parse(sS[i]);
                assignments[i] = int.Parse(sA[i]);
                workers[i] = int.Parse(sW[i]);
            }
            /*string machineStartBlocks = (string)data["machineBlocks"];
            string[] mSB = machineStartBlocks.Split(",");
            int[] machineBlocks = new int[mSB.Length];
            for(int i = 0; i < mSB.Length; i++)
            {
                machineBlocks[i] = int.Parse(mSB[i]);
            }
            string workerStartBlocks = (string)data["workerBlocks"];
            string[] wSB = workerStartBlocks.Split(",");
            int[] workerBlocks = new int[wSB.Length];
            for(int i = 0; i < wSB.Length; i++)
            {
                workerBlocks[i] = int.Parse(wSB[i]);
            }*/

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

            bool simulateUncertainty = true;// (bool)bool.Parse(data["simulateUncertainty"]);
            List<Tuple<float, float>> uncertaintyParameters = new List<Tuple<float, float>>();
            int nSimulations = 10;// (int)int.Parse(data["nSimulations"]);
            Random random = new Random();
            for (int i = 0; i < config.NWorkers; ++i)
            {
                float alpha = (float)random.NextDouble();
                float beta = 10.0f * alpha;
                Tuple<float, float> values = new Tuple<float, float>(alpha, beta);
                uncertaintyParameters.Add(values);
            }

            GA ga = new GA(config, sequence, assignments, workers,fixedOperations, count, true, encoding.Durations, recombinationMethod: recombinationMethod, mutationMethod: mutationMethod, mutationRateChangeMethod: mutationGrowthMethod, simulateUncertainty: simulateUncertainty, uncertaintyParameters: uncertaintyParameters, nSimulations: nSimulations);
            ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]);
            History gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, keepMultiple);
            File.AppendAllText(outPath, basepath + ";" + gaResult.OverallBestFitness[gaResult.OverallBestFitness.Count - 1] + ";" + gaResult.Result.Best[0].Sequence.ToString() + ";" + gaResult.Result.Best[0].Assignments.ToString() + ";" + gaResult.Result.Best[0].Workers.ToString() +"\n");
            /*gaResult.Name = experimentName;
            string filename = outPath + gaResult.Name + ".json";
            gaResult.ToFile(filename);
            if (iteration == 0)
            {
                PrepareFile(filename);
            }
            if (iteration != nExperiments)
            {
                DelimitRun(filename);
            }
            else
            {
                EndFile(filename);
            }*/
            //}
            //catch (Exception e)
            //{
            //    Console.WriteLine("Error during input parsing or GA execution: " + e.Message);
            //}

        }
    }
}
