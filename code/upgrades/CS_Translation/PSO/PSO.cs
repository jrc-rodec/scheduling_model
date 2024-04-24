using GAWorkerProcess;
using NetMQ;
using NetMQ.Sockets;
using Solver;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace PSO
{
    public class PSO
    {

        private int _nExperiments = 5;
        private int _fevalBudget = 50000;
        private int[,] _durations;
        private ResponseSocket _server;
        private RequestSocket _client; // for finished messages
        private PublisherSocket _publisher;

        public PSO(int[,] durations, int nExperiments, int fevalBudget) 
        {
            _durations = durations;
            _nExperiments = nExperiments;
            _fevalBudget = fevalBudget;
        }

        private void Publish(string topic, RequestMessage message)
        {
            if(_publisher.IsDisposed) return;
            MessageConverter<RequestMessage> messageConverter = new MessageConverter<RequestMessage>();
            _publisher.SendMoreFrame(topic).SendFrame(messageConverter.ToByteArray(message));
            // NOTE: subscriber code for worker:
            /*
             using (var subscriber = new SubscriberSocket())
            {
                subscriber.Connect("tcp://127.0.0.1:5556");
                subscriber.Subscribe("A");

                while (true)
                {
                    var topic = subscriber.ReceiveFrameString();
                    var msg = subscriber.ReceiveFrameString();
                    Console.WriteLine("From Publisher: {0} {1}", topic, msg);
                }
            } 
             */
        }

        private Process StartProcess(string[] args)
        {
            string workerPath = "";
            Process process = new Process();
            process.StartInfo.UseShellExecute = false;

            process.StartInfo.FileName = workerPath;

            StringBuilder argumentText = new StringBuilder();
            for (int i = 0; i < args.Length; ++i)
            {
                argumentText.Append(args[i] + " ");
            }
            // Remove trailing whitespace
            argumentText.Remove(argumentText.Length - 2, argumentText.Length - 1);

            process.StartInfo.Arguments = argumentText.ToString();
            process.StartInfo.CreateNoWindow = true;

            process.Start();
            return process;
        }

        private void ProcessFinished(object? sender, EventArgs e)
        {
            // needed?
        }

        public void Run(int[,] durations, int swarmSize, int nIterations, string benchmarkFile)
        {
            _client = new RequestSocket();
            _client.Connect("tcp://127.0.0.1:5557");
            
            _publisher = new PublisherSocket();
            _publisher.Bind("tcp://5556");
            // Start Worker Processes (nExperiments for now) here, subscribe to different topics
            Process[] workers = new Process[_nExperiments];
            for(int i = 0; i < _nExperiments; ++i)
            {
                string[] args = { i.ToString(), benchmarkFile };
                Process process = StartProcess(args);
                process.Exited += new EventHandler(ProcessFinished);
                workers[i] = process;
            }

            Random random = new Random();
            int particleSize = 0;
            List<List<int>> machinesPerOperation = new List<List<int>>();
            for(int i = 0; i < durations.GetLength(0); ++i) 
            {
                List<int> machines = new List<int>();
                for(int j = 0; j < durations.GetLength(1); ++j)
                {
                    if (durations[i,j] > 0)
                    {
                        machines.Add(j);
                        ++particleSize;
                    }
                }
                machinesPerOperation.Add(machines);
            }
            Particle.STRUCTURE = new (int, int)[particleSize];
            int structureIndex = 0;
            for(int i = 0; i < machinesPerOperation.Count; ++i)
            {
                for(int j = 0; j < machinesPerOperation[i].Count; ++j)
                {
                    Particle.STRUCTURE[structureIndex++] = (i, machinesPerOperation[i][j]);
                }
            }
            float[] lowerBounds = new float[particleSize];
            float[] upperBounds = new float[particleSize];
            for(int i = 0; i < upperBounds.Length; ++i)
            {
                upperBounds[i] = 1.0f;
                lowerBounds[i] = 0.0f;
            }

            Particle[] swarm = new Particle[swarmSize];
            float[] bestGlobalPosition = new float[particleSize];
            float bestGlobalFitness = float.MaxValue;

            float minVelocity = -1.0f;
            float maxVelocity = 1.0f;

            float w = 0.729f;
            float c1 = 1.49f;
            float c2 = 1.49f;
            float r1, r2;

            //TODO: add time limit
            
            for(int i = 0; i < swarmSize; ++i)
            {
                float[] randomPosition = new float[particleSize];
                for(int j = 0; j < randomPosition.Length; ++j)
                {
                    randomPosition[j] = (maxVelocity - minVelocity) * (float)random.NextDouble() + minVelocity;
                }
                Particle p = new Particle(randomPosition);
                swarm[i] = p;
            }
            Evaluate(swarm);

            for(int iteration = 0; iteration < nIterations; ++iteration)
            {
                for(int i = 0; i < swarmSize; ++i)
                {
                    Particle current = swarm[i];
                    float[] newVelocities = new float[current.Velocities.Length];
                    for(int j = 0; j < current.Velocities.Length; ++j)
                    {
                        r1 = (float)random.NextDouble();
                        r2 = (float)random.NextDouble();
                        float velocity = (w * current.Velocities[j]) + (c1 * r1 * (current.BestPosition[j] - current.Position[j])) + (c2 * r2 * (bestGlobalPosition[j] - current.Position[j]));
                        newVelocities[j] = Math.Min(Math.Max(velocity, minVelocity), maxVelocity);
                    }
                    newVelocities.CopyTo(current.Velocities, 0);
                    float[] newPosition = new float[current.Position.Length];
                    for(int j = 0; j < current.Position.Length; ++j)
                    {
                        float position = current.Position[j] + current.Velocities[j];
                        newPosition[j] = Math.Min(Math.Max(position, lowerBounds[j]), upperBounds[j]);
                    }
                    newPosition.CopyTo(current.Position, 0);
                    Evaluate(current); // Evaluate immediately to use updated fitness values for the other particle updates
                    if(current.BestFitness < bestGlobalFitness)
                    {
                        current.BestPosition.CopyTo(bestGlobalPosition, 0);
                        bestGlobalFitness = current.BestFitness;
                    }
                }
            }
            // kill worker processes
            for(int i = 0; i < workers.Length; ++i)
            {
                workers[i].Kill();
                workers[i].Close();
            }
            
            _publisher.Close();
            _client.Close();
            _server.Close();
        }

        private int[,] GenerateDurationMatrix(float[] position)
        {
            Random random = new Random();
            int[,] result = new int[_durations.GetLength(0), _durations.GetLength(1)]; // should be filled with 0s
            for (int i = 0; i < position.Length; ++i)
            {
                int operation = Particle.STRUCTURE[i].Item1;
                int machine = Particle.STRUCTURE[i].Item2;
                if (random.NextDouble() < position[i])
                {
                    result[operation, machine] = _durations[operation, machine];
                }
            }
            // check feasibility
            for (int i = 0; i < result.GetLength(0); ++i)
            {
                List<int> values = new List<int>();
                float max = 0.0f;
                for(int j = 0; j < result.GetLength(1); ++j)
                {
                    if (result[i, j] > 0)
                    {
                        values.Append(result[i, j]);
                        if (result[i,j] > max)
                        {
                            max = result[i, j];
                        }
                    }
                }
                // if no assignments are available after randomization, activate the most probable one
                // if multiple assignments have the same probability, choose randomly between those
                if (values.Count == 0)
                {
                    List<int> maxProbability = new List<int>();
                    for (int j = 0; j < _durations.GetLength(1); ++j)
                    {
                        if(result[i,j] == max)
                        {
                            maxProbability.Add(j);
                        }
                    }
                    int activate = maxProbability[random.Next(maxProbability.Count)];
                    result[i, activate] = _durations[Particle.STRUCTURE[i].Item1,activate];
                }
            }
            return result;
        }

        public void Evaluate(Particle particle)
        {
            List<int[,]> experiments = new List<int[,]>();
            int fevalLimit = _fevalBudget / _nExperiments;

            for (int experiment = 0; experiment < _nExperiments; ++experiment)
            {
                // TODO: make sure every generated duration matrix is feasible
                int[,] result = GenerateDurationMatrix(particle.Position);
                // gather information about the experiment setup for parameters (maybe add experiment class)

                experiments.Add(result);

                // start the optimization in a separate process (zeromq)
                // publish data to topics in order
                RequestMessage request = new RequestMessage();
                request.durations = result;
                request.fevalLimit = fevalLimit;
                Publish(experiment.ToString(), request);
            }
            float fitness = float.MaxValue;
            List<Individual> best = new List<Individual>();
            // wait for the processes to finish
            MessageConverter<ResponseMessage> messageConverter = new MessageConverter<ResponseMessage>();
            for(int i = 0; i < experiments.Count; ++i)
            {
                Msg msg = new Msg();
                _client.Receive(ref msg);
                Span<byte> response = msg.Slice();
                byte[] byteResponse = response.ToArray();
                // cast response
                ResponseMessage result = messageConverter.FromByteArray(byteResponse);
                // read result values
                // TODO
                History history = result.history;
                string senderTopic = result.senderTopic;
                Result optimizationResult = result.history.Result;
                // just makespan for now
                float makespan = optimizationResult.Fitness[Criteria.Makespan];
                if(makespan < fitness)
                {
                    fitness = makespan;
                    best = optimizationResult.Best;
                } else if(makespan == fitness)
                {
                    // merge
                    foreach(Individual individual in optimizationResult.Best)
                    {
                        if (!best.Contains(individual))
                        {
                            best.Add(individual);
                        }
                    }
                }
            }

            particle.Fitness = fitness;
            particle.UpdateBestPosition();
        }

        public void Evaluate(Particle[] swarm)
        {
            foreach (Particle particle in swarm)
            {
                Evaluate(particle);
            }
        }
    }
}
