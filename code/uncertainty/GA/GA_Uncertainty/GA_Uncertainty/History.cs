﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Text.Json;
using Newtonsoft.Json;

namespace GA_Uncertainty
{
    public class History
    {
        private string _name;
        private List<Dictionary<Criteria, float>> _overallBestFitness;
        private List<Dictionary<Criteria, float>> _resetBestHistory;
        private List<int> _nEqualOverallBestSolutions;
        private List<int> _nEqualResetBestSolutions;
        private List<float> _mutationProbability;
        private List<int> _populationSize;
        private List<double> _updateTimestamps;
        private List<Dictionary<Criteria, float>> _averagePopulationFitness;
        private Result _result;

        public History()
        {
            _overallBestFitness = new List<Dictionary<Criteria, float>>();
            _resetBestHistory = new List<Dictionary<Criteria, float>>();
            _mutationProbability = new List<float>();
            _populationSize = new List<int>();
            _nEqualOverallBestSolutions = new List<int>();
            _nEqualResetBestSolutions = new List<int>();
            _averagePopulationFitness = new List<Dictionary<Criteria, float>>();
            _updateTimestamps = new List<double>();
            _name = "";

        }

        public void Update(List<Individual> overallBest, List<Individual> currentBest, float p, List<Individual> population, TimeSpan runtime)
        {
            // TODO: parameter to determine which criteria are needed
            Dictionary<Criteria, float> overallBestDict = new Dictionary<Criteria, float>{
                {Criteria.Makespan, overallBest[0].Fitness[Criteria.Makespan]},
                {Criteria.AverageRobustness, overallBest[0].Fitness[Criteria.AverageRobustness]}
            };
            _overallBestFitness.Add(overallBestDict);
            Dictionary<Criteria, float> resetBest = new Dictionary<Criteria, float>{
                {Criteria.Makespan, overallBest[0].Fitness[Criteria.Makespan]},
                {Criteria.AverageRobustness, overallBest[0].Fitness[Criteria.AverageRobustness]}
            };
            _resetBestHistory.Add(resetBest);
            //_overallBestFitness.Add(overallBest[0].Fitness[Criteria.Makespan]);
            //_resetBestHistory.Add(currentBest[0].Fitness[Criteria.Makespan]);
            _nEqualOverallBestSolutions.Add(overallBest.Count);
            _nEqualResetBestSolutions.Add(currentBest.Count);
            _mutationProbability.Add(p);
            _populationSize.Add(population.Count);
            _updateTimestamps.Add(runtime.TotalMilliseconds / 1000.0);
            float averageMakespan = 0.0f;
            float averageAverageRobustness = 0.0f;
            for (int i = 0; i < population.Count; ++i)
            {
                averageMakespan += population[i].Fitness[Criteria.Makespan];
                averageAverageRobustness += population[i].Fitness[Criteria.AverageRobustness];
            }
            Dictionary<Criteria, float> averageBest = new Dictionary<Criteria, float>{
                {Criteria.Makespan, averageMakespan / population.Count},
                {Criteria.AverageRobustness, averageAverageRobustness / population.Count}
            };
            _averagePopulationFitness.Add(averageBest);
        }

        public void ToFile(string path)
        {
            string text = JsonConvert.SerializeObject(this);
            File.AppendAllText(@path, text);
        }

        public List<Dictionary<Criteria, float>> OverallBestFitness { get => _overallBestFitness; }
        public List<Dictionary<Criteria, float>> ResetBestHistory { get => _resetBestHistory; }
        public List<int> NEqualOverallBestSolutions { get => _nEqualOverallBestSolutions; }
        public List<int> NEqualResetBestSolutions { get => _nEqualResetBestSolutions; }
        public List<float> MutationProbability { get => _mutationProbability; }
        public List<int> PopulationSize { get => _populationSize; }
        public List<Dictionary<Criteria, float>> AveragePopulationFitness { get => _averagePopulationFitness; }
        public Result Result { get => _result; set => _result = value; }
        public string Name { get => _name; set => _name = value; }
    }
}
