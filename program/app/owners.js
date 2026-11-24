"use strict";
/* Собственники: частные объявления Otodom с оценкой «кому агент нужнее», скрипт звонка и статусы.
   Подключается после clients.js. */

const OW_L = {
ru: {
  m_owners: "Собственники",
  ow_title: "Собственники", ow_sub: "Частные объявления Otodom по 18 районам. Сверху те, кому агент нужнее всего. Обновляется раз в день, пока программа открыта.",
  ow_last: "проверено {d}", ow_refresh: "Обновить сейчас", ow_running: "Собираю районы: {n} из {t}…", ow_reading: "Читаю объявления: {n} из {t}…",
  ow_empty_t: "Список ещё не собран", ow_empty: "Программа пройдёт по частным объявлениям во всех районах Варшавы (5–10 минут) и отсортирует собственников по шансу на сотрудничество.",
  ow_f_new: "К звонку", ow_f_called: "Звонил", ow_f_agreed: "Согласны", ow_f_refused: "Отказ", ow_f_hidden: "Скрытые",
  ow_all: "Все районы", ow_find: "Улица или район", ow_more: "Показать ещё", ow_none: "Здесь пока пусто.",
  ow_open: "Открыть на Otodom", ow_script: "Скрипт звонка", ow_close: "Свернуть",
  ow_s_called: "Поговорил", ow_s_nocall: "Не дозвонился", ow_s_agreed: "Согласен на 50%", ow_s_refused: "Отказ", ow_s_hidden: "Скрыть", ow_s_back: "Вернуть в список",
  ow_note: "Заметка: когда перезвонить, что сказал…", ow_photo: "Обработать фото", ow_photo_ok: "Квартира добавлена в обработку фото",
  ow_name: "Имя в скрипте", ow_gone: "снято с сайта",
  ow_hot: "горячий", ow_warm: "тёплый", ow_cold: "холодный",
  ow_saved: "Сохранено", ow_copy: "Копировать скрипт", ow_copied: "Скрипт скопирован",
  ow_obj: "Если возражает",
  w_days: "{n} дн. на сайте", w_old: "объявлению {n} мес., выставлено снова", w_drop: "цену снизили на {n} zł", w_relisted: "перевыставлено",
  w_pushed: "платит за поднятие", w_promoted: "платная реклама", w_above: "дороже рынка на {n}%", w_photos: "всего {n} фото",
  w_neg: "пишет «без посредников»", w_pos: "агенты приветствуются", w_empty: "уже пустует", w_short: "короткое описание", w_others: "{n} объявл. у владельца",
},
uk: {
  m_owners: "Власники",
  ow_title: "Власники", ow_sub: "Приватні оголошення Otodom по 18 районах. Зверху ті, кому агент потрібен найбільше. Оновлюється раз на день, поки програма відкрита.",
  ow_last: "перевірено {d}", ow_refresh: "Оновити зараз", ow_running: "Збираю райони: {n} з {t}…", ow_reading: "Читаю оголошення: {n} з {t}…",
  ow_empty_t: "Список ще не зібраний", ow_empty: "Програма пройде по приватних оголошеннях у всіх районах Варшави (5–10 хвилин) і відсортує власників за шансом на співпрацю.",
  ow_f_new: "До дзвінка", ow_f_called: "Дзвонив", ow_f_agreed: "Згодні", ow_f_refused: "Відмова", ow_f_hidden: "Приховані",
  ow_all: "Усі райони", ow_find: "Вулиця або район", ow_more: "Показати ще", ow_none: "Тут поки порожньо.",
  ow_open: "Відкрити на Otodom", ow_script: "Скрипт дзвінка", ow_close: "Згорнути",
  ow_s_called: "Поговорив", ow_s_nocall: "Не додзвонився", ow_s_agreed: "Згоден на 50%", ow_s_refused: "Відмова", ow_s_hidden: "Приховати", ow_s_back: "Повернути в список",
  ow_note: "Нотатка: коли передзвонити, що сказав…", ow_photo: "Обробити фото", ow_photo_ok: "Квартиру додано в обробку фото",
  ow_name: "Ім'я в скрипті", ow_gone: "знято з сайту",
  ow_hot: "гарячий", ow_warm: "теплий", ow_cold: "холодний",
  ow_saved: "Збережено", ow_copy: "Копіювати скрипт", ow_copied: "Скрипт скопійовано",
  ow_obj: "Якщо заперечує",
  w_days: "{n} дн. на сайті", w_old: "оголошенню {n} міс., виставлено знову", w_drop: "ціну знизили на {n} zł", w_relisted: "перевиставлено",
  w_pushed: "платить за підняття", w_promoted: "платна реклама", w_above: "дорожче ринку на {n}%", w_photos: "лише {n} фото",
  w_neg: "пише «без посередників»", w_pos: "агентів запрошують", w_empty: "вже пустує", w_short: "короткий опис", w_others: "{n} оголош. у власника",
},
pl: {
  m_owners: "Właściciele",
  ow_title: "Właściciele", ow_sub: "Prywatne ogłoszenia z Otodom w 18 dzielnicach. Na górze ci, którym agent jest najbardziej potrzebny. Odświeżane raz dziennie, gdy program jest otwarty.",
  ow_last: "sprawdzono {d}", ow_refresh: "Odśwież teraz", ow_running: "Zbieram dzielnice: {n} z {t}…", ow_reading: "Czytam ogłoszenia: {n} z {t}…",
  ow_empty_t: "Lista nie jest jeszcze zebrana", ow_empty: "Program przejdzie przez prywatne ogłoszenia we wszystkich dzielnicach Warszawy (5–10 minut) i ułoży właścicieli według szansy na współpracę.",
  ow_f_new: "Do telefonu", ow_f_called: "Dzwoniłem", ow_f_agreed: "Zgoda", ow_f_refused: "Odmowa", ow_f_hidden: "Ukryte",
  ow_all: "Wszystkie dzielnice", ow_find: "Ulica lub dzielnica", ow_more: "Pokaż więcej", ow_none: "Na razie pusto.",
  ow_open: "Otwórz na Otodom", ow_script: "Skrypt rozmowy", ow_close: "Zwiń",
  ow_s_called: "Rozmawiałem", ow_s_nocall: "Nie odebrał", ow_s_agreed: "Zgoda na 50%", ow_s_refused: "Odmowa", ow_s_hidden: "Ukryj", ow_s_back: "Przywróć",
  ow_note: "Notatka: kiedy oddzwonić, co powiedział…", ow_photo: "Obrób zdjęcia", ow_photo_ok: "Mieszkanie dodane do obróbki zdjęć",
  ow_name: "Imię w skrypcie", ow_gone: "zdjęte z portalu",
  ow_hot: "gorący", ow_warm: "ciepły", ow_cold: "zimny",
  ow_saved: "Zapisano", ow_copy: "Kopiuj skrypt", ow_copied: "Skrypt skopiowany",
  ow_obj: "Jeśli ma obiekcje",
  w_days: "{n} dni na portalu", w_old: "ogłoszenie ma {n} mies., wystawione ponownie", w_drop: "cena obniżona o {n} zł", w_relisted: "wystawione ponownie",
  w_pushed: "płaci za podbicie", w_promoted: "płatna promocja", w_above: "{n}% drożej niż rynek", w_photos: "tylko {n} zdjęć",
  w_neg: "pisze „bez pośredników”", w_pos: "biura mile widziane", w_empty: "już stoi puste", w_short: "krótki opis", w_others: "{n} ogłosz. właściciela",
},
};
Object.assign(L.ru, OW_L.ru); Object.assign(L.uk, OW_L.uk); Object.assign(L.pl, OW_L.pl);

