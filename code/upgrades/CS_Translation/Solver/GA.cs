using System;
using System.Collections.Generic;
using System.Data;
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

        private bool _generationStop = false;
        private bool _fitnessStop = false;
        private bool _timeStop = false;
        private bool _fevalStop = false;

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

        private Individual Recombine(int tournamentSize)
        {
            Individual parentA = TournamentSelection(tournamentSize);
            Individual parentB;
            do
            {
                parentB = TournamentSelection(tournamentSize);
            } while (parentA.Equals(parentB));
            return new Individual(parentA, parentB);
        }

        private void Adjust(Individual individual)
        {
            // TODO
        }

        private void Evaluate(Individual individual)
        {
            // TODO
        }

        private void CreatePopulation(int populationSize)
        {
            _population = new List<Individual>();
            for(int i = 0; i < populationSize; ++i)
            {
                Individual individual = new Individual(_population);
                // Adjustment step
                Adjust(individual);
                Evaluate(individual);
                _population.Add(individual);
            }
        }

        private void CreateOffspring(List<Individual> offspring, int offspringAmount, int tournamentSize, float mutationProbability)
        {
            offspring = new List<Individual>();
            for(int i = 0; i < offspringAmount; ++i)
            {
                Individual o = Recombine(tournamentSize);
                // Adjustment step
                Adjust(o);
                o.Mutate(mutationProbability);
                Evaluate(o);
                offspring.Add(o);
            }
        }

        // TODO: Add parameters for missing criteria
        private void UpdateStoppingCriteria(int generation, int maxGeneration, int functionEvaluations, int maxFunctionEvaluations)
        {
            _generationStop = generation >= maxGeneration;
            _timeStop = false;
            _fevalStop = functionEvaluations >= maxFunctionEvaluations;
            _fitnessStop = false;
        }

        private List<Individual> GetAllEqual(Individual original, List<Individual> individuals)
        {
            List<Individual> result = new List<Individual>();
            for(int i = 0; i <  individuals.Count; ++i)
            {
                if (original.Fitness[Criteria.Makespan] == individuals[i].Fitness[Criteria.Makespan])
                {
                    result.Add(individuals[i]);
                }
            }
            return result;
        }

        private float UpdateMutationProbability(float p, int generation, int lastProgress, int maxWait, float maxP)
        {
            return (float)(p * (Math.Pow((generation - lastProgress) * (1.0f / maxWait), 4) * maxP));
        }

        //TODO: change to public History Run()
        public void Run(int maxGeneration, int timeLimit, float targetFitness, int maxFunctionEvaluations)
        {
            CreatePopulation(_configuration.PopulationSize);
            List<Individual> offspring = new List<Individual>();
            // Setup all required parameters using the decision variables
            int populationSize = _configuration.PopulationSize;
            int offspringAmount = _configuration.OffspringAmount;
            int tournamentSize = _configuration.TournamentSize; //TODO: adjust
            float mutationProbability = _configuration.MutationProbability;
            float maxMutationProbability = _configuration.MaxMutationProbability;
            float elitism = _configuration.ElitismRate;
            int maxWait = _configuration.RestartGenerations;
            _population.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
            List<Individual> overallBest = GetAllEqual(_population[0], _population);
            List<Individual> currentBest = GetAllEqual(_population[0], _population);
            int lastProgress = 0;
            int generation = 0;
            int functionEvaluations = 0;
            UpdateStoppingCriteria(generation, maxGeneration, functionEvaluations, maxFunctionEvaluations);
            while(!_generationStop && !_fevalStop && !_fitnessStop && !_timeStop)
            {
                if(generation > 0 && lastProgress < generation - 1)
                {
                    mutationProbability = UpdateMutationProbability(mutationProbability, generation, lastProgress, maxWait, maxMutationProbability);
                }
                // TODO: restarts

                CreateOffspring(offspring, offspringAmount, tournamentSize, mutationProbability);
                //offspring.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
                List<Individual> pool = offspring;
                for(int i = 0; i < _population.Count * elitism; ++i)
                {
                    // NOTE: population always be sorted at this point
                    pool.Add(_population[i]);
                }
                pool.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
                _population = new List<Individual>();
                for(int i = 0; i < populationSize; ++i)
                {
                    _population.Add(pool[i]);
                }

                if (_population[0].Fitness[Criteria.Makespan] < currentBest[0].Fitness[Criteria.Makespan])
                {
                    currentBest = GetAllEqual(_population[0], _population);
                    if (currentBest[0].Fitness[Criteria.Makespan] < overallBest[0].Fitness[Criteria.Makespan])
                    {
                        overallBest = GetAllEqual(_population[0], _population); // just to not copy currentBest
                    } else if (currentBest[0].Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan])
                    {
                        for(int i = 0; i < currentBest.Count; ++i)
                        {
                            if (!overallBest.Contains(currentBest[i]))
                            {
                                overallBest.Add(currentBest[i]);
                            }
                        }
                    }
                } else if (_population[0].Fitness[Criteria.Makespan] == currentBest[0].Fitness[Criteria.Makespan])
                {
                    List<Individual> equals = GetAllEqual(_population[0], _population);
                    for(int i = 0; i < equals.Count; ++i)
                    {
                        if (!currentBest.Contains(equals[i]))
                        {
                            currentBest.Add(equals[i]);
                        }
                    }
                    if (currentBest[0].Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan])
                    {
                        for (int i = 0; i < currentBest.Count; ++i)
                        {
                            if (!overallBest.Contains(currentBest[i]))
                            {
                                overallBest.Add(currentBest[i]);
                            }
                        }
                    }
                }

                ++generation;
            }
        }
        
    }
}
