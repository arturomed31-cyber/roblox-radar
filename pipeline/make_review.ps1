$games = [System.IO.File]::ReadAllText("$PWD\raw_v3.json",[System.Text.Encoding]::UTF8) | ConvertFrom-Json
$auto  = [System.IO.File]::ReadAllText("$PWD\auto_class.json",[System.Text.Encoding]::UTF8) | ConvertFrom-Json
$hand  = [System.IO.File]::ReadAllText("$PWD\classification_v2.json",[System.Text.Encoding]::UTF8) | ConvertFrom-Json

$autoMap = @{}; foreach ($a in $auto) { $autoMap[[string]$a.id] = $a }
$handIds = @{}; foreach ($h in $hand) { $handIds[[string]$h.id] = $true }

$new = $games | Where-Object { -not $handIds.ContainsKey([string]$_.id) } | Sort-Object -Property playing -Descending
Write-Output "new games to review: $($new.Count)"

$sb = New-Object System.Text.StringBuilder
foreach ($g in $new) {
    $a = $autoMap[[string]$g.id]
    $d = ""
    if ($g.description) { $d = ($g.description -replace "[\r\n]+"," ") -replace "\s{2,}"," " }
    if ($d.Length -gt 150) { $d = $d.Substring(0,150) }
    $line = [PSCustomObject]@{
        id = $g.id
        n  = $g.name
        gl = "$($g.genreL1)/$($g.genreL2)"
        p  = $g.playing
        v  = $g.visits
        ac = $a.c
        at = @($a.t)
        d  = $d
    } | ConvertTo-Json -Compress -Depth 4
    [void]$sb.AppendLine($line)
}
[System.IO.File]::WriteAllText("$PWD\review.jsonl", $sb.ToString(), [System.Text.UTF8Encoding]::new($false))
Write-Output "wrote review.jsonl"
