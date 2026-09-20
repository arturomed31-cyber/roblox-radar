"""'Not to buy' list: six new tags, a NOT TO BUY badge, a filter, a score penalty, and classifier rules."""
p = 'index.html'
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

# --- tag classes + signals
rep("""'flagship':'good','anime':'info','meme':'warn'};""",
    """'flagship':'good','anime':'info','meme':'warn','modded':'risk','hood-rp':'risk','donation':'risk','incremental':'risk','hangout':'risk','troll-tower':'risk'};
// the buyer's "not to buy" list: any of these tags, or the roleplay category
const NOBUY_TAGS = ['modded','hood-rp','minecraft-clone','troll-tower','brainrot','donation','incremental','hangout','mm2-clone','mm2-original'];
const isNoBuy = g => g.cat === 'rp' || g.tags.some(x => NOBUY_TAGS.includes(x));
const NOBUY_I18N = {
  en:{badge:'NOT TO BUY', sel:{'':'Not-to-buy: show all', hide:'Hide not-to-buy', only:'Only not-to-buy'}, sc:'On the not-to-buy list', sig:'Not to buy',
      why:'On the not-to-buy list: modded, roleplay, Minecraft copies, troll towers, hood RP, brainrot, donation, incremental, hangout and MM2 games.'},
  es:{badge:'NO COMPRAR', sel:{'':'No comprar: mostrar todos', hide:'Ocultar "no comprar"', only:'Solo "no comprar"'}, sc:'En la lista de no comprar', sig:'No comprar',
      why:'En la lista de no comprar: modded, roleplay, copias de Minecraft, troll towers, hood RP, brainrot, donaciones, incrementales, hangout y juegos MM2.'},
  pt:{badge:'NÃO COMPRAR', sel:{'':'Não comprar: mostrar todos', hide:'Ocultar "não comprar"', only:'Só "não comprar"'}, sc:'Na lista de não comprar', sig:'Não comprar',
      why:'Na lista de não comprar: modded, roleplay, cópias de Minecraft, troll towers, hood RP, brainrot, doações, incrementais, hangout e jogos MM2.'},
  fr:{badge:'NE PAS ACHETER', sel:{'':'À éviter : tout afficher', hide:'Masquer « à éviter »', only:'Seulement « à éviter »'}, sc:'Sur la liste à éviter', sig:'À éviter',
      why:'Sur la liste à éviter : modded, roleplay, copies de Minecraft, troll towers, hood RP, brainrot, dons, incrémentaux, hangout et jeux MM2.'},
  de:{badge:'NICHT KAUFEN', sel:{'':'Nicht kaufen: alle zeigen', hide:'„Nicht kaufen“ ausblenden', only:'Nur „Nicht kaufen“'}, sc:'Auf der Nicht-kaufen-Liste', sig:'Nicht kaufen',
      why:'Auf der Nicht-kaufen-Liste: Modded, Roleplay, Minecraft-Kopien, Troll Towers, Hood-RP, Brainrot, Spenden, Incremental, Hangout und MM2-Spiele.'},
  it:{badge:'NON COMPRARE', sel:{'':'Non comprare: mostra tutti', hide:'Nascondi "non comprare"', only:'Solo "non comprare"'}, sc:'Nella lista da non comprare', sig:'Non comprare',
      why:'Nella lista da non comprare: modded, roleplay, copie di Minecraft, troll tower, hood RP, brainrot, donazioni, incrementali, hangout e giochi MM2.'},
  ru:{badge:'НЕ ПОКУПАТЬ', sel:{'':'Не покупать: показать все', hide:'Скрыть «не покупать»', only:'Только «не покупать»'}, sc:'В списке «не покупать»', sig:'Не покупать',
      why:'В списке «не покупать»: modded, ролевые, копии Minecraft, troll tower, hood RP, brainrot, донаты, incremental, hangout и игры MM2.'},
  ja:{badge:'購入非推奨', sel:{'':'購入非推奨：すべて表示', hide:'購入非推奨を隠す', only:'購入非推奨のみ'}, sc:'購入非推奨リスト', sig:'購入非推奨',
      why:'購入非推奨リスト：modded、ロールプレイ、Minecraftコピー、troll tower、hood RP、brainrot、寄付、インクリメンタル、hangout、MM2系。'}
};
const tn = k => (NOBUY_I18N[settings.lang] || NOBUY_I18N.en)[k];
const EXTRA_TAGS = {
  en:{modded:'Modded', 'hood-rp':'Hood roleplay', donation:'Donation game', incremental:'Incremental / idle', hangout:'Hangout', 'troll-tower':'Troll tower'},
  es:{modded:'Modded', 'hood-rp':'Hood roleplay', donation:'Juego de donaciones', incremental:'Incremental / idle', hangout:'Hangout', 'troll-tower':'Troll tower'},
  pt:{modded:'Modded', 'hood-rp':'Hood roleplay', donation:'Jogo de doações', incremental:'Incremental / idle', hangout:'Hangout', 'troll-tower':'Troll tower'},
  fr:{modded:'Modded', 'hood-rp':'Hood roleplay', donation:'Jeu de dons', incremental:'Incrémental / idle', hangout:'Hangout', 'troll-tower':'Troll tower'},
  de:{modded:'Modded', 'hood-rp':'Hood-Roleplay', donation:'Spendenspiel', incremental:'Incremental / Idle', hangout:'Hangout', 'troll-tower':'Troll Tower'},
  it:{modded:'Modded', 'hood-rp':'Hood roleplay', donation:'Gioco di donazioni', incremental:'Incrementale / idle', hangout:'Hangout', 'troll-tower':'Troll tower'},
  ru:{modded:'Modded', 'hood-rp':'Hood-ролевая', donation:'Донат-игра', incremental:'Incremental / idle', hangout:'Hangout', 'troll-tower':'Troll tower'},
  ja:{modded:'Modded', 'hood-rp':'Hood ロールプレイ', donation:'寄付ゲーム', incremental:'インクリメンタル / 放置', hangout:'たまり場', 'troll-tower':'トロールタワー'}
};
Object.keys(EXTRA_TAGS).forEach(l => { if(I18N[l] && I18N[l].tags) Object.assign(I18N[l].tags, EXTRA_TAGS[l]); });""")

