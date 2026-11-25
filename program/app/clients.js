"use strict";
/* Клиенты (карточка, договор, сообщения, калькулятор) и Рынок. Подключается после svk.js. */

// ================================================================ тексты
const CL = {
ru: {
  m_clients: "Клиенты", m_market: "Рынок",
  c_new: "Новый клиент", c_search: "Найти клиента", c_noname: "Без имени", c_empty: "Клиентов пока нет. Добавьте первого — его лид сразу попадёт в СВК.",
  c_calc_btn: "Калькулятор", st_new: "Новый", st_search: "Подбор", st_shows: "Показы", st_contract: "Договор", st_deal: "Сделка", st_lost: "Отказ",
  tab_card: "Карточка", tab_msg: "Сообщения", tab_calc: "Калькулятор",
  g_contact: "Контакт", g_contract: "Для договора", g_request: "Запрос клиента", g_viewed: "Просмотренные объекты",
  f_name: "Имя и фамилия", f_phone: "Телефон", f_email: "Email", f_lang: "Язык общения", f_source: "Откуда лид",
  src_direct: "Прямой клиент", src_agents: "Риэлтор", src_duty: "Дежурство",
  f_status: "Статус", f_lost: "Причина отказа и этап", f_address: "Адрес проживания (zamieszkały)", f_id: "Паспорт / документ (серия и номер)",
  f_pesel: "PESEL", f_package: "Пакет", f_commission: "Комиссия, %", f_type: "Тип объекта", f_location: "Районы / локация",
  f_area: "Площадь от, м²", f_parking: "Паркинг", f_budget: "Бюджет, zł/мес.", f_residents: "Кто будет жить", f_children: "Дети",
  f_pets: "Животные", f_move_in: "Дата заселения", f_term: "Срок аренды", f_income: "Работа / источник дохода",
  f_okaz: "Najem okazjonalny", f_must: "Обязательно", f_not: "Не рассматриваем", f_extra: "Дополнительно", f_notes: "Заметки для себя",
  yes: "Да", no: "Нет", any: "Не важно",
  v_date: "Дата", v_address: "Адрес", v_rooms: "Комн.", v_rent: "Аренда", v_admin: "Czynsz", v_link: "Ссылка", v_add: "Добавить просмотр",
  v_none: "Пока нет просмотров. Каждый добавленный просмотр засчитывается в СВК как проведённый показ и попадает в приложение к договору.",
  contract_btn: "Сформировать договор (PDF)", contract_done: "Договор готов: {f}", contract_need: "Для договора заполните: {f}",
  delete: "Удалить клиента", delete_confirm: "Удалить карточку клиента {n}? Это нельзя отменить.", saved: "Сохранено", saving: "Сохраняю…",
  svk_added: "В СВК: {w}", svk_w: { direct: "+1 лид", agents: "+1 лид", duty: "+1 лид", shows: "+1 показ", coop: "+1 договор", lost: "+1 отказ", main: "+1 основной договор" },
  msg_lang: "Язык сообщения", msg_copy: "Копировать", msg_copied: "Сообщение скопировано", msg_missing: "Не заполнено: {n}. В тексте стоит «___».",
  msg_fields: "Данные для этого сообщения", msg_calc_hint: "Суммы берутся из калькулятора этого клиента.",
  k_title: "Калькулятор заселения", k_rent: "Аренда, zł", k_admin: "Czynsz administracyjny, zł", k_deposit: "Кауция, zł",
  k_package: "Кто платит комиссию", k_owner_pays: "Собственник", k_repeat: "Повторный подбор (скидка {p}%)",
  k_addons: "Услуги по запросу", k_included: "входит в пакет", k_notary: "Нотариус (najem okazjonalny)", k_translator: "Переводчик у нотариуса",
  k_owner_comm: "Комиссия от собственника, % аренды", k_client_pays: "Клиент платит в день подписания", k_first: "Первый месяц (аренда + czynsz)",
  k_dep: "Кауция", k_comm: "Комиссия агентства", k_extra: "Услуги по запросу", k_total: "Итого в день подписания",
  k_at_notary: "Отдельно у нотариуса", k_you: "Твой доход по сделке", k_level: "уровень {p}%", k_company: "Комиссия компании",
  k_copy: "Скопировать сообщение клиенту", k_save: "Применить к клиенту",
  a_okaz: "Адрес для najem okazjonalny", a_pesel: "Сопровождение PESEL", a_meld: "Сопровождение meldunek", a_bank: "Помощь со счётом в банке",
  mk_title: "Рынок аренды Варшавы", mk_sub: "Медианы по свежим объявлениям Otodom. Обновляется раз в день, пока программа открыта.",
  mk_last: "снимок {d}", mk_since: "история с {d}", mk_refresh: "Обновить сейчас", mk_running: "Собираю районы: {n} из 18…",
  mk_empty_t: "Данных о рынке пока нет", mk_empty: "Программа соберёт цены по 18 районам Варшавы (пара минут). Тренд «растут или падают» появится через несколько дней сбора.",
  mk_m2: "Медиана, zł/м²", mk_r1: "1 комната", mk_r2: "2 комнаты", mk_r3: "3 комнаты", mk_week: "за неделю", mk_month: "за месяц",
  mk_district: "Район", mk_n: "Объявл.", mk_median: "Медиана/мес", mk_trend: "Тренд zł/м²", mk_wait: "нужна неделя истории",
  mk_up: "Цены растут", mk_down: "Цены снижаются", mk_flat: "Цены стабильны",
  srch_mkt_up: "+{p}% к рынку", srch_mkt_down: "{p}% к рынку", srch_drop: "−{d} zł",
  set_agent: "Имя в сообщениях клиентам", set_agent_ph: "например, Павло", set_level: "Мой уровень (доля от комиссии)",
  set_tpl: "Шаблон договора", set_tpl_ok: "Загружен", set_tpl_no: "Не загружен", set_tpl_btn: "Загрузить PDF", set_tpl_done: "Шаблон договора загружен",
},
uk: {
  m_clients: "Клієнти", m_market: "Ринок",
  c_new: "Новий клієнт", c_search: "Знайти клієнта", c_noname: "Без імені", c_empty: "Клієнтів поки немає. Додайте першого — його лід одразу потрапить у СВК.",
  c_calc_btn: "Калькулятор", st_new: "Новий", st_search: "Підбір", st_shows: "Покази", st_contract: "Договір", st_deal: "Угода", st_lost: "Відмова",
  tab_card: "Картка", tab_msg: "Повідомлення", tab_calc: "Калькулятор",
  g_contact: "Контакт", g_contract: "Для договору", g_request: "Запит клієнта", g_viewed: "Переглянуті об'єкти",
  f_name: "Ім'я та прізвище", f_phone: "Телефон", f_email: "Email", f_lang: "Мова спілкування", f_source: "Звідки лід",
  src_direct: "Прямий клієнт", src_agents: "Рієлтор", src_duty: "Чергування",
  f_status: "Статус", f_lost: "Причина відмови та етап", f_address: "Адреса проживання (zamieszkały)", f_id: "Паспорт / документ (серія і номер)",
  f_pesel: "PESEL", f_package: "Пакет", f_commission: "Комісія, %", f_type: "Тип об'єкта", f_location: "Райони / локація",
  f_area: "Площа від, м²", f_parking: "Паркінг", f_budget: "Бюджет, zł/міс.", f_residents: "Хто житиме", f_children: "Діти",
  f_pets: "Тварини", f_move_in: "Дата заселення", f_term: "Термін оренди", f_income: "Робота / джерело доходу",
  f_okaz: "Najem okazjonalny", f_must: "Обов'язково", f_not: "Не розглядаємо", f_extra: "Додатково", f_notes: "Нотатки для себе",
  yes: "Так", no: "Ні", any: "Не важливо",
  v_date: "Дата", v_address: "Адреса", v_rooms: "Кімн.", v_rent: "Оренда", v_admin: "Czynsz", v_link: "Посилання", v_add: "Додати перегляд",
  v_none: "Поки немає переглядів. Кожен доданий перегляд зараховується в СВК як проведений показ і потрапляє в додаток до договору.",
  contract_btn: "Сформувати договір (PDF)", contract_done: "Договір готовий: {f}", contract_need: "Для договору заповніть: {f}",
  delete: "Видалити клієнта", delete_confirm: "Видалити картку клієнта {n}? Це не можна скасувати.", saved: "Збережено", saving: "Зберігаю…",
  svk_added: "У СВК: {w}", svk_w: { direct: "+1 лід", agents: "+1 лід", duty: "+1 лід", shows: "+1 показ", coop: "+1 договір", lost: "+1 відмова", main: "+1 основний договір" },
  msg_lang: "Мова повідомлення", msg_copy: "Копіювати", msg_copied: "Повідомлення скопійовано", msg_missing: "Не заповнено: {n}. У тексті стоїть «___».",
  msg_fields: "Дані для цього повідомлення", msg_calc_hint: "Суми беруться з калькулятора цього клієнта.",
  k_title: "Калькулятор заселення", k_rent: "Оренда, zł", k_admin: "Czynsz administracyjny, zł", k_deposit: "Кауція, zł",
  k_package: "Хто платить комісію", k_owner_pays: "Власник", k_repeat: "Повторний підбір (знижка {p}%)",
  k_addons: "Послуги на запит", k_included: "входить у пакет", k_notary: "Нотаріус (najem okazjonalny)", k_translator: "Перекладач у нотаріуса",
  k_owner_comm: "Комісія від власника, % оренди", k_client_pays: "Клієнт платить у день підписання", k_first: "Перший місяць (оренда + czynsz)",
  k_dep: "Кауція", k_comm: "Комісія агенції", k_extra: "Послуги на запит", k_total: "Разом у день підписання",
  k_at_notary: "Окремо в нотаріуса", k_you: "Твій дохід з угоди", k_level: "рівень {p}%", k_company: "Комісія компанії",
  k_copy: "Скопіювати повідомлення клієнту", k_save: "Застосувати до клієнта",
  a_okaz: "Адреса для najem okazjonalny", a_pesel: "Супровід PESEL", a_meld: "Супровід meldunek", a_bank: "Допомога з рахунком у банку",
  mk_title: "Ринок оренди Варшави", mk_sub: "Медіани за свіжими оголошеннями Otodom. Оновлюється раз на день, поки програма відкрита.",
  mk_last: "знімок {d}", mk_since: "історія з {d}", mk_refresh: "Оновити зараз", mk_running: "Збираю райони: {n} з 18…",
  mk_empty_t: "Даних про ринок поки немає", mk_empty: "Програма збере ціни по 18 районах Варшави (кілька хвилин). Тренд «ростуть чи падають» з'явиться через кілька днів збору.",
  mk_m2: "Медіана, zł/м²", mk_r1: "1 кімната", mk_r2: "2 кімнати", mk_r3: "3 кімнати", mk_week: "за тиждень", mk_month: "за місяць",
  mk_district: "Район", mk_n: "Огол.", mk_median: "Медіана/міс", mk_trend: "Тренд zł/м²", mk_wait: "потрібен тиждень історії",
  mk_up: "Ціни ростуть", mk_down: "Ціни знижуються", mk_flat: "Ціни стабільні",
  srch_mkt_up: "+{p}% до ринку", srch_mkt_down: "{p}% до ринку", srch_drop: "−{d} zł",
  set_agent: "Ім'я в повідомленнях клієнтам", set_agent_ph: "наприклад, Павло", set_level: "Мій рівень (частка від комісії)",
  set_tpl: "Шаблон договору", set_tpl_ok: "Завантажено", set_tpl_no: "Не завантажено", set_tpl_btn: "Завантажити PDF", set_tpl_done: "Шаблон договору завантажено",
},
pl: {
  m_clients: "Klienci", m_market: "Rynek",
  c_new: "Nowy klient", c_search: "Szukaj klienta", c_noname: "Bez nazwiska", c_empty: "Nie ma jeszcze klientów. Dodaj pierwszego — jego lead od razu trafi do raportu.",
  c_calc_btn: "Kalkulator", st_new: "Nowy", st_search: "Dobór", st_shows: "Prezentacje", st_contract: "Umowa", st_deal: "Transakcja", st_lost: "Odmowa",
  tab_card: "Karta", tab_msg: "Wiadomości", tab_calc: "Kalkulator",
  g_contact: "Kontakt", g_contract: "Do umowy", g_request: "Zapytanie klienta", g_viewed: "Obejrzane mieszkania",
  f_name: "Imię i nazwisko", f_phone: "Telefon", f_email: "Email", f_lang: "Język kontaktu", f_source: "Skąd lead",
  src_direct: "Klient bezpośredni", src_agents: "Agent", src_duty: "Dyżur",
  f_status: "Status", f_lost: "Powód odmowy i etap", f_address: "Adres zamieszkania", f_id: "Paszport / dokument (seria i numer)",
  f_pesel: "PESEL", f_package: "Pakiet", f_commission: "Prowizja, %", f_type: "Rodzaj nieruchomości", f_location: "Dzielnice / lokalizacja",
  f_area: "Powierzchnia od, m²", f_parking: "Parking", f_budget: "Budżet, zł/mies.", f_residents: "Kto zamieszka", f_children: "Dzieci",
  f_pets: "Zwierzęta", f_move_in: "Data wprowadzenia", f_term: "Okres najmu", f_income: "Praca / źródło dochodu",
  f_okaz: "Najem okazjonalny", f_must: "Obowiązkowo", f_not: "Nie rozważamy", f_extra: "Dodatkowo", f_notes: "Notatki dla siebie",
  yes: "Tak", no: "Nie", any: "Bez znaczenia",
  v_date: "Data", v_address: "Adres", v_rooms: "Pok.", v_rent: "Najem", v_admin: "Czynsz", v_link: "Link", v_add: "Dodaj prezentację",
  v_none: "Brak prezentacji. Każda dodana prezentacja liczy się w raporcie i trafia do załącznika umowy.",
  contract_btn: "Utwórz umowę (PDF)", contract_done: "Umowa gotowa: {f}", contract_need: "Do umowy uzupełnij: {f}",
  delete: "Usuń klienta", delete_confirm: "Usunąć kartę klienta {n}? Tego nie można cofnąć.", saved: "Zapisano", saving: "Zapisuję…",
  svk_added: "W raporcie: {w}", svk_w: { direct: "+1 lead", agents: "+1 lead", duty: "+1 lead", shows: "+1 prezentacja", coop: "+1 umowa", lost: "+1 odmowa", main: "+1 umowa najmu" },
  msg_lang: "Język wiadomości", msg_copy: "Kopiuj", msg_copied: "Wiadomość skopiowana", msg_missing: "Brakuje: {n}. W tekście jest „___”.",
  msg_fields: "Dane do tej wiadomości", msg_calc_hint: "Kwoty pochodzą z kalkulatora tego klienta.",
  k_title: "Kalkulator wprowadzenia", k_rent: "Najem, zł", k_admin: "Czynsz administracyjny, zł", k_deposit: "Kaucja, zł",
  k_package: "Kto płaci prowizję", k_owner_pays: "Właściciel", k_repeat: "Ponowny dobór (rabat {p}%)",
  k_addons: "Usługi na życzenie", k_included: "w pakiecie", k_notary: "Notariusz (najem okazjonalny)", k_translator: "Tłumacz u notariusza",
  k_owner_comm: "Prowizja od właściciela, % najmu", k_client_pays: "Klient płaci w dniu podpisania", k_first: "Pierwszy miesiąc (najem + czynsz)",
  k_dep: "Kaucja", k_comm: "Prowizja agencji", k_extra: "Usługi na życzenie", k_total: "Razem w dniu podpisania",
  k_at_notary: "Osobno u notariusza", k_you: "Twój dochód z transakcji", k_level: "poziom {p}%", k_company: "Prowizja firmy",
  k_copy: "Kopiuj wiadomość do klienta", k_save: "Zastosuj do klienta",
  a_okaz: "Adres do najmu okazjonalnego", a_pesel: "Pomoc z PESEL", a_meld: "Pomoc z meldunkiem", a_bank: "Pomoc z kontem w banku",
  mk_title: "Rynek najmu w Warszawie", mk_sub: "Mediany ze świeżych ogłoszeń Otodom. Aktualizacja raz dziennie, gdy program jest otwarty.",
  mk_last: "stan na {d}", mk_since: "historia od {d}", mk_refresh: "Odśwież teraz", mk_running: "Zbieram dzielnice: {n} z 18…",
  mk_empty_t: "Brak danych o rynku", mk_empty: "Program zbierze ceny z 18 dzielnic Warszawy (kilka minut). Trend „rosną czy spadają” pojawi się po kilku dniach.",
  mk_m2: "Mediana, zł/m²", mk_r1: "1 pokój", mk_r2: "2 pokoje", mk_r3: "3 pokoje", mk_week: "w tygodniu", mk_month: "w miesiącu",
  mk_district: "Dzielnica", mk_n: "Ogł.", mk_median: "Mediana/mies", mk_trend: "Trend zł/m²", mk_wait: "potrzeba tygodnia historii",
  mk_up: "Ceny rosną", mk_down: "Ceny spadają", mk_flat: "Ceny stabilne",
  srch_mkt_up: "+{p}% do rynku", srch_mkt_down: "{p}% do rynku", srch_drop: "−{d} zł",
  set_agent: "Imię w wiadomościach do klientów", set_agent_ph: "np. Paweł", set_level: "Mój poziom (udział w prowizji)",
  set_tpl: "Szablon umowy", set_tpl_ok: "Wgrany", set_tpl_no: "Nie wgrany", set_tpl_btn: "Wgraj PDF", set_tpl_done: "Szablon umowy wgrany",
},
};
Object.assign(L.ru, CL.ru); Object.assign(L.uk, CL.uk); Object.assign(L.pl, CL.pl);
// списки для полей запроса: можно выбрать или вписать своё
Object.assign(L.ru, {"f_rooms": "Комнаты", "l_rooms": ["Кавалерка", "1 комната", "2 комнаты", "3 комнаты", "4+ комнаты", "1–2 комнаты", "2–3 комнаты"], "l_type": ["Квартира", "Кавалерка", "Апартаменты", "Дом", "Комната"], "l_term": ["12 месяцев", "6 месяцев", "от 1 года", "долгосрочно"], "l_residents": ["1 человек", "пара", "семья с ребёнком", "2 друга", "3+ человека"], "l_pets": ["нет", "кот", "маленькая собака", "большая собака"], "l_children": ["нет", "1 ребёнок", "2 ребёнка"], "l_move_in": ["сразу", "с 1 числа", "через 2 недели", "гибко"], "l_income": ["umowa o pracę", "B2B / ФОП", "студент", "своя фирма"], "f_pick": "выбери или впиши своё", "l_location": ["Mokotów", "Wola", "Śródmieście", "Ochota", "Żoliborz", "Bielany", "Bemowo", "Ursynów", "Wilanów", "Praga-Południe", "Praga-Północ", "Targówek", "Białołęka", "Włochy", "Ursus", "Wawer", "Wesoła", "Rembertów"]});
Object.assign(L.uk, {"f_rooms": "Кімнати", "l_rooms": ["Кавалерка", "1 кімната", "2 кімнати", "3 кімнати", "4+ кімнати", "1–2 кімнати", "2–3 кімнати"], "l_type": ["Квартира", "Кавалерка", "Апартаменти", "Будинок", "Кімната"], "l_term": ["12 місяців", "6 місяців", "від 1 року", "довгостроково"], "l_residents": ["1 особа", "пара", "сім'я з дитиною", "2 друзі", "3+ особи"], "l_pets": ["немає", "кіт", "маленький собака", "великий собака"], "l_children": ["немає", "1 дитина", "2 дитини"], "l_move_in": ["одразу", "з 1 числа", "через 2 тижні", "гнучко"], "l_income": ["umowa o pracę", "B2B / ФОП", "студент", "своя фірма"], "f_pick": "вибери або впиши своє", "l_location": ["Mokotów", "Wola", "Śródmieście", "Ochota", "Żoliborz", "Bielany", "Bemowo", "Ursynów", "Wilanów", "Praga-Południe", "Praga-Północ", "Targówek", "Białołęka", "Włochy", "Ursus", "Wawer", "Wesoła", "Rembertów"]});
Object.assign(L.pl, {"f_rooms": "Pokoje", "l_rooms": ["Kawalerka", "1 pokój", "2 pokoje", "3 pokoje", "4+ pokoje", "1–2 pokoje", "2–3 pokoje"], "l_type": ["Mieszkanie", "Kawalerka", "Apartament", "Dom", "Pokój"], "l_term": ["12 miesięcy", "6 miesięcy", "od 1 roku", "długoterminowo"], "l_residents": ["1 osoba", "para", "rodzina z dzieckiem", "2 znajomych", "3+ osoby"], "l_pets": ["brak", "kot", "mały pies", "duży pies"], "l_children": ["brak", "1 dziecko", "2 dzieci"], "l_move_in": ["od zaraz", "od 1. dnia miesiąca", "za 2 tygodnie", "elastycznie"], "l_income": ["umowa o pracę", "B2B", "student", "własna firma"], "f_pick": "wybierz lub wpisz swoje", "l_location": ["Mokotów", "Wola", "Śródmieście", "Ochota", "Żoliborz", "Bielany", "Bemowo", "Ursynów", "Wilanów", "Praga-Południe", "Praga-Północ", "Targówek", "Białołęka", "Włochy", "Ursus", "Wawer", "Wesoła", "Rembertów"]});

