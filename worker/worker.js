/*
 * Roblox Radar — Cloudflare Worker.
 *
 *   GET  /live?ids=1,2,3   live players / visits / favorites / rating for up to 10 games
 *                          (proxied from Roblox with a 10 s cache; the site's "live mode")
 *   POST /discord          Discord interactions endpoint (slash commands)
 *   GET  /register?key=…   registers the slash commands once (key = ADMIN_KEY secret)
 *
 * Secrets / variables (Worker → Settings → Variables):
 *   DISCORD_PUBLIC_KEY   from the Discord application page
 *   DISCORD_APP_ID       application id
 *   DISCORD_TOKEN        bot token (only used to register commands)
 *   ADMIN_KEY            any long random string you choose, protects /register
 *   SITE (optional)      defaults to https://roblox-radar.pages.dev
 *   LANG (optional)      "es" (default) or "en" for the bot's replies
 *   GITHUB_TOKEN         (optional) fine-grained token with Actions: write on the repo — lets the
 *                        Worker's Cron Trigger start the hourly reading, since GitHub's own
 *                        schedule skips runs. Add a trigger "7 * * * *" under Settings → Triggers.
 *   GITHUB_REPO          (optional) "owner/repo", default arturomed31-cyber/roblox-radar
 *   INBOX_CHANNEL        (optional) id of the #para-claude channel; with INBOX_KEY it enables
 *   INBOX_KEY            GET /inbox?key=…&limit=20  (read recent messages, bot must see the channel)
 *                        POST /say?key=…  {text}     (post as the bot into that channel)
 */

const DEFAULT_SITE = 'https://roblox-radar.pages.dev';
const ALLOWED_ORIGINS = [
  'https://roblox-radar.pages.dev', 'https://arturomed31-cyber.github.io',
  'http://127.0.0.1:8080', 'http://localhost:8080'
];
const UA = 'roblox-radar-worker/1.0';

export default {
  // Cron Trigger: kick the hourly reading on GitHub (reliable, unlike GitHub's own schedule)
  async scheduled(event, env, ctx) {
    if (!env.GITHUB_TOKEN) return;
    const repo = env.GITHUB_REPO || 'arturomed31-cyber/roblox-radar';
    ctx.waitUntil(fetch(`https://api.github.com/repos/${repo}/actions/workflows/refresh.yml/dispatches`, {
      method: 'POST',
      headers: { 'authorization': `Bearer ${env.GITHUB_TOKEN}`, 'accept': 'application/vnd.github+json', 'user-agent': UA, 'content-type': 'application/json' },
      body: JSON.stringify({ ref: 'main' })
    }));
  },

  async fetch(req, env) {
    const url = new URL(req.url);
    try {
      if (url.pathname === '/live') return live(req, url);
      if (url.pathname === '/discord') return discord(req, env);
      if (url.pathname === '/register') return register(url, env);
      if (url.pathname === '/health') return json({ ok: true, t: Date.now() });
      if (url.pathname === '/inbox') return inbox(req, url, env);
      if (url.pathname === '/say') return say(req, url, env);
    } catch (e) {
      return json({ error: String(e && e.message || e) }, 500);
    }
    return new Response('roblox-radar worker', { status: 200 });
  }
};

