"use strict";
// Hermea — ядро окна: связь с программой (api), общее состояние, переключение вкладок, верхняя панель,
// настройки, уведомления. Подключается после i18n.js и до файлов вкладок.
const T = window.TOKEN;          // ключ доступа подставляет программа в index.html
const morphish = (fn) => (window.morph ? window.morph(fn) : fn());

// ================================================================ помощники
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const img = (f, w) => `/img?f=${encodeURIComponent(f)}&w=${w || 0}&t=${T}`;
const live = (j, i) => `/live?j=${j}&i=${i}&t=${T}`;

async function api(path, body) {
  const opt = { headers: { "X-Hermea": T } };
  if (body !== undefined) {
    opt.method = "POST";
    opt.headers["Content-Type"] = "application/json";
    opt.body = JSON.stringify(body);
  }
  const r = await fetch(path, opt);
  let data = {};
  try { data = await r.json(); } catch (e) {}
  if (!r.ok) throw new Error(data.error || "HTTP " + r.status);
  return data;
}
function day0() { const n = new Date(); return new Date(n.getFullYear(), n.getMonth(), n.getDate()).getTime() / 1000; }
function hm(d) { return d.toLocaleTimeString(LOCALE[LANG], { hour: "2-digit", minute: "2-digit" }); }
function whenText(ts) {
  const d = new Date(ts * 1000), z = day0();
  if (ts >= z) return t("g_today").toLowerCase() + ", " + hm(d);
  if (ts >= z - 86400) return t("g_yesterday").toLowerCase() + ", " + hm(d);
  return d.toLocaleDateString(LOCALE[LANG], { day: "numeric", month: "long" });
}
function agoText(ts) {
  const s = Date.now() / 1000 - ts;
  if (s < 90) return t("just_now");
  return whenText(ts);
}
function stampText(s) {           // "2026-11-23 14:06" → "сегодня, 14:06"
  if (!s) return "";
  const m = s.match(/(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/);
  if (!m) return s;
  return whenText(new Date(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]).getTime() / 1000);
}
function money(v) { return v == null ? "" : String(v).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " zł"; }
function nice(name) {
  const manual = /\s*\(ручная обработка\)\s*$/i.test(name);
  return { title: name.replace(/\s*\(ручная обработка\)\s*$/i, ""), manual };
}
function shortUrl(u) {
  try {
    const x = new URL(u);
    const last = x.pathname.split("/").filter(Boolean).pop() || "";
    return x.hostname.replace(/^www\./, "") + "/…/" + last;
  } catch (e) { return u || ""; }
}
let toastTimer = 0;
function toast(msg, bad) {
  const el = $("#toast");
  el.textContent = msg;
  el.classList.toggle("bad", !!bad);
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), bad ? 5200 : 2600);
}
// плавное появление экрана: элементы поднимаются по очереди (один раз при открытии)
function enter(root, sel) {
  if (!root) return;
  let i = 0;
  root.querySelectorAll(sel || ":scope > *").forEach((el) => {
    if (i > 14) return;
    el.classList.remove("rise"); void el.offsetWidth;
    el.style.setProperty("--i", i++);
    el.classList.add("rise");
    el.addEventListener("animationend", () => el.classList.remove("rise"), { once: true });
  });
}
function countUp(el) {
  if (!el || (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches)) return;
  const txt = el.textContent, m = txt.match(/^(\D*)([\d\s\u00a0]+)(\D*)$/);
  if (!m) return;
  const to = +m[2].replace(/\D/g, "");
  if (!to) return;
  const t0 = performance.now();
  const step = (now) => {
    const k = Math.min(1, (now - t0) / 900), v = Math.round(to * (1 - Math.pow(1 - k, 3)));
    el.textContent = m[1] + String(v).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + m[3];
    if (k < 1) requestAnimationFrame(step); else el.textContent = txt;
  };
  requestAnimationFrame(step);
}
const ICON = {
  folder: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M3 7.5A1.5 1.5 0 0 1 4.5 6h4l2 2h9A1.5 1.5 0 0 1 21 9.5v8A1.5 1.5 0 0 1 19.5 19h-15A1.5 1.5 0 0 1 3 17.5z"/></svg>',
  send: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M21 4 3 11l7 2.5L12.5 21 21 4z"/><path d="m10 13.5 4.5-4.5"/></svg>',
  web: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.4 3.8 5.3 3.8 8.5s-1.2 6.1-3.8 8.5c-2.6-2.4-3.8-5.3-3.8-8.5S9.4 5.9 12 3.5z"/></svg>',
  copy: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5.5A1.5 1.5 0 0 0 14.5 4h-9A1.5 1.5 0 0 0 4 5.5v9A1.5 1.5 0 0 0 5.5 16H8"/></svg>',
  search: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/></svg>',
  plus: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  refresh: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/></svg>',
};

