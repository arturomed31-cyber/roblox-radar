"""Discord alerts for notable moves, run after every reading.

Rules (each with a 24 h cooldown per game so the channel is not spammed):
  spike      +50 % vs the same time yesterday, at least 2,000 players now
  drop       -40 % vs the same time yesterday, at least 5,000 players a day ago
  newcomer   game added today that already holds 5,000+ players
  watchlist  any game in data/watchlist.json moving +/-30 % vs yesterday
  milestone  a game crossing 50K / 100K / 250K / 500K / 1M players for the first time on record

Needs DISCORD_WEBHOOK in the environment; without it the script only prints.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "data" / "games.json"
HISTORY = ROOT / "data" / "history.json"
WATCHLIST = ROOT / "data" / "watchlist.json"
STATE = ROOT / "data" / "alerts_state.json"

COOLDOWN_H = 24
MAX_PER_RUN = 10
MILESTONES = [50_000, 100_000, 250_000, 500_000, 1_000_000, 2_000_000]
SITE = "https://roblox-radar.pages.dev/"
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


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


def fmt(n):
    if n is None:
        return "—"
    if n >= 1e6:
        return f"{n/1e6:.2f}M".replace(".00M", "M")
    if n >= 1e3:
        return f"{n/1e3:.1f}K".replace(".0K", "K")
    return str(n)


def main():
    webhook = os.environ.get("DISCORD_WEBHOOK", "").strip()
    doc = json.loads(GAMES.read_text(encoding="utf-8"))
    hist = json.loads(HISTORY.read_text(encoding="utf-8"))
    watch = set()
    if WATCHLIST.exists():
        try:
            watch = {str(x) for x in json.loads(WATCHLIST.read_text(encoding="utf-8"))}
        except Exception:
            watch = set()
    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            state = {}

    times = hist.get("times", [])
    if len(times) < 2:
        print("not enough readings for alerts")
        return
    times_s = [parse_ts(x) for x in times]
    now = times_s[-1]
    ref = same_hour_reading(times_s, 1)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def cooled(gid, kind):
        last = state.get(f"{gid}:{kind}")
        return not last or now - last >= COOLDOWN_H * 3600

    alerts = []  # (priority, embed, gid, kind)
    for g in doc["games"]:
        gid = str(g["id"])
        s = hist["series"].get(gid) or []
        cur = s[-1] if len(s) == len(times) and s[-1] is not None else g.get("playing")
        if cur is None:
            continue
        prev = s[ref] if ref is not None and ref < len(s) else None
        pct = (cur - prev) / prev * 100 if prev else None
        link = f"https://www.roblox.com/games/{g.get('place')}"
        base = {"title": g["name"][:120], "url": link,
                "thumbnail": {"url": g.get("icon") or ""},
                "footer": {"text": f"{g.get('creator') or ''} · {SITE}"}}

        def add(kind, color, headline, extra, prio):
            if not cooled(gid, kind):
                return
            e = dict(base)
            e["color"] = color
            e["description"] = headline
            e["fields"] = [{"name": "Players now", "value": fmt(cur), "inline": True}] + extra
            alerts.append((prio, e, gid, kind))

        if pct is not None and pct >= 50 and cur >= 2000:
            add("spike", 0x5fd77c, f"📈 **+{pct:.0f}% in 24 h** ({fmt(prev)} → {fmt(cur)})",
                [{"name": "Category", "value": g.get("cat", "—"), "inline": True},
                 {"name": "Tags", "value": ", ".join(g.get("tags") or []) or "—", "inline": False}], pct)
        if pct is not None and pct <= -40 and prev >= 5000:
            add("drop", 0xef6461, f"📉 **{pct:.0f}% in 24 h** ({fmt(prev)} → {fmt(cur)})",
                [{"name": "Category", "value": g.get("cat", "—"), "inline": True}], -pct)
        if g.get("added") == today and cur >= 5000:
            add("newcomer", 0x4fd1c5, f"🆕 **New on the radar** with {fmt(cur)} players",
                [{"name": "Category", "value": g.get("cat", "—"), "inline": True},
                 {"name": "Owner", "value": g.get("cType") or "—", "inline": True}], cur / 100)
        if gid in watch and pct is not None and abs(pct) >= 30:
            add("watch", 0xf0b429, f"⭐ **Watchlist:** {pct:+.0f}% in 24 h ({fmt(prev)} → {fmt(cur)})",
                [{"name": "Category", "value": g.get("cat", "—"), "inline": True}], abs(pct) + 1000)
        past = [v for v in s[:-1] if v is not None]
        peak_before = max(past) if past else 0
        for m in MILESTONES:
            if cur >= m > peak_before:
                add(f"ms{m}", 0xa78bfa, f"🏁 **Crossed {fmt(m)} players** for the first time on record",
                    [{"name": "Previous peak", "value": fmt(peak_before), "inline": True}], m / 1000)
                break

    alerts.sort(key=lambda a: -a[0])
    alerts = alerts[:MAX_PER_RUN]
    print(f"{len(alerts)} alerts")
    for _, e, gid, kind in alerts:
        print(f"  [{kind}] {e['title']} — {e['description']}")

    if not alerts:
        return
    if not webhook:
        print("DISCORD_WEBHOOK not set; nothing sent")
        return

    payload = {"username": "Roblox Radar", "embeds": [e for _, e, _, _ in alerts]}
    req = urllib.request.Request(webhook, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json", "User-Agent": "roblox-radar"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5)
                continue
            print(f"discord error {e.code}: {e.read()[:200]}")
            sys.exit(0)
    else:
        print("discord: gave up after retries")
        return

    for _, _, gid, kind in alerts:
        state[f"{gid}:{kind}"] = now
    # prune old state
    state = {k: v for k, v in state.items() if now - v < 7 * 86400 or k.split(":")[1].startswith("ms")}
    STATE.write_text(json.dumps(state, separators=(",", ":")), encoding="utf-8")
    print("sent")


if __name__ == "__main__":
    main()
