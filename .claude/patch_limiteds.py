"""Limiteds tab: table, filters, item window with RAP/price chart. Data loads when the tab opens."""
p = 'index.html'
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

# ---------- CSS ----------
rep("</style>\n</head>", """
/* limiteds */
.lim-wrap{border:1px solid var(--border);border-radius:10px;overflow:auto;background:var(--panel);max-height:74vh;}
.lim-wrap table{min-width:1000px;}
.lim-item{display:flex;align-items:center;gap:10px;}
.lim-item img{width:40px;height:40px;border-radius:8px;background:var(--panel-2);border:1px solid var(--border);object-fit:cover;flex:none;}
.lim-item .nm{font-weight:600;font-size:13px;max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;background:none;border:none;padding:0;color:var(--text);font-family:inherit;cursor:pointer;text-align:left;}
.lim-item .nm:hover{color:var(--accent);}
.lim-item .sub{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--text-faint);}
.lvl{font-family:'IBM Plex Mono',monospace;font-size:10.5px;padding:2px 7px;border-radius:5px;white-space:nowrap;border:1px solid transparent;}
.lvl.l0{background:color-mix(in srgb,var(--risk) 15%,transparent);color:var(--risk);} .lvl.l1{background:color-mix(in srgb,var(--warn) 15%,transparent);color:var(--warn);}
.lvl.l2{background:var(--chip);color:var(--text-dim);} .lvl.l3{background:color-mix(in srgb,var(--good) 15%,transparent);color:var(--good);} .lvl.l4{background:color-mix(in srgb,var(--accent) 15%,transparent);color:var(--accent);}
.lvl.none{color:var(--text-faint);}
.flag{font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:700;letter-spacing:.05em;padding:1px 6px;border-radius:4px;margin-right:3px;}
.flag.proj{background:color-mix(in srgb,var(--risk) 18%,transparent);color:var(--risk);} .flag.hyped{background:color-mix(in srgb,var(--warn) 18%,transparent);color:var(--warn);} .flag.rare{background:color-mix(in srgb,var(--accent) 18%,transparent);color:var(--accent);}
.lim-credit{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--text-faint);margin-top:8px;line-height:1.6;}
.lim-credit a{color:var(--accent);}
.premium{font-family:'IBM Plex Mono',monospace;}
.premium.hi{color:var(--good);} .premium.lo{color:var(--risk);}
@media (max-width:700px){ .lim-wrap{max-height:none;} }
</style>
</head>""")

# ---------- HTML ----------
rep("""      <button type="button" data-view="studios" id="studiosTab"></button>
    </div>""", """      <button type="button" data-view="studios" id="studiosTab"></button>
      <button type="button" data-view="limiteds" id="limTab"></button>
    </div>""")
rep("""  <footer><div id="footerNote"></div>""", """  <div id="limView" hidden>
    <div class="controls">
      <input id="limSearch" type="text" aria-label="Search limiteds">
      <select id="limDemand" aria-label="Demand"></select>
      <select id="limTrend" aria-label="Trend"></select>
      <select id="limFlag" aria-label="Flags"></select>
      <select id="limSort" aria-label="Sort"></select>
    </div>
    <div class="share-row"><div class="count-row" id="limCount" style="margin:0;flex:1"></div><button type="button" class="share-btn" id="limShare"></button></div>
    <div class="lim-wrap"><table><thead id="limHead"></thead><tbody id="limBody"></tbody></table>
      <div class="more-row" id="limMoreRow" hidden><button class="more-btn" id="limMoreBtn" type="button"></button></div></div>
    <div class="lim-credit" id="limCredit"></div>
  </div>

  <footer><div id="footerNote"></div>""")

# ---------- view switching / url / language ----------
rep("""  document.getElementById('studiosView').hidden = v !== 'studios';
  if(v === 'market') renderMarket();""", """  document.getElementById('studiosView').hidden = v !== 'studios';
  document.getElementById('limView').hidden = v !== 'limiteds';
  if(v === 'limiteds') loadLimiteds().then(renderLimiteds);
  if(v === 'market') renderMarket();""")
rep("""  if(view === 'studios'){
    q.set('view', 'studios');""", """  if(view === 'limiteds'){
    q.set('view', 'limiteds');
    if(LM.search) q.set('lq', LM.search); if(LM.demand !== '') q.set('ldemand', LM.demand); if(LM.trend !== '') q.set('ltrend', LM.trend);
    if(LM.flag) q.set('lflag', LM.flag); if(LM.sort !== 'rap') q.set('lsort', LM.sort);
    if(currentItem) q.set('item', currentItem.id);
  }
  if(view === 'studios'){
    q.set('view', 'studios');""")
rep("""  if(q.get('view') === 'studios'){""", """  if(q.get('view') === 'limiteds'){
    view = 'limiteds';
    LM.search = q.get('lq') || ''; LM.demand = q.get('ldemand') ?? ''; LM.trend = q.get('ltrend') ?? ''; LM.flag = q.get('lflag') || ''; LM.sort = q.get('lsort') || 'rap';
    LM.openItem = q.get('item');
  }
  if(q.get('view') === 'studios'){""")
