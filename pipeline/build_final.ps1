$ErrorActionPreference = "Stop"
function ReadJson($p){ [System.IO.File]::ReadAllText("$PWD\$p", [System.Text.Encoding]::UTF8) | ConvertFrom-Json }

$games     = ReadJson "raw_v3.json"
$auto      = ReadJson "auto_class.json"
$overrides = ReadJson "overrides.json"
$hand      = ReadJson "classification_v2.json"

$imgMeta = ReadJson "images_meta.json"
$spriteMap = @{}
foreach ($p in $imgMeta.map.PSObject.Properties) { $spriteMap[$p.Name] = @($p.Value) }
$thumbSet = @{}
foreach ($t in $imgMeta.thumbs) { $thumbSet[[string]$t] = $true }

$cls = @{}
foreach ($a in $auto)      { $cls[[string]$a.id] = [PSCustomObject]@{ c=$a.c; t=@($a.t); src="rules" } }
foreach ($o in $overrides) { $cls[[string]$o.id] = [PSCustomObject]@{ c=$o.c; t=@($o.t); src="review" } }
foreach ($h in $hand)      { $cls[[string]$h.id] = [PSCustomObject]@{ c=$h.c; t=@($h.t); src="review" } }

# ---- player samples ----
$series = @{}
$stamps = @()
if (Test-Path "$PWD\samples.jsonl") {
    $lines = [System.IO.File]::ReadAllLines("$PWD\samples.jsonl", [System.Text.Encoding]::UTF8)
    $idx = 0
    foreach ($line in $lines) {
        if (-not $line.Trim()) { continue }
        $s = $line | ConvertFrom-Json
        if (-not $s.n -or $s.n -lt 50) { continue }
        $stamps += $s.t
        foreach ($p in $s.c.PSObject.Properties) {
            if (-not $series.ContainsKey($p.Name)) { $series[$p.Name] = @{} }
            $series[$p.Name][$idx] = $p.Value
        }
        $idx++
    }
}
$sampleCount = $stamps.Count
Write-Output "samples loaded: $sampleCount"

# ---- socials from description ----
function Get-Socials($desc){
    $out = @()
    if (-not $desc) { return $out }
    $pats = @(
        @{ k="discord"; r="(?i)(discord\.gg/[A-Za-z0-9\-]+|discord\.com/invite/[A-Za-z0-9\-]+)" },
        @{ k="youtube"; r="(?i)(youtube\.com/[A-Za-z0-9_\-/@\.]+|youtu\.be/[A-Za-z0-9_\-]+)" },
        @{ k="x";       r="(?i)((?:twitter|x)\.com/[A-Za-z0-9_]+)" },
        @{ k="tiktok";  r="(?i)(tiktok\.com/@?[A-Za-z0-9_\.]+)" },
        @{ k="group";   r="(?i)(roblox\.com/(?:groups|communities)/\d+)" }
    )
    foreach ($p in $pats) {
        $m = [regex]::Match($desc, $p.r)
        if ($m.Success) {
            $u = $m.Value
            if ($u -notmatch "^https?://") { $u = "https://" + $u }
            $out += [PSCustomObject]@{ k = $p.k; u = $u }
        }
    }
    return $out
}

$out = @()
foreach ($g in $games) {
    $id = [string]$g.id
    $c = $cls[$id]
    if (-not $c) { $c = [PSCustomObject]@{ c="other"; t=@(); src="rules" } }

    $tot = $g.up + $g.down
    $like = $null
    if ($tot -gt 0) { $like = [Math]::Round(100.0 * $g.up / $tot) }
    $ageDays = $null
    if ($g.created) { $ageDays = [int]((Get-Date) - [datetime]$g.created).TotalDays }
    $updDays = $null
    if ($g.updated) { $updDays = [int]((Get-Date) - [datetime]$g.updated).TotalDays }

    $hist = @()
    if ($series.ContainsKey($id)) {
        for ($i = 0; $i -lt $sampleCount; $i++) {
            if ($series[$id].ContainsKey($i)) { $hist += $series[$id][$i] } else { $hist += $null }
        }
    }

    $creatorUrl = $null
    if ($g.creatorType -eq "Group") { $creatorUrl = "https://www.roblox.com/communities/$($g.creatorId)" }
    elseif ($g.creatorId)           { $creatorUrl = "https://www.roblox.com/users/$($g.creatorId)/profile" }

    $vpd = $null
    if ($ageDays -and $ageDays -gt 0) { $vpd = [int]($g.visits / $ageDays) }

    $out += [PSCustomObject]@{
        id       = $g.id
        place    = $g.place
        name     = $g.name
        sp       = $(if ($spriteMap.ContainsKey($id)) { @($spriteMap[$id]) } else { $null })
        th       = [bool]$thumbSet.ContainsKey($id)
        cat      = $c.c
        tags     = @($c.t)
        src      = $c.src
        playing  = $g.playing
        visits   = $g.visits
        favs     = $g.favorites
        like     = $like
        votes    = $tot
        age      = $ageDays
        upd      = $updDays
        maxP     = $g.maxPlayers
        genre    = "$($g.genreL1)$(if($g.genreL2){" / " + $g.genreL2})"
        creator  = $g.creatorName
        cType    = $g.creatorType
        cUrl     = $creatorUrl
        verified = [bool]$g.verified
        maturity = $g.maturity
        vpd      = $vpd
        hist     = @($hist)
        socials  = @(Get-Socials $g.description)
    }
}

$meta = [PSCustomObject]@{
    generated   = (Get-Date).ToUniversalTime().ToString("o")
    sampleTimes = @($stamps)
    sprite      = [PSCustomObject]@{ cell = $imgMeta.cell; cols = $imgMeta.cols; rows = $imgMeta.rows }
    games       = $out
}

$json = $meta | ConvertTo-Json -Depth 8 -Compress
[System.IO.File]::WriteAllText("$PWD\games_final.json", $json, [System.Text.UTF8Encoding]::new($false))
Write-Output "games_final.json -> $($out.Count) games, $sampleCount samples"
Write-Output "with socials: $(($out | Where-Object { $_.socials.Count -gt 0 }).Count)"
Write-Output "reviewed by hand: $(($out | Where-Object { $_.src -eq 'review' }).Count)"
