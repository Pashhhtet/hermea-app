"use strict";
// Hermea — вкладка «Обработка фото»: список квартир и поисков слева, рабочая область, создание по ссылке,
// свои фото, просмотр до/после. В конце — запуск окна (applyStatic, tick).
// ================================================================ список слева
function jobStatusText(j) {
  if (j.status === "queued") return S.st.warm === "loading" ? t("st_prep") : t("st_queued");
  if (j.status === "running") {
    if (j.step === "listing") return t("st_listing");
    if (j.step === "photos") return t("st_photos", { k: j.k, t: j.total });
    if (j.step === "saving") return t("st_saving");
    if (j.step === "telegram") return t("st_tg");
  }
  if (j.status === "error") return t("st_error");
  if (j.status === "cancelled") return t("st_cancelled");
  return t("st_done");
}
function jobName(j) { return j.name ? nice(j.name).title : (j.kind === "local" ? (j.title || t("own_title")) : shortUrl(j.url)); }
function renderList() {
  const jobs = (S.st.jobs || []).filter((j) => j.status === "running" || j.status === "queued");
  const failed = (S.st.jobs || []).filter((j) => j.status === "error");
  const searches = S.st.searches || [];
  const q = S.filter.trim().toLowerCase();
  const flats = q ? S.flats.filter((f) => f.name.toLowerCase().includes(q)) : S.flats;
  const selKey = S.sel ? S.sel.kind + ":" + (S.sel.id || S.sel.f || "") : "";
  const sig = JSON.stringify([jobs.map((j) => [j.id, j.status, j.step, j.k, j.name, j.thumbs > 0]), failed.map((j) => j.id),
    searches.map((s) => [s.id, s.title, s.new, !!s.error]), S.flatsVersion, q, selKey, LANG]);
  if (sig === S.listSig) return;
  S.listSig = sig;

  let h = "";
  const jobItem = (j) => {
    const cur = S.sel && S.sel.kind === "job" && S.sel.id === j.id;
    const pct = j.status === "running" && j.total ? Math.round((j.k / j.total) * 100) : 0;
    const err = j.status === "error";
    return `<button class="item" type="button" data-job="${j.id}" aria-current="${cur}">
      <span class="thumb job${err ? " err" : ""}">${err ? "!" : j.thumbs ? `<img class="thumb" src="${live(j.id, 0)}" alt="">` : ""}</span>
      <span><span class="t">${esc(jobName(j))}</span>
      <span class="s"><span class="${err ? "err" : ""}">${esc(jobStatusText(j))}</span></span>
      ${j.status === "running" ? `<span class="mini"><i style="width:${pct}%"></i></span>` : ""}</span></button>`;
  };
  if (jobs.length) h += `<div class="group">${t("g_work")}</div>` + jobs.map(jobItem).join("");
  if (failed.length) h += `<div class="group">${t("g_failed")}</div>` + failed.map(jobItem).join("");
  if (!q) {
    h += `<div class="group">${t("g_searches")}</div>`;
    for (const s of searches) {
      const cur = S.sel && S.sel.kind === "search" && S.sel.id === s.id;
      h += `<button class="item" type="button" data-search="${s.id}" aria-current="${cur}">
        <span class="thumb srch">${ICON.search}</span>
        <span><span class="t">${esc(s.title)}</span>
        <span class="s">${s.new ? `<span class="pill">${s.new} ${esc(plural(s.new, "news"))}</span>` : ""}
        ${s.error ? `<span class="err">!</span>` : ""}</span></span></button>`;
    }
    h += `<button class="add-link" type="button" data-addsearch="1">${ICON.plus}<span>${t("add_search")}</span></button>`;
  }
  const groups = [[t("g_today"), []], [t("g_yesterday"), []], [t("g_earlier"), []]];
  const z = day0();
  for (const f of flats) groups[f.when >= z ? 0 : f.when >= z - 86400 ? 1 : 2][1].push(f);
  groups.forEach(([title, arr], gi) => {
    if (!arr.length) return;
    h += `<div class="group">${title}</div>`;
    for (const f of arr) {
      const cur = S.sel && S.sel.kind === "flat" && S.sel.f === f.f;
      const n = nice(f.name);
      const d = new Date(f.when * 1000);
      const when = gi < 2 ? hm(d) : d.toLocaleDateString(LOCALE[LANG], { day: "numeric", month: "short" });
      h += `<button class="item" type="button" data-flat="${esc(f.f)}" aria-current="${cur}">
        ${f.cover ? `<img class="thumb" loading="lazy" src="${img(f.cover, 160)}" alt="">` : `<span class="thumb"></span>`}
        <span><span class="t">${esc(n.title)}</span>
        <span class="s"><span>${esc(t("photos_n", { n: f.count }))}</span><span>${esc(when)}</span>${n.manual ? `<span>${t("manual")}</span>` : ""}</span></span></button>`;
    }
  });
  if (!jobs.length && !failed.length && !flats.length && q) h += `<p class="empty-list">${t("list_nothing")}</p>`;
  else if (!flats.length && !q) h += `<p class="empty-list">${t("list_empty")}</p>`;
  $("#list").innerHTML = h;
}
$("#list").addEventListener("click", (e) => {
  const b = e.target.closest("[data-job],[data-flat],[data-search],[data-addsearch]");
  if (!b) return;
  if (b.dataset.job) select({ kind: "job", id: b.dataset.job });
  else if (b.dataset.flat) select({ kind: "flat", f: b.dataset.flat });
  else if (b.dataset.search) select({ kind: "search", id: b.dataset.search });
  else select({ kind: "addsearch" });
});
$("#search").addEventListener("input", (e) => { S.filter = e.target.value; S.listSig = ""; renderList(); });

