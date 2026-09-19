"""Discover Roblox games that are not tracked yet and add them to data/games.json.

Sources: the four front-page chart sorts plus a keyword sweep of Roblox search.
New games are classified with keyword rules (src = "rules") and any entry in
data/overrides.json wins over the rules. Standard library only.

    python scripts/discover.py --min-players 1000
"""
import argparse
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


def get_json(url, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = e.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else min(30, 5 * 2 ** attempt)
                print(f"  429 rate limited, waiting {wait}s", flush=True)
                time.sleep(wait)
            else:
                time.sleep(min(20, 3 * 2 ** attempt))
        except Exception:
            time.sleep(min(20, 3 * 2 ** attempt))
    return None


def batches(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-players", type=int, default=1000)
    ap.add_argument("--pages", type=int, default=2, help="search pages per keyword")
    ap.add_argument("--apply-only", action="store_true", help="only apply data/overrides.json, no discovery")
    args = ap.parse_args()

    games_doc = json.loads(GAMES.read_text(encoding="utf-8"))
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    overrides = {}
    if OVERRIDES.exists():
        for o in json.loads(OVERRIDES.read_text(encoding="utf-8")):
            overrides[str(o["id"])] = o
    known = {str(g["id"]) for g in games_doc["games"]}

    # hand corrections always win, also for games that are already tracked
    fixed = 0
    for g in games_doc["games"]:
        o = overrides.get(str(g["id"]))
        if o and (g.get("cat") != o["c"] or sorted(g.get("tags", [])) != sorted(o["t"]) or g.get("src") != "review"):
            g["cat"], g["tags"], g["src"] = o["c"], list(o["t"]), "review"
            fixed += 1
    if fixed:
        print(f"applied {fixed} overrides to tracked games", flush=True)
    if args.apply_only:
        if fixed:
            GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        return

    pool = {}
    for s in SORTS:
        d = get_json(f"https://apis.roblox.com/explore-api/v1/get-sort-content?sessionId=radar{int(time.time())}&sortId={s}&device=computer&country=us")
        for g in (d or {}).get("games", []):
            pool.setdefault(str(g["universeId"]), g)
        time.sleep(PAUSE)
    print(f"charts: {len(pool)} games", flush=True)

    for i, kw in enumerate(KEYWORDS, 1):
        token = ""
        for _ in range(args.pages):
            url = ("https://apis.roblox.com/search-api/omni-search?searchQuery=" + urllib.parse.quote(kw)
                   + f"&pageToken={token}&sessionId=radar{int(time.time())}&pageType=all")
            d = get_json(url, tries=3)
            if not d:
                break
            for grp in d.get("searchResults", []):
                if grp.get("contentGroupType") != "Game":
                    continue
                for g in grp.get("contents", []):
                    if g.get("universeId"):
                        pool.setdefault(str(g["universeId"]), g)
            token = d.get("nextPageToken") or ""
            if not token:
                break
            time.sleep(0.4)
        if i % 10 == 0:
            print(f"  keywords {i}/{len(KEYWORDS)} -> pool {len(pool)}", flush=True)
        time.sleep(0.3)

    new_ids = [uid for uid, g in pool.items()
               if uid not in known and (g.get("playerCount") or 0) >= args.min_players]
    print(f"new candidates with >= {args.min_players} players: {len(new_ids)}", flush=True)
    if not new_ids:
        if fixed:
            GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        return

    details, votes, icons, thumbs = {}, {}, {}, {}
    for chunk in batches(new_ids, 50):
        q = ",".join(chunk)
        d = get_json(f"https://games.roblox.com/v1/games?universeIds={q}")
        for item in (d or {}).get("data", []):
            details[str(item["id"])] = item
        time.sleep(PAUSE)
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
    for uid in new_ids:
        d = details.get(uid)
        if not d:
            continue
        p = pool[uid]
        cat, tags = classify(d.get("name"), d.get("description"), d.get("genre_l1") or p.get("genreL1"))
        src = "rules"
        if uid in overrides:
            cat, tags, src = overrides[uid]["c"], list(overrides[uid]["t"]), "review"
        vt = votes.get(uid, {})
        up, down = vt.get("upVotes", 0), vt.get("downVotes", 0)
        creator = d.get("creator") or {}
        ctype = creator.get("type")
        cid = creator.get("id")
        curl = (f"https://www.roblox.com/communities/{cid}" if ctype == "Group"
                else f"https://www.roblox.com/users/{cid}/profile" if cid else None)
        genre = d.get("genre_l1") or p.get("genreL1") or ""
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
            "maturity": p.get("contentMaturity"), "socials": socials(d.get("description")),
            "added": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        })
        history["series"][uid] = [None] * n_times
        added += 1

    GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"added {added} games (total {len(games_doc['games'])})")


if __name__ == "__main__":
    main()
