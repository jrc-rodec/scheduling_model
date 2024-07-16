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

        protected List<Individual> _population;
        private GAConfiguration _configuration;
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

        public int FunctionEvaluations { get => _functionEvaluations; set => _functionEvaluations = value; }

        protected bool _output = false;
        //public GA() { }
        public GA(GAConfiguration configuration, bool output)
        {
            _configuration = configuration;
            _output = output;
            Reset();
        }

        public void Reset()
        {
            _random = new Random();
            _population = new List<Individual>();
            _functionEvaluations = 0;
        }

        protected Individual TournamentSelection(int tournamentSize)
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

        protected virtual void Adjust(Individual individual)
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

        protected virtual void Evaluate(Individual individual)
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

        protected bool HasInvalidAssignment(Individual individual)
        {
            for(int i = 0; i < individual.Assignments.Length; ++i)
            {
                if (_configuration.Durations[i, individual.Assignments[i]] == 0)
                {
                    return true;
                }
            }
            return false;
        }

        protected void CheckIndividual(Individual individual)
        {
            if (HasInvalidAssignment(individual))
            {
                Console.WriteLine("Something went wrong!");
            }
        }

        protected void CreatePopulation(int populationSize)
        {
            _population = new List<Individual>();
            for(int i = 0; i < populationSize; ++i)
            {
                Individual individual = new Individual(_population);
                // Adjustment step
                Adjust(individual);
                Evaluate(individual);
                //CheckIndividual(individual);
                _population.Add(individual);
            }
            _population.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
        }

        protected void CreateOffspring(List<Individual> offspring, int offspringAmount, int tournamentSize, float mutationProbability)
        {
            offspring.Clear();
            //offspring = new List<Individual>();
            for(int i = 0; i < offspringAmount; ++i)
            {
                Individual o = Recombine(tournamentSize);
                // Adjustment step
                //CheckIndividual(o);
                Adjust(o);
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

        // TODO: Add parameters for missing criteria
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
            for(int i = 0; i <  individuals.Count; ++i)
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

        protected void MutateMachineVector(Individual individual){
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

        protected void MutateSequenceVector(Individual individual)
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

        protected Individual SimulatedAnnealing(Individual individual)
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

        protected Individual LocalSearch(List<Individual> currentBest)
        {
            //NOTE: since currentBest is now a list, somehow one of the individuals would need to be chosen for simulated annealing?
            return SimulatedAnnealing(currentBest[0]);
        }

        public void Debug_Report(int generation, List<Individual> best, List<Individual> currentBest, int restarts, bool improvement, bool match)
        {
            if (improvement)
            {
                Console.ForegroundColor = ConsoleColor.Green;
            } else if (match)
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
            }
            Console.WriteLine("Generation " + generation + " Overall Best: " + best[0].Fitness[Criteria.Makespan] + " (" + best.Count + " equal solutions), Current Run Best " + currentBest[0].Fitness[Criteria.Makespan] + " (" + currentBest.Count + " equal solutions) - " + restarts + " restarts" + ")");
            Console.ResetColor();
        }

        public History Run(int maxGeneration, int timeLimit, float targetFitness, int maxFunctionEvaluations)
        {
            CreatePopulation(_configuration.PopulationSize);
            Console.WriteLine("Created Initial Population");
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

            History history = new History();
            bool improvement = false;
            bool match = false;
            UpdateStoppingCriteria(generation, overallBest[0].Fitness[Criteria.Makespan], maxGeneration, _functionEvaluations, maxFunctionEvaluations, timeLimit, targetFitness);
            Console.WriteLine("Starting Optimization Main Loop");
            while(!_generationStop && !_fevalStop && !_fitnessStop && !_timeStop)
            {
                history.Update(overallBest, currentBest, mutationProbability, _population);
                if(generation > 0 && lastProgress < generation - 1)
                {
                    mutationProbability = UpdateMutationProbability(mutationProbability, generation, lastProgress, maxWait, maxMutationProbability);
                }
                if(mutationProbability > maxMutationProbability){
                    //Note: local minimum
                    /*Console.WriteLine("Local Search");
                    Individual localMinimum = LocalSearch(currentBest);
                    Console.WriteLine("Local Search Done");*/
                    // only necessary if local search is conducted
                    Individual localMinimum = currentBest[0];
                    if(localMinimum.Fitness[Criteria.Makespan] < overallBest[0].Fitness[Criteria.Makespan]){
                        improvement = true;
                        foreach(Individual individual in currentBest)
                        {
                            if (!overallBest.Contains(individual))
                            {
                                overallBest.Add(individual);
                            }
                        }
                        //overallBest = currentBest;
                    } else if(localMinimum.Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan] && !overallBest.Contains(localMinimum))
                    {
                        overallBest.Add(localMinimum);
                        match = true;
                    }
                    if (_output)
                    {
                        Debug_Report(generation-1, overallBest, currentBest, restarts, improvement, match);
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
                //offspring.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan])); // pool gets sorted anyway
                List<Individual> pool = offspring; // NOTE: since no copy is made, could just use offspring as list
                for(int i = 0; i < elitism; ++i)
                {
                    // NOTE: population should always be sorted at this point
                    pool.Add(_population[i]);
                }
                pool.Sort((a, b) => a.Fitness[Criteria.Makespan].CompareTo(b.Fitness[Criteria.Makespan]));
                _population = new List<Individual>();
                for (int i = 0; i < populationSize; ++i)
                {
                    _population.Add(pool[i]);
                }

                if (currentBest.Count == 0 || _population[0].Fitness[Criteria.Makespan] < currentBest[0].Fitness[Criteria.Makespan])
                {
                    currentBest = GetAllEqual(_population[0], _population);
                    if (currentBest[0].Fitness[Criteria.Makespan] < overallBest[0].Fitness[Criteria.Makespan])
                    {
                        improvement = true;
                        overallBest = GetAllEqual(_population[0], _population); // just to not copy currentBest
                    } else if (currentBest[0].Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan])
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