function select(sel) {
  if (S.dirty && !confirm(t("unsaved_confirm"))) return;
  S.dirty = false;
  S.sel = sel;
  S.selSince = Date.now();
  S.view = "";
  S.flat = null;
  S.srch = null;
  S.listSig = "";
  renderList();
  if (sel && sel.kind === "flat") loadFlat(sel.f);
  else if (sel && sel.kind === "search") loadSearch(sel.id);
  else renderWork();
  $("#main").scrollTo({ top: 0, behavior: "smooth" });
}
async function loadFlat(f) {
  try {
    const d = await api("/api/flat?f=" + encodeURIComponent(f));
    if (!S.sel || S.sel.kind !== "flat" || S.sel.f !== f) return;
    S.flat = d;
    S.view = "";
    renderWork();
  } catch (e) { toast(e.message, true); }
}

// ================================================================ рабочая область
function renderWork() {
  const w = $("#work");
  const sel = S.sel;
  if (sel && sel.kind === "job") {
    const j = jobById(sel.id);
    if (!j) {
      if (!S.selSince || Date.now() - S.selSince > 8000) { S.sel = null; return renderWork(); }
      return;
    }
    if (j.status === "done" && j.f) return select({ kind: "flat", f: j.f });
    if (j.status === "cancelled") { S.sel = null; S.view = ""; return renderWork(); }
    if (j.status === "error") return drawError(j);
    return drawJob(j);
  }
  if (sel && sel.kind === "flat") { if (S.flat) drawFlat(S.flat); return; }
  if (sel && sel.kind === "search") { refreshSearchIfNeeded(); if (S.srch) drawSearch(S.srch); return; }
  if (sel && sel.kind === "addsearch") return drawAddSearch();
  const run = (S.st && S.st.jobs || []).find((j) => j.status === "running");
  if (run) { S.sel = { kind: "job", id: run.id }; S.listSig = ""; return renderWork(); }
  if (S.view !== "empty:" + LANG) {
    S.view = "empty:" + LANG;
    let frames = "";
    for (let i = 1; i <= 10; i++) frames += `<div class="frame"><span class="no">${i}</span></div>`;
    w.innerHTML = `<div class="tray dim">${frames}
      <div class="tray-empty"><b>${t("empty_title")}</b><span>${t("empty_text")}</span></div></div>`;
    enter(w.querySelector(".tray"), ".frame");
  }
}

const STEPS = ["listing", "photos", "saving", "telegram"];
function stepsHtml(j) {
  const idx = j.status === "queued" ? -1 : STEPS.indexOf(j.step);
  return STEPS.map((key, i) => {
    let fill = 0, cls = "";
    let text = t(key === "listing" ? (j.kind === "local" ? "step_own" : "step_listing") : key === "photos" ? "step_photos" : key === "saving" ? "step_saving" : "step_tg");
    if (i < idx) { fill = 100; cls = "done"; }
    if (i === idx) {
      cls = "on";
      fill = key === "photos" && j.total ? Math.max(4, Math.round(((j.k - 1) / j.total) * 100)) : 40;
      if (key === "photos" && j.total) text = t("st_photos", { k: j.k, t: j.total });
    }
    if (key === "telegram" && !j.telegram) { text = t("step_tg_off"); fill = 0; cls = ""; }
    return `<div class="step ${cls}"><div class="rail"><i style="width:${fill}%"></i></div><div class="lbl">${esc(text)}</div></div>`;
  }).join("");
}
function factsHtml(facts) {
  if (!facts || !facts.length) return "";
  const label = { "Всего": "f_total", "Аренда": "f_rent", "Czynsz": "f_czynsz", "Залог": "f_deposit" };
  const total = facts.filter((f) => f.main), rest = facts.filter((f) => !f.main);
  const cell = (f, cls) => `<div class="${cls}"><dt>${esc(t(label[f.label] || f.label))}</dt><dd>${esc(f.value)}</dd></div>`;
  return `<dl class="facts">${total.map((f) => cell(f, "total")).join("")}${rest.map((f) => cell(f, "")).join("")}</dl>`;
}

function drawJob(j) {
  const w = $("#work");
  const key = "job:" + j.id + ":" + (j.total || 0) + ":" + LANG;
  if (S.view !== key) {
    S.view = key;
    S.liveShown = 0;
    const n = j.total || 8;
    let frames = "";
    for (let i = 1; i <= n; i++) frames += `<div class="frame" data-i="${i - 1}"><span class="no">${i}</span></div>`;
    w.innerHTML = `
      <div class="work-head">
        <div><h2 class="work-title" id="jTitle"></h2><p class="work-sub" id="jSub"></p></div>
        <button class="text-btn" type="button" id="jCancel">${t("cancel")}</button>
      </div>
      <div class="steps" id="jSteps"></div>
      <div class="body">
        <div class="tray" id="jTray">${frames}</div>
        <div class="sheet"><div id="jFacts"></div>
          <h3>${t("opis")}</h3><div class="opis-wait">${t("opis_wait")}</div></div>
      </div>
      <div class="queue" id="jQueue"></div>`;
    enter(w.querySelector(".tray"), ".frame");
    $("#jCancel").onclick = async () => {
      if (!confirm(t("cancel_confirm"))) return;
      try { await api("/api/cancel", { id: j.id }); toast(t("stopping")); } catch (e) { toast(e.message, true); }
    };
  }
  $("#jTitle").textContent = j.name ? nice(j.name).title : (j.status === "queued" ? t("waiting") : (j.kind === "local" ? (j.title || t("own_title")) : t("st_listing")));
  if (j.no_fee) $("#jTitle").insertAdjacentHTML("beforeend", `<span class="nofee-tag">${esc(t("no_fee"))}</span>`);
  if (j.agency) $("#jTitle").insertAdjacentHTML("beforeend", `<span class="nofee-tag">${esc(t("agency"))}</span>`);
  $("#jSub").textContent = j.kind === "local" ? t("own_title") : (j.name ? shortUrl(j.url) : j.url);
  $("#jSteps").innerHTML = stepsHtml(j);
  $("#jFacts").innerHTML = factsHtml(j.facts);
  $("#jCancel").hidden = !(j.status === "running" || j.status === "queued");
  const tray = $("#jTray");
  for (let i = S.liveShown; i < j.thumbs; i++) {
    const fr = tray.querySelector(`.frame[data-i="${i}"]`);
    if (!fr) continue;
    fr.classList.add("has");
    const im = new Image();
    im.alt = "";
    im.onload = () => im.classList.add("dev");
    im.src = live(j.id, i);
    fr.prepend(im);
  }
  S.liveShown = Math.max(S.liveShown, j.thumbs);
  tray.querySelectorAll(".frame.busy").forEach((f) => f.classList.remove("busy"));
  if (j.status === "running" && j.step === "photos") {
    const fr = tray.querySelector(`.frame[data-i="${j.thumbs}"]`);
    if (fr) fr.classList.add("busy");
  }
  const queued = (S.st.jobs || []).filter((x) => x.status === "queued" && x.id !== j.id);
  $("#jQueue").innerHTML = queued.length
    ? `<h3>${t("queue_next")}</h3>${queued.map((x) => `<div class="q"><span>${esc(jobName(x))}</span><button class="text-btn" type="button" data-rm="${x.id}">${t("remove")}</button></div>`).join("")}`
    : "";
}
$("#work").addEventListener("click", async (e) => {
  const rm = e.target.closest("[data-rm]");
  if (rm) {
    try { await api("/api/remove", { id: rm.dataset.rm }); toast(t("removed")); } catch (err) { toast(err.message, true); }
  }
});

