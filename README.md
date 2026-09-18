# Roblox Radar

A scanner for the Roblox games that currently hold real traffic, tagged by what each game actually is
(category + copy patterns such as brainrot, "+1 per click", "steal a X", MM2 / Minecraft clones) with
a daily player-history chart per game.

- `index.html` — the whole site (no build step). Reads `data/games.json` and `data/history.json`.
- `data/games.json` — 823 games with metadata, classification, live stats and image URLs.
- `data/history.json` — one player-count reading per game per refresh (`times[]` + `series{id:[...]}`).
- `scripts/update.py` — pulls fresh stats from Roblox's public APIs and appends to the history. Standard library only.
- `.github/workflows/daily.yml` — runs the update every day at 20:00 UTC and commits the result.

## Run locally

```bash
python -m http.server 8080
```

Then open http://localhost:8080. Opening `index.html` straight from disk will not work because the page fetches JSON.

## Refresh the data by hand

```bash
python scripts/update.py
```

## How classification works

`cat` is one of: sim, rp, shooter, fight, action, obby, sports, rpg, horror, party, strategy, sandbox, fangame, other.
`tags` flags patterns: brainrot, mm2-clone, mm2-original, minecraft-clone, tower, tower-defense, steal-pattern,
plus1-pattern, duels-pattern, rng-gacha, copycat, licensed-ip, flagship, anime, meme.
`src` says whether a game was reviewed by hand (`review`) or only by keyword rules (`rules`).
