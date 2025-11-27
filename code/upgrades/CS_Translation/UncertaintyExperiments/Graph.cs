using MathNet.Numerics.Distributions;
using MathNet.Numerics.Statistics;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UncertaintyExperiments
{
    public enum UncertaintySource
    {
        Worker, Machine, Single
    }

    public class Graph
    {
        public float[] StartingTimes
        {
            get => _startingTimes;
            set => _startingTimes = value ?? throw new ArgumentNullException(nameof(value));
        }

        public float[] EndingTimes
        {
            get => _endingTimes;
            set => _endingTimes = value ?? throw new ArgumentNullException(nameof(value));
        }

        public int[] Machines
        {
            get => _machines;
            set => _machines = value ?? throw new ArgumentNullException(nameof(value));
        }

        public int[] Workers
        {
            get => _workers;
            set => _workers = value ?? throw new ArgumentNullException(nameof(value));
        }

        public int[] JobSequence
        {
            get => _jobSequence;
            set => _jobSequence = value ?? throw new ArgumentNullException(nameof(value));
        }

        public float[,,] Durations
        {
            get => _durations;
            //set => _durations = value ?? throw new ArgumentNullException(nameof(value));
        }

        public float[] Buffers
        {
            get => _buffers;
            set => _buffers = value ?? throw new ArgumentNullException(nameof(value));
        }

        public float Makespan
        {
            get => _endingTimes.Max();
        }

        public bool LeftShift
        {
            get => _leftShift;
            set => _leftShift = value;
        }

        private float[] _startingTimes;
        private float[] _endingTimes;
        private int[] _machines;
        private int[] _workers;
        private int[] _jobSequence;
        private readonly float[,,] _durations;
        private float[] _buffers;
        private bool _leftShift;
        private List<Node> _nodes;

        public List<Node> Nodes
        {
            get => _nodes;
            set => _nodes = value ?? throw new ArgumentNullException(nameof(value));
        }

        public List<Node> Roots
        {
            get => _roots;
            set => _roots = value ?? throw new ArgumentNullException(nameof(value));
        }

        public List<Node> Leafs
        {
            get => _leafs;
            set => _leafs = value ?? throw new ArgumentNullException(nameof(value));
        }

        private List<Node> _roots;
        private List<Node> _leafs;

        public Graph(int[] s, int[] m, int[] w, int[] js, float[,,] d, float[] b, bool leftShift = false) 
        {
            _jobSequence = new int[js.Length];
            js.CopyTo(_jobSequence, 0);

            _startingTimes = new float[s.Length];
            _endingTimes = new float[s.Length];
            _machines = new int[m.Length];
            m.CopyTo(_machines, 0);
            _workers = new int[w.Length];
            w.CopyTo(_workers, 0);
            _durations = d;
            _buffers = new float[s.Length];
            if (b.Length == 0)
            {
                for (int i = 0; i < b.Length; i++)
                {
                    _buffers[i] = 0.0f;
                }
            }
            else
            {
                b.CopyTo(_buffers, 0);
            }
            _leftShift = leftShift;
            Node.LeftShift = leftShift;

            Node[] mLast = new Node[_durations.GetLength(1)];
            for(int i = 0; i < mLast.Length; i++)
            {
                mLast[i] = null;
            }
            List<List<Node>> workerWindows = new List<List<Node>>();
            for(int i = 0; i < w.Max() + 1; i++)
            {
                workerWindows.Add(new List<Node>());
            }
            int[] operation = new int[_jobSequence.Length];
            _nodes = new List<Node>();
            List<int> jobStartIndices = new List<int>();
            for(int i = 0; i < _jobSequence.Max()+1; i++)
            {
                jobStartIndices.Add(Array.IndexOf(_jobSequence, i));
            }
            for(int i = 0; i < s.Length; i++)
            {
                _nodes.Add(null);
            }
            for(int i = 0; i < s.Length; i++)
            {
                Node operationParent = null;
                Node machineParent = null;
                Node workerParent = null;
                int current = s[i];
                int operationIndex = jobStartIndices[current] + operation[current];
                float operationTime = 0.0f;
                if (operation[current] > 0)
                {
                    operationTime = _nodes[operationIndex - 1].End;
                    operationParent = _nodes[operationIndex - 1];
                }
                operation[current]++;
                int machine = _machines[operationIndex];
                int worker = _workers[operationIndex];
                float machineTime = 0.0f;// mLast[machine].End;
                if (mLast[machine] != null)
                {
                    machineTime = mLast[machine].End;
                    machineParent = mLast[machine];
                }
                float workerTime = 0.0f;
                if (workerWindows[worker].Count > 0)
                {
                    if (workerWindows[worker].Count == 1)
                    {
                        if (workerWindows[worker][0].Start < _durations[operationIndex,machine,worker])
                        {
                            workerTime = workerWindows[worker][0].End;
                            workerParent = workerWindows[worker][0];
                        }
                    } else
                    {
                        List<Node> sortedWindows = new List<Node>();
                        workerWindows[worker].Sort((a, b) => a.End.CompareTo(b.End));
                        foreach(Node node in workerWindows[worker])
                        {
                            if(node.End >= Math.Max(operationTime, machineTime))
                            {
                                sortedWindows.Add(node);
                            }
                        }
                        if(sortedWindows.Count > 0)
                        {
                            //sortedWindows.Sort((a, b) => a.End.CompareTo(b.End));
                            Node window = null;
                            if (sortedWindows[0].Start < _durations[operationIndex, machine, worker])
                            {
                                for(int j = 1; j < sortedWindows.Count; j++)
                                {
                                    if (sortedWindows[j].Start - sortedWindows[j-1].End >= _durations[operationIndex, machine, worker])
                                    {
                                        window = sortedWindows[j];
                                    }
                                    break;
                                }
                            }
                            if(window != null)
                            {
                                workerTime = window.End;
                                workerParent = window;
                            } else
                            {
                                if (sortedWindows[0].Start < _durations[operationIndex, machine, worker])
                                {
                                    workerTime = sortedWindows.Last().End;
                                    workerParent = sortedWindows.Last();
                                }
                            }
                        } else
                        {
                            workerTime = workerWindows[worker].Last().End;// sortedWindows.Last().End;
                            workerParent = workerWindows[worker].Last();// sortedWindows.Last();
                        }
                    }
                }
                float startTime = Math.Max(operationTime, Math.Max(machineTime, workerTime));
                float endTime = startTime + _durations[operationIndex, machine, worker];
                _startingTimes[operationIndex] = startTime;
                _endingTimes[operationIndex] = endTime;
                _nodes[operationIndex] = new Node(_startingTimes, _endingTimes, _machines, _workers, _jobSequence, _buffers, operationIndex);
                mLast[machine] = _nodes[operationIndex];
                workerWindows[worker].Add(_nodes[operationIndex]);
                _nodes[operationIndex].OperationParent = operationParent;
                _nodes[operationIndex].MachineParent = machineParent;
                _nodes[operationIndex].WorkerParent = workerParent;

                if(machineParent != null)
                {
                    if(machineParent.MachineChild != null)
                    {
                        throw new Exception("Tried to register a wrong child!");
                    }
                    machineParent.MachineChild = _nodes[operationIndex];
                }
                if(workerParent != null)
                {
                    if (workerParent.WorkerChild != null)
                    {
                        _nodes[operationIndex].WorkerChild = workerParent.WorkerChild;
                        _nodes[operationIndex].WorkerChild.WorkerParent = _nodes[operationIndex];
                    }
                    workerParent.WorkerChild = _nodes[operationIndex];
                }
            }
            _roots = new List<Node>();
            _leafs = new List<Node>();
            foreach(Node n in _nodes)
            {
                if(n.OperationParent == null && n.MachineParent == null && n.WorkerParent == null) 
                {
                    _roots.Add(n);
                }
                if(n.OperationChild == null && n.MachineChild == null && n.WorkerChild == null)
                {
                    _leafs.Add(n);
                }
            }
        }

        public Graph(float[] s, float[] e, int[] m, int[] w, int[] js, float[,,] d, float[] b, bool leftShift = false)
        {
            _startingTimes = new float[s.Length];
            s.CopyTo(_startingTimes, 0);
            _endingTimes = new float[e.Length];
            e.CopyTo(_endingTimes, 0);
            _machines = new int[m.Length];
            m.CopyTo(_machines, 0);
            _workers = new int[w.Length];
            w.CopyTo(_workers, 0);
            _jobSequence = new int[js.Length];
            js.CopyTo(_jobSequence, 0);
            _durations = d;
            /*_durations = new float[s.Length, m.Max() + 1, w.Max() + 1];
            for (int i = 0; i < _durations.GetLength(0); i++)
            {
                for (int j = 0; j < _durations.GetLength(1); j++)
                {
                    for (int k = 0; k < _durations.GetLength(2); k++)
                    {
                        _durations[i, j, k] = d[i, j, k];
                    }
                }
            }*/
            //d.CopyTo(_durations, 0);
            _buffers = new float[s.Length];
            if (b.Length == 0)
            {
                for (int i = 0; i < b.Length; i++)
                {
                    _buffers[i] = 0.0f;
                }
            } else
            {
                b.CopyTo(_buffers, 0);
            }
            _leftShift = leftShift;
            Node.LeftShift = leftShift;
            _nodes = new List<Node>();
            for (int i = 0; i < s.Length; i++)
            {
                _nodes.Add(new Node(_startingTimes, _endingTimes, _machines, _workers, _jobSequence, _buffers, i));
            }
            _roots = new List<Node>();
            for (int i = 0; i < _nodes.Count; i++)
            {
                _nodes[i].AddNeighbours(_machines, _workers, _jobSequence, _nodes, i);
                if (_nodes[i].Parents.Count == 0)
                {
                    _roots.Add(_nodes[i]);
                }
            }

            _leafs = new List<Node>();
            for (int i = 0; i < _nodes.Count; i++)
            {
                _nodes[i].AddNeighbours(_machines, _workers, _jobSequence, _nodes, i);
                if (_nodes[i].Children.Count == 0)
                {
                    _leafs.Add(_nodes[i]);
                }
            }
        }

        public Dictionary<string, dynamic> GetVectors()
        {
            Dictionary<string, dynamic> vectors = new Dictionary<string, dynamic>();
            float[] s = new float[_startingTimes.Length];
            _startingTimes.CopyTo(s, 0);
            float[] e = new float[_endingTimes.Length];
            _endingTimes.CopyTo(e, 0);
            int[] m = new int[_machines.Length];
            _machines.CopyTo(m, 0);
            int[] w = new int[_workers.Length];
            _workers.CopyTo(w, 0);
            float[] b = new float[_buffers.Length];
            _buffers.CopyTo(b, 0);
            vectors["s"] = s;
            vectors["e"] = e;
            vectors["m"] = m;
            vectors["w"] = w;
            vectors["b"] = b;
            return vectors;
        }

        public Dictionary<string, float> StructureData()
        {
            float[] inDegrees = new float[_nodes.Count];
            float[] outDegrees = new float[_nodes.Count];
            float[] predecessors = new float[_nodes.Count];
            float[] successors = new float[_nodes.Count];
            float[] naturalBuffers = new float[_nodes.Count];

            for (int i = 0; i < _nodes.Count; i++)
            {
                inDegrees[i] = _nodes[i].Parents.Count;
                outDegrees[i] = _nodes[i].Children.Count;
                predecessors[i] = _nodes[i].CountPredecessors();
                successors[i] = _nodes[i].CountSuccessors();
                float maxParentEnd = 0.0f;
                foreach (Node parent in _nodes[i].Parents)
                {
                    if (parent.End > maxParentEnd)
                    {
                        maxParentEnd = parent.End;
                    }
                }
                naturalBuffers[i] = _nodes[i].Start - maxParentEnd; // maybe should be average?
            }

            Dictionary<string, float> result = new Dictionary<string, float>();
            result["muInDegree"] = inDegrees.Average();
            result["sigmaInDegree"] = (float)inDegrees.StandardDeviation();
            result["muOutDegree"] = outDegrees.Average();
            result["sigmaOutDegree"] = (float)outDegrees.StandardDeviation();
            result["muPredecessors"] = predecessors.Average();
            result["sigmaPredecessors"] = (float)predecessors.StandardDeviation();
            result["muSuccessors"] = successors.Average();
            result["sigmaSuccessors"] = (float)successors.StandardDeviation();
            result["muNaturalBuffers"] = naturalBuffers.Average();
            result["sigmaNaturalBuffers"] = (float)naturalBuffers.StandardDeviation();

            return result;
        }

        public float RealDuration(float d, Tuple<float, float> uncertaintyParameters)
        {
            //Beta random = new Beta(uncertaintyParameters.Item1, uncertaintyParameters.Item2);

            //return (float)(d * (1.0 + random.Sample()));
            return (float)(d + (d * (float)Beta.Sample(uncertaintyParameters.Item1, uncertaintyParameters.Item2)));
        }

        private void AddChild(Node current, List<Node> openList, List<Node> closedList)
        {
            if (openList.Contains(current) || closedList.Contains(current))
            {
                return;
            }

            foreach (Node parent in current.Parents)
            {
                if (!openList.Contains(parent) && !closedList.Contains(parent))
                {
                    AddChild(parent, openList, closedList);
                }
            }
            openList.Add(current);
        }

        public void Update()
        {
            List<Node> openList = new List<Node>();
            List<Node> closedList = new List<Node>();
            openList.AddRange(_roots);
            while (openList.Count > 0)
            {
                Node current = openList[0];
                openList.RemoveAt(0);
                closedList.Add(current);
                foreach (Node child in current.Children)
                {
                    AddChild(child, openList, closedList);
                }
                current.UpdateValues();
            }
            for (int i = 0; i < _endingTimes.Length; i++)
            {
                _startingTimes[i] = _nodes[i].Start;
                _endingTimes[i] = _nodes[i].End;
                _buffers[i] = _nodes[i].Buffer;
            }
        }

        private void AddChildFirst(Node current, List<Node> openList, List<Node> closedList)
        {
            if (openList.Contains(current) || closedList.Contains(current))
            {
                return;
            }

            foreach (Node parent in current.Parents)
            {
                if (!openList.Contains(parent) && !closedList.Contains(parent))
                {
                    AddChildFirst(parent, openList, closedList);
                }
            }
            openList.Insert(0, current);
            //openList.Add(current);
        }

        public void PrintAll(Node current, List<Node> openList, List<Node> closedList)
        {
            openList.Remove(current);
            closedList.Add(current);
            if (_roots.Contains(current))
            {
                Console.Write("End at: " + current.End);
                Console.WriteLine("\nNEW ROOT:");
            }
            Console.Write(current.Operation + "->");

            foreach (Node child in current.Children)
            {
                AddChildFirst(child, openList, closedList);
            }
            if (openList.Count > 0)
            {
                current = openList[0];
                PrintAll(current, openList, closedList);
            }
            else
            {
                Console.WriteLine("End at: " + current.End);
                Console.WriteLine("\nFinished.");
            }

        }

        public void PrintPaths()
        {
            List<Node> openList = new List<Node>();
            openList.AddRange(_roots);
            List<Node> closedList = new List<Node>();
            Node current = openList[0];
            PrintAll(current, openList, closedList);
        }

        private List<List<Tuple<float, float>>> GenerateEvents(float[,] parameters)
        {
            List<List<Tuple<float, float>>> events = new List<List<Tuple<float, float>>>();
            Random random = new Random();
            float makespan = _endingTimes.Max();
            for (int i = 0; i < parameters.GetLength(0); i++)
            {
                List<Tuple<float, float>> currentEvents = new List<Tuple<float, float>>();
                float t = 0.0f;
                //MathNet.Numerics.Distributions.Exponential
                float r = (float)Exponential.Sample(parameters[i, 0]);
                while (r > t && r < makespan)
                {
                    //MathNet.Numerics.Distributions.Weibull
                    float duration = (float)Weibull.Sample(parameters[i, 1], parameters[i, 2]);
                    currentEvents.Add(new Tuple<float, float>(r, duration));
                    t = r + duration;
                    r = (float)Exponential.Sample(random, parameters[i, 0]);
                }

                currentEvents.Sort((a, b) => a.Item1.CompareTo(b.Item1));
                events.Add(currentEvents);
            }
            return events;
        }

        private int FindAffectedOperation(float start, float end, int machine = -1, int worker = -1)
        {
            int[] search;
            int find;
            if (machine == -1)
            {
                // worker unavailability
                search = _workers;
                find = worker;
            }
            else
            {
                // machine breakdown
                search = _machines;
                find = machine;
            }

            List<int> indices = new List<int>();
            for (int i = 0; i < search.Length; i++)
            {
                if (search[i] == find)
                {
                    if (_startingTimes[i] <= end && start <= _endingTimes[i])
                    {
                        indices.Add(i);
                    }
                }
            }

            if (indices.Count == 0)
            {
                return -1;
            }
            int earliest = indices[0];
            for (int i = 0; i < indices.Count; i++)
            {
                if (_startingTimes[indices[i]] < _startingTimes[earliest])
                {
                    earliest = indices[i];
                }
            }
            return earliest;
        }

        private List<Tuple<int, Tuple<float, float>>> GenerateAllEvents(float[,] up)
        {
            List<List<Tuple<float, float>>> events = GenerateEvents(up);
            List<Tuple<int, Tuple<float, float>>> allEvents = new List<Tuple<int, Tuple<float, float>>>();
            for (int i = 0; i < events.Count; i++)
            {
                for (int j = 0; j < events[i].Count; j++)
                {
                    allEvents.Add(new Tuple<int, Tuple<float, float>>(i, events[i][j]));
                }
            }
            allEvents.Sort((a, b) => a.Item2.Item1.CompareTo(b.Item2.Item1));
            return allEvents;
        }

        public void SimulateMachineBreakdown()
        {
            int nMachines = _machines.Max() + 1;
            float makespan = _endingTimes.Max();
            float lambda = (1.0f / nMachines) / makespan;
            float[,] up = new float[nMachines, 3];
            for (int i = 0; i < nMachines; i++)
            {
                //MathNet.Numerics.Distributions.ContinuousUniform
                float mlam = lambda * (float)ContinuousUniform.Sample(0.9, 1.1);
                float alpha = (float)ContinuousUniform.Sample(makespan * 0.1f, makespan * 0.2f);
                up[i, 0] = mlam;
                up[i, 1] = alpha;
                up[i, 2] = 3.602f;
            }
            List<Tuple<int, Tuple<float, float>>> allEvents = GenerateAllEvents(up);
            List<Tuple<int, Tuple<float, float>>> operations = new List<Tuple<int, Tuple<float, float>>>();
            for (int i = 0; i < allEvents.Count; i++)
            {
                int operation = FindAffectedOperation(allEvents[i].Item2.Item1, allEvents[i].Item2.Item2, machine: allEvents[i].Item1);
                if (operation != -1)
                {
                    operations.Add(new Tuple<int, Tuple<float, float>>(operation, allEvents[i].Item2));
                }
            }
            if (operations.Count == 0)
            {
                return; // nothing happens
            }
            operations.Sort((a, b) => a.Item2.Item1.CompareTo(b.Item2.Item1));
            for (int i = 0; i < operations.Count; i++)
            {
                _nodes[operations[i].Item1].End = operations[i].Item2.Item2;
                //Update(); // should update all affected nodes
            }
            Update();
        }

        public void SimulateWorkerUnavailabilitiy()
        {
            int nWorkers = _workers.Max() + 1;
            float makespan = _endingTimes.Max();
            float lambda = ((1.0f / nWorkers) / makespan) / 2.0f;
            float[,] up = new float[nWorkers, 3];
            for (int i = 0; i < nWorkers; i++)
            {
                float wlam = lambda * (float)ContinuousUniform.Sample(0.9, 1.1);
                float alpha = (float)ContinuousUniform.Sample(makespan * 0.5f, makespan * 1.0f);
                up[i, 0] = wlam;
                up[i, 1] = alpha;
                up[i, 2] = 3.602f;
            }
            List<Tuple<int, Tuple<float, float>>> allEvents = GenerateAllEvents(up);
            List<Tuple<int, Tuple<float, float>>> operations = new List<Tuple<int, Tuple<float, float>>>();
            for (int i = 0; i < allEvents.Count; i++)
            {
                int operation = FindAffectedOperation(allEvents[i].Item2.Item1, allEvents[i].Item2.Item2, worker: allEvents[i].Item1);
                if (operation != -1)
                {
                    operations.Add(new Tuple<int, Tuple<float, float>>(operation, allEvents[i].Item2));
                }
            }

            if (operations.Count == 0)
            {
                return; // nothing happens
            }
            operations.Sort((a, b) => a.Item2.Item1.CompareTo(b.Item2.Item1));
            for (int i = 0; i < operations.Count; i++)
            {
                _nodes[operations[i].Item1].End = operations[i].Item2.Item2;
                //Update(); // should update all affected nodes
            }
            Update();
        }

        public void SimulateProcessingTimes(float[,,] durations, Tuple<float, float>[] uncertaintyParameters,
            UncertaintySource uncertaintySource = UncertaintySource.Worker)
        {
            /*float[,,] d = new float[durations.GetLength(0), durations.GetLength(1), durations.GetLength(2)];
            for (int i = 0; i < d.GetLength(0); i++)
            {
                for (int j = 0; j < d.GetLength(1); j++)
                {
                    for (int k = 0; k < d.GetLength(2); k++)
                    {
                        d[i, j, k] = durations[i, j, k];
                    }
                }
            }
            //durations.CopyTo(d, 0);
            bool machineUncertainty = uncertaintySource == UncertaintySource.Machine;
            bool singleDistribution = uncertaintySource == UncertaintySource.Single;
            for (int i = 0; i < durations.GetLength(0); i++)
            {
                for (int j = 0; j < durations.GetLength(1); j++)
                {
                    for (int k = 0; k < durations.GetLength(2); k++)
                    {
                        if (!singleDistribution)
                        {
                            if (machineUncertainty)
                            {
                                d[i, j, k] = RealDuration(d[i, j, k], uncertaintyParameters[j]);
                            }
                            else
                            {
                                d[i, j, k] = RealDuration(d[i, j, k], uncertaintyParameters[k]);
                            }
                        }
                        else
                        {
                            d[i, j, k] = RealDuration(d[i, j, k], uncertaintyParameters[0]);
                        }
                    }
                }
            }*/
            List<Node> openList = new List<Node>();
            List<Node> closedList = new List<Node>();
            openList.AddRange(_roots);
            while (openList.Count > 0)
            {
                Node current = openList[0];
                openList.RemoveAt(0);
                current.End = current.Start + RealDuration(_durations[current.Operation, current.Machine, current.Worker], uncertaintyParameters[current.Worker]);//d[current.Operation, current.Machine, current.Worker];
                closedList.Add(current);
                Update();
                foreach (Node parent in current.Parents)
                {
                    if (!closedList.Contains(parent))
                    {
                        throw new InvalidDataException("Invalid graph data - a parent of a node was not in the closed list already.");
                    }
                }

                foreach (Node child in current.Children)
                {
                    AddChild(child, openList, closedList);
                }
            }

            Update();
        }

        public void Simulate(float[,,] durations, Tuple<float, float>[] uncertaintyParameters,
            UncertaintySource uncertaintySource = UncertaintySource.Worker, bool processingTimes = true, bool machineBreakdowns = true, bool workerUnavailabilities = true)
        {
            if (processingTimes)
            {
                SimulateProcessingTimes(durations, uncertaintyParameters, uncertaintySource);
                //Update();
            }
            if (machineBreakdowns)
            {
                SimulateMachineBreakdown();
                //Update();
            }
            if (workerUnavailabilities)
            {
                SimulateWorkerUnavailabilitiy();
                //Update();
            }

            //Update();
        }

        public bool IsInCriticalPath(Node node)
        {
            List<Node> criticalPath = new List<Node>();
            float makespan = Makespan;
            float eps = 0.0001f;
            foreach (Node leaf in _leafs)
            {
                if (Math.Abs(leaf.End - makespan) < eps)
                {
                    if (leaf.GetPredecessors().Contains(node))
                    {
                        return true;
                    }
                }
            }
            return false;
        }
    }

    public class Node
    {
        public float Start
        {
            get => _start;
            set => _start = value;
        }

        public float End
        {
            get => _end;
            set => _end = value;
        }

        public int Job
        {
            get => _job;
            set => _job = value;
        }

        public int Machine
        {
            get => _machine;
            set => _machine = value;
        }

        public int Worker
        {
            get => _worker;
            set => _worker = value;
        }

        public int Operation
        {
            get => _operation;
            set => _operation = value;
        }
        public Node OperationParent { get => _operationParent; set => _operationParent = value; }
        public Node MachineParent { get => _machineParent; set => _machineParent = value; }
        public Node WorkerParent { get => _workerParent; set => _workerParent = value; }
        public Node OperationChild { get => _operationChild; set => _operationChild = value; }
        public Node MachineChild { get => _machineChild; set => _machineChild = value; }
        public Node WorkerChild { get => _workerChild; set => _workerChild = value; }

        public List<Node> Parents
        {
            get => new List<Node> { _operationParent, _machineParent, _workerParent };// _parents;
            //set => _parents = value ?? throw new ArgumentNullException(nameof(value));
        }

        public List<Node> Children
        {
            get => new List<Node> { _operationChild, _machineChild, _workerChild };// _children;
            //set => _children = value ?? throw new ArgumentNullException(nameof(value));
        }

        //private List<Node> _parents;
        //private List<Node> _children;

        private float _start;
        private float _end;
        private int _job;
        private int _machine;
        private int _worker;
        private float _buffer;
        private int _operation;

        private Node _operationParent = null;
        private Node _machineParent = null;
        private Node _workerParent = null;
        private Node _operationChild = null;
        private Node _machineChild = null;
        private Node _workerChild = null;

        public Node(float[] startingTimes, float[] endingTimes, int[] machines, int[] workers, int[] jobSequence, float[] buffers, int operation)
        {
            _start = startingTimes[operation];
            _end = endingTimes[operation];
            _job = jobSequence[operation];
            _machine = machines[operation];
            _worker = workers[operation];
            _buffer = buffers[operation];
            _operation = operation;
            //_parents = new List<Node>();
            //_children = new List<Node>();

        }

        public float Buffer
        {
            get => _buffer;
            set => _buffer = value;
        }

        public float BufferTime
        {
            get => _buffer * (_end - _start);
        }


        public static bool LeftShift;

        public void AddNeighbours(int[] machines, int[] workers, int[] jobSequence, List<Node> nodes, int operation)
        {
            // job dependencies
            if (operation > 0 && jobSequence[operation - 1] == jobSequence[operation])
            {
                //_parents.Add(nodes[operation - 1]);
                _operationParent = nodes[operation-1];
            }

            if (operation + 1 < jobSequence.Length && jobSequence[operation + 1] == jobSequence[operation])
            {
                //_children.Add(nodes[operation + 1]);
                _operationChild = nodes[operation + 1];
            }
            // machine dependencies
            List<int> onMachine = new List<int>();
            for (int i = 0; i < machines.Length; i++)
            {
                if (machines[i] == _machine)
                {
                    onMachine.Add(i);
                }
            }
            onMachine.Sort((a, b) => nodes[a].Start.CompareTo(nodes[b].Start));
            int machineIndex = onMachine.IndexOf(operation);
            float eps = 0.00001f;
            if (machineIndex > 0)
            {
                int index = machineIndex - 1;
                while (index > 0 && Math.Abs(nodes[onMachine[index]].Start - nodes[onMachine[machineIndex]].Start) < eps)
                {
                    index -= 1;
                }

                if (Math.Abs(nodes[onMachine[index]].Start - nodes[onMachine[machineIndex]].Start) > eps)
                {
                    _machineParent = nodes[onMachine[index]];
                    //_parents.Add(nodes[onMachine[index]]);
                }
            }
            if (machineIndex + 1 < onMachine.Count)
            {
                _machineChild = nodes[onMachine[machineIndex + 1]];
                //_children.Add(nodes[onMachine[machineIndex + 1]]);
            }
            // worker dependencies
            List<int> sameWorker = new List<int>();
            for (int i = 0; i < workers.Length; i++)
            {
                if (workers[i] == _worker)
                {
                    sameWorker.Add(i);
                }
            }
            sameWorker.Sort((a, b) => nodes[a].Start.CompareTo(nodes[b].Start));
            int workerIndex = sameWorker.IndexOf(operation);
            if (workerIndex > 0)
            {
                int index = workerIndex - 1;
                while (index > 0 && Math.Abs(nodes[sameWorker[index]].Start - nodes[sameWorker[workerIndex]].Start) < eps)
                {
                    index -= 1;
                }

                if (Math.Abs(nodes[sameWorker[index]].Start - nodes[sameWorker[workerIndex]].Start) > eps)
                {
                    _workerParent = nodes[sameWorker[index]];
                    //_parents.Add(nodes[sameWorker[index]]);
                }
            }

            if (workerIndex + 1 < sameWorker.Count)
            {
                _workerChild = nodes[sameWorker[workerIndex + 1]];
                //_children.Add(nodes[sameWorker[workerIndex + 1]]);
            }
        }

        private List<float> GetParentEndTimes()
        {
            List<float> parentEndTimes = new List<float>();
            foreach (Node parent in Parents)
            {
                parentEndTimes.Add(parent.End + parent.BufferTime);
            }

            return parentEndTimes;
        }

        private float GetEarliestStartTime()
        {
            List<float> parentEndTimes = GetParentEndTimes();
            parentEndTimes.Add(_start);
            return parentEndTimes.Max();
        }
        public void UpdateValues()
        {
            float s = _start;
            float e = _end;
            float d = e - s;
            float earliestStart = GetEarliestStartTime();
            if (earliestStart > s || (LeftShift && earliestStart < s))
            {
                s = earliestStart;
                e = s + d;
            }
            _start = s;
            _end = e;
        }

        public void UpdateTimeSlot(float[,,] durations)
        {
            float s = _start;
            float d = durations[_operation, _machine, _worker];
            float e = s + d;
            float earliestStart = GetEarliestStartTime();
            if (earliestStart > s || (LeftShift && earliestStart < s))
            {
                s = earliestStart;
                e = s + d;
            }
            _start = s;
            _end = e;
        }

        public List<Node> GetPredecessors()
        {
            List<Node> openList = new List<Node>();
            openList.AddRange(Parents);
            List<Node> closedList = new List<Node>();
            while (openList.Count > 0)
            {
                Node current = openList[0];
                openList.RemoveAt(0);
                closedList.Add(current);
                foreach (Node parent in current.Parents)
                {
                    if (!openList.Contains(parent) && !closedList.Contains(parent))
                    {
                        openList.Add(parent);
                    }
                }
            }
            return closedList;
        }

        public int CountPredecessors()
        {
            return GetPredecessors().Count;
        }

        public List<Node> GetSuccessors()
        {
            List<Node> openList = new List<Node>();
            openList.AddRange(Children);
            List<Node> closedList = new List<Node>();
            while (openList.Count > 0)
            {
                Node current = openList[0];
                openList.RemoveAt(0);
                closedList.Add(current);
                foreach (Node child in current.Children)
                {
                    if (!openList.Contains(child) && !closedList.Contains(child))
                    {
                        openList.Add(child);
                    }
                }
            }
            return closedList;
        }

        public int CountSuccessors()
        {
            return GetSuccessors().Count;
        }
    }

}
