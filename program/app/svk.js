"use strict";
/* СВК — ежедневная сводка агента. Подключается после основного скрипта и пользуется его помощниками
   ($, esc, api, t, plural, toast, LANG, LOCALE, S). */

// ================================================================ тексты
Object.assign(L.ru, {
  m_photo: "Обработка фото", m_svk: "СВК",
  sv_day: "День", sv_week: "Неделя", sv_month: "Месяц", sv_report: "Отчёт",
  sv_today: "сегодня", sv_yesterday: "вчера", sv_plan_done: "план дня выполнен на {p}%", sv_weekend: "выходной",
  sv_leads: "Лиды", sv_direct: "Прямой клиент", sv_agents: "Риэлтор другого агентства", sv_duty: "Дежурный телефон",
  sv_ads: "Публикации", sv_ads_sub: "OLX, Threads и другие личные объявления",
  sv_auto: "В программе сегодня обработано: {n} {flats}.", sv_auto_add: "Записать {n} {pubs}",
  pubs: ["публикацию", "публикации", "публикаций"],
  sv_shows: "Показы", sv_shows_plan: "Назначено", sv_shows_fact: "Проведено",
  sv_docs: "Договоры за день", sv_coop: "Клиент – агентство", sv_open: "Umowa otwarta", sv_open_sub: "объект на неэксклюзиве",
  sv_excl: "Эксклюзив с собственником", sv_deposit: "Задаток / резервация", sv_main: "Основной договор", sv_main_sub: "аренда или купля-продажа",
  sv_deals: "Сделки и деньги", sv_clients: "Клиентов в работе", sv_clients_sub: "активные сделки на сегодня",
  sv_pending: "Ждут основного договора", sv_closed: "Сделок закрыто", sv_closed_sub: "комиссия поступила",
  sv_comm: "Комиссия получена", sv_expected: "Ожидаемая комиссия", sv_expected_sub: "по забронированным сделкам",
  sv_lost: "Отказы и потерянные клиенты", sv_lost_btn: "Записать отказ",
  sv_of: "из {n}", sv_was: "вчера {n}", sv_add_sum: "Добавить сумму",
  sv_log: "Журнал дня", sv_log_empty: "Нажимайте «+», когда что-то происходит. Здесь соберётся весь день, и по нему легко отчитаться.",
  sv_note_add: "заметка", sv_undo: "Удалить запись", sv_fixed: "исправлено вручную",
  j_direct: "Лид: прямой клиент", j_agents: "Лид: риэлтор", j_duty: "Лид: дежурство", j_ads: "Публикация",
  j_shows_plan: "Показ назначен", j_shows: "Показ проведён", j_coop: "Договор клиент – агентство", j_open: "Umowa otwarta",
  j_excl: "Эксклюзив", j_deposit: "Задаток / резервация", j_main: "Основной договор", j_closed: "Сделка закрыта",
  j_comm: "Комиссия", j_lost: "Отказ",
  p_reason: "Причина и этап (необязательно)", p_reason_ph: "например, выбрал другое агентство",
  p_comm: "Комиссия по этой сделке, zł", p_amount: "Сумма комиссии, zł", p_note: "Кто или откуда (необязательно)",
  p_plan: "План на этот день", p_plan_def: "Сделать планом на каждый будний день", p_save: "Записать", p_cancel: "Отмена",
  p_plan_saved: "План сохранён", sv_goal: "План дня выполнен 🎯",
  r_title: "Отчёт", r_day: "За день", r_week: "За неделю", r_copy: "Копировать отчёт", r_copy_tsv: "Копировать для таблицы",
  r_copied: "Отчёт скопирован", r_tsv_copied: "Скопировано: 17 строк План и Факт",
  r_howto: "<b>Как вставить в таблицу СВК:</b> нажмите «Копировать для таблицы», в Google Таблице кликните ячейку «План» нужного дня в строке «Кол-во полученных лидов» и вставьте (⌘V). Заполнятся все 17 строк сразу, План и Факт.",
  r_name: "Имя в отчёте", r_name_ph: "например, Pashhhtet",
  r_leads: "Лиды", r_direct: "прямые клиенты", r_agents: "риэлторы других агентств", r_duty: "дежурный телефон",
  r_ads: "Публикации", r_clients: "Клиентов в работе", r_coop: "Договоры клиент – агентство", r_open: "Umowa otwarta",
  r_excl: "Эксклюзивы", r_shows: "Показы", r_shows_of: "{f} из {p} назначенных", r_deposit: "Задатки / резервации",
  r_pending: "Ждут основного договора", r_main: "Основных договоров", r_closed: "Сделок закрыто", r_comm: "Комиссия получена",
  r_expected: "Ожидаемая комиссия", r_lost: "Отказы", r_total: "Выполнение плана: {p}%", r_week_of: "Неделя {a} – {b}",
  t_metric: "Показатель", t_plan: "План", t_fact: "Факт", t_total_w: "Итог недели", t_total_m: "Итог месяца", t_week_n: "{n} неделя",
  t_leads: "Кол-во полученных лидов", t_direct: "из них: прямые клиенты", t_agents: "из них: риэлторы других агентств",
  t_duty: "из них: заявки, полученные на дежурстве", t_ads: "Кол-во рекламных публикаций за день (OLX, Threads и др.)",
  t_clients: "Кол-во клиентов в работе (активных сделок) на сегодня", t_coop: "Договоров о сотрудничестве «клиент – агентство» подписано",
  t_open: "Объектов принято на неэксклюзивном договоре (umowa otwarta)", t_excl: "Договоров эксклюзива с собственниками подписано",
  t_shows: "Показов проведено (план — назначенные, факт — проведённые)", t_deposit: "Договоров задатка / резервационных подписано",
  t_pending: "Сделок в ожидании подписания основного договора", t_main: "Основных договоров подписано (аренда / купля-продажа)",
  t_closed: "Сделок закрыто (комиссия поступила)", t_comm: "Сумма поступившей комиссии, PLN",
  t_expected: "Ожидаемая комиссия по забронированным сделкам, PLN", t_lost: "Отказов / потерянных клиентов",
  s_leads: "Лиды", s_ads: "Публикации", s_shows: "Показы", s_comm: "Комиссия",
});
Object.assign(L.uk, {
  m_photo: "Обробка фото", m_svk: "СВК",
  sv_day: "День", sv_week: "Тиждень", sv_month: "Місяць", sv_report: "Звіт",
  sv_today: "сьогодні", sv_yesterday: "вчора", sv_plan_done: "план дня виконано на {p}%", sv_weekend: "вихідний",
  sv_leads: "Ліди", sv_direct: "Прямий клієнт", sv_agents: "Рієлтор іншої агенції", sv_duty: "Черговий телефон",
  sv_ads: "Публікації", sv_ads_sub: "OLX, Threads та інші особисті оголошення",
  sv_auto: "У програмі сьогодні оброблено: {n} {flats}.", sv_auto_add: "Записати {n} {pubs}",
  pubs: ["публікацію", "публікації", "публікацій"],
  sv_shows: "Покази", sv_shows_plan: "Призначено", sv_shows_fact: "Проведено",
  sv_docs: "Договори за день", sv_coop: "Клієнт – агенція", sv_open: "Umowa otwarta", sv_open_sub: "об'єкт на неексклюзиві",
  sv_excl: "Ексклюзив із власником", sv_deposit: "Завдаток / резервація", sv_main: "Основний договір", sv_main_sub: "оренда або купівля-продаж",
  sv_deals: "Угоди та гроші", sv_clients: "Клієнтів у роботі", sv_clients_sub: "активні угоди на сьогодні",
  sv_pending: "Чекають основного договору", sv_closed: "Угод закрито", sv_closed_sub: "комісія надійшла",
  sv_comm: "Комісію отримано", sv_expected: "Очікувана комісія", sv_expected_sub: "за заброньованими угодами",
  sv_lost: "Відмови та втрачені клієнти", sv_lost_btn: "Записати відмову",
  sv_of: "з {n}", sv_was: "вчора {n}", sv_add_sum: "Додати суму",
  sv_log: "Журнал дня", sv_log_empty: "Натискайте «+», коли щось відбувається. Тут збереться весь день, і за ним легко звітувати.",
  sv_note_add: "нотатка", sv_undo: "Видалити запис", sv_fixed: "виправлено вручну",
  j_direct: "Лід: прямий клієнт", j_agents: "Лід: рієлтор", j_duty: "Лід: чергування", j_ads: "Публікація",
  j_shows_plan: "Показ призначено", j_shows: "Показ проведено", j_coop: "Договір клієнт – агенція", j_open: "Umowa otwarta",
  j_excl: "Ексклюзив", j_deposit: "Завдаток / резервація", j_main: "Основний договір", j_closed: "Угоду закрито",
  j_comm: "Комісія", j_lost: "Відмова",
  p_reason: "Причина й етап (необов'язково)", p_reason_ph: "наприклад, обрав іншу агенцію",
  p_comm: "Комісія за цією угодою, zł", p_amount: "Сума комісії, zł", p_note: "Хто або звідки (необов'язково)",
  p_plan: "План на цей день", p_plan_def: "Зробити планом на кожен будній день", p_save: "Записати", p_cancel: "Скасувати",
  p_plan_saved: "План збережено", sv_goal: "План дня виконано 🎯",
  r_title: "Звіт", r_day: "За день", r_week: "За тиждень", r_copy: "Копіювати звіт", r_copy_tsv: "Копіювати для таблиці",
  r_copied: "Звіт скопійовано", r_tsv_copied: "Скопійовано: 17 рядків План і Факт",
  r_howto: "<b>Як вставити в таблицю СВК:</b> натисніть «Копіювати для таблиці», у Google Таблиці клацніть клітинку «План» потрібного дня в рядку «Кол-во полученных лидов» і вставте (⌘V). Заповняться всі 17 рядків одразу, План і Факт.",
  r_name: "Ім'я у звіті", r_name_ph: "наприклад, Pashhhtet",
  r_leads: "Ліди", r_direct: "прямі клієнти", r_agents: "рієлтори інших агенцій", r_duty: "черговий телефон",
  r_ads: "Публікації", r_clients: "Клієнтів у роботі", r_coop: "Договори клієнт – агенція", r_open: "Umowa otwarta",
  r_excl: "Ексклюзиви", r_shows: "Покази", r_shows_of: "{f} з {p} призначених", r_deposit: "Завдатки / резервації",
  r_pending: "Чекають основного договору", r_main: "Основних договорів", r_closed: "Угод закрито", r_comm: "Комісію отримано",
  r_expected: "Очікувана комісія", r_lost: "Відмови", r_total: "Виконання плану: {p}%", r_week_of: "Тиждень {a} – {b}",
  t_metric: "Показник", t_plan: "План", t_fact: "Факт", t_total_w: "Підсумок тижня", t_total_m: "Підсумок місяця", t_week_n: "{n} тиждень",
  t_leads: "Кількість отриманих лідів", t_direct: "з них: прямі клієнти", t_agents: "з них: рієлтори інших агенцій",
  t_duty: "з них: заявки на чергуванні", t_ads: "Кількість рекламних публікацій за день (OLX, Threads тощо)",
  t_clients: "Кількість клієнтів у роботі на сьогодні", t_coop: "Договорів про співпрацю «клієнт – агенція» підписано",
  t_open: "Об'єктів прийнято на неексклюзивному договорі (umowa otwarta)", t_excl: "Договорів ексклюзиву з власниками підписано",
  t_shows: "Показів проведено (план — призначені, факт — проведені)", t_deposit: "Договорів завдатку / резервації підписано",
  t_pending: "Угод в очікуванні основного договору", t_main: "Основних договорів підписано (оренда / купівля-продаж)",
  t_closed: "Угод закрито (комісія надійшла)", t_comm: "Сума отриманої комісії, PLN",
  t_expected: "Очікувана комісія за заброньованими угодами, PLN", t_lost: "Відмов / втрачених клієнтів",
  s_leads: "Ліди", s_ads: "Публікації", s_shows: "Покази", s_comm: "Комісія",
});
Object.assign(L.pl, {
  m_photo: "Obróbka zdjęć", m_svk: "Raport",
  sv_day: "Dzień", sv_week: "Tydzień", sv_month: "Miesiąc", sv_report: "Raport",
  sv_today: "dzisiaj", sv_yesterday: "wczoraj", sv_plan_done: "plan dnia wykonany w {p}%", sv_weekend: "weekend",
  sv_leads: "Leady", sv_direct: "Klient bezpośredni", sv_agents: "Agent z innej agencji", sv_duty: "Telefon dyżurny",
  sv_ads: "Publikacje", sv_ads_sub: "OLX, Threads i inne własne ogłoszenia",
  sv_auto: "W programie dziś przetworzono: {n} {flats}.", sv_auto_add: "Zapisz {n} {pubs}",
  pubs: ["publikację", "publikacje", "publikacji"],
  sv_shows: "Prezentacje", sv_shows_plan: "Umówione", sv_shows_fact: "Odbyte",
  sv_docs: "Umowy dzisiaj", sv_coop: "Klient – agencja", sv_open: "Umowa otwarta", sv_open_sub: "oferta bez wyłączności",
  sv_excl: "Wyłączność z właścicielem", sv_deposit: "Zadatek / rezerwacja", sv_main: "Umowa główna", sv_main_sub: "najem lub sprzedaż",
  sv_deals: "Transakcje i pieniądze", sv_clients: "Klienci w toku", sv_clients_sub: "aktywne transakcje na dziś",
  sv_pending: "Czekają na umowę główną", sv_closed: "Zamknięte transakcje", sv_closed_sub: "prowizja wpłynęła",
  sv_comm: "Otrzymana prowizja", sv_expected: "Oczekiwana prowizja", sv_expected_sub: "z zarezerwowanych transakcji",
  sv_lost: "Odmowy i utraceni klienci", sv_lost_btn: "Zapisz odmowę",
  sv_of: "z {n}", sv_was: "wczoraj {n}", sv_add_sum: "Dodaj kwotę",
  sv_log: "Dziennik dnia", sv_log_empty: "Klikaj „+”, gdy coś się dzieje. Tu zbierze się cały dzień i łatwo z niego zdać raport.",
  sv_note_add: "notatka", sv_undo: "Usuń wpis", sv_fixed: "poprawiono ręcznie",
  j_direct: "Lead: klient bezpośredni", j_agents: "Lead: agent", j_duty: "Lead: dyżur", j_ads: "Publikacja",
  j_shows_plan: "Prezentacja umówiona", j_shows: "Prezentacja odbyta", j_coop: "Umowa klient – agencja", j_open: "Umowa otwarta",
  j_excl: "Wyłączność", j_deposit: "Zadatek / rezerwacja", j_main: "Umowa główna", j_closed: "Transakcja zamknięta",
  j_comm: "Prowizja", j_lost: "Odmowa",
  p_reason: "Powód i etap (opcjonalnie)", p_reason_ph: "np. wybrał inną agencję",
  p_comm: "Prowizja z tej transakcji, zł", p_amount: "Kwota prowizji, zł", p_note: "Kto lub skąd (opcjonalnie)",
  p_plan: "Plan na ten dzień", p_plan_def: "Ustaw jako plan na każdy dzień roboczy", p_save: "Zapisz", p_cancel: "Anuluj",
  p_plan_saved: "Plan zapisany", sv_goal: "Plan dnia wykonany 🎯",
  r_title: "Raport", r_day: "Za dzień", r_week: "Za tydzień", r_copy: "Kopiuj raport", r_copy_tsv: "Kopiuj do tabeli",
  r_copied: "Raport skopiowany", r_tsv_copied: "Skopiowano: 17 wierszy Plan i Fakt",
  r_howto: "<b>Jak wkleić do tabeli:</b> kliknij „Kopiuj do tabeli”, w Arkuszu Google zaznacz komórkę „План” wybranego dnia w wierszu „Кол-во полученных лидов” i wklej (⌘V). Wypełni się wszystkie 17 wierszy naraz, Plan i Fakt.",
  r_name: "Imię w raporcie", r_name_ph: "np. Pashhhtet",
  r_leads: "Leady", r_direct: "klienci bezpośredni", r_agents: "agenci innych agencji", r_duty: "telefon dyżurny",
  r_ads: "Publikacje", r_clients: "Klienci w toku", r_coop: "Umowy klient – agencja", r_open: "Umowa otwarta",
  r_excl: "Wyłączności", r_shows: "Prezentacje", r_shows_of: "{f} z {p} umówionych", r_deposit: "Zadatki / rezerwacje",
  r_pending: "Czekają na umowę główną", r_main: "Umowy główne", r_closed: "Zamknięte transakcje", r_comm: "Otrzymana prowizja",
  r_expected: "Oczekiwana prowizja", r_lost: "Odmowy", r_total: "Wykonanie planu: {p}%", r_week_of: "Tydzień {a} – {b}",
  t_metric: "Wskaźnik", t_plan: "Plan", t_fact: "Fakt", t_total_w: "Suma tygodnia", t_total_m: "Suma miesiąca", t_week_n: "Tydzień {n}",
  t_leads: "Liczba otrzymanych leadów", t_direct: "w tym: klienci bezpośredni", t_agents: "w tym: agenci innych agencji",
  t_duty: "w tym: zgłoszenia z dyżuru", t_ads: "Liczba publikacji reklamowych (OLX, Threads itp.)",
  t_clients: "Klienci w toku (aktywne transakcje) na dziś", t_coop: "Podpisane umowy „klient – agencja”",
  t_open: "Oferty przyjęte na umowę otwartą", t_excl: "Podpisane umowy na wyłączność",
  t_shows: "Odbyte prezentacje (plan — umówione, fakt — odbyte)", t_deposit: "Podpisane umowy zadatku / rezerwacji",
  t_pending: "Transakcje czekające na umowę główną", t_main: "Podpisane umowy główne (najem / sprzedaż)",
  t_closed: "Zamknięte transakcje (prowizja wpłynęła)", t_comm: "Kwota otrzymanej prowizji, PLN",
  t_expected: "Oczekiwana prowizja z rezerwacji, PLN", t_lost: "Odmowy / utraceni klienci",
  s_leads: "Leady", s_ads: "Publikacje", s_shows: "Prezentacje", s_comm: "Prowizja",
});

