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

        private readonly int[,] _durations;
        private readonly int[] _jobSequence;
        private readonly int[] _jobStartIndices;
        private readonly DecisionVariables _decisionVariables;
        
        private int _populationSize = 5;
        private int _offspringAmount = 20;
        private float _mutationProbability;
        private float _maxMutationProbability = 1.0f;//0.5f;//1.0f;
        private float _elitismRate = 0.1f;
        private int _tournamentSize = 1;
        private float _populationGrowthRate = 2.0f;
        private float _maxElitism = 0.1f; // 1.0f // scale freely between , and + if 1
        private float _maxTournamentRate = 0.2f; // 1.0f // NOTE: 0 -> TournamentSize = 1 -> Random Selection, 1 -> TournamentSize = PopulationSize -> Rank Selection
        private int _restartGenerations = 50;

        public GAConfiguration(BenchmarkParsing.Encoding encoding, DecisionVariables variables)
        {
            _durations = encoding.Durations;
            _jobSequence = encoding.JobSequence;

            _mutationProbability = 1.0f / (2.0f * _jobSequence.Length);
            _decisionVariables = variables;

            // NOTE: this should probably be moved somewhere else
            Individual.Durations = _durations;
            Individual.JobSequence = _jobSequence;
            Individual.AvailableMachines = encoding.GetMachinesForAllOperations();
            Individual.DetermineMaxDissimiarilty();

            _jobStartIndices = new int[NJobs];
            int operation = 0;
            _jobStartIndices[operation++] = 0;
            for(int i = 1; i < JobSequence.Length; ++i)
            {
                if (JobSequence[i] != JobSequence[i - 1])
                {
                    _jobStartIndices[operation++] = i;
                }
            }
        }

        public GAConfiguration(BenchmarkParsing.Encoding encoding, DecisionVariables variables, int populationSize, int offspringAmount, float maxMutationProbability, float maxElitismRate, float maxTournamentRate, float populationGrowthRate, int restartGenerations) : this(encoding, variables)
        {
            _populationSize = populationSize;
            _offspringAmount = offspringAmount;
            _maxMutationProbability = maxMutationProbability;
            _maxElitism = maxElitismRate;
            _maxTournamentRate = maxTournamentRate;
            _populationGrowthRate = populationGrowthRate;
            _restartGenerations = restartGenerations;
            _tournamentSize = Math.Min(1, (int)(variables.DurationVariety * MaxTournamentRate * _populationSize + 0.5f));
            _elitismRate = Math.Min(MaxElitismRate, (int)(variables.DurationVariety * _populationSize + 0.5f));
        }

        public void UpdateDynamicParameters()
        {
            _tournamentSize = Math.Min(1, (int)(_decisionVariables.DurationVariety * MaxTournamentRate * _populationSize + 0.5f));
            _elitismRate = Math.Min(MaxElitismRate, (int)(_decisionVariables.DurationVariety * _populationSize + 0.5f));
        }

        public int[,] Durations => _durations;
        public int[] JobSequence => _jobSequence;
        public float Flexibility => _decisionVariables.Flexibility;
        public float AverageMachines => _decisionVariables.AverageMachines;
        public float DurationVariety => _decisionVariables.DurationVariety;
        public int NOperations => _decisionVariables.NOperations;
        public int NMachines => _decisionVariables.NMachines;
        public int NJobs => _decisionVariables.NJobs;
        public float AverageOperations => _decisionVariables.AverageOperations;
        public float AverageOperationsOnMachines => _decisionVariables.AverageOperationsOnMachines;
        public float TheoreticalMinimumMakespan => _decisionVariables.TheoreticalMinimumMakespan;

        public int PopulationSize { get => _populationSize; set => _populationSize = value; }
        public int OffspringAmount { get => _offspringAmount; set => _offspringAmount = value; }
        public float MutationProbability { get => _mutationProbability; set => _mutationProbability = value; }
        public float ElitismRate { get => _elitismRate; set => _elitismRate = value; }
        public int TournamentSize { get => _tournamentSize; set => _tournamentSize = value; }
        public int RestartGenerations { get => _restartGenerations; set => _restartGenerations = value; }
        public float MaxMutationProbability { get => _maxMutationProbability; set => _maxMutationProbability = value; }
        public float PopulationSizeGrowthRate { get => _populationGrowthRate; set => _populationGrowthRate = value; }
        public float MaxElitismRate { get => _maxElitism; set => _maxElitism = value; }
        public float MaxTournamentRate { get => _maxTournamentRate; set => _maxTournamentRate = value; }

        public int[] JobStartIndices => _jobStartIndices;
    }
}
