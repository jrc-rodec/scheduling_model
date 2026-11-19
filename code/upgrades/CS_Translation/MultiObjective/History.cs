using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MultiObjective
{
    public class History
    {
        private string _name;
        private List<List<IndividualSummary>> _overallBestFitness;
        private List<List<IndividualSummary>> _resetBestHistory;
        private List<int> _nEqualOverallBestSolutions;
        private List<int> _nEqualResetBestSolutions;
        private List<float> _mutationProbability;
        private List<int> _populationSize;
        private List<Dictionary<Criteria, float>> _averagePopulationFitness;
        private List<int> _fevalHistory;
        private List<double> _updateTimeStamps;
        private List<int> _restarts;
        private Result _result;

        public History()
        {
            _overallBestFitness = new List<List<IndividualSummary>>();
            _resetBestHistory = new List<List<IndividualSummary>>();
            _mutationProbability = new List<float>();
            _populationSize = new List<int>();
            _nEqualOverallBestSolutions = new List<int>();
            _nEqualResetBestSolutions = new List<int>();
            _averagePopulationFitness = new List<Dictionary<Criteria, float>>();
            _updateTimeStamps = new List<double>();
            _restarts = new List<int>();
            _fevalHistory = new List<int>();
            _name = "";

        }

        public void Update(List<Individual> overallBest, List<Individual> currentBest, float p, List<Individual> population, TimeSpan runtime, int restartCount, int fevals)
        {
            List<IndividualSummary> best = new List<IndividualSummary>();
            foreach(Individual individual in overallBest)
            {
                best.Add(individual.ToSummary());
            }
            List<IndividualSummary> resetBest = new List<IndividualSummary>();
            foreach (Individual individual in currentBest)
            {
                resetBest.Add(individual.ToSummary());
            }
            _overallBestFitness.Add(best);
            _resetBestHistory.Add(resetBest);
            _nEqualOverallBestSolutions.Add(overallBest.Count);
            _nEqualResetBestSolutions.Add(currentBest.Count);
            _mutationProbability.Add(p);
            _populationSize.Add(population.Count);
            _updateTimeStamps.Add(runtime.TotalMilliseconds / 1000.0);
            _restarts.Add(restartCount);
            _fevalHistory.Add(fevals);
            float average = 0.0f;
            List<Criteria> criterias = population[0].Fitness.Keys.ToList();
            Dictionary<Criteria, float> averages = new Dictionary<Criteria, float>();
            foreach(Criteria c in criterias)
            {
                averages[c] = 0.0f;
            }
            for (int i = 0; i < population.Count; ++i)
            {
                foreach(Criteria c in population[i].Fitness.Keys.ToList())
                {
                    averages[c] += population[i].Fitness[c];
                }
                //average += population[i].Fitness[Criteria.Makespan];
            }
            foreach(Criteria c in averages.Keys.ToList())
            {
                averages[c] /= population.Count;
            }
            _averagePopulationFitness.Add(averages);
        }

        public void ToFile(string path)
        {
            string text = JsonConvert.SerializeObject(this);
            File.AppendAllText(@path, text);
        }

        public List<List<IndividualSummary>> OverallBestFitness { get => _overallBestFitness; }
        public List<List<IndividualSummary>> ResetBestHistory { get => _resetBestHistory; }
        public List<int> NEqualOverallBestSolutions { get => _nEqualOverallBestSolutions; }
        public List<int> NEqualResetBestSolutions { get => _nEqualResetBestSolutions; }
        public List<float> MutationProbability { get => _mutationProbability; }
        public List<int> PopulationSize { get => _populationSize; }
        public List<Dictionary<Criteria, float>> AveragePopulationFitness { get => _averagePopulationFitness; }
        public Result Result { get => _result; set => _result = value; }
        public string Name { get => _name; set => _name = value; }
        public List<int> Restarts { get => _restarts; set => _restarts = value; }
        public List<double> UpdateTimeStamps { get => _updateTimeStamps; set => _updateTimeStamps = value; }
        public List<int> FevalHistory { get => _fevalHistory; set => _fevalHistory = value; }
    }
}
