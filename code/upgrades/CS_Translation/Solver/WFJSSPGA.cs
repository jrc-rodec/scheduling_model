using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Solver
{
    public class WFJSSPGA : GA
    {
        private int[,,] _workerDurations;

        public WFJSSPGA(GAConfiguration configuration, bool output, int[,,] workerDurations) : base(configuration, output)
        {
            _workerDurations = workerDurations;
            List<List<List<int>>> availableWorkers = new List<List<List<int>>>();
            for(int operation = 0; operation < _workerDurations.GetLength(0); ++operation)
            {
                List<List<int>> operationWorkers = new List<List<int>>();
                for(int machine = 0; machine < _workerDurations.GetLength(1); ++machine)
                {
                    List<int> machineWorkers = new List<int>();
                    for(int worker = 0; worker < _workerDurations.GetLength(2); ++worker)
                    {
                        if (_workerDurations[operation,machine,worker] > 0)
                        {
                            machineWorkers.Add(worker);
                        }
                    }
                    operationWorkers.Add(machineWorkers);
                }
                availableWorkers.Add(operationWorkers);
            }
            WFJSSPIndividual.AvailableWorkers = availableWorkers;
            // TODO: update mutation probability
            configuration.MutationProbability = 1.0f / (configuration.NOperations * 3.0f);
        }

        protected override void Adjust(Individual nIndividual)
        {
            return;
            WFJSSPIndividual individual = (WFJSSPIndividual)nIndividual;
            // TODO
            List<List<Dictionary<string, int>>> gaps = new List<List<Dictionary<string, int>>>();
            for (int i = 0; i < _configuration.NMachines; ++i)
            {
                gaps.Add(new List<Dictionary<string, int>>());
            }
            int[] endTimesOnMachines = new int[_configuration.NMachines];
            int[] endTimesOfOperations = new int[_configuration.NOperations];

            int[] endTimesOfWorkers = new int[_workerDurations.GetLength(2)]; // should be N workers

            int[] nextOperation = new int[_configuration.NJobs];

            for (int i = 0; i < individual.Sequence.Length; ++i)
            {
                int job = 0;
                int operation = nextOperation[job]++;
                int operationIndex = _configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[operationIndex];

                int worker = individual.Workers[operationIndex];

                int duration = _workerDurations[operation, machine, worker];

                bool inserted = false;
                for (int j = 0; j < gaps[machine].Count; ++j)
                {
                    Dictionary<string, int> gap = gaps[machine][j];
                    if (gap["end"] - gap["start"] >= duration)
                    {
                        if (operationIndex == 0 || _configuration.JobSequence[operationIndex - 1] == _configuration.JobSequence[operationIndex] && endTimesOfOperations[operationIndex - 1] <= gap["end"] - duration)
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
                            int jobSwap = _configuration.JobSequence[gap["preceedsOperation"]];
                            int swapOperationIndex = 0;
                            int swapStartIndex = 0;
                            bool found = false;
                            for (int k = 0; k < _configuration.JobSequence.Length && !found; ++k)
                            {
                                if (_configuration.JobSequence[k] == jobSwap)
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
                    if (operationIndex != 0 && _configuration.JobSequence[operationIndex - 1] == _configuration.JobSequence[operationIndex])
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
        }

        protected override void Evaluate(Individual nIndividual)
        {
            WFJSSPIndividual individual = (WFJSSPIndividual)nIndividual;
            // TODO: test
            if (!individual.Feasible)
            {
                individual.Fitness[Criteria.Makespan] = float.MaxValue;
                return;
            }
            int[] nextOperation = new int[_configuration.NJobs];
            int[] endOnMachines = new int[_configuration.NMachines];
            int[] endOfWorkers = new int[_workerDurations.GetLength(2)];
            int[] endTimes = new int[_configuration.JobSequence.Length];
            for (int i = 0; i < individual.Sequence.Length; ++i)
            {
                int job = individual.Sequence[i];
                int operation = nextOperation[job]++;
                int startIndex = _configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[startIndex];

                int worker = individual.Workers[startIndex];

                int duration = _workerDurations[startIndex, machine, worker];
                int offset = 0;
                int minStartJob = 0;
                if (operation > 0)
                {
                    offset = Math.Max(Math.Max(0, endTimes[startIndex - 1] - endOnMachines[machine]), endTimes[startIndex - 1] - endOfWorkers[worker]);
                    minStartJob = endTimes[startIndex - 1];
                }
                endTimes[startIndex] = Math.Max(endOnMachines[machine], endOfWorkers[worker]) + duration + offset;
                endOnMachines[machine] = endTimes[startIndex];
            }
            individual.Fitness[Criteria.Makespan] = endTimes.Max();
            _functionEvaluations++;
        }
    }
}
