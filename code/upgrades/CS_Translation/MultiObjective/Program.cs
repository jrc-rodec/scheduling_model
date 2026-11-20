using BenchmarkParsing;
using System.Text.Json;
using static BenchmarkParsing.BenchmarkParser;

namespace MultiObjective
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
            //string inputString = args[0];
            //FileStream stream = File.OpenRead(inputString);
            //Dictionary<string, string> data = JsonSerializer.Deserialize<Dictionary<string, string>>(stream);
            //JsonNode data = JsonArray.Parse(inputString);
            string basepath = args[1];// "C:\\Users\\huda\\Documents\\GitHub\\FJSSP-W-Benchmarking\\instances\\Example_Instances_FJSSP-WF\\Fattahi14.fjs";// (string)data["path"];
            int maxGenerations = 0;// (int)int.Parse(data["maxGenerations"]);
            int timeLimit = 0;// (int)int.Parse(data["timeLimit"]);
            float targetFitness = 0.0f;// (float)float.Parse(data["targetFitness"]);
            int maxFunctionEvaluations = 5000000;// (int)int.Parse(data["maxFevals"]);

            bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0 };
            if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
            {
                Console.WriteLine("No valid stopping criteria was set!");
                return;
            }

            bool keepMultiple = true;// (bool)bool.Parse(data["keepMultiple"]);
            string instance = basepath.Split('\\')[^1].Split('.')[0];// (string)data["instanceName"];
            string experimentName = instance + args[0];// (string)data["name"];

            string outPath = "C:\\Users\\huda\\Desktop\\MOFJSSP\\results\\";// (string)data["outputPath"];
            int nExperiments = 1;// (int)int.Parse(data["nExperiments"]);

            int iteration = (int)int.Parse(args[0]);// int.Parse(args[1]);

            int populationSize = 5;// (int)int.Parse(data["populationSize"]);
            int offspringAmount = 20;// (int)int.Parse(data["offspringAmount"]);
            float populationSizeGrowthRate = 1.1f;// (float)float.Parse(data["populationGrowthRate"]);
            int maxPopulationSize = 100;// (int)int.Parse(data["maxPopulationSize"]);
            float offspringRate = 4;// (float)float.Parse(data["offspringRate"]);
            float mutationProbability = 0.1f;// (float)float.Parse(data["mutationProbability"]);
            bool adaptMutationProbability = true;// (bool)bool.Parse(data["adaptMutationProbability"]);
            float maxMutationProbability = 1.0f;// (float)float.Parse(data["maxMutationProbability"]);
            float elitismRate = 0.1f;// (float)float.Parse(data["elitismRate"]);
            int tournamentSize = 2;// (int)int.Parse(data["tournamentSize"]);
            //bool adaptRates = (bool)data["adaptRates"];
            bool adaptTournamentSize = true;// (bool)bool.Parse(data["adaptTournamentSize"]);
            bool adaptElitismRate = false;// (bool)bool.Parse(data["adaptElitismRate"]);
            float maxElitism = 0.1f;// (float)float.Parse(data["maxElitism"]);
            float maxTournament = 0.2f;// (float)float.Parse(data["maxTournamentRate"]);
            bool doRestarts = true;// true;// (bool)bool.Parse(data["doRestarts"]);
            int restartGenerations = 10;// (int)int.Parse(data["restartGenerations"]);

            string mutationMethod = "sr";//;(string)data["mutationMethod"];
            string recombinationMethod = "u";// (string)data["recombinationMethod"];
            string mutationGrowthMethod = "s";// (string)data["mutationGrowthMethod"];

            GA.SORT = true;
            WorkerBenchmarkParser parser = new WorkerBenchmarkParser();
            WorkerEncoding encoding = parser.ParseBenchmark(basepath);
            WorkerDecisionVariables variables = new WorkerDecisionVariables(encoding);
            mutationProbability = 1.0f / (3.0f* encoding.NOperations);
            
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
            List<Criteria> evaluationCriteria = new List<Criteria>();
            evaluationCriteria.Add(Criteria.Makespan);
            evaluationCriteria.Add(Criteria.OriginalMakespan);
            evaluationCriteria.Add(Criteria.IdleTime);
            
            GA ga = new GA(config, true, encoding.Durations, recombinationMethod: recombinationMethod, mutationMethod: mutationMethod, mutationRateChangeMethod: mutationGrowthMethod, simulateUncertainty: simulateUncertainty, uncertaintyParameters: uncertaintyParameters, nSimulations: nSimulations, evaluationCriteria: evaluationCriteria);
            ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]);
            History gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations, keepMultiple);

            gaResult.Name = experimentName;
            string filename = outPath + instance + ".json";
            
            //if (iteration == 0)
            //{
            //    PrepareFile(filename);
            //}
            gaResult.ToFile(filename);
            if (iteration != nExperiments)
            {
                DelimitRun(filename);
            }
            //else
            //{
            //    EndFile(filename);
            //}
        }
    }
}
