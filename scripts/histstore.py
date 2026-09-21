"""Sharded player history: data/h/NN.json, one file per last-two-digits of the game id.

Every shard carries the same `times` array and the series of its games, so the page
can fetch just the shard of the game it needs while the scripts keep working with
one in-memory {"times": [...], "series": {id: [...]}} structure.

    from histstore import load_history, save_history
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HDIR = ROOT / "data" / "h"
LEGACY = ROOT / "data" / "history.json"


def shard_of(gid):
    s = str(gid)[-2:]
    return s.zfill(2) if s.isdigit() else "00"


def load_history():
    if HDIR.exists() and any(HDIR.glob("*.json")):
        times, series = None, {}
        for f in sorted(HDIR.glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            if times is None:
                times = d["times"]
            elif d["times"] != times:
                # a shard written by an interrupted run: align it to the longest times array
                if len(d["times"]) > len(times):
                    times = d["times"]
            series.update(d.get("series", {}))
        n = len(times or [])
        for gid, s in series.items():
            if len(s) < n:
                series[gid] = s + [None] * (n - len(s))
            elif len(s) > n:
                series[gid] = s[:n]
        return {"times": times or [], "series": series}
    if LEGACY.exists():   # first run after the split: read the old single file
        return json.loads(LEGACY.read_text(encoding="utf-8"))
    return {"times": [], "series": {}}


def save_history(history):
    HDIR.mkdir(parents=True, exist_ok=True)
    buckets = {}
    for gid, s in history["series"].items():
        buckets.setdefault(shard_of(gid), {})[gid] = s
    written = set()
    for shard, series in buckets.items():
        (HDIR / f"{shard}.json").write_text(json.dumps({"times": history["times"], "series": series}, separators=(",", ":")), encoding="utf-8")
        written.add(shard)
    # shards that lost all their games keep a valid, empty file so the page never 404s
    for f in HDIR.glob("*.json"):
        if f.stem not in written:
            f.write_text(json.dumps({"times": history["times"], "series": {}}, separators=(",", ":")), encoding="utf-8")
    if LEGACY.exists():
        LEGACY.unlink()
