// Add skills you installed on this PC to the app.
//
//   npm run add-skills                         -> lists installed skills the app does not show yet, with a draft card for each. Changes nothing.
//   npm run add-skills -- --yes                -> adds all of those drafts (card + artwork) to the app
//   npm run add-skills -- --yes --only a,b     -> adds only skills a and b
//   npm run add-skills -- --ignore a,b         -> never offer a and b again (kept in scripts/add-skills.ignore.json)
//   npm run add-skills -- --repo owner/name    -> with --yes: sets the GitHub repo these skills came from, so each card shows install steps
//
// Where it looks: ~/.claude/skills (change with --dir <folder>). A skill counts as "already in the app" if its folder
// name is a skill id, a pack member, or a collection id in public/skills.js.
// What it writes: a card in public/skills.js, a spare 3D icon copied into public/assets/skills (plus manifest.json,
// skill-images.js, sw.js), and new ?v= tags. The draft wording is plain and short: read it in skills.js and polish it,
// then run `npm test` and `npm run push-site`.
import { readFileSync, writeFileSync, readdirSync, existsSync, copyFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const P = (...a) => join(root, ...a);
const args = process.argv.slice(2);
const flag = n => args.includes(n);
const val = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : ''; };
const list = n => (val(n) || '').split(',').map(s => s.trim()).filter(Boolean);

const skillsDir = val('--dir') || join(homedir(), '.claude', 'skills');
const ignoreFile = P('scripts', 'add-skills.ignore.json');
const ignored = new Set(existsSync(ignoreFile) ? JSON.parse(readFileSync(ignoreFile, 'utf8')) : []);

if (flag('--ignore')) {
  list('--ignore').forEach(id => ignored.add(id));
  writeFileSync(ignoreFile, JSON.stringify([...ignored].sort(), null, 2) + '\n');
  console.log('Will not offer again: ' + [...ignored].sort().join(', '));
  process.exit(0);
}

// ---- what the app already has
const loadData = () => {
  const ctx = vm.createContext({ window: {} });
  vm.runInContext(readFileSync(P('public', 'skills.js'), 'utf8'), ctx);
  return ctx.window.SKILL_DATA;
};
const data = loadData();
const known = new Set();
for (const s of data.skills) { known.add(s.id); (s.members || []).forEach(m => known.add(m[0])); }
(data.collections || []).forEach(c => known.add(c.id));

