"use strict";
/* Шаблоны сообщений клиенту — по «Скрипты для агентов Hermea» (оригинал UA), переводы RU и PL.
   {поле} заполняется из карточки клиента и калькулятора; пустое поле остаётся «___». */
const TPL_ORDER = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s10a", "s10b", "s10c"];
const TPL_VARS = {      // какие поля спросить в окне, если их нет в карточке
  s5: ["v_address", "v_date", "v_time", "v_price", "v_link"],
  s6: ["v_address", "v_date", "v_time"],
  s7: ["v_address", "v_date"],
};
const TPL = {
ua: {
  s1: ["Привітання", "Перше повідомлення новому клієнту",
`Доброго дня! Мене звати {agent}, я менеджер з нерухомості Hermea Real Estate. Із задоволенням допоможу Вам з пошуком житла 😊

Щоб уточнити Ваші побажання та умови співпраці, підкажіть, будь ласка, як Вам зручніше поспілкуватися — телефоном чи в текстовому форматі?
Якщо телефоном — напишіть, будь ласка, коли Вам буде зручно звʼязатися?`],
  s2: ["Що таке najem okazjonalny", "Коли клієнт питає про najem okazjonalny",
`Найм оказіональний (польськ. najem okazjonalny) — це особливий вид оренди, який забезпечує власнику додатковий захист та спрощує процедуру повернення житла у разі порушення умов договору.

Орендар оформлює у нотаріуса заяву про підпорядкування примусовому виконанню та вказує адресу в Польщі, куди зможе переїхати у разі необхідності звільнення квартири. Якщо орендар не має такої адреси, наше агентство може допомогти з оформленням адреси для najmu okazjonalnego.`],
  s3: ["Фіксація запиту", "Після розмови: критерії на підтвердження",
`Надсилаю узгоджені критерії Вашого пошуку, щоб зафіксувати запит та розпочати підбір відповідних варіантів.

• Склад проживаючих: {residents}
• Діти: {children}
• Домашні тварини: {pets}
• Тип обʼєкта: {type}
• Бажана площа: {area} м²
• Райони / локація: {location}
• Бажана дата заселення: {move_in}
• Термін оренди: {term}
• Бюджет: {budget} zł/міс.
• Паркінг: {parking}
• Сфера діяльності / джерело доходу: {income}
• Najem okazjonalny: {okazjonalny}
• Обраний пакет співпраці: {package}
• Обовʼязкові вимоги до квартири: {must}
• Що не розглядаємо: {not_considered}
• Додаткові побажання: {extra}

Будь ласка, перевірте інформацію та підтвердьте, що все зазначено правильно. Після підтвердження розпочинаємо підбір квартир відповідно до Вашого запиту 😊`],
  s4: ["Договір про співпрацю", "Перед першим переглядом",
`Перед першим переглядом, згідно з регламентом компанії, нам необхідно підписати договір про співпрацю з агенцією.

• Онлайн — надішліть, будь ласка, ПІБ, адресу проживання, PESEL та дані паспорта. Я підготую договір, а підписати його можна буде онлайн через Notatki.
• Офлайн — підпишемо договір перед переглядом, із собою потрібно мати паспорт.

Підкажіть, який варіант Вам зручніший? 😊`],
  s5: ["Підтвердження перегляду", "Коли перегляд узгоджено",
`Підтверджую перегляд квартири 🏠

📍 Адреса: {v_address}
📅 Дата: {v_date}
🕐 Час: {v_time}
💰 Вартість: {v_price}
🔗 Посилання на обʼєкт: {v_link}

Зустрічаємось за вказаною адресою. Буду чекати Вас на місці 😊`],
  s6: ["Підписання договору оренди", "Запрошення на підписання і ключі",
`Запрошую Вас на підписання договору оренди та передачі ключів 😊

📍 Адреса: {v_address}
📅 Дата: {v_date}
🕐 Час: {v_time}

З собою необхідно мати паспорт.

Оплати в день підписання:
• перший місяць оренди — {c_first} zł
• кауція — {c_deposit} zł
• послуги агентства, пакет {package} — {c_commission} zł{c_extra_ua}
Загальна сума: {c_total} zł

Комісію агентства можна оплатити на рахунок компанії, українську картку, криптовалютою або готівкою. Підкажіть, будь ласка, зручний для Вас спосіб оплати — я надішлю відповідні реквізити 😊`],
  s7: ["Нотаріус (najem okazjonalny)", "Запрошення до нотаріуса",
`Для підписання документів у нотаріуса, будь ласка, візьміть із собою:
• паспорт;
• оригінал договору оренди;
• 620 zł — оплата послуг нотаріуса
• 300 zł — оплата послуг перекладача

Документ із резервною адресою для najmu okazjonalnego я привезу на зустріч.

Зустрічаємось:
📍 Адреса: {v_address}
🕐 Дата та час: {v_date}

До зустрічі! 😊`],
  s10a: ["Недодзвон: 1-а спроба", "У день звернення",
`Добрий день! Мене звати {agent}, агентство нерухомості Hermea. Телефонував Вам щодо Вашого запиту на оренду житла. Підкажіть, коли Вам буде зручно поговорити? Можу також відповісти на всі питання в переписці.`],
  s10b: ["Недодзвон: 2-а спроба", "Наступного робочого дня",
`Добрий день, {client}! Це {agent} з агентства Hermea. Не вдалося з Вами звʼязатися. У мене вже є кілька варіантів, які можуть Вам підійти. Напишіть, будь ласка, чи актуальний ще пошук житла?`],
  s10c: ["Недодзвон: фінальна", "Через два робочі дні",
`Добрий день, {client}! Відповіді від Вас не отримав, тому поки ставлю Ваш запит на паузу. Якщо пошук житла знову стане актуальним, напишіть мені — одразу продовжимо роботу. Гарного дня!`],
},
ru: {
  s1: ["Приветствие", "Первое сообщение новому клиенту",
`Добрый день! Меня зовут {agent}, я менеджер по недвижимости Hermea Real Estate. С удовольствием помогу Вам с поиском жилья 😊

Чтобы уточнить Ваши пожелания и условия сотрудничества, подскажите, пожалуйста, как Вам удобнее пообщаться — по телефону или в переписке?
Если по телефону — напишите, пожалуйста, когда Вам будет удобно связаться?`],
  s2: ["Что такое najem okazjonalny", "Когда клиент спрашивает про najem okazjonalny",
`Najem okazjonalny — это особый вид аренды, который даёт собственнику дополнительную защиту и упрощает возврат жилья, если условия договора нарушены.

Арендатор оформляет у нотариуса заявление о добровольном подчинении принудительному исполнению и указывает адрес в Польше, куда сможет переехать, если понадобится освободить квартиру. Если у арендатора нет такого адреса, наше агентство поможет с оформлением адреса для najmu okazjonalnego.`],
  s3: ["Фиксация запроса", "После разговора: критерии на подтверждение",
`Отправляю согласованные критерии Вашего поиска, чтобы зафиксировать запрос и начать подбор подходящих вариантов.

• Состав проживающих: {residents}
• Дети: {children}
• Домашние животные: {pets}
• Тип объекта: {type}
• Желаемая площадь: {area} м²
• Районы / локация: {location}
• Желаемая дата заселения: {move_in}
• Срок аренды: {term}
• Бюджет: {budget} zł/мес.
• Паркинг: {parking}
• Сфера деятельности / источник дохода: {income}
• Najem okazjonalny: {okazjonalny}
• Выбранный пакет сотрудничества: {package}
• Обязательные требования к квартире: {must}
• Что не рассматриваем: {not_considered}
• Дополнительные пожелания: {extra}

Пожалуйста, проверьте информацию и подтвердите, что всё указано верно. После подтверждения начинаем подбор квартир по Вашему запросу 😊`],
  s4: ["Договор о сотрудничестве", "Перед первым просмотром",
`Перед первым просмотром, согласно регламенту компании, нам нужно подписать договор о сотрудничестве с агентством.

• Онлайн — пришлите, пожалуйста, ФИО, адрес проживания, PESEL и данные паспорта. Я подготовлю договор, подписать его можно будет онлайн через Notatki.
• Офлайн — подпишем договор перед просмотром, с собой нужно иметь паспорт.

Подскажите, какой вариант Вам удобнее? 😊`],
  s5: ["Подтверждение просмотра", "Когда просмотр согласован",
`Подтверждаю просмотр квартиры 🏠

📍 Адрес: {v_address}
📅 Дата: {v_date}
🕐 Время: {v_time}
💰 Стоимость: {v_price}
🔗 Ссылка на объект: {v_link}

Встречаемся по указанному адресу. Буду ждать Вас на месте 😊`],
  s6: ["Подписание договора аренды", "Приглашение на подписание и ключи",
`Приглашаю Вас на подписание договора аренды и передачу ключей 😊

📍 Адрес: {v_address}
📅 Дата: {v_date}
🕐 Время: {v_time}

С собой нужно иметь паспорт.

Оплаты в день подписания:
• первый месяц аренды — {c_first} zł
• залог (kaucja) — {c_deposit} zł
• услуги агентства, пакет {package} — {c_commission} zł{c_extra_ru}
Общая сумма: {c_total} zł

Комиссию агентства можно оплатить на счёт компании, украинскую карту, криптовалютой или наличными. Подскажите, пожалуйста, удобный для Вас способ оплаты — я пришлю реквизиты 😊`],
  s7: ["Нотариус (najem okazjonalny)", "Приглашение к нотариусу",
`Для подписания документов у нотариуса, пожалуйста, возьмите с собой:
• паспорт;
• оригинал договора аренды;
• 620 zł — оплата услуг нотариуса
• 300 zł — оплата услуг переводчика

Документ с резервным адресом для najmu okazjonalnego я привезу на встречу.

Встречаемся:
📍 Адрес: {v_address}
🕐 Дата и время: {v_date}

До встречи! 😊`],
  s10a: ["Недозвон: 1-я попытка", "В день обращения",
`Добрый день! Меня зовут {agent}, агентство недвижимости Hermea. Звонил Вам по Вашему запросу на аренду жилья. Подскажите, когда Вам будет удобно поговорить? Могу также ответить на все вопросы в переписке.`],
  s10b: ["Недозвон: 2-я попытка", "На следующий рабочий день",
`Добрый день, {client}! Это {agent} из агентства Hermea. Не получилось с Вами связаться. У меня уже есть несколько вариантов, которые могут Вам подойти. Напишите, пожалуйста, актуален ли ещё поиск жилья?`],
  s10c: ["Недозвон: финальная", "Через два рабочих дня",
`Добрый день, {client}! Ответа от Вас не получил, поэтому пока ставлю Ваш запрос на паузу. Если поиск жилья снова станет актуальным, напишите мне — сразу продолжим работу. Хорошего дня!`],
},
pl: {
  s1: ["Powitanie", "Pierwsza wiadomość do nowego klienta",
`Dzień dobry! Nazywam się {agent}, jestem doradcą ds. nieruchomości w Hermea Real Estate. Chętnie pomogę Panu/Pani w znalezieniu mieszkania 😊

Aby doprecyzować oczekiwania i warunki współpracy, proszę dać znać, jaka forma kontaktu będzie wygodniejsza — telefon czy wiadomości?
Jeśli telefon — proszę napisać, kiedy mogę zadzwonić.`],
  s2: ["Czym jest najem okazjonalny", "Gdy klient pyta o najem okazjonalny",
`Najem okazjonalny to szczególna forma najmu, która daje właścicielowi dodatkową ochronę i ułatwia odzyskanie mieszkania w razie naruszenia umowy.

Najemca składa u notariusza oświadczenie o poddaniu się egzekucji i wskazuje adres w Polsce, pod który może się przeprowadzić w razie konieczności opuszczenia lokalu. Jeśli najemca nie ma takiego adresu, nasza agencja może pomóc w zapewnieniu adresu do najmu okazjonalnego.`],
  s3: ["Potwierdzenie kryteriów", "Po rozmowie: kryteria do potwierdzenia",
`Przesyłam uzgodnione kryteria wyszukiwania, aby potwierdzić zapytanie i rozpocząć dobór ofert.

• Liczba osób: {residents}
• Dzieci: {children}
• Zwierzęta: {pets}
• Rodzaj nieruchomości: {type}
• Powierzchnia: {area} m²
• Dzielnice / lokalizacja: {location}
• Data wprowadzenia: {move_in}
• Okres najmu: {term}
• Budżet: {budget} zł/mies.
• Parking: {parking}
• Branża / źródło dochodu: {income}
• Najem okazjonalny: {okazjonalny}
• Wybrany pakiet: {package}
• Wymagania obowiązkowe: {must}
• Czego nie rozważamy: {not_considered}
• Dodatkowe życzenia: {extra}

Proszę sprawdzić informacje i potwierdzić, że wszystko się zgadza. Po potwierdzeniu zaczynamy dobór mieszkań 😊`],
  s4: ["Umowa współpracy", "Przed pierwszą prezentacją",
`Przed pierwszą prezentacją, zgodnie z regulaminem firmy, musimy podpisać umowę współpracy z agencją.

• Online — proszę przesłać imię i nazwisko, adres zamieszkania, PESEL i dane paszportu. Przygotuję umowę, którą można podpisać online przez Notatki.
• Na miejscu — podpiszemy umowę przed prezentacją, proszę mieć ze sobą paszport.

Która opcja będzie wygodniejsza? 😊`],
  s5: ["Potwierdzenie prezentacji", "Gdy prezentacja jest umówiona",
`Potwierdzam prezentację mieszkania 🏠

📍 Adres: {v_address}
📅 Data: {v_date}
🕐 Godzina: {v_time}
💰 Cena: {v_price}
🔗 Link do oferty: {v_link}

Spotykamy się pod wskazanym adresem. Będę czekać na miejscu 😊`],
  s6: ["Podpisanie umowy najmu", "Zaproszenie na podpisanie i klucze",
`Zapraszam na podpisanie umowy najmu i przekazanie kluczy 😊

📍 Adres: {v_address}
📅 Data: {v_date}
🕐 Godzina: {v_time}

Proszę mieć ze sobą paszport.

Płatności w dniu podpisania:
• pierwszy miesiąc najmu — {c_first} zł
• kaucja — {c_deposit} zł
• usługi agencji, pakiet {package} — {c_commission} zł{c_extra_pl}
Razem: {c_total} zł

Prowizję agencji można zapłacić przelewem na konto firmy, ukraińską kartą, kryptowalutą lub gotówką. Proszę dać znać, jaka forma płatności będzie wygodna — prześlę dane 😊`],
  s7: ["Notariusz (najem okazjonalny)", "Zaproszenie do notariusza",
`Do podpisania dokumentów u notariusza proszę zabrać:
• paszport;
• oryginał umowy najmu;
• 620 zł — opłata notarialna
• 300 zł — opłata za tłumacza

Dokument z adresem do najmu okazjonalnego przywiozę na spotkanie.

Spotykamy się:
📍 Adres: {v_address}
🕐 Data i godzina: {v_date}

Do zobaczenia! 😊`],
  s10a: ["Brak kontaktu: 1. próba", "W dniu zgłoszenia",
`Dzień dobry! Nazywam się {agent}, agencja nieruchomości Hermea. Dzwoniłem w sprawie zapytania o wynajem mieszkania. Kiedy będzie Panu/Pani wygodnie porozmawiać? Mogę też odpowiedzieć na wszystkie pytania w wiadomościach.`],
  s10b: ["Brak kontaktu: 2. próba", "Następnego dnia roboczego",
`Dzień dobry, {client}! Tu {agent} z agencji Hermea. Nie udało mi się dodzwonić. Mam już kilka ofert, które mogą Panu/Pani odpowiadać. Czy poszukiwanie mieszkania jest nadal aktualne?`],
  s10c: ["Brak kontaktu: ostatnia", "Po dwóch dniach roboczych",
`Dzień dobry, {client}! Nie otrzymałem odpowiedzi, więc na razie wstrzymuję zapytanie. Jeśli poszukiwanie mieszkania znów będzie aktualne, proszę napisać — od razu wrócimy do pracy. Miłego dnia!`],
},
};
