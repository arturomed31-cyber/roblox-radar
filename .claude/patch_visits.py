p = 'index.html'
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

VIS_BOX = ('<span class="range-in"><label for="minVis" id="visLbl"></label>'
           '<input id="minVis" type="text" inputmode="numeric" aria-label="Minimum visits">'
           '<span>–</span>'
           '<input id="maxVis" type="text" inputmode="numeric" aria-label="Maximum visits"></span>\n      ')
rep('<span class="range-in"><label for="minPl" id="plLbl">',
    VIS_BOX + '<span class="range-in"><label for="minPl" id="plLbl">')

rep("nobuy:'', discord:'', pmin:'', pmax:'', tags:new Set()", "nobuy:'', discord:'', pmin:'', pmax:'', vmin:'', vmax:'', tags:new Set()")
rep("discord:state.discord, pmin:state.pmin, pmax:state.pmax, tags:[...state.tags]",
    "discord:state.discord, pmin:state.pmin, pmax:state.pmax, vmin:state.vmin, vmax:state.vmax, tags:[...state.tags]")
rep("state.pmin = f.pmin || ''; state.pmax = f.pmax || '';",
    "state.pmin = f.pmin || ''; state.pmax = f.pmax || ''; state.vmin = f.vmin || ''; state.vmax = f.vmax || '';")
rep("  if(typedMax != null) rows = rows.filter(g => (g.playing||0) <= typedMax);",
    """  if(typedMax != null) rows = rows.filter(g => (g.playing||0) <= typedMax);
  const vMin = state.vmin === '' ? null : Number(state.vmin), vMax = state.vmax === '' ? null : Number(state.vmax);
  if(vMin != null) rows = rows.filter(g => (g.visits||0) >= vMin);
  if(vMax != null) rows = rows.filter(g => (g.visits||0) <= vMax);""")
rep("  if(state.pmax !== '') q.set('pmax', state.pmax);",
    "  if(state.pmax !== '') q.set('pmax', state.pmax);\n  if(state.vmin !== '') q.set('vmin', state.vmin);\n  if(state.vmax !== '') q.set('vmax', state.vmax);")
rep("state.pmin = q.get('pmin') ?? ''; state.pmax = q.get('pmax') ?? '';",
    "state.pmin = q.get('pmin') ?? ''; state.pmax = q.get('pmax') ?? ''; state.vmin = q.get('vmin') ?? ''; state.vmax = q.get('vmax') ?? '';")
rep("""  document.getElementById('minPl').value = state.pmin;
  document.getElementById('maxPl').value = state.pmax;""",
    """  document.getElementById('minPl').value = state.pmin;
  document.getElementById('maxPl').value = state.pmax;
  document.getElementById('visLbl').textContent = tp('visits');
  document.getElementById('minVis').placeholder = tp('min');
  document.getElementById('maxVis').placeholder = tp('max');
  document.getElementById('minVis').value = state.vmin === '' ? '' : fmtNum(Number(state.vmin));
  document.getElementById('maxVis').value = state.vmax === '' ? '' : fmtNum(Number(state.vmax));""")

rep("""let plTimer = null;
['minPl','maxPl'].forEach(id => document.getElementById(id).addEventListener('input', e => {
  const v = e.target.value.trim();
  state[id === 'minPl' ? 'pmin' : 'pmax'] = v === '' ? '' : Math.max(0, Math.floor(Number(v) || 0));
  clearTimeout(plTimer); plTimer = setTimeout(() => { state.shown = PAGE; render(); }, 250);   // wait for typing to settle
}));""", """let plTimer = null;
const rangeInput = (id, key, parse) => document.getElementById(id).addEventListener('input', e => {
  const v = e.target.value.trim();
  state[key] = v === '' ? '' : parse(v);
  clearTimeout(plTimer); plTimer = setTimeout(() => { state.shown = PAGE; render(); }, 250);   // wait for typing to settle
});
const toInt = v => Math.max(0, Math.floor(Number(v) || 0));
// visits run to the billions, so "2m", "500k", "1.5B" and "1,000,000" all work
function parseBig(v){
  const m = String(v).replace(/[\\s,]/g, '').match(/^([\\d.]+)([kmb])?$/i);
  if(!m) return toInt(v);
  const mult = {k: 1e3, m: 1e6, b: 1e9}[(m[2] || '').toLowerCase()] || 1;
  return Math.max(0, Math.round(Number(m[1]) * mult) || 0);
}
rangeInput('minPl', 'pmin', toInt);
rangeInput('maxPl', 'pmax', toInt);
rangeInput('minVis', 'vmin', parseBig);
rangeInput('maxVis', 'vmax', parseBig);""")
rep("  document.getElementById('minPl').value = ''; document.getElementById('maxPl').value = '';",
    "  document.getElementById('minPl').value = ''; document.getElementById('maxPl').value = '';\n  document.getElementById('minVis').value = ''; document.getElementById('maxVis').value = '';")
rep("""  if(state.pmin !== '' || state.pmax !== '') out.push(['players', `${tp('lbl')} ${state.pmin || 0}–${state.pmax || '∞'}`]);""",
    """  if(state.pmin !== '' || state.pmax !== '') out.push(['players', `${tp('lbl')} ${state.pmin || 0}–${state.pmax || '∞'}`]);
  if(state.vmin !== '' || state.vmax !== '') out.push(['visits', `${tp('visits')} ${state.vmin === '' ? 0 : fmtNum(Number(state.vmin))}–${state.vmax === '' ? '∞' : fmtNum(Number(state.vmax))}`]);""")
rep("""  else if(k === 'players'){ state.pmin = ''; state.pmax = ''; document.getElementById('minPl').value = ''; document.getElementById('maxPl').value = ''; }""",
    """  else if(k === 'players'){ state.pmin = ''; state.pmax = ''; document.getElementById('minPl').value = ''; document.getElementById('maxPl').value = ''; }
  else if(k === 'visits'){ state.vmin = ''; state.vmax = ''; document.getElementById('minVis').value = ''; document.getElementById('maxVis').value = ''; }""")

for a, b in [("en:{lbl:'Players', min:'min', max:'max'}", "en:{lbl:'Players', visits:'Visits', min:'min', max:'max'}"),
             ("es:{lbl:'Jugadores', min:'mín', max:'máx'}", "es:{lbl:'Jugadores', visits:'Visitas', min:'mín', max:'máx'}"),
             ("pt:{lbl:'Jogadores', min:'mín', max:'máx'}", "pt:{lbl:'Jogadores', visits:'Visitas', min:'mín', max:'máx'}"),
             ("fr:{lbl:'Joueurs', min:'min', max:'max'}", "fr:{lbl:'Joueurs', visits:'Visites', min:'min', max:'max'}"),
             ("de:{lbl:'Spieler', min:'min', max:'max'}", "de:{lbl:'Spieler', visits:'Besuche', min:'min', max:'max'}"),
             ("it:{lbl:'Giocatori', min:'min', max:'max'}", "it:{lbl:'Giocatori', visits:'Visite', min:'min', max:'max'}"),
             ("ru:{lbl:'Игроки', min:'мин', max:'макс'}", "ru:{lbl:'Игроки', visits:'Визиты', min:'мин', max:'макс'}"),
             ("ja:{lbl:'プレイヤー', min:'最小', max:'最大'}", "ja:{lbl:'プレイヤー', visits:'訪問数', min:'最小', max:'最大'}")]:
    rep(a, b)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
