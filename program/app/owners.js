"use strict";
/* Собственники: частные объявления Otodom с оценкой «кому агент нужнее», скрипт звонка и статусы.
   Подключается после clients.js. */

const OW_L = {
ru: {
  m_owners: "Собственники",
  ow_f_calls: "Перезвоны", cl_sub: "Вставь ссылку с Otodom, можно сразу с телефоном и «в пятницу перезвонить». Утром в нужный день придёт напоминание.",
  cl_ph: "Ссылка на объявление, телефон и заметка, например: https://www.otodom.pl/… tel 535 016 721 в пятницу перезвонить",
  cl_add: "Добавить", cl_adding: "Открываю объявление…", cl_find: "Номер телефона или улица", cl_empty: "Пока пусто. Вставь ссылку выше, как в канал «Перезвоны».",
  cl_sec_today: "Сегодня", cl_sec_later: "Позже", cl_sec_nodate: "Без даты", cl_sec_done: "Сделано",
  cl_today: "сегодня", cl_tomorrow: "завтра", cl_overdue: "с {d}", cl_no_phone: "нет телефона", cl_no_title: "Без названия",
  cl_phone: "Телефон", cl_note: "Заметка", cl_when: "Перезвонить:", cl_w_today: "Сегодня", cl_w_tomorrow: "Завтра", cl_w_fri: "Пятница", cl_w_week: "Через неделю", cl_w_none: "Без даты",
  cl_done: "Позвонил ✓", cl_reopen: "Вернуть", cl_copy_phone: "Копировать номер", cl_delete: "Удалить", cl_to_calls: "В перезвоны", cl_added: "Добавлено в «Перезвоны»",
  ow_title: "Собственники", ow_sub: "Частные объявления Otodom по 18 районам. Сверху те, кому агент нужнее всего. Обновляется раз в день, пока программа открыта.",
  ow_last: "проверено {d}", ow_refresh: "Обновить сейчас", ow_running: "Собираю районы: {n} из {t}…", ow_reading: "Читаю объявления: {n} из {t}…",
  ow_empty_t: "Список ещё не собран", ow_empty: "Программа пройдёт по частным объявлениям во всех районах Варшавы (5–10 минут) и отсортирует собственников по шансу на сотрудничество.",
  ow_f_new: "К звонку", ow_f_called: "Звонил", ow_f_agreed: "Согласны", ow_f_refused: "Отказ", ow_f_hidden: "Скрытые",
  ow_all: "Все районы", ow_price_all: "Любая цена", ow_price_to: "до {n} zł", ow_price_from: "от {n} zł", ow_find: "Улица или район", ow_more: "Показать ещё", ow_none: "Здесь пока пусто.",
  ow_open: "Открыть на Otodom", ow_script: "Скрипт звонка", ow_close: "Свернуть",
  ow_s_called: "Поговорил", ow_s_nocall: "Не дозвонился", ow_s_agreed: "Согласен на 50%", ow_s_refused: "Отказ", ow_s_hidden: "Скрыть", ow_s_back: "Вернуть в список",
  ow_note: "Заметка: когда перезвонить, что сказал…", ow_photo: "Обработать фото", ow_photo_ok: "Квартира добавлена в обработку фото",
  ow_name: "Имя в скрипте", ow_gone: "снято с сайта",
  ow_hot: "горячий", ow_warm: "тёплый", ow_cold: "холодный",
  ow_saved: "Сохранено", ow_copy: "Копировать скрипт", ow_copied: "Скрипт скопирован",
  ow_obj: "Если возражает",
  w_days: "{n} дн. на сайте", w_old: "объявлению {n} мес., выставлено снова", w_drop: "цену снизили на {n} zł", w_relisted: "перевыставлено",
  w_pushed: "платит за поднятие", w_promoted: "платная реклама", w_above: "дороже рынка на {n}%", w_photos: "всего {n} фото",
  w_neg: "пишет «без посредников»", w_pos: "агенты приветствуются", w_empty: "давно пустует", w_short: "короткое описание", w_others: "{n} объявл. у владельца", w_many: "{n} объявлений: похоже на компанию",
},
uk: {
  m_owners: "Власники",
  ow_f_calls: "Передзвони", cl_sub: "Встав посилання з Otodom, можна одразу з телефоном і «в п'ятницю передзвонити». Зранку в потрібний день прийде нагадування.",
  cl_ph: "Посилання на оголошення, телефон і нотатка, наприклад: https://www.otodom.pl/… tel 535 016 721 в п'ятницю передзвонити",
  cl_add: "Додати", cl_adding: "Відкриваю оголошення…", cl_find: "Номер телефону або вулиця", cl_empty: "Поки порожньо. Встав посилання вище, як у канал «Перезвоны».",
  cl_sec_today: "Сьогодні", cl_sec_later: "Пізніше", cl_sec_nodate: "Без дати", cl_sec_done: "Зроблено",
  cl_today: "сьогодні", cl_tomorrow: "завтра", cl_overdue: "з {d}", cl_no_phone: "немає телефону", cl_no_title: "Без назви",
  cl_phone: "Телефон", cl_note: "Нотатка", cl_when: "Передзвонити:", cl_w_today: "Сьогодні", cl_w_tomorrow: "Завтра", cl_w_fri: "П'ятниця", cl_w_week: "Через тиждень", cl_w_none: "Без дати",
  cl_done: "Подзвонив ✓", cl_reopen: "Повернути", cl_copy_phone: "Копіювати номер", cl_delete: "Видалити", cl_to_calls: "У передзвони", cl_added: "Додано в «Передзвони»",
  ow_title: "Власники", ow_sub: "Приватні оголошення Otodom по 18 районах. Зверху ті, кому агент потрібен найбільше. Оновлюється раз на день, поки програма відкрита.",
  ow_last: "перевірено {d}", ow_refresh: "Оновити зараз", ow_running: "Збираю райони: {n} з {t}…", ow_reading: "Читаю оголошення: {n} з {t}…",
  ow_empty_t: "Список ще не зібраний", ow_empty: "Програма пройде по приватних оголошеннях у всіх районах Варшави (5–10 хвилин) і відсортує власників за шансом на співпрацю.",
  ow_f_new: "До дзвінка", ow_f_called: "Дзвонив", ow_f_agreed: "Згодні", ow_f_refused: "Відмова", ow_f_hidden: "Приховані",
  ow_all: "Усі райони", ow_price_all: "Будь-яка ціна", ow_price_to: "до {n} zł", ow_price_from: "від {n} zł", ow_find: "Вулиця або район", ow_more: "Показати ще", ow_none: "Тут поки порожньо.",
  ow_open: "Відкрити на Otodom", ow_script: "Скрипт дзвінка", ow_close: "Згорнути",
  ow_s_called: "Поговорив", ow_s_nocall: "Не додзвонився", ow_s_agreed: "Згоден на 50%", ow_s_refused: "Відмова", ow_s_hidden: "Приховати", ow_s_back: "Повернути в список",
  ow_note: "Нотатка: коли передзвонити, що сказав…", ow_photo: "Обробити фото", ow_photo_ok: "Квартиру додано в обробку фото",
  ow_name: "Ім'я в скрипті", ow_gone: "знято з сайту",
  ow_hot: "гарячий", ow_warm: "теплий", ow_cold: "холодний",
  ow_saved: "Збережено", ow_copy: "Копіювати скрипт", ow_copied: "Скрипт скопійовано",
  ow_obj: "Якщо заперечує",
  w_days: "{n} дн. на сайті", w_old: "оголошенню {n} міс., виставлено знову", w_drop: "ціну знизили на {n} zł", w_relisted: "перевиставлено",
  w_pushed: "платить за підняття", w_promoted: "платна реклама", w_above: "дорожче ринку на {n}%", w_photos: "лише {n} фото",
  w_neg: "пише «без посередників»", w_pos: "агентів запрошують", w_empty: "давно пустує", w_short: "короткий опис", w_others: "{n} оголош. у власника", w_many: "{n} оголошень: схоже на компанію",
},
pl: {
  m_owners: "Właściciele",
  ow_f_calls: "Oddzwonić", cl_sub: "Wklej link z Otodom, od razu z telefonem i np. „w piątek oddzwonić”. Rano w dany dzień przyjdzie przypomnienie.",
  cl_ph: "Link do ogłoszenia, telefon i notatka, np.: https://www.otodom.pl/… tel 535 016 721 w piątek oddzwonić",
  cl_add: "Dodaj", cl_adding: "Otwieram ogłoszenie…", cl_find: "Numer telefonu lub ulica", cl_empty: "Na razie pusto. Wklej link powyżej.",
  cl_sec_today: "Dziś", cl_sec_later: "Później", cl_sec_nodate: "Bez daty", cl_sec_done: "Zrobione",
  cl_today: "dziś", cl_tomorrow: "jutro", cl_overdue: "od {d}", cl_no_phone: "brak telefonu", cl_no_title: "Bez tytułu",
  cl_phone: "Telefon", cl_note: "Notatka", cl_when: "Oddzwonić:", cl_w_today: "Dziś", cl_w_tomorrow: "Jutro", cl_w_fri: "Piątek", cl_w_week: "Za tydzień", cl_w_none: "Bez daty",
  cl_done: "Zadzwoniłem ✓", cl_reopen: "Przywróć", cl_copy_phone: "Kopiuj numer", cl_delete: "Usuń", cl_to_calls: "Do oddzwonienia", cl_added: "Dodano do „Oddzwonić”",
  ow_title: "Właściciele", ow_sub: "Prywatne ogłoszenia z Otodom w 18 dzielnicach. Na górze ci, którym agent jest najbardziej potrzebny. Odświeżane raz dziennie, gdy program jest otwarty.",
  ow_last: "sprawdzono {d}", ow_refresh: "Odśwież teraz", ow_running: "Zbieram dzielnice: {n} z {t}…", ow_reading: "Czytam ogłoszenia: {n} z {t}…",
  ow_empty_t: "Lista nie jest jeszcze zebrana", ow_empty: "Program przejdzie przez prywatne ogłoszenia we wszystkich dzielnicach Warszawy (5–10 minut) i ułoży właścicieli według szansy na współpracę.",
  ow_f_new: "Do telefonu", ow_f_called: "Dzwoniłem", ow_f_agreed: "Zgoda", ow_f_refused: "Odmowa", ow_f_hidden: "Ukryte",
  ow_all: "Wszystkie dzielnice", ow_price_all: "Każda cena", ow_price_to: "do {n} zł", ow_price_from: "od {n} zł", ow_find: "Ulica lub dzielnica", ow_more: "Pokaż więcej", ow_none: "Na razie pusto.",
  ow_open: "Otwórz na Otodom", ow_script: "Skrypt rozmowy", ow_close: "Zwiń",
  ow_s_called: "Rozmawiałem", ow_s_nocall: "Nie odebrał", ow_s_agreed: "Zgoda na 50%", ow_s_refused: "Odmowa", ow_s_hidden: "Ukryj", ow_s_back: "Przywróć",
  ow_note: "Notatka: kiedy oddzwonić, co powiedział…", ow_photo: "Obrób zdjęcia", ow_photo_ok: "Mieszkanie dodane do obróbki zdjęć",
  ow_name: "Imię w skrypcie", ow_gone: "zdjęte z portalu",
  ow_hot: "gorący", ow_warm: "ciepły", ow_cold: "zimny",
  ow_saved: "Zapisano", ow_copy: "Kopiuj skrypt", ow_copied: "Skrypt skopiowany",
  ow_obj: "Jeśli ma obiekcje",
  w_days: "{n} dni na portalu", w_old: "ogłoszenie ma {n} mies., wystawione ponownie", w_drop: "cena obniżona o {n} zł", w_relisted: "wystawione ponownie",
  w_pushed: "płaci za podbicie", w_promoted: "płatna promocja", w_above: "{n}% drożej niż rynek", w_photos: "tylko {n} zdjęć",
  w_neg: "pisze „bez pośredników”", w_pos: "biura mile widziane", w_empty: "długo stoi puste", w_short: "krótki opis", w_others: "{n} ogłosz. właściciela", w_many: "{n} ogłoszeń: raczej firma",
},
};
Object.assign(L.ru, OW_L.ru); Object.assign(L.uk, OW_L.uk); Object.assign(L.pl, OW_L.pl);

