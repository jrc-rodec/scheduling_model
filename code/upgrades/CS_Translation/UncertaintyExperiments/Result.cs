using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UncertaintyExperiments
{
    public class Result
    {
        private List<Individual> _best;
        private GAConfiguration _parameters;
        private int _generations;
        private int _functionEvaluations;
        private double _timeInSeconds;
        private bool[] _triggeredStop;
        private int _nRestarts;

        public Result(List<Individual> best, GAConfiguration config, int generations, int functionEvaluations, double timeInSeconds, bool[] triggers, int nRestarts)
        {
            _best = best;
            _parameters = config;
            _generations = generations;
            _functionEvaluations = functionEvaluations;
            _timeInSeconds = timeInSeconds;
            _triggeredStop = triggers;
            _nRestarts = nRestarts;
        }

        public List<Individual> Best { get => _best; }
        public GAConfiguration Parameters { get => _parameters; }
        public int Generations { get => _generations; }
        public int FunctionEvaluations { get => _functionEvaluations; }
        public double TimeInSeconds { get => _timeInSeconds; }
        public bool[] TriggeredStop { get => _triggeredStop; }
        public int NRestarts { get => _nRestarts; }
        public Dictionary<Criteria, float> Fitness { get => _best[0].Fitness; }

        public override string ToString()
        {
            StringBuilder sb = new StringBuilder();
            sb.Append("Best Fitness: " + _best[0].Fitness[Criteria.Makespan] + " (" + _best.Count + " equal solution(s))\n");
            sb.Append("Time in Seconds: " + _timeInSeconds + ", Generations: " + _generations + ", Function Evaluations: " + _functionEvaluations + ", Restarts: " + _nRestarts + "\n");
            sb.Append("Stops triggered:\nMax. Generations: " + _triggeredStop[0] + ", Function Evaluations: " + _triggeredStop[1] + ", Target Fitness: " + _triggeredStop[2] + ", Time Limit: " + _triggeredStop[3]);
            return sb.ToString();
        }
    }
}
