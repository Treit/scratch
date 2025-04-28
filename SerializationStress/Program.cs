using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text.Json;

class Program
{
    static async Task Main()
    {
        // Start GC ETW event listener in the background
        var gcListener = new GcEventListener();
        gcListener.Start();

        var exeDir = AppContext.BaseDirectory;
        var jsonPath = Path.Combine(exeDir, "StressTestDocument_300KB.json");
        var json = File.ReadAllText(jsonPath);


        while (true)
        {
            var start = DateTime.Now;
            var sw = Stopwatch.StartNew();
            var doc = JsonSerializer.Deserialize<StressTestDocument>(json);
            var elapsed = sw.ElapsedMilliseconds;
            var end = DateTime.Now;
            if (elapsed > 100)
            {
                Console.WriteLine($"Deserialization: start={start:yyyy-MM-dd HH:mm:ss.fff}, end={end:yyyy-MM-dd HH:mm:ss.fff}, duration={elapsed} ms");
            }
            // Kick off the stress test
            _ = StressTest.RunMemoryPressureTestAsync(16, 10);
        }
    }
}

