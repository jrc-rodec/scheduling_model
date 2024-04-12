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
            // TODO: update mutation probability
            configuration.MutationProbability = 1.0f / (configuration.NOperations * 3.0f);
        }
    }
}
