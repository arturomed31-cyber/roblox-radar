"""Find the small games: rotate through tracked creators' catalogues every day, and add
long-tail keywords. Small sibling games of studios we already track are the richest source
(e.g. Florover: one 6.6M-visit hit and four games under 400k)."""
p = 'scripts/discover.py'
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

rep('    ap.add_argument("--no-groups", action="store_true", help="skip creator catalogues")',
    '''    ap.add_argument("--no-groups", action="store_true", help="skip creator catalogues")
    ap.add_argument("--creator-slice", type=int, default=0,
                    help="read only this many creator catalogues, rotating a different slice each run")''')

rep("""        creators = [] if args.no_groups else creators_of(games_doc)""",
    """        creators = [] if args.no_groups else creators_of(games_doc)
        if args.creator_slice and creators:
            creators = rotate_slice(creators, args.creator_slice)""")

rep("""# ---------------------------------------------------------------- adding games""",
    '''STATE = ROOT / "data" / "discover_state.json"


def rotate_slice(creators, size):
    """Return `size` creators, continuing where the previous run stopped, wrapping around."""
    try:
        start = json.loads(STATE.read_text(encoding="utf-8")).get("creator_cursor", 0)
    except Exception:
        start = 0
    start %= max(1, len(creators))
    picked = (creators + creators)[start:start + size]
    STATE.write_text(json.dumps({"creator_cursor": (start + size) % max(1, len(creators))}), encoding="utf-8")
    print(f"creators: reading {len(picked)} of {len(creators)} (from #{start})", flush=True)
    return picked


# ---------------------------------------------------------------- adding games''')

# long-tail keywords: the phrasing small and brand-new games use
rep('''    "magic", "farm", "restaurant", "hotel", "hangout", "duels", "rng", "mining", "build", "craft",''',
    '''    "magic", "farm", "restaurant", "hotel", "hangout", "duels", "rng", "mining", "build", "craft",
    # long tail: wording typical of small and brand-new games
    "beta", "early access", "alpha", "new game", "update 1", "demo", "remake", "revamp", "test",
    "grow a", "eat the", "collect a", "unbox", "merge a", "carry a", "push a", "throw a", "climb a",
    "escape the", "survive the", "find the", "guess the", "become a", "be a", "catch a", "hide from",
    "obby but", "tower of", "roll a", "spin a", "open a", "sell a", "dig a", "fish a", "race a",''')
open(p, 'w', encoding='utf-8', newline='').write(s)
import ast
ast.parse(s)
print('ok')
