using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Transactions;

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

        private int _functionEvaluations = 0;

        public int FunctionEvaluations { get => _functionEvaluations; set => _functionEvaluations = value; }

        public GA(GAConfiguration configuration)
        {
            _configuration = configuration;
            Reset();
        }

        public void Reset()
        {
            _random = new Random();
            _population = new List<Individual>();
            _functionEvaluations = 0;
        }

        private Individual TournamentSelection(int tournamentSize)
        {
            if(tournamentSize == 0)
            {
                tournamentSize = Math.Max(1, _population.Count / 10);
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
            List<List<Dictionary<string, int>>> gaps = new List<List<Dictionary<string, int>>>();
            for(int i = 0; i < _configuration.NMachines; ++i){
                gaps.Add(new List<Dictionary<string, int>>());
            }
            int[] endTimesOnMachines = new int[_configuration.NMachines];
            int[] endTimesOfOperations = new int[_configuration.NOperations];
            int[] nextOperation = new int[_configuration.NJobs];

            for(int i = 0; i < individual.Sequence.Length; ++i){
                int job = 0;
                int operation = nextOperation[job]++;
                int operationIndex = _configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[operationIndex];
                int duration = _configuration.Durations[operation, machine];
                bool inserted = false;
                for(int j = 0; j < gaps[machine].Count; ++j){
                    Dictionary<string, int> gap = gaps[machine][j];
                    if(gap["end"] - gap["start"] >= duration){
                        if(operationIndex == 0 || _configuration.JobSequence[operationIndex-1] == _configuration.JobSequence[operationIndex] && endTimesOfOperations[operationIndex-1] <= gap["end"] - duration){
                            // gap can be used
                            inserted = true;
                            int start = 0;
                            if(operationIndex != 0){
                                start = Math.Min(gap["start"], endTimesOfOperations[operationIndex-1]);
                            }
                            int end = start + duration;
                            if(gap["end"] - end > 0){
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
                            for(int k = 0; k < _configuration.JobSequence.Length && !found; ++k){
                                if(_configuration.JobSequence[k] == jobSwap){
                                    swapStartIndex = k;
                                    found = true;
                                }
                            }
                            swapOperationIndex = gap["preceedsOperation"] - swapStartIndex;
                            int count = 0;
                            int swapIndividualIndex = 0;
                            found = false;
                            for(int k = 0; k < individual.Sequence.Length && !found; ++k){
                                if(individual.Sequence[k] == jobSwap){
                                    if(count == swapOperationIndex){
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
                if(!inserted){
                    int jobMinStart = 0;
                    if(operationIndex != 0 && _configuration.JobSequence[operationIndex-1] == _configuration.JobSequence[operationIndex]){
                        jobMinStart = endTimesOfOperations[operationIndex-1];
                    }
                    if(jobMinStart > endTimesOnMachines[machine]){
                        gaps[machine].Add(new Dictionary<string, int>(){["start"] = jobMinStart, ["end"] = jobMinStart + duration, ["preceedsOperation"] = operationIndex});
                        endTimesOnMachines[machine] = jobMinStart + duration;
                    } else {
                        endTimesOnMachines[machine] += duration;
                    }
                }
                endTimesOfOperations[operationIndex] = endTimesOnMachines[machine];
            }
        }

        private void Evaluate(Individual individual)
        {
            if (!individual.Feasible)
            {
                individual.Fitness[Criteria.Makespan] = float.MaxValue;
                return;
            }
            int[] nextOperation = new int[_configuration.NJobs];
            int[] endOnMachines = new int[_configuration.NMachines];
            int[] endTimes = new int[_configuration.JobSequence.Length];
            for(int i = 0; i <  individual.Sequence.Length; ++i)
            {
                int job = individual.Sequence[i];
                int operation = nextOperation[job]++;
                int startIndex = _configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[startIndex];
                int duration = _configuration.Durations[startIndex, machine];
                int offset = 0;
                int minStartJob = 0;
                if(operation > 0)
                {
                    offset = Math.Max(0, endTimes[startIndex - 1] - endOnMachines[machine]);
                    minStartJob = endTimes[startIndex - 1];
                }
                endTimes[startIndex] = endOnMachines[machine] + duration + offset;
                endOnMachines[machine] = endTimes[startIndex];
            }
            individual.Fitness[Criteria.Makespan] = endTimes.Max();
            _functionEvaluations++;
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
            _population.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
        }

        private void CreateOffspring(List<Individual> offspring, int offspringAmount, int tournamentSize, float mutationProbability)
        {
            offspring.Clear();
            //offspring = new List<Individual>();
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
        private void UpdateStoppingCriteria(int generation, float bestFitness, int maxGeneration, int functionEvaluations, int maxFunctionEvaluations)
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

        private void MutateMachineVector(Individual individual){
            float p = 1.0f / individual.Assignments.Length;
            for(int i = 0; i < individual.Assignments.Length; ++i)
            {
                if(_random.NextDouble() < p)
                {
                    if (Individual.AvailableMachines[i].Count > 1)
                    {
                        int swap;
                        do
                        {
                            swap = Individual.AvailableMachines[i][_random.Next(Individual.AvailableMachines[i].Count)];
                        } while (swap != individual.Assignments[i]);
                        individual.Assignments[i] = swap;
                    }
                }
            }
        }

        private void MutateSequenceVector(Individual individual)
        {
            float p = 1.0f / individual.Sequence.Length;
            for(int i = 0; i < individual.Sequence.Length; ++i)
            {
                if(_random.NextDouble() < p)
                {
                    int swap;
                    do
                    {
                        swap = _random.Next(individual.Sequence.Length);
                    } while (swap == i || individual.Sequence[i] == individual.Sequence[swap]);
                    int tmp = individual.Sequence[i];
                    individual.Sequence[i] = individual.Sequence[swap];
                    individual.Sequence[swap] = tmp;
                }
            }
        } 

        private Individual SimulatedAnnealing(Individual individual)
        {
            int nMachineMutations = 5;
            int nSequenceMutations = 20;
            float initialT = 20.0f;
            float alpha = 0.8f;
            int nT = 7;
            float T = initialT;
            Individual best = new Individual(individual);
            for(int i = 0; i < nMachineMutations; ++i)
            {
                Individual y = new Individual(individual);
                if(i > 0)
                {
                    MutateMachineVector(y);
                }
                for(int j = 0; j < nT; ++j)
                {
                    Individual yTmp = new Individual(y);
                    Evaluate(yTmp);
                    for(int k = 0; k < nSequenceMutations; ++k)
                    {
                        Individual z = new Individual(y);
                        MutateSequenceVector(z);
                        Evaluate(z);
                        if (z.Fitness[Criteria.Makespan] < yTmp.Fitness[Criteria.Makespan])
                        {
                            yTmp = z;
                        }
                    }
                    if (yTmp.Fitness[Criteria.Makespan] < y.Fitness[Criteria.Makespan])
                    {
                        y = yTmp;
                    }
                    if (y.Fitness[Criteria.Makespan] < best.Fitness[Criteria.Makespan])
                    {
                        best = y;
                    }
                    T *= alpha;
                }
                T = initialT;
            }
            return best;
        }

        private Individual LocalSearch(List<Individual> currentBest)
        {
            //NOTE: since currentBest is now a list, somehow one of the individuals would need to be chosen for simulated annealing?
            return SimulatedAnnealing(currentBest[0]);
        }

        public void Debug_Report(int generation, List<Individual> best, int restarts, float mutationProbability)
        {
            Console.WriteLine(generation + " Best: " + best[0].Fitness[Criteria.Makespan] + "(" + best.Count + " equal solutions, " + restarts + " restarts, current p: " + mutationProbability + ")");
        }

        //TODO: change to public History Run()
        public List<Individual> Run(int maxGeneration, int timeLimit, float targetFitness, int maxFunctionEvaluations)
        {
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
            int functionEvaluations = 0;
            UpdateStoppingCriteria(generation, overallBest[0].Fitness[Criteria.Makespan], maxGeneration, functionEvaluations, maxFunctionEvaluations);
            while(!_generationStop && !_fevalStop && !_fitnessStop && !_timeStop)
            {
                Debug_Report(generation, overallBest, restarts, mutationProbability);
                if(generation > 0 && lastProgress < generation - 1)
                {
                    mutationProbability = UpdateMutationProbability(mutationProbability, generation, lastProgress, maxWait, maxMutationProbability);
                }
                if(mutationProbability > maxMutationProbability){
                    //Note: local minimum
                    /*Console.WriteLine("Local Search");
                    Individual localMinimum = LocalSearch(currentBest);
                    Console.WriteLine("Local Search Done");*/
                    Individual localMinimum = currentBest[0];
                    // only necessary if local search is conducted
                    if(localMinimum.Fitness[Criteria.Makespan] < overallBest[0].Fitness[Criteria.Makespan]){
                        overallBest = currentBest;
                    } else if(localMinimum.Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan] && !overallBest.Contains(localMinimum))
                    {
                        overallBest.Add(localMinimum);
                    }
                    int maxPopulationSize = 400; // TODO: parameter
                    int maxOffspringAmount = maxPopulationSize * 4; // TODO: parameter
                    populationSize = (int)Math.Min(maxPopulationSize, _configuration.PopulationSizeGrowthRate * populationSize);
                    offspringAmount = (int)Math.Min(maxOffspringAmount, _configuration.PopulationSizeGrowthRate * offspringAmount);

                    elitism = Math.Max(0, populationSize * _configuration.MaxElitismRate * _configuration.DurationVariety);
                    tournamentSize = (int)Math.Max(1, (int)populationSize * _configuration.MaxTournamentRate * _configuration.DurationVariety);

                    // NOTE: also sorts the population
                    CreatePopulation(populationSize);
                    mutationProbability = _configuration.MutationProbability;
                    lastProgress = generation;
                    restarts++;
                }

                CreateOffspring(offspring, offspringAmount, tournamentSize, mutationProbability);
                //offspring.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
                List<Individual> pool = offspring;
                for(int i = 0; i < elitism; ++i)
                {
                    // NOTE: population always be sorted at this point
                    pool.Add(_population[i]);
                }
                pool.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
                _population = new List<Individual>();
                for (int i = 0; i < populationSize; ++i)
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
                    lastProgress = generation;
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
                UpdateStoppingCriteria(generation, overallBest[0].Fitness[Criteria.Makespan], maxGeneration, functionEvaluations, maxFunctionEvaluations);
                ++generation;
            }
            return overallBest;
        }
        
    }
}
