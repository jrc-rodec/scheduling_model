﻿using System;
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
        private int[] _sequence;
        private int[] _assignments;
        private Dictionary<Criteria, float> _fitness;
        private bool _feasible = true;

        public static int[] JobSequence;
        public static int[,] Durations;
        public static List<List<int>> AvailableMachines;
        public static float MaxDissimilarity;
        public static int MaxInitializationAttemps = 100; // TODO
        public static float DistanceAdjustmentRate = 0.75f; // TODO

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

        private Individual(bool randomize = false)
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

        public Individual(List<Individual> population) : this(true)
        {
            float minDistance = MaxDissimilarity;
            int attempts = 0;
            float[] dissimilarity = new float[population.Count];
            while(dissimilarity.Length > 0 && Average(dissimilarity) < minDistance)
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
            }
            population.Add(this);
        }

        public Individual(Individual parentA, Individual parentB) : this(false)
        {
            // randomly divide jobs into distinct sets
            HashSet<int> jobs = new HashSet<int>(JobSequence); // I hope this does what I think
            
            List<int> a = new List<int>();
            List<int> b = new List<int>();
            jobs.ElementAt(0);
            Random random = new Random();
            // IPOX-Crossover for Operation Sequence
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
            int bIndex = 0;
            List<int> parentBValues = new List<int>();
            for(int i = 0; i < parentB._sequence.Length; ++i)
            {
                if (b.Contains(parentB._sequence[i]))
                {
                    parentBValues.Add(i);
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
            }
            // Uniform Crossover for Machine Assignments
            for(int i = 0; i < _assignments.Length; ++i)
            {
                if(random.NextDouble() < 0.5)
                {
                    _assignments[i] = parentA._assignments[i];
                } else
                {
                    _assignments[i] = parentB._assignments[i];
                }
            }
        }

        public void Mutate(float p)
        {
            Random random = new Random();
            for(int i = 0; i < _sequence.Length; ++i)
            {
                if(random.NextDouble() < p)
                {
                    int swap;
                    do
                    {
                        swap = random.Next(_sequence.Length); 
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
                            swap = random.Next(_assignments.Length);
                        } while (swap == i);
                        int tmp = _assignments[swap];
                        _assignments[swap] = _assignments[i];
                        _assignments[i] = tmp;
                    }
                }
            }
        }

        private void Randomize()
        {
            JobSequence.CopyTo(_sequence, 0);
            Random random = new Random();
            for (int i = 0; i < _assignments.Length; ++i)
            {
                _assignments[i] = AvailableMachines[i][random.Next(0, AvailableMachines[i].Count)];
            }
        }

        private float Average(float[] values)
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