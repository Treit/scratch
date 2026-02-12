param(
    [string]$LogFile = "$PSScriptRoot\..\msbuild.log",
    [string]$OutputHtml = "",
    [int]$Columns = 0
)

$LogFile = Resolve-Path $LogFile

$descriptions = @{
    'CS0105'='Duplicate using directive'; 'CS0108'='Hides inherited member'; 'CS0114'='Hides inherited member'
    'CS0162'='Unreachable code'; 'CS0168'='Variable never used'; 'CS0169'='Field never used'
    'CS0219'='Variable assigned not used'; 'CS0618'='Obsolete member usage'; 'CS0649'='Field never assigned'
    'CS0659'='Missing GetHashCode'; 'CS0672'='Overrides obsolete member'; 'CS1570'='Invalid XML in comment'
    'CS1571'='Duplicate param XML tag'; 'CS1572'='Param tag no matching param'; 'CS1573'='Missing param XML tag'
    'CS1574'='Unresolved cref'; 'CS1587'='Misplaced XML comment'; 'CS1591'='Missing XML comment'
    'CS1998'='Async lacks await'; 'CS4014'='Unawaited async call'; 'CS7022'='Entry point is global code'
    'CS8524'='Missing enum switch cases'; 'CS8600'='Null to non-nullable type'; 'CS8601'='Possible null assignment'
    'CS8602'='Possibly null dereference'; 'CS8603'='Possible null return'; 'CS8604'='Possible null argument'
    'CS8605'='Unboxing possibly null'; 'CS8613'='Nullability in return'; 'CS8618'='Non-nullable uninitialized'
    'CS8619'='Nullability mismatch'; 'CS8620'='Nullability mismatch in arg'; 'CS8621'='Nullability in return type'
    'CS8622'='Nullability in parameter'; 'CS8625'='Null to non-nullable'; 'CS8629'='Nullable value may be null'
    'CS8632'='Nullable annotation context'; 'CS8633'='Nullability mismatch in constraint'
    'CS8634'='Nullability in type param'; 'CS8714'='Type param constraint'; 'CS8765'='Nullability in override'
    'CS8767'='Nullability in param'; 'CS9107'='Param captured and assigned'; 'CS9113'='Parameter unread'
    'CS9124'='Param in state machine'; 'CS0414'='Field assigned, never used'
    'CA1001'='Types own disposable fields'; 'CA1002'='Do not expose generic lists'
    'CA1008'='Enums have zero value'; 'CA1012'='Abstract types no ctors'; 'CA1016'='Mark with AssemblyVersion'
    'CA1024'='Use properties'; 'CA1027'='Mark enums with Flags'; 'CA1028'='Enum storage Int32'
    'CA1031'='Catch specific exceptions'; 'CA1032'='Implement exception ctors'; 'CA1033'='Interface callable by child'
    'CA1034'='Nested types visible'; 'CA1040'='Avoid empty interfaces'; 'CA1051'='Visible instance fields'
    'CA1052'='Seal static holder types'; 'CA1054'='URI param not string'; 'CA1055'='URI return not string'
    'CA1056'='URI prop not string'; 'CA1062'='Validate public args'; 'CA1063'='Implement IDisposable'
    'CA1065'='Unexpected exception location'; 'CA1067'='Override Equals for IEquatable'
    'CA1068'='CancellationToken last'; 'CA1069'='Duplicate enum values'; 'CA1303'='Do not pass literals'
    'CA1304'='Specify CultureInfo'; 'CA1305'='Specify IFormatProvider'; 'CA1307'='Specify StringComparison'
    'CA1308'='Normalize to uppercase'; 'CA1309'='Use ordinal StringComparison'; 'CA1310'='Specify StringComparison'
    'CA1311'='Specify culture for strings'; 'CA1416'='Platform compatibility'; 'CA1507'='Use nameof'
    'CA1508'='Dead conditional code'; 'CA1510'='Use ThrowIfNull'; 'CA1707'='Remove underscores from names'
    'CA1711'='Incorrect identifier suffix'; 'CA1715'='Identifier prefix'; 'CA1716'='Identifier matches keyword'
    'CA1720'='No type names in identifiers'; 'CA1721'='Property matches get method'
    'CA1724'='Type name conflicts namespace'; 'CA1725'='Param names match base'; 'CA1805'='Unnecessary initialization'
    'CA1806'='Do not ignore results'; 'CA1816'='Call GC.SuppressFinalize'; 'CA1819'='Properties return arrays'
    'CA1820'='Test empty using length'; 'CA1822'='Mark members as static'; 'CA1823'='Avoid unused private fields'
    'CA1825'='Avoid zero-length arrays'; 'CA1826'='Use property not Enumerable'; 'CA1827'='Use Any not Count'
    'CA1829'='Use Length/Count property'; 'CA1834'='Use StringBuilder char'; 'CA1836'='Prefer IsEmpty over Count'
    'CA1844'='Memory-based overrides'; 'CA1845'='Use span-based Concat'; 'CA1846'='Prefer AsSpan'
    'CA1847'='Use string.Contains(char)'; 'CA1848'='Use LoggerMessage delegates'; 'CA1849'='Call async in async method'
    'CA1850'='Prefer static HashData'; 'CA1851'='Possible multiple enumerations'; 'CA1852'='Seal internal types'
    'CA1854'='Prefer TryGetValue'; 'CA1859'='Use concrete types'; 'CA1860'='Avoid Enumerable.Any()'
    'CA1861'='Avoid constant arrays as args'; 'CA1862'='Use StringComparison'; 'CA1863'='Use char overload'
    'CA1866'='Use char overload'; 'CA1867'='Use char overload'; 'CA1869'='Cache JsonSerializerOptions'
    'CA2000'='Dispose objects'; 'CA2007'='Call ConfigureAwait'; 'CA2016'='Forward CancellationToken'
    'CA2201'='Reserved exception types'; 'CA2208'='Correct ArgumentException'; 'CA2211'='Non-constant visible fields'
    'CA2213'='Dispose disposable fields'; 'CA2215'='Call base Dispose'; 'CA2227'='Read-only collection props'
    'CA2234'='Pass URIs not strings'; 'CA2254'='Template should be static'; 'CA5394'='Insecure randomness'
    'CA5399'='Disable cert check'
    'IDE0004'='Remove unnecessary cast'; 'IDE0009'='Add this qualification'; 'IDE0010'='Add missing switch cases'
    'IDE0011'='Add braces'; 'IDE0017'='Use object initializers'; 'IDE0019'='Use pattern matching'
    'IDE0020'='Pattern matching null check'; 'IDE0027'='Use expression body'; 'IDE0028'='Use collection initializer'
    'IDE0031'='Use null propagation'; 'IDE0034'='Simplify default expression'; 'IDE0040'='Add accessibility modifiers'
    'IDE0044'='Make field readonly'; 'IDE0055'='Fix formatting'; 'IDE0056'='Use index operator'
    'IDE0057'='Use range operator'; 'IDE0058'='Unused expression value'; 'IDE0059'='Unnecessary assignment'
    'IDE0060'='Remove unused parameter'; 'IDE0065'='Using directive placement'; 'IDE0071'='Simplify interpolation'
    'IDE0072'='Add missing switch cases'; 'IDE0073'='File header mismatch'; 'IDE0090'='Simplify new expression'
    'IDE0100'='Unnecessary equality op'; 'IDE0120'='Simplify LINQ'; 'IDE0130'='Namespace mismatch'
    'IDE0161'='Use file-scoped namespace'; 'IDE0220'='Add explicit cast'; 'IDE0300'='Use collection expression'
    'IDE0301'='Use collection expression'; 'IDE0305'='Use collection expression'; 'IDE1006'='Naming rule violation'
    'MSB3277'='Assembly version conflict'
    'NU1504'='Duplicate PackageReference'; 'NU1603'='Dependency version mismatch'; 'NU1604'='Missing version bound'
    'NU1701'='Package compatibility'; 'NETSDK1086'='Redundant FrameworkReference'
    'SYSLIB0026'='Obsolete MutuallyAuth'; 'SYSLIB0045'='Use GeneratedRegex'; 'SYSLIB0050'='Obsolete serialization API'
    'SYSLIB0051'='Obsolete serialization API'; 'SYSLIB1045'='Use GeneratedRegex'
    'ASP0000'='Avoid BuildServiceProvider'; 'ASP0018'='Unused route parameter'; 'ASP0019'='Use IHeaderDictionary'
    'RCS1194'='Implement exception ctors'; 'RCS1203'='Use AttributeUsageAttribute'
    'xUnit1012'='Null for type parameter'; 'xUnit1025'='InlineData should be unique'
    'xUnit1026'='Theory param not used'; 'xUnit1031'='Theory param type mismatch'; 'xUnit2020'='Always-failing Assert'
}

