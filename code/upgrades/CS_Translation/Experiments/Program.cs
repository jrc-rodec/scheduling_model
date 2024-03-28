using BenchmarkParsing;
using Solver;

namespace Experiments
{
    public class Program
    {

        static string GetPath(string source, int instance)
        {
            string basePath = "C:\\Users\\huda\\Documents\\GitHub\\scheduling_model\\code\\upgrades\\code\\benchmarks\\";
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

        static void Main(string[] args)
        {
            //TODO: for ALL instances
            string path = "C:\\Users\\huda\\Documents\\GitHub\\scheduling_model\\code\\upgrades\\code\\benchmarks\\6_Fattahi\\Fattahi18.fjs"; // DEBUG
            int maxGenerations = 0;
            int timeLimit = 3600; // in seconds

            // TODO: read best found results with python GA version
            float targetFitness = 1000.0f;//884.0f;
            int maxFunctionEvaluations = 0;

            bool[] criteriaStatus = { maxGenerations > 0, timeLimit > 0, targetFitness > 0.0f, maxFunctionEvaluations > 0 };
            if (!(criteriaStatus[0] || criteriaStatus[1] || criteriaStatus[2] || criteriaStatus[3]))
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
            History gaResult = ga.Run(maxGenerations, timeLimit, targetFitness, maxFunctionEvaluations);
            gaResult.ToFile("test.json");
        }
    }
}