const OW = { data: null, filter: "new", district: "", q: "", shown: 40, open: "", timer: 0 };
try { OW.filter = localStorage.getItem("hermea_ow_filter") || "new"; } catch (e) {}
const OW_GROUP = { new: ["new"], called: ["called", "nocall"], agreed: ["agreed"], refused: ["refused"], hidden: ["hidden"] };

function owName() {
  try { return localStorage.getItem("hermea_ow_name") || "Paweł"; } catch (e) { return "Paweł"; }
}

async function ownersOpen(quiet) {
  try { OW.data = await api("/api/owners"); drawOwners(!quiet); } catch (e) { toast(e.message, true); }
  clearTimeout(OW.timer);
  if (OW.data && OW.data.state && OW.data.state.state === "running")
    OW.timer = setTimeout(() => { if (SV.mode === "owners") ownersOpen(true); }, 2500);
}

function owWhy(w) {
  const [k, v] = w;
  const txt = k === "days" ? t("w_days", { n: v }) : k === "old" ? t("w_old", { n: v }) : k === "drop" ? t("w_drop", { n: zl(v) })
    : k === "above" ? t("w_above", { n: v }) : k === "photos" ? t("w_photos", { n: v }) : k === "others" ? t("w_others", { n: v })
    : t("w_" + k);
  const cls = k === "neg" ? "bad" : k === "pos" || k === "empty" || k === "drop" ? "good" : "";
  return `<span class="ow-why ${cls}">${esc(txt)}</span>`;
}

