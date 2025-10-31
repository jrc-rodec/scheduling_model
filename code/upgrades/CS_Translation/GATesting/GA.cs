using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GATesting
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

        private string _recombinationMethod = "u";
        private string _mutationMethod = "sr";
        private string _mutationRateChangeMethod = "s";
        private string _selectionMethod = "ts";

        DateTime _startTime;
        protected int _functionEvaluations = 0;

        public int FunctionEvaluations { get => _functionEvaluations; set => _functionEvaluations = value; }
        public string RecombinationMethod { get => _recombinationMethod; set => _recombinationMethod = value; }
        public string MutationMethod { get => _mutationMethod; set => _mutationMethod = value; }
        public string MutationRateChangeMethod { get => _mutationRateChangeMethod; set => _mutationRateChangeMethod = value; }

        protected bool _output = false;
        private int[,,] _workerDurations;
        private GAConfiguration _configuration;


        public static bool SORT = true;

        public void Reset()
        {
            _random = new Random();
            _population = new List<Individual>();
            _functionEvaluations = 0;
        }

        public GA(GAConfiguration configuration, bool output, int[,,] workerDurations, string selectionMethod = "ts", string recombinationMethod = "u", string mutationMethod = "sr", string mutationRateChangeMethod = "s")// : base(configuration, output)
        {
            _configuration = configuration;
            _output = output;
            Reset();
            _selectionMethod = selectionMethod;
            _recombinationMethod = recombinationMethod;
            _mutationMethod = mutationMethod;
            Individual.MUTATIONMETHOD = _mutationMethod;
            Individual.RECOMBINATIONMETHOD = _recombinationMethod;
            _mutationRateChangeMethod = mutationRateChangeMethod;
            _workerDurations = workerDurations;
            //List<List<List<int>>> availableWorkers = new List<List<List<int>>>();
            //for(int operation = 0; operation < _workerDurations.GetLength(0); ++operation)
            //{
            //    List<List<int>> operationWorkers = new List<List<int>>();
            //    for(int machine = 0; machine < _workerDurations.GetLength(1); ++machine)
            //    {
            //        List<int> machineWorkers = new List<int>();
            //        for(int worker = 0; worker < _workerDurations.GetLength(2); ++worker)
            //        {
            //            if (_workerDurations[operation,machine,worker] > 0)
            //            {
            //                machineWorkers.Add(worker);
            //            }
            //        }
            //        operationWorkers.Add(machineWorkers);
            //    }
            //    availableWorkers.Add(operationWorkers);
            //}
            //Individual.AvailableWorkers = availableWorkers;
            // TODO: update mutation probability
            configuration.MutationProbability = 1.0f / (configuration.NOperations * 3.0f);
        }

        class TimeSlot
        {
            public int Start = 0;
            public int End = 0;

            public TimeSlot(int start, int end)
            {
                Start = start;
                End = end;
            }
            public bool Overlaps(TimeSlot other)
            {
                return Contains(other.Start) || Contains(other.End) || other.Contains(Start) || other.Contains(End);
            }

            public bool Contains(int time)
            {
                return time >= Start && time <= End;
            }
        }

        private TimeSlot EarliestFit(List<TimeSlot> slots, TimeSlot slot)
        {
            for (int i = 1; i < slots.Count; ++i)
            {
                if (slots[i - 1].End <= slot.Start && slots[i].Start >= slot.End)
                {
                    return slots[i - 1];
                }
            }
            return slots.Last();
        }

        private void EvaluateSlots(Individual nIndividual)
        {

            Individual individual = (Individual)nIndividual;
            // TODO: test
            if (!individual.Feasible)
            {
                individual.Fitness[Criteria.Makespan] = float.MaxValue;
                return;
            }
            int[] nextOperation = new int[_configuration.NJobs];
            List<TimeSlot>[] endOnMachines = new List<TimeSlot>[_configuration.NMachines];
            for (int i = 0; i < endOnMachines.Length; ++i)
            {
                endOnMachines[i] = new List<TimeSlot>();
                endOnMachines[i].Add(new TimeSlot(0, 0));
            }
            List<TimeSlot>[] endOfWorkers = new List<TimeSlot>[_workerDurations.GetLength(2)];
            for (int i = 0; i < endOfWorkers.Length; ++i)
            {
                endOfWorkers[i] = new List<TimeSlot>();
                endOfWorkers[i].Add(new TimeSlot(0, 0));
            }
            //int[] endOnMachines = new int[_configuration.NMachines];
            // TODO: need to keep record of worker times in a different format
            //int[] endOfWorkers = new int[_workerDurations.GetLength(2)];
            int[] endTimes = new int[_configuration.JobSequence.Length];
            for (int i = 0; i < individual.Sequence.Length; ++i)
            {
                int job = individual.Sequence[i];
                int operation = nextOperation[job];
                ++nextOperation[job];
                int startIndex = _configuration.JobStartIndices[job] + operation;
                int machine = individual.Assignments[startIndex];

                int worker = individual.Workers[startIndex];

                int duration = _workerDurations[startIndex, machine, worker];
                if (duration == 0)
                {
                    Console.WriteLine("0 DURATION, INVALID ASSIGNMENT!");
                }
                int offset = 0;
                int minStartJob = 0;
                if (operation > 0)
                {
                    if (endTimes[startIndex - 1] > offset)
                    {
                        // need to wait for previous operation to finish
                        offset = endTimes[startIndex - 1];
                    }
                }
                if (endOnMachines[machine].Count > 0 && endOnMachines[machine].Last().End >= offset)
                {
                    // need to wait for machine to be available
                    // TODO: could check for earlier timeslot here, but complicated with worker 
                    offset = endOnMachines[machine].Last().End;
                }
                // TODO: don't check if the worker is finished, check if the worker is free in the timespan instead
                // (could be on other machine at a later time already)
                if (endOfWorkers[worker].Count > 0)
                {
                    TimeSlot workerEarliest = EarliestFit(endOfWorkers[worker], new TimeSlot(offset, offset + duration));
                    if (workerEarliest.End >= offset)
                    //if (endOfWorkers[worker].Last().End >= offset)
                    {
                        // need to wait for worker to be ready
                        //offset = endOfWorkers[worker].Last().End;
                        offset = workerEarliest.End;
                    }
                }

                //offset = Math.Max(Math.Max(0, endTimes[startIndex - 1] - endOnMachines[machine]), endTimes[startIndex - 1] - endOfWorkers[worker]);
                //minStartJob = endTimes[startIndex - 1];
                //}
                endTimes[startIndex] = offset + duration;
                //endTimes[startIndex] = Math.Max(endOnMachines[machine], endOfWorkers[worker]) + duration + offset;
                endOnMachines[machine].Add(new TimeSlot(offset, offset + duration));
                endOfWorkers[worker].Add(new TimeSlot(offset, offset + duration));
                if (SORT)
                {
                    endOfWorkers[worker] = endOfWorkers[worker].OrderBy(o => o.Start).ToList();
                }
                //endOnMachines[machine] = endTimes[startIndex];
                //endOfWorkers[worker] = endTimes[startIndex];
            }
            individual.Fitness[Criteria.Makespan] = endTimes.Max();
            _functionEvaluations++;
        }

        private void Evaluate(Individual nIndividual)
        {
            // just redirect for now
            EvaluateSlots(nIndividual);
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
            _selectionMethod = "ts"; // no other selection method for now
            if(_selectionMethod == "ts")
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
            return null; // TODO
        }

        protected bool HasInvalidAssignment(Individual individual)
        {
            for (int i = 0; i < individual.Assignments.Length; ++i)
            {
                if (_configuration.Durations[i, individual.Assignments[i], individual.Workers[i]] == 0)
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
            for (int i = 0; i < populationSize; ++i)
            {
                Individual individual = new Individual(_population);
                Evaluate(individual);
                //CheckIndividual(individual);
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

        protected float UpdateMutationProbability2(float p, int generation, int lastProgress, int maxWait, float maxP)
        {
            return (float)p+(((float)(generation-lastProgress) / (float)maxWait) * (maxP-p));
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

        public void Merge(List<Individual> a, List<Individual> b)
        {
            for (int i = 0; i < b.Count; ++i)
            {
                if (!a.Contains(b[i]))
                {
                    a.Add(new Individual(b[i]));
                }
            }
            b.Clear();
        }
        
        public History Run(int maxGeneration, int timeLimit, float targetFitness, int maxFunctionEvaluations, bool keepMultiple, int collectInstances = 0)
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
            if (_configuration.AdaptElitismRate)
            {
                elitism = Math.Max(0, populationSize * _configuration.MaxElitismRate * _configuration.DurationVariety);
            }
            if (_configuration.AdaptTournamentSize) { 
                tournamentSize = (int)Math.Max(1, (int)populationSize * _configuration.MaxTournamentRate * _configuration.DurationVariety);
            }
            int maxWait = _configuration.RestartGenerations;
            int restarts = 0;
            List<Individual> overallBest = new List<Individual>();
            List<Individual> overallTemp = GetAllEqual(_population[0], _population);
            Merge(overallBest, overallTemp);
            List<Individual> currentBest = new List<Individual>();
            List<Individual> currentTemp = GetAllEqual(_population[0], _population);
            Merge(currentBest, currentTemp);
            int lastProgress = 0;
            int generation = 0;
            _functionEvaluations = 0;
            _startTime = DateTime.Now;

            _output = false;

            History history = new History();
            bool improvement = false;
            bool match = false;
            UpdateStoppingCriteria(generation, overallBest[0].Fitness[Criteria.Makespan], maxGeneration, _functionEvaluations, maxFunctionEvaluations, timeLimit, targetFitness);
            history.Update(overallBest, currentBest, mutationProbability, _population, DateTime.Now.Subtract(_startTime), restarts, _functionEvaluations);

            List<Individual> collection = new List<Individual>();


            while (!_generationStop && !_fevalStop && !_fitnessStop && !_timeStop)
            {
                if (_configuration.AdaptMutationProbability && generation > 0 && lastProgress < generation - 1)
                {
                    if(_mutationRateChangeMethod == "s")
                    {
                        mutationProbability = UpdateMutationProbability(mutationProbability, generation, lastProgress, maxWait, maxMutationProbability);
                    } else
                    {
                        mutationProbability = UpdateMutationProbability2(_configuration.MutationProbability, generation, lastProgress, maxWait, maxMutationProbability);
                    }

                    if(maxMutationProbability > 0 && !_configuration.DoRestarts)
                    {
                        mutationProbability = Math.Min(mutationProbability, maxMutationProbability);
                    }
                }
                if (_configuration.DoRestarts && mutationProbability > maxMutationProbability)
                {
                    Individual localMinimum = currentBest[0];
                    // Note: shouldn't technically be necessary
                    if (localMinimum.Fitness[Criteria.Makespan] < overallBest[0].Fitness[Criteria.Makespan])
                    {
                        overallBest.Clear();
                        improvement = true;
                        currentTemp = GetAllEqual(localMinimum, _population);
                        currentBest.Clear();
                        Merge(currentBest, currentTemp);
                        if (keepMultiple)
                        {
                            overallTemp.Clear();
                            foreach (Individual individual in currentBest)
                            {
                                if (individual.Fitness[Criteria.Makespan] == localMinimum.Fitness[Criteria.Makespan] && !overallBest.Contains(individual))
                                {
                                    overallTemp.Add(individual);
                                }
                            }
                            Merge(overallBest, overallTemp);
                        }
                        else
                        {
                            overallBest.Add(new Individual(localMinimum));
                        }
                        //overallBest = currentBest;
                    }
                    else if (keepMultiple && localMinimum.Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan] && !overallBest.Contains(localMinimum))
                    {
                        currentTemp = GetAllEqual(localMinimum, _population);
                        currentBest.Clear();
                        Merge(currentBest, currentTemp);
                        currentBest.Add(localMinimum);
                        overallTemp.Clear();
                        foreach (Individual individual in currentBest)
                        {
                            if (!overallBest.Contains(individual))
                            {
                                overallTemp.Add(individual);
                            }
                        }
                        Merge(overallBest, overallTemp);
                        //overallBest.Add(localMinimum);
                        match = true;
                    }
                    if (_output)
                    {
                        Debug_Report(generation - 1, overallBest, currentBest, restarts, improvement, match);
                    }
                    int maxPopulationSize = _configuration.MaxPopulationSize;
                    int maxOffspringAmount = (int)(maxPopulationSize * _configuration.OffspringRate);
                    populationSize = (int)Math.Min(maxPopulationSize, _configuration.PopulationSizeGrowthRate * populationSize);
                    offspringAmount = (int)Math.Min(maxOffspringAmount, _configuration.PopulationSizeGrowthRate * offspringAmount);

                    if (_configuration.AdaptElitismRate)
                    {
                        elitism = Math.Max(0, populationSize * _configuration.MaxElitismRate * _configuration.DurationVariety);
                    }
                    if (_configuration.AdaptTournamentSize) { 
                        tournamentSize = (int)Math.Max(1, (int)populationSize * _configuration.MaxTournamentRate * _configuration.DurationVariety);
                    }

                    currentBest.Clear();
                    currentTemp.Clear();
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
                for (int i = 0; i < elitism; ++i)
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
                    if (keepMultiple)
                    {
                        currentTemp = GetAllEqual(_population[0], _population);
                        currentBest.Clear();
                        Merge(currentBest, currentTemp);
                    }
                    else
                    {
                        currentBest.Clear();
                        currentBest.Add(new Individual(_population[0]));
                    }
                    if (currentBest[0].Fitness[Criteria.Makespan] < overallBest[0].Fitness[Criteria.Makespan])
                    {
                        overallBest.Clear();
                        improvement = true;
                        if (keepMultiple)
                        {
                            overallTemp = GetAllEqual(_population[0], _population);
                            overallBest.Clear(); // just to not copy currentBest
                            Merge(overallBest, overallTemp);
                        }
                        else
                        {
                            overallBest.Add(new Individual(currentBest[0]));
                        }
                    }
                    else if (keepMultiple && currentBest[0].Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan])
                    {
                        match = true;
                        overallTemp.Clear();
                        for (int i = 0; i < currentBest.Count; ++i)
                        {
                            if (!overallBest.Contains(currentBest[i]))
                            {
                                overallTemp.Add(currentBest[i]);
                            }
                        }
                        Merge(overallBest, overallTemp);
                    }
                    lastProgress = generation;
                }
                else if (keepMultiple && _population[0].Fitness[Criteria.Makespan] == currentBest[0].Fitness[Criteria.Makespan])
                {
                    List<Individual> equals = GetAllEqual(_population[0], _population);
                    currentTemp.Clear();
                    for (int i = 0; i < equals.Count; ++i)
                    {
                        if (!currentBest.Contains(equals[i]))
                        {
                            currentTemp.Add(equals[i]);
                        }

                    }
                    Merge(currentBest, currentTemp);
                    if (currentBest[0].Fitness[Criteria.Makespan] == overallBest[0].Fitness[Criteria.Makespan])
                    {
                        for (int i = 0; i < currentBest.Count; ++i)
                        {
                            if (!overallBest.Contains(currentBest[i]))
                            {
                                match = true;
                                overallBest.Add(new Individual(currentBest[i]));
                            }
                        }
                    }
                }
                UpdateStoppingCriteria(generation, overallBest[0].Fitness[Criteria.Makespan], maxGeneration, _functionEvaluations, maxFunctionEvaluations, timeLimit, targetFitness);
                history.Update(overallBest, currentBest, mutationProbability, _population, DateTime.Now.Subtract(_startTime), restarts, _functionEvaluations);
                if (collectInstances > 0 && generation % collectInstances == 0)
                {
                    collection.Add(_population[0]);
                }
                ++generation;
            }
            if (_output)
            {
                Debug_Report(generation, overallBest, currentBest, restarts, improvement, match);
            }
            history.Result = new Result(overallBest, _configuration, generation - 1, _functionEvaluations, DateTime.Now.Subtract(_startTime).TotalSeconds, [_generationStop, _fevalStop, _fitnessStop, _timeStop], restarts);
            if(collectInstances > 0 && !collection.Contains(overallBest[0]))
            {
                collection.Add(overallBest[0]);
            }
            history.Collection = collection;
            return history;
        }
    }
}
