using BenchmarkParsing;

namespace Solver
{
    internal class Program
    {
        static void Main(string[] args)
        {
            string path = "C:\\Users\\huda\\Documents\\GitHub\\scheduling_model\\code\\upgrades\\code\\benchmarks\\1_Brandimarte\\BrandimarteMk15.fjs"; // DEBUG
            int maxGenerations = 0;
            int timeLimit = 3600; // in seconds
            float targetFitness = 0;
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
            if (!(criteriaStatus[0] && criteriaStatus[1] && criteriaStatus[2] && criteriaStatus[3]))
            {
                Console.WriteLine("No valid stopping criteria was set!");
                return;
            }
            BenchmarkParser parser = new BenchmarkParser();
            Encoding result = parser.ParseBenchmark(path);
            DecisionVariables variables = new DecisionVariables(result);
            GAConfiguration configuration = new GAConfiguration(result, variables);
            GA ga = new GA(configuration);
            ga.SetStoppingCriteriaStatus(criteriaStatus[0], criteriaStatus[1], criteriaStatus[3], criteriaStatus[2]); // TODO: change signature parameter order
            List<Individual> best = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
            Console.WriteLine(best[0].Fitness[Criteria.Makespan]);
            Console.ReadLine();
        }
    }
}
