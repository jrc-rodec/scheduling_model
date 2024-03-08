using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Solver
{
    public class GA
    {

        private List<Individual> _population;
        private GAConfiguration _configuration;
        private Random _random;
        public GA(GAConfiguration configuration)
        {
            _configuration = configuration;
            Reset();
        }

        public void Reset()
        {
            _random = new Random();
            _population = new List<Individual>();
        }

        private Individual TournamentSelection(int tournamentSize)
        {
            if(tournamentSize == 0)
            {
                tournamentSize = _population.Count / 10;
            }
            List<int> participants = new List<int>();
            while(participants.Count < tournamentSize)
            {
                int index;
                do
                {
                    index = _random.Next(_population.Count);
                } while (participants.Contains(index));
                participants.Add(index);
            }
            Individual winner = _population[participants[0]];
            for(int i = 1; i < participants.Count; ++i)
            {
                if (_population[participants[i]].Fitness[Criteria.Makespan] < winner.Fitness[Criteria.Makespan]){
                    winner = _population[participants[i]];
                }
            }
            return winner;
        }

        public Individual Recombine(int tournamentSize)
        {
            Individual parentA = TournamentSelection(tournamentSize);
            Individual parentB;
            do
            {
                parentB = TournamentSelection(tournamentSize);
            } while (parentA.Equals(parentB));
            return new Individual(parentA, parentB);
        }

        
    }
}