# --- signal card: count of not-to-buy games; clicking it shows only those
rep("""  el.innerHTML = SIGNAL_DEFS.map(s => {
    const n = GAMES.filter(g => g.tags.includes(s.key)).length;
    return `<button type="button" class="signal ${s.tone}" data-tag="${s.key}" aria-pressed="false"><div class="n" data-n="${n}">${n}</div><div class="lbl">${t('signals')[s.key]}</div></button>`;
  }).join('');
  el.querySelectorAll('.signal').forEach(n => n.addEventListener('click', () => toggleTag(n.dataset.tag)));""",
    """  el.innerHTML = SIGNAL_DEFS.map(s => {
    const n = GAMES.filter(g => g.tags.includes(s.key)).length;
    return `<button type="button" class="signal ${s.tone}" data-tag="${s.key}" aria-pressed="false"><div class="n" data-n="${n}">${n}</div><div class="lbl">${t('signals')[s.key]}</div></button>`;
  }).join('') + `<button type="button" class="signal risk" id="sigNoBuy" title="${esc(tn('why'))}" aria-pressed="false"><div class="n" data-n="${GAMES.filter(isNoBuy).length}">${GAMES.filter(isNoBuy).length}</div><div class="lbl">🚫 ${tn('sig')}</div></button>`;
  el.querySelectorAll('.signal[data-tag]').forEach(n => n.addEventListener('click', () => toggleTag(n.dataset.tag)));
  document.getElementById('sigNoBuy').addEventListener('click', () => { state.nobuy = state.nobuy === 'only' ? '' : 'only'; document.getElementById('nobuySelect').value = state.nobuy; state.shown = PAGE; render(); });""")

