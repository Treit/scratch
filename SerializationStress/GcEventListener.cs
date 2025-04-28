using System;
using System.Diagnostics.Tracing;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

public class GcEventListener : EventListener
{
    // For .NET Core+ GC events, use the following:
    // - Provider: Microsoft-Windows-DotNETRuntime
    // - Keywords: 0x1C0000001 (GC + GCHeapSurvivalAndMovement + GCHeapCollect + GCHeapAndTypeNames)
    // - Level: Verbose
    // Note: You may need to run as administrator to receive all events.
    private readonly string _providerName = "Microsoft-Windows-DotNETRuntime";
    private readonly EventLevel _level = EventLevel.Verbose;
    private readonly EventKeywords _keywords = (EventKeywords)0x1C0000001;

    private CancellationTokenSource _cts;
    private Task _listenTask;
    private StreamWriter _writer;
    private readonly string _logFilePath;

    public GcEventListener(string logFilePath = "gc_log.txt")
    {
        _logFilePath = logFilePath;
    }

    public void Start()
    {
        _cts = new CancellationTokenSource();
        _writer = new StreamWriter(_logFilePath, append: false) { AutoFlush = true };
        _listenTask = Task.Run(() => Listen(_cts.Token));
    }

    public void Stop()
    {
        _cts?.Cancel();
        _listenTask?.Wait();
        _writer?.Dispose();
    }

    private void Listen(CancellationToken token)
    {
        // Just keep the listener alive
        while (!token.IsCancellationRequested)
        {
            Thread.Sleep(100);
        }
    }

    protected override void OnEventSourceCreated(EventSource eventSource)
    {
        if (eventSource.Name == _providerName)
        {
            EnableEvents(eventSource, _level, _keywords);
        }
    }

    protected override void OnEventWritten(EventWrittenEventArgs eventData)
    {
        var timestamp = eventData.TimeStamp.ToString("yyyy-MM-dd HH:mm:ss.fff");
        if (eventData.EventName == "GCAllocationTick_V4")
        {
            return;
        }

        if (eventData.EventName != null && eventData.Payload != null)
        {
            _writer.WriteLine($"[{timestamp}] [GC ETW] {eventData.EventName}: {string.Join(", ", eventData.Payload)}");
        }
        else if (eventData.EventName != null)
        {
            _writer.WriteLine($"[{timestamp}] [GC ETW] {eventData.EventName}");
        }
    }
}