"""Daily refresh for Roblox Radar.

Reads data/games.json, pulls fresh live stats for every tracked game from
Roblox's public APIs, appends one reading per game to data/history.json and
rewrites the live fields in data/games.json. Standard library only.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "data" / "games.json"
HISTORY = ROOT / "data" / "history.json"

BATCH = 50
PAUSE = 1.0
UA = "roblox-radar/1.0 (+https://github.com)"


def get_json(url, tries=5):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # rate limits, transient errors
            wait = min(90, 5 * 2 ** attempt)
            print(f"  retry {attempt + 1}/{tries} after {wait}s: {e}", flush=True)
            time.sleep(wait)
    return None


def batches(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def main():
    games_doc = json.loads(GAMES.read_text(encoding="utf-8"))
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    games = games_doc["games"]
    ids = [str(g["id"]) for g in games]

    details, votes, icons, thumbs = {}, {}, {}, {}
    for chunk in batches(ids, BATCH):
        q = ",".join(chunk)
        d = get_json(f"https://games.roblox.com/v1/games?universeIds={q}")
        if d:
            for item in d.get("data", []):
                details[str(item["id"])] = item
        time.sleep(PAUSE)
        v = get_json(f"https://games.roblox.com/v1/games/votes?universeIds={q}")
        if v:
            for item in v.get("data", []):
                votes[str(item["id"])] = item
        time.sleep(PAUSE)
        ic = get_json(
            f"https://thumbnails.roblox.com/v1/games/icons?universeIds={q}&size=256x256&format=Png&isCircular=false")
        if ic:
            for item in ic.get("data", []):
                if item.get("imageUrl"):
                    icons[str(item["targetId"])] = item["imageUrl"]
        time.sleep(PAUSE)
        th = get_json(
            f"https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds={q}&size=768x432&format=Png&countPerUniverse=1&defaults=true")
        if th:
            for item in th.get("data", []):
                t = item.get("thumbnails") or []
                if t and t[0].get("imageUrl"):
                    thumbs[str(item["universeId"])] = t[0]["imageUrl"]
        time.sleep(PAUSE)
        print(f"  {len(details)}/{len(ids)} games fetched", flush=True)

    if len(details) < len(ids) * 0.5:
        print("Too few games fetched; leaving files untouched.")
        sys.exit(1)

    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    history["times"].append(stamp)
    for g in games:
        gid = str(g["id"])
        d = details.get(gid)
        history["series"].setdefault(gid, [])
        # keep every series aligned with the times array
        while len(history["series"][gid]) < len(history["times"]) - 1:
            history["series"][gid].append(None)
        history["series"][gid].append(d["playing"] if d else None)
        if not d:
            continue
        g["playing"] = d.get("playing")
        g["visits"] = d.get("visits")
        g["favs"] = d.get("favoritedCount")
        g["updated"] = d.get("updated")
        g["maxP"] = d.get("maxPlayers")
        vt = votes.get(gid)
        if vt:
            up, down = vt.get("upVotes", 0), vt.get("downVotes", 0)
            g["votes"] = up + down
            g["like"] = round(100 * up / (up + down)) if up + down else None
        if icons.get(gid):
            g["icon"] = icons[gid]
        if thumbs.get(gid):
            g["thumb"] = thumbs[gid]

    games_doc["generated"] = stamp
    GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"done: {len(details)} games updated, history now has {len(history['times'])} readings")


if __name__ == "__main__":
    main()
