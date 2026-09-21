"""Limiteds for Roblox Radar.

Item list, RAP, value, demand/trend and the projected/hyped/rare flags come from the
public Rolimons API (https://www.rolimons.com — data credited on the page); the best
resale price, quantity and favorites from Roblox's catalog API; icons from Roblox
thumbnails. Writes data/limiteds.json and appends a reading (RAP + best price) to
data/limiteds_history.json at most every --every hours (default 6). Standard library.

    python scripts/limiteds.py [--every 6] [--force]
"""
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "limiteds.json"
HIST = ROOT / "data" / "limiteds_history.json"
UA = "roblox-radar/1.0 (+https://github.com/arturomed31-cyber/roblox-radar)"
RAW_DAYS = 30


def request(url, data=None, headers=None, tries=4):
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs, method="POST" if data else "GET")
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, dict(r.headers), r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code == 403 and "x-csrf-token" in {k.lower() for k in e.headers.keys()}:
                return e.code, dict(e.headers), body
            wait = min(60, 5 * 2 ** attempt)
            print(f"  HTTP {e.code}, retry in {wait}s", flush=True)
            time.sleep(wait)
        except Exception as e:
            wait = min(60, 5 * 2 ** attempt)
            print(f"  {e}, retry in {wait}s", flush=True)
            time.sleep(wait)
    return None, {}, ""


