
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;


namespace GA_Uncertainty
{

    public class IndividualLoader {

        private class JSONResultList
        {
            public List<JSONResult> results { get; set; }
        }
        private class JSONResult
        {
            public String instance { get; set; }
            public float fitness { get; set; }
            public List<int> sequence { get; set; }
            public List<int> machines { get; set; }
            public List<int> worker { get; set; }
        }

        private static List<string> ReadFile(string path){
            List<string> lines = new List<string>();
            StreamReader reader = new StreamReader(path);
            try {
                while(reader.Peek() >= 0){
                    lines.Add(reader.ReadLine());
                }
            } catch (IOException e) {
                Console.WriteLine("Error reading file:\n" + e.Message);
            } finally {
                reader.Close();
            }
            return lines;
        }

        private static List<Individual> ParseJson(string path, string benchmarkPath, bool translateOperations){
            List<string> lines = ReadFile(path);
            string text = lines[0];
            JSONResultList data = JsonSerializer.Deserialize<JSONResultList>(text);
            //List<JSONResult> data = JsonSerializer.Deserialize<List<JSONResult>>(text);
            List<Individual> solutions = new List<Individual>();
            
            foreach (JSONResult result in data.results)
            {
                Console.WriteLine(result.instance);
                // load benchmark data for context
                BenchmarkParser parser = new BenchmarkParser();
                Encoding encoding = parser.ParseBenchmark(benchmarkPath + result.instance);
                DecisionVariables variables = new DecisionVariables(encoding);
                GAConfiguration configuration = new GAConfiguration(encoding, variables);
                Individual.Durations = encoding.Durations;
                Individual.AvailableWorkers = encoding.GetAllWorkersForAllOperations();
                Individual.AvailableMachines = encoding.GetAllMachinesForAllOperations();
                Individual.JobSequence = encoding.JobSequence;
                Individual individual = new Individual(true);
                
                // fill Individual
                individual.Sequence = result.sequence.ToArray();
                if (translateOperations) { 
                    // sequence values are currently the start times
                    for(int i = 0; i < individual.Sequence.Length; ++i)
                    {
                        // TODO: translate GA to start times instead of start times to sequence
                    }
                }
                individual.Assignments = result.machines.ToArray();
                individual.Workers = result.worker.ToArray();
                
                // for testing
                Evaluation evaluation = new Makespan(configuration, encoding.Durations);
                evaluation.Evaluate(individual);
                // double check if everything is loaded correctly
                if (individual.Fitness[Criteria.Makespan] != result.fitness)
                {
                    Console.WriteLine("SOMETHING DOESN'T ADD UP!");
                }

                Evaluation processingTimes = new AverageRobustness(configuration, encoding.Durations, 10, 0.4f);
                float[] machineProbabilities = new float[result.machines.Max()+1];
                for(int i = 0; i < machineProbabilities.Length; ++i)
                {
                    machineProbabilities[i] = 0.1f;
                }
                Evaluation randomDelays = new RandomDelayRobustnessEvaluation(configuration, encoding.Durations, machineProbabilities, 10);
                processingTimes.Evaluate(individual);
                randomDelays.Evaluate(individual);
                Console.WriteLine(result.fitness + " | " + individual.Fitness[Criteria.Makespan] + " | " + individual.Fitness[Criteria.AverageRobustness] + " | " + individual.Fitness[Criteria.RandomDelays]);
            }


            return solutions;
        }

        private static List<Individual> ParseCSV(string path){
            List<string> lines = ReadFile(path);
            List<Individual> solutions = new List<Individual>();
            // find benchmark ? load all ? 
            Individual individual = new Individual(true);
            // fill individual

            return solutions;
        }

        public static void LoadResults(string benchmarkPath, string resultPath)
        {
            LoadResults(benchmarkPath, resultPath, false);
        }
        public static void LoadResults(string benchmarkPath, string resultPath, bool translateOperations){
            List<Individual> individual;
            if(resultPath.EndsWith(".json")){
                individual = ParseJson(resultPath, benchmarkPath, translateOperations);
            } else {
                individual = ParseCSV(resultPath);
            }

        }
    }
    public class Individual //: Individual
    {
        public static List<List<Criteria>> ranking;

