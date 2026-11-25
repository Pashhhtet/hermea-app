"""Та же квартира у агентств: для частного объявления ищем копии на Otodom и OLX.

Как ищем (на одно объявление 2 запроса поиска + маленькие картинки с CDN):
  1. Otodom: тот же район, те же комнаты, площадь ±1 м², цена ±15 % — берём только не частные объявления.
  2. OLX: то же по всей Варшаве среди бизнес-объявлений, затем оставляем тот же район;
     копии с Otodom пропускаем (их уже видно в п. 1).
Две степени уверенности:
  - how="photo": совпали фото (dHash 16×16 по первым трём фото, расстояние ≤ PHOTO_MAX) — та же квартира;
  - how="place": фото разные, но совпали улица, комнаты, этаж и площадь (±0,5 м²) — скорее всего та же,
    агентство пересняло; бывает и соседняя квартира в новостройке, поэтому агент сверяет по ссылке.
Проверено на 1642 парах из Праги-Южной, Мокотова и Воли (ноябрь 2026): у копий расстояние фото 5–58,
у разных квартир — от 80; на 12 объявлениях без копий ложных совпадений нет. Совместимо с Python 3.9.
"""
import math
import re
import time
import unicodedata
from urllib.parse import quote

import app_market

PHOTO_MAX = 60           # из 256 бит; разные квартиры начинаются примерно с 80
AREA_TOL = 1.0           # для поиска
PRICE_TOL = 0.15
MAX_CMP = 10             # сколько кандидатов сравниваем по фото
OTO = ("https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa/{d}"
       "?limit=72&roomsNumber=%5B{r}%5D&areaMin={a0}&areaMax={a1}&priceMin={p0}&priceMax={p1}")
OLX = ("https://www.olx.pl/api/v1/offers/?offset=0&limit=50&category_id=15&city_id=17871&owner_type=business"
       "&filter_float_m:from={a0}&filter_float_m:to={a1}&filter_float_price:from={p0}&filter_float_price:to={p1}{r}")
OTO_ROOMS = {"1": "ONE", "2": "TWO", "3": "THREE", "4": "FOUR", "5": "FIVE", "6": "SIX"}
OLX_ROOMS = {"1": "one", "2": "two", "3": "three", "4": "four"}
_HASHES = {}             # url картинки -> hex (в памяти, на время работы программы)


# ---------------------------------------------------------------- фото
def dhash(img_bytes):
    """Картинка (jpeg/png) -> 64 hex-символа: градиент яркости по сетке 17×16, средним по блокам."""
    import cv2
    import numpy as np
    im = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    if im is None:
        raise ValueError("bad image")
    return dhash_array(im)