// ================================================================ метрики
// порядок строк как в таблице СВК — по нему же копируется «для таблицы»
const SV_ROWS = ["leads", "direct", "agents", "duty", "ads", "clients", "coop", "open", "excl", "shows", "deposit",
  "pending", "main", "closed", "comm", "expected", "lost"];
const SV_SUB = new Set(["direct", "agents", "duty"]);
const SV_SNAP = new Set(["clients", "pending", "expected"]);
const SV_MONEY = new Set(["comm", "expected"]);
// что входит в «план дня выполнен на …%»
const SV_GOALS = ["leads", "ads", "coop", "open", "excl", "shows", "deposit", "main", "closed"];
const RM = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

const SV = {
  mode: "photo", view: "day", date: "", data: null, key: "", range: null, rdata: null, rkey: "",
  report: "day", agent: "", busy: false, hit: {}, goal: {},
};
const MODES = ["photo", "svk", "clients", "market", "owners"];
const MODE_OPEN = { svk: () => svkOpen(true) };          // clients.js добавит свои экраны
try { const m = localStorage.getItem("hermea_mode"); SV.mode = MODES.includes(m) ? m : "photo"; } catch (e) {}
try { SV.view = ["day", "week", "month"].includes(localStorage.getItem("hermea_svk_view")) ? localStorage.getItem("hermea_svk_view") : "day"; } catch (e) {}

