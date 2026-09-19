"""Discover Roblox games that are not tracked yet and add them to data/games.json.

Sources
  charts   the four front-page chart sorts
  search   a keyword sweep of Roblox search
  groups   the public catalogue of every creator group/user already tracked

Modes
  default            sweep everything in one process, then add the new games
  --shard i/N --out  sweep only slice i of the keywords and groups (shard 0 also
                     does the charts) and write the candidates to a JSON file —
                     run N shards in parallel on separate runners
  --merge DIR        read every candidates-*.json in DIR and add the new games
  --apply-only       only apply data/overrides.json

New games are classified with keyword rules (src = "rules"); any entry in
data/overrides.json wins over the rules. Standard library only.
"""
import argparse
import glob
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "data" / "games.json"
HISTORY = ROOT / "data" / "history.json"
OVERRIDES = ROOT / "data" / "overrides.json"

UA = "roblox-radar/1.0 (+https://github.com)"
PAUSE = 0.9

SORTS = ["top-playing-now", "top-trending", "up-and-coming", "fun-with-friends"]
KEYWORDS = [
    "simulator", "tycoon", "obby", "tower", "rpg", "anime", "horror", "roleplay", "shooter", "fps",
    "brainrot", "steal", "minecraft", "murder mystery", "racing", "soccer", "football", "basketball", "fishing", "pet",
    "survival", "clicker", "battlegrounds", "escape", "prison", "city", "school", "zombie", "parkour", "sword",
    "magic", "farm", "restaurant", "hotel", "hangout", "duels", "rng", "mining", "build", "craft",
    "backrooms", "granny", "squid game", "bed wars", "one piece", "dragon ball", "naruto", "car", "train", "plane",
    "pizza", "baby", "family", "dress up", "story", "scary", "gun", "war", "army", "ninja",
    "dungeon", "idle", "grow", "kick", "slap", "lift", "race", "pvp", "trading", "hide and seek",
    "tower defense", "battle royale", "roblox horror", "escape room", "puzzle", "adventure", "open world",
    "military", "tank", "boat", "ship", "pirate", "space", "alien", "dinosaur", "dragon", "monster",
    "cat", "dog", "animal", "bird", "fish", "shark", "egg", "hatch", "pull", "merge", "roll",
    "lucky block", "rebirth", "evolution", "escape obby", "difficulty chart", "troll", "meme", "funny",
    "girls", "makeup", "fashion", "hair salon", "house", "mansion", "life", "job", "work", "bank",
    "police", "cops", "thief", "mafia", "gang", "hood", "crime", "heist", "ninja warrior", "samurai",
    "wizard", "elemental", "superhero", "villain", "godzilla", "kaiju", "titan", "demon", "vampire",
    "school escape", "prison escape", "camping", "forest", "island", "desert", "arctic", "winter",
    "summer", "halloween", "christmas", "hospital", "doctor", "vet", "daycare", "cafe", "bakery",
    "sushi", "burger", "ice cream", "candy", "supermarket", "store", "shop", "mall", "arcade",
    "casino", "card", "deck", "chess", "tag", "freeze tag", "dodgeball", "volleyball", "tennis",
    "golf", "bowling", "boxing", "wrestling", "karate", "gym", "muscle", "strength", "speed",
    "flying", "jetpack", "glider", "elevator", "cart ride", "slide", "water park", "roller coaster",
    "theme park", "zoo", "aquarium", "museum", "library", "airport", "bus", "taxi", "truck",
    "drift", "motorcycle", "bike", "skate", "surf", "ski", "roblox rp", "anime fighting", "anime rng",
    "brainrot tycoon", "steal a", "jump to steal", "for brainrots", "per click", "keyboard escape",
]

