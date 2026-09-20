p = 'worker/worker.js'
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

rep(""" *   INBOX_CHANNEL        (optional) id of the #para-claude channel; with INBOX_KEY it enables""",
    """ *   RADAR_KV             KV namespace binding (Bindings -> KV) - stores personal /watch lists.
 *                        Cron Triggers: "7 * * * *" starts the reading on GitHub (needs GITHUB_TOKEN),
 *                        "25 * * * *" checks every /watch against the fresh 24 h trends.
 *   INBOX_CHANNEL        (optional) id of the #para-claude channel; with INBOX_KEY it enables""")

rep("""  async scheduled(event, env, ctx) {
    if (!env.GITHUB_TOKEN) return;""", """  async scheduled(event, env, ctx) {
    if (event.cron === '25 * * * *') { ctx.waitUntil(checkWatches(env)); return; }
    if (!env.GITHUB_TOKEN) return;""")

rep("""      if (url.pathname === '/inbox') return inbox(req, url, env);""",
    """      if (url.pathname === '/inbox') return inbox(req, url, env);
      if (url.pathname === '/check-watches') {   // manual run, same key as /inbox
        if (!env.INBOX_KEY || url.searchParams.get('key') !== env.INBOX_KEY) return json({ error: 'forbidden' }, 403);
        return json(await checkWatches(env));
      }""")

rep("""`/studio nombre` — resumen de un estudio\\n\\nDatos: Roblox Radar · '
  },""", """`/studio nombre` — resumen de un estudio\\n`/watch add nombre [umbral]` — avísame si sube o baja ≥ umbral % en 24 h (por defecto 30)\\n`/watch list` · `/watch remove nombre`\\n\\nDatos: Roblox Radar · ',
    wAdded: (g, p) => `✅ Vigilando **${g}** — te aviso aquí si sube o baja **±${p} %** en 24 h (revisión cada hora, máximo un aviso por juego cada 24 h).`,
    wExists: (g, p) => `Ya vigilabas **${g}**; umbral actualizado a ±${p} %.`, wRemoved: g => `🗑️ Dejo de vigilar **${g}**.`, wNone: 'No vigilas ningún juego. Usa `/watch add nombre`.',
    wList: 'Tus juegos vigilados', wNoKV: 'Las alertas personales aún no están activadas (falta el almacenamiento KV del Worker).', wMax: 'Máximo 25 juegos por persona.',
    wUp: (g, d, a, b) => `📈 **${g}** +${d} % en 24 h (${a} → ${b})`, wDown: (g, d, a, b) => `📉 **${g}** ${d} % en 24 h (${a} → ${b})`, wThr: p => `umbral ±${p} %`
  },""")
rep("""`/studio name` — studio summary\\n\\nData: Roblox Radar · '
  }""", """`/studio name` — studio summary\\n`/watch add name [threshold]` — ping me when it moves ≥ threshold % in 24 h (default 30)\\n`/watch list` · `/watch remove name`\\n\\nData: Roblox Radar · ',
    wAdded: (g, p) => `✅ Watching **${g}** — I will ping you here when it moves **±${p} %** in 24 h (checked hourly, at most one alert per game per 24 h).`,
    wExists: (g, p) => `Already watching **${g}**; threshold set to ±${p} %.`, wRemoved: g => `🗑️ No longer watching **${g}**.`, wNone: 'You are not watching any game. Use `/watch add name`.',
    wList: 'Your watched games', wNoKV: 'Personal alerts are not enabled yet (the Worker has no KV storage bound).', wMax: 'Up to 25 games per person.',
    wUp: (g, d, a, b) => `📈 **${g}** +${d} % in 24 h (${a} → ${b})`, wDown: (g, d, a, b) => `📉 **${g}** ${d} % in 24 h (${a} → ${b})`, wThr: p => `threshold ±${p} %`
  }""")

rep("""  { name: 'help', description: 'Lista de comandos / command list' }
];""", """  { name: 'help', description: 'Lista de comandos / command list' },
  { name: 'watch', description: 'Alertas personales / personal alerts', options: [
    { type: 1, name: 'add', description: 'Vigilar un juego / watch a game', options: [
      { name: 'nombre', description: 'nombre del juego / game name', type: 3, required: true },
      { name: 'umbral', description: '% de cambio en 24 h que dispara el aviso (5-500, por defecto 30)', type: 4, required: false, min_value: 5, max_value: 500 }] },
    { type: 1, name: 'remove', description: 'Dejar de vigilar / stop watching', options: [
      { name: 'nombre', description: 'nombre del juego / game name', type: 3, required: true }] },
    { type: 1, name: 'list', description: 'Tus juegos vigilados / your watched games' }
  ] }
];""")