// ================================================================ даты
const pad = (n) => String(n).padStart(2, "0");
const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const parseIso = (s) => { const [y, m, d] = s.split("-").map(Number); return new Date(y, m - 1, d); };
const addDays = (s, n) => { const d = parseIso(s); d.setDate(d.getDate() + n); return iso(d); };
const todayIso = () => iso(new Date());
const monday = (s) => { const d = parseIso(s); const wd = (d.getDay() + 6) % 7; d.setDate(d.getDate() - wd); return iso(d); };
const dm = (s) => { const d = parseIso(s); return pad(d.getDate()) + "." + pad(d.getMonth() + 1); };
const wdShort = (s) => parseIso(s).toLocaleDateString(LOCALE[LANG], { weekday: "short" }).replace(".", "");
SV.date = todayIso();

function fmt(m, v) {
  if (v == null) return "";
  const s = String(Math.round(v * 100) / 100).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  return SV_MONEY.has(m) ? s + " zł" : s;
}

// ================================================================ анимации
function tween(el, to, m, dur) {
  const from = +(el.dataset.v || 0);
  el.dataset.v = to;
  if (RM || from === to || !el.isConnected) { el.textContent = fmt(m, to); return; }
  const t0 = performance.now(), d = dur || (SV_MONEY.has(m) ? 900 : 420);
  const step = (now) => {
    const k = Math.min(1, (now - t0) / d), e = 1 - Math.pow(1 - k, 3);
    const v = from + (to - from) * e;
    el.textContent = fmt(m, k < 1 ? (SV_MONEY.has(m) ? Math.round(v) : Math.round(v)) : to);
    if (k < 1 && +el.dataset.v === to) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
function bump(el) {
  if (RM || !el) return;
  el.classList.remove("bump"); void el.offsetWidth; el.classList.add("bump");
}
function floater(anchor, text, neg) {
  if (RM || !anchor) return;
  const r = anchor.getBoundingClientRect();
  const f = document.createElement("span");
  f.className = "float" + (neg ? " neg" : "");
  f.textContent = text;
  const Z = window.ZOOM || 1;
  f.style.left = (r.left + r.width / 2) / Z + "px";
  f.style.top = (r.top - 4) / Z + "px";
  document.body.appendChild(f);
  f.addEventListener("animationend", () => f.remove());
}
function ringSvg(r, w) {
  const c = 2 * Math.PI * r, s = (r + w) * 2;
  return `<svg class="ring" viewBox="0 0 ${s} ${s}" aria-hidden="true"><circle class="bg" cx="${r + w}" cy="${r + w}" r="${r}" fill="none" stroke-width="${w}"/>
    <circle class="fg" cx="${r + w}" cy="${r + w}" r="${r}" fill="none" stroke-width="${w}" stroke-dasharray="${c.toFixed(2)}" stroke-dashoffset="${c.toFixed(2)}"/></svg>`;
}
function setRing(svg, k) {
  if (!svg) return;
  const fg = svg.querySelector(".fg");
  const c = +fg.getAttribute("stroke-dasharray");
  fg.style.strokeDashoffset = String(c * (1 - Math.max(0, Math.min(1, k))));
}
const CHECK = '<svg class="check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>';
// смена экрана: плавный переход, если браузер умеет
function morph(fn) {
  if (RM || !document.startViewTransition) return fn();
  return document.startViewTransition(fn);
}
// бегунок под выбранной кнопкой сегмента
function slideSeg(seg) {
  if (!seg) return;
  let ind = seg.querySelector(".seg-ind");
  if (!ind) { ind = document.createElement("i"); ind.className = "seg-ind"; seg.prepend(ind); seg.classList.add("slide"); }
  const on = seg.querySelector('button[aria-pressed="true"]');
  if (!on) { ind.style.width = "0"; return; }
  ind.style.width = on.offsetWidth + "px";
  ind.style.transform = `translateX(${on.offsetLeft}px)`;
}

// ================================================================ режим: фото / СВК
function setMode(mode, quiet) {
  if (SV.mode === mode && !quiet) return;
  const go = () => {
    SV.mode = mode;
    for (const m of MODES) document.body.classList.toggle("mode-" + m, mode === m);
    document.body.classList.toggle("mode-aux", mode !== "photo");
    try { localStorage.setItem("hermea_mode", mode); } catch (e) {}
    drawModes();
    if (MODE_OPEN[mode]) MODE_OPEN[mode]();
  };
  quiet ? go() : morph(go);
}
function drawModes() {
  const nav = $("#modes");
  nav.querySelectorAll("button").forEach((b) => b.setAttribute("aria-current", String(b.dataset.mode === SV.mode)));
  const on = nav.querySelector('[aria-current="true"]'), ind = nav.querySelector(".ind");
  if (on && ind) { ind.style.width = on.offsetWidth + "px"; ind.style.transform = `translateX(${on.offsetLeft}px)`; }
  // напоминание: после 16:00 в будни, если день ещё пустой
  const now = new Date();
  const late = now.getDay() >= 1 && now.getDay() <= 5 && now.getHours() >= 16;
  $("#svkDot").hidden = !(late && S.st && S.st.svk_touched === false && SV.mode !== "svk");
}
$("#modes").addEventListener("click", (e) => {
  const b = e.target.closest("[data-mode]");
  if (b) setMode(b.dataset.mode);
});

// ================================================================ загрузка
async function svkOpen(fresh) {
  if (fresh) { SV.key = ""; SV.rkey = ""; }
  if (SV.view === "day") return loadDay(SV.date);
  return loadRange();
}
async function loadDay(date, dir) {
  try {
    const d = await api(`/api/svk?from=${date}&to=${date}`);
    SV.agent = d.agent; SV.defaults = d.defaults;
    SV.date = date;
    SV.data = d.days[0];
    drawDay(dir);
  } catch (e) { toast(e.message, true); }
}
function rangeOf() {
  if (SV.view === "week") { const a = monday(SV.date); return [a, addDays(a, 6)]; }
  const d = parseIso(SV.date);
  return [iso(new Date(d.getFullYear(), d.getMonth(), 1)), iso(new Date(d.getFullYear(), d.getMonth() + 1, 0))];
}
async function loadRange(dir) {
  const [a, b] = rangeOf();
  try {
    const d = await api(`/api/svk?from=${a}&to=${b}`);
    SV.agent = d.agent; SV.defaults = d.defaults;
    SV.rdata = d;
    drawRange(dir);
  } catch (e) { toast(e.message, true); }
}
async function op(body) {
  const r = await api("/api/svk", Object.assign({ date: SV.date }, body));
  if (r && r.date === SV.date) { SV.data = r; patchDay(); }
  if (S.st) S.st.svk_touched = SV.date === todayIso() ? !!(r && r.touched) : S.st.svk_touched;
  return r;
}

// ================================================================ день
function dayPct(dv) {
  const ks = SV_GOALS.filter((k) => (dv.plan[k] || 0) > 0);
  if (!ks.length) return null;
  return Math.round((ks.reduce((s, k) => s + Math.min(1, (dv.v[k] || 0) / dv.plan[k]), 0) / ks.length) * 100);
}
function titleOf(date) {
  const d = parseIso(date);
  return d.toLocaleDateString(LOCALE[LANG], { weekday: "long", day: "numeric", month: "long" });
}
function headHtml(title, sub, dial) {
  const c = 2 * Math.PI * 36;
  return `<div class="sv-head">
    <div class="sv-when">
      ${dial ? `<div class="sv-dial" id="svDial"><svg viewBox="0 0 84 84"><circle class="bg" cx="42" cy="42" r="36" fill="none" stroke-width="6"/>
        <circle class="fg" cx="42" cy="42" r="36" fill="none" stroke-width="6" stroke-dasharray="${c.toFixed(2)}" stroke-dashoffset="${c.toFixed(2)}"/></svg><b id="svDialN">–</b></div>` : ""}
      <div class="sv-title-box" id="svTitleBox"><h1 class="sv-title">${esc(title)}</h1><p class="sv-sub" id="svSub">${sub}</p></div>
      <div class="sv-nav">
        <button class="sv-arrow" type="button" data-nav="-1" aria-label="‹">${ARROW_L}</button>
        <button class="sv-arrow" type="button" data-nav="1" aria-label="›">${ARROW_R}</button>
      </div>
    </div>
    <div class="sv-tools">
      <div class="seg" id="svView">
        <button type="button" data-v="day" aria-pressed="${SV.view === "day"}">${t("sv_day")}</button>
        <button type="button" data-v="week" aria-pressed="${SV.view === "week"}">${t("sv_week")}</button>
        <button type="button" data-v="month" aria-pressed="${SV.view === "month"}">${t("sv_month")}</button>
      </div>
      <button class="btn-primary" type="button" id="svReport">${ICON_DOC} ${t("sv_report")}</button>
    </div></div>`;
}
const ARROW_L = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 5-7 7 7 7"/></svg>';
const ARROW_R = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 5 7 7-7 7"/></svg>';
const ICON_DOC = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round"><path d="M7 3.5h7l4 4V20a.5.5 0 0 1-.5.5h-10A.5.5 0 0 1 7 20z"/><path d="M14 3.5V8h4M10 12.5h5M10 16h5"/></svg>';
const PLUS = '<span class="plus"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></span>';

function daySub(dv) {
  const parts = [];
  const td = todayIso();
  if (dv.date === td) parts.push(`<span class="today-pill">${t("sv_today")}</span>`);
  else if (dv.date === addDays(td, -1)) parts.push(`<span>${t("sv_yesterday")}</span>`);
  const wd = parseIso(dv.date).getDay();
  if (wd === 0 || wd === 6) parts.push(`<span>${t("sv_weekend")}</span>`);
  const p = dayPct(dv);
  if (p != null) parts.push(`<span>${esc(t("sv_plan_done", { p }))}</span>`);
  if (SV.agent) parts.push(`<span>${esc(SV.agent)}</span>`);
  return parts.join("");
}
function ofHtml(m) { return `<span class="of" data-of="${m}"></span>`; }
function stepper(m, money) {
  return `<div class="stepper${money ? " money" : ""}" data-m="${m}">
    <button type="button" data-step="-1" aria-label="−1">−</button><output data-n="${m}" data-v="0">0</output>
    <button type="button" class="add" data-step="1" aria-label="+1">+</button></div>`;
}
function row(m, label, sub, ctrl, noOf) {
  return `<div class="sv-row" data-row="${m}"><div class="lbl">${esc(label)} ${noOf ? "" : ofHtml(m)}${sub ? `<small>${esc(sub)}</small>` : ""}</div>${ctrl || stepper(m)}</div>`;
}

function drawDay(dir) {
  const dv = SV.data;
  const key = "day:" + dv.date + ":" + LANG;
  const box = $("#svk");
  if (SV.key === key) return patchDay();
  const first = !SV.key.startsWith("day:");
  SV.key = key;
  SV.hit = {}; SV.goal = {};
  let i = 0;
  const r = () => `rise" style="--i:${i++}`;
  box.innerHTML = `<div class="sv-wrap">${headHtml(titleOf(dv.date), daySub(dv), true)}
    <div class="sv-day">
      <div class="sv-cols">
        <div class="sv-hero">
          <section class="sv-card c-leads ${r()}" data-card="leads">
            <h3>${t("sv_leads")} ${CHECK}</h3>
            <div class="sv-big">${ringSvg(27, 5)}<div><span class="num" data-n="leads" data-v="0">0</span>${ofHtml("leads")}</div></div>
            <div class="chips">
              ${["direct", "agents", "duty"].map((m) => `<div class="chip" data-m="${m}">
                <button class="chip-add" type="button" data-add="${m}">${PLUS}<span>${t("sv_" + m)}</span></button>
                <output data-n="${m}" data-v="0">0</output>
                <button class="chip-sub" type="button" data-sub="${m}" aria-label="−1">−</button></div>`).join("")}
            </div>
          </section>
          <section class="sv-card ${r()}" data-card="ads">
            <h3>${t("sv_ads")} ${CHECK}</h3>
            <div class="sv-big">${ringSvg(27, 5)}<div><span class="num" data-n="ads" data-v="0">0</span>${ofHtml("ads")}</div></div>
            <div class="chip-row">
              <div class="chip" data-m="ads"><button class="chip-add" type="button" data-add="ads">+1</button>
                <button class="chip-sub" type="button" data-sub="ads" aria-label="−1">−</button></div>
              <div class="chip"><button class="chip-add" type="button" data-add="ads" data-d="5">+5</button></div>
            </div>
            <div class="auto-hint" id="svAuto" hidden></div>
            <p class="hint" style="font-size:12.5px;margin:10px 0 0">${t("sv_ads_sub")}</p>
          </section>
          <section class="sv-card ${r()}" data-card="shows">
            <h3>${t("sv_shows")} ${CHECK}</h3>
            <div class="sv-big">${ringSvg(27, 5)}<div><span class="num" data-n="shows" data-v="0">0</span>${ofHtml("shows")}</div></div>
            <div class="sv-rows">
              ${row("shows_plan", t("sv_shows_plan"), "", "", true)}
              ${row("shows", t("sv_shows_fact"), "", "", true)}
            </div>
          </section>
        </div>
        <div class="sv-pair">
          <section class="sv-card ${r()}">
            <h3>${t("sv_docs")}</h3>
            <div class="sv-rows">
              ${row("coop", t("sv_coop"), "")}
              ${row("open", t("sv_open"), t("sv_open_sub"))}
              ${row("excl", t("sv_excl"), "")}
              ${row("deposit", t("sv_deposit"), "")}
              ${row("main", t("sv_main"), t("sv_main_sub"))}
            </div>
          </section>
          <section class="sv-card ${r()}">
            <h3>${t("sv_deals")}</h3>
            <div class="sv-rows">
              ${row("clients", t("sv_clients"), t("sv_clients_sub"))}
              ${row("pending", t("sv_pending"), "")}
              ${row("closed", t("sv_closed"), t("sv_closed_sub"))}
              ${row("comm", t("sv_comm"), "", `<div><span class="money-val" data-n="comm" data-v="0">0 zł</span><button class="btn-add" type="button" data-amount="comm">${t("sv_add_sum")}</button></div>`)}
              ${row("expected", t("sv_expected"), t("sv_expected_sub"), stepper("expected", true).replace(/data-step="-1"[^>]*>−/, 'data-step="-1" hidden>−').replace(/class="add" data-step="1"[^>]*>\+/, 'class="add" data-step="1" hidden>+'))}
            </div>
          </section>
        </div>
        <section class="sv-card ${r()}" data-card="lost">
          <h3>${t("sv_lost")}</h3>
          <div class="sv-lost"><span class="num" data-n="lost" data-v="0">0</span>
            <button class="btn-add" type="button" data-reason="lost">${PLUS.replace("plus", "plus sm")} ${t("sv_lost_btn")}</button>
            <button class="text-btn" type="button" data-sub="lost">−1</button></div>
        </section>
      </div>
      <aside class="sv-log ${r()}"><h3><span>${t("sv_log")}</span><span id="svLogN"></span></h3><div class="scroll" id="svLog"></div></aside>
    </div></div>`;
  if (!first && dir) $("#svTitleBox").classList.add(dir < 0 ? "slide-l" : "slide-r");
  if (!first) box.querySelectorAll(".rise").forEach((el) => el.classList.remove("rise"));
  slideSeg($("#svView"));
  // «вчера N» для показателей «на сегодня»
  SV.logIds = null;
  patchDay(true);
  box.scrollTo({ top: 0 });
}

function patchDay(initial) {
  const dv = SV.data, box = $("#svk");
  if (!dv || !SV.key.startsWith("day:")) return;
  const v = dv.v, plan = dv.plan;
  box.querySelectorAll("[data-n]").forEach((el) => {
    const m = el.dataset.n, val = v[m] || 0;
    if (el.tagName === "INPUT") return;
    if (+el.dataset.v !== val || initial) tween(el, val, m, initial ? 700 : 0);
  });
  box.querySelectorAll("[data-of]").forEach((el) => {
    const m = el.dataset.of;
    let txt = "";
    if (SV_SNAP.has(m)) txt = (plan[m] || 0) !== (v[m] || 0) || plan[m] ? t("sv_was", { n: fmt(m, plan[m] || 0) }) : "";
    else if (m === "shows") txt = plan.shows ? t("sv_of", { n: plan.shows }) : "";
    else if (m === "shows_plan" || m === "comm") txt = "";
    else if (!SV_SUB.has(m)) txt = plan[m] != null ? t("sv_of", { n: plan[m] }) : "";
    const can = !SV_SNAP.has(m) && m !== "shows" && m !== "shows_plan" && m !== "comm";
    el.innerHTML = txt ? (can ? `<button type="button" data-plan="${m}">${esc(txt)}</button>` : esc(txt))
      : (can ? `<button type="button" data-plan="${m}">${esc(t("sv_of", { n: 0 }))}</button>` : "");
  });
  // карточки с кольцами
  box.querySelectorAll("[data-card]").forEach((card) => {
    const m = card.dataset.card;
    if (m === "lost") return;
    const p = plan[m] || 0, f = v[m] || 0;
    setRing(card.querySelector(".ring"), p ? f / p : (f ? 1 : 0));
    const hit = p > 0 && f >= p;
    card.classList.toggle("hit", hit);
    if (hit && SV.hit[m] === false && !initial) {
      card.classList.remove("hit-now"); void card.offsetWidth; card.classList.add("hit-now");
    }
    SV.hit[m] = hit;
  });
  box.querySelectorAll("[data-row]").forEach((r) => {
    const m = r.dataset.row;
    r.classList.toggle("hit", !SV_SNAP.has(m) && m !== "comm" && m !== "shows_plan" && (plan[m] || 0) > 0 && (v[m] || 0) >= plan[m]);
  });
  // день целиком
  const pct = dayPct(dv);
  const dial = $("#svDial");
  if (dial) {
    const fg = dial.querySelector(".fg"), c = +fg.getAttribute("stroke-dasharray");
    fg.style.strokeDashoffset = String(c * (1 - Math.min(1, (pct || 0) / 100)));
    const n = $("#svDialN");
    n.innerHTML = pct == null ? "–" : `${pct}<small>%</small>`;
    const full = pct != null && pct >= 100;
    if (full && SV.goal[dv.date] === false && !initial) { toast(t("sv_goal")); dial.classList.remove("full"); void dial.offsetWidth; }
    dial.classList.toggle("full", full);
    SV.goal[dv.date] = full;
  }
  $("#svSub").innerHTML = daySub(dv);
  patchAuto();
  if (!$("#svLog .note-in")) drawLog(initial);
}
// подсказка: обработанные в программе квартиры — это материал для публикаций
function patchAuto() {
  const dv = SV.data, v = dv.v;
  const auto = $("#svAuto");
  const nflats = (S.today && S.today.flats) || 0;
  if (auto) {
    auto.hidden = !(dv.date === todayIso() && nflats > 0 && (v.ads || 0) < nflats);
    if (!auto.hidden) {
      const n = nflats - (v.ads || 0);
      auto.innerHTML = `<span>${esc(t("sv_auto", { n: nflats, flats: plural(nflats, "flats") }))}</span>
        <button type="button" data-add="ads" data-d="${n}">${esc(t("sv_auto_add", { n, pubs: plural(n, "pubs") }))}</button>`;
    }
  }
}

function drawLog(initial) {
  const dv = SV.data, list = $("#svLog");
  if (!list) return;
  const log = (dv.log || []).slice().reverse();
  $("#svLogN").textContent = log.length ? String(log.length) : "";
  const ids = log.map((e) => e.id);
  const prev = SV.logIds;
  SV.logIds = new Set(ids);
  if (!log.length) { list.innerHTML = `<p class="jempty">${t("sv_log_empty")}</p>`; return; }
  const have = new Map([...list.querySelectorAll(".jrow")].map((r) => [r.dataset.id, r]));
  const frag = document.createDocumentFragment();
  for (const e of log) {
    let r = have.get(e.id);
    const what = `<span>${esc(e.fix ? t("sv_fixed") + ": " + t("j_" + e.m).toLowerCase() : t("j_" + e.m))}`
      + (e.m === "comm" ? ` <i>${esc(fmt("comm", e.d))}</i>` : (e.d !== 1 ? ` <i>${e.d > 0 ? "+" : ""}${esc(String(e.d))}</i>` : "")) + "</span>"
      + (e.note ? "" : `<button class="note-btn" type="button" data-note="${e.id}">${t("sv_note_add")}</button>`);
    const html = `<time>${hm(new Date(e.ts * 1000))}</time>
      <div><div class="what">${what}</div>${e.note ? `<div class="note">${esc(e.note)}</div>` : ""}</div>
      <button class="x" type="button" data-undo="${e.id}" title="${esc(t("sv_undo"))}" aria-label="${esc(t("sv_undo"))}">×</button>`;
    if (!r) {
      r = document.createElement("div");
      r.className = "jrow";
      r.dataset.id = e.id;
      if (prev && !initial) r.classList.add("in");
    }
    if (r.dataset.h !== html && !r.querySelector(".note-in")) { r.innerHTML = html; r.dataset.h = html; }
    frag.appendChild(r);
  }
  list.innerHTML = "";
  list.appendChild(frag);
}

// ================================================================ действия на экране дня
$("#svk").addEventListener("click", async (e) => {
  const el = e.target.closest("button");
  if (!el || el.disabled) return;
  const ds = el.dataset;
  if (ds.nav) return navigate(+ds.nav);
  if (ds.v) {
    if (ds.v === SV.view) return;
    SV.view = ds.v;
    try { localStorage.setItem("hermea_svk_view", SV.view); } catch (err) {}
    $("#svView").querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.v === SV.view)));
    slideSeg($("#svView"));
    SV.key = ""; SV.rkey = "";
    return morph(() => svkOpen());
  }
  if (el.id === "svReport") return openReport();
  if (ds.jump) { SV.date = ds.jump; SV.view = "day"; try { localStorage.setItem("hermea_svk_view", "day"); } catch (err) {} SV.key = ""; return morph(() => loadDay(SV.date)); }
  if (ds.add) {
    const n = +(ds.d || 1);
    floater(el, "+" + n);
    bump($(`#svk .num[data-n="${ds.add === "direct" || ds.add === "agents" || ds.add === "duty" ? "leads" : ds.add}"]`));
    try { await op({ op: "add", m: ds.add, d: n }); } catch (err) { toast(err.message, true); }
    return;
  }
  if (ds.sub) {
    if (!(SV.data.v[ds.sub] > 0)) return;
    floater(el, "−1", true);
    try { await op({ op: "add", m: ds.sub, d: -1 }); } catch (err) { toast(err.message, true); }
    return;
  }
  if (ds.step) {
    const box = el.closest("[data-m]"), m = box.dataset.m, d = +ds.step;
    const cur = SV.data.v[m] || 0;
    if (d < 0 && cur <= 0) return;
    if (m === "closed" && d > 0) return askPop(el, "closed");
    floater(el, d > 0 ? "+1" : "−1", d < 0);
    bump(box.querySelector("output"));
    if (m === "shows" || m === "shows_plan") bump($('#svk .num[data-n="shows"]'));
    try {
      if (SV_SNAP.has(m)) await op({ op: "set", m, value: Math.max(0, cur + d) });
      else await op({ op: "add", m, d });
    } catch (err) { toast(err.message, true); }
    return;
  }
  if (ds.amount) return askPop(el, "comm");
  if (ds.reason) return askPop(el, "lost");
  if (ds.plan) return askPop(el, "plan", ds.plan);
  if (ds.undo) {
    const r = el.closest(".jrow");
    if (r && !RM) { r.classList.add("out"); await new Promise((ok) => setTimeout(ok, 220)); }
    try { await op({ op: "undo", id: ds.undo }); } catch (err) { toast(err.message, true); }
    return;
  }
  if (ds.note) return editNote(el, ds.note);
});
// клик по числу — ввести руками
$("#svk").addEventListener("click", (e) => {
  const out = e.target.closest(".stepper output");
  if (!out) return;
  const box = out.closest("[data-m]"), m = box.dataset.m;
  const inp = document.createElement("input");
  inp.type = "number"; inp.min = "0"; inp.step = SV_MONEY.has(m) ? "50" : "1"; inp.value = SV.data.v[m] || 0;
  out.replaceWith(inp);
  inp.focus(); inp.select();
  let done = false;
  const finish = async (save) => {
    if (done) return; done = true;
    const val = Math.max(0, Number(inp.value) || 0);
    inp.replaceWith(out);
    if (!save || val === (SV.data.v[m] || 0)) return;
    try { await op(SV_SNAP.has(m) ? { op: "set", m, value: val } : { op: "fix", m, value: val }); bump(out); } catch (err) { toast(err.message, true); }
  };
  inp.addEventListener("keydown", (k) => { if (k.key === "Enter") finish(true); if (k.key === "Escape") finish(false); });
  inp.addEventListener("blur", () => finish(true));
});

