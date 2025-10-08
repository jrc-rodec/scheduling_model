using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace Solver
{

    public class WorkerHistory
    {
        private string _name;
        private List<float> _overallBestFitness;
        private List<float> _resetBestHistory;
        private List<int> _nEqualOverallBestSolutions;
        private List<int> _nEqualResetBestSolutions;
        private List<float> _mutationProbability;
        private List<int> _populationSize;
        private List<float> _averagePopulationFitness;
        private List<double> _updateTimeStamps;
        private List<int> _updateFevals;
        private List<int> _restarts;
        private WorkerResult _result;

        public WorkerHistory()
        {
            _overallBestFitness = new List<float>();
            _resetBestHistory = new List<float>();
            _mutationProbability = new List<float>();
            _populationSize = new List<int>();
            _nEqualOverallBestSolutions = new List<int>();
            _nEqualResetBestSolutions = new List<int>();
            _averagePopulationFitness = new List<float>();
            _updateTimeStamps = new List<double>();
            _updateFevals = new List<int>();
            _restarts = new List<int>();
            _name = "";

        }

        public void Update(List<WFJSSPIndividual> overallBest, List<WFJSSPIndividual> currentBest, float p, List<WFJSSPIndividual> population, TimeSpan runtime, int restartCount, int fevals)
        {
            _overallBestFitness.Add(overallBest[0].Fitness[Criteria.Makespan]);
            _resetBestHistory.Add(currentBest[0].Fitness[Criteria.Makespan]);
            _nEqualOverallBestSolutions.Add(overallBest.Count);
            _nEqualResetBestSolutions.Add(currentBest.Count);
            _mutationProbability.Add(p);
            _populationSize.Add(population.Count);
            _updateTimeStamps.Add(runtime.TotalMilliseconds / 1000.0);
            _updateFevals.Add(fevals);
            _restarts.Add(restartCount);
            float average = 0.0f;
            for (int i = 0; i < population.Count; ++i)
            {
                average += population[i].Fitness[Criteria.Makespan];
            }
            _averagePopulationFitness.Add(average / population.Count);
        }

        public void ToFile(string path)
        {
            string text = JsonConvert.SerializeObject(this);
            File.AppendAllText(@path, text);
        }

        public List<float> OverallBestFitness { get => _overallBestFitness; }
        public List<float> ResetBestHistory { get => _resetBestHistory; }
        public List<int> NEqualOverallBestSolutions { get => _nEqualOverallBestSolutions; }
        public List<int> NEqualResetBestSolutions { get => _nEqualResetBestSolutions; }
        public List<float> MutationProbability { get => _mutationProbability; }
        public List<int> PopulationSize { get => _populationSize; }
        public List<float> AveragePopulationFitness { get => _averagePopulationFitness; }
        
        public WorkerResult Result { get => _result; set => _result = value; }
        public string Name { get => _name; set => _name = value; }
        public List<double> UpdateTimeStamps { get => _updateTimeStamps; }
        public List<int> UpdateFevals { get => _updateFevals; }
        public List<int> Restarts { get => _restarts; set => _restarts = value; }
    }
    public class History
    {

        // TODO: multiobjective
        private string _name = "";
        private List<float> _overallBestFitness;
        private List<float> _resetBestHistory;
        private List<int> _nEqualOverallBestSolutions;
        private List<int> _nEqualResetBestSolutions;
        private List<float> _mutationProbability;
        private List<int> _populationSize;
        private List<float> _averagePopulationFitness;
        private List<double> _updateTimeStamps;
        private List<int> _updateFevals;
        private List<int> _restarts;
        private Result _result;

        public History()
        {
            _overallBestFitness = new List<float>();
            _resetBestHistory = new List<float>();
            _mutationProbability = new List<float>();
            _populationSize = new List<int>();
            _nEqualOverallBestSolutions = new List<int>();
            _nEqualResetBestSolutions = new List<int>();
            _averagePopulationFitness = new List<float>();
            _updateTimeStamps = new List<double>();
            _restarts = new List<int>();

        }

        public void Update(List<Individual> overallBest, List<Individual> currentBest, float p, List<Individual> population, TimeSpan runtime, int restartCount, int fevals)
        {
            _overallBestFitness.Add(overallBest[0].Fitness[Criteria.Makespan]);
            _resetBestHistory.Add(currentBest[0].Fitness[Criteria.Makespan]);
            _nEqualOverallBestSolutions.Add(overallBest.Count);
            _nEqualResetBestSolutions.Add(currentBest.Count);
            _mutationProbability.Add(p);
            _populationSize.Add(population.Count);
            _updateTimeStamps.Add(runtime.TotalMilliseconds / 1000.0);
            _updateFevals.Add(fevals);
            _restarts.Add(restartCount);
            float average = 0.0f;
            for(int i = 0; i < population.Count; ++i)
            {
                average += population[i].Fitness[Criteria.Makespan];
            }
            _averagePopulationFitness.Add(average / population.Count);
        }

        public void ToFile(string path)
        {
            string text = JsonConvert.SerializeObject(this);
            File.AppendAllText(@path, text);
        }

        public List<float> OverallBestFitness { get => _overallBestFitness; }
        public List<float> ResetBestHistory { get => _resetBestHistory; }
        public List<int> NEqualOverallBestSolutions { get => _nEqualOverallBestSolutions;  }
        public List<int> NEqualResetBestSolutions { get => _nEqualResetBestSolutions;  }
        public List<float> MutationProbability { get => _mutationProbability;  }
        public List<int> PopulationSize { get => _populationSize;  }
        public List<float> AveragePopulationFitness { get => _averagePopulationFitness;  }
        public List<double> UpdateTimeStamps { get => _updateTimeStamps; }
        public List<int> UpdateFevals { get => _updateFevals; }
        public Result Result { get => _result; set => _result = value; }
        public string Name { get => _name; set => _name = value; }
        public List<int> Restarts { get => _restarts; set => _restarts = value; }
    }
}