$lines = [System.IO.File]::ReadAllLines($LogFile)

$summaryStart = -1
for ($i = $lines.Count - 1; $i -ge 0; $i--) {
    if ($lines[$i] -match 'Build succeeded') {
        $summaryStart = $i
        break
    }
}

$searchLines = if ($summaryStart -gt 0) { $lines[$summaryStart..($lines.Count - 1)] } else { $lines }

$codes = foreach ($line in $searchLines) {
    if ($line -match ': warning\s*(\w*)\s*:') {
        $code = $Matches[1]
        if ([string]::IsNullOrWhiteSpace($code)) { '(no code)' } else { $code }
    }
}

$grouped = $codes | Group-Object | Sort-Object Count -Descending
$total = ($grouped | Measure-Object -Property Count -Sum).Sum
$distinctCount = $grouped.Count

$grouped | Format-Table Count, @{Label = 'Warning'; Expression = { $_.Name }} -AutoSize

if (-not $OutputHtml) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($LogFile)
    $OutputHtml = Join-Path (Split-Path $LogFile) "$baseName-warnings.html"
}

if ($Columns -le 0) {
    $Columns = if ($distinctCount -le 20) { 1 }
               elseif ($distinctCount -le 50) { 2 }
               elseif ($distinctCount -le 100) { 3 }
               else { 4 }
}

