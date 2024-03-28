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
            float[] averageDurations = new float[nOperations];
            float[] averageDurationsOnMachines = new float[nMachines];
            float[] averageAlternatives = new float[nMachines];
            for(int i = 0; i < durations.GetLength(0); ++i) 
            {
                float averageDuration = 0.0f;
                int possibleMachines = 0;
                for(int j = 0; j < durations.GetLength(1); ++j)
                {
                    if (durations[i, j] > 0)
                    {
                        ++nPossibleCombinations;
                        ++onMachine[j];
                        averageDurationsOnMachines[j] += durations[i, j];
                        durationSet.Add(durations[i, j]);
                        averageDuration += durations[i, j];
                        ++possibleMachines;
                    }
                }
                averageDurations[i] = averageDuration / possibleMachines;
            }

            for(int i = 0; i < nMachines; ++i)
            {
                averageDurationsOnMachines[i] /= onMachine[i];
                for(int j = 0; j < jobSequence.Length; ++j)
                {
                    if (durations[j, i] > 0)
                    {
                        int alternatives = 0;
                        for(int k = 0; k < durations.GetLength(1); ++k)
                        {
                            if (durations[j, k] > 0)
                            {
                                ++alternatives;
                            }
                        }
                        averageAlternatives[i] = alternatives;
                    }
                }
                averageAlternatives[i] /= onMachine[i];
            }
            float averageOperationsPerJob = (nOperations + 0.0f)/ nJobs;
            averageOperationsPerMachine = (onMachine.Sum() + 0.0f) / onMachine.Length;
            averageMachinesPerOperation = nPossibleCombinations / nOperations;
            int nUniqueDurations = durationSet.Count;
            durationVariety = (nUniqueDurations + 0.0f) / nPossibleCombinations;
            flexibility = (averageMachinesPerOperation + 0.0f) / nMachines;
            /*for(int i = 0; i < durations.GetLength(0); ++i)
            {
                for(int j = 0; j < durations.GetLength(1); ++j)
                {
                    if (durations[i, j] > 0)
                    {
                        for(int k = 0; k < durations.GetLength(0); ++k)
                        {
                            // count amount of jobs on this machine

                        }
                    }
                }
            }*/
        }
    }
}
