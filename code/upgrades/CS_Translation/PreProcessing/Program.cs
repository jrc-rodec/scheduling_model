using BenchmarkParsing;

namespace PreProcessing
{
    internal class Program
    {
        static void Main(string[] args)
        {
            string path = "C:\\Users\\dhutt\\Desktop\\SCHEDULING_MODEL\\code\\upgrades\\code\\benchmarks\\6_Fattahi\\Fattahi20.fjs";
            BenchmarkParser parser = new BenchmarkParser();
            Encoding result = parser.ParseBenchmark(path);
            DecisionVariables variables = new DecisionVariables(result);
            Console.WriteLine(variables.ToString());
        }
    }
}