        private int[] _workers;
        public static List<List<List<int>>> AvailableWorkers;
        public static int[,,] Durations;
        protected int[] _sequence;
        protected int[] _assignments;
        protected Dictionary<Criteria, float> _fitness;
        protected bool _feasible = true;

        public static int[] JobSequence;
        public static List<List<int>> AvailableMachines;
        public static float MaxDissimilarity;
        public static int MaxInitializationAttemps = 100; // TODO add parameter
        public static float DistanceAdjustmentRate = 0.75f; // TODO add parameter
        public static bool UseDissimilarity = true;
        public int[] Workers { get => _workers; set => _workers = value; }

        public Dictionary<Criteria, float> Fitness { get => _fitness; set => _fitness = value; }
        public bool Feasible { get => _feasible; set => _feasible = value; }
        public int[] Sequence { get => _sequence; set => _sequence = value; }
        public int[] Assignments { get => _assignments; set => _assignments = value; }

        public static List<Individual> RankedSort(List<Individual> individuals)
        {
            //TODO: adapt for multiple in the same rank + test speed, also for unknown amount of ranks
            return [.. individuals
                        .OrderBy(m => m.Fitness[ranking[0][0]])
                        .ThenBy(r => r.Fitness[ranking[1][0]])];
        }

        public static int CompareRanked(Individual a, Individual b){
            foreach(List<Criteria> rank in ranking){
                // TODO: enable more than one per rank
                if(a.Fitness[rank[0]] < b.Fitness[rank[0]]){
                    return 1;
                }
                if(a.Fitness[rank[0]] > b.Fitness[rank[0]]){
                    return -1;
                }
            }
            return 0;
        }

        public Individual DeepCopy()
        {
            Individual copy = new Individual(false);
            for(int i = 0; i < _workers.Length; ++i)
            {
                copy._workers[i] = _workers[i];
                copy._sequence[i] = _sequence[i];
                copy._assignments[i] = _assignments[i];
            }

            return copy;
        }
        public Individual(bool randomize)// : base(randomize)
        {
            _workers = new int[JobSequence.Length];
            _sequence = new int[JobSequence.Length];
            _assignments = new int[JobSequence.Length];
            _fitness = new Dictionary<Criteria, float>();
            if (randomize)
            {
                // randomize
                Randomize();
            }
        }

        public Individual(Individual other)// : base(other)
        {
            _sequence = new int[other._sequence.Length];
            other._sequence.CopyTo(_sequence, 0);
            _assignments = new int[other._assignments.Length];
            other._assignments.CopyTo(_assignments, 0);
            _fitness = other.Fitness;
            _workers = new int[other._workers.Length];
            other._workers.CopyTo(_workers, 0);
        }

        public Individual(List<Individual> population) : this(true)
        {
            if (population.Count < 1 || !UseDissimilarity)
            {
                Randomize();
            }
            else
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
        }

        public float GetDissimilarity(Individual other)
        {
            float result = 0.0f;
            for (int i = 0; i < _sequence.Length; ++i)
            {
                if (_assignments[i] != other._assignments[i])
                {
                    result += AvailableMachines[i].Count;
                }
                if (_sequence[i] != other._sequence[i])
                {
                    ++result;
                }
                if (_workers[i] != other._workers[i])
                {
                    result += AvailableWorkers[i][other._assignments[i]].Count;
                }
            }
            return result;
        }

        public static void DetermineMaxDissimiarilty()
        {
            MaxDissimilarity = 0.0f;
            // For every operation
            for (int i = 0; i < AvailableMachines.Count; ++i)
            {
                MaxDissimilarity += AvailableMachines[i].Count;
                int maxWorkers = 0;
                //maxWorkers = AvailableWorkers.Count();
                // for every machine available for the operation
                for (int j = 0; j < AvailableMachines[i].Count; ++j)
                {
                    if (AvailableWorkers[i][AvailableMachines[i][j]].Count > maxWorkers)
                    {
                        maxWorkers = AvailableWorkers[i][AvailableMachines[i][j]].Count;
                    }
                }
                MaxDissimilarity += maxWorkers;
            }
            MaxDissimilarity += JobSequence.Length;
        }

