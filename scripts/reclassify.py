"""Re-run the classification rules over every automatically classified game.

Fetches fresh name/description/genre from Roblox and applies discover.classify();
hand-reviewed games (src == "review") and data/overrides.json are never touched.

    python scripts/reclassify.py            # apply
    python scripts/reclassify.py --dry-run  # only print what would change
"""
import json
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover import classify, get_json, batches  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "data" / "games.json"
OVERRIDES = ROOT / "data" / "overrides.json"


def main():
    dry = "--dry-run" in sys.argv
    doc = json.loads(GAMES.read_text(encoding="utf-8"))
    overrides = {str(o["id"]): o for o in json.loads(OVERRIDES.read_text(encoding="utf-8"))}
    auto = [g for g in doc["games"] if g.get("src") != "review" and str(g["id"]) not in overrides]
    print(f"{len(auto)} auto-classified games to re-check", flush=True)

    details = {}
    for chunk in batches([str(g["id"]) for g in auto], 50):
        d = get_json("https://games.roblox.com/v1/games?universeIds=" + ",".join(chunk))
        for item in (d or {}).get("data", []):
            details[str(item["id"])] = item
        time.sleep(1.0)

    changed_cat, changed_tags = 0, 0
    tag_delta = {}
    for g in auto:
        d = details.get(str(g["id"]))
        if not d:
            continue
        cat, tags = classify(d.get("name"), d.get("description"), d.get("genre_l1"))
        if cat != g["cat"]:
            changed_cat += 1
            if dry:
                print(f"  cat {g['cat']} -> {cat}: {g['name'][:60]}")
        if sorted(tags) != sorted(g["tags"]):
            changed_tags += 1
            for t in set(tags) - set(g["tags"]):
                tag_delta[t] = tag_delta.get(t, 0) + 1
            for t in set(g["tags"]) - set(tags):
                tag_delta[t] = tag_delta.get(t, 0) - 1
        if not dry:
            g["cat"], g["tags"] = cat, tags
            g["name"] = d.get("name") or g["name"]
    print(f"category changes: {changed_cat}, tag changes: {changed_tags}")
    print("net tag delta:", dict(sorted(tag_delta.items(), key=lambda x: x[1])))
    if not dry:
        GAMES.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print("games.json updated")
    if "--dump" in sys.argv:   # material for a hand review: name, description snippet, current labels
        rows = [{"id": g["id"], "p": g.get("playing"), "name": g["name"], "genre": (details.get(str(g["id"])) or {}).get("genre_l1"),
                 "desc": ((details.get(str(g["id"])) or {}).get("description") or "")[:280].replace(chr(10), " "),
                 "cat": g["cat"], "tags": g["tags"]} for g in auto if str(g["id"]) in details]
        rows.sort(key=lambda r: -(r["p"] or 0))
        (ROOT / ".claude" / "review_dump.json").write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"dumped {len(rows)} rows for review")


if __name__ == "__main__":
    main()