function drawError(j) {
  const key = "err:" + j.id + ":" + LANG;
  if (S.view === key) return;
  S.view = key;
  $("#work").innerHTML = `
    <div class="work-head"><div><h2 class="work-title">${t("err_title")}</h2>
    <p class="work-sub">${esc(j.kind === "local" ? (j.title || t("own_title")) : shortUrl(j.url))}</p></div></div>
    <div class="fail"><p>${esc(j.error || t("err_unknown"))}</p>
      <div class="row-btns">
        ${j.kind === "url" ? `<button class="btn ink" type="button" id="eRetry">${t("retry")}</button>
        <button class="btn" type="button" id="eOpen">${ICON.web} ${t("open_ad")}</button>` : ""}
        <button class="btn" type="button" id="eHide">${t("hide")}</button>
      </div>
      ${j.log && j.log.length ? `<pre class="log">${esc(j.log.join("\n"))}</pre>` : ""}</div>`;
  enter($("#work"));
  if ($("#eRetry")) $("#eRetry").onclick = () => create(j.url, true);
  if ($("#eOpen")) $("#eOpen").onclick = () => api("/api/open", { what: "url", url: j.url }).catch((e) => toast(e.message, true));
  $("#eHide").onclick = async () => {
    try { await api("/api/dismiss", { id: j.id }); } catch (e) {}
    S.sel = null; S.view = ""; S.listSig = ""; tick1();
  };
}

function drawFlat(d) {
  const key = "flat:" + d.f + ":" + d.photos.length + ":" + JSON.stringify(d.telegram || null) + ":" + LANG;
  if (S.view === key) return;
  S.view = key;
  S.dirty = false;
  const n = nice(d.name);
  const frames = d.photos.map((p, i) =>
    `<button class="frame has" type="button" data-p="${i}" aria-label="${esc(t("photo_n", { n: i + 1 }))}"><img loading="lazy" src="${img(p.f, 520)}" alt=""><span class="no">${i + 1}</span></button>`).join("");
  const sub = [`<span>${esc(t("photos_n", { n: d.photos.length }))}</span>`];
  if (d.created) sub.push(`<span>${esc(t("created", { when: stampText(d.created) }))}</span>`);
  if (n.manual) sub.push(`<span>${t("manual_done")}</span>`);
  if (d.kind === "local") sub.push(`<span>${t("own_done")}</span>`);
  if (d.telegram && d.telegram.ok) sub.push(`<span class="ok">${esc(t("tg_sent_at", { when: stampText(d.telegram.at) }))}</span>`);
  else if (d.telegram && d.telegram.ok === false) sub.push(`<span class="bad">${t("tg_not_sent")}</span>`);
  const tgErr = d.telegram && d.telegram.ok === false ? `<p class="tg-line bad">${esc(t("tg_err_line", { e: d.telegram.error || "" }))}</p>` : "";
  $("#work").innerHTML = `
    <div class="work-head"><div><h2 class="work-title">${esc(n.title)}</h2>
      <p class="work-sub">${sub.join("")}</p></div></div>
    <div class="body">
      <div class="tray" id="fTray">${frames || `<div class="tray-empty"><b>${t("no_photos")}</b></div>`}</div>
      <div class="sheet">
        <div class="sheet-top">
          ${d.has_opis ? `<button class="btn ink" type="button" id="fCopy">${ICON.copy} ${t("copy_opis")}</button>` : ""}
          <button class="btn" type="button" id="fFolder">${ICON.folder} ${t("open_folder")}</button>
        </div>
        ${factsHtml(d.facts)}
        <h3>${t("opis")}</h3>
        ${d.has_opis
          ? `<textarea class="opis" id="fOpis" spellcheck="false" aria-label="${esc(t("opis"))}">${esc(d.opis)}</textarea>
             <div class="row-btns" id="fSaveRow" hidden><button class="btn ink" type="button" id="fSave">${t("save_edits")}</button>
             <button class="btn" type="button" id="fUndo">${t("undo_edits")}</button></div>`
          : `<div class="opis-wait">${t("no_opis")}</div>`}
        ${(d.has_opis || d.url) ? `<div class="actions">
          ${d.has_opis ? `<button class="btn" type="button" id="fTg">${ICON.send} <span>${t("send_to_tg")}</span></button>` : ""}
          ${d.url ? `<button class="btn" type="button" id="fUrl">${ICON.web} ${t("open_ad")}</button>` : ""}
        </div>` : ""}
        ${tgErr}
        ${d.otodom ? `<details class="oto"><summary>${t("oto_title")}</summary>
          <textarea class="opis" id="fOto" spellcheck="false" readonly>${esc(d.otodom)}</textarea>
          <button class="btn ink" type="button" id="fOtoCopy">${ICON.copy} ${t("oto_copy")}</button></details>` : ""}
      </div>
    </div>`;
  if ($("#fOtoCopy")) $("#fOtoCopy").onclick = async () => {
    const o = $("#fOto");
    try { await navigator.clipboard.writeText(o.value); } catch (e) { o.select(); document.execCommand("copy"); }
    toast(t("copied"));
  };
  if ($("#fOto")) $(".oto").addEventListener("toggle", () => { const o = $("#fOto"); o.style.height = "auto"; o.style.height = Math.min(o.scrollHeight + 4, 640) + "px"; });
  enter($("#work"), ".work-head, .sheet");
  enter($("#fTray"), ".frame");
  countUp($("#work .facts .total dd"));
  $("#fTray").onclick = (e) => {
    const b = e.target.closest("[data-p]");
    if (b) openLb(d.photos, +b.dataset.p, b.querySelector("img"));
  };
  $("#fFolder").onclick = () => api("/api/open", { f: d.f }).catch((e) => toast(e.message, true));
  if ($("#fUrl")) $("#fUrl").onclick = () => api("/api/open", { what: "url", f: d.f }).catch((e) => toast(e.message, true));
  if (!d.has_opis) return;
  const ta = $("#fOpis");
  const fit = () => { ta.style.height = "auto"; ta.style.height = Math.min(ta.scrollHeight + 4, 520) + "px"; };
  fit();
  const setDirty = (v) => { S.dirty = v; $("#fSaveRow").hidden = !v; };
  ta.oninput = () => { setDirty(ta.value !== d.opis); fit(); };
  $("#fCopy").onclick = async () => {
    try { await navigator.clipboard.writeText(ta.value); } catch (e) { ta.select(); document.execCommand("copy"); }
    toast(t("copied"));
  };
  $("#fSave").onclick = async () => {
    try { await api("/api/opis", { f: d.f, text: ta.value }); d.opis = ta.value; setDirty(false); toast(t("saved")); }
    catch (e) { toast(e.message, true); }
  };
  $("#fUndo").onclick = () => { ta.value = d.opis; setDirty(false); fit(); };
  $("#fTg").onclick = async (e) => {
    const b = e.currentTarget, label = b.querySelector("span");
    if (S.dirty) {
      try { await api("/api/opis", { f: d.f, text: ta.value }); d.opis = ta.value; setDirty(false); }
      catch (err) { return toast(err.message, true); }
    }
    if (!confirm(t("send_confirm"))) return;
    b.disabled = true; label.textContent = t("sending");
    try { await api("/api/telegram", { f: d.f }); toast(t("sent")); loadFlat(d.f); }
    catch (err) { toast(err.message, true); b.disabled = false; label.textContent = t("send_to_tg"); }
  };
}

