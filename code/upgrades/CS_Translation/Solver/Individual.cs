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
        private int[] _sequence;
        private int[] _assignments;
        private Dictionary<Criteria, float> _fitness;

        public static int[,] Duration;
        public static List<List<int>> AvailableMachines;

        private Individual(int nOperations)
        {
            _sequence = new int[nOperations];
            _assignments = new int[nOperations];
            _fitness = new Dictionary<Criteria, float>();
        }

        public Individual(int[] jobSequence) : this(jobSequence.Length)
        {
            // randomize
            jobSequence.CopyTo(_sequence, 0);
            Random random = new Random();
            for(int i = 0; i < _assignments.Length; ++i)
            {
                _assignments[i] = AvailableMachines[i][random.Next(0, AvailableMachines[i].Count)];
            }
        }

        public Individual(List<Individual> population) : this(population[0]._sequence.Length)
        {
            
        }


    }
}
