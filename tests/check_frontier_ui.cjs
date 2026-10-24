// No npm dependencies. Run with CHROMIUM_BIN=/path/to/chrome node tests/check_frontier_ui.cjs.
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
  requests.push(pathname);
  if (!/^\/(index\.html|free_models\.html|data\/[a-z0-9_]+\.(js|json))$/.test(pathname)) {
    res.writeHead(404).end(); return;
  }
  try {
    res.setHeader('Content-Type', pathname.endsWith('.html') ? 'text/html; charset=utf-8' : pathname.endsWith('.js') ? 'text/javascript; charset=utf-8' : 'application/json');
    res.end(fs.readFileSync(path.join(root, pathname)));
  } catch { res.writeHead(404).end(); }
});
const requests = [];
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
  const errors=[];
  const receive=socket.onmessage;
  socket.onmessage=event=>{ const m=JSON.parse(event.data); if(m.method==='Runtime.exceptionThrown') errors.push(m.params.exceptionDetails); receive(event); };
  await command('Runtime.enable');
  async function navigate(page,query='') {
    await evaluate(`document.getElementById('conditionAnalysis')?.removeAttribute('data-frontier-ids')`);
    await command('Page.navigate',{url:base+'/'+page+'?lang=ko'+(page==='index.html'?'&cost=go_effective&mode=all&scope=go_only':'')+query});
    for(let i=0;i<200;i++) {
      if(await evaluate(`location.pathname === '/${page}' && document.readyState === 'complete' && !!window.I18N && ${page==='index.html' ? "!!document.getElementById('conditionAnalysis')?.dataset.frontierIds" : "!!document.querySelector('#categoryFilterBar')"}`)) {
        if(page==='index.html') await evaluate(`(() => {const original=FrontierAnalysis.analyze; FrontierAnalysis.analyze=(rows,opts)=>{const a=original(rows,opts); window.__analysis=a;return a;}; I18N.setLanguage(I18N.lang);})()`);
        return;
      }
      await new Promise(resolve=>setTimeout(resolve,50));
    }
    throw Error('page did not initialize '+JSON.stringify({errors,diagnostic:await evaluate(`({url:location.href,ready:document.readyState,i18n:!!window.I18N,analysis:!!window.__analysis,api:!!window.FrontierAnalysis})`)}));
  }
  async function check(label) {
    const result=await evaluate(`(() => {
      const box=document.getElementById('conditionAnalysis');
      return {graph:JSON.parse(document.getElementById('scatter').dataset.frontierIds),
        markers:[...document.querySelectorAll('#scatter .hit[data-frontier="true"]')].map(d=>d.dataset.modelId).sort(),
        analysis:JSON.parse(box.dataset.frontierIds),
        candidates:JSON.parse(box.dataset.candidateIds), text:box.textContent,
        expected:__analysis.frontier.map(d=>d.id),
        priced:__analysis.priced.length, free:__analysis.free.length};
    })()`);
    assert.deepEqual(result.graph,result.analysis,label);
    assert.deepEqual(result.graph,result.expected,label);
    assert.deepEqual([...result.graph].sort(),result.markers,label);
    assert.ok(result.text.length>50,label);
    console.log(label+': PASS ('+result.priced+' priced, '+result.graph.length+' frontier, '+result.free+' free)');
    return result;
  }
  await navigate('index.html');
  let result=await check('default');
  console.log('EXAMPLE default: '+result.text);
  if(process.env.ANALYSIS_SCREENSHOT) {
    const clip=await evaluate(`(() => {const r=document.getElementById('conditionAnalysis').getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height,scale:1};})()`);
    const shot=await command('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip});
    fs.writeFileSync(process.env.ANALYSIS_SCREENSHOT,Buffer.from(shot.data,'base64'));
  }
  for(const axis of ['go_effective','go_task','task','go_quota','blended']) {
    await evaluate(`document.querySelector('[data-cost="${axis}"]').click()`);
    const before=await check(axis);
    await evaluate(`document.getElementById('frontierOnly').click()`);
    const after=await check(axis+' frontier only');
    assert.deepEqual(before.candidates,after.candidates);
    assert.equal(before.text,after.text);
    await evaluate(`document.getElementById('frontierOnly').click()`);
    if(axis==='go_task') console.log('EXAMPLE Go /task: '+after.text);
  }
  // Each control must change the same candidate pool used by graph and analysis.
  await evaluate(`document.querySelector('[data-cost="go_effective"]').click(); document.getElementById('makerSel').value=__analysis.priced[0].creator; document.getElementById('makerSel').dispatchEvent(new Event('change'))`);
  result=await check('manufacturer');
  assert.ok(await evaluate(`__analysis.candidates.every(d=>d.creator===document.getElementById('makerSel').value)`));
  console.log('EXAMPLE manufacturer: '+result.text);
  const maker=await evaluate(`document.getElementById('makerSel').value`);
  await evaluate(`I18N.setLanguage('en')`);
  assert.equal(await evaluate(`document.getElementById('makerSel').value`),maker);
  await check('manufacturer English');
  await evaluate(`I18N.setLanguage('ko')`);
  await evaluate(`document.getElementById('makerSel').value=''; document.getElementById('makerSel').dispatchEvent(new Event('change'));`);
  for(const id of ['filterTrain','filterNoTrain','collapse']) {
    await evaluate(`document.getElementById('${id}').click()`);
    await check(id);
    await evaluate(`document.getElementById('${id}').click()`);
  }
  await evaluate(`document.querySelector('[data-scope="all"]').click()`);
  await check('all-market scope');
  await evaluate(`document.getElementById('multiplierSel').value=[...document.getElementById('multiplierSel').options].find(o=>parseFloat(o.value)>1).value; document.getElementById('multiplierSel').dispatchEvent(new Event('change'))`);
  await check('multiplier');
  await evaluate(`document.getElementById('multiplierSel').value=''; document.getElementById('multiplierSel').dispatchEvent(new Event('change')); document.getElementById('minIdx').value='40'; document.getElementById('minIdx').dispatchEvent(new Event('input'))`);
  await check('minimum score');
  await evaluate(`document.getElementById('search').value='no-such-model-for-test'; document.getElementById('search').dispatchEvent(new Event('input'))`);
  result=await check('empty search');
  assert.equal(result.priced+result.free,0);
  await evaluate(`document.getElementById('search').value=''; document.getElementById('search').dispatchEvent(new Event('input')); [...document.querySelectorAll('#tbl tbody tr')].find(tr=>tr.textContent.includes(__analysis.priced[0].name)).querySelector('input[type=checkbox]').click(); document.getElementById('btnModeCustom').click()`);
  result=await check('custom selection');
  assert.equal(result.priced,1);
  await navigate('index.html');
  await evaluate(`document.getElementById('search').value=__analysis.priced[0].name; document.getElementById('search').dispatchEvent(new Event('input'))`);
  result=await check('one model search');
  assert.equal(result.priced,1);
  await evaluate(`I18N.setLanguage('en')`);
  result=await check('English');
  assert.match(result.text,/Current selection analysis/);
  await evaluate(`I18N.setLanguage('ko')`);
  result=await check('Korean');
  assert.match(result.text,/현재 조건 분석/);
  await navigate('index.html','&fk=0');
  assert.equal(await evaluate('__analysis.weight'),0);
  await check('plain Pareto fk=0');
  // Render a long label through the real DOM renderer, including narrow layout.
  await command('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:false});
  await evaluate(`FrontierAnalysis.render(document.getElementById('conditionAnalysis'),FrontierAnalysis.analyze([{id:'long',name:'Long model name '.repeat(40),x:1,v:20}]),{isKo:true,title:'test',unit:'/1M',formatCost:String})`);
  assert.ok(await evaluate(`document.getElementById('conditionAnalysis').scrollWidth<=document.getElementById('conditionAnalysis').clientWidth+1`));
  await navigate('free_models.html');
  assert.equal(await evaluate(`!!document.getElementById('aiSummaryBox') || !!window.__SUMMARIES__`),false);
  assert.ok(!requests.some(p=>/summaries|summary_view/.test(p)));
  assert.deepEqual(errors,[]);
  console.log('No generated summaries requested; no page exceptions; free page guide absent; long label wraps: PASS');

}
const timeout=setTimeout(()=>{console.error('UI check timed out');process.exitCode=1;socket?.close();browser?.kill();server.close();},30000);
main().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>{
  clearTimeout(timeout);socket?.close();browser?.kill();server.close();
  browser?.on('exit',()=>fs.rmSync(profile,{recursive:true,force:true}));
});