# --- filter state
rep("const defaultState = () => ({search:'', cat:'', age:'', trend:'', owner:'', tags:new Set(), sort:'playing_desc', shown:PAGE});",
    "const defaultState = () => ({search:'', cat:'', age:'', trend:'', owner:'', nobuy:'', tags:new Set(), sort:'playing_desc', shown:PAGE});")
rep("JSON.stringify({search:state.search, cat:state.cat, age:state.age, trend:state.trend, owner:state.owner, tags:[...state.tags], sort:state.sort})",
    "JSON.stringify({search:state.search, cat:state.cat, age:state.age, trend:state.trend, owner:state.owner, nobuy:state.nobuy, tags:[...state.tags], sort:state.sort})")
rep("state.trend = f.trend || ''; state.owner = f.owner || '';\n    state.tags = new Set(f.tags || []); state.sort = f.sort || 'playing_desc';",
    "state.trend = f.trend || ''; state.owner = f.owner || ''; state.nobuy = f.nobuy || '';\n    state.tags = new Set(f.tags || []); state.sort = f.sort || 'playing_desc';")
rep("  if(state.owner) rows = rows.filter(g => g.cType === state.owner);",
    "  if(state.owner) rows = rows.filter(g => g.cType === state.owner);\n  if(state.nobuy === 'hide') rows = rows.filter(g => !isNoBuy(g));\n  if(state.nobuy === 'only') rows = rows.filter(isNoBuy);")
rep("  if(state.owner) q.set('owner', state.owner);", "  if(state.owner) q.set('owner', state.owner);\n  if(state.nobuy) q.set('nobuy', state.nobuy);")
rep("  state.trend = q.get('trend') || ''; state.owner = q.get('owner') || '';",
    "  state.trend = q.get('trend') || ''; state.owner = q.get('owner') || ''; state.nobuy = q.get('nobuy') || '';")
rep("""      <select id="ownerSelect" aria-label="Filter by owner"></select>""",
    """      <select id="ownerSelect" aria-label="Filter by owner"></select>
      <select id="nobuySelect" aria-label="Not-to-buy filter"></select>""")
rep("""  const trend = document.getElementById('trendSelect');
  trend.innerHTML = TREND_OPTS.map(([v,k]) => `<option value="${v}">${t(k)}</option>`).join('');
  trend.value = state.trend;""", """  const trend = document.getElementById('trendSelect');
  trend.innerHTML = TREND_OPTS.map(([v,k]) => `<option value="${v}">${t(k)}</option>`).join('');
  trend.value = state.trend;
  const nb = document.getElementById('nobuySelect');
  nb.innerHTML = Object.entries(tn('sel')).map(([v,l]) => `<option value="${v}">${l}</option>`).join('');
  nb.value = state.nobuy;""")
rep("document.getElementById('ownerSelect').addEventListener('change', e => { state.owner = e.target.value; state.shown = PAGE; render(); });",
    "document.getElementById('ownerSelect').addEventListener('change', e => { state.owner = e.target.value; state.shown = PAGE; render(); });\ndocument.getElementById('nobuySelect').addEventListener('change', e => { state.nobuy = e.target.value; state.shown = PAGE; render(); });")
rep("""  document.getElementById('ownerSelect').value = '';
  document.getElementById('sortSelect').value = 'playing_desc';
  render();
});""", """  document.getElementById('ownerSelect').value = '';
  document.getElementById('nobuySelect').value = '';
  document.getElementById('sortSelect').value = 'playing_desc';
  render();
});""")
rep("""  document.querySelectorAll('.signal, .chip[data-tag]').forEach(n => {
    const on = state.tags.has(n.dataset.tag);""", """  const sb = document.getElementById('sigNoBuy'); if(sb){ sb.classList.toggle('active', state.nobuy === 'only'); sb.setAttribute('aria-pressed', String(state.nobuy === 'only')); }
  document.querySelectorAll('.signal[data-tag], .chip[data-tag]').forEach(n => {
    const on = state.tags.has(n.dataset.tag);""")

