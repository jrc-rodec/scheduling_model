using BenchmarkParsing;

namespace Solver
{
    internal class Program
    {
        static void Main(string[] args)
        {
            string path = "C:\\Users\\dhutt\\Desktop\\SCHEDULING_MODEL\\code\\upgrades\\code\\benchmarks\\6_Fattahi\\Fattahi20.fjs";
            BenchmarkParser parser = new BenchmarkParser();
            Encoding result = parser.ParseBenchmark(path);
            DecisionVariables variables = new DecisionVariables(result);
            GAConfiguration configuration = new GAConfiguration(result, variables);
            GA ga = new GA(configuration);
            List<Individual> best = ga.Run(100, 300, 0, 10000);
            Console.WriteLine(best[0].Fitness[Criteria.Makespan]);
        }
    }
}
