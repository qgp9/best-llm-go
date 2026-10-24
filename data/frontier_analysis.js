/* Shared graph calculations and evidence-based explanations. No model API. */
(function (root) {
  'use strict';
  const idCompare = (a, b) => String(a.id).localeCompare(String(b.id), 'en') || String(a.name).localeCompare(String(b.name), 'en');
  const order = (a, b) => a.x - b.x || b.v - a.v || idCompare(a, b);
  function analyze(input, {weight = 0.1, frontierOnly = false} = {}) {
    weight = Number.isFinite(weight) ? Math.max(0, weight) : 0.1;
    const candidates = input.filter(d => Number.isFinite(d.v) &&
      (d.kind === 'free' || (Number.isFinite(d.x) && d.x > 0)))
      .map(d => ({...d, x: d.kind === 'free' ? 0 : d.x, front: false}));
    const priced = candidates.filter(d => d.kind !== 'free').sort(order);
    const free = candidates.filter(d => d.kind === 'free').sort((a, b) => b.v - a.v || idCompare(a, b));
    const frontier = [];
    for (const d of priced) {
      const previous = frontier.at(-1);
      if (!previous || d.v > previous.v + weight * (d.x - previous.x)) frontier.push(d);
    }
    const selected = new Set(frontier);
    candidates.forEach(d => { d.front = selected.has(d); });
    // Strict Pareto dominance is different from failing the weighted threshold.
    const dominatedIds = new Set();
    const pairs = [];
    for (const worse of priced) for (const better of priced) {
      if (better.x <= worse.x && better.v >= worse.v && (better.x < worse.x || better.v > worse.v)) {
        dominatedIds.add(worse);
        pairs.push({better, worse, saving: worse.x - better.x, scoreGain: better.v - worse.v});
      }
    }
    pairs.sort((a, b) => b.saving - a.saving || idCompare(a.worse, b.worse) || idCompare(a.better, b.better));
    const chosen = [...new Set([0, 1, frontier.length - 1])].filter(i => i >= 0 && i < frontier.length);
    const picks = chosen.map(i => ({model: frontier[i], previous: frontier[i - 1] || null,
      costDelta: i ? frontier[i].x - frontier[i - 1].x : null,
      costRatio: i ? frontier[i].x / frontier[i - 1].x : null,
      scoreDelta: i ? frontier[i].v - frontier[i - 1].v : null,
      role: i === 0 ? 'entry' : i === frontier.length - 1 ? 'ceiling' : 'next'}));
    const equivalents = priced.filter(d => !selected.has(d) && frontier.some(f => f.x === d.x && f.v === d.v));
    const equivalentIds = new Set(equivalents);
    return {candidates, priced, free, frontier, picks, dominance: pairs[0] || null,
      equivalents: equivalents.length,
      weightedExcluded: priced.filter(d => !selected.has(d) && !dominatedIds.has(d) && !equivalentIds.has(d)).length,
      weight, vis: frontierOnly ? candidates.filter(d => d.front || d.kind === 'free') : candidates};
  }

  const number = n => Number(n.toPrecision(4)).toString();
  function describe(a, {isKo = true, title, unit, formatCost, effective = false, quota = false} = {}) {
    const score = d => number(d.v);
    const cost = x => `${formatCost(x)} ${unit}`;
    const delta = x => quota ? `${number(x)} ${isKo ? '%p /1M 토큰' : 'percentage points /1M tokens'}` : cost(x);
    const lines = a.picks.map(p => {
      const m = p.model;
      const role = isKo ? {entry:'최저비용 진입점', next:'다음 단계', ceiling:'Frontier 최고점'}[p.role]
        : {entry:'Lowest-cost entry', next:'Next step', ceiling:'Highest frontier score'}[p.role];
      const base = `${role}: ${m.name} · ${cost(m.x)} · ${isKo ? '지능 지수' : 'Intelligence Index'} ${score(m)}`;
      if (!p.previous) return base;
      return base + (isKo
        ? `. ${p.previous.name} 대비 비용 +${delta(p.costDelta)} (${number(p.costRatio)}배), 점수 +${number(p.scoreDelta)}점.`
        : `. Versus ${p.previous.name}: cost +${delta(p.costDelta)} (${number(p.costRatio)}×), score +${number(p.scoreDelta)} points.`);
    });
    if (!a.priced.length) lines.push(isKo ? '현재 조건에서 가격과 점수가 모두 있는 유료 비교 후보가 없습니다.' : 'No priced candidates have both cost and score under these conditions.');
    else if (a.priced.length === 1) lines.push(isKo ? '유료 후보가 하나뿐이므로 다른 모델보다 유리하다는 결론은 낼 수 없습니다.' : 'Only one priced candidate remains; no comparative advantage can be established.');
    if (a.dominance) {
      const {better, worse, saving, scoreGain} = a.dominance;
      lines.push(isKo
        ? `비교상 열위 사례: ${worse.name}보다 ${better.name}의 비용이 ${saving ? delta(saving) + ' 낮고' : '같고'}, 점수는 ${scoreGain ? number(scoreGain) + '점 높습니다' : '같습니다'}. 이 두 지표만으로는 ${worse.name}를 우선할 근거가 없습니다.`
        : `Dominance example: ${better.name} costs ${saving ? delta(saving) + ' less' : 'the same'} as ${worse.name}, with ${scoreGain ? number(scoreGain) + ' more points' : 'the same score'}. These two metrics do not favor ${worse.name}.`);
    }
    if (a.equivalents) lines.push(isKo
      ? `동일한 비용과 점수의 후보 ${a.equivalents}개는 중복 점으로 묶어 Frontier 대표 하나만 표시합니다.`
      : `${a.equivalents} candidates share a frontier point's cost and score; one representative is shown on the frontier.`);
    if (a.weightedExcluded) lines.push(isKo
      ? `${a.weightedExcluded}개는 가중 Frontier 기준에서 제외됐지만 엄밀한 파레토 열위는 아닙니다. 추가 비용에 비해 점수 상승이 설정 기준에 못 미칩니다.`
      : `${a.weightedExcluded} candidates miss the weighted threshold without being strictly Pareto-dominated: their score gains do not meet the configured cost-increase threshold.`);
    const free = a.free.length ? (isKo
      ? `무료 영역: ${a.free.length}개 후보, 최고 관측 지능 지수 ${score(a.free[0])} (${a.free[0].name}). 유료 Frontier와 별도로 비교합니다. 무료 표시는 외부 API 사용 가능성을 보장하지 않습니다.`
      : `Free lane: ${a.free.length} candidates; highest observed score ${score(a.free[0])} (${a.free[0].name}). Separate from the priced frontier; a free listing does not establish external API access.`)
      : (isKo ? '현재 조건에 표시되는 무료 후보는 없습니다.' : 'No free candidates are shown under these conditions.');
    const caveats = [isKo
      ? `가중 기준 k=${number(a.weight)}. 점수 차이는 실제 작업 성능의 개선율이 아니며, 응답 속도·안정성·작업 적합성은 이 그래프로 판단하지 않습니다. 가격이나 점수가 없는 모델은 유료 비교에서 제외됩니다.`
      : `Weight k=${number(a.weight)}. Score differences are not workload performance percentages; latency, reliability and workload suitability are not established by this chart. Models lacking cost or score are excluded from priced comparisons.`];
    if (effective) caveats.unshift(isKo
      ? 'Go 체감 비용은 구독 한도를 반영한 비교 지표이며 실제 종량제 청구 단가가 아닙니다.'
      : 'Go effective cost is a subscription-adjusted comparison metric, not an actual pay-as-you-go billing rate.');
    return {heading: isKo ? '현재 조건 분석' : 'Current selection analysis',
      context: isKo ? `${title} · 유료 비교 ${a.priced.length}개 · Frontier ${a.frontier.length}개`
        : `${title} · ${a.priced.length} priced candidates · ${a.frontier.length} frontier points`, lines, free, caveats};
  }

  function render(container, analysis, options) {
    const text = describe(analysis, options);
    const doc = container.ownerDocument;
    const node = (tag, value, cls) => { const e = doc.createElement(tag); e.textContent = value; if (cls) e.className = cls; return e; };
    container.replaceChildren(node('h2', text.heading), node('p', text.context, 'analysis-context'));
    const list = doc.createElement('ul');
    text.lines.forEach(line => list.append(node('li', line)));
    container.append(list, node('p', text.free, 'analysis-free'));
    text.caveats.forEach(line => container.append(node('p', line, 'analysis-note')));
    container.dataset.frontierIds = JSON.stringify(analysis.frontier.map(d => d.id));
    container.dataset.candidateIds = JSON.stringify(analysis.candidates.map(d => d.id));
  }
  const api = {analyze, describe, render};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FrontierAnalysis = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
