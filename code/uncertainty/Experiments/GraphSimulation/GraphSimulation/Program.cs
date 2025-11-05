using MathNet.Numerics.Distributions;
using MathNet.Numerics.Financial;
using System.Globalization;
using System.Reflection.Metadata.Ecma335;
using System.Runtime.InteropServices;
using System.Windows.Markup;

namespace GraphSimulation
{
    internal class Program
    {
        class TimeSlot
        {
            public float Start = 0;
            public float End = 0;

            public TimeSlot(float start, float end)
            {
                Start = start;
                End = end;
            }
            public bool Overlaps(TimeSlot other)
            {
                return Contains(other.Start) || Contains(other.End) || other.Contains(Start) || other.Contains(End);
            }

            public bool Contains(float time)
            {
                return time >= Start && time <= End;
            }
        }

        private static TimeSlot EarliestFit(List<TimeSlot> slots, TimeSlot slot)
        {

            for (int i = 1; i < slots.Count; ++i)
            {
                if (slots[i - 1].End <= slot.Start && slots[i].Start >= slot.End)
                {
                    return slots[i - 1];
                }
            }
            return slots.Last();
        }

        static int FirstIndex(int[] values, int value)
        {
            for(int i = 0; i < values.Length; ++i)
            {
                if (values[i] == value)
                {
                    return i;
                }
            }
            return -1;
        }

        class Individual
        {
            public float[] StartTimes;
            public float[] EndTimes;
            public int[] Machines;
            public int[] Workers;
            public float[] Buffers;
            public float Fitness
            {
                get => EndTimes.Max();
            }

            public Individual(float[] startTimes, float[] endTimes, int[] machines, int[] workers, float[] buffers)
            {
                StartTimes = startTimes;
                EndTimes = endTimes;
                Machines = machines;
                Workers = workers;
                Buffers = buffers;
            }

            public Individual(float[] startTimes, float[] endTimes, int[] machines, int[] workers) : this(startTimes, endTimes, machines, workers, new float[startTimes.Length])
            {
                
            }

        }
        static Individual Translate(int[] sequence, int[] machines, int[] workers, float[,,] durations)
        {
            int nJobs = sequence.Max()+1;
            int nMachines = machines.Max()+1;
            int nWorkers = workers.Max()+1;
            int nOperations = sequence.Length;

            int[] jobSequence = new int[nOperations];
            sequence.CopyTo(jobSequence, 0);
            Array.Sort(jobSequence);
            int[] jobStartIndices = new int[nJobs];
            for(int i = 0; i < jobStartIndices.Length; ++i)
            {
                int index = FirstIndex(jobSequence, i);
                if(index == -1)
                {
                    throw new InvalidDataException("Invalid job sequence - job " + i + " is missing from the sequence.");
                }
                jobStartIndices[i] = index;
            }

            int[] nextOperation = new int[nJobs];
            List<TimeSlot>[] endOnMachines = new List<TimeSlot>[nMachines];
            for (int i = 0; i < endOnMachines.Length; ++i)
            {
                endOnMachines[i] = new List<TimeSlot>();
                endOnMachines[i].Add(new TimeSlot(0, 0));
            }
            List<TimeSlot>[] endOfWorkers = new List<TimeSlot>[nWorkers];
            for (int i = 0; i < endOfWorkers.Length; ++i)
            {
                endOfWorkers[i] = new List<TimeSlot>();
                endOfWorkers[i].Add(new TimeSlot(0, 0));
            }

            float[] endTimes = new float[nOperations];
            float[] startTimes = new float[nOperations];
            for (int i = 0; i < nOperations; ++i)
            {
                int job = sequence[i];
                int operation = nextOperation[job];
                ++nextOperation[job];
                int startIndex =jobStartIndices[job] + operation;
                int machine = machines[startIndex];

                int worker = workers[startIndex];

                float duration = durations[startIndex, machine, worker];
                if (duration == 0.0f)
                {
                    Console.WriteLine("0 DURATION, INVALID ASSIGNMENT!");
                }
                float offset = 0;
                
                if (operation > 0)
                {
                    if (endTimes[startIndex - 1] > offset)
                    {
                        // need to wait for previous operation to finish
                        offset = endTimes[startIndex - 1];
                    }
                }
                if (endOnMachines[machine].Count > 0 && endOnMachines[machine].Last().End >= offset)
                {
                    // need to wait for machine to be available
                    offset = endOnMachines[machine].Last().End;
                }
                if (endOfWorkers[worker].Count > 0)
                {
                    TimeSlot workerEarliest = EarliestFit(endOfWorkers[worker], new TimeSlot(offset, offset + duration));
                    if (workerEarliest.End >= offset)
                    {
                        // need to wait for worker to be ready
                        offset = workerEarliest.End;
                    }
                }
                endTimes[startIndex] = offset + duration;
                startTimes[startIndex] = offset;
                endOnMachines[machine].Add(new TimeSlot(offset, offset + duration));
                endOfWorkers[worker].Add(new TimeSlot(offset, offset + duration));
                endOfWorkers[worker] = endOfWorkers[worker].OrderBy(o => o.Start).ToList();
  
            }
            Console.WriteLine(endTimes.Max());
            return new Individual(startTimes, endTimes, machines, workers);
        }

        static int[] ParseIntArray(string values)
        {
            values = values.Remove(0, 1);
            values = values.Remove(values.Length - 1, 1);
            string[] parts = values.Split(',');
            int[] result = new int[parts.Length];
            for(int i = 0; i < parts.Length; i++)
            {
                try
                {
                    result[i] = int.Parse(parts[i].Trim());
                } catch(Exception e)
                {
                    throw new InvalidCastException("The provided string had the wrong format to parse it as int[].");
                }
            }
            return result;
        }

