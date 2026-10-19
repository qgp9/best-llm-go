/* Shared renderer for the structured AI summary guides (data/summaries.json).
   Each summary is {ko: {headline, picks[], caveats[], howto}, en: {...}}.
   Kept in one file so index.html and free_models.html render them identically. */
window.SummaryView = (function () {
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  // Returns true when a summary was rendered, false when there is nothing to show.
  function render(container, summary, isKo) {
    if (!container) return false;
    container.replaceChildren();
    if (!summary) { container.style.display = "none"; return false; }
    const lang = isKo ? "ko" : "en";
    const data = summary[lang] || summary.ko || summary.en;
    if (!data || !data.headline) { container.style.display = "none"; return false; }

    container.appendChild(el("div", "sv-headline", data.headline));

    if (Array.isArray(data.picks) && data.picks.length) {
      const list = el("ul", "sv-picks");
      data.picks.forEach((pick) => {
        const item = el("li");
        item.appendChild(el("b", null, pick.model));
        item.appendChild(document.createTextNode(" — " + pick.why));
        list.appendChild(item);
      });
      container.appendChild(list);
    }

    if (Array.isArray(data.caveats) && data.caveats.length) {
      const box = el("div", "sv-caveats");
      data.caveats.forEach((text) => box.appendChild(el("div", null, "⚠ " + text)));
      container.appendChild(box);
    }

    if (data.howto) {
      container.appendChild(el("div", "sv-howto", "💡 " + data.howto));
    }
    container.style.display = "block";
    return true;
  }

  return { render: render };
})();
