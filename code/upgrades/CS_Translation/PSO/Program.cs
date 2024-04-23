namespace PSO
{
    internal class Program
    {
        static void Main(string[] args)
        {
            // TESTING
            int[,] result = new int[10, 10];
            for(int i = 0; i < result.GetLength(0); ++i) 
            { 
                for(int j = 0; j < result.GetLength(1); ++j)
                {
                    Console.Write(result[i, j]);
                }
                Console.WriteLine();
            }

            List<int> values = new List<int>();
            values.Add(1);
            Random random = new Random();
            for(int i = 0; i <100; ++i)
            {
                Console.WriteLine(random.Next(values.Count));

            }
        }
    }
}