# --- badge in rows and in the game window
rep("""        <span class="creator">${t('by')} ${esc(g.creator || t('unknown'))}${g.verified ? ' ✓' : ''} ${trendBadge(g.trend)}</span>""",
    """        <span class="creator">${t('by')} ${esc(g.creator || t('unknown'))}${g.verified ? ' ✓' : ''} ${trendBadge(g.trend)}${isNoBuy(g) ? ` <span class="nobuy-badge" title="${esc(tn('why'))}">🚫 ${tn('badge')}</span>` : ''}</span>""")
rep("""      <div class="modal-tags">${g.tags.length ? g.tags.map(tagHtml).join('') : `<span class="tag none">${t('noTag')}</span>`}</div>""",
    """      <div class="modal-tags">${isNoBuy(g) ? `<span class="nobuy-badge big" title="${esc(tn('why'))}">🚫 ${tn('badge')}</span>` : ''}${g.tags.length ? g.tags.map(tagHtml).join('') : `<span class="tag none">${t('noTag')}</span>`}</div>""")

# --- score penalty
rep("""    if(g.src !== 'review') { parts.push(['sc_auto', -3, 0, false]); adj -= 3; }""",
    """    if(g.src !== 'review') { parts.push(['sc_auto', -3, 0, false]); adj -= 3; }
    if(isNoBuy(g)) { parts.push(['sc_nobuy', -20, 0, false]); adj -= 20; }""")
rep("""          ${g.scoreParts.map(([k, pts, max, na]) => `<div class="score-part"><span>${t(k)}${na ? ' *' : ''}</span>""",
    """          ${g.scoreParts.map(([k, pts, max, na]) => `<div class="score-part"><span>${k === 'sc_nobuy' ? tn('sc') : t(k)}${na ? ' *' : ''}</span>""")

# --- CSS
rep("</style>\n</head>", """
.nobuy-badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:9.5px;font-weight:700;letter-spacing:.06em;padding:1px 6px;border-radius:4px;background:color-mix(in srgb,var(--risk) 18%,transparent);color:var(--risk);border:1px solid color-mix(in srgb,var(--risk) 45%,transparent);vertical-align:1px;}
.nobuy-badge.big{font-size:11px;padding:3px 9px;margin-right:6px;}
</style>
</head>""")

open(p, 'w', encoding='utf-8', newline='').write(s)

# --- classifier rules
p2 = 'scripts/discover.py'
d = open(p2, encoding='utf-8').read()
old = """    if "tower-defense" in tags: tags.discard("tower")"""
new = """    if "tower-defense" in tags: tags.discard("tower")
    # the buyer's "not to buy" families
    if re.search(r"\\bmodded\\b|\\bmods?\\b(?! ?menu)|admin commands|\\badmin\\b.*\\b(free|abuse)", n) or re.search(r"\\bmodded\\b", d): tags.add("modded")
    if re.search(r"\\bhood\\b|da hood|the streets\\b|south bronx|\\bghetto\\b|\\btrenches\\b", n) or (cat in ("rp", "action") and re.search(r"\\bhood\\b|da hood|south bronx|\\bghetto\\b", d)):
        tags.add("hood-rp")
    if re.search(r"\\bdonat(e|ion|ions)\\b|pls donate|please donate|\\btip\\b.*\\brobux|\\bbeg\\b", n) or re.search(r"donate robux|donation game|receive donations|get donations|tip other players", d):
        tags.add("donation")
    if re.search(r"\\bincremental\\b|\\bidle\\b|\\bclicker\\b|\\bincremen", n) or re.search(r"incremental game|idle game|clicker game", d): tags.add("incremental")
    if re.search(r"hang ?out|\\bchill\\b|\\bvibe\\b|\\bvibes\\b|chat ?room|\\bcafe\\b.*\\bhangout|\\blounge\\b", n) or re.search(r"hangout game|a place to hang ?out|chill and chat|social hangout|hang out with friends and chat", d):
        tags.add("hangout")
    if re.search(r"\\btroll\\b.*\\btower\\b|\\btower\\b.*\\btroll\\b|troll obby|troll ragdoll", n): tags.add("troll-tower")"""
assert old in d
d = d.replace(old, new)
open(p2, 'w', encoding='utf-8', newline='').write(d)
print('ok')