GENRE_MAP = {
    "Simulation": "sim", "Roleplay & Avatar Sim": "rp", "Shooter": "shooter", "Action": "fight",
    "Obby & Platformer": "obby", "Sports & Racing": "sports", "RPG": "rpg", "Survival": "horror",
    "Party & Casual": "party", "Strategy": "strategy", "Adventure": "rpg", "Puzzle": "party",
    "Shopping": "other", "Entertainment": "other", "Education": "other", "Utility & Other": "other",
    "Social": "rp", "Building": "sandbox",
}
ANIME_WORDS = ["anime", "naruto", "one piece", "dragon ball", "jujutsu", "demon slayer", "bleach", "attack on titan",
               "blue lock", "solo leveling", "goku", "manga", "shinobi", "hunter x", "my hero", "gojo", "luffy",
               "one punch", "chainsaw man", "umamusume", "devil fruit"]
LICENSED_WORDS = ["naruto", "one piece", "dragon ball", "jujutsu kaisen", "demon slayer", "bleach", "attack on titan",
                  "blue lock", "solo leveling", "my hero academia", "one punch", "sonic", "mario", "pokemon", "pokémon",
                  "squid game", "spongebob", "nfl", "fifa", "nba", "five nights", "fnaf", "undertale", "deltarune",
                  "death note", "walking dead", "scp", "hello kitty", "sanrio", "fortnite", "among us", "kaiju no",
                  "chainsaw man", "doraemon", "hunter x hunter", "stranger things", "barbie", "disney", "marvel",
                  "batman", "spider-man", "star wars", "harry potter", "transformers", "hot wheels", "umamusume",
                  "skibidi", "mrbeast", "simpsons", "hello neighbor", "granny", "gorilla tag", "tesla"]