function owHeat(s) { return s >= 70 ? "hot" : s >= 50 ? "warm" : "cold"; }

function owScript(a) {
  const nm = owName();
  const where = a.street ? `przy ul. ${a.street}` : `w dzielnicy ${a.district}`;
  const why = Object.fromEntries((a.why || []).map((w) => [w[0], w[1]]));
  let hook = `Mamy sprawdzonych klientów, którzy szukają mieszkania właśnie w tej okolicy.`;
  if (why.empty) hook = `Rozumiem, że mieszkanie już stoi wolne, a każdy miesiąc bez najemcy to strata. Dlatego dzwonię z konkretną propozycją: mamy klientów, którzy szukają w tej okolicy.`;
  else if (why.drop) hook = `Widzę, że cena była już obniżana. Zanim zejdzie Pan/Pani jeszcze niżej, warto spróbować z nami: mamy aktywnych klientów w tej okolicy.`;
  else if (why.days >= 14) hook = `Widzę, że ogłoszenie jest już od około ${why.days} dni. Mamy klientów, którzy szukają właśnie w tej okolicy, więc możemy pomóc znaleźć najemcę szybciej.`;
  else if (why.above) hook = `Mamy klientów z budżetem na tę okolicę. Pomożemy też tak przygotować ofertę, żeby mieszkanie szybko się wynajęło.`;
  const photos = why.photos || why.short ? "\nW ramach współpracy robimy też profesjonalne zdjęcia i opis mieszkania, bez dodatkowych kosztów." : "";
  return `Dzień dobry, nazywam się ${nm}, dzwonię z agencji nieruchomości Hermea. Dzwonię w sprawie ogłoszenia mieszkania na wynajem ${where}. Czy jest jeszcze aktualne?

${hook}${photos}

Pracujemy tak: robimy prezentacje, sprawdzamy najemców i ich dokumenty, przygotowujemy umowę, także najem okazjonalny. Nasze wynagrodzenie to 50% jednego czynszu najmu, płatne dopiero po podpisaniu umowy z najemcą. Jeśli nie znajdziemy najemcy, nic Pan/Pani nie płaci.

Czy mogę zaprosić naszych klientów na prezentację? Kiedy byłoby wygodnie pokazać mieszkanie?`;
}
function owObjections() {
  return [
    ["Mam dużo telefonów", "Rozumiem. My przyprowadzamy już sprawdzonych najemców z dokumentami, więc oszczędza Pan/Pani czas na niepotrzebnych prezentacjach."],
    ["Nie chcę płacić prowizji", "Rozumiem. Płaci Pan/Pani tylko po podpisaniu umowy i to połowę jednego czynszu, a jeden pusty miesiąc kosztuje cały czynsz."],
    ["Sam/sama sobie poradzę", "Oczywiście. Proponuję tylko dodatkowy kanał: jeśli nasz klient będzie pierwszy, wynajmie Pan/Pani szybciej, a jeśli nie, nic Pan/Pani nie traci."],
    ["Proszę zadzwonić później", "Jasne. Kiedy będzie wygodnie? Zapiszę i zadzwonię dokładnie wtedy."],
  ];
}