// ================================================================ состояние
const S = {
  st: null, flats: [], flatsVersion: -1, today: { flats: 0, photos: 0 },
  sel: null,            // {kind:"job"|"flat"|"search"|"addsearch", id|f}
  flat: null, srch: null, view: "", liveShown: 0, filter: "", dirty: false, ownersOnly: false,
  own: null,            // свои фото: {files: [File], urls: []}
};
const jobById = (id) => (S.st && S.st.jobs || []).find((j) => j.id === id);
try { S.ownersOnly = localStorage.getItem("hermea_owners") === "1"; } catch (e) {}

const seenDone = new Set();
let firstTick = true;
let bootVersion = null;
// ---------------------------------------------------------------- уведомления
// Системное уведомление macOS через osascript при клике открывало «Редактор скриптов».
// Поэтому уведомления показывает само окно: клик по ним открывает Hermea на нужной квартире или поиске.
const NOTE = { last: null };
const canNote = () => "Notification" in window && Notification.permission === "granted";
function askNotes() {
  if ("Notification" in window && Notification.permission === "default") {
    try { Notification.requestPermission(); } catch (e) {}
  }
}
document.addEventListener("click", askNotes, { once: true });
function showNotes(notes) {
  if (!notes) return;
  const max = notes.reduce((m, n) => Math.max(m, n.id), 0);
  if (NOTE.last === null) { NOTE.last = max; return; }      // старые при открытии окна не показываем
  for (const n of notes) {
    if (n.id <= NOTE.last) continue;
    if (canNote()) {
      try {
        const no = new Notification(n.title, { body: n.text, tag: "hermea-" + n.id, icon: "/app/mark.png" });
        no.onclick = () => { window.focus(); no.close(); goTarget(n.target || {}); };
      } catch (e) {}
    }
  }
  NOTE.last = Math.max(NOTE.last, max);
}
function goTarget(tg) {
  if (tg.mode) {
    if (tg.calls && typeof OW !== "undefined") { OW.filter = "calls"; }
    setMode(tg.mode); if (tg.calls && typeof ownersOpen === "function") ownersOpen();
    return;
  }
  if (!tg.kind) return;
  if (SV.mode !== "photo") setMode("photo");
  if (tg.kind === "search" && tg.id) select({ kind: "search", id: tg.id });
  else if (tg.kind === "flat" && tg.f) select({ kind: "flat", f: tg.f });
  else if (tg.kind === "job" && tg.id) select({ kind: "job", id: tg.id });
}

async function tick1() {
  try {
    S.st = await api("/api/state" + (canNote() ? "?wn=1" : ""));
    showNotes(S.st.notes);
    setOnline(true);
    if (bootVersion === null) bootVersion = S.st.version;
    else if (S.st.version !== bootVersion) {          // программа обновилась — перезагружаем окно
      try { sessionStorage.setItem("hermea_updated", S.st.version); } catch (e) {}
      location.reload();
      return;
    }
    for (const j of S.st.jobs || []) {
      if (j.status !== "done" || seenDone.has(j.id)) continue;
      seenDone.add(j.id);
      if (!firstTick) toast(t("done_toast", { name: nice(j.name).title, n: j.n }) + (j.tg === "sent" ? t("done_toast_tg") : ""));
    }
    firstTick = false;
    if (S.st.flats_version !== S.flatsVersion) await loadFlats();
    renderTop();
    renderList();
    renderWork();
    if (!$("#pop").hidden) renderPop();
  } catch (e) {
    setOnline(false);
  }
}
async function tick() {
  await tick1();
  const fast = S.st && (S.st.busy || ["installing", "restarting", "checking"].includes((S.st.update || {}).state));
  setTimeout(tick, fast ? 700 : 3000);
}
let offlineSince = 0;
function setOnline(ok) {
  if (ok) { offlineSince = 0; $("#gone").hidden = true; return; }
  if (!offlineSince) offlineSince = Date.now();
  const upd = S.st && ["installing", "restarting"].includes((S.st.update || {}).state);
  if (Date.now() - offlineSince > (upd ? 60000 : 6000)) $("#gone").hidden = false;
}
async function loadFlats() {
  const d = await api("/api/flats");
  S.flats = d.flats;
  S.flatsVersion = d.version;
  S.today = d.today;
  S.listSig = "";
}