# ---------------------------------------------------------------- http
def get_json(url, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ra = e.headers.get("Retry-After")
                wait = int(ra) if ra and ra.isdigit() else min(30, 5 * 2 ** attempt)
                print(f"  429 rate limited, waiting {wait}s", flush=True)
                time.sleep(wait)
            elif e.code in (400, 404):
                return None
            else:
                time.sleep(min(20, 3 * 2 ** attempt))
        except Exception:
            time.sleep(min(20, 3 * 2 ** attempt))
    return None


def batches(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


# ---------------------------------------------------------------- sources
def sweep_charts(pool):
    for s in SORTS:
        d = get_json(f"https://apis.roblox.com/explore-api/v1/get-sort-content?sessionId=radar{int(time.time())}&sortId={s}&device=computer&country=us")
        for g in (d or {}).get("games", []):
            pool.setdefault(str(g["universeId"]), {"p": g.get("playerCount"), "m": g.get("contentMaturity"), "g": g.get("genreL1"), "src": "chart"})
        time.sleep(PAUSE)
    print(f"charts: pool {len(pool)}", flush=True)


def sweep_keywords(pool, keywords, pages):
    for i, kw in enumerate(keywords, 1):
        token, before = "", len(pool)
        for _ in range(pages):
            url = ("https://apis.roblox.com/search-api/omni-search?searchQuery=" + urllib.parse.quote(kw)
                   + f"&pageToken={token}&sessionId=radar{int(time.time())}&pageType=all")
            d = get_json(url, tries=3)
            if not d:
                break
            added = 0
            for grp in d.get("searchResults", []):
                if grp.get("contentGroupType") != "Game":
                    continue
                for g in grp.get("contents", []):
                    uid = str(g.get("universeId") or "")
                    if uid and uid not in pool:
                        pool[uid] = {"p": g.get("playerCount"), "m": g.get("contentMaturity"), "g": None, "src": "search"}
                        added += 1
            token = d.get("nextPageToken") or ""
            if not token or added == 0:      # adaptive: stop paging keywords that add nothing
                break
            time.sleep(0.4)
        if i % 20 == 0:
            print(f"  keywords {i}/{len(keywords)} -> pool {len(pool)}", flush=True)
        time.sleep(0.3)


def sweep_groups(pool, creators):
    """creators: list of (type, id). Reads each creator's public catalogue."""
    for i, (ctype, cid) in enumerate(creators, 1):
        base = (f"https://games.roblox.com/v2/groups/{cid}/games?accessFilter=2&limit=100&sortOrder=Asc" if ctype == "Group"
                else f"https://games.roblox.com/v2/users/{cid}/games?accessFilter=2&limit=50&sortOrder=Asc")
        cursor, guard = "", 0
        while guard < 5:
            d = get_json(base + (f"&cursor={cursor}" if cursor else ""), tries=3)
            if not d:
                break
            for g in d.get("data", []):
                uid = str(g.get("id") or "")
                if uid and uid not in pool:
                    pool[uid] = {"p": None, "m": None, "g": None, "src": "creator"}
            cursor = d.get("nextPageCursor") or ""
            guard += 1
            if not cursor:
                break
            time.sleep(0.4)
        if i % 100 == 0:
            print(f"  creators {i}/{len(creators)} -> pool {len(pool)}", flush=True)
        time.sleep(0.5)


# ---------------------------------------------------------------- classification
def classify(name, desc, genre_l1):
    n = (name or "").lower()
    d = (desc or "").lower()
    t = f"{n} {d}"
    cat = GENRE_MAP.get(genre_l1, "other")

    if re.search(r"\btycoon\b|\bsimulator\b|\bclicker\b|\bidle\b|\+\s?\d", n): cat = "sim"
    if re.search(r"\bobby\b|\bparkour\b|difficulty chart|tower of |tower climb", n): cat = "obby"
    if re.search(r"tower defense|place units to defend|defend against waves", t): cat = "strategy"
    if re.search(r"\brp\b|roleplay|role play", n): cat = "rp"
    if re.search(r"battlegrounds|\bduels\b|fighting game", n): cat = "fight"
    if re.search(r"\bfps\b|\bshooter\b|sniper|strike\b", n): cat = "shooter"
    if re.search(r"horror game|scary|nextbot|backrooms|survive the night|jumpscare", t): cat = "horror"
    if genre_l1 == "Survival" and re.search(r"steal|grow|collect|tycoon", n): cat = "sim"
    if cat == "fight" and re.search(r"hood|open world|open-world|rob banks|criminal|gang|police|streets", t): cat = "action"
    if re.search(r"voxel|block[- ]building|infinite block", t) and cat in ("sim", "other"): cat = "sandbox"

    tags = set()
    if re.search(r"brainrot|tung tung|tralalero|bombardiro|sahur|crocodilo|skibidi", t): tags.add("brainrot")
    if re.search(r"\bsteal\b", n) or (re.search(r"steal (a|an|the)? ?\w* ?(from|back)", d) and re.search(r"base|plot|pen|island|farm", d)):
        tags.add("steal-pattern")
    if re.search(r"\+\s?1\b", n) or re.search(r"every step = \+1|click to gain \+1|\+1 (speed|damage|strength|power) per", d):
        tags.add("plus1-pattern")
    if re.search(r"\bduels?\b", n): tags.add("duels-pattern")
    if re.search(r"\btower\b", n) and "tower defense" not in n: tags.add("tower")
    if "tower defense" in t or re.search(r"\btd\b", n): tags.add("tower-defense")
    if re.search(r"murder mystery|murderers? vs|mm2|traitor vs sheriff", n) or (("murderer" in d or "murder" in n) and re.search(r"sheriff|innocent", d)):
        tags.add("mm2-clone")
    if re.search(r"bed ?wars|sky ?wars|block ?craft|mine ?craft|skyblock|one block|bridge wars", n) or re.search(r"bed wars|mine blocks|craft and build blocks|voxel world", d):
        tags.add("minecraft-clone")
    if re.search(r"\brng\b|gacha|roll for|hatch eggs|summon units|luck multiplier|spin to|open packs|unbox", t):
        tags.add("rng-gacha")
    if any(w in t for w in ANIME_WORDS): tags.add("anime")
    if any(w in t for w in LICENSED_WORDS): tags.add("licensed-ip")
    if re.search(r"inspired by|fan game|fangame|based on the (anime|series|game|show)|tribute to", d): tags.add("copycat")
    return cat, sorted(tags)


SOCIAL_PATTERNS = [
    ("discord", r"(?i)(discord\.gg/[A-Za-z0-9\-]+|discord\.com/invite/[A-Za-z0-9\-]+)"),
    ("youtube", r"(?i)(youtube\.com/[A-Za-z0-9_\-/@\.]+|youtu\.be/[A-Za-z0-9_\-]+)"),
    ("x", r"(?i)((?:twitter|x)\.com/[A-Za-z0-9_]+)"),
    ("tiktok", r"(?i)(tiktok\.com/@?[A-Za-z0-9_\.]+)"),
    ("group", r"(?i)(roblox\.com/(?:groups|communities)/\d+)"),
]


def socials(desc):
    out = []
    for k, pat in SOCIAL_PATTERNS:
        m = re.search(pat, desc or "")
        if m:
            u = m.group(1)
            if not u.startswith("http"):
                u = "https://" + u
            out.append({"k": k, "u": u})
    return out


# ---------------------------------------------------------------- adding games
def add_candidates(games_doc, history, overrides, pool, min_players):
    known = {str(g["id"]) for g in games_doc["games"]}
    # candidates with a known player count below the bar are dropped before any request
    cand = [uid for uid, p in pool.items() if uid not in known and (p.get("p") is None or p["p"] >= min_players)]
    print(f"candidates to check: {len(cand)} (of {len(pool)} found, {len(known)} already tracked)", flush=True)
    if not cand:
        return 0

    details, votes, icons, thumbs = {}, {}, {}, {}
    for chunk in batches(cand, 50):
        q = ",".join(chunk)
        d = get_json(f"https://games.roblox.com/v1/games?universeIds={q}")
        for item in (d or {}).get("data", []):
            if (item.get("playing") or 0) >= min_players:
                details[str(item["id"])] = item
        time.sleep(PAUSE)
    new_ids = list(details.keys())
    print(f"new games with >= {min_players} players: {len(new_ids)}", flush=True)
    if not new_ids:
        return 0

    for chunk in batches(new_ids, 50):
        q = ",".join(chunk)
        v = get_json(f"https://games.roblox.com/v1/games/votes?universeIds={q}")
        for item in (v or {}).get("data", []):
            votes[str(item["id"])] = item
        time.sleep(PAUSE)
        ic = get_json(f"https://thumbnails.roblox.com/v1/games/icons?universeIds={q}&size=256x256&format=Png&isCircular=false")
        for item in (ic or {}).get("data", []):
            if item.get("imageUrl"):
                icons[str(item["targetId"])] = item["imageUrl"]
        time.sleep(PAUSE)
        th = get_json(f"https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds={q}&size=768x432&format=Png&countPerUniverse=1&defaults=true")
        for item in (th or {}).get("data", []):
            tl = item.get("thumbnails") or []
            if tl and tl[0].get("imageUrl"):
                thumbs[str(item["universeId"])] = tl[0]["imageUrl"]
        time.sleep(PAUSE)

    added = 0
    n_times = len(history["times"])
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for uid in new_ids:
        d = details[uid]
        p = pool.get(uid, {})
        cat, tags = classify(d.get("name"), d.get("description"), d.get("genre_l1") or p.get("g"))
        src = "rules"
        if uid in overrides:
            cat, tags, src = overrides[uid]["c"], list(overrides[uid]["t"]), "review"
        vt = votes.get(uid, {})
        up, down = vt.get("upVotes", 0), vt.get("downVotes", 0)
        creator = d.get("creator") or {}
        ctype, cid = creator.get("type"), creator.get("id")
        curl = (f"https://www.roblox.com/communities/{cid}" if ctype == "Group"
                else f"https://www.roblox.com/users/{cid}/profile" if cid else None)
        genre = d.get("genre_l1") or p.get("g") or ""
        if d.get("genre_l2"):
            genre += " / " + d["genre_l2"]
        games_doc["games"].append({
            "id": d["id"], "place": d.get("rootPlaceId"), "name": d.get("name"),
            "icon": icons.get(uid), "thumb": thumbs.get(uid),
            "cat": cat, "tags": tags, "src": src,
            "playing": d.get("playing"), "visits": d.get("visits"), "favs": d.get("favoritedCount"),
            "like": round(100 * up / (up + down)) if up + down else None, "votes": up + down,
            "created": d.get("created"), "updated": d.get("updated"), "maxP": d.get("maxPlayers"),
            "genre": genre, "creator": creator.get("name"), "cType": ctype, "cUrl": curl,
            "verified": bool(creator.get("hasVerifiedBadge")),
            "maturity": p.get("m"), "socials": socials(d.get("description")),
            "added": stamp, "found": p.get("src"),
        })
        history["series"][uid] = [None] * n_times
        added += 1
    return added


def apply_overrides(games_doc, overrides):
    fixed = 0
    for g in games_doc["games"]:
        o = overrides.get(str(g["id"]))
        if o and (g.get("cat") != o["c"] or sorted(g.get("tags", [])) != sorted(o["t"]) or g.get("src") != "review"):
            g["cat"], g["tags"], g["src"] = o["c"], list(o["t"]), "review"
            fixed += 1
    if fixed:
        print(f"applied {fixed} overrides to tracked games", flush=True)
    return fixed


def creators_of(games_doc):
    seen, out = set(), []
    for g in games_doc["games"]:
        cid = (g.get("cUrl") or "").rsplit("/", 1)[-1]
        if g.get("cType") == "User":
            cid = (g.get("cUrl") or "").split("/users/")[-1].split("/")[0]
        if g.get("cType") in ("Group", "User") and cid.isdigit() and (g["cType"], cid) not in seen:
            seen.add((g["cType"], cid))
            out.append((g["cType"], cid))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-players", type=int, default=1000)
    ap.add_argument("--pages", type=int, default=2, help="max search pages per keyword")
    ap.add_argument("--apply-only", action="store_true")
    ap.add_argument("--shard", help="i/N: sweep only slice i of the sources and write candidates")
    ap.add_argument("--out", help="candidates file for --shard")
    ap.add_argument("--merge", help="directory with candidates-*.json from shards")
    ap.add_argument("--no-groups", action="store_true", help="skip creator catalogues")
    args = ap.parse_args()

    games_doc = json.loads(GAMES.read_text(encoding="utf-8"))
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    overrides = {}
    if OVERRIDES.exists():
        for o in json.loads(OVERRIDES.read_text(encoding="utf-8")):
            overrides[str(o["id"])] = o

    fixed = apply_overrides(games_doc, overrides)
    if args.apply_only:
        if fixed:
            GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        return

    pool = {}
    if args.merge:
        for f in sorted(glob.glob(str(Path(args.merge) / "**" / "candidates-*.json"), recursive=True)):
            part = json.loads(Path(f).read_text(encoding="utf-8"))
            for uid, p in part.items():
                pool.setdefault(uid, p)
            print(f"  {Path(f).name}: {len(part)} candidates", flush=True)
        print(f"merged pool: {len(pool)}", flush=True)
    else:
        creators = [] if args.no_groups else creators_of(games_doc)
        if args.shard:
            i, n = (int(x) for x in args.shard.split("/"))
            kws = KEYWORDS[i::n]
            crs = creators[i::n]
            if i == 0:
                sweep_charts(pool)
            print(f"shard {i}/{n}: {len(kws)} keywords, {len(crs)} creators", flush=True)
            sweep_keywords(pool, kws, args.pages)
            sweep_groups(pool, crs)
            out = Path(args.out or f"candidates-{i}.json")
            out.write_text(json.dumps(pool, separators=(",", ":")), encoding="utf-8")
            print(f"wrote {out} with {len(pool)} candidates")
            return
        sweep_charts(pool)
        sweep_keywords(pool, KEYWORDS, args.pages)
        sweep_groups(pool, creators)

    added = add_candidates(games_doc, history, overrides, pool, args.min_players)
    if added or fixed:
        GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        HISTORY.write_text(json.dumps(history, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"added {added} games (total {len(games_doc['games'])})")


if __name__ == "__main__":
    main()