/* ---------------- helpers ---------------- */
function json(obj, status = 200, extra = {}) {
  return new Response(JSON.stringify(obj), {
    status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra }
  });
}
function corsHeaders(req) {
  const origin = req.headers.get('origin') || '';
  const ok = ALLOWED_ORIGINS.includes(origin) || /^https:\/\/[a-z0-9-]+\.roblox-radar\.pages\.dev$/.test(origin);
  return ok ? { 'access-control-allow-origin': origin, 'access-control-allow-methods': 'GET', 'vary': 'origin' } : {};
}
async function robloxJson(url) {
  const r = await fetch(url, { headers: { 'user-agent': UA, 'accept': 'application/json' } });
  if (!r.ok) throw new Error(`roblox ${r.status}`);
  return r.json();
}
const fmt = n => n == null ? '—' : n >= 1e9 ? (n / 1e9).toFixed(2).replace(/\.?0+$/, '') + 'B'
  : n >= 1e6 ? (n / 1e6).toFixed(2).replace(/\.?0+$/, '') + 'M' : n >= 1e3 ? (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'K' : String(n);
const pct = v => v == null ? '—' : (v > 0 ? '+' : '') + Math.round(v) + '%';
const full = n => n == null ? '—' : Number(n).toLocaleString('en-US');

/* ---------------- /live ---------------- */
async function live(req, url) {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: corsHeaders(req) });
  const ids = (url.searchParams.get('ids') || '').split(',').map(s => s.trim()).filter(s => /^\d{1,20}$/.test(s)).slice(0, 10);
  if (!ids.length) return json({ error: 'ids required' }, 400, corsHeaders(req));
  const key = new Request('https://cache.roblox-radar.local/live?ids=' + ids.join(','));
  const cache = caches.default;
  let res = await cache.match(key);
  if (!res) {
    const q = ids.join(',');
    const [d, v] = await Promise.all([
      robloxJson(`https://games.roblox.com/v1/games?universeIds=${q}`),
      robloxJson(`https://games.roblox.com/v1/games/votes?universeIds=${q}`).catch(() => ({ data: [] }))
    ]);
    const votes = {};
    for (const x of v.data || []) votes[String(x.id)] = x;
    const games = {};
    for (const g of d.data || []) {
      const vt = votes[String(g.id)];
      const up = vt ? vt.upVotes : null, down = vt ? vt.downVotes : null;
      games[String(g.id)] = {
        playing: g.playing, visits: g.visits, favs: g.favoritedCount, updated: g.updated,
        votes: vt ? up + down : null, like: vt && up + down ? Math.round(100 * up / (up + down)) : null
      };
    }
    res = new Response(JSON.stringify({ t: Date.now(), games }), {
      headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=10' }
    });
    await cache.put(key, res.clone());
  }
  const body = await res.text();
  return new Response(body, { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...corsHeaders(req) } });
}

/* ---------------- inbox: a channel people write to, read and answered by Claude via the bot ---------------- */
function inboxAuth(url, env) {
  return env.INBOX_KEY && env.INBOX_CHANNEL && url.searchParams.get('key') === env.INBOX_KEY;
}
async function inbox(req, url, env) {
  if (!inboxAuth(url, env)) return json({ error: 'forbidden' }, 403);
  const limit = Math.min(50, Math.max(1, Number(url.searchParams.get('limit') || 20)));
  const after = url.searchParams.get('after');   // message id: only newer ones
  const q = new URLSearchParams({ limit: String(limit) });
  if (after) q.set('after', after);
  const r = await fetch(`https://discord.com/api/v10/channels/${env.INBOX_CHANNEL}/messages?${q}`, {
    headers: { 'authorization': `Bot ${env.DISCORD_TOKEN}`, 'user-agent': UA }
  });
  if (!r.ok) return json({ error: `discord ${r.status}`, detail: await r.text() }, 502);
  const msgs = await r.json();
  return json({
    channel: env.INBOX_CHANNEL,
    messages: msgs.reverse().map(m => ({
      id: m.id, at: m.timestamp, from: m.author?.global_name || m.author?.username, bot: !!m.author?.bot,
      text: m.content, attachments: (m.attachments || []).map(a => a.url)
    }))
  });
}
async function say(req, url, env) {
  if (!inboxAuth(url, env)) return json({ error: 'forbidden' }, 403);
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);
  let body = {};
  try { body = await req.json(); } catch (e) {}
  const text = String(body.text || '').slice(0, 1900);
  if (!text) return json({ error: 'text required' }, 400);
  const r = await fetch(`https://discord.com/api/v10/channels/${body.channel || env.INBOX_CHANNEL}/messages`, {
    method: 'POST',
    headers: { 'authorization': `Bot ${env.DISCORD_TOKEN}`, 'content-type': 'application/json', 'user-agent': UA },
    body: JSON.stringify({ content: text, allowed_mentions: { parse: [] } })
  });
  const out = await r.text();
  return new Response(out, { status: r.status, headers: { 'content-type': 'application/json' } });
}

