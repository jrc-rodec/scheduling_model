using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Solver
{
    public class WFJSSPIndividual : Individual
    {
        private int[] _workers;
        public static List<List<List<int>>> AvailableWorkers;

        public WFJSSPIndividual(bool randomize) : base(randomize)
        {
            _workers = new int[JobSequence.Length];
        }

        public WFJSSPIndividual(WFJSSPIndividual other) : base(other)
        {
            _workers = new int[other._workers.Length];
            other._workers.CopyTo(_workers, 0);
        }

        public WFJSSPIndividual(List<WFJSSPIndividual> population) : this(true)
        {
            //NOTE: code duplication
            float minDistance = MaxDissimilarity;
            int attempts = 0;
            float[] dissimilarity = new float[population.Count];
            while (dissimilarity.Length > 0 && Average(dissimilarity) < minDistance)
            {
                if (attempts > MaxInitializationAttemps)
                {
                    minDistance = minDistance * DistanceAdjustmentRate;
                    attempts = 0;
                }
                Randomize();
                for (int i = 0; i < population.Count; ++i)
                {
                    dissimilarity[i] = GetDissimilarity(population[i]);
                }
                ++attempts;
            }
        }

        public WFJSSPIndividual(WFJSSPIndividual parentA, WFJSSPIndividual parentB) : this(false)
        {
            //NOTE: Code duplication
            HashSet<int> jobs = new HashSet<int>(JobSequence);

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

            int bIndex = 0;
            List<int> parentBValues = new List<int>();
            for(int i = 0; i < parentB._sequence.Length; ++i)
            {
                if (b.Contains(parentB._sequence[i]))
                {
                    parentBValues.Add(parentB._sequence[i]);
                }
            }
            for(int i = 0; i < parentA._sequence.Length; ++i)
            {
                if (a.Contains(parentA._sequence[i]))
                {
                    _sequence[i] = parentA._sequence[i];
                } else
                {
                    _sequence[i] = parentBValues[bIndex++];
                }
                // since sequence length == assignments length == workers length
                if (random.NextDouble() < 0.5)
                {
                    _assignments[i] = parentA._assignments[i];
                    _workers[i] = parentA._workers[i];
                }
                else
                {
                    _assignments[i] = parentB._assignments[i];
                    _workers[i] = parentB._workers[i];
                }
            }

            /*for(int i = 0; i < _assignments.Length; ++i)
            {
                if(random.NextDouble() < 0.5)
                {
                    _assignments[i] = parentA._assignments[i];
                    _workers[i] = parentA._workers[i];
                } else
                {
                    _assignments[i] = parentB._assignments[i];
                    _workers[i] = parentB._workers[i];
                }
            }*/
        }

        protected override void Randomize()
        {
            Random random = new Random();
            base.Randomize();
            _workers = new int[JobSequence.Length];
            for (int i = 0; i < _workers.Length; ++i)
            {
                _workers[i] = AvailableWorkers[i][_assignments[i]][random.Next(0, AvailableWorkers[i][_assignments[i]].Count)];
            }
        }

        public static void DetermineMaxDissimilarity()
        {
            Individual.DetermineMaxDissimiarilty();
            for(int i = 0; i < AvailableWorkers.Count; ++i)
            {
                MaxDissimilarity += AvailableWorkers[i].Count;
            }
        }

        public override void Mutate(float p)
        {
            // mutate sequence and assignments through base would require one unnecessary loop
            //base.Mutate(p);
            Random random = new Random();
            for (int i = 0; i < _sequence.Length; ++i)
            {
                if (random.NextDouble() < p)
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
                if (random.NextDouble() < p)
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
                if(random.NextDouble() < p)
                {
                    if (AvailableWorkers[i][_assignments[i]].Count > 1){
                        int swap;
                        do
                        {
                            swap = random.Next(AvailableWorkers[i][_assignments[i]].Count);
                        } while (AvailableWorkers[i][_assignments[i]][swap] == _workers[i]);
                        _workers[i] = AvailableWorkers[i][_assignments[i]][swap];
                    }
                }
            }
        }
    }
}
