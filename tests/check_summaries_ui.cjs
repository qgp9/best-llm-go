// No npm dependencies. Run with CHROMIUM_BIN=/path/to/chrome node tests/check_summaries_ui.cjs.
const {spawn} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const http = require('node:http');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'best-llm-ui-'));
const server = http.createServer((req, res) => {
  const pathname = new URL(req.url, 'http://localhost').pathname;
  if (!/^\/(index\.html|free_models\.html|data\/[a-z0-9_]+\.(js|json))$/.test(pathname)) {
    res.writeHead(404).end(); return;
  }
  try {
    res.setHeader('Content-Type', pathname.endsWith('.html') ? 'text/html; charset=utf-8' : pathname.endsWith('.js') ? 'text/javascript; charset=utf-8' : 'application/json');
    res.end(fs.readFileSync(path.join(root, pathname)));
  } catch { res.writeHead(404).end(); }
});
let browser;
let socket;
async function main() {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  browser = spawn(process.env.CHROMIUM_BIN, ['--no-sandbox', '--headless', '--disable-gpu', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank']);
  const browserWS = await new Promise((resolve, reject) => {
    let output = '';
    browser.stderr.on('data', b => {
      output += b;
      const match = output.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) resolve(match[1]);
    });
    browser.on('error', reject);
    browser.on('exit', code => reject(Error(`browser exited ${code}`)));
  });
  const endpoint = new URL(browserWS);
  const target = await fetch(`http://${endpoint.host}/json/new?${encodeURIComponent('about:blank')}`, {method: 'PUT'}).then(r=>r.json());
  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  let sequence=0;
  const pending = new Map();
  socket.onmessage = ({data}) => {
    const message = JSON.parse(data);
    const p = pending.get(message.id);
    if (p) { pending.delete(message.id); message.error ? p.reject(Error(JSON.stringify(message.error))) : p.resolve(message.result); }
  };
  function command(method, params={}) {
    return new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}));});
  }
  async function evaluate(expression) {
    const result=await command('Runtime.evaluate',{expression,returnByValue:true});
    if(result.exceptionDetails) throw Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  }
  for (const page of ['index.html','free_models.html']) {
    await command('Page.navigate',{url:`${base}/${page}?lang=ko`});
    for(let i=0;i<200;i++) {
      if(await evaluate(`location.pathname === '/${page}' && document.readyState === 'complete' && !!window.I18N && !!window.__SUMMARIES__`)) break;
      await new Promise(resolve=>setTimeout(resolve,50));
      if(i===199) throw Error('page did not initialize');
    }
    const go=page==='index.html';
    const id=go?'go-overall':'free-overall';
    const selector=go?'aiSummaryCard':'aiSummaryBox';
    const text=go?`document.getElementById('aiSummaryText').textContent`:`document.getElementById('aiSummaryBox').textContent`;
    const result = await evaluate(`(() => {
      const s=window.__SUMMARIES__['${id}'];
      I18N.setLanguage('ko'); const ko=${text};
      I18N.setLanguage('en'); const en=${text};
      delete window.__SUMMARIES__['${id}']; I18N.setLanguage('ko');
      const hidden=document.getElementById('${selector}').style.display==='none';
      window.__SUMMARIES__['${id}']=s; I18N.setLanguage('ko');
      return {ko:ko.includes(s.ko), en:en.includes(s.en), hidden,
              restored:document.getElementById('${selector}').style.display==='block'};
    })()`);
    assert.deepEqual(result,{ko:true,en:true,hidden:true,restored:true});
    console.log(`${page}: ko/en, missing summary hidden, restored summary visible: PASS`);
    const sets = await evaluate(`(() => {
      const cases = ${go ? "[['go-overall','go-overall'],['go-coding','go-coding'],['go-budget','go-budget']]" : "[['free-overall','all'],['free-coding','coding'],['free-reasoning','reasoning'],['free-longcontext','long_context'],['free-fast','lightweight'],['free-private','private']]"};
      return cases.map(([id, filter]) => {
        if (${go}) document.querySelector('[data-aiset="'+filter+'"]').click();
        else if (filter === 'private') document.getElementById('safeOnlyChk').click();
        else document.querySelector('#categoryFilterBar [data-cat="'+filter+'"]').click();
        I18N.setLanguage('ko'); const ko=${text};
        I18N.setLanguage('en'); const en=${text};
        const summary=window.__SUMMARIES__[id];
        return {id, ok:ko.includes(summary.ko) && en.includes(summary.en)
                   && document.getElementById('${selector}').style.display==='block'};
      });
    })()`);
    assert.ok(sets.every(result=>result.ok), JSON.stringify(sets));
    console.log(`${page}: ${sets.length} summary selectors in ko/en: PASS`);
  }
}
const timeout=setTimeout(()=>{console.error('UI check timed out');process.exitCode=1;socket?.close();browser?.kill();server.close();},30000);
main().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>{
  clearTimeout(timeout);socket?.close();browser?.kill();server.close();
  browser?.on('exit',()=>fs.rmSync(profile,{recursive:true,force:true}));
});
