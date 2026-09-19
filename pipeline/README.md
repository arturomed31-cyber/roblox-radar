# Data pipeline

One-off PowerShell scripts used to build `data/games.json` the first time. The daily refresh does
not need them — `scripts/update.py` handles that. Re-run these when you want to discover new games
or redo the classification. Run them from inside this folder; intermediates land here and are ignored by git.

Order:

1. `expand.ps1` — chart sorts + ~70 keyword searches → `pool.json` (games with 250+ players).
2. `fetch_v3.ps1` then `fetch_v3_retry.ps1` — details, icons, thumbnails → `raw_v3.json`.
3. `classify_rules.ps1` — keyword rules → `auto_class.json`.
4. `make_review.ps1` — writes `review.jsonl` for hand review; corrections go in `classification/overrides.json`.
   `classification/classification_v2.json` holds the fully hand-classified first batch and wins over everything.
5. `sampler.ps1` (optional) — local player-count sampling into `samples.jsonl`.
6. `build_final.ps1` → `games_final.json`, then `export_web.ps1` → `../data/games.json` + `../data/history.json`.

`build_images.ps1` builds a sprite sheet; only needed for the claude.ai artifact version, not the website.

Note: `export_web.ps1` overwrites `data/history.json`. To keep accumulated history, merge instead of overwriting.
