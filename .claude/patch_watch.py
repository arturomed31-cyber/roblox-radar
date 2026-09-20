"""Watchlist (star games, own view, share/export) + compare up to 4 games."""
p = 'index.html'
s = open(p, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, old[:80]
    s = s.replace(old, new, count)

# ---------- CSS ----------
rep("</style>\n</head>", """
/* watchlist + compare */
.star-btn{flex:none;width:22px;height:22px;border:none;background:transparent;color:var(--text-faint);font-size:17px;line-height:1;cursor:pointer;padding:0;border-radius:5px;}
.star-btn:hover{color:var(--warn);}
.star-btn.on{color:var(--warn);}
.link-btn.star.on{border-color:var(--warn);color:var(--warn);}
.watch-tools{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:0 0 12px;}
.watch-tools .share-btn.danger:hover{border-color:var(--bad);color:var(--bad);}
.watch-empty{padding:40px 20px;text-align:center;color:var(--text-dim);border:1px dashed var(--border);border-radius:10px;font-size:13.5px;line-height:1.6;}
.watch-empty b{color:var(--warn);}
.cmp-box{border:1px solid var(--border);border-radius:10px;background:var(--panel);padding:14px 16px;margin-bottom:14px;}
.cmp-head{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px;}
.cmp-head .t{font-family:'Barlow Condensed',sans-serif;font-size:17px;font-weight:600;letter-spacing:.01em;}
.cmp-legend{display:flex;gap:6px 14px;flex-wrap:wrap;margin:8px 0 4px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--text-dim);}
.cmp-legend span{display:inline-flex;align-items:center;gap:6px;}
.cmp-legend i{width:12px;height:3px;border-radius:2px;display:inline-block;}
.cmp-empty{padding:20px;text-align:center;color:var(--text-faint);font-family:'IBM Plex Mono',monospace;font-size:12px;}
.cmp-table-wrap{overflow:auto;margin-top:10px;}
.cmp-table{min-width:0;width:100%;}
.cmp-table th,.cmp-table td{padding:6px 10px;border-bottom:1px solid var(--border);font-size:12.5px;white-space:nowrap;}
.cmp-table th{text-align:left;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--text-faint);font-weight:500;}
.cmp-table th.g{color:var(--text);font-family:inherit;font-size:12.5px;font-weight:600;border-bottom-width:2px;}
.cmp-table td.num{text-align:right;}
.cmp-table td.best{color:var(--good);font-weight:600;}
.cmp-table th.g i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px;}
.cmp-check{accent-color:var(--accent);width:15px;height:15px;cursor:pointer;flex:none;}
</style>
</head>""")

# ---------- HTML: third view + watch view ----------
rep("""      <button type="button" data-view="market" data-i18n="v_market"></button>
    </div>""", """      <button type="button" data-view="market" data-i18n="v_market"></button>
      <button type="button" data-view="watch" id="watchTab"></button>
    </div>""")

rep("""  <footer><div id="footerNote"></div>""", """  <div id="watchView" hidden>
    <div class="watch-tools" id="watchTools"></div>
    <div id="cmpBox"></div>
    <div class="table-scroll" id="watchTableWrap">
      <table>
        <thead id="whead"></thead>
        <tbody id="wbody"></tbody>
      </table>
    </div>
    <div id="watchEmpty" class="watch-empty" hidden></div>
  </div>

  <footer><div id="footerNote"></div>""")

# ---------- row star ----------
rep("""  return `<tr>
    <td><div class="game-cell">
      <button class="thumb-btn" data-open="${g._i}\"""", """  return `<tr>
    <td><div class="game-cell">
      ${starHtml(g)}
      <button class="thumb-btn" data-open="${g._i}\"""")

rep("""document.getElementById('tbody').addEventListener('click', e => {
  const btn = e.target.closest('[data-open]');
  if(btn) openModal(Number(btn.dataset.open));
});""", """document.getElementById('tbody').addEventListener('click', e => {
  const st = e.target.closest('[data-star]');
  if(st){ toggleWatch(st.dataset.star); return; }
  const btn = e.target.closest('[data-open]');
  if(btn) openModal(Number(btn.dataset.open));
});""")

# ---------- modal star ----------
rep("""        <button type="button" class="link-btn ghost" id="shareGame">${ts('shareGame')}</button>
      </div>""", """        <button type="button" class="link-btn ghost" id="shareGame">${ts('shareGame')}</button>
        <button type="button" class="link-btn star ${isWatched(g.id) ? 'on' : ''}" id="watchGame">${isWatched(g.id) ? '★ ' + tw('w_on') : '☆ ' + tw('w_add')}</button>
      </div>""")
rep("""  document.getElementById('shareGame').addEventListener('click', e => copyText(buildUrl(g.id), e.currentTarget));
  document.body.style.overflow = 'hidden';""", """  document.getElementById('shareGame').addEventListener('click', e => copyText(buildUrl(g.id), e.currentTarget));
  document.getElementById('watchGame').addEventListener('click', e => {
    toggleWatch(g.id);
    const b = e.currentTarget, on = isWatched(g.id);
    b.classList.toggle('on', on); b.textContent = on ? '★ ' + tw('w_on') : '☆ ' + tw('w_add');
  });
  document.body.style.overflow = 'hidden';""")

# ---------- view switching ----------
rep("""  document.getElementById('gamesView').hidden = v !== 'games';
  document.getElementById('marketView').hidden = v !== 'market';
  if(v === 'market') renderMarket();""", """  document.getElementById('gamesView').hidden = v !== 'games';
  document.getElementById('marketView').hidden = v !== 'market';
  document.getElementById('watchView').hidden = v !== 'watch';
  if(v === 'market') renderMarket();
  if(v === 'watch') renderWatch();""")

# ---------- url ----------
rep("""  if(view === 'market') q.set('view', 'market');
  const qs = q.toString();""", """  if(view === 'market') q.set('view', 'market');
  if(view === 'watch'){ q.set('view', 'watch'); if(WATCH.size) q.set('watch', [...WATCH].join(',')); }
  const qs = q.toString();""")
rep("""  if(q.get('view') === 'market') view = 'market';
  return q.get('game');""", """  if(q.get('view') === 'market') view = 'market';
  if(q.get('view') === 'watch'){
    view = 'watch';
    (q.get('watch') || '').split(',').filter(Boolean).forEach(id => WATCH.add(String(id)));
    saveWatch();
  }
  return q.get('game');""")

# ---------- language hook ----------
rep("""    render();
    renderMarket();
    if(currentGame) openModal(currentGame._i, currentRange);
  }
}""", """    render();
    renderMarket();
    renderWatch();
    if(currentGame) openModal(currentGame._i, currentRange);
  }
  document.getElementById('watchTab').textContent = tw('w_view') + (WATCH.size ? ` (${WATCH.size})` : '');
}""")

# ---------- watch module (before shareable links) ----------
rep("""/* ---------- shareable links ---------- */""", r"""/* ---------- watchlist + compare ---------- */
const WATCH_KEY = 'radar.watch.v1', CMP_KEY = 'radar.cmp.v1';
let WATCH = new Set(), CMP = [], cmpRange = '7d', cmpMode = 'abs';
try { WATCH = new Set((JSON.parse(localStorage.getItem(WATCH_KEY) || '[]')).map(String)); } catch (e) {}
try { CMP = (JSON.parse(localStorage.getItem(CMP_KEY) || '[]')).map(String); } catch (e) {}
function saveWatch(){ try { localStorage.setItem(WATCH_KEY, JSON.stringify([...WATCH])); localStorage.setItem(CMP_KEY, JSON.stringify(CMP)); } catch (e) {} }
const WATCH_I18N = {
  en: {w_view:'Watchlist', w_add:'Watch', w_on:'Watching', w_star:'Add to watchlist', w_unstar:'Remove from watchlist',
       w_empty:'Your watchlist is empty. Press <b>☆</b> next to any game (in the table or in its stats window) to keep an eye on it. The list is saved in this browser.',
       w_export:'Copy IDs for Discord alerts', w_link:'Copy link to this list', w_clear:'Clear list', w_cleared:'Cleared',
       w_exportHint:'Paste the copied IDs into data/watchlist.json in the repository and Discord will warn you when any of these games moves ±30 % in 24 h.',
       w_cmp:'Compare', w_cmpHint:'Tick up to 4 games in the list to overlay their player charts.', w_abs:'Players', w_rel:'% change', w_cmpMax:'Up to 4 games', w_metric:'Metric',
       w_since:'since the start of the range', w_n:(n)=>`${n} game${n===1?'':'s'}`},
  es: {w_view:'Mi lista', w_add:'Seguir', w_on:'Siguiendo', w_star:'Añadir a mi lista', w_unstar:'Quitar de mi lista',
       w_empty:'Tu lista está vacía. Pulsa <b>☆</b> junto a cualquier juego (en la tabla o en su ventana de estadísticas) para seguirlo. La lista se guarda en este navegador.',
       w_export:'Copiar IDs para alertas de Discord', w_link:'Copiar enlace a esta lista', w_clear:'Vaciar lista', w_cleared:'Vaciada',
       w_exportHint:'Pega los IDs copiados en data/watchlist.json del repositorio y Discord te avisará cuando alguno de estos juegos se mueva ±30 % en 24 h.',
       w_cmp:'Comparar', w_cmpHint:'Marca hasta 4 juegos de la lista para superponer sus gráficas de jugadores.', w_abs:'Jugadores', w_rel:'% cambio', w_cmpMax:'Máximo 4 juegos', w_metric:'Métrica',
       w_since:'desde el inicio del rango', w_n:(n)=>`${n} juego${n===1?'':'s'}`},
  pt: {w_view:'Minha lista', w_add:'Seguir', w_on:'Seguindo', w_star:'Adicionar à lista', w_unstar:'Remover da lista',
       w_empty:'Sua lista está vazia. Toque em <b>☆</b> ao lado de qualquer jogo para acompanhá-lo. A lista fica salva neste navegador.',
       w_export:'Copiar IDs para alertas do Discord', w_link:'Copiar link desta lista', w_clear:'Limpar lista', w_cleared:'Limpa',
       w_exportHint:'Cole os IDs copiados em data/watchlist.json do repositório e o Discord avisará quando algum desses jogos variar ±30 % em 24 h.',
       w_cmp:'Comparar', w_cmpHint:'Marque até 4 jogos da lista para sobrepor seus gráficos.', w_abs:'Jogadores', w_rel:'% variação', w_cmpMax:'Máximo 4 jogos', w_metric:'Métrica',
       w_since:'desde o início do período', w_n:(n)=>`${n} jogo${n===1?'':'s'}`},
  fr: {w_view:'Ma liste', w_add:'Suivre', w_on:'Suivi', w_star:'Ajouter à ma liste', w_unstar:'Retirer de ma liste',
       w_empty:'Votre liste est vide. Appuyez sur <b>☆</b> à côté d’un jeu pour le suivre. La liste est enregistrée dans ce navigateur.',
       w_export:'Copier les IDs pour les alertes Discord', w_link:'Copier le lien de cette liste', w_clear:'Vider la liste', w_cleared:'Vidée',
       w_exportHint:'Collez les IDs copiés dans data/watchlist.json du dépôt et Discord vous préviendra quand un de ces jeux bouge de ±30 % en 24 h.',
       w_cmp:'Comparer', w_cmpHint:'Cochez jusqu’à 4 jeux de la liste pour superposer leurs courbes.', w_abs:'Joueurs', w_rel:'% variation', w_cmpMax:'4 jeux maximum', w_metric:'Mesure',
       w_since:'depuis le début de la période', w_n:(n)=>`${n} jeu${n===1?'':'x'}`},
  de: {w_view:'Meine Liste', w_add:'Beobachten', w_on:'Beobachtet', w_star:'Zur Liste hinzufügen', w_unstar:'Aus der Liste entfernen',
       w_empty:'Deine Liste ist leer. Drücke <b>☆</b> neben einem Spiel, um es zu beobachten. Die Liste wird in diesem Browser gespeichert.',
       w_export:'IDs für Discord-Alarme kopieren', w_link:'Link zu dieser Liste kopieren', w_clear:'Liste leeren', w_cleared:'Geleert',
       w_exportHint:'Füge die kopierten IDs in data/watchlist.json im Repository ein; Discord warnt dann bei ±30 % in 24 h.',
       w_cmp:'Vergleichen', w_cmpHint:'Wähle bis zu 4 Spiele aus der Liste, um ihre Spielerkurven zu überlagern.', w_abs:'Spieler', w_rel:'% Änderung', w_cmpMax:'Höchstens 4 Spiele', w_metric:'Kennzahl',
       w_since:'seit Beginn des Zeitraums', w_n:(n)=>`${n} Spiel${n===1?'':'e'}`},
  it: {w_view:'La mia lista', w_add:'Segui', w_on:'Seguito', w_star:'Aggiungi alla lista', w_unstar:'Rimuovi dalla lista',
       w_empty:'La tua lista è vuota. Premi <b>☆</b> accanto a un gioco per seguirlo. La lista è salvata in questo browser.',
       w_export:'Copia ID per gli avvisi Discord', w_link:'Copia link a questa lista', w_clear:'Svuota lista', w_cleared:'Svuotata',
       w_exportHint:'Incolla gli ID copiati in data/watchlist.json del repository e Discord ti avviserà quando uno di questi giochi si muove del ±30 % in 24 h.',
       w_cmp:'Confronta', w_cmpHint:'Spunta fino a 4 giochi della lista per sovrapporre i loro grafici.', w_abs:'Giocatori', w_rel:'% variazione', w_cmpMax:'Massimo 4 giochi', w_metric:'Metrica',
       w_since:'dall’inizio del periodo', w_n:(n)=>`${n} gioc${n===1?'o':'hi'}`},
  ru: {w_view:'Мой список', w_add:'Следить', w_on:'Слежу', w_star:'Добавить в список', w_unstar:'Убрать из списка',
       w_empty:'Список пуст. Нажмите <b>☆</b> рядом с игрой, чтобы следить за ней. Список хранится в этом браузере.',
       w_export:'Скопировать ID для оповещений Discord', w_link:'Скопировать ссылку на список', w_clear:'Очистить список', w_cleared:'Очищено',
       w_exportHint:'Вставьте скопированные ID в data/watchlist.json репозитория — Discord предупредит при изменении ±30 % за 24 ч.',
       w_cmp:'Сравнить', w_cmpHint:'Отметьте до 4 игр из списка, чтобы наложить их графики.', w_abs:'Игроки', w_rel:'% изменение', w_cmpMax:'Не более 4 игр', w_metric:'Показатель',
       w_since:'с начала периода', w_n:(n)=>`${n} игр`},
  ja: {w_view:'ウォッチリスト', w_add:'ウォッチ', w_on:'ウォッチ中', w_star:'リストに追加', w_unstar:'リストから削除',
       w_empty:'リストは空です。ゲームの横の <b>☆</b> を押すと追跡できます。リストはこのブラウザに保存されます。',
       w_export:'Discord通知用のIDをコピー', w_link:'このリストへのリンクをコピー', w_clear:'リストを空にする', w_cleared:'空にしました',
       w_exportHint:'コピーしたIDをリポジトリの data/watchlist.json に貼り付けると、24時間で±30 %動いたときにDiscordが通知します。',
       w_cmp:'比較', w_cmpHint:'リストから最大4件を選ぶとプレイヤー推移を重ねて表示します。', w_abs:'プレイヤー', w_rel:'% 変化', w_cmpMax:'最大4件', w_metric:'指標',
       w_since:'期間開始時から', w_n:(n)=>`${n} 件`}
};
const tw = k => (WATCH_I18N[settings.lang] || WATCH_I18N.en)[k] ?? WATCH_I18N.en[k];
const CMP_COLORS = ['var(--accent)', 'var(--warn)', 'var(--good)', '#a78bfa'];
function isWatched(id){ return WATCH.has(String(id)); }
function starHtml(g){
  const on = isWatched(g.id);
  return `<button type="button" class="star-btn ${on ? 'on' : ''}" data-star="${g.id}" title="${tw(on ? 'w_unstar' : 'w_star')}" aria-pressed="${on}">${on ? '★' : '☆'}</button>`;
}
function toggleWatch(id){
  id = String(id);
  if(WATCH.has(id)){ WATCH.delete(id); CMP = CMP.filter(x => x !== id); }
  else WATCH.add(id);
  saveWatch();
  document.querySelectorAll(`[data-star="${id}"]`).forEach(b => {
    const on = WATCH.has(id);
    b.classList.toggle('on', on); b.textContent = on ? '★' : '☆'; b.title = tw(on ? 'w_unstar' : 'w_star'); b.setAttribute('aria-pressed', String(on));
  });
  document.getElementById('watchTab').textContent = tw('w_view') + (WATCH.size ? ` (${WATCH.size})` : '');
  if(view === 'watch') renderWatch();
  else syncUrl();
}
function watchedGames(){
  const byId = new Map(GAMES.map(g => [String(g.id), g]));
  return [...WATCH].map(id => byId.get(id)).filter(Boolean).sort((a,b) => (b.playing||0) - (a.playing||0));
}
function renderWatch(){
  if(!GAMES.length) return;
  const tab = document.getElementById('watchTab');
  tab.textContent = tw('w_view') + (WATCH.size ? ` (${WATCH.size})` : '');
  if(view !== 'watch') return;
  const games = watchedGames();
  CMP = CMP.filter(id => WATCH.has(id)).slice(0, 4);
  const tools = document.getElementById('watchTools');
  tools.innerHTML = `<div class="count-row" style="margin:0;flex:1">${tw('w_n')(games.length)}</div>
    <button type="button" class="share-btn" id="wLink">${tw('w_link')}</button>
    <button type="button" class="share-btn" id="wExport" title="${esc(tw('w_exportHint'))}">${tw('w_export')}</button>
    <button type="button" class="share-btn danger" id="wClear">${tw('w_clear')}</button>`;
  document.getElementById('wLink').addEventListener('click', e => copyText(buildUrl(null), e.currentTarget));
  document.getElementById('wExport').addEventListener('click', e => copyText(JSON.stringify(games.map(g => g.id)), e.currentTarget));
  document.getElementById('wClear').addEventListener('click', e => {
    if(!WATCH.size) return;
    WATCH.clear(); CMP = []; saveWatch();
    document.querySelectorAll('[data-star]').forEach(b => { b.classList.remove('on'); b.textContent = '☆'; });
    renderWatch();
  });
  const empty = document.getElementById('watchEmpty'), wrap = document.getElementById('watchTableWrap'), cmpBox = document.getElementById('cmpBox');
  empty.hidden = games.length > 0; wrap.hidden = !games.length;
  empty.innerHTML = tw('w_empty');
  if(!games.length){ cmpBox.innerHTML = ''; syncUrl(); return; }

  const cols = visibleCols();
  document.getElementById('whead').innerHTML = `<tr><th style="width:34px" title="${tw('w_cmp')}">⇄</th><th>${t('h_game')}</th><th>${t('h_cat')}</th><th>${t('h_signals')}</th>${cols.map(c => `<th style="text-align:right">${t(c.h)}</th>`).join('')}</tr>`;
  document.getElementById('wbody').innerHTML = games.map(g => {
    const id = String(g.id), on = CMP.includes(id), full = CMP.length >= 4 && !on;
    return rowHtml(g).replace('<tr>', `<tr>
    <td><input type="checkbox" class="cmp-check" data-cmp="${id}" ${on ? 'checked' : ''} ${full ? `disabled title="${tw('w_cmpMax')}"` : ''} aria-label="${tw('w_cmp')}"></td>`);
  }).join('');
  const wb = document.getElementById('wbody');
  wb.onclick = e => {
    const st = e.target.closest('[data-star]');
    if(st){ toggleWatch(st.dataset.star); return; }
    const btn = e.target.closest('[data-open]');
    if(btn) openModal(Number(btn.dataset.open));
  };
  wb.querySelectorAll('[data-cmp]').forEach(cb => cb.addEventListener('change', () => {
    const id = cb.dataset.cmp;
    if(cb.checked){ if(!CMP.includes(id) && CMP.length < 4) CMP.push(id); }
    else CMP = CMP.filter(x => x !== id);
    saveWatch(); renderWatch();
  }));
  renderCompare();
  syncUrl();
}
function renderCompare(){
  const box = document.getElementById('cmpBox');
  const byId = new Map(GAMES.map(g => [String(g.id), g]));
  const games = CMP.map(id => byId.get(id)).filter(Boolean);
  const ranges = RANGES.map(r => `<button type="button" class="range-btn ${r.key === cmpRange ? 'on' : ''}" data-crange="${r.key}">${t('r_'+r.key)}</button>`).join('');
  const modes = `<div class="seg"><button type="button" data-cmode="abs" class="${cmpMode === 'abs' ? 'on' : ''}">${tw('w_abs')}</button><button type="button" data-cmode="rel" class="${cmpMode === 'rel' ? 'on' : ''}">${tw('w_rel')}</button></div>`;
  let body;
  if(games.length < 1){
    body = `<div class="cmp-empty">${tw('w_cmpHint')}</div>`;
    renderCompare._geom = null;
  } else {
    const range = RANGES.find(r => r.key === cmpRange) || RANGES[RANGES.length-1];
    const series = games.map(g => pointsInRange(seriesFor(g), range));
    const end = Math.max(...series.map(s => s.length ? s[s.length-1].t : 0));
    const start = range.ms === Infinity ? Math.min(...series.map(s => s.length ? s[0].t : Infinity)) : end - range.ms;
    const rel = cmpMode === 'rel';
    const lines = series.map(s => {
      const base = s.length ? s[0].v : 1;
      return s.map(p => ({t: p.t, v: rel ? (base ? (p.v / base - 1) * 100 : 0) : p.v, raw: p.v}));
    });
    const W = 680, H = 220, PL = 56, PR = 14, PT = 14, PB = 28;
    const t0 = isFinite(start) ? start : end - 1, span = Math.max(1, end - t0);
    const vals = lines.flatMap(l => l.map(p => p.v));
    let vmin = vals.length ? Math.min(...vals) : 0, vmax = vals.length ? Math.max(...vals) : 1;
    if(rel){ vmin = Math.min(vmin, 0); vmax = Math.max(vmax, 0); }
    const ystep = niceStep(Math.max(1, vmax - vmin) * 1.25, 4);
    let ylo = Math.floor(vmin / ystep) * ystep, yhi = Math.ceil(vmax / ystep) * ystep;
    if(ylo === yhi) yhi = ylo + ystep;
    if(!rel && ylo < 0) ylo = 0;
    const x = tt => PL + ((tt - t0) / span) * (W - PL - PR);
    const y = v => PT + (1 - (v - ylo) / (yhi - ylo)) * (H - PT - PB);
    let ygrid = '';
    for(let v = ylo; v <= yhi + 1e-9; v += ystep){
      ygrid += `<line x1="${PL}" y1="${y(v).toFixed(1)}" x2="${W-PR}" y2="${y(v).toFixed(1)}" stroke="${rel && Math.abs(v) < 1e-9 ? 'var(--text-faint)' : 'var(--border)'}" stroke-width="1"/>
        <text x="${PL-8}" y="${(y(v)+3.5).toFixed(1)}" text-anchor="end" font-size="10" font-family="IBM Plex Mono, monospace" fill="var(--text-faint)">${rel ? fmtPct(v) : fmtNum(Math.round(v))}</text>`;
    }
    const withDate = span > 20*3600e3, nx = 5;
    let xgrid = '';
    for(let i = 0; i <= nx; i++){
      const tt = t0 + span * i / nx;
      xgrid += `<line x1="${x(tt).toFixed(1)}" y1="${PT}" x2="${x(tt).toFixed(1)}" y2="${H-PB}" stroke="var(--border)" stroke-width="1" stroke-dasharray="2 3"/>
        <text x="${x(tt).toFixed(1)}" y="${H-9}" text-anchor="${i === 0 ? 'start' : i === nx ? 'end' : 'middle'}" font-size="10" font-family="IBM Plex Mono, monospace" fill="var(--text-faint)">${span > 3*86400e3 ? fmtDateShort(tt) : fmtTime(tt, withDate)}</text>`;
    }
    const paths = lines.map((l, i) => {
      if(l.length < 2) return '';
      const gaps = l.slice(1).map((p,j) => p.t - l[j].t).sort((a,b)=>a-b);
      const gapLimit = Math.max((gaps[Math.floor(gaps.length/2)] || 1) * 3, 26*3600e3);
      let d = '';
      l.forEach((p, j) => { d += (j === 0 || p.t - l[j-1].t > gapLimit ? ' M' : ' L') + x(p.t).toFixed(1) + ',' + y(p.v).toFixed(1); });
      return `<path d="${d.trim()}" fill="none" stroke="${CMP_COLORS[i]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>`;
    }).join('');
    const dots = lines.map((l, i) => `<circle id="cmpDot${i}" cx="0" cy="0" r="4" fill="var(--panel)" stroke="${CMP_COLORS[i]}" stroke-width="2" visibility="hidden"/>`).join('');
    body = `<div class="chart-wrap" id="cmpWrap">
      <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${tw('w_cmp')}" id="cmpSvg">${ygrid}${xgrid}${paths}
        <line id="cmpCursor" x1="0" y1="${PT}" x2="0" y2="${H-PB}" stroke="var(--text-dim)" stroke-width="1" visibility="hidden"/>${dots}
      </svg><div class="chart-tip" id="cmpTip" hidden></div></div>
      <div class="cmp-legend">${games.map((g, i) => `<span><i style="background:${CMP_COLORS[i]}"></i>${esc(g.name.length > 34 ? g.name.slice(0,33) + '…' : g.name)}</span>`).join('')}${rel ? `<span style="color:var(--text-faint)">${tw('w_since')}</span>` : ''}</div>`;
    renderCompare._geom = {lines, W, H, PL, PR, t0, span, x, y, rel};
  }
  // side-by-side metrics
  const metrics = [
    ['st_now', g => g.playing, fmtFull, 1], ['st_peak', g => { const s = seriesFor(g); return s.length ? Math.max(...s.map(p=>p.v)) : null; }, fmtFull, 1],
    ['st_d1', g => g.d1, fmtPct, 1], ['st_d7', g => g.d7, fmtPct, 1], ['st_d30', g => g.d30, fmtPct, 1],
    ['st_rating', g => g.like, v => v == null ? '—' : v + '%', 1], ['st_visits', g => g.visits, fmtFull, 1], ['st_vpd', g => g.vpd, fmtFull, 1],
    ['st_favs', g => g.favs, fmtFull, 1], ['st_age', g => g.age, fmtAge, 0], ['st_upd', g => g.upd, fmtUpd, -1],
    ['h_score', g => g.score, v => v, 1], ['bz_rev', g => g.rev, v => v == null ? '—' : '$' + fmtFull(v) + ' ' + t('bz_perMonth'), 1],
    ['bz_members', g => g.members, fmtFull, 1], ['bz_passes', g => g.passes, v => v ?? '—', 0]
  ];
  let table = '';
  if(games.length){
    table = `<div class="cmp-table-wrap"><table class="cmp-table"><thead><tr><th>${tw('w_metric')}</th>${games.map((g, i) => `<th class="g"><i style="background:${CMP_COLORS[i]}"></i><button class="game-name" data-open="${g._i}">${esc(g.name.length > 28 ? g.name.slice(0,27) + '…' : g.name)}</button></th>`).join('')}</tr></thead><tbody>` +
      metrics.map(([k, get, fmt, dir]) => {
        const vals = games.map(get);
        const nums = vals.filter(v => typeof v === 'number');
        const best = dir && nums.length > 1 ? (dir > 0 ? Math.max(...nums) : Math.min(...nums)) : null;
        return `<tr><th>${t(k)}</th>${vals.map(v => `<td class="num ${best != null && v === best ? 'best' : ''}">${fmt(v)}</td>`).join('')}</tr>`;
      }).join('') + `</tbody></table></div>`;
  }
  box.innerHTML = `<div class="cmp-box">
    <div class="cmp-head"><span class="t">${tw('w_cmp')} <span class="market-sub">· ${tw('w_cmpMax')}</span></span>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">${games.length ? modes : ''}<div class="range-bar">${ranges}</div></div></div>
    ${body}${table}</div>`;
  box.querySelectorAll('[data-crange]').forEach(b => b.addEventListener('click', () => { cmpRange = b.dataset.crange; renderCompare(); }));
  box.querySelectorAll('[data-cmode]').forEach(b => b.addEventListener('click', () => { cmpMode = b.dataset.cmode; renderCompare(); }));
  box.querySelectorAll('[data-open]').forEach(b => b.addEventListener('click', () => openModal(Number(b.dataset.open))));
  bindCompareHover(games);
}
function bindCompareHover(games){
  const geom = renderCompare._geom, svg = document.getElementById('cmpSvg');
  if(!geom || !svg) return;
  const tip = document.getElementById('cmpTip'), cursor = document.getElementById('cmpCursor'), wrap = document.getElementById('cmpWrap');
  const move = e => {
    const r = svg.getBoundingClientRect();
    const sx = (e.clientX - r.left) * geom.W / r.width;
    const tt = Math.max(geom.t0, Math.min(geom.t0 + geom.span, geom.t0 + ((sx - geom.PL) / (geom.W - geom.PL - geom.PR)) * geom.span));
    let rows = '', px = geom.x(tt), py = null;
    geom.lines.forEach((l, i) => {
      const dot = document.getElementById('cmpDot' + i);
      if(!l.length){ dot.setAttribute('visibility', 'hidden'); return; }
      let best = l[0];
      for(const p of l) if(Math.abs(p.t - tt) < Math.abs(best.t - tt)) best = p;
      const near = Math.abs(best.t - tt) < geom.span / 8;
      dot.setAttribute('cx', geom.x(best.t)); dot.setAttribute('cy', geom.y(best.v)); dot.setAttribute('visibility', near ? 'visible' : 'hidden');
      if(near){ if(py == null) py = geom.y(best.v); rows += `<span style="color:${CMP_COLORS[i]}">■</span> ${esc(games[i].name.slice(0, 22))}: <b>${fmtFull(best.raw)}</b>${geom.rel ? ` (${fmtPct(best.v)})` : ''}<br>`; }
    });
    cursor.setAttribute('x1', px); cursor.setAttribute('x2', px); cursor.setAttribute('visibility', 'visible');
    tip.innerHTML = fmtTime(tt, true) + '<br>' + rows;
    tip.hidden = !rows;
    tip.style.left = (px * r.width / geom.W) + 'px';
    tip.style.top = ((py ?? 30) * r.height / geom.H) + 'px';
  };
  const leave = () => { tip.hidden = true; cursor.setAttribute('visibility', 'hidden'); geom.lines.forEach((_, i) => document.getElementById('cmpDot' + i).setAttribute('visibility', 'hidden')); };
  wrap.addEventListener('mousemove', move);
  wrap.addEventListener('mouseleave', leave);
  wrap.addEventListener('touchstart', e => move(e.touches[0]), {passive:true});
  wrap.addEventListener('touchmove', e => move(e.touches[0]), {passive:true});
}

/* ---------- shareable links ---------- */""")

open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
