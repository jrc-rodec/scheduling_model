using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace Solver
{

    public enum Criteria
    {
        Makespan, IdleTime, QueueTime, Tardiness
    }

    public class Individual
    {
        protected int[] _sequence;
        protected int[] _assignments;
        protected Dictionary<Criteria, float> _fitness;
        protected bool _feasible = true;

        public static int[] JobSequence;
        public static int[,] Durations;
        public static List<List<int>> AvailableMachines;
        public static float MaxDissimilarity;
        public static int MaxInitializationAttemps = 100; // TODO add parameter
        public static float DistanceAdjustmentRate = 0.75f; // TODO add parameter

        public Dictionary<Criteria, float> Fitness { get => _fitness; set => _fitness = value; }
        public bool Feasible { get => _feasible; set => _feasible = value; }
        public int[] Sequence { get => _sequence; set => _sequence = value; }
        public int[] Assignments { get => _assignments; set => _assignments = value; }

        public static void DetermineMaxDissimiarilty()
        {
            MaxDissimilarity = 0.0f;
            for(int i = 0; i < AvailableMachines.Count; ++i)
            {
                MaxDissimilarity += AvailableMachines[i].Count;
            }
            MaxDissimilarity += JobSequence.Length;
        }

        protected Individual(bool randomize = false)
        {
            _sequence = new int[JobSequence.Length];
            _assignments = new int[JobSequence.Length];
            _fitness = new Dictionary<Criteria, float>();
            if (randomize)
            {
                // randomize
                Randomize();
            }
        }

        public Individual(Individual individual)
        {
            // Copy
            _sequence = new int[individual._sequence.Length];
            individual._sequence.CopyTo(_sequence, 0);
            _assignments = new int[individual._assignments.Length];
            individual._assignments.CopyTo(_assignments, 0);
            _fitness = individual.Fitness;
        }

        public Individual(List<Individual> population) : this(true)
        {
            if(population.Count < 1)
            {
                // create random individual, since population does not contain any individuals
                Randomize();
            } else
            {
                float minDistance = MaxDissimilarity;
                int attempts = 0;
                int overallMaxAttempts = 10000;
                int overallAttempts = 0;
                float[] dissimilarity = new float[population.Count];
                while(Average(dissimilarity) <= minDistance && overallAttempts < overallMaxAttempts)
                {
                    if(attempts > MaxInitializationAttemps)
                    {
                        minDistance = minDistance * DistanceAdjustmentRate;
                        attempts = 0;
                    }
                    Randomize();
                    for(int i = 0; i < population.Count; ++i)
                    {
                        dissimilarity[i] = GetDissimilarity(population[i]);
                    }
                    ++attempts;
                    ++overallAttempts;
                }
            }
        }

        public Individual(Individual parentA, Individual parentB) : this(false)
        {
            // randomly divide jobs into distinct sets
            HashSet<int> jobs = new HashSet<int>(JobSequence); // I hope this does what I think
            
            List<int> a = new List<int>();
            List<int> b = new List<int>();
            Random random = new Random();
            for(int i = 0; i < jobs.Count; ++i)
            {
                if(random.NextDouble() < 0.5)
                {
                    a.Add(jobs.ElementAt(i));
                } else
                {
                    b.Add(jobs.ElementAt(i));
                }
            }

            // IPOX-Crossover for Operation Sequence
            int bIndex = 0;
            List<int> parentBValues = new List<int>();
            for(int i = 0; i < parentB._sequence.Length; ++i)
            {
                if (b.Contains(parentB._sequence[i]))
                {
                    parentBValues.Add(parentB._sequence[i]);
                }
            }
            for (int i = 0; i < parentA._sequence.Length; ++i)
            {
                if (a.Contains(parentA._sequence[i]))
                {
                    _sequence[i] = parentA._sequence[i];
                } else
                {
                    _sequence[i] = parentBValues[bIndex++];
                }

                if (random.NextDouble() < 0.5)
                {
                    _assignments[i] = parentA._assignments[i];
                }
                else
                {
                    _assignments[i] = parentB._assignments[i];
                }
            }

            // Uniform Crossover for Machine Assignments
            /*for(int i = 0; i < _assignments.Length; ++i)
            {
                if(random.NextDouble() < 0.5)
                {
                    _assignments[i] = parentA._assignments[i];
                } else
                {
                    _assignments[i] = parentB._assignments[i];
                }
            }*/
        }

        public virtual void Mutate(float p)
        {
            Random random = new Random();
            for(int i = 0; i < _sequence.Length; ++i)
            {
                if(random.NextDouble() < p)
                {
                    int swap;
                    int attempts = 0;
                    do
                    {
                        swap = random.Next(_sequence.Length);
                        ++attempts;
                    } while (_sequence[swap] == _sequence[i]); // make sure it does not swap with itself
                    int tmp = _sequence[swap];
                    _sequence[swap] = _sequence[i];
                    _sequence[i] = tmp;
                }
                // since _sequence.Length == _assignments.Length
                if(random.NextDouble() < p)
                {
                    if (AvailableMachines[i].Count > 1)
                    {
                        int swap;
                        do
                        {
                            swap = random.Next(AvailableMachines[i].Count);
                        } while (AvailableMachines[i][swap] == _assignments[i]);
                        _assignments[i] = AvailableMachines[i][swap];
                    }
                }
            }
        }

        protected void ShuffleSequence()
        {
            Random random = new Random();
            for(int i = 0; i < _sequence.Length; ++i)
            {
                int index = random.Next(_sequence.Length);
                int tmp = _sequence[index];
                _sequence[index] = _sequence[i];
                _sequence[i] = tmp;
            }
        }

        protected virtual void Randomize()
        {
            JobSequence.CopyTo(_sequence, 0);
            Random random = new Random();
            //_sequence = _sequence.Select(x => (x, random.Next())) // TODO: ????
            //             .OrderBy(tuple => tuple.Item2)
            //             .Select(tuple => tuple.Item1)
            //             .ToArray();
            ShuffleSequence();
            for (int i = 0; i < _assignments.Length; ++i)
            {
                _assignments[i] = AvailableMachines[i][random.Next(0, AvailableMachines[i].Count)];
            }
        }

        protected float Average(float[] values)
        {
            float sum = 0;
            for(int i = 0; i < values.Length; ++i)
            {
                sum += values[i];
            }
            return sum / values.Length;
        }

        public float GetDissimilarity(Individual other)
        {
            float result = 0.0f;
            for(int i = 0; i < _sequence.Length; ++i)
            {
                if (_assignments[i] != other._assignments[i])
                {
                    result += AvailableMachines[i].Count;
                }
                if (_sequence[i] != other._sequence[i])
                {
                    ++result;
                }
            }
            return result;
        }


        public bool Equals(Individual other)
        {
            // NOTE: _sequence and _assignments are always the same length
            for(int i = 0; i < _sequence.Length; ++i)
            {
                if (_sequence[i] != other._sequence[i])
                {
                    return false;
                }
                if (_assignments[i] != other._assignments[i])
                {
                    return false;
                }
            }
            return true;
        }

    }
}