// подбор квартир
Object.assign(L.ru, {
  mt_title: "Подходящие квартиры", mt_of: "{n} из {t}", mt_refresh: "Обновить", mt_new: "новая", mt_owner: "собственник", mt_agency: "агентство",
  mt_agreed: "согласен на 50%", mt_days: "{d} дн. на сайте", mt_today: "сегодня", mt_open: "Открыть", mt_photo: "Обработать фото", mt_skip: "Не подходит",
  mt_need: "Заполни в запросе бюджет, районы или комнаты, и здесь появятся квартиры из того, что Hermea уже собрала: собственники Otodom и OLX, свежие объявления всех районов и твои поиски.",
  mt_none: "Сейчас ничего не подходит. Можно поднять бюджет или добавить районы. Объявления обновляются каждый день.",
  mt_copy: "Скопировать подборку ({n})", mt_links: "со ссылками", mt_pick: "Отметь квартиры галочками, текст будет на языке клиента.",
  mt_copied: "Подборка скопирована", mt_photo_ok: "Фото обрабатываются, смотри «Обработка фото»", mt_upto: "до {b} zł", mt_from: "от {a} м²", mt_rooms: "{r} комн.",
  mt_parking: "паркинг", mt_pets: "с животными", mt_loading: "Подбираю…",
});
Object.assign(L.uk, {
  mt_title: "Підходящі квартири", mt_of: "{n} з {t}", mt_refresh: "Оновити", mt_new: "нова", mt_owner: "власник", mt_agency: "агентство",
  mt_agreed: "згоден на 50%", mt_days: "{d} дн. на сайті", mt_today: "сьогодні", mt_open: "Відкрити", mt_photo: "Обробити фото", mt_skip: "Не підходить",
  mt_need: "Заповни в запиті бюджет, райони або кімнати, і тут з'являться квартири з того, що Hermea вже зібрала: власники Otodom і OLX, свіжі оголошення всіх районів і твої пошуки.",
  mt_none: "Зараз нічого не підходить. Можна підняти бюджет або додати райони. Оголошення оновлюються щодня.",
  mt_copy: "Скопіювати добірку ({n})", mt_links: "з посиланнями", mt_pick: "Відміть квартири галочками, текст буде мовою клієнта.",
  mt_copied: "Добірку скопійовано", mt_photo_ok: "Фото обробляються, дивись «Обробка фото»", mt_upto: "до {b} zł", mt_from: "від {a} м²", mt_rooms: "{r} кімн.",
  mt_parking: "паркінг", mt_pets: "з тваринами", mt_loading: "Підбираю…",
});
Object.assign(L.pl, {
  mt_title: "Pasujące mieszkania", mt_of: "{n} z {t}", mt_refresh: "Odśwież", mt_new: "nowe", mt_owner: "właściciel", mt_agency: "agencja",
  mt_agreed: "zgoda na 50%", mt_days: "{d} dni w sieci", mt_today: "dziś", mt_open: "Otwórz", mt_photo: "Obrób zdjęcia", mt_skip: "Nie pasuje",
  mt_need: "Uzupełnij w zapytaniu budżet, dzielnice lub liczbę pokoi, a pojawią się tu mieszkania z tego, co Hermea już zebrała: właściciele z Otodom i OLX, świeże ogłoszenia ze wszystkich dzielnic i Twoje wyszukiwania.",
  mt_none: "Teraz nic nie pasuje. Można podnieść budżet lub dodać dzielnice. Ogłoszenia odświeżają się codziennie.",
  mt_copy: "Kopiuj wybór ({n})", mt_links: "z linkami", mt_pick: "Zaznacz mieszkania, tekst będzie w języku klienta.",
  mt_copied: "Skopiowano", mt_photo_ok: "Zdjęcia w obróbce, zobacz «Obróbka zdjęć»", mt_upto: "do {b} zł", mt_from: "od {a} m²", mt_rooms: "{r} pok.",
  mt_parking: "parking", mt_pets: "ze zwierzętami", mt_loading: "Szukam…",
});