function drawOwners(first) {
  const box = $("#owners"), d = OW.data;
  if (!box || !d) return;
  const st = d.state || {};
  const run = st.state === "running";
  const runTxt = run ? (st.phase === "detail" ? t("ow_reading", { n: st.done, t: st.total }) : t("ow_running", { n: st.done, t: st.total || 18 })) : t("ow_refresh");
  const dd = (s) => (s ? parseIso(s).toLocaleDateString(LOCALE[LANG], { day: "numeric", month: "long" }) : "");
  if (!d.last_scan && !d.items.length) {
    box.innerHTML = `<div class="sv-wrap"><div class="cl-head"><div><h1 class="display">${t("ow_title")}</h1><p class="sv-sub">${t("ow_sub")}</p></div></div>
      <div class="mk-empty rise"><b>${t("ow_empty_t")}</b><p>${t("ow_empty")}</p>
      <button class="btn-primary" type="button" id="owGo" ${run ? "disabled" : ""}>${esc(runTxt)}</button></div></div>`;
    $("#owGo").onclick = owScan;
    return;
  }
  const groups = OW_GROUP[OW.filter] || OW_GROUP.new;
  const cnt = (g) => OW_GROUP[g].reduce((s, k) => s + ((d.counts || {})[k] || 0), 0);
  const q = OW.q.trim().toLowerCase();
  let rows = d.items.filter((a) => groups.includes(a.status || "new"));
  if (OW.filter === "new") rows = rows.filter((a) => !a.gone);
  if (OW.district) rows = rows.filter((a) => (a.district || "") === OW.district);
  if (q) rows = rows.filter((a) => `${a.street} ${a.district} ${a.sub} ${a.title}`.toLowerCase().includes(q));
  const dists = [...new Set(d.items.map((a) => a.district).filter(Boolean))].sort((a, b) => a.localeCompare(b));
  box.innerHTML = `<div class="sv-wrap ow-wrap">
    <div class="cl-head"><div><h1 class="display">${t("ow_title")}</h1>
      <p class="sv-sub"><span>${esc(t("ow_sub"))}</span>${d.last_scan ? `<span class="today-pill">${esc(t("ow_last", { d: dd(d.last_scan) }))}</span>` : ""}</p></div>
      <button class="btn" type="button" id="owGo" ${run ? "disabled" : ""}>${ICON.refresh} ${esc(runTxt)}</button></div>
    <div class="ow-bar">
      <div class="seg" id="owSeg">${Object.keys(OW_GROUP).map((g) => `<button type="button" data-g="${g}" aria-pressed="${g === OW.filter}">${t("ow_f_" + g)} <small>${cnt(g)}</small></button>`).join("")}</div>
      <select class="pop-in ow-sel" id="owDist"><option value="">${t("ow_all")}</option>${dists.map((x) => `<option ${x === OW.district ? "selected" : ""}>${esc(x)}</option>`).join("")}</select>
      <input class="pop-in ow-q" id="owQ" type="search" placeholder="${esc(t("ow_find"))}" value="${esc(OW.q)}">
      <label class="ow-name">${t("ow_name")} <input class="pop-in" id="owName" value="${esc(owName())}" maxlength="40"></label>
    </div>
    <ol class="ow-list" id="owList">${rows.slice(0, OW.shown).map(owRow).join("") || `<li class="ow-none">${t("ow_none")}</li>`}</ol>
    ${rows.length > OW.shown ? `<button class="btn ow-more" type="button" id="owMore">${t("ow_more")} (${rows.length - OW.shown})</button>` : ""}
  </div>`;
  if (first) enter($("#owList"), ":scope > li");
  requestAnimationFrame(() => slideSeg($("#owSeg")));
  $("#owGo").onclick = owScan;
  $("#owSeg").onclick = (e) => {
    const b = e.target.closest("[data-g]"); if (!b) return;
    OW.filter = b.dataset.g; OW.shown = 40; OW.open = "";
    try { localStorage.setItem("hermea_ow_filter", OW.filter); } catch (err) {}
    drawOwners(true);
  };
  $("#owDist").onchange = (e) => { OW.district = e.target.value; OW.shown = 40; drawOwners(true); };
  $("#owQ").oninput = (e) => { OW.q = e.target.value; clearTimeout(OW.qt); OW.qt = setTimeout(() => { drawOwners(); const i = $("#owQ"); i.focus(); i.setSelectionRange(i.value.length, i.value.length); }, 250); };
  $("#owName").onchange = (e) => { try { localStorage.setItem("hermea_ow_name", e.target.value.trim() || "Paweł"); } catch (err) {} drawOwners(); };
  if ($("#owMore")) $("#owMore").onclick = () => { OW.shown += 40; drawOwners(); };
  $("#owList").onclick = owClick;
  $("#owList").addEventListener("change", owNote);
}