/* ---------------- site data (cached 5 min in memory + edge cache) ---------------- */
let DATA = { at: 0, games: null, trends: null, biz: null };
async function siteData(env) {
  const site = (env.SITE || DEFAULT_SITE).replace(/\/$/, '');
  if (DATA.games && Date.now() - DATA.at < 5 * 60e3) return DATA;
  const get = async p => {
    const r = await fetch(`${site}/data/${p}`, { cf: { cacheTtl: 300, cacheEverything: true } });
    return r.ok ? r.json() : null;
  };
  const [g, t, b] = await Promise.all([get('games.json'), get('trends.json'), get('business.json')]);
  if (g) DATA = { at: Date.now(), games: g.games, generated: g.generated, trends: (t && t.t) || {}, biz: b || {} };
  return DATA;
}
function findGame(games, q) {
  q = q.trim().toLowerCase();
  if (!q) return null;
  const norm = s => s.toLowerCase().replace(/[\[\]()!🔥⭐🎉✨💎🐉]/g, ' ').replace(/\s+/g, ' ').trim();
  let hits = games.filter(g => norm(g.name) === q);
  if (!hits.length) hits = games.filter(g => norm(g.name).startsWith(q));
  if (!hits.length) hits = games.filter(g => norm(g.name).includes(q));
  if (!hits.length) { const w = q.split(' ').filter(Boolean); hits = games.filter(g => w.every(x => norm(g.name).includes(x))); }
  if (!hits.length) return null;
  return hits.sort((a, b) => (b.playing || 0) - (a.playing || 0))[0];
}

/* ---------------- Discord ---------------- */
const T = {
  es: {
    players: 'Jugadores ahora', h24: '24 h', d7: '7 d', d30: '30 d', rating: 'Valoración', visits: 'Visitas', cat: 'Categoría', tags: 'Señales',
    owner: 'Dueño', group: 'Grupo', user: 'Cuenta personal', age: 'Edad', passes: 'Passes', members: 'Miembros', live: 'en vivo', notFound: 'No encuentro ningún juego con ese nombre en el radar.',
    top: n => `Top ${n} por jugadores ahora`, rising: 'Subiendo más en 7 días (2.000+ jugadores)', newest: 'Nuevos en el radar (últimos 7 días)', none: 'Nada que mostrar todavía.',
    studioNF: 'No encuentro ese estudio.', studio: 'Estudio', games: 'Juegos', total: 'Jugadores totales', main: 'Juego principal', conc: 'de sus jugadores', days: 'd',
    help: '**Comandos**\n`/game nombre` — estadísticas de un juego (en vivo)\n`/top [n]` — los más jugados ahora\n`/rising` — los que más suben en 7 días\n`/new` — nuevos en el radar\n`/studio nombre` — resumen de un estudio\n\nDatos: Roblox Radar · '
  },
  en: {
    players: 'Players now', h24: '24 h', d7: '7 d', d30: '30 d', rating: 'Rating', visits: 'Visits', cat: 'Category', tags: 'Signals',
    owner: 'Owner', group: 'Group', user: 'User account', age: 'Age', passes: 'Passes', members: 'Members', live: 'live', notFound: 'No tracked game matches that name.',
    top: n => `Top ${n} by players now`, rising: 'Rising most over 7 days (2,000+ players)', newest: 'New on the radar (last 7 days)', none: 'Nothing to show yet.',
    studioNF: 'No such studio found.', studio: 'Studio', games: 'Games', total: 'Total players', main: 'Main game', conc: 'of its players', days: 'd',
    help: '**Commands**\n`/game name` — live stats for a game\n`/top [n]` — most played right now\n`/rising` — biggest 7-day risers\n`/new` — newest on the radar\n`/studio name` — studio summary\n\nData: Roblox Radar · '
  }
};
const COMMANDS = [
  { name: 'game', description: 'Estadísticas en vivo de un juego / live stats for a game', options: [{ name: 'nombre', description: 'nombre del juego / game name', type: 3, required: true }] },
  { name: 'top', description: 'Los más jugados ahora / most played right now', options: [{ name: 'n', description: '1-25', type: 4, required: false, min_value: 1, max_value: 25 }] },
  { name: 'rising', description: 'Los que más suben en 7 días / biggest 7-day risers' },
  { name: 'new', description: 'Nuevos en el radar / newest on the radar' },
  { name: 'studio', description: 'Resumen de un estudio / studio summary', options: [{ name: 'nombre', description: 'nombre del estudio o del juego / studio or game name', type: 3, required: true }] },
  { name: 'help', description: 'Lista de comandos / command list' }
];

