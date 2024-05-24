using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BenchmarkParsing
{

    public class Program
    {

        public static void Main(string[] args)
        {
            // Testing
            string path = "C:\\Users\\dhutt\\Desktop\\SCHEDULING_MODEL\\code\\upgrades\\code\\benchmarks\\6_Fattahi\\Fattahi20.fjs";
            BenchmarkParser parser = new BenchmarkParser();
            Encoding result = parser.ParseBenchmark(path);
            for(int i = 0; i < result.Durations.GetLength(0); ++i)
            {
                for (int j = 0; j < result.Durations.GetLength(1); ++j)
                {
                    Console.Write(result.Durations[i,j] + ",");
                }
                Console.WriteLine();
            }
            Console.WriteLine(result.NJobs);
            Console.WriteLine(result.NMachines);
            Console.WriteLine(result.NOperations);
        }
    }
}
