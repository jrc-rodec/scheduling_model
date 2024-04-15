using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Solver
{
    public class WFJSSPGA : GA
    {
        private int[,,] _workerDurations;

        public WFJSSPGA(GAConfiguration configuration, bool output, int[,,] workerDurations) : base(configuration, output)
        {
            _workerDurations = workerDurations;
            List<List<List<int>>> availableWorkers = new List<List<List<int>>>();
            for(int operation = 0; operation < _workerDurations.GetLength(0); ++operation)
            {
                List<List<int>> operationWorkers = new List<List<int>>();
                for(int machine = 0; machine < _workerDurations.GetLength(1); ++machine)
                {
                    List<int> machineWorkers = new List<int>();
                    for(int worker = 0; worker < _workerDurations.GetLength(2); ++worker)
                    {
                        if (_workerDurations[operation,machine,worker] > 0)
                        {
                            machineWorkers.Add(worker);
                        }
                    }
                    operationWorkers.Add(machineWorkers);
                }
                availableWorkers.Add(operationWorkers);
            }
            WFJSSPIndividual.AvailableWorkers = availableWorkers;
            // TODO: update mutation probability
            configuration.MutationProbability = 1.0f / (configuration.NOperations * 3.0f);
        }

        protected override void Adjust(Individual individual)
        {
            WFJSSPIndividual wIndividual = (WFJSSPIndividual)individual;
            // TODO
        }

        protected override void Evaluate(Individual individual)
        {
            WFJSSPIndividual wIndividual = (WFJSSPIndividual)individual;
            // TODO
        }
    }
}