async function navigate(d) {
  if (SV.view === "day") {
    const nd = addDays(SV.date, d);
    SV.key = "day:pending";
    return loadDay(nd, d);
  }
  if (SV.view === "week") SV.date = addDays(monday(SV.date), d * 7);
  else { const x = parseIso(SV.date); SV.date = iso(new Date(x.getFullYear(), x.getMonth() + d, 1)); }
  SV.rkey = "";
  return loadRange(d);
}

function editNote(btn, id) {
  const wrap = btn.closest(".what").parentElement;
  const inp = document.createElement("input");
  inp.className = "note-in"; inp.type = "text"; inp.placeholder = t("p_note"); inp.maxLength = 200;
  btn.remove();
  wrap.appendChild(inp);
  inp.focus();
  let done = false;
  const fin = async (save) => {
    if (done) return; done = true;
    const v = inp.value.trim();
    inp.remove();
    const r = wrap.closest(".jrow"); if (r) r.dataset.h = "";
    if (save && v) { try { await op({ op: "note", id, note: v }); } catch (e) { toast(e.message, true); } }
    else drawLog();
  };
  inp.addEventListener("keydown", (k) => { if (k.key === "Enter") fin(true); if (k.key === "Escape") fin(false); });
  inp.addEventListener("blur", () => fin(true));
}