function owRow(a) {
  const s = a.score || 0, heat = owHeat(s);
  const open = OW.open === a.id;
  const mk = a.market == null ? "" : `<span class="ow-mk ${a.market > 5 ? "hi" : a.market < -5 ? "lo" : ""}">${a.market > 0 ? "+" : ""}${a.market}%</span>`;
  const rooms = a.rooms ? `${a.rooms} ${LANG === "pl" ? "pok." : LANG === "uk" ? "кімн." : "комн."}` : "";
  const status = a.status || "new";
  const btns = status === "new"
    ? ["called", "nocall", "agreed", "refused", "hidden"]
    : status === "agreed" ? ["photo", "back"] : ["agreed", "called", "refused", "back"].filter((x) => x !== status);
  const btn = (k) => k === "photo" ? `<button class="btn-primary sm" type="button" data-act="photo">${t("ow_photo")}</button>`
    : k === "back" ? `<button class="text-btn" type="button" data-st="new">${t("ow_s_back")}</button>`
    : `<button class="btn ${k === "agreed" ? "ow-yes" : k === "refused" ? "ow-no" : ""}" type="button" data-st="${k}">${t("ow_s_" + k)}</button>`;
  return `<li class="ow-row ${heat}${open ? " open" : ""}${a.gone ? " gone" : ""}" data-id="${esc(a.id)}">
    <div class="ow-main">
      <div class="ow-score" title="${t("ow_" + heat)}"><b>${s}</b><i style="--k:${s / 100}"></i></div>
      ${a.img ? `<img class="ow-img" src="${esc(a.img)}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.style.visibility='hidden'">` : `<div class="ow-img"></div>`}
      <div class="ow-info">
        <div class="ow-t"><b>${esc(a.district || "")}${a.street ? ", " + esc(a.street) : ""}</b><span>${esc([rooms, a.area ? Math.round(a.area) + " м²" : ""].filter(Boolean).join(" · "))}</span>${a.gone ? `<em>${t("ow_gone")}</em>` : ""}</div>
        <div class="ow-p"><span class="fact">${zl(a.total || a.price)} zł</span>${mk}${a.name ? `<span class="hint">${esc(a.name)}</span>` : ""}</div>
        <div class="ow-whys">${(a.why || []).map(owWhy).join("")}</div>
      </div>
      <div class="ow-acts">
        <button class="btn" type="button" data-act="url">${ICON.web} ${t("ow_open")}</button>
        <button class="btn" type="button" data-act="script">${open ? t("ow_close") : t("ow_script")}</button>
      </div>
    </div>
    ${open ? `<div class="ow-more-box">
      <div class="ow-script"><pre id="owTxt">${esc(owScript(a))}</pre>
        <button class="text-btn" type="button" data-act="copy">${t("ow_copy")}</button></div>
      <div class="ow-side">
        ${a.detail && a.detail.snippet ? `<p class="ow-snip">${esc(a.detail.snippet.replace(/[.\s…]+$/, ""))}…</p>` : ""}
        <h4>${t("ow_obj")}</h4>
        <dl class="ow-obj">${owObjections().map(([q2, r]) => `<dt>${esc(q2)}</dt><dd>${esc(r)}</dd>`).join("")}</dl>
        <textarea class="pop-in ow-note" data-note="${esc(a.id)}" rows="2" placeholder="${esc(t("ow_note"))}">${esc(a.note || "")}</textarea>
        <div class="ow-btns">${btns.map(btn).join("")}</div>
      </div></div>` : ""}
  </li>`;
}

async function owClick(e) {
  const li = e.target.closest(".ow-row"); if (!li) return;
  const id = li.dataset.id, a = OW.data.items.find((x) => x.id === id); if (!a) return;
  const act = e.target.closest("[data-act]"), stb = e.target.closest("[data-st]");
  if (act) {
    const k = act.dataset.act;
    if (k === "url") return api("/api/open", { what: "url", url: a.url }).catch((err) => toast(err.message, true));
    if (k === "script") { OW.open = OW.open === id ? "" : id; return drawOwners(); }
    if (k === "copy") {
      try { await navigator.clipboard.writeText(owScript(a)); toast(t("ow_copied")); } catch (err) { toast(err.message, true); }
      return;
    }
    if (k === "photo") {
      try { await api("/api/create", { text: a.url, force: false, telegram: true }); toast(t("ow_photo_ok")); setMode("photo"); }
      catch (err) { toast(err.message, true); }
      return;
    }
  }
  if (stb) {
    const st = stb.dataset.st;
    try {
      await api("/api/owners", { op: "status", id, status: st });
      const prev = a.status || "new";
      a.status = st;
      OW.data.counts[prev] = Math.max(0, (OW.data.counts[prev] || 0) - 1);
      OW.data.counts[st] = (OW.data.counts[st] || 0) + 1;
      if (st !== "agreed") OW.open = "";
      if (!RM) { li.classList.add("leaving"); setTimeout(drawOwners, 220); } else drawOwners();
    } catch (err) { toast(err.message, true); }
    return;
  }
  if (!e.target.closest("textarea, input, a, button")) { OW.open = OW.open === id ? "" : id; drawOwners(); }
}

async function owNote(e) {
  const ta = e.target.closest("[data-note]"); if (!ta) return;
  try {
    await api("/api/owners", { op: "status", id: ta.dataset.note, note: ta.value });
    const a = OW.data.items.find((x) => x.id === ta.dataset.note); if (a) a.note = ta.value;
    toast(t("ow_saved"));
  } catch (err) { toast(err.message, true); }
}

async function owScan() {
  try { await api("/api/owners", { op: "scan" }); } catch (e) { toast(e.message, true); }
  setTimeout(() => ownersOpen(true), 600);
}

MODE_OPEN.owners = () => ownersOpen();
applyStatic();
if (SV.mode === "owners") setMode("owners", true);
