import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import { createHash } from 'node:crypto';
import { createServer } from '../server.mjs';

async function load() {
  const context = vm.createContext({ window: {} });
  for (const name of ['skills.js', 'preview-data.js', 'skill-previews.js']) {
    vm.runInContext(await readFile('public/' + name, 'utf8'), context);
  }
  return context.window;
}

test('every published skill has a local result preview with honest provenance', async () => {
  const { SKILL_DATA: data, SKILL_PREVIEW_DATA: previews, SkillPreviews: renderer } = await load();
  const items = [...data.skills, ...data.collections];
  assert.equal(Object.keys(previews).length, items.length);
  for (const item of items) {
    const preview = previews[item.id];
    assert.ok(preview, item.id);
    assert.ok(preview.caption.length > 15, item.id);
    assert.match(preview.sampleSrc, /^assets\/previews\/[a-z0-9-]+-sample\.webp$/);
    if (preview.credit) {
      assert.equal(preview.label, "Creator's example");
      assert.match(preview.credit.url, /^https:\/\//);
      assert.ok(preview.credit.name.length > 2);
    } else assert.equal(preview.label, 'Sample output');
    for (const image of [...preview.images, { src: preview.sampleSrc, width: 960, height: 600 }]) {
      assert.match(image.src, /^assets\/previews\/[a-z0-9-]+\.webp$/);
      assert.ok(Number.isInteger(image.width) && image.width > 200);
      assert.ok(Number.isInteger(image.height) && image.height > 100);
      const bytes = await readFile('public/' + image.src);
      assert.equal(bytes.toString('ascii', 0, 4), 'RIFF');
      assert.equal(bytes.toString('ascii', 8, 12), 'WEBP');
      assert.ok(bytes.length > 1000, image.src);
    }
    const markup = renderer.markup(item.id);
    assert.match(markup, /See the result/);
    assert.match(markup, /Open larger/);
    assert.match(markup, /loading="lazy"/);
    assert.match(markup, /width="\d+" height="\d+"/);
  }
});

test('preview markup rejects private paths and escapes labels and credits', async () => {
  const source = await readFile('public/skill-previews.js', 'utf8');
  const context = vm.createContext({ window: { SKILL_PREVIEW_DATA: {
    bad: { images: [{ src: '../../data/lessons.json' }] },
    safe: { title: '<script>title</script>', label: '<img src=x>', caption: 'A & B',
      images: [{ src: 'assets/previews/demo.webp', alt: '" onerror="alert(1)', width: 960, height: 600 }],
      credit: { name: '<b>author</b>', url: 'javascript:alert(1)' } }
  } } });
  vm.runInContext(source, context);
  assert.equal(context.window.SkillPreviews.markup('bad'), '');
  assert.equal(context.window.SkillPreviews.markup('missing'), '');
  const markup = context.window.SkillPreviews.markup('safe');
  assert.ok(!markup.includes('<script>'));
  assert.ok(!markup.includes('<b>author</b>'));
  assert.ok(!markup.includes('href="javascript:'));
  assert.ok(!markup.includes(' onerror="'));
  assert.match(markup, /&lt;script&gt;/);
});

test('preview data and renderer load before the library controller', async () => {
  const shelf = await readFile('public/shelf.html', 'utf8');
  assert.ok(shelf.indexOf('./preview-data.js?') < shelf.indexOf('./skill-previews.js?'));
  assert.ok(shelf.indexOf('./skill-previews.js?') < shelf.indexOf('./shelf.js?'));
  for (const name of ['public/shelf.html', 'public/index.html']) {
    const page = await readFile(name, 'utf8');
    assert.match(page, /skill-previews\.css\?v=/);
    assert.match(page, /preview-data\.js\?v=/);
    assert.match(page, /skill-previews\.js\?v=/);
  }
});

test('local preview routes work without exposing source or private files', async () => {
  const server = createServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + server.address().port;
  try {
    for (const path of ['/preview-data.js', '/skill-previews.js', '/skill-previews.css', '/assets/previews/manifest.json', '/assets/previews/unslop-after.webp', '/assets/previews/xlsx-sample.webp']) {
      assert.equal((await fetch(base + path)).status, 200, path);
    }
    for (const path of ['/scripts/preview-source-audit.json', '/assets/previews/creator-candidates.json', '/assets/previews/not-an-example.webp']) {
      assert.equal((await fetch(base + path)).status, 404, path);
    }
  } finally { await new Promise(resolve => server.close(resolve)); }
});

test('homepage inline scripts are allowed after browser line-ending normalization', async () => {
  const server = createServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    const response = await fetch('http://127.0.0.1:' + server.address().port + '/index.html');
    const html = await response.text();
    const policy = response.headers.get('content-security-policy');
    const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)].filter(match => match[1].trim());
    assert.ok(scripts.length >= 2);
    for (const [, source] of scripts) {
      const browserText = source.replace(/\r\n?/g, '\n');
      assert.ok(policy.includes("'sha256-" + createHash('sha256').update(browserText).digest('base64') + "'"));
    }
    assert.ok(!policy.includes("script-src 'unsafe-inline'"));
  } finally { await new Promise(resolve => server.close(resolve)); }
});