// маленькое окошко: сумма комиссии, причина отказа, план
function closePop() { const p = $("#svPop"); if (p) p.remove(); }
function askPop(anchor, kind, metric) {
  closePop();
  const p = document.createElement("form");
  p.className = "sv-pop"; p.id = "svPop"; p.autocomplete = "off";
  let body = "";
  if (kind === "closed") body = `<label for="svPopIn">${t("p_comm")}</label><input id="svPopIn" type="number" min="0" step="50" placeholder="0">`;
  if (kind === "comm") body = `<label for="svPopIn">${t("p_amount")}</label><input id="svPopIn" type="number" min="0" step="50" required>`;
  if (kind === "lost") body = `<label for="svPopIn">${t("p_reason")}</label><input id="svPopIn" type="text" maxlength="200" placeholder="${esc(t("p_reason_ph"))}">`;
  if (kind === "plan") {
    body = `<label for="svPopIn">${t("p_plan")}</label><input id="svPopIn" type="number" min="0" step="1" value="${SV.data.plan[metric] || 0}">
      <label class="chk"><input type="checkbox" id="svPopDef"> ${t("p_plan_def")}</label>`;
  }
  p.innerHTML = body + `<div class="row-btns"><button class="btn-primary sm" type="submit">${t("p_save")}</button>
    <button class="btn" type="button" data-close="1">${t("p_cancel")}</button></div>`;
  document.body.appendChild(p);
  const r = anchor.getBoundingClientRect(), Z = window.ZOOM || 1;
  const pw = p.offsetWidth * Z, ph = p.offsetHeight * Z;           // на экране, с учётом масштаба
  const x = Math.min(window.innerWidth - pw - 12, Math.max(12, r.left));
  const below = r.bottom + 8 + ph < window.innerHeight;
  p.style.left = x / Z + "px";
  p.style.top = (below ? r.bottom + 8 : Math.max(12, r.top - ph - 8)) / Z + "px";
  const inp = $("#svPopIn");
  inp.focus(); if (inp.select) inp.select();
  p.querySelector("[data-close]").onclick = closePop;
  p.onsubmit = async (e) => {
    e.preventDefault();
    const val = inp.value.trim();
    const asDefault = !!(p.querySelector("#svPopDef") && p.querySelector("#svPopDef").checked);
    closePop();
    try {
      if (kind === "closed") {
        floater(anchor, "+1"); bump(anchor.closest("[data-m]").querySelector("output"));
        await op({ op: "add", m: "closed", d: 1 });
        if (Number(val) > 0) await op({ op: "add", m: "comm", d: Number(val) });
      } else if (kind === "comm") {
        if (Number(val) > 0) { floater(anchor, "+" + fmt("comm", Number(val))); await op({ op: "add", m: "comm", d: Number(val) }); }
      } else if (kind === "lost") {
        floater(anchor, "+1", true); bump($('#svk .num[data-n="lost"]'));
        await op({ op: "add", m: "lost", d: 1, note: val });
      } else if (kind === "plan") {
        await op({ op: "plan", m: metric, value: Number(val) || 0 });
        if (asDefault) {
          await api("/api/svk", { op: "defaults", values: { [metric]: Number(val) || 0 } });
        }
        toast(t("p_plan_saved"));
      }
    } catch (err) { toast(err.message, true); }
  };
}
document.addEventListener("mousedown", (e) => { const p = $("#svPop"); if (p && !p.contains(e.target)) closePop(); });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") { closePop(); closeReport(); }
  // быстрые клавиши на экране дня: 1/2/3 — лид, П — публикация
  if (SV.mode !== "svk" || SV.view !== "day" || e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.target.closest("input, textarea") || $("#svPop") || !$("#svDrawer").hidden) return;
  const map = { "1": "direct", "2": "agents", "3": "duty" };
  if (map[e.key]) { e.preventDefault(); const b = $(`#svk .chip-add[data-add="${map[e.key]}"]`); if (b) b.click(); }
  if (e.key === "ArrowLeft") navigate(-1);
  if (e.key === "ArrowRight") navigate(1);
});

