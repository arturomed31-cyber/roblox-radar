"""Studios view: games grouped by owner (group or user)."""
p = 'index.html'
s = open(p, encoding='utf-8').read()

def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)

rep("</style>\n</head>", """
/* studios */
.studio-wrap{border:1px solid var(--border);border-radius:10px;overflow:auto;background:var(--panel);}
.studio-wrap table{min-width:900px;}
.studio-wrap tbody tr.st{cursor:pointer;}
.studio-wrap tbody tr.st:hover td{background:var(--panel-2);}
.studio-name{font-weight:600;display:flex;align-items:center;gap:8px;}
.studio-name .kind{font-family:'IBM Plex Mono',monospace;font-size:10px;padding:2px 6px;border-radius:4px;border:1px solid var(--border);color:var(--text-dim);white-space:nowrap;}
.studio-name .kind.group{color:var(--good);border-color:color-mix(in srgb, var(--good) 40%, transparent);}
.studio-sub{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--text-faint);margin-top:2px;}
.studio-top{font-size:12px;}
.studio-top .conc{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--text-faint);}
.studio-games td{background:var(--panel-2);padding:0 !important;}
.studio-games table{min-width:0;width:100%;}
.studio-games table td{padding:7px 12px;font-size:12.5px;border-bottom:1px solid var(--border);}
.studio-games table tr:last-child td{border-bottom:none;}
.studio-games .game-name{font-size:12.5px;}
.studio-games .cat-pill{font-size:11px;}
.studio-hint{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--text-faint);margin-top:8px;line-height:1.6;}
.chev{display:inline-block;width:14px;color:var(--text-faint);font-size:10px;transition:transform .15s;}
tr.st.open .chev{transform:rotate(90deg);}
</style>
</head>""")

rep("""      <button type="button" data-view="watch" id="watchTab"></button>
    </div>""", """      <button type="button" data-view="watch" id="watchTab"></button>
      <button type="button" data-view="studios" id="studiosTab"></button>
    </div>""")

rep("""  <footer><div id="footerNote"></div>""", """  <div id="studiosView" hidden>
    <div class="controls">
      <input id="stSearch" type="text" aria-label="Search studios">
      <select id="stMin" aria-label="Minimum games"></select>
      <select id="stOwner" aria-label="Owner type"></select>
      <select id="stSort" aria-label="Sort studios"></select>
    </div>
    <div class="share-row"><div class="count-row" id="stCount" style="margin:0;flex:1"></div><button type="button" class="share-btn" id="stShare"></button></div>
    <div class="studio-wrap"><table><thead id="sthead"></thead><tbody id="stbody"></tbody></table>
      <div class="more-row" id="stMoreRow" hidden><button class="more-btn" id="stMoreBtn" type="button"></button></div></div>
    <div class="studio-hint" id="stHint"></div>
  </div>

  <footer><div id="footerNote"></div>""")

rep("""  document.getElementById('watchView').hidden = v !== 'watch';
  if(v === 'market') renderMarket();
  if(v === 'watch') renderWatch();""", """  document.getElementById('watchView').hidden = v !== 'watch';
  document.getElementById('studiosView').hidden = v !== 'studios';
  if(v === 'market') renderMarket();
  if(v === 'watch') renderWatch();
  if(v === 'studios') renderStudios();""")

rep("""  if(view === 'watch'){ q.set('view', 'watch'); if(WATCH.size) q.set('watch', [...WATCH].join(',')); }
  const qs = q.toString();""", """  if(view === 'watch'){ q.set('view', 'watch'); if(WATCH.size) q.set('watch', [...WATCH].join(',')); }
  if(view === 'studios'){
    q.set('view', 'studios');
    if(ST.search) q.set('sq', ST.search); if(ST.min !== 2) q.set('smin', ST.min);
    if(ST.owner) q.set('sowner', ST.owner); if(ST.sort !== 'players') q.set('ssort', ST.sort);
  }
  const qs = q.toString();""")

rep("""  if(q.get('view') === 'watch'){""", """  if(q.get('view') === 'studios'){
    view = 'studios';
    ST.search = q.get('sq') || ''; ST.min = Number(q.get('smin') || 2) || 1;
    ST.owner = q.get('sowner') || ''; ST.sort = q.get('ssort') || 'players';
  }
  if(q.get('view') === 'watch'){""")