// ================================================================ общие помощники
const zl = (v) => (v == null || v === "" || isNaN(v) ? "0" : String(Math.round(+v)).replace(/\B(?=(\d{3})+(?!\d))/g, " "));
const num = (v) => { const x = parseFloat(String(v || "").replace(/\s/g, "").replace(",", ".")); return isNaN(x) ? 0 : x; };
const PRICE = {
  SMART: { pct: 70, repeat: 5, addons: { okaz: 580, pesel: 200, meld: 200, bank: 200 }, notary: 620 },
  COMFORT: { pct: 100, repeat: 10, addons: { okaz: 400, pesel: 0, meld: 0, bank: 0 }, notary: 0 },
  OWNER: { pct: 0, repeat: 0, addons: { okaz: 580, pesel: 200, meld: 200, bank: 200 }, notary: 620 },
};
const TRANSLATOR = 300;

const CLS = { mnew: {}, match: null, mpick: new Set(), mlinks: false, list: [], q: "", id: null, c: null, tab: "card", tpl: "s1", tplLang: null, vars: {}, saveT: 0, pend: {}, template: false, calcOnly: false };
const CALC_KEY = "hermea_calc_";
function calcState(id) {
  const def = { rent: "", admin: "", deposit: "", pkg: "SMART", repeat: false, addons: {}, notary: false, translator: false, owner: 0 };
  try { return Object.assign(def, JSON.parse(localStorage.getItem(CALC_KEY + (id || "free")) || "{}")); } catch (e) { return def; }
}
function calcSave(id, st) { try { localStorage.setItem(CALC_KEY + (id || "free"), JSON.stringify(st)); } catch (e) {} }
function calc(st) {
  const P = PRICE[st.pkg] || PRICE.SMART;
  const rent = num(st.rent), admin = num(st.admin), base = rent + admin;
  const deposit = st.deposit === "" || st.deposit == null ? rent : num(st.deposit);
  const disc = st.repeat ? P.repeat : 0;
  const commission = Math.round(base * P.pct / 100 * (1 - disc / 100));
  let extra = 0;
  for (const k in P.addons) if (st.addons[k]) extra += P.addons[k];
  const notary = (st.notary ? P.notary : 0) + (st.translator ? TRANSLATOR : 0);
  const owner = Math.round(rent * num(st.owner) / 100);
  const level = (S.st && S.st.settings && S.st.settings.agent_level) || 30;
  return { rent, admin, base, deposit, commission, extra, notary, owner, first: base, total: base + deposit + commission + extra,
    company: commission + owner, mine: Math.round((commission + owner) * level / 100), level, pkg: st.pkg, pct: P.pct, disc };
}

