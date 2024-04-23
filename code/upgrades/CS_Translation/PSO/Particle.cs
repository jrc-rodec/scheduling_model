using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PSO
{
    public class Particle
    {

        public static (int,int)[] STRUCTURE; // operation index for each value, structure.Length == positions.Length
        private float[] _position;
        private float[] _velocities;
        private float _fitness;

        private float[] _bestPosition;
        private float _bestFitness;

        public Particle(float[] position, float fitness, float[] velocity, float[] bestPosition, float bestFitness)
        {
            _position = position;
            _velocities = velocity;
            _fitness = fitness;
            _bestPosition = bestPosition;
            _bestFitness = bestFitness;
        }

        public Particle(float[] position)
        {
            _position = position;
            _velocities = new float[position.Length];
            _fitness = float.MaxValue;
            _bestPosition = new float[position.Length];
            _position.CopyTo(_bestPosition, 0);
            _bestFitness = float.MaxValue;
        }

        public void UpdateBestPosition()
        {
            if(_fitness < _bestFitness)
            {
                _position.CopyTo(_bestPosition, 0);
                _bestFitness = _fitness;
            }
        }


        public float[] Position { get => _position; set => _position = value; }
        public float[] Velocities { get => _velocities; set => _velocities = value; }
        public float Fitness { get => _fitness; set => _fitness = value; }
        public float[] BestPosition { get => _bestPosition; }
        public float BestFitness { get => _bestFitness; }
    }
}
