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

        public WFJSSPIndividual() : base(true)
        {
            _workers = new int[JobSequence.Length];
        }

        protected override void Randomize()
        {
            Random random = new Random();
            base.Randomize();
            for(int i = 0; i < _workers.Length; ++i)
            {
                _workers[i] = AvailableWorkers[i][_assignments[i]][random.Next(0, AvailableWorkers[i][_assignments[i]].Count)];
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
