using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BenchmarkParsing
{
    public class Encoding
    {
        private int[,] _durations;
        private readonly int[] _jobSequence;
        private readonly int _nJobs;

        public Encoding(int[,] durations, int[] jobSequence)
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

        public int[] JobSequence { get => _jobSequence; }

        public int NOperations => _durations.GetLength(0);
        public int NMachines => _durations.GetLength(1);

        public int NJobs => _nJobs;

        public int[,] Durations { get => _durations; set => _durations = value; }

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
            for (int i = 0; i < _durations.GetLength(0); ++i)
            {
                machines.Add(new List<int>());
                for (int j = 0; j < _durations.GetLength(1); ++j)
                {
                    if (_durations[i, j] > 0)
                    {
                        machines[i].Add(j);
                    }
                }
            }
            return machines;
        }

        public Encoding Copy()
        {
            return new Encoding(_durations, _jobSequence);
        }

        public Encoding DeepCopy()
        {
            int[,] durationCopy = new int[_durations.GetLength(0), _durations.GetLength(1)];
            for(int i = 0; i < _durations.GetLength(0); ++i)
            {
                for(int j = 0; j< _durations.GetLength(1); ++j)
                {
                    durationCopy[i, j] = _durations[i, j];
                }
            }
            int[] jobSequenceCopy = new int[_jobSequence.Length];
            for(int i = 0; i < _jobSequence.Length; ++i)
            {
                jobSequenceCopy[i] = _jobSequence[i];
            }
            return new Encoding(durationCopy, jobSequenceCopy);
        }
    }

    public class WorkerEncoding
    {
        private int[,,] _durations; 
        private readonly int[] _jobSequence;
        private readonly int _nJobs;

        public int[,,] Durations { get => _durations; set => _durations = value; }

        public int[] JobSequence => _jobSequence;

        public int NJobs => _nJobs;

        public WorkerEncoding(int[,,] durations, int[] jobSequence)
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
                for(int j = 0; j < _durations.GetLength(2); ++j)
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
                        // at least one worker is available, so stop here
                        workers.Add(i);
                    }
                }
            }
            return workers;
        }

        public List<List<int>> GetAllMachinesForAllOperations()
        {
            List<List<int>> operations = new List<List<int>>();
            for(int i = 0; i < _durations.GetLength(0); ++i)
            {
                List<int> machines = new List<int>();
                for(int j = 0; j < _durations.GetLength(1); ++j)
                {
                    for(int k = 0; k < _durations.GetLength(2); ++k)
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
            int[,,] durationCopy = new int[_durations.GetLength(0), _durations.GetLength(1), _durations.GetLength(2)];
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
}
