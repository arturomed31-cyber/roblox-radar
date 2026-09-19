/* Roblox Radar — interface strings. Missing keys fall back to English. */
const I18N = {
  en: {
    subtitle: "Every Roblox game currently holding real traffic, plus everything on the front-page charts — sorted by what each game actually is, so a genre-defining original never looks like the fifth copy of last month's hit.",
    settings: "Settings", signalsLabel: "Pattern signals — click to filter", searchPh: "Search game or creator…",
    reset: "Reset", all: "All", allCats: "All categories",
    age_any: "Any age", age_30: "Launched < 30 days ago", age_90: "Launched < 3 months ago", age_365: "Launched < 1 year ago", age_old: "Older than 1 year",
    sort_playing_desc: "Players now ↓", sort_playing_asc: "Players now ↑", sort_visits_desc: "Total visits ↓", sort_vpd_desc: "Visits per day ↓",
    sort_like_desc: "Rating ↓", sort_like_asc: "Rating ↑", sort_age_asc: "Newest first", sort_age_desc: "Oldest first", sort_name_asc: "Name A→Z",
    sort_favs_desc: "Favorites ↓", sort_upd_asc: "Recently updated", sort_rev_desc: "Est. earnings ↓", sort_members_desc: "Group size ↓",
    h_game: "Game", h_cat: "Category", h_signals: "Signals", h_rating: "Rating", h_players: "Players", h_visits: "Visits", h_age: "Age",
    h_favs: "Favorites", h_vpd: "Visits/day", h_upd: "Updated",
    count: (n, total, p) => `${n} of ${total} games · ${p} players in them right now`,
    empty: "No game matches these filters. Try removing one.", more: n => `Show more (${n} left)`,
    noTag: "no pattern flagged", by: "by", unknown: "unknown", auto: "auto",
    reviewed: "Hand-reviewed classification", autoTip: "Auto-classified by keyword rules, not yet reviewed",
    openStats: n => `Open stats for ${n}`,
    tracked: (n, p) => `<b>${n}</b> games tracked · <b>${p}</b> concurrent players`, lastRefresh: d => `last reading ${d} UTC · readings every 2 h, full refresh daily`,
    footer: 'Click any thumbnail for full stats, the player-history chart, the creator\'s Roblox group and any social links. Counts come from Roblox\'s public game and thumbnail APIs and are read every 2 hours; ratings, images, social links and new games refresh daily at 20:00 UTC. Categories and pattern signals were assigned by reading each game\'s name, description and genre — a research starting point, not a verdict. "Copy of another hit" means the core loop visibly follows an earlier game; "Borrowed IP" flags external copyrighted characters or brands.',
    loading: "Loading radar data…", loadErr: "Could not load data/games.json — if you opened this file directly, serve the folder over http (GitHub Pages does this for you).",
    st_now: "Players now", st_rank: "Rank by players", st_peak: "Peak on record", st_visits: "Total visits", st_vpd: "Visits / day", st_rating: "Rating",
    st_votes: "Votes", st_favs: "Favorites", st_age: "Age", st_upd: "Last updated", st_server: "Server size", st_mat: "Maturity",
    today: "today", daysAgo: n => `${n}d ago`, players: "players", classifiedAs: "classified as", autoNote: "(auto, by keyword rules — not yet hand-reviewed)", added: "added",
    openRoblox: "Open on Roblox", group: "Roblox group", profile: "Creator profile",
    noSocials: "No Discord or social link found for this game. Roblox only shows a game's Social Links to logged-in users 13+ — check the game page.",
    ch_title: "Concurrent players", ch_now: "now", ch_peak: "range peak", ch_low: "range low", ch_avg: "range avg", ch_allPeak: "all-time peak on record",
    ch_notEnough: "Not enough history recorded yet", ch_empty: "Not enough readings for this range yet.", ch_peakLbl: "peak",
    ch_note: (n, h) => `${n} readings across ${h} of monitoring, one every 2 hours. Roblox publishes no player history, so this chart only grows as the radar keeps sampling; beyond 30 days it keeps one daily peak per game.`,
    underHour: "under an hour", hours: h => `${h} h`,
    r_24h: "24h", r_7d: "7d", r_30d: "1mo", r_1y: "1y", r_all: "All",
    s_lang: "Language", s_lang_h: "Interface language", s_theme: "Theme", s_theme_h: "System follows your OS setting",
    t_system: "System", t_dark: "Dark", t_light: "Light",
    s_numbers: "Numbers", s_numbers_h: "How players and visits are shown in the table",
    s_cols: "Visible columns", s_cols_h: "Game, category, signals and players are always shown",
    s_min: "Minimum players", s_min_h: "Hide games below this many concurrent players",
    s_rows: "Rows per page", s_rows_h: "More rows means more images to load",
    s_remember: "Remember filters", s_remember_h: "Reopen the page with the last search, filters and sort",
    s_hideauto: "Hide auto-classified games", s_hideauto_h: "Show only games whose category was hand-reviewed",
    s_tz: "Chart time", s_tz_h: "Time zone for the player-history axis", tz_local: "Local",
    s_saved: "Saved in this browser only.", s_reset: "Reset to defaults",
    v_games: "Games", v_market: "Market", m_byTags: "By pattern", m_byCats: "By category",
    m_hint: "Click a row to see its games", m_note: "Share = percentage of all tracked concurrent players. New 30d / 90d = games in the group launched in that window. Median players and rating describe the typical game in the group, not the biggest. 7d growth is the median change per game and only appears once a week of history exists.",
    m_group: "Group", m_games: "Games", m_players: "Players now", m_share: "Share", m_new30: "New 30d", m_new90: "New 90d", m_median: "Median players", m_rating: "Median rating", m_d7: "7d growth", m_score: "Avg score",
    m_all: "All tracked games",
    trend_any: "Any trend", trend_rising: "Rising", trend_falling: "Falling", trend_flat: "Stable", trend_new: "New (< 30 days)",
    tb_rising: "rising", tb_falling: "falling", tb_flat: "stable", tb_new: "new",
    h_d1: "24h", h_d7: "7d", h_d30: "30d", h_score: "Score",
    sort_score_desc: "Opportunity score ↓", sort_d7_desc: "7d growth ↓", sort_d30_desc: "30d growth ↓", sort_d1_desc: "24h change ↓",
    st_d1: "24h change", st_d7: "7d change", st_d30: "30d change",
    sc_title: "Opportunity score", sc_hint: "0–100 · momentum, rating, scale and freshness, minus copy/IP risks. A research shortlist, not advice.",
    sc_momentum: "Momentum (growth)", sc_rating: "Rating", sc_scale: "Scale (players)", sc_fresh: "Freshness (age)", sc_engage: "Engagement (visits/day)",
    sc_flagship: "Original flagship bonus", sc_copycat: "Copy of another hit", sc_ip: "Borrowed IP risk", sc_pattern: "Saturated formula", sc_auto: "Not hand-reviewed",
    sc_noHist: "no growth data yet — momentum counted as neutral",
    coverage: (d, n) => `trend data: ${n} readings over ${d} days · 7d/30d columns fill in as history accumulates`,
    own_any: "Any owner", own_group: "Owned by a group", own_user: "Owned by a user",
    h_members: "Group size", h_rev: "Est. $/mo", h_passes: "Passes",
    bz_title: "Business", bz_hint: "What a buyer looks at: who owns it, how it monetizes, what it might earn.",
    bz_owner: "Owner", bz_group: "Group (transferable)", bz_user: "User account (not transferable)", bz_members: "Group members", bz_groupAge: "Group created",
    bz_passes: "Game passes", bz_priceRange: "Pass prices", bz_vip: "Private servers", bz_paid: "Paid access", bz_yes: "yes", bz_no: "no",
    bz_dau: "Est. daily players (DAU)", bz_rev: "Est. developer earnings", bz_val: "Typical asking price", bz_perMonth: "/ month",
    bz_note: "Estimates only. DAU ≈ average concurrent players over the last 24 h × 12 (a common Roblox ratio). Earnings assume $6–18 per month per average concurrent player after Roblox's cut (calibrated on publicly reported cases), adjusted for how the game monetizes. Asking prices in the buyer market usually run 12–24× monthly earnings for small and mid-size games; the biggest games are rarely for sale. Roblox publishes none of this; treat it as a starting range for due diligence.",
    bz_pending: "Ownership and monetization data arrive with the next daily refresh.",
    sc_group: "Group-owned (transferable)",
    lg_title: "Privacy & legal notice", lg_link: "Privacy · Legal notice",
    lg_html: `
<h3>Who runs this site</h3>
<p>Roblox Radar is an independent, personal project. Contact: <a href="mailto:Arturomed31@gmail.com">Arturomed31@gmail.com</a>.</p>
<h3>Privacy</h3>
<p><b>No accounts, no cookies, no tracking.</b> This site has no server-side code and no analytics. It does not collect, store or share personal data.</p>
<ul>
<li><b>Local storage only:</b> your settings, filters and chart notes are saved in your own browser (localStorage) and never leave your device. Clearing your browser data removes them.</li>
<li><b>Third-party requests:</b> game icons and thumbnails are loaded directly from Roblox's image servers (tr.rbxcdn.com). When your browser fetches them, Roblox receives your IP address and standard request headers, under <a href="https://en.help.roblox.com/hc/en-us/articles/115004630823" target="_blank" rel="noopener">Roblox's privacy policy</a>. Fonts are hosted on this site; nothing is sent to Google.</li>
<li><b>Hosting:</b> the site is served by Cloudflare Pages and GitHub Pages, which may keep standard server logs (IP address, time, requested file) for security. See <a href="https://www.cloudflare.com/privacypolicy/" target="_blank" rel="noopener">Cloudflare</a> and <a href="https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">GitHub</a>.</li>
</ul>
<h3>Where the data comes from</h3>
<p>All game statistics (players, visits, ratings, images, creator and group names, social links) come from Roblox's public web APIs and are refreshed automatically. Only information that Roblox already shows publicly is displayed.</p>
<h3>Not affiliated with Roblox</h3>
<p>This site is not endorsed by, sponsored by or affiliated with Roblox Corporation. Roblox and the Roblox logo are registered trademarks of Roblox Corporation. Game names, images and other content belong to their respective creators and are shown for identification and informational purposes.</p>
<h3>No financial advice</h3>
<p><b>Estimates of daily players, developer earnings and asking prices are rough calculations based on public player counts and generic industry ratios.</b> Roblox does not publish revenue data. Categories, pattern signals and the opportunity score are editorial opinions produced partly by automated rules. Nothing on this site is financial, investment or legal advice; verify everything independently before any transaction.</p>
<h3>Removal requests</h3>
<p>If you own a game or group listed here and want it removed or corrected, write to the contact address above and it will be handled promptly.</p>
<div class="legal-meta">Last updated: September 2026</div>`,
    n_title: "Notes on this chart", n_hint: "Click anywhere on the chart to pin a note at that moment. Notes are saved in this browser; export them to keep or share.",
    n_placeholder: "What happened here? (update, promo, drop…)", n_save: "Save", n_cancel: "Cancel", n_delete: "Delete", n_edit: "Edit",
    n_empty: "No notes yet.", n_export: "Export", n_import: "Import", n_shared: "shared", n_exported: "Notes exported", n_imported: n => `${n} notes imported`,
    cats: {sim:'Simulator / Idle', rp:'Roleplay', shooter:'Shooter', fight:'Fighting / PvP', action:'Open-world action', obby:'Obby / Platformer', sports:'Sports & Racing', rpg:'RPG / Adventure', horror:'Horror / Survival', party:'Party / Casual', strategy:'Strategy / TD', sandbox:'Sandbox / Building', fangame:'Fan game', other:'Tool / Other'},
    tags: {'brainrot':'Brainrot','mm2-clone':'MM2 clone','mm2-original':'MM2 (the original)','minecraft-clone':'Minecraft-derived','tower':'Tower climb','tower-defense':'Tower defense','steal-pattern':'"Steal a X" formula','plus1-pattern':'"+1 per click" formula','duels-pattern':'"DUELS" arena formula','rng-gacha':'RNG / gacha loop','copycat':'Copy of another hit','licensed-ip':'Borrowed IP','flagship':'Original flagship','anime':'Anime','meme':'Meme premise'},
    signals: {'brainrot':'Brainrot themed','mm2-clone':'MM2 clones','minecraft-clone':'Minecraft-derived','tower':'Tower climbers','steal-pattern':'"Steal a X" formula','plus1-pattern':'"+1 per click" formula','duels-pattern':'"DUELS" arenas','copycat':'Copies of other hits','licensed-ip':'Borrowed IP','flagship':'Original flagships'},
    socials: {discord:'Discord', youtube:'YouTube', x:'X / Twitter', tiktok:'TikTok', twitch:'Twitch', facebook:'Facebook', guilded:'Guilded', group:'Linked group'},
    months: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  },
  es: {
    subtitle: "Todos los juegos de Roblox con tráfico real ahora mismo, más los de las listas de portada — ordenados por lo que cada juego es en realidad, para que un original que define un género nunca parezca la quinta copia del éxito del mes pasado.",
    settings: "Configuración", signalsLabel: "Señales de patrón — clic para filtrar", searchPh: "Buscar juego o creador…",
    reset: "Limpiar", all: "Todos", allCats: "Todas las categorías",
    age_any: "Cualquier edad", age_30: "Lanzado hace < 30 días", age_90: "Lanzado hace < 3 meses", age_365: "Lanzado hace < 1 año", age_old: "Más de 1 año",
    sort_playing_desc: "Jugadores ahora ↓", sort_playing_asc: "Jugadores ahora ↑", sort_visits_desc: "Visitas totales ↓", sort_vpd_desc: "Visitas por día ↓",
    sort_like_desc: "Valoración ↓", sort_like_asc: "Valoración ↑", sort_age_asc: "Más nuevos primero", sort_age_desc: "Más antiguos primero", sort_name_asc: "Nombre A→Z",
    sort_favs_desc: "Favoritos ↓", sort_upd_asc: "Actualizados recientemente", sort_rev_desc: "Ganancia est. ↓", sort_members_desc: "Tamaño de grupo ↓",
    h_game: "Juego", h_cat: "Categoría", h_signals: "Señales", h_rating: "Valoración", h_players: "Jugadores", h_visits: "Visitas", h_age: "Edad",
    h_favs: "Favoritos", h_vpd: "Visitas/día", h_upd: "Actualizado",
    count: (n, total, p) => `${n} de ${total} juegos · ${p} jugadores en ellos ahora mismo`,
    empty: "Ningún juego coincide con estos filtros. Prueba quitando uno.", more: n => `Mostrar más (quedan ${n})`,
    noTag: "sin patrón detectado", by: "de", unknown: "desconocido", auto: "auto",
    reviewed: "Clasificación revisada a mano", autoTip: "Clasificado automáticamente por reglas, aún sin revisar",
    openStats: n => `Ver estadísticas de ${n}`,
    tracked: (n, p) => `<b>${n}</b> juegos seguidos · <b>${p}</b> jugadores concurrentes`, lastRefresh: d => `última lectura ${d} UTC · lecturas cada 2 h, actualización completa diaria`,
    footer: 'Haz clic en cualquier miniatura para ver estadísticas completas, la gráfica de jugadores, el grupo de Roblox del creador y sus redes. Los datos vienen de las APIs públicas de Roblox y se leen cada 2 horas; valoraciones, imágenes, redes y juegos nuevos se actualizan a diario a las 20:00 UTC. Las categorías y señales se asignaron leyendo nombre, descripción y género de cada juego — son un punto de partida para investigar, no un veredicto. "Copia de otro éxito" significa que la mecánica central sigue visiblemente a un juego anterior; "IP prestada" marca personajes o marcas con derechos de terceros.',
    loading: "Cargando datos del radar…", loadErr: "No se pudo cargar data/games.json — si abriste el archivo directamente, sirve la carpeta por http (GitHub Pages lo hace por ti).",
    st_now: "Jugadores ahora", st_rank: "Puesto por jugadores", st_peak: "Pico registrado", st_visits: "Visitas totales", st_vpd: "Visitas / día", st_rating: "Valoración",
    st_votes: "Votos", st_favs: "Favoritos", st_age: "Edad", st_upd: "Última actualización", st_server: "Tamaño de servidor", st_mat: "Madurez",
    today: "hoy", daysAgo: n => `hace ${n}d`, players: "jugadores", classifiedAs: "clasificado como", autoNote: "(auto, por reglas — aún sin revisar a mano)", added: "añadido",
    openRoblox: "Abrir en Roblox", group: "Grupo de Roblox", profile: "Perfil del creador",
    noSocials: "No se encontró Discord ni redes para este juego. Roblox solo muestra los Social Links a usuarios con sesión y 13+ — revisa la página del juego.",
    ch_title: "Jugadores concurrentes", ch_now: "ahora", ch_peak: "pico del rango", ch_low: "mínimo del rango", ch_avg: "promedio", ch_allPeak: "pico histórico registrado",
    ch_notEnough: "Aún no hay suficiente historial", ch_empty: "Aún no hay suficientes lecturas para este rango.", ch_peakLbl: "pico",
    ch_note: (n, h) => `${n} lecturas a lo largo de ${h} de seguimiento, una cada 2 horas. Roblox no publica historial de jugadores, así que esta gráfica solo crece mientras el radar sigue midiendo; más allá de 30 días conserva un pico diario por juego.`,
    underHour: "menos de una hora", hours: h => `${h} h`,
    r_24h: "24h", r_7d: "7d", r_30d: "1m", r_1y: "1a", r_all: "Todo",
    s_lang: "Idioma", s_lang_h: "Idioma de la interfaz", s_theme: "Tema", s_theme_h: "Sistema sigue el ajuste de tu equipo",
    t_system: "Sistema", t_dark: "Oscuro", t_light: "Claro",
    s_numbers: "Números", s_numbers_h: "Cómo se muestran jugadores y visitas en la tabla",
    s_cols: "Columnas visibles", s_cols_h: "Juego, categoría, señales y jugadores siempre se muestran",
    s_min: "Jugadores mínimos", s_min_h: "Oculta juegos por debajo de esta cantidad de jugadores",
    s_rows: "Filas por página", s_rows_h: "Más filas implica cargar más imágenes",
    s_remember: "Recordar filtros", s_remember_h: "Abrir la página con la última búsqueda, filtros y orden",
    s_hideauto: "Ocultar juegos clasificados automáticamente", s_hideauto_h: "Mostrar solo juegos con categoría revisada a mano",
    s_tz: "Hora de la gráfica", s_tz_h: "Zona horaria del eje de la gráfica", tz_local: "Local",
    s_saved: "Se guarda solo en este navegador.", s_reset: "Restablecer",
    v_games: "Juegos", v_market: "Mercado", m_byTags: "Por patrón", m_byCats: "Por categoría",
    m_hint: "Clic en una fila para ver sus juegos", m_note: "Cuota = porcentaje de todos los jugadores concurrentes seguidos. Nuevos 30d / 90d = juegos del grupo lanzados en esa ventana. Mediana de jugadores y valoración describen al juego típico del grupo, no al más grande. El crecimiento 7d es la mediana por juego y solo aparece cuando hay una semana de historial.",
    m_group: "Grupo", m_games: "Juegos", m_players: "Jugadores ahora", m_share: "Cuota", m_new30: "Nuevos 30d", m_new90: "Nuevos 90d", m_median: "Mediana jugadores", m_rating: "Valoración mediana", m_d7: "Crec. 7d", m_score: "Puntaje medio",
    m_all: "Todos los juegos seguidos",
    trend_any: "Cualquier tendencia", trend_rising: "Subiendo", trend_falling: "Bajando", trend_flat: "Estable", trend_new: "Nuevo (< 30 días)",
    tb_rising: "subiendo", tb_falling: "bajando", tb_flat: "estable", tb_new: "nuevo",
    h_d1: "24h", h_d7: "7d", h_d30: "30d", h_score: "Puntaje",
    sort_score_desc: "Puntaje de oportunidad ↓", sort_d7_desc: "Crecimiento 7d ↓", sort_d30_desc: "Crecimiento 30d ↓", sort_d1_desc: "Cambio 24h ↓",
    st_d1: "Cambio 24h", st_d7: "Cambio 7d", st_d30: "Cambio 30d",
    sc_title: "Puntaje de oportunidad", sc_hint: "0–100 · impulso, valoración, escala y frescura, menos riesgos de copia/IP. Una lista para investigar, no un consejo.",
    sc_momentum: "Impulso (crecimiento)", sc_rating: "Valoración", sc_scale: "Escala (jugadores)", sc_fresh: "Frescura (edad)", sc_engage: "Tracción (visitas/día)",
    sc_flagship: "Bono original insignia", sc_copycat: "Copia de otro éxito", sc_ip: "Riesgo de IP prestada", sc_pattern: "Fórmula saturada", sc_auto: "Sin revisar a mano",
    sc_noHist: "aún sin datos de crecimiento — impulso contado como neutro",
    coverage: (d, n) => `datos de tendencia: ${n} lecturas en ${d} días · las columnas 7d/30d se llenan al acumular historial`,
    own_any: "Cualquier dueño", own_group: "Propiedad de un grupo", own_user: "Propiedad de un usuario",
    h_members: "Tamaño grupo", h_rev: "Est. $/mes", h_passes: "Passes",
    bz_title: "Negocio", bz_hint: "Lo que mira un comprador: quién es el dueño, cómo monetiza y cuánto podría ganar.",
    bz_owner: "Dueño", bz_group: "Grupo (transferible)", bz_user: "Cuenta de usuario (no transferible)", bz_members: "Miembros del grupo", bz_groupAge: "Grupo creado",
    bz_passes: "Game passes", bz_priceRange: "Precios de passes", bz_vip: "Servidores privados", bz_paid: "Acceso de pago", bz_yes: "sí", bz_no: "no",
    bz_dau: "Jugadores diarios est. (DAU)", bz_rev: "Ganancia est. del desarrollador", bz_val: "Precio de venta típico", bz_perMonth: "/ mes",
    bz_note: "Solo estimaciones. DAU ≈ jugadores concurrentes promedio de las últimas 24 h × 12 (proporción habitual en Roblox). La ganancia asume $6–18 al mes por jugador concurrente promedio tras la comisión de Roblox (calibrado con casos públicos), ajustado por cómo monetiza el juego. En el mercado de compraventa se suele pedir 12–24× la ganancia mensual en juegos pequeños y medianos; los gigantes rara vez se venden. Roblox no publica nada de esto; úsalo como rango inicial para tu diligencia.",
    bz_pending: "Los datos de propiedad y monetización llegan con la próxima actualización diaria.",
    sc_group: "Propiedad de grupo (transferible)",
    lg_title: "Privacidad y aviso legal", lg_link: "Privacidad · Aviso legal",
    lg_html: `
<h3>Quién opera este sitio</h3>
<p>Roblox Radar es un proyecto personal e independiente. Contacto: <a href="mailto:Arturomed31@gmail.com">Arturomed31@gmail.com</a>.</p>
<h3>Privacidad</h3>
<p><b>Sin cuentas, sin cookies, sin rastreo.</b> Este sitio no tiene código de servidor ni analíticas. No recopila, almacena ni comparte datos personales.</p>
<ul>
<li><b>Solo almacenamiento local:</b> tus ajustes, filtros y notas en las gráficas se guardan en tu propio navegador (localStorage) y nunca salen de tu dispositivo. Al borrar los datos del navegador se eliminan.</li>
<li><b>Peticiones a terceros:</b> los iconos y miniaturas de los juegos se cargan directamente desde los servidores de imágenes de Roblox (tr.rbxcdn.com). Al pedirlos, Roblox recibe tu dirección IP y las cabeceras habituales, bajo la <a href="https://es.help.roblox.com/hc/es/articles/115004630823" target="_blank" rel="noopener">política de privacidad de Roblox</a>. Las fuentes se alojan en este sitio; no se envía nada a Google.</li>
<li><b>Alojamiento:</b> el sitio se sirve desde Cloudflare Pages y GitHub Pages, que pueden conservar registros estándar de servidor (IP, hora, archivo solicitado) por seguridad. Consulta <a href="https://www.cloudflare.com/privacypolicy/" target="_blank" rel="noopener">Cloudflare</a> y <a href="https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">GitHub</a>.</li>
</ul>
<h3>De dónde salen los datos</h3>
<p>Todas las estadísticas (jugadores, visitas, valoraciones, imágenes, nombres de creadores y grupos, enlaces sociales) provienen de las APIs web públicas de Roblox y se actualizan automáticamente. Solo se muestra información que Roblox ya publica.</p>
<h3>Sin relación con Roblox</h3>
<p>Este sitio no está respaldado, patrocinado ni afiliado a Roblox Corporation. Roblox y el logotipo de Roblox son marcas registradas de Roblox Corporation. Los nombres, imágenes y demás contenido de los juegos pertenecen a sus respectivos creadores y se muestran con fines de identificación e información.</p>
<h3>No es asesoría financiera</h3>
<p><b>Las estimaciones de jugadores diarios, ganancias del desarrollador y precios de venta son cálculos aproximados a partir de conteos públicos de jugadores y proporciones genéricas del sector.</b> Roblox no publica datos de ingresos. Las categorías, señales de patrón y el puntaje de oportunidad son opiniones editoriales generadas en parte por reglas automáticas. Nada en este sitio constituye asesoría financiera, de inversión ni legal; verifica todo de forma independiente antes de cualquier transacción.</p>
<h3>Solicitudes de retiro</h3>
<p>Si eres dueño de un juego o grupo listado aquí y quieres que se retire o corrija, escribe al correo de contacto y se atenderá con prontitud.</p>
<div class="legal-meta">Última actualización: septiembre de 2026</div>`,
    n_title: "Notas en esta gráfica", n_hint: "Haz clic en cualquier punto de la gráfica para fijar una nota en ese momento. Las notas se guardan en este navegador; expórtalas para conservarlas o compartirlas.",
    n_placeholder: "¿Qué pasó aquí? (actualización, promo, caída…)", n_save: "Guardar", n_cancel: "Cancelar", n_delete: "Borrar", n_edit: "Editar",
    n_empty: "Aún no hay notas.", n_export: "Exportar", n_import: "Importar", n_shared: "compartida", n_exported: "Notas exportadas", n_imported: n => `${n} notas importadas`,
    cats: {sim:'Simulador / Idle', rp:'Roleplay', shooter:'Shooter', fight:'Lucha / PvP', action:'Acción mundo abierto', obby:'Obby / Plataformas', sports:'Deportes y carreras', rpg:'RPG / Aventura', horror:'Terror / Supervivencia', party:'Fiesta / Casual', strategy:'Estrategia / TD', sandbox:'Sandbox / Construcción', fangame:'Fan game', other:'Herramienta / Otro'},
    tags: {'brainrot':'Brainrot','mm2-clone':'Clon de MM2','mm2-original':'MM2 (el original)','minecraft-clone':'Derivado de Minecraft','tower':'Torre','tower-defense':'Tower defense','steal-pattern':'Fórmula "Steal a X"','plus1-pattern':'Fórmula "+1 por clic"','duels-pattern':'Fórmula "DUELS"','rng-gacha':'Bucle RNG / gacha','copycat':'Copia de otro éxito','licensed-ip':'IP prestada','flagship':'Original insignia','anime':'Anime','meme':'Premisa meme'},
    signals: {'brainrot':'Temática brainrot','mm2-clone':'Clones de MM2','minecraft-clone':'Derivados de Minecraft','tower':'Torres','steal-pattern':'Fórmula "Steal a X"','plus1-pattern':'Fórmula "+1 por clic"','duels-pattern':'Arenas "DUELS"','copycat':'Copias de otros éxitos','licensed-ip':'IP prestada','flagship':'Originales insignia'},
    socials: {discord:'Discord', youtube:'YouTube', x:'X / Twitter', tiktok:'TikTok', twitch:'Twitch', facebook:'Facebook', guilded:'Guilded', group:'Grupo vinculado'},
    months: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
  }
};
