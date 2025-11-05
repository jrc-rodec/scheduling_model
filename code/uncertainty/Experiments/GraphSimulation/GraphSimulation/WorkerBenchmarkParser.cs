using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GraphSimulation
{

    public class WorkerEncoding
    {
        private float[,,] _durations;
        private readonly int[] _jobSequence;
        private readonly int _nJobs;

        public float[,,] Durations { get => _durations; set => _durations = value; }
        public int[] JobSequence { get => _jobSequence; }

        public int NOperations => _durations.GetLength(0);
        public int NMachines => _durations.GetLength(1);

        public int NJobs => _nJobs;
        public int NWorkers => _durations.GetLength(2);

        public WorkerEncoding(float[,,] durations, int[] jobSequence)
        {
            _durations = durations;
            _jobSequence = jobSequence;
            _nJobs = 1;
            for (int i = 1; i < _jobSequence.Length; ++i)
            {
                if (_jobSequence[i] != _jobSequence[i - 1])
                {
                    ++_nJobs;
                }
            }
        }

        public List<int> GetMachinesForOperation(int operation)
        {
            List<int> machines = new List<int>();
            for (int i = 0; i < _durations.GetLength(1); ++i)
            {
                for (int j = 0; j < _durations.GetLength(2); ++j)
                {
                    if (_durations[operation, i, j] > 0)
                    {
                        // at least one worker is available, so stop here
                        machines.Add(i);
                        break;
                    }
                }
            }
            return machines;
        }

        public List<int> GetWorkersForOperation(int operation)
        {
            List<int> workers = new List<int>();
            for (int i = 0; i < _durations.GetLength(1); ++i)
            {
                for (int j = 0; j < _durations.GetLength(2); ++j)
                {
                    if (_durations[operation, i, j] > 0)
                    {
                        workers.Add(j);
                    }
                }
            }
            return workers;
        }

        public List<List<List<int>>> GetAllWorkersForAllOperations()
        {
            List<List<List<int>>> result = new List<List<List<int>>>();
            for (int i = 0; i < _durations.GetLength(0); ++i)
            {
                List<List<int>> machinesWorkers = new List<List<int>>();
                for (int j = 0; j < _durations.GetLength(1); ++j)
                {
                    List<int> workers = new List<int>();
                    for (int k = 0; k < _durations.GetLength(2); ++k)
                    {
                        if (_durations[i, j, k] > 0)
                        {
                            workers.Add(k);
                        }
                    }
                    machinesWorkers.Add(workers);
                }
                result.Add(machinesWorkers);
            }
            return result;
        }

        public List<List<int>> GetAllMachinesForAllOperations()
        {
            List<List<int>> operations = new List<List<int>>();
            for (int i = 0; i < _durations.GetLength(0); ++i)
            {
                List<int> machines = new List<int>();
                for (int j = 0; j < _durations.GetLength(1); ++j)
                {
                    for (int k = 0; k < _durations.GetLength(2); ++k)
                    {
                        if (_durations[i, j, k] > 0)
                        {
                            machines.Add(j);
                            break;
                        }
                    }
                }
                operations.Add(machines);
            }
            return operations;
        }

        public List<int> GetWorkersForOperationOnMachine(int operation, int machine)
        {
            List<int> workers = new List<int>();
            for (int j = 0; j < _durations.GetLength(2); ++j)
            {
                if (_durations[operation, machine, j] > 0)
                {
                    workers.Add(j);
                }
            }
            return workers;
        }

        public bool IsPossible(int operation, int machine, int worker)
        {
            return _durations[operation, machine, worker] > 0;
        }

        public WorkerEncoding Copy()
        {
            return new WorkerEncoding(_durations, _jobSequence);
        }

        public WorkerEncoding DeepCopy()
        {
            float[,,] durationCopy = new float[_durations.GetLength(0), _durations.GetLength(1), _durations.GetLength(2)];
            for (int i = 0; i < _durations.GetLength(0); ++i)
            {
                for (int j = 0; j < _durations.GetLength(1); ++j)
                {
                    for (int k = 0; k < _durations.GetLength(2); ++k)
                    {
                        durationCopy[i, j, k] = _durations[i, j, k];
                    }
                }
            }
            int[] jobSequenceCopy = new int[_jobSequence.Length];
            for (int i = 0; i < _jobSequence.Length; ++i)
            {
                jobSequenceCopy[i] = _jobSequence[i];
            }
            return new WorkerEncoding(durationCopy, jobSequenceCopy);
        }


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
            float[,,] durations = new float[nOverallOperations, nMachines, nWorkers];
            int operationIndex = 0;
            int[] jobSequence = new int[nOverallOperations];
            for (int i = 1; i < lines.Length + 1; ++i)
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
                        for (int l = 0; l < nWorkerOptions; ++l)
                        {
                            int worker;
                            Int32.TryParse(line[index++], out worker);
                            float duration;
                            float.TryParse(line[index++], out duration);
                            durations[operationIndex, machine - 1, worker - 1] = duration; // NOTE: switching benchmark input to 0 indexing
                        }
                    }
                    ++operationIndex;
                }
            }
            return new WorkerEncoding(durations, jobSequence);
        }
    }
}