rep("""  document.getElementById('studiosTab').textContent = tst('s_view');
  buildStudioControls();
}""", """  document.getElementById('studiosTab').textContent = tst('s_view');
  buildStudioControls();
  document.getElementById('limTab').textContent = tl2('view');
  buildLimControls();
  if(LIM && view === 'limiteds') renderLimiteds();
}""")

# ---------- JS module ----------
rep("""/* ---------- shareable links ---------- */""", r"""/* ---------- limiteds ---------- */
const LIM_I18N = {
  en:{view:'Limiteds', search:'Search item or acronym…', item:'Item', price:'Best price', rap:'RAP', value:'Value', ratio:'Value / RAP', d1:'24h', d7:'7d', demand:'Demand', trend:'Trend', flags:'Flags', qty:'Quantity', favs:'Favorites',
      dAny:'Any demand', tAny:'Any trend', fAny:'Any flag', fProj:'Projected', fNoProj:'Not projected', fHyped:'Hyped', fRare:'Rare', fValued:'Has a value',
      demandL:['Terrible','Low','Normal','High','Amazing'], trendL:['Lowering','Unstable','Stable','Raising','Fluctuating'], none:'—',
      sort:{rap:'RAP', value:'Value', price:'Best price ↓', priceAsc:'Best price ↑', d1:'24h change', d7:'7d change', favs:'Favorites', qty:'Quantity ↑', ratio:'Value / RAP', name:'Name A→Z'},
      count:(n,t)=>`${n} of ${t} limiteds`, more:n=>`Show ${n} more`, empty:'No limited matches.', loading:'Loading limiteds…', err:'Could not load limiteds.',
      credit:'RAP, value, demand, trend and projected/hyped/rare flags by <a href="https://www.rolimons.com" target="_blank" rel="noopener">Rolimons</a>; best price, quantity and favorites from the Roblox catalog. Read every 6 hours. Estimates can be wrong — verify before trading.',
      created:'Released', type:'Type', creator:'Creator', openRoblox:'Open in catalog', rolimons:'Rolimons page', chart:'RAP and best price', share:'Copy link to this view',
      ratioHint:'Value above RAP = community prices it higher than recent sales; below = the reverse.', chRap:'RAP', chPrice:'Best price'},
  es:{view:'Limiteds', search:'Buscar ítem o acrónimo…', item:'Ítem', price:'Mejor precio', rap:'RAP', value:'Valor', ratio:'Valor / RAP', d1:'24h', d7:'7d', demand:'Demanda', trend:'Tendencia', flags:'Marcas', qty:'Cantidad', favs:'Favoritos',
      dAny:'Cualquier demanda', tAny:'Cualquier tendencia', fAny:'Cualquier marca', fProj:'Projected', fNoProj:'No projected', fHyped:'Hyped', fRare:'Rare', fValued:'Con valor',
      demandL:['Terrible','Baja','Normal','Alta','Increíble'], trendL:['Bajando','Inestable','Estable','Subiendo','Fluctuando'], none:'—',
      sort:{rap:'RAP', value:'Valor', price:'Mejor precio ↓', priceAsc:'Mejor precio ↑', d1:'Cambio 24h', d7:'Cambio 7d', favs:'Favoritos', qty:'Cantidad ↑', ratio:'Valor / RAP', name:'Nombre A→Z'},
      count:(n,t)=>`${n} de ${t} limiteds`, more:n=>`Mostrar ${n} más`, empty:'Ningún limited coincide.', loading:'Cargando limiteds…', err:'No se pudieron cargar los limiteds.',
      credit:'RAP, valor, demanda, tendencia y marcas projected/hyped/rare de <a href="https://www.rolimons.com" target="_blank" rel="noopener">Rolimons</a>; mejor precio, cantidad y favoritos del catálogo de Roblox. Lectura cada 6 horas. Las estimaciones pueden fallar: verifica antes de comerciar.',
      created:'Lanzado', type:'Tipo', creator:'Creador', openRoblox:'Abrir en el catálogo', rolimons:'Página en Rolimons', chart:'RAP y mejor precio', share:'Copiar enlace a esta vista',
      ratioHint:'Valor por encima del RAP = la comunidad lo cotiza más alto que las ventas recientes; por debajo, al revés.', chRap:'RAP', chPrice:'Mejor precio'},
  pt:{view:'Limiteds', search:'Buscar item ou sigla…', item:'Item', price:'Melhor preço', rap:'RAP', value:'Valor', ratio:'Valor / RAP', d1:'24h', d7:'7d', demand:'Demanda', trend:'Tendência', flags:'Marcas', qty:'Quantidade', favs:'Favoritos',
      dAny:'Qualquer demanda', tAny:'Qualquer tendência', fAny:'Qualquer marca', fProj:'Projected', fNoProj:'Não projected', fHyped:'Hyped', fRare:'Rare', fValued:'Com valor',
      demandL:['Terrível','Baixa','Normal','Alta','Incrível'], trendL:['Caindo','Instável','Estável','Subindo','Flutuando'], none:'—',
      sort:{rap:'RAP', value:'Valor', price:'Melhor preço ↓', priceAsc:'Melhor preço ↑', d1:'Variação 24h', d7:'Variação 7d', favs:'Favoritos', qty:'Quantidade ↑', ratio:'Valor / RAP', name:'Nome A→Z'},
      count:(n,t)=>`${n} de ${t} limiteds`, more:n=>`Mostrar mais ${n}`, empty:'Nenhum limited encontrado.', loading:'Carregando limiteds…', err:'Não foi possível carregar.',
      credit:'RAP, valor, demanda, tendência e marcas por <a href="https://www.rolimons.com" target="_blank" rel="noopener">Rolimons</a>; melhor preço, quantidade e favoritos do catálogo Roblox. Leitura a cada 6 horas. Verifique antes de negociar.',
      created:'Lançado', type:'Tipo', creator:'Criador', openRoblox:'Abrir no catálogo', rolimons:'Página no Rolimons', chart:'RAP e melhor preço', share:'Copiar link desta visão',
      ratioHint:'Valor acima do RAP = a comunidade cota mais alto que as vendas recentes; abaixo, o contrário.', chRap:'RAP', chPrice:'Melhor preço'},
  fr:{view:'Limiteds', search:'Rechercher un objet ou un sigle…', item:'Objet', price:'Meilleur prix', rap:'RAP', value:'Valeur', ratio:'Valeur / RAP', d1:'24h', d7:'7j', demand:'Demande', trend:'Tendance', flags:'Marques', qty:'Quantité', favs:'Favoris',
      dAny:'Toute demande', tAny:'Toute tendance', fAny:'Toute marque', fProj:'Projected', fNoProj:'Non projected', fHyped:'Hyped', fRare:'Rare', fValued:'Avec valeur',
      demandL:['Terrible','Faible','Normale','Forte','Énorme'], trendL:['En baisse','Instable','Stable','En hausse','Fluctuante'], none:'—',
      sort:{rap:'RAP', value:'Valeur', price:'Meilleur prix ↓', priceAsc:'Meilleur prix ↑', d1:'Variation 24h', d7:'Variation 7j', favs:'Favoris', qty:'Quantité ↑', ratio:'Valeur / RAP', name:'Nom A→Z'},
      count:(n,t)=>`${n} sur ${t} limiteds`, more:n=>`Afficher ${n} de plus`, empty:'Aucun limited ne correspond.', loading:'Chargement…', err:'Chargement impossible.',
      credit:'RAP, valeur, demande, tendance et marques par <a href="https://www.rolimons.com" target="_blank" rel="noopener">Rolimons</a> ; meilleur prix, quantité et favoris du catalogue Roblox. Lecture toutes les 6 heures. Vérifiez avant d’échanger.',
      created:'Sorti', type:'Type', creator:'Créateur', openRoblox:'Ouvrir dans le catalogue', rolimons:'Page Rolimons', chart:'RAP et meilleur prix', share:'Copier le lien de cette vue',
      ratioHint:'Valeur au-dessus du RAP = la communauté le cote plus haut que les ventes récentes ; en dessous, l’inverse.', chRap:'RAP', chPrice:'Meilleur prix'},
  de:{view:'Limiteds', search:'Item oder Kürzel suchen…', item:'Item', price:'Bester Preis', rap:'RAP', value:'Wert', ratio:'Wert / RAP', d1:'24h', d7:'7T', demand:'Nachfrage', trend:'Trend', flags:'Marker', qty:'Anzahl', favs:'Favoriten',
      dAny:'Jede Nachfrage', tAny:'Jeder Trend', fAny:'Jeder Marker', fProj:'Projected', fNoProj:'Nicht projected', fHyped:'Hyped', fRare:'Rare', fValued:'Mit Wert',
      demandL:['Miserabel','Niedrig','Normal','Hoch','Enorm'], trendL:['Fallend','Instabil','Stabil','Steigend','Schwankend'], none:'—',
      sort:{rap:'RAP', value:'Wert', price:'Bester Preis ↓', priceAsc:'Bester Preis ↑', d1:'24h-Änderung', d7:'7T-Änderung', favs:'Favoriten', qty:'Anzahl ↑', ratio:'Wert / RAP', name:'Name A→Z'},
      count:(n,t)=>`${n} von ${t} Limiteds`, more:n=>`${n} weitere anzeigen`, empty:'Kein Limited passt.', loading:'Lade Limiteds…', err:'Limiteds konnten nicht geladen werden.',
      credit:'RAP, Wert, Nachfrage, Trend und Marker von <a href="https://www.rolimons.com" target="_blank" rel="noopener">Rolimons</a>; bester Preis, Anzahl und Favoriten aus dem Roblox-Katalog. Alle 6 Stunden gelesen. Vor dem Handel prüfen.',
      created:'Erschienen', type:'Typ', creator:'Ersteller', openRoblox:'Im Katalog öffnen', rolimons:'Rolimons-Seite', chart:'RAP und bester Preis', share:'Link zu dieser Ansicht kopieren',
      ratioHint:'Wert über RAP = die Community bewertet höher als jüngste Verkäufe; darunter umgekehrt.', chRap:'RAP', chPrice:'Bester Preis'},
  it:{view:'Limiteds', search:'Cerca oggetto o sigla…', item:'Oggetto', price:'Miglior prezzo', rap:'RAP', value:'Valore', ratio:'Valore / RAP', d1:'24h', d7:'7g', demand:'Domanda', trend:'Tendenza', flags:'Marcatori', qty:'Quantità', favs:'Preferiti',
      dAny:'Qualsiasi domanda', tAny:'Qualsiasi tendenza', fAny:'Qualsiasi marcatore', fProj:'Projected', fNoProj:'Non projected', fHyped:'Hyped', fRare:'Rare', fValued:'Con valore',
      demandL:['Pessima','Bassa','Normale','Alta','Enorme'], trendL:['In calo','Instabile','Stabile','In salita','Fluttuante'], none:'—',
      sort:{rap:'RAP', value:'Valore', price:'Miglior prezzo ↓', priceAsc:'Miglior prezzo ↑', d1:'Variazione 24h', d7:'Variazione 7g', favs:'Preferiti', qty:'Quantità ↑', ratio:'Valore / RAP', name:'Nome A→Z'},
      count:(n,t)=>`${n} di ${t} limiteds`, more:n=>`Mostra altri ${n}`, empty:'Nessun limited corrisponde.', loading:'Caricamento…', err:'Impossibile caricare.',
      credit:'RAP, valore, domanda, tendenza e marcatori da <a href="https://www.rolimons.com" target="_blank" rel="noopener">Rolimons</a>; miglior prezzo, quantità e preferiti dal catalogo Roblox. Lettura ogni 6 ore. Verifica prima di scambiare.',
      created:'Uscito', type:'Tipo', creator:'Creatore', openRoblox:'Apri nel catalogo', rolimons:'Pagina Rolimons', chart:'RAP e miglior prezzo', share:'Copia link a questa vista',
      ratioHint:'Valore sopra il RAP = la community lo quota più delle vendite recenti; sotto, il contrario.', chRap:'RAP', chPrice:'Miglior prezzo'},
  ru:{view:'Лимитки', search:'Поиск предмета или аббревиатуры…', item:'Предмет', price:'Лучшая цена', rap:'RAP', value:'Value', ratio:'Value / RAP', d1:'24ч', d7:'7д', demand:'Спрос', trend:'Тренд', flags:'Метки', qty:'Количество', favs:'Избранное',
      dAny:'Любой спрос', tAny:'Любой тренд', fAny:'Любая метка', fProj:'Projected', fNoProj:'Не projected', fHyped:'Hyped', fRare:'Rare', fValued:'С value',
      demandL:['Ужасный','Низкий','Обычный','Высокий','Огромный'], trendL:['Падает','Нестабильный','Стабильный','Растёт','Колеблется'], none:'—',
      sort:{rap:'RAP', value:'Value', price:'Лучшая цена ↓', priceAsc:'Лучшая цена ↑', d1:'Изменение 24ч', d7:'Изменение 7д', favs:'Избранное', qty:'Количество ↑', ratio:'Value / RAP', name:'Имя A→Z'},
      count:(n,t)=>`${n} из ${t} лимиток`, more:n=>`Показать ещё ${n}`, empty:'Ничего не найдено.', loading:'Загрузка…', err:'Не удалось загрузить.',
      credit:'RAP, value, спрос, тренд и метки — <a href="https://www.rolimons.com" target="_blank" rel="noopener">Rolimons</a>; лучшая цена, количество и избранное — каталог Roblox. Чтение каждые 6 часов. Проверяйте перед сделкой.',
      created:'Выпущен', type:'Тип', creator:'Создатель', openRoblox:'Открыть в каталоге', rolimons:'Страница Rolimons', chart:'RAP и лучшая цена', share:'Скопировать ссылку на этот вид',
      ratioHint:'Value выше RAP = сообщество оценивает дороже недавних продаж; ниже — наоборот.', chRap:'RAP', chPrice:'Лучшая цена'},
  ja:{view:'リミテッド', search:'アイテム名または略称で検索…', item:'アイテム', price:'最安値', rap:'RAP', value:'Value', ratio:'Value / RAP', d1:'24h', d7:'7d', demand:'需要', trend:'トレンド', flags:'フラグ', qty:'数量', favs:'お気に入り',
      dAny:'すべての需要', tAny:'すべてのトレンド', fAny:'すべてのフラグ', fProj:'Projected', fNoProj:'Projected以外', fHyped:'Hyped', fRare:'Rare', fValued:'Valueあり',
      demandL:['最悪','低い','普通','高い','非常に高い'], trendL:['下落','不安定','安定','上昇','変動'], none:'—',
      sort:{rap:'RAP', value:'Value', price:'最安値 ↓', priceAsc:'最安値 ↑', d1:'24h変化', d7:'7d変化', favs:'お気に入り', qty:'数量 ↑', ratio:'Value / RAP', name:'名前 A→Z'},
      count:(n,t)=>`${t} 件中 ${n} 件`, more:n=>`さらに ${n} 件`, empty:'該当なし。', loading:'読み込み中…', err:'読み込めませんでした。',
      credit:'RAP・Value・需要・トレンド・フラグは <a href="https://www.rolimons.com" target="_blank" rel="noopener">Rolimons</a>、最安値・数量・お気に入りはRobloxカタログより。6時間ごとに取得。取引前に確認してください。',
      created:'発売', type:'種類', creator:'制作者', openRoblox:'カタログで開く', rolimons:'Rolimonsページ', chart:'RAPと最安値', share:'この表示へのリンクをコピー',
      ratioHint:'ValueがRAPより高い＝コミュニティは直近の売買より高く評価。低い場合は逆。', chRap:'RAP', chPrice:'最安値'}
};
const tl2 = k => (LIM_I18N[settings.lang] || LIM_I18N.en)[k] ?? LIM_I18N.en[k];
const LM = {search:'', demand:'', trend:'', flag:'', sort:'rap', shown:100, openItem:null};
let LIM = null, LIM_HIST = null, LIM_MS = [], currentItem = null, limRange = 'all';
async function loadLimiteds(){
  if(LIM) return;
  const body = document.getElementById('limBody');
  body.innerHTML = `<tr><td colspan="12"><div class="loading">${tl2('loading')}</div></td></tr>`;
  try {
    const bust = '?v=' + Math.floor(Date.now() / 3600e3);
    const [d, h] = await Promise.all([fetch('data/limiteds.json' + bust).then(r => r.json()), fetch('data/limiteds_history.json' + bust).then(r => r.ok ? r.json() : {times:[], rap:{}, price:{}})]);
    LIM_HIST = h; LIM_MS = (h.times || []).map(x => new Date(x).getTime());
    LIM = d.items.map(it => {
      it.d1 = limChange(it.id, 1); it.d7 = limChange(it.id, 7);
      it.ratio = it.value && it.rap ? it.value / it.rap : null;
      it.search = (it.name + ' ' + (it.acr || '')).toLowerCase();
      return it;
    });
    LIM.generated = d.generated;
  } catch (e) { body.innerHTML = `<tr><td colspan="12"><div class="loading">${tl2('err')}</div></td></tr>`; LIM = null; }
}
function limSeries(id, key){
  const s = ((LIM_HIST || {})[key] || {})[String(id)] || [];
  return s.map((v, i) => ({t: LIM_MS[i], v})).filter(p => p.v != null && p.t);
}
function limChange(id, days){
  const s = limSeries(id, 'rap');
  if(s.length < 2) return null;
  const last = s[s.length-1], target = last.t - days * 86400e3;
  let best = null;
  for(const p of s){ if(p.t <= target + 3 * 3600e3 && (!best || Math.abs(p.t - target) < Math.abs(best.t - target))) best = p; }
  if(!best || best === last || !best.v) return null;
  return (last.v - best.v) / best.v * 100;
}
const lvlHtml = (n, labels) => n == null ? `<span class="lvl none">${tl2('none')}</span>` : `<span class="lvl l${n}">${labels[n]}</span>`;
const flagsHtml = it => (it.proj ? `<span class="flag proj">PROJ</span>` : '') + (it.hyped ? `<span class="flag hyped">HYPED</span>` : '') + (it.rare ? `<span class="flag rare">RARE</span>` : '');
const rbx = n => n == null ? '—' : fmtTable(n) + ' R$';
function buildLimControls(){
  const L = LIM_I18N[settings.lang] || LIM_I18N.en;
  const se = document.getElementById('limSearch'); se.placeholder = L.search; se.value = LM.search;
  const dm = document.getElementById('limDemand');
  dm.innerHTML = `<option value="">${L.dAny}</option>` + L.demandL.map((l, i) => `<option value="${i}">${l}</option>`).join(''); dm.value = LM.demand;
  const tr = document.getElementById('limTrend');
  tr.innerHTML = `<option value="">${L.tAny}</option>` + L.trendL.map((l, i) => `<option value="${i}">${l}</option>`).join(''); tr.value = LM.trend;
  const fl = document.getElementById('limFlag');
  fl.innerHTML = `<option value="">${L.fAny}</option><option value="proj">${L.fProj}</option><option value="noproj">${L.fNoProj}</option><option value="hyped">${L.fHyped}</option><option value="rare">${L.fRare}</option><option value="valued">${L.fValued}</option>`; fl.value = LM.flag;
  const so = document.getElementById('limSort');
  so.innerHTML = Object.entries(L.sort).map(([k, l]) => `<option value="${k}">${l}</option>`).join(''); so.value = L.sort[LM.sort] ? LM.sort : 'rap';
  document.getElementById('limShare').textContent = L.share;
  document.getElementById('limCredit').innerHTML = L.credit;
}
function limRows(){
  let rows = LIM;
  if(LM.search){ const q = LM.search.toLowerCase(); rows = rows.filter(i => i.search.includes(q)); }
  if(LM.demand !== '') rows = rows.filter(i => String(i.demand) === String(LM.demand));
  if(LM.trend !== '') rows = rows.filter(i => String(i.trend) === String(LM.trend));
  if(LM.flag === 'proj') rows = rows.filter(i => i.proj);
  if(LM.flag === 'noproj') rows = rows.filter(i => !i.proj);
  if(LM.flag === 'hyped') rows = rows.filter(i => i.hyped);
  if(LM.flag === 'rare') rows = rows.filter(i => i.rare);
  if(LM.flag === 'valued') rows = rows.filter(i => i.value);
  const miss = -Infinity;
  const key = {rap:i=>i.rap ?? miss, value:i=>i.value ?? miss, price:i=>i.price ?? miss, priceAsc:i=>-(i.price ?? Infinity), d1:i=>i.d1 ?? miss, d7:i=>i.d7 ?? miss,
    favs:i=>i.favs ?? miss, qty:i=>-(i.qty ?? Infinity), ratio:i=>i.ratio ?? miss}[LM.sort];
  if(LM.sort === 'name') return [...rows].sort((a,b) => a.name.localeCompare(b.name));
  return [...rows].sort((a,b) => key(b) - key(a) || (b.rap||0) - (a.rap||0));
}
function renderLimiteds(){
  if(!LIM || view !== 'limiteds') return;
  syncUrl();
  const L = LIM_I18N[settings.lang] || LIM_I18N.en;
  const rows = limRows();
  document.getElementById('limCount').textContent = L.count(rows.length, LIM.length);
  document.getElementById('limHead').innerHTML = `<tr><th>${L.item}</th><th style="text-align:right">${L.price}</th><th style="text-align:right">${L.rap}</th><th style="text-align:right">${L.value}</th>
    <th style="text-align:right" title="${esc(L.ratioHint)}">${L.ratio}</th><th style="text-align:right">${L.d1}</th><th style="text-align:right">${L.d7}</th><th>${L.demand}</th><th>${L.trend}</th><th>${L.flags}</th><th style="text-align:right">${L.qty}</th><th style="text-align:right">${L.favs}</th></tr>`;
  const body = document.getElementById('limBody');
  if(!rows.length){ body.innerHTML = `<tr><td colspan="12"><div class="empty-state">${L.empty}</div></td></tr>`; document.getElementById('limMoreRow').hidden = true; return; }
  body.innerHTML = rows.slice(0, LM.shown).map(it => `<tr>
    <td><div class="lim-item"><img src="${esc(it.icon || '')}" alt="" loading="lazy" onerror="this.style.visibility='hidden'"><div><button class="nm" data-item="${it.id}">${esc(it.name)}</button><span class="sub">${it.acr ? esc(it.acr) + ' · ' : ''}${esc(it.type || '')}</span></div></div></td>
    <td class="num">${rbx(it.price)}</td><td class="num">${rbx(it.rap)}</td><td class="num">${it.value ? rbx(it.value) : '—'}</td>
    <td class="num"><span class="premium ${it.ratio ? (it.ratio >= 1.15 ? 'hi' : it.ratio <= 0.9 ? 'lo' : '') : ''}">${it.ratio ? it.ratio.toFixed(2) + '×' : '—'}</span></td>
    <td class="num">${deltaHtml(it.d1)}</td><td class="num">${deltaHtml(it.d7)}</td>
    <td>${lvlHtml(it.demand, L.demandL)}</td><td>${lvlHtml(it.trend, L.trendL)}</td><td>${flagsHtml(it) || '<span class="lvl none">—</span>'}</td>
    <td class="num">${fmtTable(it.qty)}</td><td class="num">${fmtTable(it.favs)}</td></tr>`).join('');
  animateRows(body);
  const more = document.getElementById('limMoreRow');
  more.hidden = rows.length <= LM.shown;
  document.getElementById('limMoreBtn').textContent = L.more(Math.min(100, rows.length - LM.shown));
  if(LM.openItem){ const it = LIM.find(x => String(x.id) === String(LM.openItem)); LM.openItem = null; if(it) openLimited(it); }
}
function limChartHtml(it, rangeKey){
  const L = LIM_I18N[settings.lang] || LIM_I18N.en;
  const range = RANGES.find(r => r.key === rangeKey) || RANGES[RANGES.length-1];
  const all = {rap: limSeries(it.id, 'rap'), price: limSeries(it.id, 'price')};
  const series = [['rap', pointsInRange(all.rap, range), 'var(--accent)'], ['price', pointsInRange(all.price, range), 'var(--good)']].filter(x => x[1].length);
  const buttons = RANGES.map(r => `<button type="button" class="range-btn ${r.key === range.key ? 'on' : ''}" data-lrange="${r.key}" ${pointsInRange(all.rap, r).length >= 2 ? '' : 'disabled'}>${t('r_'+r.key)}</button>`).join('');
  let body;
  const pts = series.flatMap(x => x[1]);
  if(pts.length < 2 || series.every(x => x[1].length < 2)){
    body = `<div class="chart-empty">${t('ch_empty')}</div>`; limChartHtml._geom = null;
  } else {
    const W = 680, H = 200, PL = 62, PR = 14, PT = 14, PB = 28;
    const t0 = Math.min(...pts.map(p => p.t)), t1 = Math.max(...pts.map(p => p.t)), span = Math.max(1, t1 - t0);
    const vals = pts.map(p => p.v), vmin = Math.min(...vals), vmax = Math.max(...vals);
    const ystep = niceStep(Math.max(1, vmax - vmin) * 1.25, 4);
    let ylo = Math.floor(vmin / ystep) * ystep, yhi = Math.ceil(vmax / ystep) * ystep; if(ylo === yhi) yhi = ylo + ystep; if(ylo < 0) ylo = 0;
    const x = tt => PL + ((tt - t0) / span) * (W - PL - PR), y = v => PT + (1 - (v - ylo) / (yhi - ylo)) * (H - PT - PB);
    let grid = '';
    for(let v = ylo; v <= yhi + 1e-9; v += ystep) grid += `<line x1="${PL}" y1="${y(v).toFixed(1)}" x2="${W-PR}" y2="${y(v).toFixed(1)}" stroke="var(--border)"/><text x="${PL-8}" y="${(y(v)+3.5).toFixed(1)}" text-anchor="end" font-size="10" font-family="IBM Plex Mono, monospace" fill="var(--text-faint)">${fmtNum(Math.round(v))}</text>`;
    const nx = 5, withDate = span > 20*3600e3;
    for(let i = 0; i <= nx; i++){ const tt = t0 + span * i / nx; grid += `<line x1="${x(tt).toFixed(1)}" y1="${PT}" x2="${x(tt).toFixed(1)}" y2="${H-PB}" stroke="var(--border)" stroke-dasharray="2 3"/><text x="${x(tt).toFixed(1)}" y="${H-9}" text-anchor="${i === 0 ? 'start' : i === nx ? 'end' : 'middle'}" font-size="10" font-family="IBM Plex Mono, monospace" fill="var(--text-faint)">${span > 3*86400e3 ? fmtDateShort(tt) : fmtTime(tt, withDate)}</text>`; }
    const paths = series.map(([k, s, c]) => `<path d="${s.map((p, i) => (i ? 'L' : 'M') + x(p.t).toFixed(1) + ',' + y(p.v).toFixed(1)).join(' ')}" fill="none" stroke="${c}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" ${k === 'price' ? 'stroke-dasharray="5 4"' : ''}/>`).join('');
    const dots = series.map(([k, s, c], i) => `<circle id="limDot${i}" r="4" fill="var(--panel)" stroke="${c}" stroke-width="2" visibility="hidden"/>`).join('');
    body = `<div class="chart-wrap" id="limWrap"><svg viewBox="0 0 ${W} ${H}" id="limSvg" role="img">${grid}${paths}<line id="limCursor" x1="0" y1="${PT}" x2="0" y2="${H-PB}" stroke="var(--text-dim)" visibility="hidden"/>${dots}</svg><div class="chart-tip" id="limTip" hidden></div></div>
      <div class="cmp-legend"><span><i style="background:var(--accent)"></i>${L.chRap}</span><span><i style="background:var(--good)"></i>${L.chPrice}</span></div>`;
    limChartHtml._geom = {series, W, H, PL, PR, t0, span, x, y};
  }
  return `<div class="chart-head"><span class="t">${L.chart}</span><div class="range-bar">${buttons}</div></div>${body}
    <div class="chart-note">${t('ch_note')(all.rap.length, all.rap.length ? t('hours')(Math.round((all.rap[all.rap.length-1].t - all.rap[0].t)/3600e3)) : t('underHour'))}</div>`;
}
function bindLimHover(){
  const geom = limChartHtml._geom, svg = document.getElementById('limSvg'); if(!geom || !svg) return;
  const tip = document.getElementById('limTip'), cursor = document.getElementById('limCursor'), wrap = document.getElementById('limWrap');
  const L = LIM_I18N[settings.lang] || LIM_I18N.en;
  const move = e => {
    const r = svg.getBoundingClientRect(); if(!r.width) return;
    const tt = geom.t0 + ((((e.clientX - r.left) * geom.W / r.width) - geom.PL) / (geom.W - geom.PL - geom.PR)) * geom.span;
    let rows = '', px = null, py = null;
    geom.series.forEach(([k, s, c], i) => {
      let best = s[0]; for(const p of s) if(Math.abs(p.t - tt) < Math.abs(best.t - tt)) best = p;
      const dot = document.getElementById('limDot' + i);
      dot.setAttribute('cx', geom.x(best.t)); dot.setAttribute('cy', geom.y(best.v)); dot.setAttribute('visibility', 'visible');
      if(px == null){ px = geom.x(best.t); py = geom.y(best.v); }
      rows += `<span style="color:${c}">■</span> ${k === 'rap' ? L.chRap : L.chPrice}: <b>${fmtFull(best.v)} R$</b> · ${fmtTime(best.t, true)}<br>`;
    });
    cursor.setAttribute('x1', px); cursor.setAttribute('x2', px); cursor.setAttribute('visibility', 'visible');
    tip.innerHTML = rows; tip.hidden = false; tip.style.left = (px * r.width / geom.W) + 'px'; tip.style.top = (py * r.height / geom.H) + 'px';
  };
  const leave = () => { tip.hidden = true; cursor.setAttribute('visibility', 'hidden'); geom.series.forEach((_, i) => document.getElementById('limDot' + i).setAttribute('visibility', 'hidden')); };
  wrap.addEventListener('mousemove', move); wrap.addEventListener('mouseleave', leave);
  wrap.addEventListener('touchstart', e => move(e.touches[0]), {passive:true}); wrap.addEventListener('touchmove', e => move(e.touches[0]), {passive:true});
}
function renderLimChart(it, rangeKey){
  const box = document.getElementById('limChartBox'); if(!box) return;
  limRange = rangeKey; box.innerHTML = limChartHtml(it, rangeKey); bindLimHover();
  box.querySelectorAll('[data-lrange]').forEach(b => b.addEventListener('click', () => renderLimChart(it, b.dataset.lrange)));
}
function openLimited(it){
  const L = LIM_I18N[settings.lang] || LIM_I18N.en;
  if(overlay.hidden) lastFocus = document.activeElement;
  currentGame = null; currentItem = it;
  const stats = [[L.price, rbx(it.price)], [L.rap, rbx(it.rap)], [L.value, it.value ? rbx(it.value) : '—'], [L.ratio, it.ratio ? it.ratio.toFixed(2) + '×' : '—'],
    [L.d1, fmtPct(it.d1)], [L.d7, fmtPct(it.d7)], [L.qty, fmtFull(it.qty)], [L.favs, fmtFull(it.favs)], [L.created, it.created || '—'], [L.type, it.type || '—'], [L.creator, it.creator || '—']];
  modal.innerHTML = `
    <div class="modal-hero icon-only"><img src="${esc(it.icon || '')}" alt="" style="width:150px;height:150px;border-radius:18px;box-shadow:0 12px 32px var(--shadow)" onerror="this.style.visibility='hidden'"><button class="modal-close" id="modalClose" aria-label="Close">×</button></div>
    <div class="modal-body">
      <h2 class="modal-title">${esc(it.name)}${it.acr ? ` <span style="color:var(--text-faint);font-size:.6em">${esc(it.acr)}</span>` : ''}</h2>
      <div class="modal-tags">${flagsHtml(it)}${lvlHtml(it.demand, L.demandL)} ${lvlHtml(it.trend, L.trendL)}</div>
      <div class="stat-grid">${stats.map(([k,v]) => `<div class="stat"><div class="v">${v}</div><div class="k">${k}</div></div>`).join('')}</div>
      <div class="chart-box" id="limChartBox"></div>
      <div class="links-row">
        <a class="link-btn primary" href="https://www.roblox.com/catalog/${it.id}" target="_blank" rel="noopener">${L.openRoblox}</a>
        <a class="link-btn" href="https://www.rolimons.com/item/${it.id}" target="_blank" rel="noopener">${L.rolimons}</a>
        <button type="button" class="link-btn ghost" id="shareItem">${ts('shareGame')}</button>
      </div>
      <div class="lim-credit">${L.credit}</div>
    </div>`;
  renderLimChart(it, limSeries(it.id, 'rap').length >= 2 ? pickDefaultRange(limSeries(it.id, 'rap')) : 'all');
  overlay.hidden = false; syncUrl();
  document.getElementById('shareItem').addEventListener('click', e => copyText(location.href, e.currentTarget));
  document.body.style.overflow = 'hidden';
  document.getElementById('modalClose').focus();
}
document.getElementById('limBody').addEventListener('click', e => {
  const b = e.target.closest('[data-item]'); if(!b) return;
  const it = LIM.find(x => String(x.id) === b.dataset.item); if(it) openLimited(it);
});
document.getElementById('limSearch').addEventListener('input', e => { LM.search = e.target.value; LM.shown = 100; renderLimiteds(); });
['limDemand','limTrend','limFlag','limSort'].forEach(id => document.getElementById(id).addEventListener('change', e => { LM[{limDemand:'demand', limTrend:'trend', limFlag:'flag', limSort:'sort'}[id]] = e.target.value; LM.shown = 100; renderLimiteds(); }));
document.getElementById('limMoreBtn').addEventListener('click', () => { LM.shown += 100; renderLimiteds(); });
document.getElementById('limShare').addEventListener('click', e => copyText(buildUrl(null), e.currentTarget));

/* ---------- shareable links ---------- */""")

# closeModal must also clear the item
rep("""  modal.innerHTML = '';
  currentGame = null;
  syncUrl();""", """  modal.innerHTML = '';
  currentGame = null; currentItem = null;
  syncUrl();""")

open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
