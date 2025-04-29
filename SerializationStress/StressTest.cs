using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

public class StressTest
{
    public static async Task RunMemoryPressureTestAsync(int taskCount = 4, int seconds = 30)
    {
        var cts = new CancellationTokenSource();
        var tasks = new List<Task>();
        for (int t = 0; t < taskCount; t++)
        {
            tasks.Add(Task.Run(async () =>
            {
                var rng = new Random();
                var allocations = new List<byte[]>();
                while (!cts.Token.IsCancellationRequested)
                {
                    int size = rng.Next(512 * 1024, 2 * 1024 * 1024);
                    size = 0;
                    allocations.Add(new byte[size]);
                    if (allocations.Count > 100)
                    {
                        allocations.RemoveAt(0);
                    }
                    if (rng.NextDouble() < 0.05)
                    {
                        await Task.Delay(50, cts.Token);
                    }
                }
            }, cts.Token));
        }
        // Console.WriteLine($"Started {taskCount} memory pressure tasks for {seconds} seconds...");
        await Task.Delay(seconds * 1000, cts.Token);
        cts.Cancel();
        try
        {
            await Task.WhenAll(tasks);
        }
        catch (OperationCanceledException)
        {
            // Expected on cancellation
        }
        //Console.WriteLine("Memory pressure test complete.");
    }
}
