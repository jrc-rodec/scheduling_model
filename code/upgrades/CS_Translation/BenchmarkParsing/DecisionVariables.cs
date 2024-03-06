using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BenchmarkParsing
{
    public class DecisionVariables
    {
        private readonly float _flexibility;
        private readonly float _averageMachines;
        private readonly float _durationVariety;
        private readonly float _averageOperations;
        private readonly float _averageOperationsOnMachines;
        private Encoding _encoding;
        // ...

        public DecisionVariables(Encoding encoding)
        {
            _encoding = encoding;
            float _averageMachines = 0.0f;
            List<int> uniqueDurations = new List<int>();
            int overallOptions = 0;
            int[] onMachines = new int[encoding.NMachines];
            for(int i = 0; i < encoding.Durations.GetLength(0); ++i)
            {
                int machineCount = 0;
                for(int j = 0; j < encoding.Durations.GetLength(1); ++j)
                {
                    if(encoding.Durations[i, j] > 0)
                    {
                        if(!uniqueDurations.Contains(encoding.Durations[i, j]))
                        {
                            uniqueDurations.Add(encoding.Durations[i, j]);
                        }
                        ++onMachines[j];
                        ++overallOptions;
                        ++machineCount;
                    }
                }
                _averageMachines += machineCount;
            }
            _averageMachines /= encoding.NOperations;
            _flexibility = _averageMachines / encoding.NMachines;
            _durationVariety = (uniqueDurations.Count + 0.0f) / (overallOptions + 0.0f);
            _averageOperations = (encoding.NOperations + 0.0f) / (encoding.NJobs + 0.0f);
            _averageOperationsOnMachines = 0;
            for(int i = 0; i < onMachines.Length; ++i)
            {
                _averageOperationsOnMachines += onMachines[i];
            }
            _averageOperationsOnMachines /= onMachines.Length;
        }

        /*
            In: Operation ID (0-indexed)
            Out: Average Duration on machines eligible to process the operation
         */
        public float AverageDurationOfOperation(int operation)
        {
            int options = 0;
            float averageDuration = 0.0f;
            for(int i = 0; i < _encoding.Durations.GetLength(1); ++i)
            {
                if (_encoding.Durations[operation, i] > 0)
                {
                    averageDuration += _encoding.Durations[operation, i];
                    ++options;
                }
            }
            return averageDuration / options;
        }

        /*
            In: Machine ID (0-indexed)
            Out: Average Duration for Operations eligible for processing on the machine
         */
        public float AverageDurationOnMachine(int machine)
        {
            int count = 0;
            float averageDuration = 0.0f;
            for(int i = 0; i < _encoding.Durations.GetLength(0); ++i)
            {
                if(_encoding.Durations[i, machine] > 0)
                {
                    averageDuration += _encoding.Durations[i, machine];
                    ++count;
                }
            }
            return averageDuration / count;
        }

        public float Flexibility => _flexibility;
        public float AverageMachines => _averageMachines;
        public float DurationVariety => _durationVariety;
        public int NOperations => _encoding.NOperations;
        public int NMachines => _encoding.NMachines;
        public int NJobs => _encoding.NJobs;
        public float AverageOperations => _averageOperations;
        public float AverageOperationsOnMachines => _averageOperationsOnMachines;
    }
}
