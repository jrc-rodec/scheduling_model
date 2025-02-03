using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GA_Uncertainty
{
    public class GA //: GA
    {
        protected List<Individual> _population;
        //private GAConfiguration _configuration;
        protected Random _random;

        protected bool _generationStop = false;
        protected bool _fitnessStop = false;
        protected bool _timeStop = false;
        protected bool _fevalStop = false;

        protected bool _useGenerationStop = true;
        protected bool _useFitnessStop = true;
        protected bool _useTimeStop = true;
        protected bool _useFevalStop = true;

        DateTime _startTime;
        protected int _functionEvaluations = 0;

        protected List<Evaluation> _evaluators;

        public int FunctionEvaluations { get => _functionEvaluations; set => _functionEvaluations = value; }

        protected bool _output = false;
        private int[,,] _workerDurations;
        private GAConfiguration _configuration;

        public void Reset()
        {
            _random = new Random();
            _population = new List<Individual>();
            _functionEvaluations = 0;
        }

        public GA(GAConfiguration configuration, bool output, int[,,] workerDurations)
        {
            _configuration = configuration;
            _output = output;
            Reset();
            _workerDurations = workerDurations;
            _evaluators = new List<Evaluation>();
            _evaluators.Add(new Makespan(configuration, workerDurations));
            _evaluators.Add(new AverageRobustness(configuration, workerDurations, 10, 0.1f)); // TODO
            // TODO: parameters
            List<Criteria> highestRank = [Criteria.Makespan];
            List<Criteria> secondRank = [Criteria.AverageRobustness];
            Individual.ranking.Add(highestRank);
            Individual.ranking.Add(secondRank);
            // TODO: update mutation probability
            configuration.MutationProbability = 1.0f / (configuration.NOperations * 3.0f);
        }

        private void Evaluate(Individual individual)
        {
            foreach (Evaluation evaluation in _evaluators)
            {
                evaluation.Evaluate(individual);
            }
        }

        protected Individual TournamentSelection(int tournamentSize)
        {
            if (tournamentSize == 0)
            {
                tournamentSize = Math.Max(1, _population.Count / 10);
            }
            List<int> participants = new List<int>();
            while (participants.Count < tournamentSize)
            {
                int index;
                do
                {
                    index = _random.Next(_population.Count);
                } while (participants.Contains(index));
                participants.Add(index);
            }
            Individual winner = _population[participants[0]];
            for (int i = 1; i < participants.Count; ++i)
            {
                if (_population[participants[i]].Fitness[Criteria.Makespan] < winner.Fitness[Criteria.Makespan])
                {
                    winner = _population[participants[i]];
                }
            }
            return winner;
        }

        protected Individual Recombine(int tournamentSize)
        {
            Individual parentA = TournamentSelection(tournamentSize);
            Individual parentB;
            int maxAttempts = 100;
            int attempts = 0;
            do
            {
                parentB = TournamentSelection(tournamentSize);
                ++attempts;
            } while (parentA.Equals(parentB) && attempts < maxAttempts);
            return new Individual(parentA, parentB);
        }

        protected void CreatePopulation(int populationSize)
        {
            _population = new List<Individual>();
            for (int i = 0; i < populationSize; ++i)
            {
                Individual individual = new Individual(_population);
                Evaluate(individual);
                _population.Add(individual);
            }
            _population.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
        }

        protected void CreateOffspring(List<Individual> offspring, int offspringAmount, int tournamentSize, float mutationProbability)
        {
            offspring.Clear();
            for (int i = 0; i < offspringAmount; ++i)
            {
                Individual o = Recombine(tournamentSize);
                o.Mutate(mutationProbability);
                Evaluate(o);
                offspring.Add(o);
            }
        }

        public void SetStoppingCriteriaStatus(bool generation, bool time, bool functionEvaluations, bool targetFitness)
        {
            _useGenerationStop = generation;
            _useTimeStop = time;
            _useFevalStop = functionEvaluations;
            _useFitnessStop = targetFitness;
        }

        protected void UpdateStoppingCriteria(int generation, float bestFitness, int maxGeneration, int functionEvaluations, int maxFunctionEvaluations, int timeLimit, float targetFitness)
        {
            _generationStop = _useGenerationStop && generation >= maxGeneration;
            _timeStop = _useTimeStop && DateTime.Now.Subtract(_startTime).TotalSeconds >= timeLimit;
            _fevalStop = _useFevalStop && functionEvaluations >= maxFunctionEvaluations;
            _fitnessStop = _useFitnessStop && bestFitness <= targetFitness;
        }

        protected List<Individual> GetAllEqual(Individual original, List<Individual> individuals)
        {
            List<Individual> result = new List<Individual>();
            for (int i = 0; i < individuals.Count; ++i)
            {
                if (original.Fitness[Criteria.Makespan] == individuals[i].Fitness[Criteria.Makespan])
                {
                    result.Add(individuals[i]);
                }
            }
            return result;
        }

        protected float UpdateMutationProbability(float p, int generation, int lastProgress, int maxWait, float maxP)
        {
            return (float)(p + (Math.Pow((generation - lastProgress) * (1.0f / maxWait), 4) * maxP));
        }

        public void Debug_Report(int generation, List<Individual> best, List<Individual> currentBest, int restarts, bool improvement, bool match)
        {
            if (improvement)
            {
                Console.ForegroundColor = ConsoleColor.Green;
            }
            else if (match)
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
            }
            Console.WriteLine("Generation " + generation + " Overall Best: " + best[0].Fitness[Criteria.Makespan] + " (" + best.Count + " equal solutions), Current Run Best " + currentBest[0].Fitness[Criteria.Makespan] + " (" + currentBest.Count + " equal solutions) - " + restarts + " restarts" + ")");
            Console.ResetColor();
        }

        public History Run(int maxGeneration, int timeLimit, float targetFitness, int maxFunctionEvaluations, bool keepMultiple)
        {
            bool rankedComparison = false; // TODO: parameter
            CreatePopulation(_configuration.PopulationSize);
            List<Individual> offspring = new List<Individual>();
            // Setup all required parameters using the decision variables
            int populationSize = _configuration.PopulationSize;
            int offspringAmount = _configuration.OffspringAmount;
            int tournamentSize = _configuration.TournamentSize; //TODO: adjust
            float mutationProbability = _configuration.MutationProbability;
            float maxMutationProbability = _configuration.MaxMutationProbability;
            float elitism = _configuration.ElitismRate * populationSize;
            int maxWait = _configuration.RestartGenerations;
            int restarts = 0;
            List<Individual> overallBest = GetAllEqual(_population[0], _population);
            List<Individual> currentBest = GetAllEqual(_population[0], _population);
            int lastProgress = 0;
            int generation = 0;
            _functionEvaluations = 0;
            _startTime = DateTime.Now;

            _output = false;

            History history = new History();
            bool improvement = false;
            bool match = false;
            UpdateStoppingCriteria(generation, overallBest[0].Fitness[Criteria.Makespan], maxGeneration, _functionEvaluations, maxFunctionEvaluations, timeLimit, targetFitness);
            while (!_generationStop && !_fevalStop && !_fitnessStop && !_timeStop)
            {
                history.Update(overallBest, currentBest, mutationProbability, _population);
                if (generation > 0 && lastProgress < generation - 1)
                {
                    mutationProbability = UpdateMutationProbability(mutationProbability, generation, lastProgress, maxWait, maxMutationProbability);
                }
                if (mutationProbability > maxMutationProbability)
                {
                    Individual localMinimum = currentBest[0];
                    // only necessary if local search is conducted
                    if (localMinimum.Fitness[Criteria.Makespan] < overallBest[0].Fitness[Criteria.Makespan])
                    {
                        overallBest.Clear(); // just never happened without local search
                        improvement = true;
                        if (keepMultiple)
                        {
                            foreach (Individual individual in currentBest)
                            {
                                if (individual.Fitness[Criteria.Makespan] == localMinimum.Fitness[Criteria.Makespan] && !overallBest.Contains(individual))
                                {
                                    overallBest.Add(individual);
                                }
                            }
                        }
                        else
                        {
                            overallBest.Add(localMinimum);
                        }
                    }
                    else if (keepMultiple && localMinimum.Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan] && !overallBest.Contains(localMinimum))
                    {
                        foreach (Individual individual in currentBest)
                        {
                            if (individual.Fitness[Criteria.Makespan] == localMinimum.Fitness[Criteria.Makespan] && !overallBest.Contains(individual))
                            {
                                overallBest.Add(individual);
                            }
                        }
                        match = true;
                    }
                    if (_output)
                    {
                        Debug_Report(generation - 1, overallBest, currentBest, restarts, improvement, match);
                    }
                    int maxPopulationSize = 400; // TODO: parameter
                    int maxOffspringAmount = maxPopulationSize * 4; // TODO: parameter
                    populationSize = (int)Math.Min(maxPopulationSize, _configuration.PopulationSizeGrowthRate * populationSize);
                    offspringAmount = (int)Math.Min(maxOffspringAmount, _configuration.PopulationSizeGrowthRate * offspringAmount);

                    elitism = Math.Max(0, populationSize * _configuration.MaxElitismRate * _configuration.DurationVariety);
                    tournamentSize = (int)Math.Max(1, (int)populationSize * _configuration.MaxTournamentRate * _configuration.DurationVariety);

                    currentBest.Clear();
                    // NOTE: for visual purposes only
                    improvement = false;
                    match = false;
                    // NOTE: also sorts the population
                    CreatePopulation(populationSize);
                    mutationProbability = _configuration.MutationProbability;
                    lastProgress = generation;
                    restarts++;
                }

                CreateOffspring(offspring, offspringAmount, tournamentSize, mutationProbability);
                List<Individual> pool = offspring; // NOTE: since no copy is made, could just use offspring as list
                for (int i = 0; i < elitism; ++i)
                {
                    // NOTE: population should always be sorted at this point
                    pool.Add(_population[i]);
                }
                if (rankedComparison)
                {
                    pool = Individual.RankedSort(pool);
                } else
                {
                    pool.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
                }
                _population = new List<Individual>();
                for (int i = 0; i < populationSize; ++i)
                {
                    _population.Add(pool[i]);
                }

                if (currentBest.Count == 0 || _population[0].Fitness[Criteria.Makespan] < currentBest[0].Fitness[Criteria.Makespan])
                {
                    if (keepMultiple)
                    {
                        currentBest = GetAllEqual(_population[0], _population);
                    }
                    else
                    {
                        currentBest.Clear();
                        currentBest.Add(_population[0]);
                    }
                    if (currentBest[0].Fitness[Criteria.Makespan] < overallBest[0].Fitness[Criteria.Makespan])
                    {
                        overallBest.Clear();
                        improvement = true;
                        if (keepMultiple)
                        {
                            overallBest = GetAllEqual(_population[0], _population); // just to not copy currentBest
                        }
                        else
                        {
                            overallBest.Add(currentBest[0]);
                        }
                    }
                    else if (keepMultiple && currentBest[0].Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan])
                    {
                        match = true;
                        for (int i = 0; i < currentBest.Count; ++i)
                        {
                            if (!overallBest.Contains(currentBest[i]))
                            {
                                overallBest.Add(currentBest[i]);
                            }
                        }
                    }
                    lastProgress = generation;
                }
                else if (keepMultiple && _population[0].Fitness[Criteria.Makespan] == currentBest[0].Fitness[Criteria.Makespan])
                {
                    List<Individual> equals = GetAllEqual(_population[0], _population);
                    for (int i = 0; i < equals.Count; ++i)
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
                                match = true;
                                overallBest.Add(currentBest[i]);
                            }
                        }
                    }
                }
                UpdateStoppingCriteria(generation, overallBest[0].Fitness[Criteria.Makespan], maxGeneration, _functionEvaluations, maxFunctionEvaluations, timeLimit, targetFitness);
                ++generation;
            }
            if (_output)
            {
                Debug_Report(generation, overallBest, currentBest, restarts, improvement, match);
            }
            history.Result = new Result(overallBest, _configuration, generation - 1, _functionEvaluations, DateTime.Now.Subtract(_startTime).TotalSeconds, [_generationStop, _fevalStop, _fitnessStop, _timeStop], restarts);
            return history;
        }
    }
}