// ================================================================ неделя / месяц
function aggregate(days, m) {
  const real = days.filter((d) => d.date <= todayIso());
  if (SV_SNAP.has(m)) {
    const last = real.length ? real[real.length - 1] : days[0];
    return { p: last ? last.plan[m] || 0 : 0, f: last ? last.v[m] || 0 : 0 };
  }
  let p = 0, f = 0;
  for (const d of days) { p += m === "shows" ? (d.v.shows_plan || 0) : (d.plan[m] || 0); f += d.v[m] || 0; }
  return { p, f };
}
function pctCell(p, f, m, over) {
  if (!p) return `<td class="pct na">${f ? "—" : ""}</td>`;
  const k = Math.round((f / p) * 100);
  const cls = m === "lost" ? (k > 100 ? "low" : "") : (k >= 100 ? "ok" : over && k < 50 ? "low" : "");
  return `<td class="pct ${cls}">${k}%<span class="bar"><i data-w="${Math.min(100, k)}"></i></span></td>`;
}
function cell(v, cls, m) { return `<td class="${cls}${v ? "" : " zero"}">${esc(fmt(m, v || 0))}</td>`; }

function drawRange(dir) {
  const d = SV.rdata, days = d.days;
  const [a, b] = rangeOf();
  const key = SV.view + ":" + a + ":" + LANG + ":" + JSON.stringify(days.map((x) => [x.v, x.plan]));
  if (SV.rkey === key) return;
  const first = !SV.key.startsWith("range:");
  SV.key = "range:" + SV.view + a;
  SV.rkey = key;
  const td = todayIso();
  let cols;           // [{label, days, date?}]
  if (SV.view === "week") {
    cols = days.filter((x) => { const wd = parseIso(x.date).getDay(); return (wd >= 1 && wd <= 5) || x.touched; })
      .map((x) => ({ label: `${wdShort(x.date)} ${dm(x.date)}`, days: [x], date: x.date }));
  } else {
    cols = [];
    let cur = null;
    for (const x of days) {
      const wd = parseIso(x.date).getDay();
      if (!cur || wd === 1) { cur = { days: [] }; cols.push(cur); }
      cur.days.push(x);
    }
    // недели без будней и недели до начала учёта в программе не показываем
    cols = cols.filter((c) => c.days.some((x) => {
      const wd = parseIso(x.date).getDay();
      return x.touched || (wd >= 1 && wd <= 5 && x.date >= (d.since || ""));
    }));
    cols.forEach((c, i) => {
      const work = c.days.filter((x) => { const wd = parseIso(x.date).getDay(); return wd >= 1 && wd <= 5; });
      const f = (work[0] || c.days[0]).date, l = (work[work.length - 1] || c.days[c.days.length - 1]).date;
      c.label = `${t("t_week_n", { n: i + 1 })} · ${dm(f)}–${dm(l)}`;
      c.week = f;
    });
  }
  const title = SV.view === "week"
    ? t("r_week_of", { a: dm(a), b: dm(addDays(a, 4)) })
    : parseIso(a).toLocaleDateString(LOCALE[LANG], { month: "long", year: "numeric" });
  const tot = (m) => aggregate(days, m);
  // крупные цифры сверху + столбики по дням
  const perDay = days.filter((x) => { const wd = parseIso(x.date).getDay(); return (wd >= 1 && wd <= 5) || x.touched; });
  const spark = (m) => {
    const mx = Math.max(1, ...perDay.map((x) => x.v[m] || 0));
    return `<div class="spark">${perDay.map((x, i) => `<i class="${x.v[m] ? "" : "zero"}" style="--i:${i};height:${Math.max(8, ((x.v[m] || 0) / mx) * 100)}%" title="${dm(x.date)}: ${x.v[m] || 0}"></i>`).join("")}</div>`;
  };
  const stat = (m, lbl, i) => {
    const x = tot(m);
    return `<div class="sv-stat rise" style="--i:${i}"><dt>${t(lbl)}</dt><dd><span data-tw="${x.f}" data-m="${m}">0</span>${x.p && !SV_MONEY.has(m) ? `<small>${esc(t("sv_of", { n: x.p }))}</small>` : ""}</dd>${spark(m)}</div>`;
  };
  let head1 = `<tr><th class="rl" rowspan="2">${t("t_metric")}</th>`;
  let head2 = "<tr>";
  for (const c of cols) {
    const isToday = c.date === td;
    const jump = c.date || c.week;
    head1 += `<th class="day${isToday ? " today" : ""}" colspan="2" data-jump="${jump}" title="${esc(c.label)}">${esc(c.label)}</th>`;
    head2 += `<th class="first-of">${t("t_plan")}</th><th>${t("t_fact")}</th>`;
  }
  head1 += `<th class="tot tot-first" colspan="3">${t(SV.view === "week" ? "t_total_w" : "t_total_m")}</th></tr>`;
  head2 += `<th class="tot-first">${t("t_plan")}</th><th>${t("t_fact")}</th><th>%</th></tr>`;
  const rows = SV_ROWS.map((m) => {
    let h = `<tr class="${SV_SUB.has(m) ? "sub" : ""}"><td class="rl">${esc(t("t_" + m))}</td>`;
    for (const c of cols) {
      const x = aggregate(c.days, m);
      const tc = c.date === td ? " today-col" : "";
      const future = c.days.every((y) => y.date > td);
      h += cell(future && SV_SNAP.has(m) ? 0 : x.p, "plan first-of" + tc, m) + cell(x.f, "fact" + tc + (future ? " future" : ""), m);
    }
    const x = tot(m);
    h += cell(x.p, "plan tot-first", m) + cell(x.f, "fact", m) + pctCell(x.p, x.f, m, b < td);
    return h + "</tr>";
  }).join("");
  $("#svk").innerHTML = `<div class="sv-wrap">${headHtml(title, SV.agent ? `<span>${esc(SV.agent)}</span>` : "", false)}
    <div class="sv-summary">${stat("leads", "s_leads", 0)}${stat("ads", "s_ads", 1)}${stat("shows", "s_shows", 2)}${stat("comm", "s_comm", 3)}</div>
    <div class="sv-table-wrap rise" style="--i:4"><table class="sv-table"><thead>${head1}${head2}</thead><tbody>${rows}</tbody></table></div></div>`;
  slideSeg($("#svView"));
  if (!first && dir) $("#svTitleBox").classList.add(dir < 0 ? "slide-l" : "slide-r");
  $("#svk").querySelectorAll("[data-tw]").forEach((el) => { el.dataset.v = 0; tween(el, +el.dataset.tw, el.dataset.m, 800); });
  requestAnimationFrame(() => requestAnimationFrame(() => {
    $("#svk").querySelectorAll(".bar i[data-w]").forEach((i) => { i.style.width = i.dataset.w + "%"; });
  }));
}
$("#svk").addEventListener("click", (e) => {
  const th = e.target.closest("th[data-jump]");
  if (!th) return;
  SV.date = th.dataset.jump; SV.view = "day";
  try { localStorage.setItem("hermea_svk_view", "day"); } catch (err) {}
  SV.key = "";
  morph(() => loadDay(SV.date));
});

