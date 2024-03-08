using BenchmarkParsing;

namespace Solver
{
    internal class Program
    {
        static void Main(string[] args)
        {
            /*string path = "C:\\Users\\dhutt\\Desktop\\SCHEDULING_MODEL\\code\\upgrades\\code\\benchmarks\\6_Fattahi\\Fattahi20.fjs";
            BenchmarkParser parser = new BenchmarkParser();
            Encoding result = parser.ParseBenchmark(path);
            DecisionVariables variables = new DecisionVariables(result);*/

            // Testing
            int[] values = { 0, 0, 1, 1, 3, 3, 3, 2, 2, 1, 5, 4 };
            HashSet<int> jobs = new HashSet<int>(values); // I hope this does what I think

            for(int i = 0; i < jobs.Count; ++i)
            {
                Console.WriteLine(jobs.ElementAt(i));

            }
        }
    }
}
