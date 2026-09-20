"""Live mode: keep re-reading one game from Roblox at a chosen pace for a chosen time, via the Worker."""
p = 'index.html'
s = open(p, encoding='utf-8').read()

def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

rep("</style>\n</head>", """
/* live mode */
.live-box .t .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--text-faint);margin-right:6px;vertical-align:1px;}
.live-box.on .t .dot{background:var(--good);box-shadow:0 0 0 0 color-mix(in srgb,var(--good) 60%,transparent);animation:pulse 1.4s ease-out infinite;}
@keyframes pulse{to{box-shadow:0 0 0 7px transparent;}}
.live-ctrl{display:flex;gap:6px;align-items:center;flex-wrap:wrap;}
.live-ctrl select{padding:6px 8px;font-size:12px;}
.live-ctrl .lbl{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--text-faint);}
.live-ctrl button{font-family:inherit;font-size:12.5px;font-weight:600;padding:7px 14px;border-radius:7px;border:1px solid var(--accent);background:var(--accent);color:var(--accent-text);cursor:pointer;}
.live-ctrl button.stop{background:transparent;color:var(--bad);border-color:var(--bad);}
.live-ctrl button:disabled{opacity:.5;cursor:not-allowed;}
.live-stats{display:flex;flex-wrap:wrap;gap:8px 22px;margin:10px 0 6px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--text-dim);}
.live-stats b{color:var(--text);font-weight:600;font-variant-numeric:tabular-nums;}
.live-stats .big{font-size:22px;color:var(--good);}
.live-spark{display:block;width:100%;height:auto;margin-top:4px;}
.live-status{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--text-faint);margin-top:6px;}
.live-status.err{color:var(--bad);}
@media (prefers-reduced-motion:reduce){.live-box.on .t .dot{animation:none;}}
</style>
</head>""")

# stat tiles get keys so live readings can update them in place
rep("""  const stats = [
    [t('st_now'), fmtFull(g.playing)], [t('st_rank'), '#'+g._rank], [t('st_peak'), peak != null ? fmtFull(peak) : '—'],
    [t('st_visits'), fmtFull(g.visits)], [t('st_vpd'), fmtFull(g.vpd)], [t('st_rating'), g.like != null ? g.like+'%' : '—'],
    [t('st_votes'), fmtFull(g.votes)], [t('st_favs'), fmtFull(g.favs)], [t('st_age'), fmtAge(g.age)],
    [t('st_upd'), fmtUpd(g.upd)], [t('st_server'), g.maxP ? g.maxP + ' ' + t('players') : '—'], [t('st_mat'), g.maturity || '—']
  ];""", """  const stats = [
    [t('st_now'), fmtFull(g.playing), 'now'], [t('st_rank'), '#'+g._rank], [t('st_peak'), peak != null ? fmtFull(peak) : '—'],
    [t('st_visits'), fmtFull(g.visits), 'visits'], [t('st_vpd'), fmtFull(g.vpd)], [t('st_rating'), g.like != null ? g.like+'%' : '—', 'rating'],
    [t('st_votes'), fmtFull(g.votes), 'votes'], [t('st_favs'), fmtFull(g.favs), 'favs'], [t('st_age'), fmtAge(g.age)],
    [t('st_upd'), fmtUpd(g.upd)], [t('st_server'), g.maxP ? g.maxP + ' ' + t('players') : '—'], [t('st_mat'), g.maturity || '—']
  ];""")
rep("""      <div class="stat-grid">${stats.map(([k,v]) => `<div class="stat"><div class="v">${v}</div><div class="k">${k}</div></div>`).join('')}</div>""",
    """      <div class="stat-grid">${stats.map(([k,v,key]) => `<div class="stat" ${key ? `data-k="${key}"` : ''}><div class="v">${v}</div><div class="k">${k}</div></div>`).join('')}</div>

      <div class="score-box live-box" id="liveBox"></div>""")

rep("""  renderChart(g, rangeKey || pickDefaultRange(series));
  overlay.hidden = false;""", """  renderChart(g, rangeKey || pickDefaultRange(series));
  renderLive(g);
  overlay.hidden = false;""")

