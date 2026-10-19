// Screenshot helper: renders a page from the local server and saves a PNG.
// Usage: CHROMIUM_BIN=... node tests/shot.cjs <page> <width> <height> <out.png> [query]
const {spawn} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const http = require('node:http');

const root = path.resolve(__dirname, '..');
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'shot-'));
const server = http.createServer((req, res) => {
  const pathname = new URL(req.url, 'http://localhost').pathname;
  if (!/^\/(index\.html|free_models\.html|data\/[a-z0-9_]+\.(js|json))$/.test(pathname)) {
    res.writeHead(404).end(); return;
  }
  try {
    res.setHeader('Content-Type', pathname.endsWith('.html') ? 'text/html; charset=utf-8' : 'text/javascript; charset=utf-8');
    res.end(fs.readFileSync(path.join(root, pathname)));
  } catch { res.writeHead(404).end(); }
});
let browser, socket;
async function main() {
  const [page, width, height, out, query = ''] = process.argv.slice(2);
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  browser = spawn(process.env.CHROMIUM_BIN, ['--no-sandbox', '--headless', '--disable-gpu', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank']);
  const browserWS = await new Promise((resolve, reject) => {
    let output = '';
    browser.stderr.on('data', d => {
      output += d;
      const match = output.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) resolve(match[1]);
    });
    browser.on('error', reject);
  });
  const endpoint = new URL(browserWS);
  const target = await fetch(`http://${endpoint.host}/json/new?${encodeURIComponent('about:blank')}`, {method: 'PUT'}).then(r => r.json());
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  let seq = 0; const pending = new Map();
  socket.onmessage = ({data}) => {
    const msg = JSON.parse(data); const p = pending.get(msg.id);
    if (p) { pending.delete(msg.id); msg.error ? p.reject(Error(JSON.stringify(msg.error))) : p.resolve(msg.result); }
  };
  const command = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++seq; pending.set(id, {resolve, reject}); socket.send(JSON.stringify({id, method, params}));
  });
  await command('Emulation.setDeviceMetricsOverride', {width: +width, height: +height, deviceScaleFactor: 1, mobile: false});
  await command('Page.navigate', {url: `${base}/${page}${query}`});
  await new Promise(r => setTimeout(r, 2500));
  const shot = await command('Page.captureScreenshot', {format: 'png', captureBeyondViewport: true});
  fs.writeFileSync(out, Buffer.from(shot.data, 'base64'));
  console.log('saved', out);
}
main().catch(e => { console.error(e); process.exitCode = 1; }).finally(() => {
  socket?.close(); browser?.kill(); server.close(); browser?.on('exit', () => fs.rmSync(profile, {recursive: true, force: true}));
});
