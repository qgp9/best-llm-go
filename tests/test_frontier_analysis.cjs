const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {analyze, describe} = require('../data/frontier_analysis.js');
const point = (id, x, v, kind = 'standard') => ({id, name:id, x, v, kind});
const ids = a => a.frontier.map(d => d.id);
const options = {title:'Effective cost', unit:'/1M tokens', formatCost:v=>'$'+v, isKo:false};

test('weighted exclusion is not strict dominance', () => {
  const a=analyze([point('entry',1,10), point('small gain',10,10.5)],{weight:0.1});
  assert.deepEqual(ids(a),['entry']);
  assert.equal(a.weightedExcluded,1);
  assert.equal(a.dominance,null);
  assert.match(describe(a,options).lines.join(' '),/without being strictly Pareto-dominated/);
  assert.deepEqual(ids(analyze(a.candidates,{weight:0})),['entry','small gain']);
});

test('strict dominance example chooses largest saving, deterministically', () => {
  const points=[point('a',1,20),point('z',10,10),point('b',10,10),point('c',3,19)];
  const a=analyze(points);
  assert.equal(a.dominance.better.id,'a');
  assert.equal(a.dominance.worse.id,'b');
  assert.equal(a.dominance.saving,9);
  assert.equal(a.dominance.scoreGain,10);
  assert.deepEqual(analyze(points.reverse()).dominance,a.dominance);
});

test('same price and higher score dominates; identical points do not', () => {
  const a=analyze([point('z',1,10),point('a',1,10),point('lower',1,9)]);
  assert.deepEqual(ids(a),['a']);
  assert.equal(a.equivalents,1);
  assert.equal(a.weightedExcluded,0);
  assert.equal(a.dominance.worse.id,'lower');
  assert.equal(a.dominance.saving,0);
});

test('free candidates remain separate even with missing or conflicting price', () => {
  const a=analyze([point('free',99,99,'free'),point('missing-free',null,40,'free'),point('paid',1,20)]);
  assert.deepEqual(ids(a),['paid']);
  assert.equal(a.free.length,2);
  assert.equal(a.free[0].x,0);
  assert.equal(a.priced.length,1);
});

test('unknown, zero and non-finite paid metrics are excluded', () => {
  const a=analyze([point('price?',null,10),point('score?',1,null),point('zero',0,10),point('infinity',Infinity,10),point('nan',1,NaN)]);
  assert.equal(a.candidates.length,0);
  assert.match(describe(a,options).lines[0],/No priced candidates/);
});

test('one candidate makes no comparative claim', () => {
  const a=analyze([point('only',1,20)]);
  assert.equal(a.picks.length,1);
  assert.equal(a.picks[0].previous,null);
  assert.match(describe(a,options).lines.join(' '),/no comparative advantage/);
});

test('representatives are entry, next and ceiling, using adjacent frontier deltas', () => {
  const a=analyze([point('a',1,10),point('b',2,20),point('c',4,30),point('d',8,40)]);
  assert.deepEqual(a.picks.map(p=>p.model.id),['a','b','d']);
  assert.equal(a.picks[2].previous.id,'c');
  assert.equal(a.picks[2].costDelta,4);
  assert.equal(a.picks[2].costRatio,2);
  assert.equal(a.picks[2].scoreDelta,10);
  assert.equal(analyze([point('a',1,10),point('b',2,20)]).picks.length,2);
});

test('frontier-only changes display, never candidates, frontier or evidence', () => {
  const rows=[point('a',1,20),point('b',2,10),point('free',0,10,'free')];
  const a=analyze(rows), b=analyze(rows,{frontierOnly:true});
  assert.deepEqual(ids(a),ids(b));
  assert.deepEqual(a.candidates,b.candidates);
  assert.deepEqual(describe(a,options),describe(b,options));
  assert.deepEqual(b.vis.map(d=>d.id),['a','free']);
});

test('changing eligible pool changes frontier and removes hidden dominators', () => {
  const hidden=point('hidden',1,30), selected=point('selected',2,20);
  assert.deepEqual(ids(analyze([hidden,selected])),['hidden']);
  assert.deepEqual(ids(analyze([selected])),['selected']);
});

test('no mutation of source data; same result regardless of input order', () => {
  const rows=[point('b',2,20),point('a',1,10)];
  const snapshot=JSON.stringify(rows);
  const a=analyze(rows);
  assert.equal(JSON.stringify(rows),snapshot);
  assert.deepEqual(ids(a),ids(analyze([...rows].reverse())));
});

test('localized explanations use score points, quotas use percentage-point deltas', () => {
  const a=analyze([point('a',1,10),point('b',2,20)],{weight:0});
  const en=describe(a,{...options,quota:true,unit:'% /1M tokens',formatCost:String});
  assert.match(en.lines[1],/1 percentage points/);
  assert.doesNotMatch(en.lines[1],/\$/);
  const ko=describe(a,{...options,isKo:true,effective:true});
  assert.equal(ko.heading,'현재 조건 분석');
  assert.match(ko.lines[1],/점수 \+10점/);
  assert.match(ko.caveats[0],/실제 종량제 청구 단가가 아닙니다/);
});

test('pages and pipeline do not consume generated AI summaries', () => {
  const root=path.resolve(__dirname,'..');
  for(const page of ['index.html','free_models.html']) {
    const html=fs.readFileSync(path.join(root,page),'utf8');
    assert.doesNotMatch(html,/src="data\/(summaries|summary_view)\.js"/);
    assert.doesNotMatch(html,/aiSummaryBox|aiSetSeg/);
  }
  assert.doesNotMatch(fs.readFileSync(path.join(root,'update.sh'),'utf8'),/build_summaries\.py/);
});

test('price bands sharing a model ID do not inherit frontier flags', () => {
  const low={...point('same-id',1,20),name:'small context'};
  const high={...point('same-id',2,20),name:'large context'};
  const a=analyze([low,high]);
  assert.equal(a.candidates[0].front,true);
  assert.equal(a.candidates[1].front,false);
  assert.equal(a.dominance.worse.name,'large context');
});