rep("""/* ---------- Discord invite ---------- */""", r"""/* ---------- live mode (needs the Cloudflare Worker relay) ---------- */
const WORKER_URL = '';   // e.g. 'https://roblox-radar.<your-subdomain>.workers.dev' — set after deploying worker/worker.js
const LIVE = new Map();  // gameId -> {every, until, timer, samples:[{t,v}], start:{...}, last, err}
const LIVE_EVERY = [[15, '15 s'], [30, '30 s'], [60, '1 min'], [300, '5 min']];
const LIVE_FOR = [[600, '10 min'], [1800, '30 min'], [3600, '1 h'], [0, '∞']];
const LIVE_I18N = {
  en:{title:'Live mode', hint:'Re-reads this game straight from Roblox at the pace you choose. Runs in this browser while the tab stays open; nothing is saved to the shared history.', every:'every', for:'for', start:'Start', stop:'Stop', forever:'until you stop it', stopsAt:'stops at', now:'now', since:'since start', min:'min', max:'max', n:'readings', last:'last', err:'Roblox did not answer, retrying…', needs:'Live mode needs the data relay (Cloudflare Worker), which is not set up yet.', done:'finished'},
  es:{title:'Modo en vivo', hint:'Vuelve a leer este juego directamente de Roblox al ritmo que elijas. Corre en este navegador mientras la pestaña esté abierta; no se guarda en el historial compartido.', every:'cada', for:'durante', start:'Iniciar', stop:'Parar', forever:'hasta que lo pares', stopsAt:'para a las', now:'ahora', since:'desde el inicio', min:'mín', max:'máx', n:'lecturas', last:'última', err:'Roblox no respondió, reintentando…', needs:'El modo en vivo necesita el relé de datos (Cloudflare Worker), que aún no está configurado.', done:'terminado'},
  pt:{title:'Modo ao vivo', hint:'Relê este jogo direto do Roblox no ritmo que você escolher. Roda neste navegador enquanto a aba estiver aberta; nada é salvo no histórico compartilhado.', every:'a cada', for:'durante', start:'Iniciar', stop:'Parar', forever:'até você parar', stopsAt:'para às', now:'agora', since:'desde o início', min:'mín', max:'máx', n:'leituras', last:'última', err:'O Roblox não respondeu, tentando de novo…', needs:'O modo ao vivo precisa do relé de dados (Cloudflare Worker), ainda não configurado.', done:'concluído'},
  fr:{title:'Mode direct', hint:'Relit ce jeu directement depuis Roblox au rythme choisi. Fonctionne dans ce navigateur tant que l’onglet reste ouvert ; rien n’est enregistré dans l’historique partagé.', every:'toutes les', for:'pendant', start:'Démarrer', stop:'Arrêter', forever:'jusqu’à l’arrêt', stopsAt:'s’arrête à', now:'maintenant', since:'depuis le début', min:'min', max:'max', n:'lectures', last:'dernière', err:'Roblox n’a pas répondu, nouvel essai…', needs:'Le mode direct nécessite le relais de données (Cloudflare Worker), pas encore configuré.', done:'terminé'},
  de:{title:'Live-Modus', hint:'Liest dieses Spiel im gewählten Takt direkt von Roblox. Läuft in diesem Browser, solange der Tab offen ist; nichts wird in der gemeinsamen Historie gespeichert.', every:'alle', for:'für', start:'Start', stop:'Stopp', forever:'bis du stoppst', stopsAt:'endet um', now:'jetzt', since:'seit Start', min:'min', max:'max', n:'Messungen', last:'letzte', err:'Roblox antwortet nicht, neuer Versuch…', needs:'Der Live-Modus braucht das Daten-Relay (Cloudflare Worker), das noch nicht eingerichtet ist.', done:'beendet'},
  it:{title:'Modalità live', hint:'Rilegge questo gioco direttamente da Roblox al ritmo scelto. Funziona in questo browser finché la scheda resta aperta; nulla viene salvato nello storico condiviso.', every:'ogni', for:'per', start:'Avvia', stop:'Ferma', forever:'finché non lo fermi', stopsAt:'si ferma alle', now:'ora', since:'dall’inizio', min:'min', max:'max', n:'letture', last:'ultima', err:'Roblox non ha risposto, riprovo…', needs:'La modalità live richiede il relay dati (Cloudflare Worker), non ancora configurato.', done:'finito'},
  ru:{title:'Режим live', hint:'Перечитывает игру прямо из Roblox с выбранной частотой. Работает в этом браузере, пока вкладка открыта; в общую историю ничего не сохраняется.', every:'каждые', for:'в течение', start:'Старт', stop:'Стоп', forever:'пока не остановите', stopsAt:'остановится в', now:'сейчас', since:'с начала', min:'мин', max:'макс', n:'замеров', last:'последний', err:'Roblox не ответил, повтор…', needs:'Режиму live нужен ретранслятор данных (Cloudflare Worker), он ещё не настроен.', done:'завершено'},
  ja:{title:'ライブモード', hint:'選んだ間隔でこのゲームをRobloxから直接読み直します。タブを開いている間このブラウザで動作し、共有履歴には保存されません。', every:'間隔', for:'期間', start:'開始', stop:'停止', forever:'停止するまで', stopsAt:'終了予定', now:'現在', since:'開始時から', min:'最小', max:'最大', n:'回', last:'最終', err:'Robloxが応答しません。再試行中…', needs:'ライブモードにはデータ中継（Cloudflare Worker）が必要ですが、まだ設定されていません。', done:'終了'}
};
const tl = k => (LIVE_I18N[settings.lang] || LIVE_I18N.en)[k];
const hhmmss = ms => { const d = new Date(ms); return settings.tz === 'utc' ? d.toISOString().slice(11, 19) + 'Z' : `${pad2(d.getHours())}:${pad2(d.getMinutes())}:${pad2(d.getSeconds())}`; };

async function liveFetch(id){
  const r = await fetch(`${WORKER_URL.replace(/\/$/, '')}/live?ids=${id}`, {cache: 'no-store'});
  if(!r.ok) throw new Error('relay ' + r.status);
  const d = await r.json();
  return d.games && d.games[String(id)];
}
function liveApply(g, d){
  if(!d) return;
  for(const k of ['playing', 'visits', 'favs', 'like', 'votes']) if(d[k] != null) g[k] = d[k];
  if(currentGame && currentGame.id === g.id){
    const set = (k, v) => { const el = modal.querySelector(`.stat[data-k="${k}"] .v`); if(el) el.textContent = v; };
    set('now', fmtFull(g.playing)); set('visits', fmtFull(g.visits)); set('rating', g.like != null ? g.like + '%' : '—');
    set('votes', fmtFull(g.votes)); set('favs', fmtFull(g.favs));
  }
}
async function liveTick(id){
  const L = LIVE.get(id); if(!L) return;
  const g = GAMES.find(x => String(x.id) === String(id)); if(!g) return;
  try {
    const d = await liveFetch(id);
    if(d && d.playing != null){
      L.samples.push({t: Date.now(), v: d.playing});
      if(L.samples.length > 2000) L.samples.shift();
      L.last = Date.now(); L.err = false;
      liveApply(g, d);
    }
  } catch (e) { L.err = true; }
  if(L.until && Date.now() >= L.until) liveStop(id, true);
  if(currentGame && currentGame.id === g.id) renderLive(g);
}
function liveStart(g, every, dur){
  liveStop(g.id);
  const L = {every, until: dur ? Date.now() + dur * 1000 : 0, samples: [], last: 0, err: false, done: false};
  L.timer = setInterval(() => liveTick(g.id), every * 1000);
  LIVE.set(String(g.id), L);
  liveTick(g.id);
  renderLive(g);
}
function liveStop(id, finished){
  const L = LIVE.get(String(id)); if(!L) return;
  clearInterval(L.timer); L.timer = null; L.done = !!finished;
  if(!finished) LIVE.delete(String(id));
}
function liveSpark(samples){
  if(samples.length < 2) return '';
  const W = 680, H = 90, PL = 46, PR = 8, PT = 8, PB = 18;
  const t0 = samples[0].t, t1 = samples[samples.length - 1].t, span = Math.max(1, t1 - t0);
  const vs = samples.map(p => p.v), lo = Math.min(...vs), hi = Math.max(...vs), rng = Math.max(1, hi - lo);
  const x = tt => PL + (tt - t0) / span * (W - PL - PR), y = v => PT + (1 - (v - lo) / rng) * (H - PT - PB);
  const d = samples.map((p, i) => (i ? 'L' : 'M') + x(p.t).toFixed(1) + ',' + y(p.v).toFixed(1)).join(' ');
  const last = samples[samples.length - 1];
  return `<svg class="live-spark" viewBox="0 0 ${W} ${H}" aria-hidden="true">
    <line x1="${PL}" y1="${PT}" x2="${W - PR}" y2="${PT}" stroke="var(--border)"/><line x1="${PL}" y1="${H - PB}" x2="${W - PR}" y2="${H - PB}" stroke="var(--border)"/>
    <text x="${PL - 6}" y="${PT + 4}" text-anchor="end" font-size="10" font-family="IBM Plex Mono, monospace" fill="var(--text-faint)">${fmtNum(hi)}</text>
    <text x="${PL - 6}" y="${H - PB + 4}" text-anchor="end" font-size="10" font-family="IBM Plex Mono, monospace" fill="var(--text-faint)">${fmtNum(lo)}</text>
    <text x="${PL}" y="${H - 5}" font-size="10" font-family="IBM Plex Mono, monospace" fill="var(--text-faint)">${hhmmss(t0)}</text>
    <text x="${W - PR}" y="${H - 5}" text-anchor="end" font-size="10" font-family="IBM Plex Mono, monospace" fill="var(--text-faint)">${hhmmss(t1)}</text>
    <path d="${d}" fill="none" stroke="var(--good)" stroke-width="2" stroke-linejoin="round"/>
    <circle cx="${x(last.t).toFixed(1)}" cy="${y(last.v).toFixed(1)}" r="3.5" fill="var(--good)"/>
  </svg>`;
}
function renderLive(g){
  const box = document.getElementById('liveBox'); if(!box) return;
  const L = LIVE.get(String(g.id));
  const running = !!(L && L.timer);
  box.classList.toggle('on', running);
  const every = L ? L.every : (renderLive.every || 30), dur = L ? (L.until ? Math.round((L.until - (L.startAt || Date.now())) / 1000) : 0) : (renderLive.dur ?? 600);
  const ctrl = running
    ? `<button type="button" class="stop" id="liveBtn">${tl('stop')}</button>`
    : `<span class="lbl">${tl('every')}</span><select id="liveEvery">${LIVE_EVERY.map(([v, l]) => `<option value="${v}" ${v === every ? 'selected' : ''}>${l}</option>`).join('')}</select>
       <span class="lbl">${tl('for')}</span><select id="liveFor">${LIVE_FOR.map(([v, l]) => `<option value="${v}" ${v === dur ? 'selected' : ''}>${l}</option>`).join('')}</select>
       <button type="button" id="liveBtn" ${WORKER_URL ? '' : 'disabled'}>${tl('start')}</button>`;
  let body = '';
  if(!WORKER_URL) body = `<div class="live-status">${tl('needs')}</div>`;
  else if(L && L.samples.length){
    const vs = L.samples.map(p => p.v), first = vs[0], last = vs[vs.length - 1];
    const delta = last - first, dp = first ? Math.round(delta / first * 100) : 0;
    body = `<div class="live-stats">
      <div>${tl('now')} <b class="big">${fmtFull(last)}</b></div>
      <div>${tl('since')} <b class="${delta > 0 ? 'pos' : delta < 0 ? 'neg' : ''}" style="color:${delta > 0 ? 'var(--good)' : delta < 0 ? 'var(--bad)' : 'inherit'}">${delta > 0 ? '+' : ''}${fmtFull(delta)} (${dp > 0 ? '+' : ''}${dp}%)</b></div>
      <div>${tl('min')} <b>${fmtFull(Math.min(...vs))}</b></div><div>${tl('max')} <b>${fmtFull(Math.max(...vs))}</b></div>
      <div><b>${vs.length}</b> ${tl('n')}</div><div>${tl('last')} <b>${hhmmss(L.last)}</b></div>
    </div>${liveSpark(L.samples)}
    <div class="live-status ${L.err ? 'err' : ''}">${L.err ? tl('err') : running ? (L.until ? `${tl('stopsAt')} ${hhmmss(L.until)}` : tl('forever')) : tl('done')}</div>`;
  } else if(L && L.err) body = `<div class="live-status err">${tl('err')}</div>`;
  box.innerHTML = `<div class="score-head"><div><div class="t"><span class="dot"></span>${tl('title')}</div><div class="hint">${tl('hint')}</div></div><div class="live-ctrl">${ctrl}</div></div>${body}`;
  const btn = document.getElementById('liveBtn');
  if(btn) btn.addEventListener('click', () => {
    if(running){ liveStop(g.id); renderLive(g); return; }
    renderLive.every = Number(document.getElementById('liveEvery').value);
    renderLive.dur = Number(document.getElementById('liveFor').value);
    liveStart(g, renderLive.every, renderLive.dur);
  });
}

/* ---------- Discord invite ---------- */""")

open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
