"""Business data for buyers: who owns each game and how it monetizes.

For every tracked game (or only those not enriched in the last N days):
  - owner group: member count, creation date, verified badge
  - game passes: how many and their price range
  - private servers / paid access flags
Everything comes from Roblox's public APIs; standard library only.

    python scripts/enrich.py --max-age 7
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "data" / "games.json"
UA = "roblox-radar/1.0 (+https://github.com)"


def get_json(url, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ra = e.headers.get("Retry-After")
                wait = int(ra) if ra and ra.isdigit() else min(60, 8 * 2 ** attempt)
                print(f"  429, waiting {wait}s", flush=True)
                time.sleep(wait)
            elif e.code in (400, 404):
                return {}
            else:
                time.sleep(min(30, 4 * 2 ** attempt))
        except Exception:
            time.sleep(min(30, 4 * 2 ** attempt))
    return None


def batches(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-age", type=int, default=7, help="re-enrich games older than this many days")
    ap.add_argument("--limit", type=int, default=0, help="stop after this many games (0 = all)")
    args = ap.parse_args()

    doc = json.loads(GAMES.read_text(encoding="utf-8"))
    games = doc["games"]
    today = datetime.now(timezone.utc)
    stamp = today.strftime("%Y-%m-%d")

    def stale(g):
        e = g.get("enrichedAt")
        if not e:
            return True
        return (today - datetime.strptime(e, "%Y-%m-%d").replace(tzinfo=timezone.utc)).days >= args.max_age

    todo = [g for g in games if stale(g)]
    todo.sort(key=lambda g: -(g.get("playing") or 0))
    if args.limit:
        todo = todo[:args.limit]
    print(f"enriching {len(todo)} of {len(games)} games", flush=True)

    # ---- private servers / paid access come with the games batch endpoint ----
    ids = [str(g["id"]) for g in todo]
    flags = {}
    for chunk in batches(ids, 50):
        d = get_json("https://games.roblox.com/v1/games?universeIds=" + ",".join(chunk))
        for item in (d or {}).get("data", []):
            flags[str(item["id"])] = {"vip": bool(item.get("createVipServersAllowed")), "paid": item.get("price")}
        time.sleep(0.8)

    # ---- owner groups ----
    gid_of = {}
    for g in todo:
        if g.get("cType") == "Group" and g.get("cUrl"):
            gid_of[str(g["id"])] = g["cUrl"].rsplit("/", 1)[1]
    groups = {}
    for i, gid in enumerate(sorted(set(gid_of.values())), 1):
        d = get_json(f"https://groups.roblox.com/v1/groups/{gid}")
        if d and d.get("id"):
            groups[gid] = {
                "m": d.get("memberCount"),
                "c": (d.get("created") or "")[:10] or None,
                "v": bool(d.get("hasVerifiedBadge")),
                "n": d.get("name"),
            }
        if i % 100 == 0:
            print(f"  groups {i}/{len(set(gid_of.values()))}", flush=True)
        time.sleep(0.7)
    print(f"  groups fetched: {len(groups)}", flush=True)

    # ---- game passes ----
    done = 0
    for i, g in enumerate(todo, 1):
        gid = str(g["id"])
        d = get_json(f"https://games.roblox.com/v1/games/{gid}/game-passes?limit=100&sortOrder=Asc")
        if d is not None:
            prices = [p.get("price") for p in d.get("data", []) if isinstance(p.get("price"), (int, float)) and p.get("price") > 0]
            g["gp"] = {"n": len(d.get("data", [])), "min": min(prices) if prices else None,
                       "max": max(prices) if prices else None, "sum": sum(prices) if prices else 0}
        f = flags.get(gid)
        if f:
            g["vip"] = f["vip"]
            g["paid"] = f["paid"]
        grp = groups.get(gid_of.get(gid, ""))
        if grp:
            g["grp"] = grp
        g["enrichedAt"] = stamp
        done += 1
        if i % 100 == 0:
            print(f"  passes {i}/{len(todo)}", flush=True)
            GAMES.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        time.sleep(0.6)

    GAMES.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"done: {done} games enriched")


if __name__ == "__main__":
    main()
