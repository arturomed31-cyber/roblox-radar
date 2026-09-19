$ErrorActionPreference = "Stop"

$games = [System.IO.File]::ReadAllText("$PWD\raw_v3.json",[System.Text.Encoding]::UTF8) | ConvertFrom-Json

$GENRE_MAP = @{
  "Simulation"="sim"; "Roleplay & Avatar Sim"="rp"; "Shooter"="shooter"; "Action"="fight";
  "Obby & Platformer"="obby"; "Sports & Racing"="sports"; "RPG"="rpg"; "Survival"="horror";
  "Party & Casual"="party"; "Strategy"="strategy"; "Adventure"="rpg"; "Puzzle"="party";
  "Shopping"="other"; "Entertainment"="other"; "Education"="other"; "Utility & Other"="other";
  "Social"="rp"; "Building"="sandbox"
}

$ANIME_WORDS = @("anime","naruto","one piece","dragon ball","jujutsu","demon slayer","bleach","titan",
  "blue lock","sung jinwoo","solo leveling","goku","sasuke","manga","shinobi","ninja way","hunter x",
  "my hero","deku","gojo","luffy","zoro","uzumaki","saitama","one punch","kaiju no","chainsaw man","uma")

$LICENSED_WORDS = @("naruto","one piece","dragon ball","jujutsu kaisen","demon slayer","bleach",
  "attack on titan","blue lock","solo leveling","my hero academia","one punch","sonic","mario","pokemon",
  "pokémon","squid game","spongebob","nfl","fifa","nba","five nights","fnaf","undertale","deltarune",
  "death note","walking dead","scp","hello kitty","sanrio","minecraft","fortnite","among us","kaiju no",
  "chainsaw man","doraemon","hunter x hunter","stranger things","barbie","disney","marvel","dc comics",
  "batman","spider-man","star wars","harry potter","transformers","hot wheels","umamusume")

function Get-Class($g){
  $name = ($g.name).ToLower()
  $desc = ""
  if ($g.description) { $desc = ($g.description).ToLower() }
  $text = "$name $desc"
  $gl1 = $g.genreL1
  $gl2 = $g.genreL2

  # ---------- category ----------
  $cat = $GENRE_MAP[$gl1]
  if (-not $cat) { $cat = "other" }

  if ($name -match '\btycoon\b|\bsimulator\b|\bclicker\b|\bidle\b' ) { $cat = "sim" }
  if ($name -match '\+\s?\d' ) { $cat = "sim" }
  if ($name -match '\bobby\b|\bparkour\b|difficulty chart') { $cat = "obby" }
  if ($name -match 'tower of |tower climb') { $cat = "obby" }
  if ($text -match 'tower defense|place units to defend|defend against waves') { $cat = "strategy" }
  if ($name -match '\brp\b|roleplay|role play') { $cat = "rp" }
  if ($name -match 'battlegrounds|\bduels\b|fighting game') { $cat = "fight" }
  if ($name -match '\bfps\b|\bshooter\b|sniper|strike\b') { $cat = "shooter" }
  if ($text -match 'horror game|scary|nextbot|backrooms|survive the night|jumpscare') { $cat = "horror" }
  if ($gl1 -eq "Survival" -and $name -match 'steal|grow|collect|tycoon') { $cat = "sim" }
  # open-world action (hood / crime / city combat) distinct from arena fighting
  if ($cat -eq "fight" -and ($text -match 'hood|open world|open-world|rob banks|criminal|gang|police|city where|streets')) { $cat = "action" }

  # ---------- tags ----------
  $tags = New-Object System.Collections.Generic.List[string]

  if ($text -match 'brainrot|tung tung|tralalero|bombardiro|sahur|crocodilo|ballerina cappuccina') { $tags.Add("brainrot") }

  if ($name -match '\bsteal\b|\bsteal a\b' -or
      ($desc -match 'steal (a|an|the)? ?\w* ?(from|back)' -and $desc -match 'base|plot|pen|island|farm')) {
      $tags.Add("steal-pattern")
  }

  if ($name -match '\+\s?1\b' -or $desc -match 'every step = \+1|click to gain \+1|\+1 (speed|damage|strength|power) per') {
      $tags.Add("plus1-pattern")
  }

  if ($name -match '\bduels?\b') { $tags.Add("duels-pattern") }

  if ($name -match '\btower\b' -and $name -notmatch 'tower defense') { $tags.Add("tower") }
  if ($text -match 'tower defense' -or $name -match '\btd\b') { $tags.Add("tower-defense") }

  if ($g.id -ne 66654135 -and ($name -match 'murder mystery|murderers? vs|mm2' -or
      ($desc -match 'murderer' -and $desc -match 'sheriff|innocent'))) {
      $tags.Add("mm2-clone")
  }
  if ($g.id -eq 66654135) { $tags.Add("mm2-original") }

  if ($name -match 'bed ?wars|sky ?wars|block ?craft|mine ?craft|skyblock' -or
      $desc -match 'bed wars|mine blocks|craft and build blocks') {
      $tags.Add("minecraft-clone")
  }

  if ($text -match '\brng\b|gacha|roll for|hatch eggs|summon units|luck multiplier|aura|spin to|open packs|unbox') {
      $tags.Add("rng-gacha")
  }

  foreach ($w in $ANIME_WORDS) { if ($text -match [regex]::Escape($w)) { $tags.Add("anime"); break } }
  foreach ($w in $LICENSED_WORDS) { if ($text -match [regex]::Escape($w)) { $tags.Add("licensed-ip"); break } }

  if ($desc -match 'inspired by|fan game|fangame|based on the (anime|series|game)|tribute to') { $tags.Add("copycat") }

  $out = @($tags | Sort-Object -Unique)
  return [PSCustomObject]@{ cat = $cat; tags = $out }
}

$res = @()
foreach ($g in $games) {
    $c = Get-Class $g
    $res += [PSCustomObject]@{ id = $g.id; c = $c.cat; t = @($c.tags) }
}

$json = $res | ConvertTo-Json -Depth 4 -Compress
[System.IO.File]::WriteAllText("$PWD\auto_class.json", $json, [System.Text.UTF8Encoding]::new($false))
Write-Output "auto-classified $($res.Count) games"
$res | Group-Object c | Sort-Object Count -Descending | ForEach-Object { "  $($_.Name): $($_.Count)" }
