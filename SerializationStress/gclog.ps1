$gcReasonMap = @{
    0 = "SOH allocation"
    1 = "Induced"
    2 = "Low memory"
    3 = "Empty"
    4 = "LOH allocation"
    5 = "SOH full"
    6 = "LOH full"
    7 = "Induced but not forced"
}

$gcTypeMap = @{
    0 = "Blocking (foreground)"
    1 = "Background (non-blocking)"
    2 = "Background (blocking)"
}


$workspace = Split-Path -Parent $MyInvocation.MyCommand.Definition
$logPath = Join-Path $workspace $args[0]
$outPath = Join-Path $workspace 'gc_durations.csv'

$logLines = Get-Content $logPath

$events = foreach ($line in $logLines) {
    if ($line -match '^[\[](.*?)[\]] \[GC ETW\] (\w+): (.*)$') {
        try {
            [PSCustomObject]@{
                Timestamp = [datetime]::ParseExact($matches[1], "yyyy-MM-dd HH:mm:ss.fff", $null)
                EventName = $matches[2]
                Payload   = $matches[3] -split ', ' | ForEach-Object { $_.Trim() }
            }
        } catch {
            Write-Warning "Failed to parse line: $line"
        }
    }
}

$gcStarts = $events | Where-Object { $_.EventName -eq "GCStart_V2" }
$gcEnds   = $events | Where-Object { $_.EventName -eq "GCEnd_V1" }

$results = foreach ($start in $gcStarts) {
    $gcNum = $start.Payload[0]
    $reasonCode = [int]$start.Payload[2]
    $typeCode = [int]$start.Payload[3]
    $end = $gcEnds | Where-Object { $_.Payload[0] -eq $gcNum } | Select-Object -First 1
    if ($end) {
        $duration = ($end.Timestamp - $start.Timestamp).TotalMilliseconds
        $reasonText = $gcReasonMap[$reasonCode]
        $typeText = $gcTypeMap[$typeCode]
        if (-not $typeText) { $typeText = "Unknown ($reasonCode)" }
        [PSCustomObject]@{
            GCNumber   = $gcNum
            Reason     = $reasonText
            Type       = $typeText
            StartTime  = $start.Timestamp.ToString("yyyy-MM-dd HH:mm:ss.fff")
            EndTime    = $end.Timestamp.ToString("yyyy-MM-dd HH:mm:ss.fff")
            DurationMs = [math]::Round($duration, 3)
        }
    }
}

$results | Select-Object GCNumber,Reason,Type,StartTime,EndTime,DurationMs | Export-Csv -NoTypeInformation -Path $outPath
Write-Host "GC durations written to $outPath"