        protected float Average(float[] values)
        {
            float sum = 0;
            for (int i = 0; i < values.Length; ++i)
            {
                sum += values[i];
            }
            return sum / values.Length;
        }

        public Individual(Individual parentA, Individual parentB) : this(false)
        {
            //NOTE: Code duplication
            HashSet<int> jobs = new HashSet<int>(JobSequence);

            List<int> a = new List<int>();
            List<int> b = new List<int>();
            Random random = new Random();
            for (int i = 0; i < jobs.Count; ++i)
            {
                if (random.NextDouble() < 0.5)
                {
                    a.Add(jobs.ElementAt(i));
                }
                else
                {
                    b.Add(jobs.ElementAt(i));
                }
            }

            int bIndex = 0;
            List<int> parentBValues = new List<int>();
            for (int i = 0; i < parentB._sequence.Length; ++i)
            {
                if (b.Contains(parentB._sequence[i]))
                {
                    parentBValues.Add(parentB._sequence[i]);
                }
            }
            for (int i = 0; i < parentA._sequence.Length; ++i)
            {
                if (a.Contains(parentA._sequence[i]))
                {
                    _sequence[i] = parentA._sequence[i];
                }
                else
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

        protected void ShuffleSequence()
        {
            Random random = new Random();
            for (int i = 0; i < _sequence.Length; ++i)
            {
                int index = random.Next(_sequence.Length);
                int tmp = _sequence[index];
                _sequence[index] = _sequence[i];
                _sequence[i] = tmp;
            }
        }

        protected void Randomize()
        {
            Random random = new Random();
            JobSequence.CopyTo(_sequence, 0);
            ShuffleSequence();
            for (int i = 0; i < _assignments.Length; ++i)
            {
                _assignments[i] = AvailableMachines[i][random.Next(0, AvailableMachines[i].Count)];
            }
            _workers = new int[JobSequence.Length];
            for (int i = 0; i < _workers.Length; ++i)
            {
                _workers[i] = AvailableWorkers[i][_assignments[i]][random.Next(0, AvailableWorkers[i][_assignments[i]].Count)];
            }
        }

        public static void DetermineMaxDissimilarity()
        {
            MaxDissimilarity = 0.0f;
            for (int i = 0; i < AvailableMachines.Count; ++i)
            {
                MaxDissimilarity += AvailableMachines[i].Count;
            }
            MaxDissimilarity += JobSequence.Length;
            for (int i = 0; i < AvailableWorkers.Count; ++i)
            {
                MaxDissimilarity += AvailableWorkers[i].Count;
            }
        }

        public void Mutate(float p)
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
                    } while (_sequence[swap] == _sequence[i] && attempts < 100); // make sure it does not swap with itself
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
                        int attempts = 0;
                        do
                        {
                            swap = random.Next(AvailableMachines[i].Count);
                            ++attempts;
                        } while (AvailableMachines[i][swap] == _assignments[i] && attempts < 100);
                        _assignments[i] = AvailableMachines[i][swap];
                        if (!AvailableWorkers[i][_assignments[i]].Contains(_workers[i]))
                        {
                            // no longer feasible - randomly choose new worker
                            _workers[i] = AvailableWorkers[i][_assignments[i]][random.Next(AvailableWorkers[i][_assignments[i]].Count)];
                        }
                    }
                }
                if (random.NextDouble() < p)
                {
                    if (AvailableWorkers[i][_assignments[i]].Count > 1)
                    {
                        int swap;
                        int attempts = 0;
                        do
                        {
                            swap = random.Next(AvailableWorkers[i][_assignments[i]].Count);
                            ++attempts;
                        } while (AvailableWorkers[i][_assignments[i]][swap] == _workers[i] && attempts < 100);
                        _workers[i] = AvailableWorkers[i][_assignments[i]][swap];
                    }
                }
            }
        }

        public bool Equals(Individual other)
        {
            for (int i = 0; i < _sequence.Length; ++i)
            {
                if (_sequence[i] != other._sequence[i] || _assignments[i] != other._assignments[i] || _workers[i] != other._workers[i])
                {
                    return false;
                }
            }
            return true;
        }
    }

}