// ================================================================ поиски Otodom
async function loadSearch(id) {
  try {
    const d = await api("/api/search?id=" + encodeURIComponent(id));
    if (!S.sel || S.sel.kind !== "search" || S.sel.id !== id) return;
    S.srch = d; S.srchAt = Date.now();
    renderWork();
  } catch (e) { toast(e.message, true); S.sel = null; S.view = ""; renderWork(); }
}
function refreshSearchIfNeeded() {
  const s = (S.st.searches || []).find((x) => S.sel && x.id === S.sel.id);
  if (!s) { S.sel = null; S.view = ""; return; }
  if (S.srch && (s.last_check !== S.srch.last_check || s.checking !== S.srch.checking) && Date.now() - (S.srchAt || 0) > 1200) loadSearch(s.id);
}
function drawSearch(d) {
  // новые — всегда первыми; если фильтр «Только собственники» прячет новые, говорим об этом
  const all = d.items.map((i, k) => [i, k]).sort((a, b) => (b[0].new ? 1 : 0) - (a[0].new ? 1 : 0) || a[1] - b[1]).map((x) => x[0]);
  const items = S.ownersOnly ? all.filter((i) => i.owner) : all;
  const hiddenNew = S.ownersOnly ? all.filter((i) => i.new && !i.owner).length : 0;
  const key = "srch:" + d.id + ":" + d.last_check + ":" + d.checking + ":" + items.map((i) => i.id + (i.new ? "n" : "")).join(",") + ":" + S.ownersOnly + ":" + LANG;
  if (S.view === key) return;
  S.view = key;
  const sub = [];
  sub.push(`<span>${d.checking ? t("srch_checking") : d.last_check ? esc(t("srch_checked", { when: agoText(d.last_check) })) : ""}</span>`);
  if (d.total != null) sub.push(`<span>${esc(t("srch_found", { n: d.total }))}</span>`);
  if (d.new) sub.push(`<span class="ok">${d.new} ${esc(plural(d.new, "news"))}</span>`);
  if (d.error) sub.push(`<span class="bad">${esc(d.error)}</span>`);
  const card = (i) => {
    const place = [i.sub || i.district, i.street].filter(Boolean).join(", ");
    return `<article class="card${i.new ? " new" : ""}">
      <div class="pic${i.img ? "" : " noimg"}">${i.img ? `<img loading="lazy" src="${esc(i.img)}" alt="" onerror="this.remove()">` : ""}
        <div class="tags">${i.new ? `<span class="tag">${t("srch_new")}</span>` : ""}${i.owner ? `<span class="tag own">${t("srch_owner")}</span>` : ""}${i.drop ? `<span class="tag pdrop">${esc(t("srch_drop", { d: zl(i.drop.from - i.drop.to) }))}</span>` : ""}${i.market != null && Math.abs(i.market) >= 5 ? `<span class="mkt ${i.market > 0 ? "hi" : "lo"}">${esc(t(i.market > 0 ? "srch_mkt_up" : "srch_mkt_down", { p: i.market }))}</span>` : ""}</div></div>
      <div class="cb">
        <div class="price">${esc(money(i.total || i.price))}<small>${i.rent ? esc(money(i.price) + " + " + money(i.rent)) : esc(t("total_word"))}</small></div>
        <div class="ttl">${esc(i.title)}</div>
        <div class="meta">${i.rooms ? `<span>${esc(t("rooms_n", { n: i.rooms }))}</span>` : ""}${i.area ? `<span>${esc(String(i.area).replace(".", ","))} m²</span>` : ""}<span>${esc(place)}</span></div>
        <div class="meta">${i.owner ? "" : `<span>${esc(i.agency)}</span>`}${i.created ? `<span>${esc(whenText(Date.parse(i.created) / 1000))}</span>` : ""}</div>
        <div class="acts">
          <button class="btn-primary sm" type="button" data-proc="${esc(i.id)}">${t("srch_process")}</button>
          <button class="btn" type="button" data-openad="${esc(i.id)}">${t("srch_open")}</button>
          <button class="text-btn" type="button" data-hidead="${esc(i.id)}">${t("hide")}</button>
        </div>
      </div></article>`;
  };
  $("#work").innerHTML = `
    <div class="work-head"><div><h2 class="work-title">${esc(d.title)}</h2><p class="work-sub">${sub.join("")}</p></div>
      <div class="head-actions">
        <button class="btn" type="button" id="sCheck"${d.checking ? " disabled" : ""}>${ICON.refresh} ${t("srch_check_now")}</button>
        ${d.new ? `<button class="btn" type="button" id="sSeen">${t("srch_mark_seen")}</button>` : ""}
        <button class="text-btn" type="button" id="sRemove">${t("srch_remove")}</button>
      </div></div>
    <div class="filters"><label class="switch"><input type="checkbox" id="sOwners"${S.ownersOnly ? " checked" : ""}><span class="track"></span>${t("srch_owners")}</label>
      ${d.last_check && !d.new && d.items.length ? `<span class="hint">${t("srch_first")}</span>` : ""}
      ${hiddenNew ? `<span class="hidden-new">${esc(t("srch_hidden_new", { n: hiddenNew }))} <button class="text-btn" type="button" id="sShowAll">${t("srch_show_all")}</button></span>` : ""}</div>
    ${items.length ? (() => {
        const fresh = items.filter((i) => i.new), rest = items.filter((i) => !i.new);
        return `<div id="sCards">${fresh.length ? `<h3 class="cards-h new">${esc(t("srch_new_block", { n: fresh.length }))}</h3>
          <div class="cards">${fresh.map(card).join("")}</div>` : ""}
          ${rest.length ? `${fresh.length ? `<h3 class="cards-h">${esc(t("srch_rest_block"))}</h3>` : ""}<div class="cards">${rest.map(card).join("")}</div>` : ""}</div>`;
      })()
      : `<div class="opis-wait">${d.checking ? t("srch_checking") : t("srch_empty")}</div>`}`;
  revealCards(d.id);
  $("#sCheck").onclick = async () => {
    $("#sCheck").disabled = true;
    try { S.srch = await api("/api/search_check", { id: d.id }); S.view = ""; drawSearch(S.srch); } catch (e) { toast(e.message, true); $("#sCheck").disabled = false; }
    tick1();
  };
  if ($("#sShowAll")) $("#sShowAll").onclick = () => { $("#sOwners").checked = false; $("#sOwners").dispatchEvent(new Event("change")); };
  if ($("#sSeen")) $("#sSeen").onclick = async () => { await api("/api/search_seen", { id: d.id }).catch(() => {}); loadSearch(d.id); tick1(); };
  $("#sRemove").onclick = async () => {
    if (!confirm(t("srch_remove_confirm"))) return;
    await api("/api/search_remove", { id: d.id }).catch(() => {});
    S.sel = null; S.view = ""; S.listSig = ""; tick1();
  };
  $("#sOwners").onchange = (e) => {
    S.ownersOnly = e.target.checked;
    try { localStorage.setItem("hermea_owners", S.ownersOnly ? "1" : "0"); } catch (err) {}
    S.view = ""; drawSearch(d);
  };
  const cards = $("#sCards");
  if (cards) cards.onclick = async (e) => {
    const p = e.target.closest("[data-proc]"), o = e.target.closest("[data-openad]"), h = e.target.closest("[data-hidead]");
    const id = (p || o || h || {}).dataset;
    if (!id) return;
    const ad = d.items.find((x) => x.id === (id.proc || id.openad || id.hidead));
    if (!ad) return;
    if (p) { api("/api/search_seen", { id: d.id, ad: ad.id }).catch(() => {}); create(ad.url, false); }
    if (o) { api("/api/search_seen", { id: d.id, ad: ad.id }).catch(() => {}); api("/api/open", { what: "url", url: ad.url }).catch((err) => toast(err.message, true)); }
    if (h) { await api("/api/search_hide", { id: d.id, ad: ad.id }).catch(() => {}); toast(t("srch_hidden")); loadSearch(d.id); tick1(); }
  };
}
// карточки поиска выплывают по мере прокрутки; уже показанные больше не мигают
const REVEALED = new Set();
let revealIO = null;
function revealCards(sid) {
  const cards = [...document.querySelectorAll("#sCards .card")];
  if (!("IntersectionObserver" in window)) return;
  if (!revealIO) revealIO = new IntersectionObserver((ents) => {
    let k = 0;
    for (const e of ents) {
      if (!e.isIntersecting) continue;
      const c = e.target;
      c.style.setProperty("--d", (k++ % 6) * 70 + "ms");
      c.classList.add("in");
      REVEALED.add(c.dataset.rid);
      revealIO.unobserve(c);
    }
  }, { root: $("#main"), rootMargin: "0px 0px -40px 0px", threshold: 0.08 });
  cards.forEach((c) => {
    const id = sid + ":" + (c.querySelector("[data-proc]") || {}).dataset.proc;
    c.dataset.rid = id;
    if (REVEALED.has(id)) return;
    c.classList.add("reveal");
    revealIO.observe(c);
  });
}
function drawAddSearch(prefill) {
  const key = "addsearch:" + LANG;
  if (S.view === key && !prefill) return;
  S.view = key;
  $("#work").innerHTML = `
    <div class="work-head"><div><h2 class="work-title">${t("add_search")}</h2></div></div>
    <div class="add-search"><p>${t("srch_add_text")}</p>
      <form class="own-row" id="asForm"><input type="text" id="asUrl" spellcheck="false" placeholder="${esc(t("srch_ph"))}" value="${esc(prefill || "")}">
      <button class="btn-primary sm" type="submit">${t("srch_watch")}</button></form></div>`;
  enter($("#work"));
  $("#asUrl").focus();
  $("#asForm").onsubmit = (e) => { e.preventDefault(); addSearch($("#asUrl").value); };
}
async function addSearch(url) {
  try {
    const r = await api("/api/search_add", { url: (url || "").trim() });
    toast(t("srch_added"));
    $("#notice").hidden = true;
    S.st = await api("/api/state");
    select({ kind: "search", id: r.id });
  } catch (e) { toast(e.message, true); }
}