// ================================================================ загрузка и список
async function clientsOpen() {
  try {
    const d = await api("/api/clients");
    CLS.list = d.clients; CLS.template = d.template; CLS.mnew = d.match_new || {};
    if (CLS.id && !CLS.list.find((c) => c.id === CLS.id)) { CLS.id = null; CLS.c = null; }
    if (!CLS.id && !CLS.calcOnly && CLS.list.length) CLS.id = CLS.list[0].id;
    if (CLS.id && (!CLS.c || CLS.c.id !== CLS.id)) CLS.c = (await api("/api/client?id=" + CLS.id)).client;
    drawClients(true);
  } catch (e) { toast(e.message, true); }
}
function statusName(s) { return t("st_" + (s || "new")); }
function drawClients(first) {
  const box = $("#clients");
  box.innerHTML = `<div class="cl-wrap">
    <aside class="cl-list ${first ? "rise" : ""}">
      <div class="cl-list-head">
        <button class="btn-primary sm" type="button" id="clNew">${ICON.plus} ${t("c_new")}</button>
        <button class="btn" type="button" id="clCalc">${t("c_calc_btn")}</button>
      </div>
      <input class="cl-q" id="clQ" type="search" placeholder="${esc(t("c_search"))}" value="${esc(CLS.q)}">
      <div class="cl-items" id="clItems"></div>
    </aside>
    <section class="cl-main" id="clMain"></section></div>`;
  drawList();
  drawMain(first);
  $("#clNew").onclick = newClient;
  $("#clCalc").onclick = () => { CLS.id = null; CLS.c = null; CLS.calcOnly = true; CLS.tab = "calc"; drawList(); drawMain(true); };
  $("#clQ").oninput = (e) => { CLS.q = e.target.value; drawList(); };
}
function drawList() {
  const q = CLS.q.trim().toLowerCase();
  const items = CLS.list.filter((c) => !q || (c.name + " " + c.phone + " " + c.location).toLowerCase().includes(q));
  $("#clItems").innerHTML = items.length ? items.map((c) => `
    <button class="cl-item" type="button" data-cid="${c.id}" aria-current="${c.id === CLS.id}">
      <span class="cl-av">${esc((c.name || "?").trim().slice(0, 1).toUpperCase())}</span>
      <span class="cl-txt"><b>${c.name ? esc(c.name) : `<span class="cl-noname">${esc(t("c_noname"))}</span>`}</b>
        <span>${CLS.mnew[c.id] ? `<i class="mt-badge" title="${esc(t("mt_title"))}">+${CLS.mnew[c.id]}</i>` : ""}<i class="st st-${c.status}">${esc(statusName(c.status))}</i>${c.budget ? ` ${esc(zl(c.budget))} zł` : ""}${c.package ? ` · ${esc(c.package)}` : ""}</span></span>
    </button>`).join("") : `<p class="cl-empty">${t("c_empty")}</p>`;
  $("#clItems").onclick = async (e) => {
    const b = e.target.closest("[data-cid]");
    if (!b) return;
    await flushSave();
    CLS.id = b.dataset.cid; CLS.calcOnly = false;
    CLS.c = (await api("/api/client?id=" + CLS.id)).client;
    CLS.vars = {};
    drawList(); drawMain(true);
  };
}
async function newClient() {
  await flushSave();
  try {
    const r = await api("/api/client", { op: "create", data: { name: "", source: "direct", lang: LANG === "pl" ? "pl" : (LANG === "ru" ? "ru" : "ua") } });
    CLS.c = r.client; CLS.id = r.client.id; CLS.tab = "card"; CLS.calcOnly = false;
    svkToast(r.svk);
    const d = await api("/api/clients"); CLS.list = d.clients;
    drawList(); drawMain(true);
    setTimeout(() => { const n = $("#clMain [data-f='name']"); if (n) n.focus(); }, 80);
  } catch (e) { toast(e.message, true); }
}
function svkToast(list) {
  if (!list || !list.length) return;
  const w = t("svk_w");
  toast(t("svk_added", { w: list.map((m) => (w && w[m]) || m).join(", ") }));
  if (S.st) S.st.svk_touched = true;
}

