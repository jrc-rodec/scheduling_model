using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BenchmarkParsing
{
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
            string[][] lines = new string[fileContent.Count - 1][];
            for (int i = 1; i < fileContent.Count; ++i)
            {
                string[] line = fileContent[i].Split(' ');
                lines[i - 1] = line;
                nOverallOperations += Int32.Parse(line[0]);
            }
            int[,] durations = new int[nOverallOperations, nMachines];
            int operationIndex = 0;
            int[] jobSequence = new int[nOverallOperations];
            for (int i = 1; i < lines.Length+1; ++i)
            {
                //string[] line = fileContent[i].Split(' ');
                string[] line = lines[i-1];
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

        public class WorkerBenchmarkParser
        {
            public WorkerEncoding ParseBenchmark(string path)
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
                int nWorkers;
                Int32.TryParse(info[2], out nWorkers);
                int nOverallOperations = 0;
                string[][] lines = new string[fileContent.Count - 1][];
                for (int i = 1; i < fileContent.Count; ++i)
                {
                    string[] line = fileContent[i].Split(' ');
                    lines[i - 1] = line;
                    nOverallOperations += Int32.Parse(line[0]);
                }
                int[,,] durations = new int[nOverallOperations, nMachines, nWorkers];
                int operationIndex = 0;
                int[] jobSequence = new int[nOverallOperations];
                for (int i = 1; i < lines.Length +1; ++i)
                {
                    string[] line = lines[i - 1];
                    int nOperations;
                    Int32.TryParse(line[0], out nOperations);
                    int index = 1;
                    for (int j = 0; j < nOperations; ++j)
                    {
                        jobSequence[operationIndex] = i - 1; // NOTE: switching benchmark input to 0 indexing
                        int nMachineOptions;
                        Int32.TryParse(line[index++], out nMachineOptions);
                        for (int k = 0; k < nMachineOptions; ++k)
                        {
                            int machine;
                            Int32.TryParse(line[index++], out machine);
                            int nWorkerOptions;
                            Int32.TryParse(line[index++], out nWorkerOptions);
                            for(int l = 0; l < nWorkerOptions; ++l)
                            {
                                int worker;
                                Int32.TryParse(line[index++], out worker);
                                int duration;
                                Int32.TryParse(line[index++], out duration);
                                durations[operationIndex, machine - 1, worker-1] = duration; // NOTE: switching benchmark input to 0 indexing
                            }
                        }
                        ++operationIndex;
                    }
                }
                return new WorkerEncoding(durations, jobSequence);
            }
        }
    }
}