// ================================================================ верхняя панель, баннеры, настройки
function renderTop() {
  const st = S.st;
  const tg = $("#tg");
  tg.dataset.state = st.tg.state;
  $("#tgText").textContent = st.tg.text;
  tg.title = (st.tg.hint ? st.tg.hint + ". " : "") + t("tg_recheck");
  const p = st.pending || [];
  $("#pending").hidden = !p.length;
  if (p.length) {
    $("#pendingText").textContent = p.length === 1 ? t("pending_one", { name: p[0] })
      : t("pending_many", { n: p.length, flats: plural(p.length, "flats") });
  }
  const u = st.update || {};
  const showUpd = u.state === "available" || u.state === "installing" || u.state === "restarting";
  $("#updBanner").hidden = !showUpd;
  if (showUpd) {
    $("#updTitle").textContent = u.state === "available" ? t("upd_banner", { v: u.version })
      : u.state === "installing" ? t("upd_installing") : t("upd_restarting");
    $("#updNotes").textContent = u.state === "available" ? (u.notes || "") : "";
    $("#updBtn").hidden = u.state !== "available";
  }
  const busy = (st.jobs || []).some((j) => j.status === "running");
  $("#go").textContent = busy ? t("to_queue") : t("create");
  const sw = $("#tgSend");
  if (!sw.dataset.touched) sw.checked = !!st.settings.telegram;
  const td = S.today;
  $("#today").textContent = td.flats
    ? t("today_stats", { n: td.flats, flats: plural(td.flats, "flats"), p: td.photos })
    : t("today_none");
}
function renderPop() {
  const st = S.st || {};
  const set = st.settings || window.BOOT || {};
  document.querySelectorAll("#segTheme button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.themeV === (set.theme || "auto"))));
  document.querySelectorAll("#segLang button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.langV === LANG)));
  document.querySelectorAll("#segScale button").forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.scaleV === Math.round(window.ZOOM * 100))));
  const u = st.update || {};
  $("#verTitle").textContent = t("version", { v: st.version || "" });
  let line = "";
  if (!u.configured) line = t("upd_off");
  else if (u.state === "checking") line = t("upd_checking");
  else if (u.state === "available") line = "<b>" + esc(t("upd_avail", { v: u.version })) + "</b>" + (u.notes ? "<br>" + esc(u.notes) : "");
  else if (u.state === "latest") line = t("upd_latest");
  else if (u.state === "installing") line = t("upd_installing");
  else if (u.state === "restarting") line = t("upd_restarting");
  else if (u.state === "error") line = t("upd_error", { e: u.error || "" });
  $("#updLine").innerHTML = line.startsWith("<b>") ? line : esc(line);
  $("#updApply").hidden = u.state !== "available";
  $("#updCheck").hidden = !u.configured || u.state === "installing" || u.state === "restarting";
}
function togglePop(open) {
  const p = $("#pop");
  const want = open === undefined ? p.hidden : open;
  p.hidden = !want;
  $("#gear").setAttribute("aria-expanded", String(want));
  if (want) renderPop();
}
$("#gear").addEventListener("click", (e) => { e.stopPropagation(); togglePop(); });
document.addEventListener("click", (e) => { if (!$("#pop").hidden && !e.target.closest("#pop")) togglePop(false); });
$("#segTheme").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-theme-v]");
  if (!b) return;
  morphish(() => { document.documentElement.dataset.theme = b.dataset.themeV; });
  if (S.st) S.st.settings.theme = b.dataset.themeV;
  renderPop();
  api("/api/settings", { theme: b.dataset.themeV }).catch(() => {});
});
$("#segScale").addEventListener("click", (e) => {
  const b = e.target.closest("[data-scale-v]");
  if (!b) return;
  const v = +b.dataset.scaleV;
  morphish(() => {
    window.ZOOM = v / 100;
    document.documentElement.style.zoom = v === 100 ? "" : window.ZOOM;
    document.documentElement.style.setProperty("--z", window.ZOOM);
  });
  if (S.st) S.st.settings.scale = v;
  renderPop();
  api("/api/settings", { scale: v }).catch(() => {});
  setTimeout(() => window.dispatchEvent(new Event("resize")), 60);
});
$("#segLang").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-lang-v]");
  if (!b) return;
  LANG = b.dataset.langV;
  try { await api("/api/settings", { lang: LANG }); } catch (err) {}
  applyStatic();
  S.view = ""; S.listSig = "";
  await tick1();
  renderPop();
});
$("#updCheck").addEventListener("click", async () => {
  try { await api("/api/update_check", {}); } catch (e) { toast(e.message, true); }
  tick1();
});
async function startUpdate() {
  try { await api("/api/update_apply", {}); toast(t("upd_installing")); } catch (e) { toast(e.message, true); }
  tick1();
}
$("#updApply").addEventListener("click", startUpdate);
$("#updBtn").addEventListener("click", startUpdate);
$("#tg").addEventListener("click", () => { api("/api/tgcheck", {}).then(() => toast(t("tg_checking_toast"))).catch(() => {}); });
$("#flushBtn").addEventListener("click", async (e) => {
  e.target.disabled = true;
  try {
    const r = await api("/api/flush", {});
    toast(r.left && r.left.length ? t("flush_part") : t("flush_ok"), !!(r.left && r.left.length));
  } catch (err) { toast(err.message, true); }
  e.target.disabled = false;
});
$("#openRoot").addEventListener("click", () => api("/api/open", { what: "root" }).catch((e) => toast(e.message, true)));
