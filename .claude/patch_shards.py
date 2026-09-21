"""Page: history is no longer downloaded up front. trends.json feeds the table; per-game
series come from data/h/NN.json, fetched when a chart is opened."""
p = 'index.html'
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

rep("""  const [gamesDoc, hist, shared, biz] = await Promise.all([
    fetch('data/games.json' + bust).then(r => r.json()),
    fetch('data/history.json' + bust).then(r => r.json()),""", """  const [gamesDoc, trends, shared, biz] = await Promise.all([
    fetch('data/games.json' + bust).then(r => r.json()),
    fetch('data/trends.json' + bust).then(r => r.ok ? r.json() : {t:{}}).catch(() => ({t:{}})),""")
rep("""    g.vpd = g.age ? Math.round(g.visits / g.age) : null;
    g.hist = hist.series[String(g.id)] || [];
  });
  DATA = {generated: gamesDoc.generated, sampleTimes: hist.times || []};
  GAMES = gamesDoc.games;
  SAMPLE_TIMES = DATA.sampleTimes;
}""", """    g.vpd = g.age ? Math.round(g.visits / g.age) : null;
    g.tr = (trends.t || {})[String(g.id)] || {};   // d1/d7/d30, a24 (avg last 24 h), pk (peak on record)
    g.hist = null;                                  // per-game series, fetched on demand (see ensureHist)
  });
  DATA = {generated: gamesDoc.generated, readings: trends.n || 0, first: trends.first, last: trends.last};
  GAMES = gamesDoc.games;
}
/* ---------- per-game history: data/h/NN.json, NN = last two digits of the id ---------- */
const HSHARDS = new Map();   // shard -> Promise<{times, series}>
const shardOf = id => { const s = String(id).slice(-2); return /^\\d+$/.test(s) ? s.padStart(2, '0') : '00'; };
function ensureHist(games){
  const need = games.filter(g => g && !g.hist);
  if(!need.length) return Promise.resolve();
  const bust = '?v=' + Math.floor(Date.now() / 900e3);   // 15-min cache window
  const shards = [...new Set(need.map(g => shardOf(g.id)))];
  return Promise.all(shards.map(sh => {
    if(!HSHARDS.has(sh)) HSHARDS.set(sh, fetch(`data/h/${sh}.json` + bust).then(r => r.ok ? r.json() : {times:[], series:{}}).catch(() => ({times:[], series:{}})));
    return HSHARDS.get(sh);
  })).then(docs => {
    const bySh = Object.fromEntries(shards.map((sh, i) => [sh, docs[i]]));
    need.forEach(g => {
      const d = bySh[shardOf(g.id)], s = (d.series || {})[String(g.id)] || [];
      const ms = (d.times || []).map(x => new Date(x).getTime());
      g.hist = {t: ms, v: s};
    });
  });
}""")
rep("""function indexGames(){
  GAMES.forEach((g,i) => { g._i = i; });
  [...GAMES].sort((a,b)=>(b.playing||0)-(a.playing||0)).forEach((g,i)=>{ g._rank = i+1; });
  SAMPLE_MS = SAMPLE_TIMES.map(x => new Date(x).getTime());
  computeMetrics();
}""", """function indexGames(){
  GAMES.forEach((g,i) => { g._i = i; });
  [...GAMES].sort((a,b)=>(b.playing||0)-(a.playing||0)).forEach((g,i)=>{ g._rank = i+1; });
  computeMetrics();
}""")
rep("""function seriesFor(g){
  return (g.hist || []).map((v,i) => ({t: SAMPLE_MS[i], v})).filter(p => p.v != null && p.t).sort((a,b)=>a.t-b.t);
}""", """function seriesFor(g){
  if(!g.hist) return [];
  return g.hist.v.map((v,i) => ({t: g.hist.t[i], v})).filter(p => p.v != null && p.t).sort((a,b)=>a.t-b.t);
}""")
# metrics from trends.json instead of the full series
rep("""  GAMES.forEach(g => {
    const s = seriesFor(g);
    g.d1 = changeOver(s, 1); g.d7 = changeOver(s, 7); g.d30 = changeOver(s, 30);
    const mom = g.d7;""", """  GAMES.forEach(g => {
    const tr = g.tr || {};
    g.d1 = tr.d1 ?? null; g.d7 = tr.d7 ?? null; g.d30 = tr.d30 ?? null; g.peak = tr.pk ?? null;
    const mom = g.d7;""")
rep("""    const last24 = s.length ? s.filter(p => p.t >= s[s.length-1].t - 86400e3) : [];
    const avgCcu = last24.length >= 3 ? last24.reduce((a,p) => a + p.v, 0) / last24.length : (g.playing || 0);""",
    """    const avgCcu = tr.a24 != null ? tr.a24 : (g.playing || 0);""")
# coverage line
rep("""    const days = SAMPLE_MS.length > 1 ? Math.max(1, Math.round((SAMPLE_MS[SAMPLE_MS.length-1] - SAMPLE_MS[0]) / 86400e3)) : 0;
    document.getElementById('trendCoverage').textContent = t('coverage')(days, SAMPLE_MS.length);""",
    """    const days = DATA.first && DATA.last ? Math.max(1, Math.round((new Date(DATA.last) - new Date(DATA.first)) / 86400e3)) : 0;
    document.getElementById('trendCoverage').textContent = t('coverage')(days, DATA.readings);""")
# game window: peak from trends, chart fetched on demand
rep("""  const series = seriesFor(g);
  const peak = series.length ? Math.max(...series.map(p=>p.v)) : null;
  const stats = [""", """  const peak = g.peak;
  const stats = [""")
rep("""  renderChart(g, rangeKey || pickDefaultRange(series));
  renderLive(g);
  overlay.hidden = false;""", """  if(g.hist) renderChart(g, rangeKey || pickDefaultRange(seriesFor(g)));
  else {
    document.getElementById('chartBox').innerHTML = `<div class="chart-head"><span class="t">${t('ch_title')}</span></div><div class="loading" style="padding:30px">${t('loading')}</div>`;
    ensureHist([g]).then(() => { if(currentGame === g && !overlay.hidden) renderChart(g, rangeKey || pickDefaultRange(seriesFor(g))); });
  }
  renderLive(g);
  overlay.hidden = false;""")
# compare: load the selected games' shards first
rep("""  renderCompare();
  syncUrl();
}""", """  ensureHist(CMP.map(id => byId.get(id)).filter(Boolean)).then(renderCompare);
  syncUrl();
}""")
rep("""    ['st_now', g => g.playing, fmtFull, 1], ['st_peak', g => { const s = seriesFor(g); return s.length ? Math.max(...s.map(p=>p.v)) : null; }, fmtFull, 1],""",
    """    ['st_now', g => g.playing, fmtFull, 1], ['st_peak', g => g.peak, fmtFull, 1],""")
rep("let DATA = null, GAMES = [], SAMPLE_TIMES = [], SAMPLE_MS = [];", "let DATA = null, GAMES = [];")

open(p, 'w', encoding='utf-8', newline='').write(s)
import re
left = re.findall(r'SAMPLE_MS|SAMPLE_TIMES|changeOver\(', s)
print('ok; leftovers:', left)