def dhash_array(im):
    import numpy as np
    g = im[..., 2] * 0.299 + im[..., 1] * 0.587 + im[..., 0] * 0.114     # BGR -> яркость
    h, w = g.shape
    ys = [int(i * h // 16) for i in range(17)]
    xs = [int(i * w // 17) for i in range(18)]
    L = np.empty((16, 17))
    for by in range(16):
        for bx in range(17):
            L[by, bx] = g[ys[by]:ys[by + 1], xs[bx]:xs[bx + 1]].mean()
    bits = (L[:, :-1] > L[:, 1:]).flatten()
    return "%064x" % int("".join("1" if b else "0" for b in bits), 2)


def distance(h1, h2):
    return bin(int(h1, 16) ^ int(h2, 16)).count("1")


def small(url):
    """Ссылка на картинку 320×240 (Otodom и OLX раздают с одного CDN)."""
    if not url:
        return ""
    if "{width}" in url:
        return url.replace(":443", "").replace("{width}x{height}", "320x240")
    return url.split(";")[0] + ";s=320x240"


def _hash_url(sess, url):
    u = small(url)
    if u in _HASHES:
        return _HASHES[u]
    r = sess.get(u, timeout=30)
    r.raise_for_status()
    h = dhash(r.content)
    if len(_HASHES) > 5000:
        _HASHES.clear()
    _HASHES[u] = h
    return h


def _hashes(sess, urls):
    out = []
    for u in (urls or [])[:3]:
        try:
            out.append(_hash_url(sess, u))
        except Exception:
            pass
    return out


def photo_distance(ha, hb):
    return min((distance(x, y) for x in ha for y in hb), default=None)


# ---------------------------------------------------------------- признаки
def street_key(s):
    s = unicodedata.normalize("NFKD", (s or "").replace("ł", "l").replace("Ł", "L"))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower().strip()
    s = re.sub(r"^(ul\.?|ulica|al\.?|aleja|pl\.?|plac|os\.?|osiedle)\s+", "", s)
    s = re.sub(r"\s*\d.*$", "", s)                     # номер дома и всё после
    return re.sub(r"[^a-z]+", " ", s).strip()


def same_street(s1, s2):
    """True/False, или None если у одного улица не указана. Сравниваем последнее слово без окончания:
    «Jana Pawła Woronicza» = «Woronicza», «Bukowińska» = «Bukowińskiej»."""
    a, b = street_key(s1).split(), street_key(s2).split()
    if not a or not b:
        return None
    x, y = a[-1], b[-1]
    n = min(len(x), len(y))
    k = n - 3 if n > 7 else n
    return x[:k] == y[:k]


def same_place(a, b):
    """Та же улица, комнаты, этаж и площадь — у соседей по этажу площадь почти никогда не совпадает до 0,5 м²."""
    fa, fb = a.get("floor") or "", b.get("floor") or ""
    if not same_street(a.get("street"), b.get("street")) or str(a.get("rooms") or "") != str(b.get("rooms") or ""):
        return False
    if not fa or fa != fb or fa == "ABOVE_TENTH":
        return False
    try:
        return abs(float(a.get("area")) - float(b.get("area"))) <= 0.5
    except (TypeError, ValueError):
        return False


def _bounds(a):
    area, price = float(a.get("area") or 0), float(a.get("price") or 0)
    if not area or not price:
        return None
    return (int(math.floor(area - AREA_TOL)), int(math.ceil(area + AREA_TOL)),
            int(round(price * (1 - PRICE_TOL))), int(round(price * (1 + PRICE_TOL))))


def otodom_url(a):
    b = _bounds(a)
    r = OTO_ROOMS.get(str(a.get("rooms") or ""))
    d = app_market.slug(a.get("district"))
    if not b or not r or d not in app_market.DISTRICTS:
        return None
    return OTO.format(d=app_market.url_slug(d), r=r, a0=b[0], a1=b[1], p0=b[2], p1=b[3])


def olx_url(a):
    b = _bounds(a)
    if not b:
        return None
    r = OLX_ROOMS.get(str(a.get("rooms") or ""))
    return OLX.format(a0=b[0], a1=b[1], p0=b[2], p1=b[3], r=("&" + quote("filter_enum_rooms[0]") + "=" + r) if r else "")


# ---------------------------------------------------------------- разбор ответов
def parse_otodom(page_props):
    """pageProps поиска Otodom -> объявления агентств и компаний (частные пропускаем)."""
    import app_searches
    out = []
    for x in (((page_props.get("data") or {}).get("searchAds") or {}).get("items") or []):
        try:
            if x.get("isPrivateOwner"):
                continue
            i = app_searches.item(x)
            out.append({
                "src": "otodom", "id": i["id"], "url": i["url"], "price": i["price"], "area": i["area"],
                "rooms": i["rooms"], "street": i["street"], "district": i["district"],
                "floor": x.get("floorNumber") or "",
                "agency": i.get("agency") or ((x.get("advertOwner") or {}).get("name") or "").strip(),
                "imgs": [im.get("url") for im in (x.get("images") or []) if isinstance(im, dict) and im.get("url")][:3],
            })
        except Exception:
            pass
    return out


def parse_olx(data):
    """Ответ OLX (owner_type=business) -> объявления агентств; копии с Otodom пропускаем."""
    import app_owners
    out = []
    for ad in data.get("data") or []:
        try:
            if "otodom.pl" in str(ad.get("external_url") or ""):
                continue
            loc = ad.get("location") or {}
            out.append({
                "src": "olx", "id": "olx-" + str(ad.get("id")), "url": ad.get("url") or "",
                "price": app_owners._num(app_owners._olx_param(ad, "price").get("value")),
                "area": app_owners._num(app_owners._olx_param(ad, "m").get("key")),
                "rooms": app_owners.OLX_ROOMS.get(str(app_owners._olx_param(ad, "rooms").get("key") or ""), ""),
                "street": "", "floor": "", "district": ((loc.get("district") or {}).get("name") or ""),
                "agency": (((ad.get("user") or {}).get("company_name") or (ad.get("user") or {}).get("name")) or "").strip(),
                "imgs": [p.get("link") for p in (ad.get("photos") or []) if p.get("link")][:3],
            })
        except Exception:
            pass
    return out


# ---------------------------------------------------------------- сравнение
def compare(a, cands, own_hashes, cand_hashes):
    """-> список копий [{src,url,agency,price,how,dist}]. cand_hashes(c) -> хеши фото кандидата."""
    def near(c):
        try:
            return abs(float(c.get("area") or 0) - float(a.get("area") or 0)) + abs((c.get("price") or 0) / (a.get("price") or 1) - 1) * 10
        except Exception:
            return 99
    pool = []
    for c in cands:
        if c.get("id") == a.get("id"):
            continue
        if a.get("district") and c.get("district") and app_market.slug(c["district"]) != app_market.slug(a["district"]):
            continue
        if same_street(a.get("street"), c.get("street")) is False:    # улицы известны и разные — другая квартира
            continue
        pool.append(c)
    pool.sort(key=near)
    out = []
    for c in pool[:MAX_CMP]:
        how, dist = None, None
        if same_place(a, c):
            how = "place"
        if own_hashes:
            dist = photo_distance(own_hashes, cand_hashes(c))
            if dist is not None and dist <= PHOTO_MAX:
                how = "photo"
        if how:
            out.append({"src": c["src"], "url": c.get("url") or "", "agency": c.get("agency") or "",
                        "price": c.get("price"), "how": how, "dist": dist,
                        "ours": "hermea" in (c.get("agency") or "").lower()})    # уже у нас
    return out


def _next_data(html):
    import app_owners
    return app_owners._next_data(html)


def find(a, sess, get, pause=1.5, log=print):
    """Ищет копии объявления a. get(sess, url) -> текст (как app_owners._get).
    -> {"checked": дата, "items": [...], "error": ""}"""
    import json
    import app_owners
    cands, err = [], ""
    u = otodom_url(a)
    if u:
        try:
            cands += parse_otodom(_next_data(get(sess, u)))
        except Exception as e:
            err = str(e)[:120]
            log("копии Otodom:", a.get("id"), e)
        time.sleep(pause)
    u = olx_url(a)
    if u:
        try:
            cands += parse_olx(json.loads(get(sess, u)))
        except Exception as e:
            err = err or str(e)[:120]
            log("копии OLX:", a.get("id"), e)
    own = _hashes(sess, a.get("imgs") or ([a["img"]] if a.get("img") else []))
    items = compare(a, cands, own, lambda c: _hashes(sess, c.get("imgs")))
    return {"checked": app_owners._today(), "items": items, "error": err if not cands else "", "n": len(cands),
            "full": bool(a.get("imgs"))}            # False: у объявления ещё не было трёх фото и этажа (до 1.12)