rep("""    renderWatch();
    if(currentGame) openModal(currentGame._i, currentRange);
  }
  document.getElementById('watchTab').textContent = tw('w_view') + (WATCH.size ? ` (${WATCH.size})` : '');
}""", """    renderWatch();
    renderStudios();
    if(currentGame) openModal(currentGame._i, currentRange);
  }
  document.getElementById('watchTab').textContent = tw('w_view') + (WATCH.size ? ` (${WATCH.size})` : '');
  document.getElementById('studiosTab').textContent = tst('s_view');
  buildStudioControls();
}""")

rep("""/* ---------- shareable links ---------- */""", r"""/* ---------- studios: games grouped by owner ---------- */
const STUDIO_I18N = {
  en: {s_view:'Studios', s_search:'Search studio or game…', s_min:n=>n===1?'All studios':`${n}+ games`, s_owner:'Any owner', s_group:'Groups', s_user:'User accounts',
       s_sort:{players:'Players', games:'Games', d7:'7d change', rev:'Est. earnings', members:'Group members', conc:'Least dependent on one game', new:'Newest game'},
       s_studio:'Studio', s_games:'Games', s_players:'Players', s_share:'Share', s_top:'Main game', s_d7:'7d', s_rating:'Rating', s_rev:'Est. earnings / mo', s_score:'Best score',
       s_count:(n,t,p)=>`${n} of ${t} studios · ${p} players`, s_more:n=>`Show ${n} more`, s_empty:'No studio matches.', s_of:'of their players', s_group_tag:'GROUP', s_user_tag:'USER', s_members:'members',
       s_hint:'A studio whose main game carries almost all of its players usually has smaller titles it would part with. Group-owned games can be transferred; games on a personal account cannot. Share = part of all tracked players.',
       s_share_btn:'Copy link to this view'},
  es: {s_view:'Estudios', s_search:'Buscar estudio o juego…', s_min:n=>n===1?'Todos los estudios':`${n}+ juegos`, s_owner:'Cualquier dueño', s_group:'Grupos', s_user:'Cuentas personales',
       s_sort:{players:'Jugadores', games:'Juegos', d7:'Cambio 7d', rev:'Ingresos est.', members:'Miembros del grupo', conc:'Menos dependiente de un juego', new:'Juego más reciente'},
       s_studio:'Estudio', s_games:'Juegos', s_players:'Jugadores', s_share:'Cuota', s_top:'Juego principal', s_d7:'7d', s_rating:'Valoración', s_rev:'Ingresos est. / mes', s_score:'Mejor puntaje',
       s_count:(n,t,p)=>`${n} de ${t} estudios · ${p} jugadores`, s_more:n=>`Mostrar ${n} más`, s_empty:'Ningún estudio coincide.', s_of:'de sus jugadores', s_group_tag:'GRUPO', s_user_tag:'USUARIO', s_members:'miembros',
       s_hint:'Un estudio cuyo juego principal concentra casi todos sus jugadores suele tener títulos pequeños que soltaría. Los juegos de grupo se pueden transferir; los de cuenta personal no. Cuota = parte de todos los jugadores rastreados.',
       s_share_btn:'Copiar enlace a esta vista'},
  pt: {s_view:'Estúdios', s_search:'Buscar estúdio ou jogo…', s_min:n=>n===1?'Todos os estúdios':`${n}+ jogos`, s_owner:'Qualquer dono', s_group:'Grupos', s_user:'Contas pessoais',
       s_sort:{players:'Jogadores', games:'Jogos', d7:'Variação 7d', rev:'Receita est.', members:'Membros do grupo', conc:'Menos dependente de um jogo', new:'Jogo mais recente'},
       s_studio:'Estúdio', s_games:'Jogos', s_players:'Jogadores', s_share:'Fatia', s_top:'Jogo principal', s_d7:'7d', s_rating:'Avaliação', s_rev:'Receita est. / mês', s_score:'Melhor pontuação',
       s_count:(n,t,p)=>`${n} de ${t} estúdios · ${p} jogadores`, s_more:n=>`Mostrar mais ${n}`, s_empty:'Nenhum estúdio encontrado.', s_of:'dos seus jogadores', s_group_tag:'GRUPO', s_user_tag:'USUÁRIO', s_members:'membros',
       s_hint:'Um estúdio cujo jogo principal concentra quase todos os jogadores costuma ter títulos menores que venderia. Jogos de grupo podem ser transferidos; os de conta pessoal não.',
       s_share_btn:'Copiar link desta visão'},
  fr: {s_view:'Studios', s_search:'Rechercher un studio ou un jeu…', s_min:n=>n===1?'Tous les studios':`${n}+ jeux`, s_owner:'Tout propriétaire', s_group:'Groupes', s_user:'Comptes personnels',
       s_sort:{players:'Joueurs', games:'Jeux', d7:'Variation 7j', rev:'Revenus est.', members:'Membres du groupe', conc:'Moins dépendant d’un jeu', new:'Jeu le plus récent'},
       s_studio:'Studio', s_games:'Jeux', s_players:'Joueurs', s_share:'Part', s_top:'Jeu principal', s_d7:'7j', s_rating:'Note', s_rev:'Revenus est. / mois', s_score:'Meilleur score',
       s_count:(n,t,p)=>`${n} sur ${t} studios · ${p} joueurs`, s_more:n=>`Afficher ${n} de plus`, s_empty:'Aucun studio ne correspond.', s_of:'de leurs joueurs', s_group_tag:'GROUPE', s_user_tag:'UTILISATEUR', s_members:'membres',
       s_hint:'Un studio dont le jeu principal concentre presque tous ses joueurs a souvent de petits titres dont il se séparerait. Les jeux de groupe sont transférables ; ceux d’un compte personnel non.',
       s_share_btn:'Copier le lien de cette vue'},
  de: {s_view:'Studios', s_search:'Studio oder Spiel suchen…', s_min:n=>n===1?'Alle Studios':`${n}+ Spiele`, s_owner:'Beliebiger Besitzer', s_group:'Gruppen', s_user:'Privatkonten',
       s_sort:{players:'Spieler', games:'Spiele', d7:'7T-Änderung', rev:'Gesch. Einnahmen', members:'Gruppenmitglieder', conc:'Am wenigsten abhängig von einem Spiel', new:'Neuestes Spiel'},
       s_studio:'Studio', s_games:'Spiele', s_players:'Spieler', s_share:'Anteil', s_top:'Hauptspiel', s_d7:'7T', s_rating:'Bewertung', s_rev:'Gesch. Einnahmen / Monat', s_score:'Bester Score',
       s_count:(n,t,p)=>`${n} von ${t} Studios · ${p} Spieler`, s_more:n=>`${n} weitere anzeigen`, s_empty:'Kein Studio passt.', s_of:'ihrer Spieler', s_group_tag:'GRUPPE', s_user_tag:'NUTZER', s_members:'Mitglieder',
       s_hint:'Ein Studio, dessen Hauptspiel fast alle Spieler trägt, hat meist kleinere Titel, die es abgeben würde. Gruppenspiele sind übertragbar, Spiele auf Privatkonten nicht.',
       s_share_btn:'Link zu dieser Ansicht kopieren'},
  it: {s_view:'Studi', s_search:'Cerca studio o gioco…', s_min:n=>n===1?'Tutti gli studi':`${n}+ giochi`, s_owner:'Qualsiasi proprietario', s_group:'Gruppi', s_user:'Account personali',
       s_sort:{players:'Giocatori', games:'Giochi', d7:'Variazione 7g', rev:'Ricavi stimati', members:'Membri del gruppo', conc:'Meno dipendente da un gioco', new:'Gioco più recente'},
       s_studio:'Studio', s_games:'Giochi', s_players:'Giocatori', s_share:'Quota', s_top:'Gioco principale', s_d7:'7g', s_rating:'Valutazione', s_rev:'Ricavi stimati / mese', s_score:'Miglior punteggio',
       s_count:(n,t,p)=>`${n} di ${t} studi · ${p} giocatori`, s_more:n=>`Mostra altri ${n}`, s_empty:'Nessuno studio corrisponde.', s_of:'dei loro giocatori', s_group_tag:'GRUPPO', s_user_tag:'UTENTE', s_members:'membri',
       s_hint:'Uno studio il cui gioco principale concentra quasi tutti i giocatori di solito ha titoli minori di cui si libererebbe. I giochi di gruppo sono trasferibili; quelli su account personale no.',
       s_share_btn:'Copia link a questa vista'},
  ru: {s_view:'Студии', s_search:'Поиск студии или игры…', s_min:n=>n===1?'Все студии':`${n}+ игр`, s_owner:'Любой владелец', s_group:'Группы', s_user:'Личные аккаунты',
       s_sort:{players:'Игроки', games:'Игры', d7:'Изменение за 7 дн.', rev:'Оценка дохода', members:'Участники группы', conc:'Меньше всего зависит от одной игры', new:'Самая новая игра'},
       s_studio:'Студия', s_games:'Игры', s_players:'Игроки', s_share:'Доля', s_top:'Главная игра', s_d7:'7д', s_rating:'Рейтинг', s_rev:'Оценка дохода / мес', s_score:'Лучший балл',
       s_count:(n,t,p)=>`${n} из ${t} студий · ${p} игроков`, s_more:n=>`Показать ещё ${n}`, s_empty:'Ни одна студия не подходит.', s_of:'их игроков', s_group_tag:'ГРУППА', s_user_tag:'ПОЛЬЗОВАТЕЛЬ', s_members:'участников',
       s_hint:'Студия, у которой почти все игроки в одной игре, обычно готова расстаться с мелкими проектами. Игры групп можно передать, игры на личном аккаунте — нет.',
       s_share_btn:'Скопировать ссылку на этот вид'},
  ja: {s_view:'スタジオ', s_search:'スタジオまたはゲームを検索…', s_min:n=>n===1?'すべてのスタジオ':`${n}本以上`, s_owner:'すべての所有者', s_group:'グループ', s_user:'個人アカウント',
       s_sort:{players:'プレイヤー', games:'ゲーム数', d7:'7日変化', rev:'推定収益', members:'グループ人数', conc:'1本への依存が少ない順', new:'最新のゲーム'},
       s_studio:'スタジオ', s_games:'ゲーム', s_players:'プレイヤー', s_share:'シェア', s_top:'主力ゲーム', s_d7:'7日', s_rating:'評価', s_rev:'推定収益 / 月', s_score:'最高スコア',
       s_count:(n,t,p)=>`${t} 中 ${n} スタジオ · ${p} プレイヤー`, s_more:n=>`さらに ${n} 件`, s_empty:'該当するスタジオはありません。', s_of:'のプレイヤーを占有', s_group_tag:'グループ', s_user_tag:'ユーザー', s_members:'人',
       s_hint:'主力ゲームにプレイヤーが集中しているスタジオは、小さなタイトルを手放すことが多いです。グループ所有のゲームは譲渡可能、個人アカウントのゲームは不可。',
       s_share_btn:'この表示へのリンクをコピー'}
};
const tst = k => (STUDIO_I18N[settings.lang] || STUDIO_I18N.en)[k] ?? STUDIO_I18N.en[k];
const ST = {search:'', min:2, owner:'', sort:'players', shown:60, open:new Set()};
let STUDIOS = null;
function buildStudios(){
  const by = new Map();
  GAMES.forEach(g => {
    const key = g.cUrl || ('name:' + g.creator);
    let s = by.get(key);
    if(!s){ s = {key, name:g.creator || t('unknown'), type:g.cType, url:g.cUrl, verified:!!g.verified, games:[]}; by.set(key, s); }
    s.games.push(g);
    if(g.verified) s.verified = true;
  });
  const total = GAMES.reduce((a,g) => a + (g.playing||0), 0);
  const list = [...by.values()].map(s => {
    s.games.sort((a,b) => (b.playing||0) - (a.playing||0));
    s.n = s.games.length;
    s.players = s.games.reduce((a,g) => a + (g.playing||0), 0);
    s.share = total ? s.players / total * 100 : 0;
    s.top = s.games[0];
    s.conc = s.players ? (s.top.playing||0) / s.players * 100 : 100;
    // 7d change weighted by players: compare the summed current count with the summed count a week ago
    let cur = 0, prev = 0;
    s.games.forEach(g => { if(g.d7 != null && g.playing){ cur += g.playing; prev += g.playing / (1 + g.d7/100); } });
    s.d7 = prev > 0 ? (cur / prev - 1) * 100 : null;
    const rated = s.games.filter(g => g.like != null && g.playing);
    s.rating = rated.length ? Math.round(rated.reduce((a,g) => a + g.like * g.playing, 0) / rated.reduce((a,g) => a + g.playing, 0)) : null;
    s.rev = s.games.some(g => g.rev != null) ? s.games.reduce((a,g) => a + (g.rev||0), 0) : null;
    s.score = Math.max(...s.games.map(g => g.score||0));
    s.members = (s.games.find(g => g.grp && g.grp.m != null) || {grp:{m:null}}).grp.m;
    s.newest = Math.min(...s.games.map(g => g.age ?? Infinity));
    s.search = (s.name + ' ' + s.games.map(g => g.name).join(' ')).toLowerCase();
    return s;
  });
  return list;
}
function buildStudioControls(){
  const min = document.getElementById('stMin');
  min.innerHTML = [1,2,3,5,10].map(n => `<option value="${n}">${tst('s_min')(n)}</option>`).join('');
  min.value = String([1,2,3,5,10].includes(ST.min) ? ST.min : 2);
  const own = document.getElementById('stOwner');
  own.innerHTML = `<option value="">${tst('s_owner')}</option><option value="Group">${tst('s_group')}</option><option value="User">${tst('s_user')}</option>`;
  own.value = ST.owner;
  const sort = document.getElementById('stSort');
  const so = tst('s_sort');
  sort.innerHTML = Object.keys(so).map(k => `<option value="${k}">${so[k]}</option>`).join('');
  sort.value = so[ST.sort] ? ST.sort : 'players';
  const se = document.getElementById('stSearch');
  se.placeholder = tst('s_search'); se.value = ST.search;
  document.getElementById('stShare').textContent = tst('s_share_btn');
  document.getElementById('stHint').textContent = tst('s_hint');
}
function studioRows(){
  let rows = STUDIOS.filter(s => s.n >= ST.min);
  if(ST.owner) rows = rows.filter(s => s.type === ST.owner);
  if(ST.search){ const q = ST.search.toLowerCase(); rows = rows.filter(s => s.search.includes(q)); }
  const miss = -Infinity;
  const key = {players:s=>s.players, games:s=>s.n, d7:s=>s.d7 ?? miss, rev:s=>s.rev ?? miss, members:s=>s.members ?? miss, conc:s=>-s.conc, new:s=>-(s.newest === Infinity ? 1e9 : s.newest)}[ST.sort] || (s=>s.players);
  return rows.sort((a,b) => key(b) - key(a) || b.players - a.players);
}
function studioGamesHtml(s){
  return `<tr class="studio-games"><td colspan="10"><table><tbody>${s.games.map(g => `<tr>
    <td style="width:44px">${imgHtml(g, 32)}</td>
    <td><button class="game-name" data-open="${g._i}">${esc(g.name)}</button> ${trendBadge(g.trend)}</td>
    <td><span class="cat-pill">${catLabel(g.cat)}</span></td>
    <td><div class="tagset">${g.tags.slice(0,3).map(tagHtml).join('')}</div></td>
    <td class="num">${fmtTable(g.playing)}</td>
    <td class="num">${deltaHtml(g.d7)}</td>
    <td class="age">${fmtAge(g.age)}</td>
    <td class="num"><span class="score-pill ${scoreClass(g.score)}">${g.score}</span></td>
  </tr>`).join('')}</tbody></table></td></tr>`;
}
function renderStudios(){
  if(!GAMES.length || view !== 'studios') return;
  if(!STUDIOS) STUDIOS = buildStudios();
  syncUrl();
  const rows = studioRows();
  const players = rows.reduce((a,s) => a + s.players, 0);
  document.getElementById('stCount').textContent = tst('s_count')(rows.length, STUDIOS.length, fmtNum(players));
  document.getElementById('sthead').innerHTML = `<tr><th style="width:14px"></th><th>${tst('s_studio')}</th><th style="text-align:right">${tst('s_games')}</th><th style="text-align:right">${tst('s_players')}</th>
    <th>${tst('s_share')}</th><th>${tst('s_top')}</th><th style="text-align:right">${tst('s_d7')}</th><th style="text-align:right">${tst('s_rating')}</th>
    <th style="text-align:right">${tst('s_rev')}</th><th style="text-align:right">${tst('s_score')}</th></tr>`;
  const body = document.getElementById('stbody');
  if(!rows.length){ body.innerHTML = `<tr><td colspan="10"><div class="empty-state">${tst('s_empty')}</div></td></tr>`; document.getElementById('stMoreRow').hidden = true; return; }
  const maxShare = Math.max(...rows.map(s => s.share), 0.01);
  body.innerHTML = rows.slice(0, ST.shown).map(s => {
    const open = ST.open.has(s.key);
    const topName = s.top.name.length > 34 ? s.top.name.slice(0,33) + '…' : s.top.name;
    return `<tr class="st ${open ? 'open' : ''}" data-key="${esc(s.key)}">
      <td><span class="chev">▶</span></td>
      <td><div class="studio-name"><span>${esc(s.name)}${s.verified ? ' ✓' : ''}</span><span class="kind ${s.type === 'Group' ? 'group' : ''}">${s.type === 'Group' ? tst('s_group_tag') : tst('s_user_tag')}</span></div>
        <div class="studio-sub">${s.members != null ? fmtTable(s.members) + ' ' + tst('s_members') : ''}</div></td>
      <td class="num">${s.n}</td>
      <td class="num">${fmtTable(s.players)}</td>
      <td><div class="bar" title="${s.share.toFixed(2)}%"><i style="width:${(s.share/maxShare*100).toFixed(1)}%"></i></div><span class="market-sub">${s.share < 0.1 ? '<0.1' : s.share.toFixed(1)}%</span></td>
      <td class="studio-top"><button class="game-name" data-open="${s.top._i}">${esc(topName)}</button><div class="conc">${Math.round(s.conc)}% ${tst('s_of')}</div></td>
      <td class="num">${deltaHtml(s.d7)}</td>
      <td class="rating ${ratingClass(s.rating)}">${s.rating != null ? s.rating + '%' : '—'}</td>
      <td class="num">${s.rev != null ? '$' + fmtNum(s.rev) : '—'}</td>
      <td class="num"><span class="score-pill ${scoreClass(s.score)}">${s.score}</span></td>
    </tr>${open ? studioGamesHtml(s) : ''}`;
  }).join('');
  const more = document.getElementById('stMoreRow');
  more.hidden = rows.length <= ST.shown;
  document.getElementById('stMoreBtn').textContent = tst('s_more')(Math.min(60, rows.length - ST.shown));
}
document.getElementById('stbody').addEventListener('click', e => {
  const op = e.target.closest('[data-open]');
  if(op){ openModal(Number(op.dataset.open)); return; }
  const tr = e.target.closest('tr.st');
  if(!tr) return;
  const k = tr.dataset.key;
  if(ST.open.has(k)) ST.open.delete(k); else ST.open.add(k);
  renderStudios();
});
document.getElementById('stSearch').addEventListener('input', e => { ST.search = e.target.value; ST.shown = 60; renderStudios(); });
document.getElementById('stMin').addEventListener('change', e => { ST.min = Number(e.target.value); ST.shown = 60; renderStudios(); });
document.getElementById('stOwner').addEventListener('change', e => { ST.owner = e.target.value; ST.shown = 60; renderStudios(); });
document.getElementById('stSort').addEventListener('change', e => { ST.sort = e.target.value; ST.shown = 60; renderStudios(); });
document.getElementById('stMoreBtn').addEventListener('click', () => { ST.shown += 60; renderStudios(); });
document.getElementById('stShare').addEventListener('click', e => copyText(buildUrl(null), e.currentTarget));

/* ---------- shareable links ---------- */""")

open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
