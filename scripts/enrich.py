"""Business data for buyers, kept in data/business.json (keyed by game id).

Per game: owner group (members, created, verified), game passes (count, price
range), private-server / paid-access flags and — with a ROBLOX_COOKIE — the
game's Social Links (Discord, YouTube, X…). Slow (one request per game), so it
runs on its own schedule and only touches business.json; readings never wait
for it. Games are re-enriched every --max-age days, most-played first.

    python scripts/enrich.py --max-age 7 [--budget-minutes 50]
"""
import argparse
import json
import re
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "data" / "games.json"
BUSINESS = ROOT / "data" / "business.json"
UA = "roblox-radar/1.0 (+https://github.com)"

SOCIAL_TYPES = {"discord": "discord", "youtube": "youtube", "twitter": "x", "x": "x", "tiktok": "tiktok",
                "twitch": "twitch", "facebook": "facebook", "guilded": "guilded", "robloxgroup": "group"}


SOCIAL_PATTERNS = [
    ("discord", r"(?i)(?:discord\.gg|discord\.com/invite|dsc\.gg)/[A-Za-z0-9\-]{4,}"),
    ("youtube", r"(?i)(?:youtube\.com/(?:@|c/|channel/|user/)[A-Za-z0-9_\-./]+|youtu\.be/[A-Za-z0-9_\-]+)"),
    ("x", r"(?i)(?:twitter|x)\.com/[A-Za-z0-9_]{2,}"),
    ("tiktok", r"(?i)tiktok\.com/@[A-Za-z0-9_.]{2,}"),
]


def socials_in_text(text):
    """Invite links a developer wrote in the game description (no cookie needed)."""
    out = []
    for kind, pat in SOCIAL_PATTERNS:
        m = re.search(pat, text or "")
        if m:
            u = m.group(0)
            out.append({"k": kind, "u": u if u.startswith("http") else "https://" + u, "t": "description"})
    return out


class Unauthorized(Exception):
    def __init__(self, code):
        super().__init__(f"HTTP {code}")
        self.code = code


def get_json(url, tries=4, headers=None):
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


