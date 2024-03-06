using BenchmarkParsing;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Solver
{
    public class GAConfiguration
    {

        private int[,] _durations;
        private int[] _jobSequence;
        private DecisionVariables _decisionVariables;
        
        private int _populationSize;
        private int _offspringAmount;
        private float _mutationProbability;
        private float _elitismRate;

        private int _restartGenerations;

        public GAConfiguration(BenchmarkParsing.Encoding encoding, DecisionVariables variables)
        {
            _durations = encoding.Durations;
            _jobSequence = encoding.JobSequence;
            _decisionVariables = variables;
        }

    }
}
