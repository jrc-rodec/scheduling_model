using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BenchmarkParsing
{

    public class Encoding
    {
        private readonly int[,] _durations;
        private readonly int[] _jobSequence;
        private readonly int _nJobs;

        public Encoding(int[,] durations, int[] jobSequence)
        {
            _durations = durations;
            _jobSequence = jobSequence;
            _nJobs = 1;
            for(int i = 1; i < _jobSequence.Length; ++i)
            {
                if(_jobSequence[i] != _jobSequence[i - 1])
                {
                    ++_nJobs;
                }
            }
        }

        public int[] JobSequence { get => _jobSequence;}
        public int[,] Durations { get => _durations;}

        public int NOperations => _durations.GetLength(0);
        public int NMachines => _durations.GetLength(1);

        public int NJobs => _nJobs;

        public List<int> GetMachinesForOperation(int operationIndex)
        {
            List<int> machines = new List<int>();
            for (int i = 0; i < _durations.GetLength(1); ++i)
            {
                if (_durations[operationIndex, i] > 0)
                {
                    machines.Add(i);
                }
            }
            return machines;
        }

        public List<List<int>> GetMachinesForAllOperations()
        {
            List<List<int>> machines = new List<List<int>>();
            for(int i = 0; i < _durations.GetLength(0); ++i)
            {
                machines.Add(new List<int>());
                for(int j = 0; j < _durations.GetLength(1); ++j)
                {
                    if(_durations[i, j] > 0)
                    {
                        machines[i].Add(j);
                    }
                }
            }
            return machines;
        }
    }

    public class BenchmarkParser
    {
        public BenchmarkParser()
        {

        }

        public Encoding ParseBenchmark(string path)
        {
            List<string> fileContent = new List<string>();
            try
            {
                StreamReader sr = new StreamReader(path);
                string line = sr.ReadLine();
                while (line != null)
                {
                    fileContent.Add(line);
                    line = sr.ReadLine();
                }
                sr.Close();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
            string[] info = fileContent[0].Split(' ');

            int nMachines;
            Int32.TryParse(info[1], out nMachines);
            int nOverallOperations = 0;
            for (int i = 1; i < fileContent.Count; ++i)
            {
                nOverallOperations += Int32.Parse(fileContent[i].Split(' ')[0]);
            }
            int[,] durations = new int[nOverallOperations, nMachines];
            int operationIndex = 0;
            int[] jobSequence = new int[nOverallOperations];
            for (int i = 1; i < fileContent.Count; ++i)
            {
                string[] line = fileContent[i].Split(' ');
                int nOperations;
                Int32.TryParse(line[0], out nOperations);
                int index = 1;
                for (int j = 0; j < nOperations; ++j)
                {
                    jobSequence[operationIndex] = i - 1; // NOTE: switching benchmark input to 0 indexing
                    int nOptions;
                    Int32.TryParse(line[index++], out nOptions);
                    for (int k = 0; k < nOptions; ++k)
                    {
                        int machine;
                        Int32.TryParse(line[index++], out machine);
                        int duration;
                        Int32.TryParse(line[index++], out duration);
                        durations[operationIndex, machine - 1] = duration; // NOTE: switching benchmark input to 0 indexing
                    }
                    ++operationIndex;
                }
            }
            return new Encoding(durations, jobSequence);
        }
    }

    public class Program
    {

        public static void Main(string[] args)
        {
            // Testing
            string path = "C:\\Users\\huda\\Documents\\GitHub\\scheduling_model\\code\\upgrades\\code\\benchmarks\\6_Fattahi\\Fattahi20.fjs";
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