// ================================================================ отчёт
async function openReport() {
  const dr = $("#svDrawer"), bg = $("#svDrawerBg");
  dr.hidden = false; bg.hidden = false;
  $("#svName").value = SV.agent || "";
  requestAnimationFrame(() => { dr.classList.add("open"); bg.classList.add("open"); slideSeg($("#svRPeriod")); });
  await drawReport();
}
function closeReport() {
  const dr = $("#svDrawer"), bg = $("#svDrawerBg");
  if (!dr || dr.hidden) return;
  dr.classList.remove("open"); bg.classList.remove("open");
  setTimeout(() => { if (!dr.classList.contains("open")) { dr.hidden = true; bg.hidden = true; } }, RM ? 0 : 420);
}
async function reportData() {
  if (SV.report === "day") {
    const d = await api(`/api/svk?from=${SV.date}&to=${SV.date}`);
    return { days: d.days, from: SV.date, to: SV.date };
  }
  const a = monday(SV.date), b = addDays(a, 6);
  const d = await api(`/api/svk?from=${a}&to=${b}`);
  return { days: d.days, from: a, to: addDays(a, 4) };
}
function reportText(rd) {
  const days = rd.days;
  const A = (m) => aggregate(days, m);
  const lines = [];
  const head = rd.from === rd.to
    ? titleOf(rd.from)
    : t("r_week_of", { a: dm(rd.from), b: dm(rd.to) });
  lines.push(`СВК${SV.agent ? " · " + SV.agent : ""} · ${head}`);
  lines.push("");
  const L1 = (key, m, always) => {
    const x = A(m);
    if (!always && !x.f && !x.p) return;
    const val = SV_SNAP.has(m) || SV_MONEY.has(m) || !x.p ? fmt(m, x.f) : `${fmt(m, x.f)} ${t("sv_of", { n: fmt(m, x.p) })}`;
    lines.push(`${t(key)}: ${val}`);
  };
  L1("r_leads", "leads", true);
  for (const m of ["direct", "agents", "duty"]) { const x = A(m); if (x.f) lines.push(`   ${t("r_" + m)}: ${x.f}`); }
  const notes = (m) => days.flatMap((d) => (d.log || []).filter((e) => e.m === m && e.note).map((e) => e.note));
  const ln = [...notes("direct"), ...notes("agents"), ...notes("duty")];
  if (ln.length && rd.from === rd.to) ln.forEach((n) => lines.push(`   · ${n}`));
  L1("r_ads", "ads", true);
  L1("r_clients", "clients", true);
  L1("r_coop", "coop"); L1("r_open", "open"); L1("r_excl", "excl");
  const sh = A("shows");
  if (sh.f || sh.p) lines.push(`${t("r_shows")}: ${t("r_shows_of", { f: sh.f, p: sh.p })}`);
  L1("r_deposit", "deposit"); L1("r_pending", "pending"); L1("r_main", "main"); L1("r_closed", "closed");
  L1("r_comm", "comm"); L1("r_expected", "expected");
  const lo = A("lost");
  if (lo.f) {
    lines.push(`${t("r_lost")}: ${lo.f}`);
    notes("lost").forEach((n) => lines.push(`   · ${n}`));
  }
  const ks = SV_GOALS.filter((k) => A(k).p > 0);
  if (ks.length) {
    const p = Math.round((ks.reduce((s, k) => { const x = A(k); return s + Math.min(1, x.f / x.p); }, 0) / ks.length) * 100);
    lines.push("");
    lines.push(t("r_total", { p }));
  }
  return lines.join("\n");
}
function reportTsv(rd) {
  return SV_ROWS.map((m) => { const x = aggregate(rd.days, m); return `${x.p}\t${x.f}`; }).join("\n");
}
async function drawReport() {
  try {
    SV.rd = await reportData();
    const txt = reportText(SV.rd);
    $("#svRText").textContent = txt;
    $("#svRSub").textContent = SV.report === "day" ? titleOf(SV.date) : t("r_week_of", { a: dm(SV.rd.from), b: dm(SV.rd.to) });
  } catch (e) { toast(e.message, true); }
}
async function copyText(s) {
  try { await navigator.clipboard.writeText(s); }
  catch (e) {
    const ta = document.createElement("textarea"); ta.value = s; document.body.appendChild(ta); ta.select();
    document.execCommand("copy"); ta.remove();
  }
}
function buildDrawer() {
  const bg = document.createElement("div");
  bg.className = "sv-drawer-bg"; bg.id = "svDrawerBg"; bg.hidden = true;
  const dr = document.createElement("aside");
  dr.className = "sv-drawer"; dr.id = "svDrawer"; dr.hidden = true; dr.setAttribute("role", "dialog");
  dr.innerHTML = `<header><div><h2 data-i18n="r_title"></h2><p id="svRSub"></p></div>
      <button class="icon-x" type="button" id="svRClose" aria-label="×">×</button></header>
    <div class="inner">
      <div class="seg" id="svRPeriod">
        <button type="button" data-rp="day" aria-pressed="true" data-i18n="r_day"></button>
        <button type="button" data-rp="week" aria-pressed="false" data-i18n="r_week"></button>
      </div>
      <pre class="sv-report" id="svRText"></pre>
      <div class="row-btns">
        <button class="btn-primary" type="button" id="svRCopy" data-i18n="r_copy"></button>
        <button class="btn" type="button" id="svRTsv" data-i18n="r_copy_tsv"></button>
      </div>
      <p class="sv-howto" id="svHowto"></p>
      <label class="sv-name"><span data-i18n="r_name"></span><input id="svName" type="text" maxlength="60" data-i18n-ph="r_name_ph"></label>
    </div>`;
  document.body.append(bg, dr);
  bg.onclick = closeReport;
  $("#svRClose").onclick = closeReport;
  $("#svRPeriod").onclick = (e) => {
    const b = e.target.closest("[data-rp]");
    if (!b) return;
    SV.report = b.dataset.rp;
    $("#svRPeriod").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    slideSeg($("#svRPeriod"));
    drawReport();
  };
  $("#svRCopy").onclick = async () => { await copyText($("#svRText").textContent); toast(t("r_copied")); };
  $("#svRTsv").onclick = async () => { if (SV.rd) { await copyText(reportTsv(SV.rd)); toast(t("r_tsv_copied")); } };
  $("#svName").addEventListener("change", async (e) => {
    SV.agent = e.target.value.trim();
    try { await api("/api/svk", { op: "agent", name: SV.agent }); } catch (err) {}
    drawReport();
    if (SV.data && SV.key.startsWith("day:")) $("#svSub").innerHTML = daySub(SV.data);
  });
}
buildDrawer();

