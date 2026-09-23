"""Readings must never rewrite games.json.

A reading and the discovery job both wrote games.json; the commit step's
`git pull --rebase -X theirs` then let the reading's stale copy win and 441
newly discovered games were lost. Now readings own history + trends only, and
trends.json carries the live player count and visits for the table.
"""
p = 'scripts/update.py'
s = open(p, encoding='utf-8').read()

def rep(a, b, src=None):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

# live values into trends.json
rep("""    for gid, s in history["series"].items():
        cur = s[-1] if len(s) == len(times_s) else None
        row = {}""", """    for gid, s in history["series"].items():
        cur = s[-1] if len(s) == len(times_s) else None
        row = {}
        if cur is not None:
            row["p"] = cur                      # players now: the table reads this, not games.json""")
rep("""def write_trends(history, stamp):""", """def write_trends(history, stamp, visits=None):""")
rep("""        peak = max((v for v in s if v is not None), default=None)
        if peak is not None:
            row["pk"] = peak""", """        peak = max((v for v in s if v is not None), default=None)
        if peak is not None:
            row["pk"] = peak
        if visits and visits.get(gid) is not None:
            row["v"] = visits[gid]""")

# light runs: touch history/trends only
rep("""    if light:
        print("light run: players/visits only", flush=True)

    compact_history(history)
    write_trends(history, stamp)
    games_doc["generated"] = stamp
    GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    save_history(history)""",
    """    compact_history(history)
    write_trends(history, stamp, {gid: (d.get("visits") if d else None) for gid, d in details.items()})
    save_history(history)
    if light:
        # games.json belongs to the daily refresh and to discovery; a reading that rewrote it
        # could undo games those jobs had just added
        print("light run: history and trends only, games.json untouched", flush=True)
    else:
        games_doc["generated"] = stamp
        GAMES.write_text(json.dumps(games_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")""")
open(p, 'w', encoding='utf-8', newline='').write(s)

# the light path must still fill g["playing"]/visits in memory for alerts.py; it does, in games_doc only.
import ast
ast.parse(s)

# workflow: readings no longer stage games.json
w = '.github/workflows/refresh.yml'
t = open(w, encoding='utf-8').read()
t = t.replace("git add data/games.json data/h data/trends.json data/alerts_state.json",
              "git add data/h data/trends.json data/alerts_state.json")
open(w, 'w', encoding='utf-8', newline='').write(t)
print('ok')
