import { createServer } from 'node:http';
import { spawn, spawnSync } from 'node:child_process';
import { readFile, readdir, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.dirname(fileURLToPath(import.meta.url));
const jar = path.join(root, 'lib', 'plantuml.jar');
const diagramsDir = path.join(root, 'diagrams');
const port = Number(process.env.PORT) || 8765;
const hasDot = spawnSync('which', ['dot']).status === 0;
const FORMATS = { svg: 'image/svg+xml', png: 'image/png' };

// UI language -> PlantUML -D flag (diagrams opt in with !ifdef; en = no flag)
const LANGS = { en: null, 'zh-tw': '-DLANG_ZH_TW=1', ja: '-DLANG_JA=1', ko: '-DLANG_KO=1' };

// Working directories PlantUML may run in (relative !include / %load_json resolve against cwd).
// The editor root is always available; extra folders come only from the PUML_BASE_DIRS allowlist.
const baseDirs = new Map([['default', { name: 'Editor folder', dir: root }]]);
for (const d of (process.env.PUML_BASE_DIRS ?? '').split(':').filter(Boolean)) {
  const dir = path.resolve(d);
  if (!existsSync(dir)) { console.warn('PUML_BASE_DIRS: skipping missing folder', dir); continue; }
  let id = path.basename(dir), n = 2;
  while (baseDirs.has(id)) id = `${path.basename(dir)}-${n++}`;
  baseDirs.set(id, { name: id, dir });
}

function render(code, format, lang, cwd) {
  return new Promise((resolve, reject) => {
    // PLANTUML_LIMIT_SIZE: default cuts images taller than 4096px
    const args = ['-Djava.awt.headless=true', '-DPLANTUML_LIMIT_SIZE=16384', '-jar', jar, '-pipe', `-t${format}`, '-charset', 'UTF-8'];
    if (LANGS[lang]) args.push(LANGS[lang]);
    if (!hasDot) args.push('-Playout=smetana'); // pure-Java layout when Graphviz is missing
    const p = spawn('java', args, { cwd });
    const out = [], err = [];
    p.stdout.on('data', (d) => out.push(d));
    p.stderr.on('data', (d) => err.push(d));
    p.on('error', reject);
    p.on('close', (c) => (out.length ? resolve(Buffer.concat(out)) : reject(new Error(Buffer.concat(err).toString() || `PlantUML exited with ${c} and no output`))));
    p.stdin.end(code);
  });
}

const readBody = async (req) => {
  let s = '';
  for await (const c of req) s += c;
  return s;
};
const safeName = (n) => /^[\w .-]+$/.test(n) && !n.includes('..');

const server = createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  try {
    if (req.method === 'GET' && url.pathname === '/') {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end(await readFile(path.join(root, 'public', 'index.html')));
    }
    if (req.method === 'POST' && url.pathname === '/render') {
      const format = url.searchParams.get('format') ?? 'svg';
      if (!FORMATS[format]) { res.writeHead(400); return res.end('bad format'); }
      const lang = url.searchParams.get('lang') ?? 'en';
      const base = baseDirs.get(url.searchParams.get('dir') ?? 'default');
      if (!(lang in LANGS) || !base) { res.writeHead(400); return res.end('bad lang or dir'); }
      const img = await render(await readBody(req), format, lang, base.dir);
      res.writeHead(200, { 'Content-Type': FORMATS[format] });
      return res.end(img);
    }
    if (req.method === 'GET' && url.pathname === '/config') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ dirs: [...baseDirs].map(([id, v]) => ({ id, name: v.name })) }));
    }
    if (req.method === 'GET' && url.pathname === '/files') {
      await mkdir(diagramsDir, { recursive: true });
      const names = (await readdir(diagramsDir)).filter((f) => f.endsWith('.puml')).sort();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify(names));
    }
    const m = url.pathname.match(/^\/files\/(.+)$/);
    if (m) {
      const name = decodeURIComponent(m[1]);
      if (!safeName(name) || !name.endsWith('.puml')) { res.writeHead(400); return res.end('bad name'); }
      const file = path.join(diagramsDir, name);
      if (req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
        return res.end(await readFile(file));
      }
      if (req.method === 'PUT') {
        await mkdir(diagramsDir, { recursive: true });
        await writeFile(file, await readBody(req));
        res.writeHead(204);
        return res.end();
      }
    }
    res.writeHead(404);
    res.end('not found');
  } catch (e) {
    res.writeHead(500);
    res.end(String(e.message));
  }
});

if (!existsSync(jar)) {
  const src = 'https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar';
  console.log('lib/plantuml.jar missing, downloading from', src);
  const r = await fetch(src);
  if (!r.ok) throw new Error(`download failed: HTTP ${r.status}`);
  await mkdir(path.dirname(jar), { recursive: true });
  await writeFile(jar, Buffer.from(await r.arrayBuffer()));
}

server.listen(port, '127.0.0.1', () => {
  console.log(`PlantUML editor: http://localhost:${port}  (layout: ${hasDot ? 'Graphviz' : 'smetana'})`);
});