        static float[] ParseFloatArray(string values)
        {
            //CultureInfo ci = (CultureInfo)CultureInfo.CurrentCulture.Clone();
            //ci.NumberFormat.CurrencyDecimalSeparator = ".";
            values = values.Remove(0, 1);
            values = values.Remove(values.Length - 1, 1);
            string[] parts = values.Split(',');
            float[] result = new float[parts.Length];
            for (int i = 0; i < parts.Length; i++)
            {
                try
                {
                    //result[i] = float.Parse(parts[i].Trim(), NumberStyles.Any, ci);
                    result[i] = float.Parse(parts[i].Trim());
                } catch (Exception e)
                {
                    throw new InvalidCastException("The provided string had the wrong format to parse it as float[].");
                }
            }
            return result;
        }

        public static void TestDistribution(Tuple<float, float> uncertaintyParameters)
        {
            for(int i = 0; i< 100; i++)
            {
                float value = (float)Beta.Sample(uncertaintyParameters.Item1, uncertaintyParameters.Item2);
                if(value < 0.0f)
                {
                    Console.Write("#############NEGATIVE VALUE##########");
                }
                Console.Write(value + " ");

            }
            Console.WriteLine();
        }

        static void Main(string[] args)
        {
            if (args.Length < 4)
            {
                throw new ArgumentException("Not enough arguments.");
            }
            CultureInfo.CurrentCulture = new CultureInfo("en-GB");

            string benchmark = args[0];
            string sequence = args[1];
            string machines = args[2];
            string workers = args[3];
            int[] s;
            int[] m;
            int[] w;
            try
            {
                s = ParseIntArray(sequence);
            } catch (InvalidCastException e)
            {
                Console.WriteLine("Error while parsing sequence: " + e.Message + "(" + sequence.ToString() + ")");
                return;
            }
            try
            {
                m = ParseIntArray(machines);
            } catch (InvalidCastException e) 
            {
                Console.WriteLine("Error while parsing machines: " + e.Message + "(" + machines.ToString() + ")");
                return;
            }
            try
            {
                w = ParseIntArray(workers);
            }
            catch (InvalidCastException e)
            {
                Console.WriteLine("Error while parsing workers: " + e.Message + "(" + workers.ToString() + ")");
                return;
            }
            float[] b = new float[s.Length];
            if(args.Length > 4)
            {
                try
                {
                    b = ParseFloatArray(args[4]);
                } catch (InvalidCastException e)
                {
                    Console.WriteLine("Error while parsing buffers: " + e.Message + "(" + b.ToString() + ")");
                    return;
                }
            }
            WorkerBenchmarkParser parser = new WorkerBenchmarkParser();
            WorkerEncoding encoding = parser.ParseBenchmark(benchmark);
            float[,,] d = encoding.Durations;

            Individual individual = Translate(s, m, w, d);
            int[] js = new int[s.Length];
            s.CopyTo(js, 0);
            Array.Sort(js);
            Graph g = new Graph(individual.StartTimes, individual.EndTimes, individual.Machines, individual.Workers, js, d, b);
            Console.WriteLine("Graph Fitness: " + g.EndingTimes.Max());
            //g.PrintPaths();
            
            int nWorkers = individual.Workers.Max() + 1;
            Tuple<float, float>[] uncertaintyParameters = new Tuple<float, float>[nWorkers];
            Random random = new Random();
            for (int i = 0; i < nWorkers; ++i)
            {
                float alpha = (float)random.NextDouble();
                float beta = 10.0f*alpha;
                Tuple<float, float> values = new Tuple<float, float>(alpha, beta);
                uncertaintyParameters[i] = values;
            }
            int nTests = 50;
            float avgPro = 0.0f;
            float avgMac = 0.0f;
            float avgWor = 0.0f;
            float avgAll = 0.0f;
            for(int i = 0; i < nTests; ++i)
            {
                g = new Graph(individual.StartTimes, individual.EndTimes, individual.Machines, individual.Workers, js, d, b);
                g.Simulate(d, uncertaintyParameters, processingTimes: true, machineBreakdowns: false, workerUnavailabilities: false);
                avgPro += g.EndingTimes.Max();
            }
            Console.WriteLine("Graph Fitness after Processing Times Only test: " + (avgPro/nTests));
            for(int i = 0; i < nTests; i++)
            {
                g = new Graph(individual.StartTimes, individual.EndTimes, individual.Machines, individual.Workers, js, d, b);
                g.Simulate(d, uncertaintyParameters, processingTimes: false, machineBreakdowns: true, workerUnavailabilities: false);
                avgMac += g.EndingTimes.Max();
            }
            Console.WriteLine("Graph Fitness after Machine Breakdowns Only test: " + (avgMac / nTests));
            for(int i = 0; i < nTests; i++)
            {
                g = new Graph(individual.StartTimes, individual.EndTimes, individual.Machines, individual.Workers, js, d, b);
                g.Simulate(d, uncertaintyParameters, processingTimes: false, machineBreakdowns: false, workerUnavailabilities: true);
                avgWor += g.EndingTimes.Max();
            }
            Console.WriteLine("Graph Fitness after Worker Unavailability Only test: " + (avgWor / nTests));
            for(int i = 0;i < nTests; i++)
            {
                g = new Graph(individual.StartTimes, individual.EndTimes, individual.Machines, individual.Workers, js, d, b);
                g.Simulate(d, uncertaintyParameters, processingTimes: true, machineBreakdowns: true, workerUnavailabilities: true);
                avgAll += g.EndingTimes.Max();
            }
            Console.WriteLine("Graph Fitness after All Uncertainty test: " + (avgAll / nTests));
        }
    }
}
