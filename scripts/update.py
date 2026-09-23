"""Refresh for Roblox Radar.

Reads data/games.json, pulls fresh live stats for every tracked game from
Roblox's public APIs, appends one reading per game to data/history.json and
rewrites the live fields in data/games.json. With --light only player counts
and visits are read (about a minute). Slow business data (groups, passes,
social links) lives in scripts/enrich.py. Standard library only.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from histstore import load_history, save_history  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "data" / "games.json"
TRENDS = ROOT / "data" / "trends.json"   # small per-game 24h/7d/30d changes for the Discord bot

BATCH = 50
PAUSE = 1.0   # Roblox answers 429 at a faster pace, even from GitHub
UA = "roblox-radar/1.0 (+https://github.com)"


class Unauthorized(Exception):
    def __init__(self, code):
        super().__init__(f"HTTP {code}")
        self.code = code


def get_json(url, tries=5, headers=None):
    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise Unauthorized(e.code)
            wait = min(90, 5 * 2 ** attempt)
            print(f"  retry {attempt + 1}/{tries} after {wait}s: {e}", flush=True)
            time.sleep(wait)
        except Exception as e:  # rate limits, transient errors
            wait = min(90, 5 * 2 ** attempt)
            print(f"  retry {attempt + 1}/{tries} after {wait}s: {e}", flush=True)
            time.sleep(wait)
    return None


def batches(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


RAW_DAYS = 30  # keep every reading for this long; older days collapse to one daily peak


def compact_history(history):
    """Collapse readings older than RAW_DAYS into one daily-peak reading per UTC day."""
    times = history["times"]
    if not times:
        return
    cutoff = datetime.now(timezone.utc).timestamp() * 1000 - RAW_DAYS * 86400e3
    parsed = [datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() * 1000 for x in times]
    old_idx = [i for i, ms in enumerate(parsed) if ms < cutoff]
    if not old_idx:
        return
    # group old readings by UTC date
    by_day = {}
    for i in old_idx:
        day = datetime.fromtimestamp(parsed[i] / 1000, timezone.utc).strftime("%Y-%m-%d")
        by_day.setdefault(day, []).append(i)
    # a day already collapsed has exactly one reading at 12:00Z; leave it alone
    collapsible = {d: idx for d, idx in by_day.items() if not (len(idx) == 1 and times[idx[0]].endswith("T12:00:00Z"))}
    if not collapsible:
        return
    keep_idx = [i for i in range(len(times)) if not any(i in idx for idx in collapsible.values())]
    new_times, new_series = [], {gid: [] for gid in history["series"]}
    # rebuild: collapsed days first (in order), then everything kept, then sort by time
    entries = []
    for day, idx in sorted(collapsible.items()):
        stamp = f"{day}T12:00:00Z"
        vals = {}
        for gid, s in history["series"].items():
            best = None
            for i in idx:
                if i < len(s) and s[i] is not None and (best is None or s[i] > best):
                    best = s[i]
            vals[gid] = best
        entries.append((stamp, vals))
    for i in keep_idx:
        entries.append((times[i], {gid: (s[i] if i < len(s) else None) for gid, s in history["series"].items()}))
    entries.sort(key=lambda e: e[0])
    for stamp, vals in entries:
        new_times.append(stamp)
        for gid in new_series:
            new_series[gid].append(vals.get(gid))
    history["times"] = new_times
    history["series"] = new_series
    print(f"  history compacted: {len(collapsible)} old days collapsed, {len(new_times)} readings kept", flush=True)


def same_hour_reading(times_s, days):
    """Index of the reading closest to `days` ago at a similar time of day (+/-3h), or None."""
    last = times_s[-1]
    target, min_back = last - days * 86400, last - days * 86400 * 0.7
    best = None
    for i, ts in enumerate(times_s):
        if ts > min_back:
            break
        d = abs((ts % 86400) - (last % 86400))
        if min(d, 86400 - d) > 3 * 3600:
            continue
        if best is None or abs(ts - target) < abs(times_s[best] - target):
            best = i
    return best


def write_trends(history, stamp, visits=None):
    """Per-game numbers the page needs without downloading the history: 24h/7d/30d change
    (same time of day), average of the last 24 h (for DAU/earnings) and the peak on record."""
    times_s = [datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() for x in history["times"]]
    refs = [same_hour_reading(times_s, d) for d in (1, 7, 30)]
    last = times_s[-1] if times_s else 0
    day_idx = [i for i, ts in enumerate(times_s) if ts >= last - 86400]
    out = {}
    for gid, s in history["series"].items():
        cur = s[-1] if len(s) == len(times_s) else None
        row = {}
        if cur is not None:
            row["p"] = cur                      # players now: the table reads this, not games.json
        for k, r in zip(("d1", "d7", "d30"), refs):
            prev = s[r] if r is not None and r < len(s) else None
            if cur is not None and prev:
                row[k] = round((cur - prev) / prev * 100, 1)
        vals24 = [s[i] for i in day_idx if i < len(s) and s[i] is not None]
        if len(vals24) >= 3:
            row["a24"] = round(sum(vals24) / len(vals24))
        peak = max((v for v in s if v is not None), default=None)
        if peak is not None:
            row["pk"] = peak
        if visits and visits.get(gid) is not None:
            row["v"] = visits[gid]
        if row:
            out[gid] = row
    TRENDS.write_text(json.dumps({"generated": stamp, "n": len(times_s),
                                  "first": history["times"][0] if history["times"] else None,
                                  "last": history["times"][-1] if history["times"] else None, "t": out},
                                 separators=(",", ":")), encoding="utf-8")


def main():
    light = "--light" in sys.argv
    games_doc = json.loads(GAMES.read_text(encoding="utf-8"))
    history = load_history()
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
        if light:
            continue
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

    compact_history(history)
    write_trends(history, stamp, {gid: (d.get("visits") if d else None) for gid, d in details.items()})
    save_history(history)
    if light:
        # games.json belongs to the daily refresh and to discovery; a reading that rewrote it
        # could undo games those jobs had just added
        print("light run: history and trends only, games.json untouched", flush=True)
    else:
        games_doc["generated"] = stamp
        GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"done: {len(details)} games updated, history now has {len(history['times'])} readings")


if __name__ == "__main__":
    main()