const OW = { data: null, filter: "new", district: "", q: "", shown: 40, open: "", timer: 0, price: "" };
try { OW.price = localStorage.getItem("hermea_ow_price") || ""; } catch (e) {}
const OW_PRICES = ["", "0-4000", "0-6000", "0-8000", "8000-999999"];
try { OW.filter = localStorage.getItem("hermea_ow_filter") || "new"; } catch (e) {}
const OW_GROUP = { calls: [], new: ["new"], called: ["called", "nocall"], agreed: ["agreed"], refused: ["refused"], hidden: ["hidden"] };

function owName() {
  try { return localStorage.getItem("hermea_ow_name") || "Paweł"; } catch (e) { return "Paweł"; }
}

async function ownersOpen(quiet) {
  try {
    const [d, c] = await Promise.all([api("/api/owners"), api("/api/calls")]);
    OW.data = d; OW.calls = c; drawOwners(!quiet);
  } catch (e) { toast(e.message, true); }
  clearTimeout(OW.timer);
  if (OW.data && OW.data.state && OW.data.state.state === "running")
    OW.timer = setTimeout(() => { if (SV.mode === "owners") ownersOpen(true); }, 2500);
}

function owWhy(w) {
  const [k, v] = w;
  const txt = k === "days" ? t("w_days", { n: v }) : k === "old" ? t("w_old", { n: v }) : k === "drop" ? t("w_drop", { n: zl(v) })
    : k === "above" ? t("w_above", { n: v }) : k === "photos" ? t("w_photos", { n: v }) : k === "others" ? t("w_others", { n: v }) : k === "many" ? t("w_many", { n: v })
    : t("w_" + k);
  const cls = k === "neg" ? "bad" : k === "pos" || k === "empty" || k === "drop" ? "good" : "";
  return `<span class="ow-why ${cls}">${esc(txt)}</span>`;
}

