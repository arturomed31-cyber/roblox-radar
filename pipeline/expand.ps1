$ErrorActionPreference = "Stop"
function Get-J($u){
    $r = Invoke-WebRequest -Uri $u -UseBasicParsing
    [System.Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray()) | ConvertFrom-Json
}

$pool = @{}   # universeId -> minimal record from charts/search

# --- 1. chart sorts ---
foreach ($s in @("top-playing-now","top-trending","up-and-coming","fun-with-friends")) {
    $d = Get-J "https://apis.roblox.com/explore-api/v1/get-sort-content?sessionId=rad$(Get-Random)&sortId=$s&device=computer&country=us"
    foreach ($g in $d.games) {
        $id = [string]$g.universeId
        if (-not $pool.ContainsKey($id)) {
            $pool[$id] = [PSCustomObject]@{
                universeId=$g.universeId; rootPlaceId=$g.rootPlaceId
                playerCount=$g.playerCount; up=$g.totalUpVotes; down=$g.totalDownVotes
                minAge=$g.minimumAge; maturity=$g.contentMaturity; genre=$g.genreL1
                source="chart:$s"
            }
        }
    }
}
Write-Output "after charts: $($pool.Count)"

# --- 2. keyword search ---
$keywords = @(
 "simulator","tycoon","obby","tower","rpg","anime","horror","roleplay","shooter","fps",
 "brainrot","steal","minecraft","murder mystery","racing","soccer","football","basketball","fishing","pet",
 "survival","clicker","battlegrounds","escape","prison","city","school","zombie","parkour","sword",
 "magic","farm","restaurant","hotel","hangout","duels","rng","mining","build","craft",
 "backrooms","granny","squid game","bed wars","one piece","dragon ball","naruto","car","train","plane",
 "pizza","baby","family","dress up","story","scary","gun","war","army","ninja",
 "dungeon","idle","grow","kick","slap","lift","race","pvp","trading","hide and seek"
)

$i = 0
foreach ($kw in $keywords) {
    $i++
    $token = ""
    for ($page = 0; $page -lt 2; $page++) {
        $enc = [uri]::EscapeDataString($kw)
        $url = "https://apis.roblox.com/search-api/omni-search?searchQuery=$enc&pageToken=$token&sessionId=rad$(Get-Random)&pageType=all"
        try { $d = Get-J $url } catch { break }
        $entries = $d.searchResults | Where-Object { $_.contentGroupType -eq 'Game' } | ForEach-Object { $_.contents }
        foreach ($g in $entries) {
            if (-not $g.universeId) { continue }
            $id = [string]$g.universeId
            if (-not $pool.ContainsKey($id)) {
                $pool[$id] = [PSCustomObject]@{
                    universeId=$g.universeId; rootPlaceId=$g.rootPlaceId
                    playerCount=$g.playerCount; up=$g.totalUpVotes; down=$g.totalDownVotes
                    minAge=$g.minimumAge; maturity=$g.contentMaturity; genre=""
                    source="search:$kw"
                }
            }
        }
        $token = $d.nextPageToken
        if (-not $token) { break }
        Start-Sleep -Milliseconds 180
    }
    if ($i % 10 -eq 0) { Write-Output "  [$i/$($keywords.Count)] pool: $($pool.Count)" }
    Start-Sleep -Milliseconds 120
}

Write-Output "raw pool: $($pool.Count)"

# keep games with meaningful live traffic
$kept = $pool.Values | Where-Object { $_.playerCount -ge 250 } | Sort-Object -Property playerCount -Descending
Write-Output "with >=250 players: $($kept.Count)"

$json = $kept | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText("$PWD\pool.json", $json, [System.Text.UTF8Encoding]::new($false))
Write-Output "saved pool.json"
