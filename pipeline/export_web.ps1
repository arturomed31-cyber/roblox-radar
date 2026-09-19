$ErrorActionPreference = "Stop"
$dest = "C:\Users\artur\Documents\roblox-radar"
New-Item -ItemType Directory -Force -Path "$dest\data" | Out-Null
function ReadJson($p){ [System.IO.File]::ReadAllText("$PWD\$p", [System.Text.Encoding]::UTF8) | ConvertFrom-Json }

$raw   = ReadJson "raw_v3.json"
$final = (ReadJson "games_final.json")
$rawMap = @{}
foreach ($r in $raw) { $rawMap[[string]$r.id] = $r }

$games = @()
foreach ($g in $final.games) {
    $r = $rawMap[[string]$g.id]
    $games += [PSCustomObject]@{
        id = $g.id; place = $g.place; name = $g.name
        icon = $r.icon; thumb = $r.thumb
        cat = $g.cat; tags = @($g.tags); src = $g.src
        playing = $g.playing; visits = $g.visits; favs = $g.favs
        like = $g.like; votes = $g.votes
        created = $r.created; updated = $r.updated
        maxP = $g.maxP; genre = $g.genre
        creator = $g.creator; cType = $g.cType; cUrl = $g.cUrl; verified = $g.verified
        maturity = $g.maturity; socials = @($g.socials)
    }
}
$gj = [PSCustomObject]@{ generated = $final.generated; games = $games } | ConvertTo-Json -Depth 8 -Compress
[System.IO.File]::WriteAllText("$dest\data\games.json", $gj, [System.Text.UTF8Encoding]::new($false))
Write-Output "games.json: $($games.Count) games"

$series = [ordered]@{}
foreach ($g in $final.games) { $series[[string]$g.id] = @($g.hist) }
$hj = [PSCustomObject]@{ times = @($final.sampleTimes); series = $series } | ConvertTo-Json -Depth 5 -Compress
[System.IO.File]::WriteAllText("$dest\data\history.json", $hj, [System.Text.UTF8Encoding]::new($false))
Write-Output "history.json: $($final.sampleTimes.Count) samples"