def batches(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def csrf_token():
    _, h, _ = request("https://catalog.roblox.com/v1/catalog/items/details", data=b'{"items":[]}',
                      headers={"Content-Type": "application/json"}, tries=1)
    for k, v in h.items():
        if k.lower() == "x-csrf-token":
            return v
    return None


def main():
    every = 6
    force = "--force" in sys.argv
    if "--every" in sys.argv:
        every = float(sys.argv[sys.argv.index("--every") + 1])

    hist = json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else {"times": [], "rap": {}, "price": {}}
    prev = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"items": []}
    prev_by_id = {str(i["id"]): i for i in prev.get("items", [])}
    now = datetime.now(timezone.utc)
    if hist["times"] and not force:
        last = datetime.fromisoformat(hist["times"][-1].replace("Z", "+00:00"))
        if (now - last).total_seconds() < every * 3600 - 600:
            print(f"last limiteds reading {hist['times'][-1]}; next one after {every} h, nothing to do")
            return

    # ---- Rolimons: the item universe with RAP / value / demand / trend / flags ----
    st, _, body = request("https://api.rolimons.com/items/v1/itemdetails")
    if st != 200:
        print("rolimons unavailable; leaving files untouched")
        sys.exit(1)
    rl = json.loads(body)["items"]
    print(f"{len(rl)} limiteds from Rolimons", flush=True)

    items = {}
    for aid, row in rl.items():
        name, acr, rap, value, _default, demand, trend, projected, hyped, rare = row[:10]
        items[str(aid)] = {"id": int(aid), "name": name, "acr": acr or None, "rap": rap if rap and rap > 0 else None,
                           "value": value if value and value > 0 else None,
                           "demand": demand if demand is not None and demand >= 0 else None,
                           "trend": trend if trend is not None and trend >= 0 else None,
                           "proj": projected == 1, "hyped": hyped == 1, "rare": rare == 1}

    # ---- Roblox catalog: best resale price, quantity, favorites, created date ----
    state = {"token": None}

    def fetch_chunk(chunk):
        payload = json.dumps({"items": [{"itemType": "Asset", "id": int(i)} for i in chunk]}).encode()
        st, h, body = request("https://catalog.roblox.com/v1/catalog/items/details", data=payload,
                              headers={"Content-Type": "application/json", "X-CSRF-TOKEN": state["token"] or ""})
        if st == 403:
            state["token"] = next((v for k, v in h.items() if k.lower() == "x-csrf-token"), state["token"])
            st, h, body = request("https://catalog.roblox.com/v1/catalog/items/details", data=payload,
                                  headers={"Content-Type": "application/json", "X-CSRF-TOKEN": state["token"] or ""})
        time.sleep(2.5)
        if st != 200:
            print(f"  catalog batch failed ({st})", flush=True)
            return False
        for d in json.loads(body).get("data", []):
            it = items.get(str(d["id"]))
            if not it:
                continue
            it["price"] = d.get("lowestResalePrice") or d.get("lowestPrice") or None
            it["qty"] = d.get("totalQuantity")
            it["favs"] = d.get("favoriteCount")
            it["created"] = (d.get("itemCreatedUtc") or "")[:10] or None
            it["type"] = (d.get("taxonomy") or [{}])[0].get("taxonomyName")
            it["creator"] = d.get("creatorName")
        return True

    ids = list(items.keys())
    state["token"] = csrf_token()
    pending = list(batches(ids, 120))
    for attempt in range(3):          # failed chunks (rate limits) get two more passes
        failed = []
        for chunk in pending:
            if not fetch_chunk(chunk):
                failed.append(chunk)
        pending = failed
        if not pending:
            break
        time.sleep(30)

    got = sum(1 for i in items.values() if "qty" in i)
    print(f"  catalog details for {got}", flush=True)

    # ---- icons: only for items we have not seen before (or that lost their icon) ----
    need = [i for i in ids if not (prev_by_id.get(i) or {}).get("icon")]
    for i in ids:
        if prev_by_id.get(i, {}).get("icon"):
            items[i]["icon"] = prev_by_id[i]["icon"]
    for chunk in batches(need, 100):
        st, _, body = request(f"https://thumbnails.roblox.com/v1/assets?assetIds={','.join(chunk)}&size=150x150&format=Png")
        if st == 200:
            for d in json.loads(body).get("data", []):
                if d.get("imageUrl") and str(d["targetId"]) in items:
                    items[str(d["targetId"])]["icon"] = d["imageUrl"]
        time.sleep(1.0)
    if need:
        print(f"  icons fetched for {len(need)} new items", flush=True)

    # ---- history: one reading of RAP and best price per item ----
    stamp = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    hist["times"].append(stamp)
    n = len(hist["times"])
    for key in ("rap", "price"):
        series = hist[key]
        for i, it in items.items():
            s = series.setdefault(i, [])
            while len(s) < n - 1:
                s.append(None)
            s.append(it.get(key))
    compact(hist)

    OUT.write_text(json.dumps({"generated": stamp, "source": "Rolimons + Roblox catalog",
                               "items": sorted(items.values(), key=lambda x: -(x.get("rap") or 0))},
                              ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    HIST.write_text(json.dumps(hist, separators=(",", ":")), encoding="utf-8")
    print(f"done: {len(items)} limiteds, {n} readings in history")


def compact(hist):
    """Readings older than RAW_DAYS collapse to one per UTC day (the day's last value)."""
    times = hist["times"]
    cutoff = datetime.now(timezone.utc).timestamp() - RAW_DAYS * 86400
    parsed = [datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() for t in times]
    by_day = {}
    for i, ts in enumerate(parsed):
        if ts < cutoff:
            by_day.setdefault(times[i][:10], []).append(i)
    collapsible = {d: idx for d, idx in by_day.items() if not (len(idx) == 1 and times[idx[0]].endswith("T12:00:00Z"))}
    if not collapsible:
        return
    drop = {i for idx in collapsible.values() for i in idx}
    entries = [(f"{d}T12:00:00Z", idx[-1]) for d, idx in sorted(collapsible.items())]   # keep the day's last reading
    entries += [(times[i], i) for i in range(len(times)) if i not in drop]
    entries.sort()
    hist["times"] = [e[0] for e in entries]
    for key in ("rap", "price"):
        for aid, s in hist[key].items():
            hist[key][aid] = [(s[i] if i < len(s) else None) for _, i in entries]
    print(f"  history compacted to {len(hist['times'])} readings", flush=True)


if __name__ == "__main__":
    main()