def save(biz):
    BUSINESS.write_text(json.dumps(biz, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-age", type=int, default=7)
    ap.add_argument("--budget-minutes", type=int, default=50, help="stop (and save) after this long")
    args = ap.parse_args()
    t_start = time.time()
    deadline = t_start + args.budget_minutes * 60

    doc = json.loads(GAMES.read_text(encoding="utf-8"))
    games = doc["games"]
    biz = json.loads(BUSINESS.read_text(encoding="utf-8")) if BUSINESS.exists() else {}

    # older runs wrote these fields into games.json; pick them up as a starting point
    # (games.json itself is left alone so this job never competes with readings for it)
    moved = 0
    for g in games:
        gid = str(g["id"])
        if any(k in g for k in ("gp", "grp", "vip", "paid", "enrichedAt", "socials")) and gid not in biz:
            e = biz.setdefault(gid, {})
            for k in ("gp", "grp", "vip", "paid", "enrichedAt", "socials"):
                if k in g:
                    e[k] = g[k]
            moved += 1
    if moved:
        print(f"seeded business.json with fields of {moved} games from games.json", flush=True)

    today = datetime.now(timezone.utc)
    stamp = today.strftime("%Y-%m-%d")

    def stale(g):
        e = biz.get(str(g["id"]), {}).get("enrichedAt")
        if not e:
            return True
        return (today - datetime.strptime(e, "%Y-%m-%d").replace(tzinfo=timezone.utc)).days >= args.max_age

    todo = [g for g in games if stale(g)]
    todo.sort(key=lambda g: (bool(biz.get(str(g["id"]), {}).get("enrichedAt")), -(g.get("playing") or 0)))
    print(f"enriching {len(todo)} of {len(games)} games (budget {args.budget_minutes} min)", flush=True)

    # ---- flags from the batch endpoint (cheap); the same call carries the description,
    # which is where many small games put their Discord invite instead of the social links ----
    flags, desc_socials = {}, {}
    for chunk in batches([str(g["id"]) for g in todo], 50):
        d = get_json("https://games.roblox.com/v1/games?universeIds=" + ",".join(chunk))
        for item in (d or {}).get("data", []):
            flags[str(item["id"])] = {"vip": bool(item.get("createVipServersAllowed")), "paid": item.get("price")}
            found = socials_in_text(item.get("description"))
            if found:
                desc_socials[str(item["id"])] = found
        time.sleep(0.8)
    print(f"  social links found in descriptions: {len(desc_socials)}", flush=True)

    # ---- owner groups: name/created/verified in batches of 100 (cheap); member counts are
    # one request per group and heavily rate-limited, so they are fetched lazily below ----
    gid_of = {str(g["id"]): g["cUrl"].rsplit("/", 1)[1] for g in todo if g.get("cType") == "Group" and g.get("cUrl")}
    groups = {}
    for chunk in batches(sorted(set(gid_of.values())), 100):
        d = get_json("https://groups.roblox.com/v2/groups?groupIds=" + ",".join(chunk))
        for item in (d or {}).get("data", []):
            groups[str(item["id"])] = {"m": None, "c": (item.get("created") or "")[:10] or None,
                                       "v": bool(item.get("hasVerifiedBadge")), "n": item.get("name")}
        time.sleep(0.8)
    print(f"  groups: {len(groups)} basic records", flush=True)
    members_deadline = t_start + args.budget_minutes * 60 * 0.6   # member counts get at most 60 % of the budget
    members_done = set()

    def member_count(grp_id):
        """One v1 request; returns None when rate-limited past the members budget."""
        if grp_id in members_done or time.time() > members_deadline:
            return
        members_done.add(grp_id)
        try:
            d = get_json(f"https://groups.roblox.com/v1/groups/{grp_id}", tries=2)
        except Unauthorized:
            d = None
        if d and d.get("id"):
            groups.setdefault(grp_id, {})["m"] = d.get("memberCount")
            groups[grp_id].setdefault("n", d.get("name"))
            groups[grp_id].setdefault("v", bool(d.get("hasVerifiedBadge")))
            groups[grp_id].setdefault("c", (d.get("created") or "")[:10] or None)

    # ---- per game: passes + social links ----
    cookie = os.environ.get("ROBLOX_COOKIE", "").strip()
    cookie_hdr = {"Cookie": f".ROBLOSECURITY={cookie}"} if cookie else None
    if cookie_hdr:
        try:
            me = get_json("https://users.roblox.com/v1/users/authenticated", tries=2, headers=cookie_hdr)
            print(f"  session ok: user id {me.get('id') if me else '?'}", flush=True)
        except Unauthorized as e:
            print(f"  ROBLOX_COOKIE rejected ({e}); social links skipped this run", flush=True)
            cookie_hdr = None
    else:
        print("  ROBLOX_COOKIE not set; social links skipped", flush=True)

    done, forbidden = 0, 0
    for i, g in enumerate(todo, 1):
        if time.time() > deadline:
            print(f"  budget reached after {done} games; the rest continues next run", flush=True)
            break
        gid = str(g["id"])
        e = biz.setdefault(gid, {})
        d = get_json(f"https://games.roblox.com/v1/games/{gid}/game-passes?limit=100&sortOrder=Asc")
        if d is not None:
            prices = [p.get("price") for p in d.get("data", []) if isinstance(p.get("price"), (int, float)) and p.get("price") > 0]
            e["gp"] = {"n": len(d.get("data", [])), "min": min(prices) if prices else None,
                       "max": max(prices) if prices else None, "sum": sum(prices) if prices else 0}
        time.sleep(0.4)
        if cookie_hdr:
            try:
                sl = get_json(f"https://games.roblox.com/v1/games/{gid}/social-links/list", tries=3, headers=cookie_hdr)
                if sl is not None:
                    links = []
                    for item in sl.get("data", []):
                        k = SOCIAL_TYPES.get(str(item.get("type", "")).lower())
                        if k and item.get("url"):
                            links.append({"k": k, "u": item["url"], "t": item.get("title") or ""})
                    e["socials"] = links or desc_socials.get(gid, [])
            except Unauthorized as ex:
                if ex.code == 403:
                    forbidden += 1
                else:
                    print(f"  session expired mid-run ({ex}); social links stop here", flush=True)
                    cookie_hdr = None
            time.sleep(0.5)
        if not e.get("socials") and desc_socials.get(gid):
            e["socials"] = desc_socials[gid]
        f = flags.get(gid)
        if f:
            e["vip"], e["paid"] = f["vip"], f["paid"]
        grp_id = gid_of.get(gid, "")
        if grp_id:
            member_count(grp_id)
            grp = groups.get(grp_id)
            if grp:
                if grp.get("m") is None and (e.get("grp") or {}).get("m") is not None:
                    grp = dict(grp, m=e["grp"]["m"])   # keep last known count
                e["grp"] = grp
        e["enrichedAt"] = stamp
        done += 1
        if i % 100 == 0:
            print(f"  games {i}/{len(todo)}", flush=True)
            save(biz)

    save(biz)
    print(f"done: {done} games enriched, {forbidden} refused social links, {len(biz)} in business.json, {int((time.time()-t_start)/60)} min")


if __name__ == "__main__":
    main()