// ---- what is installed
function frontmatter(text) {
  const m = text.replace(/^﻿/, '').match(/^---\r?\n([\s\S]*?)\r?\n---/);
  const out = {};
  if (!m) return out;
  const lines = m[1].split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const kv = lines[i].match(/^([\w-]+):\s*(.*)$/);
    if (!kv) continue;
    let v = kv[2].trim();
    if (/^[>|][+-]?$/.test(v)) { v = ''; while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1])) v += ' ' + lines[++i].trim(); }
    else if (v === '') { while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1])) v += ' ' + lines[++i].trim(); }
    out[kv[1]] = v.trim().replace(/^(["'])([\s\S]*)\1$/, '$2').trim();
  }
  return out;
}
if (!existsSync(skillsDir)) { console.error('No skills folder at ' + skillsDir); process.exit(1); }
const installed = [];
for (const d of readdirSync(skillsDir, { withFileTypes: true })) {
  if (!d.isDirectory() && !d.isSymbolicLink()) continue;
  const file = join(skillsDir, d.name, 'SKILL.md');
  if (!existsSync(file)) continue;
  installed.push({ id: d.name, ...frontmatter(readFileSync(file, 'utf8')) });
}
const fresh = installed.filter(s => /^[a-z0-9-]+$/.test(s.id) && !known.has(s.id) && !ignored.has(s.id));

// ---- drafts
const CATS = [
  ['motion', '✨', /animat|motion|3d|video|gsap|three|shader|render|gif/],
  ['design', '🎨', /design|\bui\b|\bux\b|css|layout|brand|figma|colou?r|typograph|website|landing/],
  ['docs', '📄', /\bpdf\b|slide|docx|word document|spreadsheet|powerpoint|\bxlsx\b|\bdoc\b/],
  ['writing', '✍️', /writ|research|summar|translat|email|essay|copy|reddit|news|learn/],
  ['coding', '🛠️', /code|test|debug|\bapi\b|review|\bgit\b|deploy|build|database|security|refactor|plan|\bcli\b/]
];
const guess = text => { const t = text.toLowerCase(); for (const [id, icon, re] of CATS) if (re.test(t)) return { cat: id, icon }; return { cat: 'workflow', icon: '🧠' }; };
const titleCase = id => id.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
const clean = t => String(t || '').replace(/\s+/g, ' ').replace(/^Use (this skill )?(it )?(when|whenever) (the user|someone|you|a user)( wants to| want to| asks (for|to)| is)? ?/i, '').trim();
const sentence = (t, id) => { const f = clean(t); const m = f.match(/^(.{20,150}?[.!?])(\s|$)/); let s = m ? m[1] : f.slice(0, 150); if (!m && f.length > 150) { const cut = Math.max(s.lastIndexOf(', '), s.lastIndexOf(' - '), s.lastIndexOf(' — '), s.lastIndexOf('; ')); s = cut >= 40 ? s.slice(0, cut) : s.replace(/\s+\S*$/, ''); } s = s.trim(); if (s.length < 15) s = 'Adds the ' + id + ' skill to Claude.'; s = s.charAt(0).toUpperCase() + s.slice(1); return /[.!?]$/.test(s) ? s : s + '.'; };
const uses = (id, t) => {
  const parts = clean(t).replace(/\([^)]*\)/g, '').replace(/\betc\.?/gi, '').split(/[.;]\s+|\s[-—]\s|,\s(?:and\s)?/).map(s => s.trim().replace(/\.$/, '')).filter(s => s.length > 8 && s.length <= 70);
  const out = parts.slice(1, 4);
  while (out.length < 2) out.push(['Ask Claude to use ' + id, 'Try it on one small, real task'][out.length]);
  return out.map(s => s.charAt(0).toUpperCase() + s.slice(1));
};
const drafts = fresh.map(s => {
  const text = s.description || s.id;
  const { cat, icon } = guess(s.id + ' ' + text);
  return { id: s.id, title: titleCase(s.id), cat, icon, level: 'medium', what: sentence(text, s.id), useFor: uses(s.id, text), say: `Use ${s.id} for this: <describe what you want>` };
});

if (!drafts.length) { console.log(`Nothing new. All ${installed.length} skills in ${skillsDir} are already in the app, a pack, or ignored.`); process.exit(0); }

const only = list('--only');
const chosen = only.length ? drafts.filter(d => only.includes(d.id)) : drafts;
const unknownOnly = only.filter(id => !drafts.some(d => d.id === id));
if (unknownOnly.length) { console.error('Not on the list: ' + unknownOnly.join(', ')); process.exit(2); }

if (!flag('--yes')) {
  console.log(`${drafts.length} installed skill(s) are not in the app yet (looked in ${skillsDir}):\n`);
  for (const d of drafts) console.log(`  ${d.icon} ${d.id}  [${d.cat}, ${d.level}]\n     ${d.what}\n     say: ${d.say}`);
  console.log('\nNothing was changed. Next:');
  console.log('  npm run add-skills -- --yes                    add all of them');
  console.log('  npm run add-skills -- --yes --only a,b         add some');
  console.log('  npm run add-skills -- --ignore a,b             never offer some again (helpers that belong to a pack, for example)');
  process.exit(0);
}

// ---- apply
const repo = val('--repo');
if (repo && !/^[\w.-]+\/[\w.-]+$/.test(repo)) { console.error('--repo must look like owner/name'); process.exit(2); }
const q = t => "'" + String(t).replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "'";

// spare icons: not yet used by any skill (compared by file hash, because the tests need different art per skill)
const manifestPath = P('public', 'assets', 'skills', 'manifest.json');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const used = new Set(manifest.map(m => m.sha256));
const spare = JSON.parse(readFileSync(P('public', 'assets', 'future-skills', 'manifest.json'), 'utf8')).filter(m => !used.has(m.sha256));
const takeIcon = cat => { let i = spare.findIndex(m => m.category === cat); if (i < 0) i = 0; return spare.splice(i, 1)[0]; };
if (spare.length < chosen.length) {
  console.error(`Only ${spare.length} spare icon(s) are left in public/assets/future-skills, but ${chosen.length} skill(s) need one. Add more icons there, or use --only.`);
  process.exit(1);
}

