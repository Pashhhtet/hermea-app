"""Быстрые проверки отдельных частей (без сети и без окна, меньше секунды).

    python3 tools/test_units.py   -> «UNITS OK» или список ошибок, код выхода 1
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "program"))

import app_calls  # noqa: E402
import app_copies  # noqa: E402
import app_i18n  # noqa: E402
import app_match  # noqa: E402
import app_owners  # noqa: E402
import app_searches  # noqa: E402
import logos  # noqa: E402
import otodom_text  # noqa: E402

# консоль Windows (cp1252) не печатает кириллицу и польские буквы
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

FAILS = []


def eq(name, got, want):
    if got != want:
        FAILS.append(name)
        print(f"FAIL {name}: получили {got!r}, ждали {want!r}")


# ---------------------------------------------------------------- перезвоны: даты и телефоны
WED = dt.date(2026, 11, 25)                      # среда
eq("дата: завтра", app_calls.parse_date("перезвонить завтра", WED), dt.date(2026, 11, 26))
eq("дата: в пятницу", app_calls.parse_date("в пятницу", WED), dt.date(2026, 11, 27))
eq("дата: у пʼятницю", app_calls.parse_date("у п'ятницю", WED), dt.date(2026, 11, 27))
eq("дата: w poniedziałek", app_calls.parse_date("w poniedziałek", WED), dt.date(2026, 11, 30))
eq("дата: через 3 дня", app_calls.parse_date("через 3 дня", WED), dt.date(2026, 11, 28))
eq("дата: 2.12", app_calls.parse_date("2.12", WED), dt.date(2026, 12, 2))
eq("дата: нет", app_calls.parse_date("просто заметка", WED), None)
eq("телефон +48", app_calls.norm_phone("+48 535 016 721"), "535016721")
eq("телефон красиво", app_calls.pretty_phone("0048535016721"), "535 016 721")
url, phone, _, note = app_calls.split_text("https://www.otodom.pl/pl/oferta/x-ID4D1uR 535 016 721 хочет 50%")
eq("вставка: ссылка", url, "https://www.otodom.pl/pl/oferta/x-ID4D1uR")
eq("вставка: телефон", app_calls.norm_phone(phone), "535016721")

# ---------------------------------------------------------------- подбор квартир
eq("районы ru", app_match.districts_of("Мокотув, Вола"), {"mokotow", "wola"})
eq("районы центр", app_match.districts_of("центр"), {"srodmiescie"})
eq("районы Прага", app_match.districts_of("Praga"), {"praga-polnoc", "praga-poludnie"})
eq("районы без ложных", app_match.districts_of("волонтёр, любой"), set())
eq("комнаты 2-3", app_match.rooms_of("2-3 комнаты"), {"2", "3"})
eq("комнаты kawalerka", app_match.rooms_of("kawalerka"), {"1"})
eq("комнаты двушка", app_match.rooms_of("двушка"), {"2"})
eq("комнаты пусто", app_match.rooms_of(""), set())
pool = [{"id": "a", "url": "https://x/a", "total": 4300, "rooms": "2", "district": "Mokotów", "area": 45},
        {"id": "b", "url": "https://x/b", "total": 5200, "rooms": "2", "district": "Mokotów", "area": 45},
        {"id": "c", "url": "https://x/c", "total": 4300, "rooms": "2", "district": "Mokotów", "area": 45},
        {"id": "d", "url": "https://x/d", "total": 4000, "rooms": "3", "district": "Mokotów", "area": 60}]
r = app_match.match({"budget": "4500", "location": "Мокотув", "type": "2 комнаты"}, [(pool[:2], "market"), (pool[2:], "owner")])
eq("подбор: дубль одной квартиры один раз, версия собственника", [i["id"] for i in r["items"]], ["c"])
eq("комнаты: кавалерка по-русски", app_match.rooms_of("Кавалерка"), {"1"})
eq("комнаты: поле «Комнаты» важнее типа", app_match.criteria({"rooms": "2–3 кімнати", "type": "kawalerka"})["rooms"], ["2", "3"])
eq("комнаты: без поля — из типа", app_match.criteria({"type": "двушка"})["rooms"], ["2"])
eq("подбор: без запроса", app_match.match({"name": "x"}, [(pool, "market")])["empty"], "need")
eq("подбор: просмотренное не показываем",
   app_match.match({"budget": "4500", "viewed": [{"link": "https://x/c"}], "match_skip": ["a"]}, [(pool, "owner")])["total"], 1)

# ---------------------------------------------------------------- OLX
P = lambda k, v: {"key": k, "value": v}  # noqa: E731
olx = {"data": [
    {"id": 1, "url": "u1", "title": "Kawalerka Ursynów", "created_time": "2026-10-10T10:00", "pushup_time": "2026-11-24T10:00",
     "description": "Bez pośredników<br/>proszę", "promotion": {"top_ad": True}, "business": False, "user": {"id": 7, "name": "M"},
     "params": [P("price", {"value": 2399}), P("m", {"key": "32"}), P("rooms", {"key": "one"}), P("rent", {"key": "790"})],
     "location": {"district": {"name": "Ursynów"}}, "photos": [{"link": "https://i.olxcdn.com:443/v1/x/image;s={width}x{height}"}]},
    {"id": 2, "title": "Apartament", "business": False, "external_url": "https://www.otodom.pl/pl/oferta/a-ID1", "params": []},
    {"id": 3, "title": "Lokal usługowy", "business": False, "params": []},
    {"id": 4, "title": "Mieszkanie", "business": True, "params": []}]}
items = app_owners.parse_olx(olx, "2026-11-25")
eq("OLX: только квартиры частников без копий Otodom", [i["id"] for i in items], ["olx-1"])
i = items[0]
eq("OLX: цена с czynsz", (i["price"], i["rent"], i["total"], i["rooms"]), (2399, 790, 3189, "1"))
eq("OLX: фото", i["img"], "https://i.olxcdn.com/v1/x/image;s=640x480")
eq("OLX: платное поднятие", (i["pushed"], i["promoted"]), ("2026-11-24", True))
eq("OLX: «без посредников» видно", app_owners._desc_detail(i["_desc"], "2026-11-25")["neg"], True)
eq("без улицы нет отпечатка", app_owners._print({"street": "", "area": 30, "rooms": "1"}), None)

# ---------------------------------------------------------------- тексты и поиски
info = {"title": "Mieszkanie", "rooms": "2", "area": "45", "district": "Mokotów", "street": "Puławska", "price": 4000,
        "rent": 500, "floor": "3", "floors": "5", "equipment": [], "desc": ""}
t = otodom_text.title(info)
eq("заголовок Otodom ≤ 70 и без провизии", (len(t) <= 70, t.endswith("bez prowizji")), (True, True))
eq("описание Otodom: без провизии", "bez prowizji" in otodom_text.build(info).lower(), True)
s = {"seen": ["2"]}
dup = [{"id": "1", "title": "Mieszkanie 2 pok", "price": 4000, "area": 45, "street": "Puławska"},
       {"id": "2", "title": "Mieszkanie 2 pok", "price": 4000, "area": 45, "street": "Puławska"}]
eq("поиск: дубль убран, остаётся просмотренный", [x["id"] for x in app_searches._dedupe(s, dup)], ["2"])

# ---------------------------------------------------------------- «Другое агентство»: поиск логотипа
import cv2  # noqa: E402
import numpy as np  # noqa: E402

rng = np.random.default_rng(7)


def room(seed):
    """Разные «комнаты»: случайные стены, мебель, линии — у каждого фото свои."""
    r = np.random.default_rng(seed)
    im = np.full((960, 1280, 3), r.integers(150, 235, 3), np.uint8)
    for _ in range(14):
        x, y = int(r.integers(0, 1200)), int(r.integers(0, 900))
        cv2.rectangle(im, (x, y), (x + int(r.integers(60, 400)), y + int(r.integers(40, 300))),
                      tuple(int(v) for v in r.integers(30, 255, 3)), -1)
    for _ in range(10):
        cv2.line(im, tuple(int(v) for v in r.integers(0, 1280, 2)), tuple(int(v) for v in r.integers(0, 960, 2)),
                 tuple(int(v) for v in r.integers(0, 255, 3)), int(r.integers(2, 8)))
    return cv2.GaussianBlur(im, (0, 0), 1.2)


def stamp(im):
    ov = im.copy()
    cv2.circle(ov, (1040, 90), 34, (255, 255, 255), -1)
    cv2.putText(ov, "AGENCJA", (1085, 105), cv2.FONT_HERSHEY_DUPLEX, 1.1, (255, 255, 255), 3, cv2.LINE_AA)
    return cv2.addWeighted(ov, 0.6, im, 0.4, 0)


clean = [room(s) for s in range(5)]
eq("логотип: на разных фото без логотипа ничего не находим", [m is None for m in logos.find_masks(clean)], [True] * 5)
ms = logos.find_masks([stamp(i) for i in clean])
logo = np.zeros((960, 1280), np.uint8)
cv2.circle(logo, (1040, 90), 34, 255, -1)
cv2.putText(logo, "AGENCJA", (1085, 105), cv2.FONT_HERSHEY_DUPLEX, 1.1, 255, 3, cv2.LINE_AA)
m = ms[0] if ms[0] is not None else np.zeros_like(logo)
cover = float((m[logo > 0] > 0).mean())
extra = float(((m > 0) & (cv2.dilate(logo, np.ones((61, 61), np.uint8)) == 0)).mean())
eq("логотип: найден почти весь (≥ 90%)", cover >= 0.9, True)
eq("логотип: лишнего почти нет (< 0.5% фото)", extra < 0.005, True)
eq("логотип: 2 фото мало — не ищем", logos.find_masks([stamp(i) for i in clean[:2]]), [None, None])


# ---------------------------------------------------------------- та же квартира у агентств
yy, xx = np.mgrid[0:240, 0:320]
pic = np.zeros((240, 320, 3))
pic[..., 2], pic[..., 1], pic[..., 0] = (xx * 7 + yy * 3) % 256, (xx * yy) % 256, ((xx ^ yy) * 5) % 256
# то же значение считает окно браузера, на котором подбирали порог (проверено вручную)
eq("копии: хеш фото как при подборе порога", app_copies.dhash_array(pic),
   "552c0aaaaaaaaa355555555550caaaaaaaaaaa55555555551aaaaaaaaaa9e555")
room = np.zeros((480, 640, 3), np.uint8)
rng = np.random.default_rng(1)
for _ in range(30):
    c = tuple(int(v) for v in rng.integers(0, 255, 3))
    cv2.rectangle(room, tuple(int(v) for v in rng.integers(0, 640, 2)), tuple(int(v) for v in rng.integers(0, 640, 2)), c, -1)
room = cv2.GaussianBlur(room, (9, 9), 0)
h0 = app_copies.dhash(cv2.imencode(".jpg", cv2.resize(room, (320, 240)), [cv2.IMWRITE_JPEG_QUALITY, 85])[1].tobytes())
copy = room.copy()
cv2.putText(copy, "AGENCJA", (420, 460), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)     # копия с логотипом
h1 = app_copies.dhash(cv2.imencode(".jpg", cv2.resize(copy, (320, 240)), [cv2.IMWRITE_JPEG_QUALITY, 60])[1].tobytes())
h2 = app_copies.dhash(cv2.imencode(".jpg", cv2.resize(cv2.flip(room, 0), (320, 240)))[1].tobytes())
eq("копии: то же фото с логотипом агентства — близко", app_copies.distance(h0, h1) <= app_copies.PHOTO_MAX, True)
eq("копии: другое фото — далеко", app_copies.distance(h0, h2) > app_copies.PHOTO_MAX + 20, True)
eq("копии: улица без «ul.», номера и диакритики", app_copies.street_key("ul. Bukowińskiej 22"), "bukowinskiej")
eq("копии: та же улица в другом падеже и без имени", (app_copies.same_street("ul. Bukowińska", "Bukowińskiej 22"),
   app_copies.same_street("ul. Jana Pawła Woronicza", "Woronicza 15"), app_copies.same_street("Kolska", "Kolejowa"),
   app_copies.same_street("", "Kolska")), (True, True, False, None))
eq("копии: ссылка на маленькое фото", app_copies.small("https://x.olxcdn.com/v1/f/image;s=640x480"), "https://x.olxcdn.com/v1/f/image;s=320x240")
own = {"id": "1", "district": "Mokotów", "rooms": "3", "area": 80, "price": 6000, "street": "ul. Bukowińska", "floor": "SEVENTH"}
eq("копии: поиск Otodom с фильтрами", app_copies.otodom_url(dict(own, district="Praga-Południe")),
   "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa/praga--poludnie"
   "?limit=72&roomsNumber=%5BTHREE%5D&areaMin=79&areaMax=81&priceMin=5100&priceMax=6900")
eq("копии: поиск OLX среди бизнеса", "owner_type=business" in app_copies.olx_url(own) and "filter_enum_rooms%5B0%5D=three" in app_copies.olx_url(own), True)
cands = [dict(id="a", src="otodom", url="ua", agency="A", price=6200, area=80, rooms="3", street="Bukowińska 22", floor="SEVENTH", district="Mokotów"),
         dict(id="b", src="otodom", url="ub", agency="B", price=5900, area=80, rooms="3", street="Bukowińska", floor="SECOND", district="Mokotów"),
         dict(id="c", src="otodom", url="uc", agency="C", price=6000, area=80, rooms="3", street="Puławska", floor="SEVENTH", district="Mokotów"),
         dict(id="d", src="olx", url="ud", agency="Hermea Real Estate", price=6000, area=80, rooms="3", street="", floor="", district="Mokotów"),
         dict(id="e", src="olx", url="ue", agency="E", price=6000, area=80, rooms="3", street="", floor="", district="Wola")]
ph = {"a": [h2], "b": [h2], "c": [h0], "d": [h1], "e": [h0]}
got = app_copies.compare(own, cands, [h0], lambda c: ph[c["id"]])
eq("копии: улица+этаж+площадь или фото; чужая улица, другой этаж и другой район — нет",
   sorted((c["url"], c["how"], c["ours"]) for c in got), [("ua", "place", False), ("ud", "photo", True)])
a = {"why": [], "copies": {"items": got}}
eq("копии: «уже у нас» не агентство; только улица и этаж — «похоже»",
   [w for w in app_owners.score(a, "2026-11-25")[1] if w[0].startswith("agency")], [["agency_maybe", 1]])
a = {"why": [], "copies": {"items": [dict(next(c for c in got if not c["ours"]), how="photo")]}}
eq("копии: те же фото — с агентствами работает", [w for w in app_owners.score(a, "2026-11-25")[1] if w[0].startswith("agency")], [["agency", 1]])
otod = {"data": {"searchAds": {"items": [
    {"id": 5, "slug": "x-ID5", "isPrivateOwner": False, "areaInSquareMeters": 80, "roomsNumber": "THREE", "totalPrice": {"value": 6100},
     "floorNumber": "SEVENTH", "agency": {"name": "Two Steps"}, "images": [{"url": "https://i/1;s=184x138"}],
     "location": {"address": {"street": {"name": "ul. Bukowińska"}}}},
    {"id": 6, "slug": "y-ID6", "isPrivateOwner": True}]}}}
po = app_copies.parse_otodom(otod)
eq("копии: из поиска Otodom только агентства", [(c["id"], c["agency"], c["floor"], c["street"]) for c in po], [("5", "Two Steps", "SEVENTH", "Bukowińska")])
ol = app_copies.parse_olx({"data": [
    {"id": 9, "url": "u9", "params": [P("price", {"value": 6000}), P("m", {"key": "80"}), P("rooms", {"key": "three"})],
     "location": {"district": {"name": "Mokotów"}}, "user": {"name": "Biuro"}, "photos": [{"link": "https://i/{width}x{height}"}]},
    {"id": 10, "external_url": "https://www.otodom.pl/pl/oferta/z-ID1"}]})
eq("копии: из OLX без копий Otodom", [(c["id"], c["price"], c["area"], c["rooms"]) for c in ol], [("olx-9", 6000, 80, "3")])

# ---------------------------------------------------------------- переводы сервера
for k, v in app_i18n.MSG.items():
    if set(v) != {"ru", "uk", "pl"} or not all(v.values()):
        FAILS.append("перевод " + k)
        print("FAIL перевод", k, sorted(v))

print("UNITS OK" if not FAILS else f"UNITS: ошибок {len(FAILS)}")
sys.exit(1 if FAILS else 0)
