using System.Diagnostics;
using System.Text.Json;

class Program
{
    static async Task Main()
    {
        await Task.Yield();

        // Start GC ETW event listener in the background
        var gcListener = new GcEventListener();
        gcListener.Start();

        var exeDir = AppContext.BaseDirectory;
        var jsonPath = Path.Combine(exeDir, "StressTestDocument_300KB.json");
        var json = File.ReadAllText(jsonPath);


        while (true)
        {
            var start = DateTimeOffset.UtcNow;
            var sw = Stopwatch.StartNew();
            _ = JsonSerializer.Deserialize<StressTestDocument>(json);
            var elapsed = sw.ElapsedMilliseconds;
            var end = DateTimeOffset.UtcNow;
            if (elapsed > 100)
            {
                Console.WriteLine($"Deserialization: start={start:yyyy-MM-dd HH:mm:ss.fff}, end={end:yyyy-MM-dd HH:mm:ss.fff}, duration={elapsed} ms");
            }

            _ = StressTest.RunMemoryPressureTestAsync(32, 5);
        }
    }
}