async function register(url, env) {
  if (!env.ADMIN_KEY || url.searchParams.get('key') !== env.ADMIN_KEY) return json({ error: 'forbidden' }, 403);
  if (!env.DISCORD_APP_ID || !env.DISCORD_TOKEN) return json({ error: 'DISCORD_APP_ID / DISCORD_TOKEN missing' }, 500);
  const r = await fetch(`https://discord.com/api/v10/applications/${env.DISCORD_APP_ID}/commands`, {
    method: 'PUT', headers: { 'authorization': `Bot ${env.DISCORD_TOKEN}`, 'content-type': 'application/json', 'user-agent': UA },
    body: JSON.stringify(COMMANDS)
  });
  const body = await r.text();
  return new Response(body, { status: r.status, headers: { 'content-type': 'application/json' } });
}

function hexToBytes(hex) { const a = new Uint8Array(hex.length / 2); for (let i = 0; i < a.length; i++) a[i] = parseInt(hex.substr(i * 2, 2), 16); return a; }
async function verifyDiscord(req, body, publicKey) {
  const sig = req.headers.get('x-signature-ed25519'), ts = req.headers.get('x-signature-timestamp');
  if (!sig || !ts || !publicKey) return false;
  try {
    const key = await crypto.subtle.importKey('raw', hexToBytes(publicKey), { name: 'Ed25519' }, false, ['verify']);
    return crypto.subtle.verify('Ed25519', key, hexToBytes(sig), new TextEncoder().encode(ts + body));
  } catch (e) { return false; }
}