rep("""  if (name === 'help') return json({ type: 4, data: { content: L.help + site } });""",
    """  if (name === 'help') return json({ type: 4, data: { content: L.help + site } });

  if (name === 'watch') {
    if (!env.RADAR_KV) return json({ type: 4, data: { content: L.wNoKV } });
    const sub = (it.data.options || [])[0] || {};
    const arg = k => ((sub.options || []).find(o => o.name === k) || {}).value;
    const user = (it.member && it.member.user) || it.user || {};
    const key = `watch:${user.id}`;
    const list = JSON.parse((await env.RADAR_KV.get(key)) || '[]');
    if (sub.name === 'list') {
      if (!list.length) return json({ type: 4, data: { content: L.wNone } });
      return json(embed(L.wList, list.map((w, i) => {
        const g = data.games.find(x => String(x.id) === String(w.id));
        return `**${i + 1}.** [${w.name.slice(0, 48)}](${site}/?game=${w.id}) — ${g ? fmt(g.playing) : '—'} · ${pct(g ? trend(g)[0] : null)} (${L.h24}) · ${L.wThr(w.pct)}`;
      })));
    }
    if (sub.name === 'remove') {
      const q = String(arg('nombre') || '').toLowerCase();
      const g = findGame(data.games, q);
      const w = (g && list.find(x => String(x.id) === String(g.id))) || list.find(x => x.name.toLowerCase().includes(q));
      if (!w) return json({ type: 4, data: { content: L.notFound } });
      await env.RADAR_KV.put(key, JSON.stringify(list.filter(x => x !== w)));
      return json({ type: 4, data: { content: L.wRemoved(w.name) } });
    }
    if (sub.name === 'add') {
      const g = findGame(data.games, String(arg('nombre') || ''));
      if (!g) return json({ type: 4, data: { content: L.notFound } });
      const p = Math.min(500, Math.max(5, arg('umbral') || 30));
      const existing = list.find(x => String(x.id) === String(g.id));
      if (existing) { existing.pct = p; existing.channel = it.channel_id; }
      else {
        if (list.length >= 25) return json({ type: 4, data: { content: L.wMax } });
        list.push({ id: g.id, name: g.name, pct: p, channel: it.channel_id, guild: it.guild_id || null, since: Date.now() });
      }
      await env.RADAR_KV.put(key, JSON.stringify(list));
      return json({ type: 4, data: { content: existing ? L.wExists(g.name, p) : L.wAdded(g.name, p) } });
    }
  }""")

rep("""/* ---------------- Discord ---------------- */""", """/* ---------------- personal watch alerts (cron, hourly) ---------------- */
async function checkWatches(env) {
  if (!env.RADAR_KV || !env.DISCORD_TOKEN) return { skipped: 'no KV or token' };
  const L = T[(env.LANG || 'es').slice(0, 2)] || T.es;
  const site = (env.SITE || DEFAULT_SITE).replace(/\\/$/, '');
  DATA.at = 0;                                   // always fresh data for the check
  const data = await siteData(env);
  if (!data.games) return { skipped: 'no data' };
  const byId = new Map(data.games.map(g => [String(g.id), g]));
  const keys = await env.RADAR_KV.list({ prefix: 'watch:' });
  let sent = 0, checked = 0;
  for (const k of keys.keys) {
    const userId = k.name.slice(6);
    const list = JSON.parse((await env.RADAR_KV.get(k.name)) || '[]');
    for (const w of list) {
      checked++;
      const g = byId.get(String(w.id)); if (!g) continue;
      const d1 = (data.trends[String(g.id)] || [])[0];
      if (d1 == null || Math.abs(d1) < w.pct) continue;
      const cool = `alerted:${userId}:${g.id}`;
      if (await env.RADAR_KV.get(cool)) continue;
      const prev = Math.round((g.playing || 0) / (1 + d1 / 100));
      const line = d1 > 0 ? L.wUp(g.name, Math.round(d1), fmt(prev), fmt(g.playing)) : L.wDown(g.name, Math.round(d1), fmt(prev), fmt(g.playing));
      const r = await fetch(`https://discord.com/api/v10/channels/${w.channel}/messages`, {
        method: 'POST',
        headers: { 'authorization': `Bot ${env.DISCORD_TOKEN}`, 'content-type': 'application/json', 'user-agent': UA },
        body: JSON.stringify({ content: `<@${userId}> ${line} · ${L.wThr(w.pct)} · ${site}/?game=${g.id}`, allowed_mentions: { users: [userId] } })
      });
      if (r.ok) { sent++; await env.RADAR_KV.put(cool, '1', { expirationTtl: 24 * 3600 }); }
    }
  }
  return { checked, sent, at: new Date().toISOString() };
}

/* ---------------- Discord ---------------- */""")

open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