// ================================================================ создать по ссылке
async function create(text, force) {
  const notice = $("#notice");
  notice.hidden = true;
  const go = $("#go");
  go.disabled = true;
  try {
    const r = await api("/api/create", { text, force: !!force, telegram: $("#tgSend").checked, no_fee: $("#noFee").checked, agency: $("#agency").checked });
    if (r.error) throw new Error(r.error);
    if (r.search) { showSearchOffer(r.search); return; }
    if (r.added && r.added.length) {
      $("#noFee").checked = false;          // «без комиссии» — только для этих ссылок
      $("#agency").checked = false;         // «другое агентство» — тоже
      if (link.value.trim() === text.trim()) { link.value = ""; fitLink(); }
      toast(r.added.length === 1 ? t("started") : t("added_n", { n: r.added.length, links: plural(r.added.length, "links") }));
      const busy = S.st && (S.st.jobs || []).some((j) => j.status === "running");
      S.st = await api("/api/state");
      if (!busy || !S.sel || S.sel.kind !== "job") select({ kind: "job", id: r.added[0].id });
      S.listSig = "";
      renderList(); renderWork();
    }
    if (r.dups && r.dups.length) showDups(r.dups);
  } catch (e) {
    notice.className = "notice err";
    notice.textContent = e.message;
    notice.hidden = false;
  } finally {
    go.disabled = false;
  }
}
function showSearchOffer(url) {
  const n = $("#notice");
  n.className = "notice";
  n.innerHTML = `<div class="row"><strong>${t("search_detected")}</strong>
    <button class="btn-primary sm" type="button" id="offerWatch">${t("watch")}</button></div>`;
  n.hidden = false;
  $("#offerWatch").onclick = () => { link.value = ""; fitLink(); addSearch(url); };
}
function showDups(dups) {
  const n = $("#notice");
  n.className = "notice";
  n.innerHTML = dups.map((d, i) => `<div class="row">
      <strong>${d.active ? t("dup_active") : t("dup_done")}</strong>
      <span class="u">${esc(d.url)}</span>
      ${d.f ? `<button class="btn" type="button" data-open="${esc(d.f)}">${t("open")}</button>` : ""}
      ${d.active ? "" : `<button class="btn ink" type="button" data-again="${i}">${t("redo")}</button>`}
    </div>`).join("");
  n.hidden = false;
  n.onclick = (e) => {
    const o = e.target.closest("[data-open]");
    const a = e.target.closest("[data-again]");
    if (o) { n.hidden = true; select({ kind: "flat", f: o.dataset.open }); }
    if (a) { n.hidden = true; create(dups[+a.dataset.again].url, true); }
  };
}
const link = $("#link");
function fitLink() { link.style.height = "auto"; link.style.height = Math.min(link.scrollHeight, 132) + "px"; }
link.addEventListener("input", () => { fitLink(); if (!S.own) $("#notice").hidden = true; });
link.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("#form").requestSubmit(); }
});
$("#form").addEventListener("submit", (e) => {
  e.preventDefault();
  const v = link.value.trim();
  if (!v) { link.focus(); return toast(t("need_link"), true); }
  create(v, false);
});
document.addEventListener("paste", (e) => {
  const tg = e.target;
  if (tg.closest && tg.closest("input, textarea")) return;
  const files = [...((e.clipboardData && e.clipboardData.files) || [])].filter(isImage);
  if (files.length) { e.preventDefault(); addOwn(files); return; }
  const text = (e.clipboardData || window.clipboardData).getData("text");
  if (!text) return;
  e.preventDefault();
  link.value = text.trim();
  fitLink();
  link.focus();
});
$("#tgSend").addEventListener("change", (e) => {
  e.target.dataset.touched = "1";
  api("/api/settings", { telegram: e.target.checked }).catch(() => {});
});

