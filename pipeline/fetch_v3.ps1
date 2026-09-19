$ErrorActionPreference = "Stop"
function Get-J($u){
    $r = Invoke-WebRequest -Uri $u -UseBasicParsing
    [System.Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray()) | ConvertFrom-Json
}
function Batches($ids, $size){
    $out = @()
    for ($i = 0; $i -lt $ids.Count; $i += $size) {
        $end = [Math]::Min($i + $size, $ids.Count) - 1
        $out += ,@($ids[$i..$end])
    }
    return $out
}

$pool = [System.IO.File]::ReadAllText("$PWD\pool.json",[System.Text.Encoding]::UTF8) | ConvertFrom-Json
$sel = $pool | Where-Object { $_.playerCount -ge 1000 -or $_.source -like "chart:*" }
Write-Output "selected: $($sel.Count)"

$meta = @{}
foreach ($g in $sel) { $meta[[string]$g.universeId] = $g }
$ids = @($meta.Keys)

$details = @{}
$b = Batches $ids 50
$n = 0
foreach ($batch in $b) {
    $n++
    try {
        $r = Get-J ("https://games.roblox.com/v1/games?universeIds=" + ($batch -join ","))
        foreach ($item in $r.data) { $details[[string]$item.id] = $item }
    } catch { Write-Output "  detail batch $n failed" }
    if ($n % 5 -eq 0) { Write-Output "  details $($details.Count)/$($ids.Count)" }
    Start-Sleep -Milliseconds 220
}
Write-Output "details: $($details.Count)"

$icons = @{}
$n = 0
foreach ($batch in $b) {
    $n++
    try {
        $r = Get-J ("https://thumbnails.roblox.com/v1/games/icons?universeIds=" + ($batch -join ",") + "&size=256x256&format=Png&isCircular=false")
        foreach ($item in $r.data) { if ($item.imageUrl) { $icons[[string]$item.targetId] = $item.imageUrl } }
    } catch { Write-Output "  icon batch $n failed" }
    Start-Sleep -Milliseconds 220
}
Write-Output "icons: $($icons.Count)"

$thumbs = @{}
foreach ($batch in $b) {
    try {
        $r = Get-J ("https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds=" + ($batch -join ",") + "&size=768x432&format=Png&countPerUniverse=1&defaults=true")
        foreach ($item in $r.data) {
            if ($item.thumbnails -and $item.thumbnails.Count -gt 0 -and $item.thumbnails[0].imageUrl) {
                $thumbs[[string]$item.universeId] = $item.thumbnails[0].imageUrl
            }
        }
    } catch { }
    Start-Sleep -Milliseconds 220
}
Write-Output "thumbs: $($thumbs.Count)"

$out = @()
foreach ($id in $ids) {
    $d = $details[$id]
    if (-not $d) { continue }
    $m = $meta[$id]
    $out += [PSCustomObject]@{
        id          = $d.id
        place       = $d.rootPlaceId
        name        = $d.name
        description = $d.description
        icon        = $icons[$id]
        thumb       = $thumbs[$id]
        genreL1     = $(if ($d.genre_l1) { $d.genre_l1 } else { $m.genre })
        genreL2     = $d.genre_l2
        playing     = $d.playing
        visits      = $d.visits
        favorites   = $d.favoritedCount
        maxPlayers  = $d.maxPlayers
        up          = $m.up
        down        = $m.down
        created     = $d.created
        updated     = $d.updated
        creatorId   = $d.creator.id
        creatorName = $d.creator.name
        creatorType = $d.creator.type
        verified    = $d.creator.hasVerifiedBadge
        maturity    = $m.maturity
        minAge      = $m.minAge
        source      = $m.source
    }
}

$json = $out | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText("$PWD\raw_v3.json", $json, [System.Text.UTF8Encoding]::new($false))
Write-Output "saved raw_v3.json with $($out.Count) games"
