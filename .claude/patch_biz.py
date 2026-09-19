import re
p='index.html'; s=open(p,encoding='utf-8').read()
old="""  const [gamesDoc, hist, shared] = await Promise.all([
    fetch('data/games.json' + bust).then(r => r.json()),
    fetch('data/history.json' + bust).then(r => r.json()),
    fetch('data/notes.json' + bust).then(r => r.ok ? r.json() : {}).catch(() => ({}))
  ]);
  SHARED_NOTES = shared && typeof shared === 'object' ? shared : {};
  const now = Date.now();
  gamesDoc.games.forEach(g => {
"""
new="""  const [gamesDoc, hist, shared, biz] = await Promise.all([
    fetch('data/games.json' + bust).then(r => r.json()),
    fetch('data/history.json' + bust).then(r => r.json()),
    fetch('data/notes.json' + bust).then(r => r.ok ? r.json() : {}).catch(() => ({})),
    fetch('data/business.json' + bust).then(r => r.ok ? r.json() : {}).catch(() => ({}))
  ]);
  SHARED_NOTES = shared && typeof shared === 'object' ? shared : {};
  const BIZ = biz && typeof biz === 'object' ? biz : {};
  const now = Date.now();
  gamesDoc.games.forEach(g => {
    // business data (groups, passes, social links) lives in its own file
    const b = BIZ[String(g.id)];
    if (b) {
      for (const k of ['gp', 'grp', 'vip', 'paid', 'enrichedAt']) if (b[k] !== undefined) g[k] = b[k];
      if (Array.isArray(b.socials) && b.socials.length) g.socials = b.socials;
    }
"""
assert old in s
s=s.replace(old,new)
open(p,'w',encoding='utf-8',newline='').write(s)
print('ok')