// ================================================================ карточка
function inp(f, label, opts) {
  opts = opts || {};
  const c = CLS.c || {}, v = c[f] == null ? "" : c[f];
  if (opts.seg) {
    return `<label class="fld ${opts.cls || ""}"><span>${esc(label)}</span><div class="seg seg-sm" data-seg="${f}">${opts.seg.map(([val, txt]) =>
      `<button type="button" data-v="${val}" aria-pressed="${String(v) === String(val)}">${esc(txt)}</button>`).join("")}</div></label>`;
  }
  if (opts.area) return `<label class="fld ${opts.cls || ""}"><span>${esc(label)}</span><textarea data-f="${f}" rows="2">${esc(v)}</textarea></label>`;
  if (opts.list) {        // выпадающий список подсказок, но вписать можно что угодно
    const items = (L[LANG] || L.ru)["l_" + f] || [];
    return `<label class="fld ${opts.cls || ""}"><span>${esc(label)}</span><input data-f="${f}" list="dl-${f}" value="${esc(v)}"
      placeholder="${esc(t("f_pick"))}" autocomplete="off" class="has-list"${opts.multi ? " data-multi=\"1\"" : ""}>
      <datalist id="dl-${f}">${items.map((x) => `<option value="${esc(x)}"></option>`).join("")}</datalist></label>`;
  }
  return `<label class="fld ${opts.cls || ""}"><span>${esc(label)}</span><input data-f="${f}" type="${opts.type || "text"}" value="${esc(v)}" ${opts.ph ? `placeholder="${esc(opts.ph)}"` : ""} autocomplete="off"></label>`;
}
function drawMain(first) {
  const m = $("#clMain");
  if (CLS.calcOnly || !CLS.c) {
    m.innerHTML = `<div class="cl-head"><h1 class="display">${t("k_title")}</h1></div><div id="clBody"></div>`;
    drawCalc($("#clBody"), null);
    if (first) enter(m, ".cl-head, #clBody > *");
    return;
  }
  const c = CLS.c;
  m.innerHTML = `
    <div class="cl-head">
      <div><h1 class="display" id="clTitle">${esc(c.name || t("c_new"))}</h1>
        <div class="seg slide cl-status" data-seg="status">${["new", "search", "shows", "contract", "deal", "lost"].map((s) =>
          `<button type="button" data-v="${s}" aria-pressed="${c.status === s}">${esc(statusName(s))}</button>`).join("")}</div></div>
      <div class="seg slide cl-tabs" id="clTabs">
        <button type="button" data-tab="card" aria-pressed="${CLS.tab === "card"}">${t("tab_card")}</button>
        <button type="button" data-tab="msg" aria-pressed="${CLS.tab === "msg"}">${t("tab_msg")}</button>
        <button type="button" data-tab="calc" aria-pressed="${CLS.tab === "calc"}">${t("tab_calc")}</button>
      </div>
    </div>
    <div id="clBody"></div>
    <p class="cl-saved" id="clSaved"></p>`;
  requestAnimationFrame(() => { slideSeg($("#clTabs")); slideSeg(m.querySelector(".cl-status")); });
  $("#clTabs").onclick = async (e) => {
    const b = e.target.closest("[data-tab]");
    if (!b || b.dataset.tab === CLS.tab) return;
    await flushSave();
    CLS.tab = b.dataset.tab;
    $("#clTabs").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    slideSeg($("#clTabs"));
    morph(() => drawTab(true));
  };
  m.querySelector(".cl-status").onclick = (e) => {
    const b = e.target.closest("[data-v]");
    if (!b) return;
    setField("status", b.dataset.v, true);
    m.querySelectorAll(".cl-status button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    slideSeg(m.querySelector(".cl-status"));
    if (CLS.tab === "card") { const lr = $("#clLost"); if (lr) lr.hidden = b.dataset.v !== "lost"; }
  };
  drawTab(first);
}
function drawTab(first) {
  const body = $("#clBody");
  if (CLS.tab === "msg") drawMessages(body);
  else if (CLS.tab === "calc") drawCalc(body, CLS.c);
  else drawCard(body);
  if (first) enter(body, ":scope > *");
}
function drawCard(body) {
  const c = CLS.c;
  const pkgSeg = [["SMART", "SMART 70%"], ["COMFORT", "COMFORT 100%"]];
  const yn = [["yes", t("yes")], ["no", t("no")], ["any", t("any")]];
  body.innerHTML = `
    <div class="cl-grid">
      <section class="cl-card"><h3>${t("g_contact")}</h3><div class="flds">
        ${inp("name", t("f_name"), { cls: "w2" })}${inp("phone", t("f_phone"), { type: "tel" })}${inp("email", t("f_email"), { type: "email" })}
        ${inp("lang", t("f_lang"), { seg: [["ua", "UA"], ["ru", "RU"], ["pl", "PL"]] })}
        ${inp("source", t("f_source"), { cls: "w2", seg: [["direct", t("src_direct")], ["agents", t("src_agents")], ["duty", t("src_duty")]] })}
        <div class="w2" id="clLost" ${c.status === "lost" ? "" : "hidden"}>${inp("lost_reason", t("f_lost"))}</div>
      </div></section>
      <section class="cl-card"><h3>${t("g_contract")}</h3><div class="flds">
        ${inp("address", t("f_address"), { cls: "w2" })}${inp("id_doc", t("f_id"))}${inp("pesel", t("f_pesel"))}
        ${inp("package", t("f_package"), { seg: pkgSeg })}${inp("commission", t("f_commission"), { type: "number", ph: c.package === "COMFORT" ? "100" : "70" })}
        <div class="w2 cl-actions"><button class="btn ink" type="button" id="clContract">${ICON_DOC} ${t("contract_btn")}</button>
          <button class="text-btn" type="button" id="clDelete">${t("delete")}</button></div>
      </div></section>
      <section class="cl-card w-full"><h3>${t("g_request")}</h3><div class="flds three">
        ${inp("type", t("f_type"), { list: 1 })}${inp("rooms", t("f_rooms"), { list: 1 })}${inp("location", t("f_location"), { list: 1, multi: 1 })}
        ${inp("budget", t("f_budget"), { type: "number" })}${inp("area", t("f_area"), { type: "number" })}${inp("residents", t("f_residents"), { list: 1 })}
        ${inp("move_in", t("f_move_in"), { list: 1 })}${inp("children", t("f_children"), { list: 1 })}${inp("pets", t("f_pets"), { list: 1 })}
        ${inp("term", t("f_term"), { list: 1 })}
        ${inp("parking", t("f_parking"), { seg: yn })}${inp("okazjonalny", t("f_okaz"), { seg: [["yes", t("yes")], ["no", t("no")]] })}${inp("income", t("f_income"), { list: 1 })}
        ${inp("must", t("f_must"), { area: true })}${inp("not_considered", t("f_not"), { area: true })}${inp("extra", t("f_extra"), { area: true })}
        ${inp("notes", t("f_notes"), { area: true, cls: "w3" })}
      </div></section>
      <section class="cl-card w-full mt-card" id="clMatch"></section>
      <section class="cl-card w-full"><h3>${t("g_viewed")}</h3><div id="clViewed"></div></section>
    </div>`;
  drawViewed();
  loadMatch();
  body.querySelectorAll("[data-f]").forEach((el) => {
    el.dataset.prev = el.value;
    el.addEventListener("input", (e) => {
      // районы: выбор из списка добавляется через запятую, а не заменяет уже вписанное
      if (el.dataset.multi && e.inputType === "insertReplacementText" && el.dataset.prev.trim()) {
        const prev = el.dataset.prev.replace(/[,\s]+$/, "");
        if (!prev.split(/\s*,\s*/).includes(el.value)) el.value = `${prev}, ${el.value}`;
        else el.value = prev;
      }
      el.dataset.prev = el.value;
      setField(el.dataset.f, el.value);
    });
  });
  body.querySelectorAll("[data-seg]").forEach((sg) => sg.addEventListener("click", (e) => {
    const b = e.target.closest("[data-v]");
    if (!b) return;
    sg.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    setField(sg.dataset.seg, b.dataset.v, true);
  }));
  $("#clContract").onclick = makeContract;
  $("#clDelete").onclick = async () => {
    if (!confirm(t("delete_confirm", { n: c.name || "" }))) return;
    await api("/api/client", { op: "delete", id: c.id }).catch(() => {});
    CLS.id = null; CLS.c = null; clientsOpen();
  };
}
function drawViewed() {
  const c = CLS.c, box = $("#clViewed");
  const rows = (c.viewed || []).map((o, i) => `<tr><td>${i + 1}</td><td>${esc(o.date)}</td><td>${o.link ? `<button class="link" type="button" data-vlink="${esc(o.link)}">${esc(o.address)}</button>` : esc(o.address)}</td>
    <td>${esc(o.rooms)}</td><td>${esc(zl(o.rent))}${o.admin ? " + " + esc(zl(o.admin)) : ""}</td>
    <td><button class="x" type="button" data-vdel="${o.id}" aria-label="×">×</button></td></tr>`).join("");
  const today = new Date().toLocaleDateString("pl-PL");
  box.innerHTML = `${rows ? `<table class="cl-vt"><thead><tr><th>№</th><th>${t("v_date")}</th><th>${t("v_address")}</th><th>${t("v_rooms")}</th><th>${t("v_rent")}</th><th></th></tr></thead><tbody>${rows}</tbody></table>` : `<p class="hint">${t("v_none")}</p>`}
    <form class="cl-vadd" id="clVAdd" autocomplete="off">
      <input name="date" value="${esc(today)}" aria-label="${esc(t("v_date"))}" style="width:110px">
      <input name="address" placeholder="${esc(t("v_address"))}" required style="flex:2 1 220px">
      <input name="rooms" placeholder="${esc(t("v_rooms"))}" style="width:70px">
      <input name="rent" placeholder="${esc(t("v_rent"))}" type="number" style="width:100px">
      <input name="admin" placeholder="${esc(t("v_admin"))}" type="number" style="width:100px">
      <input name="link" placeholder="${esc(t("v_link"))}" style="flex:1 1 180px">
      <button class="btn-primary sm" type="submit">${t("v_add")}</button></form>`;
  $("#clVAdd").onsubmit = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    try {
      const r = await api("/api/client", { op: "viewed", id: c.id, data });
      CLS.c = r.client; svkToast(r.svk); drawViewed(); refreshListItem();
      const tb = $("#clViewed tbody tr:last-child"); if (tb && !RM) tb.classList.add("row-in");
    } catch (err) { toast(err.message, true); }
  };
  box.onclick = async (e) => {
    const d = e.target.closest("[data-vdel]"), l = e.target.closest("[data-vlink]");
    if (l) api("/api/open", { what: "url", url: l.dataset.vlink }).catch((err) => toast(err.message, true));
    if (d) { const r = await api("/api/client", { op: "viewed", id: c.id, data: { remove: d.dataset.vdel } }); CLS.c = r.client; drawViewed(); refreshListItem(); }
  };
}
function setField(f, v, now) {
  if (!CLS.c) return;
  CLS.c[f] = v;
  CLS.pend[f] = v;
  if (f === "name") { const h = $("#clTitle"); if (h) h.textContent = v || t("c_new"); }
  if (f === "package" && !CLS.c.commission) { const ci = $("#clMain [data-f='commission']"); if (ci) ci.placeholder = v === "COMFORT" ? "100" : "70"; }
  $("#clSaved").textContent = t("saving");
  clearTimeout(CLS.saveT);
  CLS.saveT = setTimeout(flushSave, now ? 0 : 700);
}
async function flushSave() {
  clearTimeout(CLS.saveT);
  if (!CLS.c || !Object.keys(CLS.pend).length) return;
  const data = CLS.pend; CLS.pend = {};
  try {
    const r = await api("/api/client", { op: "update", id: CLS.c.id, data });
    Object.assign(CLS.c, data);
    svkToast(r.svk);
    const s = $("#clSaved"); if (s) s.textContent = t("saved");
    refreshListItem();
    if (["budget", "location", "type", "rooms", "area", "parking", "pets", "must"].some((k) => k in data)) loadMatch();
  } catch (e) { toast(e.message, true); }
}
function refreshListItem() {
  const c = CLS.c, i = CLS.list.findIndex((x) => x.id === c.id);
  if (i >= 0) Object.assign(CLS.list[i], { name: c.name, status: c.status, budget: c.budget, package: c.package, phone: c.phone, location: c.location });
  if ($("#clItems")) drawList();
}
async function makeContract() {
  await flushSave();
  const c = CLS.c, need = [];
  if (!c.name) need.push(t("f_name"));
  if (!c.address) need.push(t("f_address"));
  if (!c.id_doc) need.push(t("f_id"));
  if (!c.package) need.push(t("f_package"));
  if (need.length) return toast(t("contract_need", { f: need.join(", ") }), true);
  const b = $("#clContract"); b.disabled = true;
  try {
    const r = await api("/api/client", { op: "contract", id: c.id });
    if (r.error) throw new Error(r.error);
    CLS.c = r.client; svkToast(r.svk);
    toast(t("contract_done", { f: r.file.split("/").pop() }));
    refreshListItem();
  } catch (e) { toast(e.message, true); }
  b.disabled = false;
}

