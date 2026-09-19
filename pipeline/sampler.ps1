$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
function Get-J($u){
    $r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 30
    [System.Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray()) | ConvertFrom-Json
}

$games = [System.IO.File]::ReadAllText("$PWD\raw_v3.json",[System.Text.Encoding]::UTF8) | ConvertFrom-Json
$ids = @($games | ForEach-Object { [string]$_.id })
$outFile = "$PWD\samples.jsonl"
$intervalSec = 300
$maxSamples = 96

for ($s = 1; $s -le $maxSamples; $s++) {
    $stamp = (Get-Date).ToUniversalTime().ToString("o")
    $counts = @{}
    $fails = 0
    for ($i = 0; $i -lt $ids.Count; $i += 50) {
        $end = [Math]::Min($i + 50, $ids.Count) - 1
        $batch = @($ids[$i..$end])
        $ok = $false
        for ($try = 1; $try -le 4 -and -not $ok; $try++) {
            try {
                $r = Get-J ("https://games.roblox.com/v1/games?universeIds=" + ($batch -join ","))
                foreach ($d in $r.data) { $counts[[string]$d.id] = $d.playing }
                $ok = $true
            } catch { Start-Sleep -Seconds ([Math]::Min(60, 5 * [Math]::Pow(2, $try - 1))) }
        }
        if (-not $ok) { $fails++ }
        Start-Sleep -Milliseconds 900
    }
    if ($counts.Count -gt 0) {
        $line = [PSCustomObject]@{ t = $stamp; n = $counts.Count; c = $counts } | ConvertTo-Json -Compress -Depth 4
        [System.IO.File]::AppendAllText($outFile, $line + "`n", [System.Text.UTF8Encoding]::new($false))
        Write-Output "sample $s at $stamp -> $($counts.Count) games ($fails failed batches)"
    } else {
        Write-Output "sample $s at $stamp -> EMPTY, backing off"
        Start-Sleep -Seconds 300
    }
    if ($s -lt $maxSamples) { Start-Sleep -Seconds $intervalSec }
}
Write-Output "sampling done"
