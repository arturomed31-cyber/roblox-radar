"""Daily refresh for Roblox Radar.

Reads data/games.json, pulls fresh live stats for every tracked game from
Roblox's public APIs, appends one reading per game to data/history.json and
rewrites the live fields in data/games.json. Standard library only.
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

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "data" / "games.json"
HISTORY = ROOT / "data" / "history.json"

BATCH = 50
PAUSE = 1.0
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


SOCIAL_TYPES = {
    "discord": "discord", "youtube": "youtube", "twitter": "x", "x": "x", "tiktok": "tiktok",
    "twitch": "twitch", "facebook": "facebook", "guilded": "guilded", "robloxgroup": "group",
}


def fetch_social_links(games, cookie):
    """Roblox only serves a game's Social Links to a logged-in session."""
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    # probe: is the session valid at all, and which account is it?
    try:
        me = get_json("https://users.roblox.com/v1/users/authenticated", tries=2, headers=headers)
        print(f"  session ok: logged in as user id {me.get('id') if me else '?'}", flush=True)
    except Unauthorized as e:
        print(f"ROBLOX_COOKIE is not a valid session ({e}). Copy .ROBLOSECURITY again and update the secret.", flush=True)
        return 0
    updated = 0
    forbidden = 0
    for i, g in enumerate(games, 1):
        try:
            d = get_json(f"https://games.roblox.com/v1/games/{g['id']}/social-links/list", tries=3, headers=headers)
        except Unauthorized as e:
            if e.code == 403:
                # a few games refuse the request (restricted content); skip them, keep going
                forbidden += 1
                if forbidden == 1:
                    print(f"  403 on game {g['id']} — skipping games that refuse social links", flush=True)
                time.sleep(0.6)
                continue
            print(f"Session expired mid-run ({e}); stopping social links here.", flush=True)
            return updated
        if d is None:
            continue
        links = []
        for item in d.get("data", []):
            k = SOCIAL_TYPES.get(str(item.get("type", "")).lower())
            if k and item.get("url"):
                links.append({"k": k, "u": item["url"], "t": item.get("title") or ""})
        if links or g.get("socials"):
            g["socials"] = links
            updated += 1
        if i % 100 == 0:
            print(f"  social links {i}/{len(games)}", flush=True)
        time.sleep(0.6)
    if forbidden:
        print(f"  {forbidden} games refused social links (403)", flush=True)
    return updated


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


def main():
    light = "--light" in sys.argv
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

    cookie = os.environ.get("ROBLOX_COOKIE", "").strip()
    if light:
        print("light run: players/visits only", flush=True)
    elif cookie:
        n = fetch_social_links(games, cookie)
        print(f"social links refreshed for {n} games", flush=True)
    else:
        print("ROBLOX_COOKIE not set; keeping social links found in descriptions only", flush=True)

    compact_history(history)
    games_doc["generated"] = stamp
    GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"done: {len(details)} games updated, history now has {len(history['times'])} readings")


if __name__ == "__main__":
    main()