// ================================================================ сообщения
function tplVals(lang) {
  const c = CLS.c || {}, st = calcState(c.id), k = calc(st);
  const yn = (v) => ({ yes: { ua: "так", ru: "да", pl: "tak" }, no: { ua: "ні", ru: "нет", pl: "nie" }, any: { ua: "не важливо", ru: "не важно", pl: "bez znaczenia" } }[v] || {})[lang] || "";
  const agent = (S.st && S.st.settings && S.st.settings.agent_name) || SV.agent || "";
  const extraLine = { ua: "\n• послуги на запит — {x} zł", ru: "\n• услуги по запросу — {x} zł", pl: "\n• usługi dodatkowe — {x} zł" };
  const v = {
    agent, client: (c.name || "").trim().split(/\s+/)[0] || "",
    residents: c.residents, children: c.children, pets: c.pets, type: c.type, area: c.area, location: c.location,
    move_in: c.move_in, term: c.term, budget: c.budget ? zl(c.budget) : "", parking: yn(c.parking), income: c.income,
    okazjonalny: yn(c.okazjonalny), package: c.package || (st.pkg !== "OWNER" ? st.pkg : ""), must: c.must,
    not_considered: c.not_considered, extra: c.extra,
    c_first: k.base ? zl(k.first) : "", c_deposit: k.base ? zl(k.deposit) : "", c_commission: k.base ? zl(k.commission) : "",
    c_total: k.base ? zl(k.total) : "",
  };
  for (const l of ["ua", "ru", "pl"]) v["c_extra_" + l] = k.extra ? extraLine[l].replace("{x}", zl(k.extra)) : "";
  return Object.assign(v, CLS.vars);
}
function fillTpl(text, vals) {
  const missing = new Set();
  const out = text.replace(/\{(\w+)\}/g, (m, k) => {
    const x = vals[k];
    if (x == null || x === "") { if (!k.startsWith("c_extra")) missing.add(k); return k.startsWith("c_extra") ? "" : "___"; }
    return x;
  });
  return { out, missing: [...missing] };
}
function drawMessages(body) {
  const c = CLS.c || {};
  const lang = CLS.tplLang || c.lang || "ua";
  const list = TPL[lang];
  const cur = list[CLS.tpl] ? CLS.tpl : "s1";
  const vars = TPL_VARS[cur] || [];
  const lbl = { v_address: t("v_address"), v_date: t("v_date"), v_time: { ru: "Время", uk: "Час", pl: "Godzina" }[LANG], v_price: t("v_rent"), v_link: t("v_link") };
  body.innerHTML = `<div class="msg-grid">
    <nav class="msg-list">${TPL_ORDER.map((k) => `<button type="button" data-tpl="${k}" aria-current="${k === cur}"><b>${esc(list[k][0])}</b><span>${esc(list[k][1])}</span></button>`).join("")}</nav>
    <section class="cl-card msg-view">
      <div class="msg-top"><div class="seg seg-sm" id="msgLang">${["ua", "ru", "pl"].map((l) => `<button type="button" data-l="${l}" aria-pressed="${l === lang}">${l.toUpperCase()}</button>`).join("")}</div>
        <button class="btn-primary sm" type="button" id="msgCopy">${ICON.copy} ${t("msg_copy")}</button></div>
      ${vars.length ? `<div class="flds msg-vars">${vars.map((v) => `<label class="fld"><span>${esc(lbl[v])}</span><input data-var="${v}" value="${esc(CLS.vars[v] || "")}"></label>`).join("")}</div>` : ""}
      ${cur === "s6" ? `<p class="hint">${t("msg_calc_hint")}</p>` : ""}
      <pre class="msg-text" id="msgText"></pre><p class="msg-miss" id="msgMiss"></p>
    </section></div>`;
  const paint = () => {
    const r = fillTpl(TPL[lang][cur][2], tplVals(lang));
    $("#msgText").innerHTML = esc(r.out).replace(/___/g, '<mark>___</mark>');
    $("#msgMiss").textContent = r.missing.length ? t("msg_missing", { n: r.missing.length }) : "";
    return r.out;
  };
  paint();
  body.querySelector(".msg-list").onclick = (e) => { const b = e.target.closest("[data-tpl]"); if (b) { CLS.tpl = b.dataset.tpl; drawMessages(body); } };
  $("#msgLang").onclick = (e) => { const b = e.target.closest("[data-l]"); if (b) { CLS.tplLang = b.dataset.l; drawMessages(body); } };
  body.querySelectorAll("[data-var]").forEach((el) => el.addEventListener("input", () => { CLS.vars[el.dataset.var] = el.value; paint(); }));
  $("#msgCopy").onclick = async () => { await copyText(paint()); toast(t("msg_copied")); };
}

// ================================================================ калькулятор
function drawCalc(body, c) {
  const id = c ? c.id : null;
  const st = calcState(id);
  if (c && !st.pkg_set && (c.package === "SMART" || c.package === "COMFORT")) st.pkg = c.package;
  const P = () => PRICE[st.pkg] || PRICE.SMART;
  const addonRow = (k, lblKey) => {
    const p = P().addons[k];
    return `<label class="chk-row"><input type="checkbox" data-addon="${k}" ${st.addons[k] ? "checked" : ""} ${p === 0 ? "disabled" : ""}>
      <span>${t(lblKey)}</span><b>${p === 0 ? esc(t("k_included")) : zl(p) + " zł"}</b></label>`;
  };
  body.innerHTML = `<div class="calc-grid">
    <section class="cl-card">
      <div class="flds">
        <label class="fld"><span>${t("k_rent")}</span><input data-k="rent" type="number" inputmode="decimal" value="${esc(st.rent)}"></label>
        <label class="fld"><span>${t("k_admin")}</span><input data-k="admin" type="number" value="${esc(st.admin)}"></label>
        <label class="fld"><span>${t("k_deposit")}</span><input data-k="deposit" type="number" value="${esc(st.deposit)}" placeholder="${esc(st.rent || "")}"></label>
        <label class="fld"><span>${t("k_owner_comm")}</span><input data-k="owner" type="number" value="${esc(st.owner || "")}" placeholder="0"></label>
        <label class="fld w2"><span>${t("k_package")}</span><div class="seg" id="kPkg">
          <button type="button" data-v="SMART" aria-pressed="${st.pkg === "SMART"}">SMART 70%</button>
          <button type="button" data-v="COMFORT" aria-pressed="${st.pkg === "COMFORT"}">COMFORT 100%</button>
          <button type="button" data-v="OWNER" aria-pressed="${st.pkg === "OWNER"}">${t("k_owner_pays")}</button></div></label>
      </div>
      <h3>${t("k_addons")}</h3>
      <div class="chks" id="kAdd">
        ${addonRow("okaz", "a_okaz")}${addonRow("pesel", "a_pesel")}${addonRow("meld", "a_meld")}${addonRow("bank", "a_bank")}
        <label class="chk-row"><input type="checkbox" data-flag="notary" ${st.notary ? "checked" : ""} ${P().notary === 0 ? "disabled" : ""}><span>${t("k_notary")}</span><b>${P().notary === 0 ? esc(t("k_included")) : zl(P().notary) + " zł"}</b></label>
        <label class="chk-row"><input type="checkbox" data-flag="translator" ${st.translator ? "checked" : ""}><span>${t("k_translator")}</span><b>${zl(TRANSLATOR)} zł</b></label>
        <label class="chk-row"><input type="checkbox" data-flag="repeat" ${st.repeat ? "checked" : ""} ${P().repeat ? "" : "disabled"}><span>${esc(t("k_repeat", { p: P().repeat }))}</span><b></b></label>
      </div>
    </section>
    <section class="cl-card calc-out" id="kOut"></section></div>`;
  const out = () => {
    const k = calc(st);
    const line = (lbl, v, cls) => `<div class="k-line ${cls || ""}"><span>${esc(lbl)}</span><b data-kv="${v}">${zl(v)} zł</b></div>`;
    $("#kOut").innerHTML = `<h3>${t("k_client_pays")}</h3>
      ${line(t("k_first"), k.first)}${line(t("k_dep"), k.deposit)}
      ${line(t("k_comm") + (k.pkg !== "OWNER" ? ` · ${k.pkg} ${k.pct}%${k.disc ? ` −${k.disc}%` : ""}` : ""), k.commission)}
      ${k.extra ? line(t("k_extra"), k.extra) : ""}
      <div class="k-total"><span>${t("k_total")}</span><b class="num" id="kTotal">${zl(k.total)} zł</b></div>
      ${k.notary ? line(t("k_at_notary"), k.notary, "muted") : ""}
      <div class="k-me"><div><span>${t("k_you")}</span><small>${esc(t("k_level", { p: k.level }))} · ${t("k_company")} ${zl(k.company)} zł</small></div><b class="num">${zl(k.mine)} zł</b></div>
      <div class="row-btns"><button class="btn ink" type="button" id="kCopy">${ICON.copy} ${t("k_copy")}</button></div>`;
    $("#kCopy").onclick = async () => {
      const lang = (c && c.lang) || (LANG === "uk" ? "ua" : LANG);
      const r = fillTpl(TPL[lang].s6[2], Object.assign(tplVals(lang), id ? {} : {}));
      await copyText(r.out); toast(t("msg_copied"));
    };
  };
  out();
  const save = () => { calcSave(id, st); out(); };
  body.querySelectorAll("[data-k]").forEach((el) => el.addEventListener("input", () => { st[el.dataset.k] = el.value; save(); }));
  $("#kPkg").onclick = (e) => {
    const b = e.target.closest("[data-v]"); if (!b) return;
    st.pkg = b.dataset.v; st.pkg_set = true; calcSave(id, st);
    if (c && b.dataset.v !== "OWNER" && c.package !== b.dataset.v) setField("package", b.dataset.v, true);
    drawCalc(body, c);
  };
  $("#kAdd").addEventListener("change", (e) => {
    const a = e.target.dataset.addon, f = e.target.dataset.flag;
    if (a) st.addons[a] = e.target.checked;
    if (f) st[f] = e.target.checked;
    save();
  });
  requestAnimationFrame(() => slideSeg($("#kPkg")));
}

