using MathNet.Numerics.Distributions;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.PortableExecutable;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace GA_Uncertainty
{
    public enum Criteria
    {
        Makespan, IdleTime, QueueTime, Tardiness, AverageRobustness, RandomDelays, AdjustedAverageRobustness
    }

    public class TimeSlot
    {
        public int Start = 0;
        public int End = 0;

        public TimeSlot(int start, int end)
        {
            Start = start;
            End = end;
        }
        public bool Overlaps(TimeSlot other)
        {
            return Contains(other.Start) || Contains(other.End) || other.Contains(Start) || other.Contains(End);
        }

        public bool Contains(int time)
        {
            return time >= Start && time <= End;
        }
    }

    public abstract class Evaluation
    {
        protected GAConfiguration _configuration;
        protected int[,,] _workerDurations;
        protected int _functionEvaluations;
        public Evaluation(GAConfiguration configuration, int[,,] workerDurations)
        {
            _configuration = configuration;
            _workerDurations = workerDurations;
            _functionEvaluations = 0;
        }
        public int FunctionEvaluations { get => _functionEvaluations; }

        public abstract void Evaluate(Individual individual);

        protected TimeSlot EarliestFit(List<TimeSlot> slots, TimeSlot slot)
        {
            for (int i = 1; i < slots.Count; ++i)
            {
                if (slots[i - 1].End <= slot.Start && slots[i].Start >= slot.End)
                {
                    return slots[i - 1];
                }
            }
            return slots.Last();
        }
    }

    public class Makespan : Evaluation
    {
        public Makespan(GAConfiguration configuration, int[,,] workerDurations) : base(configuration, workerDurations)
        {
        }

        public override void Evaluate(Individual individual)
        {
            if (!individual.Feasible)
            {
                individual.Fitness[Criteria.Makespan] = float.MaxValue;
                return;
            }
            int[] nextOperation = new int[_configuration.NJobs];
            List<TimeSlot>[] endOnMachines = new List<TimeSlot>[_configuration.NMachines];
            for (int i = 0; i < endOnMachines.Length; ++i)
            {
                endOnMachines[i] = new List<TimeSlot>();
                endOnMachines[i].Add(new TimeSlot(0, 0));
            }
            List<TimeSlot>[] endOfWorkers = new List<TimeSlot>[_workerDurations.GetLength(2)];
            for (int i = 0; i < endOfWorkers.Length; ++i)
            {
                endOfWorkers[i] = new List<TimeSlot>();
                endOfWorkers[i].Add(new TimeSlot(0, 0));
            }
            int[] endTimes = new int[_configuration.JobSequence.Length];
            for (int i = 0; i < individual.Sequence.Length; ++i)
            {
                int job = individual.Sequence[i];
                int operation = nextOperation[job];
                ++nextOperation[job];
                int startIndex = _configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[startIndex];

                int worker = individual.Workers[startIndex];

                int duration = _workerDurations[startIndex, machine, worker];
                if (duration == 0)
                {
                    Console.WriteLine("0 DURATION, INVALID ASSIGNMENT!");
                }
                int offset = 0;
                if (operation > 0)
                {
                    if (endTimes[startIndex - 1] > offset)
                    {
                        // need to wait for previous operation to finish
                        offset = endTimes[startIndex - 1];
                    }
                }
                if (endOnMachines[machine].Count > 0 && endOnMachines[machine].Last().End >= offset)
                {
                    // need to wait for machine to be available
                    offset = endOnMachines[machine].Last().End;
                }
                // (could be on other machine at a later time already)
                if (endOfWorkers[worker].Count > 0)
                {
                    TimeSlot workerEarliest = EarliestFit(endOfWorkers[worker], new TimeSlot(offset, offset + duration));
                    if (workerEarliest.End >= offset)
                    //if (endOfWorkers[worker].Last().End >= offset)
                    {
                        // need to wait for worker to be ready
                        offset = workerEarliest.End;
                    }
                }

                endTimes[startIndex] = offset + duration;
                endOnMachines[machine].Add(new TimeSlot(offset, offset + duration));
                endOfWorkers[worker].Add(new TimeSlot(offset, offset + duration)); // Sort?
            }
            individual.Fitness[Criteria.Makespan] = endTimes.Max();
            _functionEvaluations++;
        }
    }

    public abstract class RobustEvaluation : Evaluation
    {

        protected int _nExperiments;
        protected Random _random;
        protected float _stdev;
        public RobustEvaluation(GAConfiguration configuration, int[,,] workerDurations, int nExperiments) : base(configuration, workerDurations)
        {
            _nExperiments = nExperiments;
            _random = new Random();
            _stdev = 0.1f;
        }

        protected double RandomNormal(float mean)
        {
            double u1 = 1.0 - _random.NextDouble(); //uniform(0,1] random doubles
            double u2 = 1.0 - _random.NextDouble();
            double randStdNormal = Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Sin(2.0 * Math.PI * u2); //random normal(0,1)
            return mean + _stdev * randStdNormal;
        }

        public void SetNormalStdev(float stdev)
        {
            _stdev = stdev;
        }
    }

    public class AverageRobustness : RobustEvaluation
    {

        Beta b; // 0.1, 0.4

        public AverageRobustness(GAConfiguration configuration, int[,,] workerDurations, int nExperiments, float stdev, float alpha, float beta) : base(configuration, workerDurations, nExperiments)
        {
            _nExperiments = nExperiments;
            _random = new Random();
            _stdev = stdev;
            b = new Beta(alpha, beta);
        }

        public float Simulate(Individual individual)
        {
            int[] nextOperation = new int[_configuration.NJobs];
            List<TimeSlot>[] endOnMachines = new List<TimeSlot>[_configuration.NMachines];
            for (int i = 0; i < endOnMachines.Length; ++i)
            {
                endOnMachines[i] = new List<TimeSlot>();
                endOnMachines[i].Add(new TimeSlot(0, 0));
            }
            List<TimeSlot>[] endOfWorkers = new List<TimeSlot>[_workerDurations.GetLength(2)];
            for (int i = 0; i < endOfWorkers.Length; ++i)
            {
                endOfWorkers[i] = new List<TimeSlot>();
                endOfWorkers[i].Add(new TimeSlot(0, 0));
            }
            int[] endTimes = new int[_configuration.JobSequence.Length];
            for (int i = 0; i < individual.Sequence.Length; ++i)
            {
                int job = individual.Sequence[i];
                int operation = nextOperation[job];
                ++nextOperation[job];
                int startIndex = _configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[startIndex];

                int worker = individual.Workers[startIndex];


                //int duration = Math.Max(1, (int)(RandomNormal(_workerDurations[startIndex, machine, worker])+0.5));
                int duration = Math.Max(1, (int)(_workerDurations[startIndex, machine, worker] * (1.0 + b.Sample())+0.5)); // beta distribution
                
                if (duration == 0)
                {
                    Console.WriteLine("0 DURATION, INVALID ASSIGNMENT!");
                }
                int offset = 0;
                if (operation > 0)
                {
                    if (endTimes[startIndex - 1] > offset)
                    {
                        // need to wait for previous operation to finish
                        offset = endTimes[startIndex - 1];
                    }
                }
                if (endOnMachines[machine].Count > 0 && endOnMachines[machine].Last().End >= offset)
                {
                    // need to wait for machine to be available
                    offset = endOnMachines[machine].Last().End;
                }
                // (could be on other machine at a later time already)
                if (endOfWorkers[worker].Count > 0)
                {
                    TimeSlot workerEarliest = EarliestFit(endOfWorkers[worker], new TimeSlot(offset, offset + duration));
                    if (workerEarliest.End >= offset)
                    //if (endOfWorkers[worker].Last().End >= offset)
                    {
                        // need to wait for worker to be ready
                        offset = workerEarliest.End;
                    }
                }
                endTimes[startIndex] = offset + duration;
                endOnMachines[machine].Add(new TimeSlot(offset, offset + duration));
                endOfWorkers[worker].Add(new TimeSlot(offset, offset + duration));
            }
            return endTimes.Max();
        }

        public override void Evaluate(Individual individual)
        { 
            float fitness = 0.0f;
            for(int i = 0; i < _nExperiments; ++i)
            {
                fitness += Simulate(individual);
            }
            individual.Fitness[Criteria.AverageRobustness] = fitness/_nExperiments;
            _functionEvaluations++;
        }
    }

    public class RandomDelayRobustnessEvaluation : RobustEvaluation
    {
        float[] _machineProbabilities;
        Poisson[] _poissons; // TODO: use
        Beta b; // 0.9, 0.1

        public RandomDelayRobustnessEvaluation(GAConfiguration configuration, int[,,] workerDurations, float[] machineProbabilities, int nExperiments, float alpha, float beta) : base(configuration, workerDurations, nExperiments)
        {
            _machineProbabilities = machineProbabilities;
            _poissons = new Poisson[_machineProbabilities.Length];
            for (int i = 0; i < _machineProbabilities.Length; ++i)
            {
                _poissons[i] = new Poisson(_machineProbabilities[i]);
            }
            b = new Beta(alpha, beta);
        }

        private float Simulate(Individual individual)
        {
            int[] nextOperation = new int[_configuration.NJobs];
            List<TimeSlot>[] endOnMachines = new List<TimeSlot>[_configuration.NMachines];
            for (int i = 0; i < endOnMachines.Length; ++i)
            {
                endOnMachines[i] = new List<TimeSlot>();
                endOnMachines[i].Add(new TimeSlot(0, 0));
            }
            List<TimeSlot>[] endOfWorkers = new List<TimeSlot>[_workerDurations.GetLength(2)];
            for (int i = 0; i < endOfWorkers.Length; ++i)
            {
                endOfWorkers[i] = new List<TimeSlot>();
                endOfWorkers[i].Add(new TimeSlot(0, 0));
            }
            int[] endTimes = new int[_configuration.JobSequence.Length];
            for (int i = 0; i < individual.Sequence.Length; ++i)
            {
                int job = individual.Sequence[i];
                int operation = nextOperation[job];
                ++nextOperation[job];
                int startIndex = _configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[startIndex];

                int worker = individual.Workers[startIndex];
                //int duration = Math.Min(1, (int)(RandomNormal(_workerDurations[startIndex, machine, worker]) + 0.5));
                int duration = _workerDurations[startIndex, machine, worker];
                if(_random.NextDouble() < _machineProbabilities[machine]) // TODO: poisson
                {
                    duration += (int)((duration * b.Sample()) + 0.5);
                    //duration += (int)((duration * _random.NextDouble()) + 0.5); //TODO: parameter for max/min ranges
                }
                if (duration == 0)
                {
                    Console.WriteLine("0 DURATION, INVALID ASSIGNMENT!");
                }
                int offset = 0;
                if (operation > 0)
                {
                    if (endTimes[startIndex - 1] > offset)
                    {
                        // need to wait for previous operation to finish
                        offset = endTimes[startIndex - 1];
                    }
                }
                if (endOnMachines[machine].Count > 0 && endOnMachines[machine].Last().End >= offset)
                {
                    // need to wait for machine to be available
                    offset = endOnMachines[machine].Last().End;
                }
                // (could be on other machine at a later time already)
                if (endOfWorkers[worker].Count > 0)
                {
                    TimeSlot workerEarliest = EarliestFit(endOfWorkers[worker], new TimeSlot(offset, offset + duration));
                    if (workerEarliest.End >= offset)
                    //if (endOfWorkers[worker].Last().End >= offset)
                    {
                        // need to wait for worker to be ready
                        offset = workerEarliest.End;
                    }
                }
                endTimes[startIndex] = offset + duration;
                endOnMachines[machine].Add(new TimeSlot(offset, offset + duration));
                endOfWorkers[worker].Add(new TimeSlot(offset, offset + duration));
            }
            return endTimes.Max();
        }

        public override void Evaluate(Individual individual)
        {
            float fitness = 0.0f;
            for (int i = 0; i < _nExperiments; ++i)
            {
                fitness += Simulate(individual);
            }
            individual.Fitness[Criteria.RandomDelays] = fitness / _nExperiments;
            _functionEvaluations++;
        }
    }


    public class AdjustedAverageRobustness : RobustEvaluation
    {

        Beta b; // 0.1, 0.4

        public AdjustedAverageRobustness(GAConfiguration configuration, int[,,] workerDurations, int nExperiments, float stdev, float alpha, float beta) : base(configuration, workerDurations, nExperiments)
        {
            _nExperiments = nExperiments;
            _random = new Random();
            _stdev = stdev;
            b = new Beta(alpha, beta);
        }

        public float Simulate(Individual individual)
        {
            int[,,] durations = _workerDurations;
            for(int i = 0; i < durations.GetLength(0); ++i)
            {
                for(int j = 0; j < durations.GetLength(1); ++j)
                {
                    for (int k = 0; k < durations.GetLength(2); ++k)
                    {
                        if (durations[i,j,k] > 0)
                        {
                            durations[i, j, k] = Math.Max(1, (int)(_workerDurations[i, j, k] * (1.0 + b.Sample()) + 0.5));
                        }
                    }
                }
            }
            _configuration.Durations = durations;
            Adjustment.Adjust(individual, _configuration);
            int[] nextOperation = new int[_configuration.NJobs];
            List<TimeSlot>[] endOnMachines = new List<TimeSlot>[_configuration.NMachines];
            for (int i = 0; i < endOnMachines.Length; ++i)
            {
                endOnMachines[i] = new List<TimeSlot>();
                endOnMachines[i].Add(new TimeSlot(0, 0));
            }
            List<TimeSlot>[] endOfWorkers = new List<TimeSlot>[durations.GetLength(2)];
            for (int i = 0; i < endOfWorkers.Length; ++i)
            {
                endOfWorkers[i] = new List<TimeSlot>();
                endOfWorkers[i].Add(new TimeSlot(0, 0));
            }
            int[] endTimes = new int[_configuration.JobSequence.Length];
            for (int i = 0; i < individual.Sequence.Length; ++i)
            {
                int job = individual.Sequence[i];
                int operation = nextOperation[job];
                ++nextOperation[job];
                int startIndex = _configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[startIndex];

                int worker = individual.Workers[startIndex];

                //int duration = Math.Max(1, (int)(RandomNormal(_workerDurations[startIndex, machine, worker])+0.5));
                int duration = durations[startIndex, machine, worker];// Math.Max(1, (int)(durations[startIndex, machine, worker] * (1.0 + b.Sample()) + 0.5)); // beta distribution

                if (duration == 0)
                {
                    Console.WriteLine("0 DURATION, INVALID ASSIGNMENT!");
                }
                int offset = 0;
                if (operation > 0)
                {
                    if (endTimes[startIndex - 1] > offset)
                    {
                        // need to wait for previous operation to finish
                        offset = endTimes[startIndex - 1];
                    }
                }
                if (endOnMachines[machine].Count > 0 && endOnMachines[machine].Last().End >= offset)
                {
                    // need to wait for machine to be available
                    offset = endOnMachines[machine].Last().End;
                }
                // (could be on other machine at a later time already)
                if (endOfWorkers[worker].Count > 0)
                {
                    TimeSlot workerEarliest = EarliestFit(endOfWorkers[worker], new TimeSlot(offset, offset + duration));
                    if (workerEarliest.End >= offset)
                    //if (endOfWorkers[worker].Last().End >= offset)
                    {
                        // need to wait for worker to be ready
                        offset = workerEarliest.End;
                    }
                }
                endTimes[startIndex] = offset + duration;
                endOnMachines[machine].Add(new TimeSlot(offset, offset + duration));
                endOfWorkers[worker].Add(new TimeSlot(offset, offset + duration));
            }
            return endTimes.Max();
        }

        public override void Evaluate(Individual individual)
        {
            float fitness = 0.0f;
            for (int i = 0; i < _nExperiments; ++i)
            {
                fitness += Simulate(individual);
            }
            individual.Fitness[Criteria.AdjustedAverageRobustness] = fitness / _nExperiments;
            _functionEvaluations++;
        }
    }


}