function owPriceLabel(p) {
  if (!p) return t("ow_price_all");
  const [lo, hi] = p.split("-").map(Number);
  return lo ? t("ow_price_from", { n: zl(lo) }) : t("ow_price_to", { n: zl(hi) });
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

Pracujemy tak: robimy prezentacje, sprawdzamy najemców i ich dokumenty, przygotowujemy umowę, także najem okazjonalny. Nasze wynagrodzenie to 50% jednego czynszu najmu plus 23% VAT, płatne dopiero po podpisaniu umowy z najemcą. Jeśli nie znajdziemy najemcy, nic Pan/Pani nie płaci.

Czy mogę zaprosić naszych klientów na prezentację? Kiedy byłoby wygodnie pokazać mieszkanie?`;
}
function owObjections() {
  return [
    ["Mam dużo telefonów", "Rozumiem. My przyprowadzamy już sprawdzonych najemców z dokumentami, więc oszczędza Pan/Pani czas na niepotrzebnych prezentacjach."],
    ["Nie chcę płacić prowizji", "Rozumiem. Płaci Pan/Pani tylko po podpisaniu umowy i to połowę jednego czynszu plus VAT, a jeden pusty miesiąc kosztuje cały czynsz."],
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
  if (OW.filter === "calls") return drawCalls(first);
  if (!d.last_scan && !d.items.length) {
    box.innerHTML = `<div class="sv-wrap ow-wrap"><div class="cl-head"><div><h1 class="display">${t("ow_title")}</h1><p class="sv-sub">${t("ow_sub")}</p></div></div>
      <div class="ow-bar">${owSegHtml()}</div>
      <div class="mk-empty rise"><b>${t("ow_empty_t")}</b><p>${t("ow_empty")}</p>
      <button class="btn-primary" type="button" id="owGo" ${run ? "disabled" : ""}>${esc(runTxt)}</button></div></div>`;
    $("#owGo").onclick = owScan;
    $("#owSeg").onclick = owSegClick;
    requestAnimationFrame(() => slideSeg($("#owSeg")));
    return;
  }
  const groups = OW_GROUP[OW.filter] || OW_GROUP.new;
  const cnt = (g) => owCnt(g);
  const q = OW.q.trim().toLowerCase();
  let rows = d.items.filter((a) => groups.includes(a.status || "new"));
  if (OW.filter === "new") rows = rows.filter((a) => !a.gone);
  if (OW.district) rows = rows.filter((a) => (a.district || "") === OW.district);
  if (OW.price) { const [lo, hi] = OW.price.split("-").map(Number); rows = rows.filter((a) => { const v = a.total || a.price || 0; return v >= lo && v <= hi; }); }
  if (q) rows = rows.filter((a) => `${a.street} ${a.district} ${a.sub} ${a.title}`.toLowerCase().includes(q));
  const dists = [...new Set(d.items.map((a) => a.district).filter(Boolean))].sort((a, b) => a.localeCompare(b));
  box.innerHTML = `<div class="sv-wrap ow-wrap">
    <div class="cl-head"><div><h1 class="display">${t("ow_title")}</h1>
      <p class="sv-sub"><span>${esc(t("ow_sub"))}</span>${d.last_scan ? `<span class="today-pill">${esc(t("ow_last", { d: dd(d.last_scan) }))}</span>` : ""}</p></div>
      <button class="btn" type="button" id="owGo" ${run ? "disabled" : ""}>${ICON.refresh} ${esc(runTxt)}</button></div>
    <div class="ow-bar">
      <div class="seg" id="owSeg">${Object.keys(OW_GROUP).map((g) => `<button type="button" data-g="${g}" aria-pressed="${g === OW.filter}">${t("ow_f_" + g)} <small>${cnt(g)}</small></button>`).join("")}</div>
      <select class="pop-in ow-sel" id="owDist"><option value="">${t("ow_all")}</option>${dists.map((x) => `<option ${x === OW.district ? "selected" : ""}>${esc(x)}</option>`).join("")}</select>
      <select class="pop-in ow-sel" id="owPrice">${OW_PRICES.map((p) => `<option value="${p}" ${p === OW.price ? "selected" : ""}>${owPriceLabel(p)}</option>`).join("")}</select>
      <input class="pop-in ow-q" id="owQ" type="search" placeholder="${esc(t("ow_find"))}" value="${esc(OW.q)}">
      <label class="ow-name">${t("ow_name")} <input class="pop-in" id="owName" value="${esc(owName())}" maxlength="40"></label>
    </div>
    <ol class="ow-list" id="owList">${rows.slice(0, OW.shown).map(owRow).join("") || `<li class="ow-none">${t("ow_none")}</li>`}</ol>
    ${rows.length > OW.shown ? `<button class="btn ow-more" type="button" id="owMore">${t("ow_more")} (${rows.length - OW.shown})</button>` : ""}
  </div>`;
  if (first) enter($("#owList"), ":scope > li");
  requestAnimationFrame(() => slideSeg($("#owSeg")));
  $("#owGo").onclick = owScan;
  $("#owSeg").onclick = owSegClick;
  $("#owDist").onchange = (e) => { OW.district = e.target.value; OW.shown = 40; drawOwners(true); };
  $("#owPrice").onchange = (e) => { OW.price = e.target.value; OW.shown = 40; try { localStorage.setItem("hermea_ow_price", OW.price); } catch (err) {} drawOwners(true); };
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
        <div class="ow-btns">${btns.map(btn).join("")}<button class="text-btn" type="button" data-act="tocall">${t("cl_to_calls")}</button></div>
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
    if (k === "tocall") {
      try { OW.calls = await api("/api/calls", { op: "from_owner", id }); OW.filter = "calls"; OW.callOpen = ""; drawOwners(true); toast(t("cl_added")); }
      catch (err) { toast(err.message, true); }
      return;
    }
    if (k === "photo") {
      try { await api("/api/create", { text: a.url, force: false, telegram: true, no_fee: true }); toast(t("ow_photo_ok")); setMode("photo"); }
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

function owCnt(g) {
  if (g === "calls") return (OW.calls && OW.calls.due) || "";
  const d = OW.data || {};
  return OW_GROUP[g].reduce((s, k) => s + ((d.counts || {})[k] || 0), 0);
}
function owSegHtml() {
  return `<div class="seg" id="owSeg">${Object.keys(OW_GROUP).map((g) => `<button type="button" data-g="${g}" aria-pressed="${g === OW.filter}"${g === "calls" && owCnt("calls") ? ' class="due"' : ""}>${t("ow_f_" + g)} <small>${owCnt(g)}</small></button>`).join("")}</div>`;
}
function owSegClick(e) {
  const b = e.target.closest("[data-g]"); if (!b) return;
  OW.filter = b.dataset.g; OW.shown = 40; OW.open = "";
  try { localStorage.setItem("hermea_ow_filter", OW.filter); } catch (err) {}
  drawOwners(true);
}

// ---------------------------------------------------------------- перезвоны
function clDay(iso) {
  if (!iso) return "";
  const d = parseIso(iso), td = parseIso(OW.calls.today);
  const diff = Math.round((d - td) / 86400000);
  if (diff === 0) return t("cl_today");
  if (diff === 1) return t("cl_tomorrow");
  if (diff < 0) return t("cl_overdue", { d: d.toLocaleDateString(LOCALE[LANG], { day: "numeric", month: "short" }) });
  return d.toLocaleDateString(LOCALE[LANG], { weekday: "short", day: "numeric", month: "short" });
}
function clRow(c) {
  const open = OW.callOpen === c.id;
  const rooms = c.rooms ? `${c.rooms} ${LANG === "pl" ? "pok." : LANG === "uk" ? "кімн." : "комн."}` : "";
  const price = (c.price || 0) + (c.rent || 0);
  const place = [c.district, c.street].filter(Boolean).join(", ");
  const due = c.status === "open" && c.remind && c.remind <= OW.calls.today;
  return `<li class="cl-row${due ? " due" : ""}${c.status === "done" ? " done" : ""}${open ? " open" : ""}" data-id="${esc(c.id)}">
    <div class="cl-main">
      ${c.img ? `<img class="ow-img" src="${esc(c.img)}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.style.visibility='hidden'">` : `<div class="ow-img"></div>`}
      <div class="ow-info">
        <div class="ow-t"><b>${esc(place || c.title || t("cl_no_title"))}</b><span>${esc([rooms, c.area ? Math.round(parseFloat(String(c.area).replace(",", "."))) + " м²" : "", price ? zl(price) + " zł" : ""].filter(Boolean).join(" · "))}</span></div>
        ${c.title && place ? `<div class="cl-sub">${esc(c.title)}</div>` : ""}
        ${c.note && !open ? `<div class="cl-note">${esc(c.note)}</div>` : ""}
      </div>
      <div class="cl-phone">${c.phone ? `<a href="tel:+48${esc(c.phone)}" class="cl-tel">${esc(c.phone_pretty)}</a>` : `<span class="hint">${t("cl_no_phone")}</span>`}
        ${c.remind ? `<span class="cl-when${due ? " due" : ""}">${esc(clDay(c.remind))}</span>` : ""}</div>
    </div>
    ${open ? `<div class="cl-edit">
      <label>${t("cl_phone")} <input class="pop-in" data-f="phone" value="${esc(c.phone_pretty || "")}" placeholder="535 016 721" inputmode="tel"></label>
      <label class="cl-n">${t("cl_note")} <textarea class="pop-in" data-f="note" rows="2">${esc(c.note || "")}</textarea></label>
      <div class="cl-dates">${t("cl_when")}
        ${["today", "tomorrow", "fri", "week"].map((k) => `<button class="chip" type="button" data-when="${k}">${t("cl_w_" + k)}</button>`).join("")}
        <input class="pop-in" type="date" data-f="remind" value="${esc(c.remind || "")}">
        ${c.remind ? `<button class="text-btn" type="button" data-when="none">${t("cl_w_none")}</button>` : ""}</div>
      <div class="ow-btns">
        ${c.status === "open" ? `<button class="btn ow-yes" type="button" data-cl="done">${t("cl_done")}</button>` : `<button class="btn" type="button" data-cl="open">${t("cl_reopen")}</button>`}
        ${c.url ? `<button class="btn" type="button" data-cl="url">${ICON.web} Otodom</button>` : ""}
        ${c.phone ? `<button class="btn" type="button" data-cl="copy">${t("cl_copy_phone")}</button>` : ""}
        <button class="text-btn ow-no" type="button" data-cl="del">${t("cl_delete")}</button>
      </div></div>` : ""}
  </li>`;
}
function drawCalls(first) {
  const box = $("#owners"), c = OW.calls || { items: [], today: "" };
  const q = (OW.cq || "").trim().toLowerCase(), qd = q.replace(/\D/g, "");
  let items = c.items;
  if (q) items = items.filter((x) => (qd.length >= 3 && (x.phone || "").includes(qd)) || `${x.street} ${x.district} ${x.title} ${x.note}`.toLowerCase().includes(q));
  const open = items.filter((x) => x.status === "open");
  const today = open.filter((x) => x.remind && x.remind <= c.today).sort((a, b) => a.remind.localeCompare(b.remind));
  const later = open.filter((x) => x.remind && x.remind > c.today).sort((a, b) => a.remind.localeCompare(b.remind));
  const nodate = open.filter((x) => !x.remind);
  const done = items.filter((x) => x.status === "done");
  const sec = (title, arr, cls) => arr.length ? `<h3 class="cards-h ${cls || ""}">${esc(title)} <small>${arr.length}</small></h3><ol class="ow-list">${arr.map(clRow).join("")}</ol>` : "";
  box.innerHTML = `<div class="sv-wrap ow-wrap">
    <div class="cl-head"><div><h1 class="display">${t("ow_title")}</h1><p class="sv-sub"><span>${esc(t("cl_sub"))}</span></p></div></div>
    <div class="ow-bar">${owSegHtml()}
      <input class="pop-in ow-q" id="clQ" type="search" placeholder="${esc(t("cl_find"))}" value="${esc(OW.cq || "")}"></div>
    <form class="cl-add" id="clAdd">
      <textarea class="pop-in" id="clText" rows="2" placeholder="${esc(t("cl_ph"))}"></textarea>
      <button class="btn-primary" type="submit" id="clGo">${t("cl_add")}</button>
    </form>
    <div id="clList">
      ${sec(t("cl_sec_today"), today, "new")}${sec(t("cl_sec_later"), later)}${sec(t("cl_sec_nodate"), nodate)}
      ${!today.length && !later.length && !nodate.length ? `<p class="ow-none">${q ? t("ow_none") : t("cl_empty")}</p>` : ""}
      ${done.length ? `<details class="cl-done"><summary>${t("cl_sec_done")} (${done.length})</summary><ol class="ow-list">${done.slice(0, 50).map(clRow).join("")}</ol></details>` : ""}
    </div></div>`;
  if (first) enter($("#clList"), ".cl-row");
  requestAnimationFrame(() => slideSeg($("#owSeg")));
  $("#owSeg").onclick = owSegClick;
  $("#clQ").oninput = (e) => { OW.cq = e.target.value; clearTimeout(OW.qt); OW.qt = setTimeout(() => { drawCalls(); const i = $("#clQ"); i.focus(); i.setSelectionRange(i.value.length, i.value.length); }, 200); };
  $("#clText").addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("#clAdd").requestSubmit(); } });
  $("#clText").addEventListener("paste", () => setTimeout(() => { const v = $("#clText").value; if (/https?:\/\//.test(v) && /\d{3}[\s-]?\d{3}[\s-]?\d{3}|[a-zа-яіїє]{4,}\s*$/i.test(v.replace(/https?:\/\/\S+/, ""))) $("#clAdd").requestSubmit(); }, 30));
  $("#clAdd").onsubmit = async (e) => {
    e.preventDefault();
    const text = $("#clText").value.trim(); if (!text) return;
    $("#clGo").disabled = true; $("#clGo").textContent = t("cl_adding");
    try { OW.calls = await api("/api/calls", { op: "add", text }); OW.callOpen = OW.calls.items[0] && OW.calls.items[0].id; drawCalls(); }
    catch (err) { toast(err.message, true); $("#clGo").disabled = false; $("#clGo").textContent = t("cl_add"); }
  };
  $("#clList").onclick = clClick;
  $("#clList").addEventListener("change", clChange);
}
async function clSave(id, patch) {
  try { OW.calls = await api("/api/calls", Object.assign({ op: "update", id }, patch)); } catch (e) { toast(e.message, true); }
}
async function clClick(e) {
  const li = e.target.closest(".cl-row"); if (!li) return;
  const id = li.dataset.id, c = OW.calls.items.find((x) => x.id === id); if (!c) return;
  const w = e.target.closest("[data-when]"), b = e.target.closest("[data-cl]");
  if (e.target.closest("a.cl-tel")) return;
  if (w) {
    const k = w.dataset.when, td = parseIso(OW.calls.today);
    const add = (n) => { const d = new Date(td); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };
    const val = k === "none" ? "" : k === "today" ? OW.calls.today : k === "tomorrow" ? add(1) : k === "week" ? add(7) : add(((5 - td.getDay() + 7) % 7) || 7);
    await clSave(id, { remind: val }); OW.callOpen = ""; return drawCalls();
  }
  if (b) {
    const k = b.dataset.cl;
    if (k === "url") return api("/api/open", { what: "url", url: c.url }).catch((err) => toast(err.message, true));
    if (k === "copy") { try { await navigator.clipboard.writeText(c.phone_pretty); toast(t("copied")); } catch (err) {} return; }
    if (k === "del") { try { OW.calls = await api("/api/calls", { op: "delete", id }); } catch (err) { toast(err.message, true); } return drawCalls(); }
    if (k === "done" || k === "open") { await clSave(id, { status: k }); OW.callOpen = ""; return drawCalls(); }
  }
  if (e.target.closest("input, textarea, button, a, label")) return;
  OW.callOpen = OW.callOpen === id ? "" : id; drawCalls();
}
async function clChange(e) {
  const f = e.target.closest("[data-f]"); if (!f) return;
  const li = e.target.closest(".cl-row");
  await clSave(li.dataset.id, { [f.dataset.f]: f.value });
  if (f.dataset.f === "remind") { OW.callOpen = ""; drawCalls(); } else toast(t("ow_saved"));
}

// счётчик «сегодня перезвонить» на вкладке
setInterval(() => {
  const b = document.querySelector('[data-mode="owners"]'); if (!b || !S.st) return;
  const n = S.st.calls_due || 0;
  b.dataset.due = n ? String(n) : "";
}, 2000);

async function owScan() {
  try { await api("/api/owners", { op: "scan" }); } catch (e) { toast(e.message, true); }
  setTimeout(() => ownersOpen(true), 600);
}

MODE_OPEN.owners = () => ownersOpen();
applyStatic();
if (SV.mode === "owners") setMode("owners", true);