// ================================================================ рынок
let MK = null, mkTimer = 0, mkSort = "m2";
async function marketOpen() {
  try { MK = await api("/api/market"); drawMarket(true); } catch (e) { toast(e.message, true); }
  clearTimeout(mkTimer);
  if (MK && MK.state && MK.state.state === "running") mkTimer = setTimeout(() => { if (SV.mode === "market") marketOpen(); }, 3000);
}
function pctHtml(p, inverse) {
  if (p == null) return `<span class="trend na">—</span>`;
  const up = p > 0.3, down = p < -0.3;
  return `<span class="trend ${up ? "up" : down ? "down" : "flat"}">${up ? "▲" : down ? "▼" : "•"} ${p > 0 ? "+" : ""}${p}%</span>`;
}
function spark(hist) {
  const ys = hist.map((h) => h.m2).filter((v) => v);
  if (ys.length < 2) return "";
  const mn = Math.min(...ys), mx = Math.max(...ys), W = 90, H = 24;
  const pts = hist.filter((h) => h.m2).map((h, i, a) => `${(i / (a.length - 1)) * W},${H - ((h.m2 - mn) / Math.max(mx - mn, 0.01)) * (H - 4) - 2}`).join(" ");
  return `<svg class="mk-spark" viewBox="0 0 ${W} ${H}"><polyline points="${pts}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
}
function drawMarket(first) {
  const box = $("#market"), d = MK;
  const run = d.state && d.state.state === "running";
  const dd = (s) => (s ? parseIso(s).toLocaleDateString(LOCALE[LANG], { day: "numeric", month: "long" }) : "");
  if (!d.districts.length) {
    box.innerHTML = `<div class="sv-wrap"><div class="cl-head"><div><h1 class="display">${t("mk_title")}</h1><p class="sv-sub">${t("mk_sub")}</p></div></div>
      <div class="mk-empty rise"><b>${t("mk_empty_t")}</b><p>${t("mk_empty")}</p>
      <button class="btn-primary" type="button" id="mkGo" ${run ? "disabled" : ""}>${run ? esc(t("mk_running", { n: d.state.done })) : t("mk_refresh")}</button></div></div>`;
    $("#mkGo").onclick = refreshMarket;
    return;
  }
  const c = d.city;
  const trendWord = c.w == null ? "" : c.w > 0.5 ? t("mk_up") : c.w < -0.5 ? t("mk_down") : t("mk_flat");
  const rows = d.districts.slice().sort((a, b) => mkSort === "name" ? a.name.localeCompare(b.name) : (b[mkSort] || 0) - (a[mkSort] || 0));
  const r = (x, k) => (x.rooms[k] ? zl(x.rooms[k].median) : "—");
  box.innerHTML = `<div class="sv-wrap">
    <div class="cl-head"><div><h1 class="display">${t("mk_title")}</h1>
      <p class="sv-sub"><span>${esc(t("mk_last", { d: dd(d.last) }))}</span><span>${esc(t("mk_since", { d: dd(d.since) }))}</span>${trendWord ? `<span class="today-pill">${esc(trendWord)}</span>` : ""}</p></div>
      <button class="btn" type="button" id="mkGo" ${run ? "disabled" : ""}>${ICON.refresh} ${run ? esc(t("mk_running", { n: d.state.done })) : t("mk_refresh")}</button></div>
    <div class="sv-summary">
      <div class="sv-stat rise" style="--i:0"><dt>${t("mk_m2")}</dt><dd><span data-tw="${c.m2 || 0}">${c.m2 || "—"}</span></dd><div class="mk-chg">${pctHtml(c.w)} <small>${t("mk_week")}</small> ${pctHtml(c.m)} <small>${t("mk_month")}</small></div></div>
      ${["1", "2", "3"].map((k, i) => `<div class="sv-stat rise" style="--i:${i + 1}"><dt>${t("mk_r" + k)}</dt><dd>${c.rooms[k] ? zl(c.rooms[k]) + "<small>zł</small>" : "—"}</dd></div>`).join("")}
    </div>
    <div class="sv-table-wrap rise" style="--i:4"><table class="sv-table mk-table"><thead><tr>
      <th class="rl" data-sort="name">${t("mk_district")}</th><th data-sort="n">${t("mk_n")}</th><th data-sort="median">${t("mk_median")}</th>
      <th data-sort="m2">zł/м²</th><th>1</th><th>2</th><th>3</th><th data-sort="w">${t("mk_week")}</th><th data-sort="m">${t("mk_month")}</th><th>${t("mk_trend")}</th></tr></thead>
      <tbody>${rows.map((x) => `<tr><td class="rl">${esc(x.name)}</td><td>${x.n || 0}</td><td class="fact">${zl(x.median)}</td><td class="fact">${x.m2 || "—"}</td>
        <td>${r(x, "1")}</td><td>${r(x, "2")}</td><td>${r(x, "3")}</td><td>${pctHtml(x.w)}</td><td>${pctHtml(x.m)}</td>
        <td>${spark(x.hist) || `<small class="hint">${t("mk_wait")}</small>`}</td></tr>`).join("")}</tbody></table></div></div>`;
  $("#mkGo").onclick = refreshMarket;
  box.querySelector("thead").onclick = (e) => { const h = e.target.closest("[data-sort]"); if (h) { mkSort = h.dataset.sort; drawMarket(); } };
}
async function refreshMarket() {
  try { await api("/api/market_refresh", {}); } catch (e) { toast(e.message, true); }
  marketOpen();
}

// ================================================================ настройки: имя, уровень, шаблон договора
function settingsExtra() {
  const pop = $("#pop");
  if ($("#setAgent")) return;
  const sec = document.createElement("section");
  sec.innerHTML = `<h4 data-i18n="set_agent"></h4><input class="pop-in" id="setAgent" type="text" maxlength="60">
    <h4 style="margin-top:14px" data-i18n="set_level"></h4>
    <div class="seg" id="segLevel">${[30, 40, 45, 50].map((p) => `<button type="button" data-lv="${p}">${p}%</button>`).join("")}</div>
    <h4 style="margin-top:14px" data-i18n="set_tpl"></h4>
    <div class="tpl-row"><span id="tplState"></span><button class="btn" type="button" id="tplBtn" data-i18n="set_tpl_btn"></button></div>
    <input type="file" id="tplFile" accept="application/pdf,.pdf" hidden>`;
  pop.insertBefore(sec, pop.lastElementChild);
  applyStatic();
  $("#setAgent").addEventListener("change", (e) => { api("/api/settings", { agent_name: e.target.value.trim() }).catch(() => {}); if (S.st) S.st.settings.agent_name = e.target.value.trim(); });
  $("#segLevel").onclick = (e) => {
    const b = e.target.closest("[data-lv]"); if (!b) return;
    const v = +b.dataset.lv; if (S.st) S.st.settings.agent_level = v;
    api("/api/settings", { agent_level: v }).catch(() => {});
    renderPop();
  };
  $("#tplBtn").onclick = () => $("#tplFile").click();
  $("#tplFile").onchange = async (e) => {
    const f = e.target.files[0]; e.target.value = "";
    if (!f) return;
    const r = await fetch("/api/contract_template", { method: "POST", headers: { "X-Hermea": T }, body: f });
    let d = {}; try { d = await r.json(); } catch (err) {}
    if (!r.ok) return toast(d.error || "HTTP " + r.status, true);
    CLS.template = true; toast(t("set_tpl_done")); renderPop();
  };
}
const _renderPop = renderPop;
renderPop = function () {        // eslint-disable-line no-func-assign
  _renderPop();
  settingsExtra();
  const s = (S.st && S.st.settings) || {};
  const a = $("#setAgent"); if (a && document.activeElement !== a) { a.value = s.agent_name || ""; a.placeholder = t("set_agent_ph"); }
  document.querySelectorAll("#segLevel button").forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.lv === (s.agent_level || 30))));
  const ts = $("#tplState");
  if (ts) { ts.textContent = CLS.template ? t("set_tpl_ok") : t("set_tpl_no"); ts.className = CLS.template ? "ok" : "bad"; }
};
api("/api/clients").then((d) => { CLS.template = d.template; }).catch(() => {});

// ================================================================ режимы
MODE_OPEN.clients = () => clientsOpen();
MODE_OPEN.market = () => marketOpen();
window.addEventListener("beforeunload", () => { if (Object.keys(CLS.pend).length) flushSave(); });
applyStatic();
if (SV.mode === "clients" || SV.mode === "market") setMode(SV.mode, true);


// ================================================================ подбор квартир под клиента
async function loadMatch() {
  const box = $("#clMatch"), c = CLS.c;
  if (!box || !c) return;
  const cid = c.id;
  if (!CLS.match || CLS.match.cid !== cid) { CLS.mpick = new Set(); box.innerHTML = `<h3>${t("mt_title")}</h3><p class="mt-empty">${t("mt_loading")}</p>`; }
  try {
    const r = await api("/api/match?id=" + encodeURIComponent(cid));
    if (!CLS.c || CLS.c.id !== cid) return;
    CLS.match = Object.assign(r, { cid });
    drawMatch();
    const fresh = r.items.filter((i) => i.new).map((i) => i.id);
    if (fresh.length) setTimeout(() => {
      if (!CLS.c || CLS.c.id !== cid) return;
      api("/api/match", { id: cid, seen: fresh }).catch(() => {});
      if (CLS.mnew[cid]) { delete CLS.mnew[cid]; drawList(); }
    }, 2500);
  } catch (e) { box.innerHTML = `<h3>${t("mt_title")}</h3><p class="mt-empty">${esc(e.message)}</p>`; }
}
function mtCrit(cr) {
  const out = [];
  if (cr.budget) out.push(t("mt_upto", { b: zl(cr.budget) }));
  if (cr.rooms && cr.rooms.length) out.push(t("mt_rooms", { r: cr.rooms.join("–") }));
  if (cr.districts && cr.districts.length) out.push(cr.districts.map((d) => MT_DIST[d] || d).join(", "));
  if (cr.area) out.push(t("mt_from", { a: cr.area }));
  if (cr.parking) out.push(t("mt_parking"));
  if (cr.pets) out.push(t("mt_pets"));
  return out.map((x) => `<span>${esc(x)}</span>`).join("");
}
const MT_DIST = { bemowo: "Bemowo", bialoleka: "Białołęka", bielany: "Bielany", mokotow: "Mokotów", ochota: "Ochota", "praga-polnoc": "Praga-Północ",
  "praga-poludnie": "Praga-Południe", rembertow: "Rembertów", srodmiescie: "Śródmieście", targowek: "Targówek", ursus: "Ursus", ursynow: "Ursynów",
  wawer: "Wawer", wesola: "Wesoła", wilanow: "Wilanów", wlochy: "Włochy", wola: "Wola", zoliborz: "Żoliborz" };
function mtRow(i) {
  const rooms = i.rooms ? t("mt_rooms", { r: i.rooms }) : "";
  const area = i.area ? Math.round(i.area) + " м²" : "";
  const who = i.agreed ? `<i class="mt-tag ok">${t("mt_agreed")}</i>` : i.private ? `<i class="mt-tag">${t("mt_owner")}</i>` : `<i class="mt-tag dim">${esc(i.agency || t("mt_agency"))}</i>`;
  const age = i.days == null ? "" : i.days <= 0 ? t("mt_today") : t("mt_days", { d: i.days });
  const on = CLS.mpick.has(i.id);
  return `<li class="mt-row${on ? " on" : ""}" data-mid="${esc(i.id)}">
    <label class="mt-chk"><input type="checkbox" ${on ? "checked" : ""} data-mpick="${esc(i.id)}" aria-label="✓"></label>
    ${i.img ? `<img class="mt-img" src="${esc(i.img)}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.style.visibility='hidden'">` : `<div class="mt-img"></div>`}
    <div class="mt-info">
      <div class="mt-t"><b>${esc(i.district || "")}${i.street ? ", " + esc(i.street) : ""}</b>${i.new ? `<i class="mt-new">${t("mt_new")}</i>` : ""}${i.src === "olx" ? `<i class="ow-src">OLX</i>` : ""}</div>
      <div class="mt-p"><b>${zl(i.total)} zł</b><span>${esc([rooms, area].filter(Boolean).join(" · "))}</span>${who}${age ? `<span class="hint">${esc(age)}</span>` : ""}</div>
    </div>
    <div class="mt-acts">
      <button class="btn sm" type="button" data-mact="open">${ICON.web} ${t("mt_open")}</button>
      <button class="btn sm" type="button" data-mact="photo">${t("mt_photo")}</button>
      <button class="icon-x sm" type="button" data-mact="skip" title="${esc(t("mt_skip"))}" aria-label="${esc(t("mt_skip"))}">×</button>
    </div></li>`;
}
function drawMatch() {
  const box = $("#clMatch"), m = CLS.match;
  if (!box || !m) return;
  const head = `<h3>${t("mt_title")}${m.total ? ` <small>${t("mt_of", { n: m.items.length, t: m.total })}</small>` : ""}
    <button class="text-btn" type="button" id="mtRef">${ICON.refresh} ${t("mt_refresh")}</button></h3>
    ${m.criteria ? `<div class="mt-crit">${mtCrit(m.criteria)}</div>` : ""}`;
  if (!m.items.length) {
    box.innerHTML = head + `<p class="mt-empty">${t(m.empty === "need" ? "mt_need" : "mt_none")}</p>`;
  } else {
    const n = CLS.mpick.size;
    box.innerHTML = head + `<ol class="mt-list">${m.items.map(mtRow).join("")}</ol>
      <div class="mt-foot"><button class="btn-primary" type="button" id="mtCopy" ${n ? "" : "disabled"}>${ICON.copy} ${t("mt_copy", { n })}</button>
        <label class="mt-links"><input type="checkbox" id="mtLinks" ${CLS.mlinks ? "checked" : ""}> ${t("mt_links")}</label>
        <span class="hint">${t("mt_pick")}</span></div>`;
  }
  $("#mtRef").onclick = () => loadMatch();
  box.onchange = (e) => {
    const p = e.target.closest("[data-mpick]");
    if (p) { p.checked ? CLS.mpick.add(p.dataset.mpick) : CLS.mpick.delete(p.dataset.mpick); drawMatch(); }
    if (e.target.id === "mtLinks") CLS.mlinks = e.target.checked;
  };
  box.onclick = async (e) => {
    const b = e.target.closest("[data-mact]"); if (!b) return;
    const id = b.closest("[data-mid]").dataset.mid, i = m.items.find((x) => x.id === id); if (!i) return;
    if (b.dataset.mact === "open") return api("/api/open", { what: "url", url: i.url }).catch(() => window.open(i.url, "_blank"));
    if (b.dataset.mact === "photo") {
      try { await api("/api/create", { text: i.url, force: false, telegram: true, no_fee: !!i.agreed }); toast(t("mt_photo_ok")); }
      catch (err) { toast(err.message, true); }
      return;
    }
    if (b.dataset.mact === "skip") {
      const li = b.closest(".mt-row"); li.classList.add("out");
      CLS.mpick.delete(id);
      await api("/api/match", { id: CLS.c.id, skip: id }).catch(() => {});
      setTimeout(loadMatch, 250);
    }
  };
  const cp = $("#mtCopy");
  if (cp) cp.onclick = async () => {
    const txt = mtText(m.items.filter((x) => CLS.mpick.has(x.id)));
    try { await navigator.clipboard.writeText(txt); toast(t("mt_copied")); } catch (err) { toast(err.message, true); }
  };
}
function mtText(list) {
  const lang = (CLS.c && CLS.c.lang) || "ua";
  const W = {
    ua: { hi: "Підібрав для вас кілька варіантів:", r: "кімн.", m: "/міс. разом з czynsz", end: "Який з них подивимось? Можу організувати перегляд найближчими днями." },
    ru: { hi: "Подобрал для вас несколько вариантов:", r: "комн.", m: "/мес. вместе с czynsz", end: "Какой из них посмотрим? Могу организовать просмотр в ближайшие дни." },
    pl: { hi: "Wybrałem dla Pana/Pani kilka propozycji:", r: "pok.", m: "/mies. razem z czynszem", end: "Które z nich chciałby Pan/chciałaby Pani zobaczyć? Mogę umówić oglądanie w najbliższych dniach." },
  }[lang] || null;
  const w = W || { hi: "Підібрав для вас кілька варіантів:", r: "кімн.", m: "/міс. разом з czynsz", end: "Який з них подивимось?" };
  const rows = list.map((i, k) => {
    const place = [i.district, i.street].filter(Boolean).join(", ");
    const parts = [i.rooms ? `${i.rooms} ${w.r}` : "", i.area ? `${Math.round(i.area)} м²` : ""].filter(Boolean).join(", ");
    return `${k + 1}. ${place}${parts ? `, ${parts}` : ""}, ${zl(i.total)} zł${w.m}${CLS.mlinks && i.url ? `\n${i.url}` : ""}`;
  });
  return `${w.hi}\n\n${rows.join("\n\n")}\n\n${w.end}`;
}