$maxCount = $grouped[0].Count
$rowsPerCol = [math]::Ceiling($distinctCount / $Columns)

function Build-TableHtml($items, $maxVal, $isLast, $runningTotal) {
    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.AppendLine('<table>')
    [void]$sb.AppendLine('  <thead><tr><th>#</th><th>Code</th><th>Description</th><th></th></tr></thead>')
    [void]$sb.AppendLine('  <tbody>')
    foreach ($item in $items) {
        $w = [math]::Max(1, [math]::Round(($item.Count / $maxVal) * 80))
        $desc = if ($descriptions[$item.Name]) { $descriptions[$item.Name] } else { '' }
        $descHtml = [System.Net.WebUtility]::HtmlEncode($desc)
        [void]$sb.AppendLine("    <tr><td>$($item.Count)</td><td>$($item.Name)</td><td class=`"desc`">$descHtml</td><td><span class=`"bar`" style=`"width:$($w)px`"></span></td></tr>")
    }
    [void]$sb.AppendLine('  </tbody>')
    if ($isLast) {
        [void]$sb.AppendLine("  <tfoot><tr><td>$runningTotal</td><td colspan=`"3`">Total</td></tr></tfoot>")
    }
    [void]$sb.AppendLine('</table>')
    return $sb.ToString()
}

$columnHtml = [System.Text.StringBuilder]::new()
for ($c = 0; $c -lt $Columns; $c++) {
    $skip = $c * $rowsPerCol
    $slice = $grouped | Select-Object -Skip $skip -First $rowsPerCol
    $isLast = ($c -eq ($Columns - 1))
    [void]$columnHtml.Append((Build-TableHtml $slice $maxCount $isLast $total))
}

$gridCols = ('1fr ' * $Columns).Trim()
$logName = [System.IO.Path]::GetFileName($LogFile)
$date = Get-Date -Format 'yyyy-MM-dd'

$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Build Warnings Summary</title>
<style>
  body { font-family: Segoe UI, system-ui, sans-serif; max-width: 1400px; margin: 1rem auto; padding: 0 .5rem; color: #e0e0e0; background: #1a1a2e; }
  h1 { font-size: 1.2rem; margin-bottom: .2rem; }
  .meta { color: #888; font-size: .8rem; margin-bottom: .5rem; }
  .columns { display: grid; grid-template-columns: $gridCols; gap: 0 1.2rem; }
  table { width: 100%; border-collapse: collapse; font-size: .72rem; }
  th { text-align: left; border-bottom: 2px solid #555; padding: .2rem .3rem; color: #ccc; }
  th:first-child { text-align: right; width: 34px; }
  td { padding: .15rem .3rem; border-bottom: 1px solid #2a2a40; white-space: nowrap; }
  td:first-child { text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }
  .desc { color: #999; font-size: .68rem; }
  tr:hover { background: #2a2a4a; }
  tfoot td { border-top: 2px solid #555; border-bottom: none; font-weight: 700; }
  .bar { display: inline-block; height: 6px; background: #6c8cff; border-radius: 2px; vertical-align: middle; }
</style>
</head>
<body>
<h1>Build Warnings Summary</h1>
<p class="meta">$logName -- $date -- $distinctCount distinct warnings, $total total</p>
<div class="columns">
$($columnHtml.ToString())
</div>
</body>
</html>
"@

[System.IO.File]::WriteAllText($OutputHtml, $html)
Write-Host "HTML report written to $OutputHtml ($Columns columns, $distinctCount warnings, $total total)"
