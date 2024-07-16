using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static BenchmarkParsing.BenchmarkParser;

namespace BenchmarkParsing
{

    public class Program
    {

        public static void Main(string[] args)
        {
            // Testing
            string path = "C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model\\code\\reworked_data_model\\benchmarks_with_workers\\0_BehnkeGeiger_1_workers.fjs";
            //BenchmarkParser parser = new BenchmarkParser();
            WorkerBenchmarkParser parser = new WorkerBenchmarkParser();
            WorkerEncoding result = parser.ParseBenchmark(path);
            for(int i = 0; i < result.Durations.GetLength(0); ++i)
            {
                for (int j = 0; j < result.Durations.GetLength(1); ++j)
                {
                    Console.Write(result.Durations[i,j, 0] + ",");
                }
                Console.WriteLine();
            }
            Console.WriteLine(result.NJobs);
            Console.WriteLine(result.NMachines);
            Console.WriteLine(result.NOperations);
        }
    }
}
