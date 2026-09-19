$ErrorActionPreference = "Stop"
function Get-J($u){
    $r = Invoke-WebRequest -Uri $u -UseBasicParsing
    [System.Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray()) | ConvertFrom-Json
}

$pool = [System.IO.File]::ReadAllText("$PWD\pool.json",[System.Text.Encoding]::UTF8) | ConvertFrom-Json
$sel  = $pool | Where-Object { $_.playerCount -ge 1000 -or $_.source -like "chart:*" }
$meta = @{}
foreach ($g in $sel) { $meta[[string]$g.universeId] = $g }

$have = [System.IO.File]::ReadAllText("$PWD\raw_v3.json",[System.Text.Encoding]::UTF8) | ConvertFrom-Json
$haveIds = @{}
foreach ($g in $have) { $haveIds[[string]$g.id] = $true }

$missing = @($meta.Keys | Where-Object { -not $haveIds.ContainsKey($_) })
Write-Output "missing details: $($missing.Count)"

# icons/thumbs for all were already fetched; re-pull for the missing ones only
$icons = @{}; $thumbs = @{}
$new = @()
$batchSize = 25
for ($i = 0; $i -lt $missing.Count; $i += $batchSize) {
    $end = [Math]::Min($i + $batchSize, $missing.Count) - 1
    $batch = @($missing[$i..$end])
    $idList = $batch -join ","

    $detail = $null
    for ($try = 1; $try -le 4; $try++) {
        try { $detail = Get-J "https://games.roblox.com/v1/games?universeIds=$idList"; break }
        catch { Start-Sleep -Seconds ($try * 3) }
    }
    if (-not $detail) { Write-Output "  giving up on batch at $i"; continue }

    try {
        $r = Get-J "https://thumbnails.roblox.com/v1/games/icons?universeIds=$idList&size=256x256&format=Png&isCircular=false"
        foreach ($item in $r.data) { if ($item.imageUrl) { $icons[[string]$item.targetId] = $item.imageUrl } }
    } catch {}
    try {
        $r = Get-J "https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds=$idList&size=768x432&format=Png&countPerUniverse=1&defaults=true"
        foreach ($item in $r.data) {
            if ($item.thumbnails -and $item.thumbnails.Count -gt 0) { $thumbs[[string]$item.universeId] = $item.thumbnails[0].imageUrl }
        }
    } catch {}

    foreach ($d in $detail.data) {
        $id = [string]$d.id
        $m = $meta[$id]
        $new += [PSCustomObject]@{
            id=$d.id; place=$d.rootPlaceId; name=$d.name; description=$d.description
            icon=$icons[$id]; thumb=$thumbs[$id]
            genreL1=$(if ($d.genre_l1) { $d.genre_l1 } else { $m.genre }); genreL2=$d.genre_l2
            playing=$d.playing; visits=$d.visits; favorites=$d.favoritedCount; maxPlayers=$d.maxPlayers
            up=$m.up; down=$m.down; created=$d.created; updated=$d.updated
            creatorId=$d.creator.id; creatorName=$d.creator.name; creatorType=$d.creator.type
            verified=$d.creator.hasVerifiedBadge; maturity=$m.maturity; minAge=$m.minAge; source=$m.source
        }
    }
    Write-Output "  recovered: $($new.Count)"
    Start-Sleep -Milliseconds 1200
}

$all = @($have) + @($new)
$json = $all | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText("$PWD\raw_v3.json", $json, [System.Text.UTF8Encoding]::new($false))
Write-Output "raw_v3.json now has $($all.Count) games"
