using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GA_Uncertainty
{
    internal class Adjustment
    {
        private static bool WorkerAvailable(Dictionary<string, int> gap, int operation, int operationIndex, Individual individual, int index, int[] operationEndTimes, GAConfiguration configuration)
        {
            int machine = individual.Assignments[operationIndex];

            int worker = individual.Workers[operationIndex];

            int duration = configuration.Durations[operation, machine, worker];
            int[] nextOperation = new int[configuration.NJobs];
            for (int i = 0; i < index; i++)
            {
                int opId = configuration.JobStartIndices[configuration.JobSequence[i]] + nextOperation[configuration.JobSequence[i]]++;
                if (individual.Workers[opId] == worker)
                {
                    int end = operationEndTimes[opId];
                    int d = configuration.Durations[opId, individual.Assignments[opId], individual.Workers[opId]];
                    int start = end - d;
                    if ((gap["start"] >= start && gap["start"] <= end) || (gap["end"] >= start && gap["end"] <= end) || (start >= gap["start"] && start <= gap["end"]) || (end >= gap["start"] && end <= gap["end"]))
                    {
                        return false;
                    }
                }
            }
            return true;
        }

        public static Individual Adjust(Individual nIndividual, GAConfiguration configuration)
        {

            Individual individual = nIndividual.DeepCopy();
            List<List<Dictionary<string, int>>> gaps = new List<List<Dictionary<string, int>>>();
            for (int i = 0; i < configuration.NMachines; ++i)
            {
                gaps.Add(new List<Dictionary<string, int>>());
            }
            int[] endTimesOnMachines = new int[configuration.NMachines];
            int[] endTimesOfOperations = new int[configuration.NOperations];

            int[] endTimesOfWorkers = new int[configuration.Durations.GetLength(2)]; // should be N workers

            int[] nextOperation = new int[configuration.NJobs];

            for (int i = 0; i < individual.Sequence.Length; ++i)
            {
                int job = configuration.JobSequence[i];
                int operation = nextOperation[job]++;
                int operationIndex = configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[operationIndex];

                int worker = individual.Workers[operationIndex];

                int duration = configuration.Durations[operation, machine, worker];

                bool inserted = false;
                for (int j = 0; j < gaps[machine].Count; ++j)
                {
                    Dictionary<string, int> gap = gaps[machine][j];
                    if (gap["end"] - gap["start"] >= duration)
                    {
                        if (operationIndex == 0 || configuration.JobSequence[operationIndex - 1] == configuration.JobSequence[operationIndex]
                            && endTimesOfOperations[operationIndex - 1] <= gap["end"] - duration && WorkerAvailable(gap, operation, operationIndex, individual, i, endTimesOfOperations, configuration))
                        {
                            // gap can be used
                            inserted = true;
                            int start = 0;
                            if (operationIndex != 0)
                            {
                                start = Math.Min(gap["start"], endTimesOfOperations[operationIndex - 1]);
                            }
                            int end = start + duration;
                            if (gap["end"] - end > 0)
                            {
                                Dictionary<string, int> newGap = new Dictionary<string, int>();
                                newGap["start"] = end;
                                newGap["end"] = gap["end"];
                                newGap["preceedsOperation"] = operationIndex;
                                gaps[machine].Add(newGap);
                            }
                            endTimesOfOperations[operationIndex] = end;
                            int jobSwap = configuration.JobSequence[gap["preceedsOperation"]];
                            int swapOperationIndex = 0;
                            int swapStartIndex = 0;
                            bool found = false;
                            for (int k = 0; k < configuration.JobSequence.Length && !found; ++k)
                            {
                                if (configuration.JobSequence[k] == jobSwap)
                                {
                                    swapStartIndex = k;
                                    found = true;
                                }
                            }
                            swapOperationIndex = gap["preceedsOperation"] - swapStartIndex;
                            int count = 0;
                            int swapIndividualIndex = 0;
                            found = false;
                            for (int k = 0; k < individual.Sequence.Length && !found; ++k)
                            {
                                if (individual.Sequence[k] == jobSwap)
                                {
                                    if (count == swapOperationIndex)
                                    {
                                        swapIndividualIndex = k;
                                        found = true;
                                    }
                                    ++count;
                                }
                            }
                            int tmp = individual.Sequence[swapIndividualIndex];
                            individual.Sequence[swapIndividualIndex] = individual.Sequence[i];
                            individual.Sequence[i] = tmp;
                            gaps[machine].Remove(gap);
                            break; // TODO: double check
                        }
                    }
                }
                if (!inserted)
                {
                    int jobMinStart = 0;
                    if (operationIndex != 0 && configuration.JobSequence[operationIndex - 1] == configuration.JobSequence[operationIndex])
                    {
                        jobMinStart = endTimesOfOperations[operationIndex - 1];
                    }
                    if (jobMinStart > endTimesOnMachines[machine])
                    {
                        gaps[machine].Add(new Dictionary<string, int>() { ["start"] = jobMinStart, ["end"] = jobMinStart + duration, ["preceedsOperation"] = operationIndex });
                        endTimesOnMachines[machine] = jobMinStart + duration;
                    }
                    else
                    {
                        endTimesOnMachines[machine] += duration;
                    }
                }
                endTimesOfOperations[operationIndex] = endTimesOnMachines[machine];
            }
            return individual;
        }
    }
}
