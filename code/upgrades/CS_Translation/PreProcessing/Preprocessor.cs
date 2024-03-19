using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PreProcessing
{
    public class Preprocessor
    {

        public Preprocessor() { }

        public void Process(int[,] durations, int[] jobSequence)
        {
            int nOperations = durations.GetLength(0);
            int nMachines = durations.GetLength(1);
            int nJobs = jobSequence.ToHashSet<int>().Count;
            float flexibility;
            float durationVariety;
            float averageMachinesPerOperation;
            float averageOperationsPerMachine;
            int nPossibleCombinations = 0;
            int[] onMachine = new int[nMachines];
            HashSet<int> durationSet = new HashSet<int>();
            for(int i = 0; i < durations.GetLength(0); ++i) 
            { 
                for(int j = 0; j < durations.GetLength(1); ++j)
                {
                    if (durations[i, j] > 0)
                    {
                        ++nPossibleCombinations;
                        ++onMachine[j];
                        durationSet.Add(durations[i, j]);
                    }
                }
            }

            float averageOperationsPerJob = (nOperations + 0.0f)/ nJobs;
            averageOperationsPerMachine = (onMachine.Sum() + 0.0f) / onMachine.Length;
            averageMachinesPerOperation = nPossibleCombinations / nOperations;
            int nUniqueDurations = durationSet.Count;
            durationVariety = (nUniqueDurations + 0.0f) / nPossibleCombinations;
            flexibility = (averageMachinesPerOperation + 0.0f) / nMachines;
            
        }
    }
}