async function discord(req, env) {
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);
  const body = await req.text();
  if (!(await verifyDiscord(req, body, env.DISCORD_PUBLIC_KEY))) return new Response('bad signature', { status: 401 });
  const it = JSON.parse(body);
  if (it.type === 1) return json({ type: 1 });                     // ping
  if (it.type !== 2) return json({ type: 4, data: { content: '?' } });
  const L = T[(env.LANG || 'es').slice(0, 2)] || T.es;
  const site = (env.SITE || DEFAULT_SITE).replace(/\/$/, '');
  const name = it.data.name;
  const opt = k => ((it.data.options || []).find(o => o.name === k) || {}).value;
  const data = await siteData(env);
  if (!data.games) return json({ type: 4, data: { content: 'data unavailable' } });
  const trend = g => data.trends[String(g.id)] || [null, null, null];
  const line = (g, i) => `**${i + 1}.** [${g.name.slice(0, 48)}](${site}/?game=${g.id}) — ${fmt(g.playing)} · ${pct(trend(g)[0])} (${L.h24})`;
  const footer = { text: `Roblox Radar · ${site.replace(/^https?:\/\//, '')}` };
  const embed = (title, lines) => ({ type: 4, data: { embeds: [{ title, description: lines.length ? lines.join('\n') : L.none, color: 0x4fd1c5, footer }] } });

  if (name === 'help') return json({ type: 4, data: { content: L.help + site } });

  if (name === 'top') {
    const n = Math.min(25, Math.max(1, opt('n') || 10));
    const rows = [...data.games].sort((a, b) => (b.playing || 0) - (a.playing || 0)).slice(0, n);
    return json(embed(L.top(n), rows.map(line)));
  }
  if (name === 'rising') {
    const rows = data.games.filter(g => (g.playing || 0) >= 2000 && trend(g)[1] != null).sort((a, b) => trend(b)[1] - trend(a)[1]).slice(0, 10);
    return json(embed(L.rising, rows.map((g, i) => `**${i + 1}.** [${g.name.slice(0, 48)}](${site}/?game=${g.id}) — ${fmt(g.playing)} · **${pct(trend(g)[1])}** (${L.d7})`)));
  }
  if (name === 'new') {
    const cutoff = new Date(Date.now() - 7 * 86400e3).toISOString().slice(0, 10);
    const rows = data.games.filter(g => g.added && g.added >= cutoff).sort((a, b) => (b.playing || 0) - (a.playing || 0)).slice(0, 10);
    return json(embed(L.newest, rows.map((g, i) => `**${i + 1}.** [${g.name.slice(0, 48)}](${site}/?game=${g.id}) — ${fmt(g.playing)} · ${g.cat} · ${g.added}`)));
  }
  if (name === 'studio') {
    const q = String(opt('nombre') || '').toLowerCase();
    let games = data.games.filter(g => (g.creator || '').toLowerCase().includes(q));
    if (!games.length) { const g = findGame(data.games, q); if (g) games = data.games.filter(x => x.cUrl === g.cUrl); }
    if (!games.length) return json({ type: 4, data: { content: L.studioNF } });
    games.sort((a, b) => (b.playing || 0) - (a.playing || 0));
    const total = games.reduce((s, g) => s + (g.playing || 0), 0), top = games[0];
    const lines = games.slice(0, 10).map(line);
    return json({ type: 4, data: { embeds: [{
      title: `${top.creator}${top.verified ? ' ✓' : ''}`, url: top.cUrl, color: 0xf0b429, footer,
      fields: [
        { name: L.owner, value: top.cType === 'Group' ? L.group : L.user, inline: true },
        { name: L.games, value: String(games.length), inline: true },
        { name: L.total, value: full(total), inline: true },
        { name: L.main, value: `${top.name} — ${Math.round((top.playing || 0) / (total || 1) * 100)}% ${L.conc}`, inline: false }
      ],
      description: lines.join('\n')
    }] } });
  }
  if (name === 'game') {
    const g = findGame(data.games, String(opt('nombre') || ''));
    if (!g) return json({ type: 4, data: { content: L.notFound } });
    let liveP = null;
    try {
      const r = await robloxJson(`https://games.roblox.com/v1/games?universeIds=${g.id}`);
      liveP = r.data && r.data[0] ? r.data[0].playing : null;
    } catch (e) {}
    const [d1, d7, d30] = trend(g);
    const b = data.biz[String(g.id)] || {};
    const ageDays = g.created ? Math.floor((Date.now() - new Date(g.created)) / 86400e3) : null;
    const fields = [
      { name: L.players, value: `**${full(liveP ?? g.playing)}**${liveP != null ? ` (${L.live})` : ''}`, inline: true },
      { name: `${L.h24} / ${L.d7} / ${L.d30}`, value: `${pct(d1)} / ${pct(d7)} / ${pct(d30)}`, inline: true },
      { name: L.rating, value: g.like != null ? `${g.like}%` : '—', inline: true },
      { name: L.visits, value: fmt(g.visits), inline: true },
      { name: L.age, value: ageDays != null ? `${ageDays}${L.days}` : '—', inline: true },
      { name: L.owner, value: g.cType === 'Group' ? `${L.group}${b.grp && b.grp.m != null ? ` · ${fmt(b.grp.m)} ${L.members.toLowerCase()}` : ''}` : L.user, inline: true },
      { name: L.cat, value: `${g.cat}${g.src === 'review' ? '' : ' (auto)'}`, inline: true },
      { name: L.tags, value: (g.tags || []).join(', ') || '—', inline: true }
    ];
    if (b.gp) fields.push({ name: L.passes, value: `${b.gp.n}${b.gp.min != null ? ` · ${b.gp.min}–${b.gp.max} R$` : ''}`, inline: true });
    return json({ type: 4, data: { embeds: [{
      title: g.name.slice(0, 200), url: `https://www.roblox.com/games/${g.place}`, color: 0x5fd77c,
      thumbnail: g.icon ? { url: g.icon } : undefined, image: g.thumb ? { url: g.thumb } : undefined,
      description: `${g.creator || ''}${g.verified ? ' ✓' : ''} · [Roblox Radar](${site}/?game=${g.id})`,
      fields, footer
    }] } });
  }
  return json({ type: 4, data: { content: '?' } });
}