// ================================================================ свои фото
function isImage(f) { return /^image\//.test(f.type) || /\.(heic|heif|jpe?g|png|webp)$/i.test(f.name); }
$("#ownBtn").addEventListener("click", () => $("#ownFile").click());
$("#ownFile").addEventListener("change", (e) => { const f = [...e.target.files]; e.target.value = ""; if (f.length) addOwn(f); });
function addOwn(files) {
  const ok = files.filter(isImage);
  if (!ok.length) return toast(t("own_noimg"), true);
  if (!S.own) S.own = { files: [] };
  S.own.files.push(...ok);
  drawOwn();
}
function drawOwn(progress) {
  const n = $("#notice");
  if (!S.own) { n.hidden = true; return; }
  const k = S.own.files.length;
  const prev = S.own.files.slice(0, 14).map((f) => /heic|heif/i.test(f.name) ? `<img alt="">` : `<img alt="" src="${URL.createObjectURL(f)}">`).join("");
  const name = $("#ownName") ? $("#ownName").value : (S.own.name || "");
  n.className = "notice";
  n.innerHTML = `<div class="row"><strong>${t("own_title")}</strong><span class="hint">${esc(t("own_selected", { n: k }))}</span>
      <button class="text-btn" type="button" id="ownMore">${t("own_more")}</button></div>
    <div class="own-thumbs">${prev}</div>
    <form class="own-row" id="ownForm"><input type="text" id="ownName" placeholder="${esc(t("own_name_ph"))}" value="${esc(name)}">
      <button class="btn-primary sm" type="submit" id="ownGo"${progress ? " disabled" : ""}>${progress || t("own_go")}</button>
      <button class="btn" type="button" id="ownCancel"${progress ? " disabled" : ""}>${t("own_cancel")}</button></form>`;
  n.hidden = false;
  $("#ownMore").onclick = () => $("#ownFile").click();
  $("#ownCancel").onclick = () => { S.own = null; n.hidden = true; };
  $("#ownForm").onsubmit = (e) => { e.preventDefault(); S.own.name = $("#ownName").value; uploadOwn(); };
  if (!progress) $("#ownName").focus();
}
async function uploadOwn() {
  const own = S.own;
  if (!own || !own.files.length) return;
  const uid = Array.from(crypto.getRandomValues(new Uint8Array(12)), (b) => b.toString(16).padStart(2, "0")).join("");
  try {
    for (let i = 0; i < own.files.length; i++) {
      drawOwn(t("own_uploading", { i: i + 1, n: own.files.length }));
      const f = own.files[i];
      const r = await fetch(`/api/upload?u=${uid}&n=${encodeURIComponent(f.name)}`, { method: "POST", headers: { "X-Hermea": T }, body: f });
      if (!r.ok) { let m = "HTTP " + r.status; try { m = (await r.json()).error || m; } catch (e) {} throw new Error(m); }
    }
    const r = await api("/api/create_local", { u: uid, name: own.name || "", telegram: $("#tgSend").checked, no_fee: $("#noFee").checked, agency: $("#agency").checked });
    if (r.error) throw new Error(r.error);
    $("#noFee").checked = false;
    $("#agency").checked = false;
    S.own = null;
    $("#notice").hidden = true;
    toast(t("started"));
    S.st = await api("/api/state");
    select({ kind: "job", id: r.added[0].id });
  } catch (e) {
    toast(e.message, true);
    drawOwn();
  }
}
let dragDepth = 0;
const hasFiles = (e) => [...(e.dataTransfer && e.dataTransfer.types || [])].includes("Files");
document.addEventListener("dragenter", (e) => { if (hasFiles(e)) { dragDepth++; $("#drop").hidden = false; } });
document.addEventListener("dragleave", (e) => { if (hasFiles(e) && --dragDepth <= 0) { dragDepth = 0; $("#drop").hidden = true; } });
document.addEventListener("dragover", (e) => e.preventDefault());
document.addEventListener("drop", (e) => {
  e.preventDefault();
  dragDepth = 0; $("#drop").hidden = true;
  const files = [...(e.dataTransfer.files || [])];
  if (files.length) { addOwn(files); return; }
  const text = e.dataTransfer.getData("text/uri-list") || e.dataTransfer.getData("text/plain");
  if (text && text.startsWith(location.origin)) return;     // перетащили картинку из самого окна
  if (text) { link.value = text.trim(); fitLink(); link.focus(); }
});

// ================================================================ просмотр фото (до / после, приближение)
const LB = { list: [], i: 0, pos: 50, drag: false, z: 1, tx: 0, ty: 0, pan: null };
const stage = $("#lbStage");
const RMQ = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
function openLb(list, i, fromImg) {
  LB.list = list; LB.i = i;
  const lb = $("#lb");
  lb.classList.remove("closing");
  lb.hidden = false;
  showLb(0, fromImg);
}
function closeLb() {
  const lb = $("#lb");
  if (lb.hidden) return;
  if (RMQ) { lb.hidden = true; return; }
  lb.classList.add("closing");
  setTimeout(() => { if (lb.classList.contains("closing")) { lb.hidden = true; lb.classList.remove("closing"); } }, 190);
}
function setZoom(z, tx, ty, anim) {
  const b = baseRect();
  LB.z = Math.max(1, Math.min(5, z));
  const minX = b.w * (1 - LB.z), minY = b.h * (1 - LB.z);
  LB.tx = LB.z === 1 ? 0 : Math.min(0, Math.max(minX, tx));
  LB.ty = LB.z === 1 ? 0 : Math.min(0, Math.max(minY, ty));
  stage.classList.toggle("anim", !!anim && !RMQ);
  const Z = window.ZOOM || 1;
  stage.style.transform = LB.z === 1 ? "" : `translate(${LB.tx / Z}px, ${LB.ty / Z}px) scale(${LB.z})`;
  stage.classList.toggle("zoomed", LB.z > 1);
  const zl = $("#lbZoom");
  zl.textContent = Math.round(LB.z * 100) + "%";
  zl.classList.toggle("show", LB.z > 1);
  clearTimeout(LB.zt);
  LB.zt = setTimeout(() => zl.classList.remove("show"), 1200);
  hintLb();
}
function baseRect() {          // где фото стоит без приближения
  const r = stage.getBoundingClientRect();
  return { left: r.left - LB.tx, top: r.top - LB.ty, w: r.width / LB.z, h: r.height / LB.z };
}
function zoomAt(cx, cy, z, anim) {
  const b = baseRect();
  const ux = (cx - b.left - LB.tx) / LB.z, uy = (cy - b.top - LB.ty) / LB.z;
  const nz = Math.max(1, Math.min(5, z));
  setZoom(nz, cx - b.left - ux * nz, cy - b.top - uy * nz, anim);
}
function hintLb() {
  const p = LB.list[LB.i];
  $("#lbHint").textContent = LB.z > 1 ? t("zoom_back") : (p && p.orig ? t("compare_hint") + ". " : "") + t("zoom_hint");
}
function showLb(dir, fromImg) {
  const p = LB.list[LB.i];
  const hasOrig = !!p.orig;
  setZoom(1, 0, 0);
  const after = $("#lbAfter");
  // сначала уже загруженная превьюшка (мгновенно), потом чёткое фото
  after.src = img(p.f, 520);
  const hi = new Image();
  hi.onload = () => { if (LB.list[LB.i] === p) after.src = hi.src; };
  hi.src = img(p.f, 2200);
  $("#lbBefore").hidden = !hasOrig;
  $("#lbHandle").hidden = !hasOrig;
  $("#lbTagL").hidden = !hasOrig;
  $("#lbTagR").hidden = !hasOrig;
  stage.classList.toggle("compare", hasOrig);
  if (hasOrig) $("#lbBeforeImg").src = img(p.orig, 2200);
  $("#lbCount").textContent = t("i_of_n", { i: LB.i + 1, n: LB.list.length });
  hintLb();
  LB.pos = 50; setPos();
  if (RMQ) return;
  const go = () => {
    if (fromImg && fromImg.isConnected) {
      const r1 = fromImg.getBoundingClientRect(), r2 = stage.getBoundingClientRect();
      if (r2.width > 0) {
        const Z = window.ZOOM || 1;
        stage.animate([
          { transform: `translate(${(r1.left - r2.left) / Z}px, ${(r1.top - r2.top) / Z}px) scale(${r1.width / r2.width})`, opacity: .4 },
          { transform: "translate(0, 0) scale(1)", opacity: 1 }],
        { duration: 420, easing: "cubic-bezier(.2, .8, .2, 1)" });
        return;
      }
    }
    if (dir) stage.animate([{ transform: `translateX(${dir * 40}px)`, opacity: 0 }, { transform: "none", opacity: 1 }],
      { duration: 320, easing: "cubic-bezier(.2, .8, .2, 1)" });
  };
  if (after.decode) after.decode().then(go, go); else go();
}
function setPos() {
  $("#lbBefore").style.clipPath = `inset(0 ${100 - LB.pos}% 0 0)`;
  $("#lbHandle").style.left = LB.pos + "%";
}
function movePos(e) {
  const r = stage.getBoundingClientRect();
  LB.pos = Math.max(0, Math.min(100, ((e.clientX - r.left) / r.width) * 100));   // доли — масштаб не важен
  setPos();
}
stage.addEventListener("dragstart", (e) => e.preventDefault());
stage.addEventListener("pointerdown", (e) => {
  e.preventDefault();
  if (LB.z > 1) {
    LB.pan = { x: e.clientX, y: e.clientY, tx: LB.tx, ty: LB.ty };
    stage.classList.add("panning");
    stage.setPointerCapture(e.pointerId);
    return;
  }
  if (!stage.classList.contains("compare")) return;
  LB.drag = true; stage.setPointerCapture(e.pointerId); movePos(e);
});
stage.addEventListener("pointermove", (e) => {
  if (LB.pan) return setZoom(LB.z, LB.pan.tx + e.clientX - LB.pan.x, LB.pan.ty + e.clientY - LB.pan.y);
  if (LB.drag) movePos(e);
});
const endDrag = () => { LB.drag = false; LB.pan = null; stage.classList.remove("panning"); };
stage.addEventListener("pointerup", endDrag);
stage.addEventListener("pointercancel", endDrag);
stage.addEventListener("dblclick", (e) => {
  e.preventDefault();
  if (LB.z > 1) setZoom(1, 0, 0, true); else zoomAt(e.clientX, e.clientY, 2.5, true);
});
$("#lb").addEventListener("wheel", (e) => {
  if ($("#lb").hidden) return;
  e.preventDefault();
  const k = Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0022));
  zoomAt(e.clientX, e.clientY, LB.z * k, false);
}, { passive: false });
function zoomCenter(f) { const r = stage.getBoundingClientRect(); zoomAt(r.left + r.width / 2, r.top + r.height / 2, LB.z * f, true); }
$("#lbIn").onclick = () => zoomCenter(1.6);
$("#lbOut").onclick = () => zoomCenter(1 / 1.6);
$("#lbClose").onclick = closeLb;
$("#lbPrev").onclick = () => { LB.i = (LB.i - 1 + LB.list.length) % LB.list.length; showLb(-1); };
$("#lbNext").onclick = () => { LB.i = (LB.i + 1) % LB.list.length; showLb(1); };
$("#lbReveal").onclick = () => api("/api/open", { what: "photo", f: LB.list[LB.i].f }).catch((e) => toast(e.message, true));
$("#lb").addEventListener("click", (e) => { if (e.target.classList.contains("lb-wrap") && LB.z === 1) closeLb(); });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !$("#pop").hidden) return togglePop(false);
  if ($("#lb").hidden) return;
  if (e.key === "Escape") { if (LB.z > 1) setZoom(1, 0, 0, true); else closeLb(); }
  if (e.key === "ArrowLeft") $("#lbPrev").click();
  if (e.key === "ArrowRight") $("#lbNext").click();
  if (e.key === "+" || e.key === "=") zoomCenter(1.6);
  if (e.key === "-") zoomCenter(1 / 1.6);
});
// тень под шапкой, когда страница прокручена
for (const sc of [$("#main"), $("#svk"), $("#clients"), $("#market"), $("#owners")].filter(Boolean)) {
  sc.addEventListener("scroll", () => document.body.classList.toggle("scrolled", sc.scrollTop > 6), { passive: true });
}

window.addEventListener("beforeunload", (e) => { if (S.dirty) { e.preventDefault(); e.returnValue = ""; } });
window.addEventListener("pagehide", () => { try { navigator.sendBeacon("/api/bye?t=" + T, ""); } catch (e) {} });
try { if (window.outerWidth < 1200) window.resizeTo(1400, 920); } catch (e) {}
applyStatic();
try {
  const upd = sessionStorage.getItem("hermea_updated");
  if (upd) { sessionStorage.removeItem("hermea_updated"); setTimeout(() => toast(t("upd_done", { v: upd })), 600); }
} catch (e) {}
link.focus();
tick();
