function flash(btn, text) {
  const orig = btn.textContent;
  btn.textContent = text;
  btn.classList.add("done");
  setTimeout(() => { btn.textContent = orig; btn.classList.remove("done"); }, 1500);
}
document.querySelectorAll("button.copy").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const text = btn.dataset.copyTarget
      ? document.getElementById(btn.dataset.copyTarget).textContent
      : btn.dataset.copy;
    try {
      await navigator.clipboard.writeText(text);
      flash(btn, "copied");
    } catch {
      flash(btn, "failed");
    }
  });
});

// /news/: filter by tool and kind; state lives in the query string (?tool=biston&kind=fixed).
const filter = document.querySelector("form.news-filter");
if (filter) {
  const items = [...document.querySelectorAll(".news-page .news-item")];
  const count = filter.querySelector(".news-count");
  const params = new URLSearchParams(location.search);
  for (const sel of filter.querySelectorAll("select")) {
    const wanted = params.get(sel.name);
    if (wanted && [...sel.options].some((o) => o.value === wanted)) sel.value = wanted;
  }
  const apply = () => {
    const tool = filter.elements.tool.value;
    const kind = filter.elements.kind.value;
    let shown = 0;
    for (const li of items) {
      const ok = (!tool || li.dataset.tool === tool) && (!kind || li.dataset.kind === kind);
      li.hidden = !ok;
      if (ok) shown++;
    }
    count.textContent = `${shown} of ${items.length}`;
    const q = new URLSearchParams();
    if (tool) q.set("tool", tool);
    if (kind) q.set("kind", kind);
    history.replaceState(null, "", q.toString() ? `?${q}` : location.pathname);
  };
  filter.addEventListener("change", apply);
  filter.addEventListener("submit", (e) => e.preventDefault());
  apply();
}
