using System;
using System.Diagnostics;
using Windows.Win32;
using Windows.Win32.Foundation;

class Program
{
    private const int WM_CLOSE = 0x0010;

    static void Main(string[] args)
    {
        if (!OperatingSystem.IsWindows())
        {
            Console.WriteLine("Not supported on this platform.");
            return;
        }

        if (args.Length == 0)
        {
            Console.WriteLine("Please provide a process name.");
            return;
        }

        var name = args[0];
        foreach (var process in Process.GetProcessesByName(name))
        {
            if (process.MainWindowHandle != IntPtr.Zero)
            {
#pragma warning disable CA1416 // Validate platform compatibility
                PInvoke.PostMessage(new HWND(process.MainWindowHandle),
                                    WM_CLOSE,
                                    default(WPARAM),
                                    default(LPARAM));
#pragma warning restore CA1416 // Validate platform compatibility
            }
        }
    }
}