// ================================================================ связка с основным окном
const _applyStatic = applyStatic;
applyStatic = function () {               // eslint-disable-line no-func-assign
  _applyStatic();
  const h = $("#svHowto"); if (h) h.innerHTML = t("r_howto");
  requestAnimationFrame(drawModes);
};
function svkTick() {
  drawModes();
  if (SV.mode !== "svk") return;
  if (SV.key && !SV.key.endsWith(LANG) && SV.key.startsWith("day:")) { SV.key = ""; drawDay(); }
  // день сменился, а экран открыт на «сегодня»
  if (SV.view === "day" && SV.data && SV.lastToday && SV.lastToday !== todayIso() && SV.date === SV.lastToday) loadDay(todayIso());
  SV.lastToday = todayIso();
  if (SV.view === "day" && SV.data && SV.key.startsWith("day:")) patchAuto();
}
const _renderTop = renderTop;
renderTop = function () { _renderTop(); svkTick(); };   // eslint-disable-line no-func-assign
window.addEventListener("resize", () => { drawModes(); slideSeg($("#svView")); slideSeg($("#svRPeriod")); });
applyStatic();
SV.lastToday = todayIso();
setMode(SV.mode === "svk" || SV.mode === "photo" ? SV.mode : "photo", true);
if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { drawModes(); slideSeg($("#svView")); });