let js = readFileSync(P('public', 'skills.js'), 'utf8');
let sourceId = 'downloaded';
if (repo) {
  sourceId = repo.split('/')[1].toLowerCase().replace(/[^a-z0-9]/g, '');
  if (!data.sources[sourceId]) {
    const line = `    ${sourceId}: { name: ${q(repo)}, url: ${q('https://github.com/' + repo)}, repo: ${q(repo)}, branch: 'main', dir: 'skills' },\n`;
    if (!js.includes('    claudeapp: {')) { console.error('skills.js layout changed: cannot place the source.'); process.exit(1); }
    js = js.replace('    claudeapp: {', line + '    claudeapp: {');
  }
}
const today = new Date().toISOString().slice(0, 10);
const entries = [], images = [];
for (const d of chosen) {
  const icon = takeIcon(d.cat);
  for (const f of ['png', 'webp']) copyFileSync(P('public', 'assets', 'future-skills', icon[f]), P('public', 'assets', 'skills', `${d.id}.${f}`));
  manifest.push({ id: d.id, title: d.title, category: d.cat, png: `${d.id}.png`, webp: `${d.id}.webp`, uploadSize: 512, appSize: 256, transparent: true,
    sha256: createHash('sha256').update(readFileSync(P('public', 'assets', 'skills', `${d.id}.png`))).digest('hex') });
  images.push(d.id);
  entries.push(`    { id: ${q(d.id)}, title: ${q(d.title)}, cat: ${q(d.cat)}, icon: ${q(d.icon)}, level: ${q(d.level)}, src: ${q(sourceId)},
      what: ${q(d.what)},
      useFor: [${d.useFor.map(q).join(', ')}],
      say: ${q(d.say)} }`);
}
const tail = /\}\s*\n  \]\n\};\s*$/;
if (!tail.test(js)) { console.error('skills.js layout changed: cannot find the end of the skills list.'); process.exit(1); }
js = js.replace(/\}(\s*)\n  \]\n\};\s*$/, `},\n\n    // ---------- Added ${today} (npm run add-skills: check the wording) ----------\n${entries.join(',\n')}\n  ]\n};\n`);
writeFileSync(P('public', 'skills.js'), js);
writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n');

const imPath = P('public', 'skill-images.js');
let im = readFileSync(imPath, 'utf8');
if (!/\n\]\);/.test(im)) { console.error('skill-images.js layout changed.'); process.exit(1); }
im = im.replace(/"\n\]\);/, `",\n${images.map(i => `  "${i}"`).join(',\n')}\n]);`);
writeFileSync(imPath, im);

const swPath = P('public', 'sw.js');
let sw = readFileSync(swPath, 'utf8');
sw = sw.replace(/\.webp"\];/, `.webp",${images.map(i => `"assets/skills/${i}.webp"`).join(',')}];`);
// new cache tags so phones fetch the new data
const tag = 'v' + today.replace(/-/g, '') + '-' + Math.random().toString(36).slice(2, 6);
for (const f of ['skills.js', 'skill-images.js']) {
  for (const p of ['public/index.html', 'public/shelf.html']) {
    const file = P(...p.split('/')); const t = readFileSync(file, 'utf8');
    writeFileSync(file, t.replace(new RegExp(`${f.replace('.', '\\.')}\\?v=[\\w-]+`, 'g'), `${f}?v=${tag}`));
  }
  sw = sw.replace(new RegExp(`${f.replace('.', '\\.')}\\?v=[\\w-]+`, 'g'), `${f}?v=${tag}`);
}
sw = sw.replace(/(const CACHE = 'ai-skill-shelf-art-v)(\d+)'/, (_, a, n) => `${a}${+n + 1}'`);
writeFileSync(swPath, sw);

// check the result loads
const after = loadData();
for (const d of chosen) if (!after.skills.some(s => s.id === d.id)) { console.error('Something went wrong: ' + d.id + ' is missing after writing.'); process.exit(1); }
console.log(`Added ${chosen.length}: ${chosen.map(d => d.id).join(', ')}`);
console.log('Next: open public/skills.js (search "Added ' + today + '"), polish the wording, then:\n  npm test\n  npm run push-site');
