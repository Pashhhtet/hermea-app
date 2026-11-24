"""Слежение за поиском Otodom: новые квартиры по сохранённым фильтрам.

Пользователь вставляет ссылку на результаты поиска (с фильтрами). Программа
открывает первую страницу (сортировка «самые новые»), запоминает, какие квартиры
уже видела, и показывает только новые. Проверка: при запуске и каждые 20 минут,
пока окно открыто. Совместимо с Python 3.9.
"""
import json
import os
import re
import secrets
import threading
import time
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

FILE = None            # задаётся из app_server (папка _program)
LOCK = threading.RLock()
DATA = {"searches": []}
CHECK_EVERY = 20 * 60
ROOMS = {"ONE": "1", "TWO": "2", "THREE": "3", "FOUR": "4", "FIVE": "5", "SIX": "6", "SEVEN": "7",
         "EIGHT": "8", "NINE": "9", "TEN": "10", "MORE": "10+"}
TAGS = {"PARKING_SPOT": "parking", "BALCONY": "balcony", "AIR_CONDITIONING": "ac", "GARDEN": "garden",
        "TERRACE": "terrace", "SEPARATE_KITCHEN": "kitchen", "LIFT": "lift"}
_SESS = {"s": None}


def init(prog_dir):
    global FILE
    FILE = os.path.join(prog_dir, "app_searches.json")
    try:
        DATA.update(json.load(open(FILE, encoding="utf-8")))
    except Exception:
        pass


def save():
    with LOCK:
        tmp = FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(DATA, f, ensure_ascii=False)
        os.replace(tmp, FILE)


def is_search_url(u):
    try:
        p = urlparse(u.strip())
    except Exception:
        return False
    return p.netloc.endswith("otodom.pl") and "/wyniki/" in p.path


def normalize(u):
    """Всегда «самые новые» сначала и первая страница."""
    p = urlparse(u.strip())
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k not in ("by", "direction", "page")]
    q += [("by", "LATEST"), ("direction", "DESC")]
    return urlunparse(p._replace(query=urlencode(q), fragment=""))


def parse(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("no data")
    pp = json.loads(m.group(1))["props"]["pageProps"]
    sa = ((pp.get("data") or {}).get("searchAds") or {})
    items = []
    for x in sa.get("items") or []:
        try:
            items.append(item(x))
        except Exception:
            pass
    title = (pp.get("pageHeading") or pp.get("pageTitle") or "Otodom").split("|")[0].strip()
    total = ((sa.get("pagination") or {}).get("totalItems"))
    return title, items, total


def item(x):
    locs = {l.get("locationLevel"): l.get("name") for l in
            (((x.get("location") or {}).get("reverseGeocoding") or {}).get("locations") or [])}
    street = ((((x.get("location") or {}).get("address") or {}).get("street") or {}).get("name") or "")
    price = ((x.get("totalPrice") or {}).get("value"))
    rent = ((x.get("rentPrice") or {}).get("value"))
    imgs = x.get("images") or []
    img = imgs[0].get("url") if imgs and isinstance(imgs[0], dict) else None
    if img and "apollo.olxcdn.com" in img:
        img = img.split(";")[0] + ";s=640x480;q=80"
    slug = x.get("slug") or ""
    return {
        "id": str(x.get("id")),
        "title": x.get("title") or "",
        "url": f"https://www.otodom.pl/pl/oferta/{slug}" if slug else "",
        "img": img,
        "price": price,
        "rent": rent,
        "total": (price or 0) + (rent or 0) if price else None,
        "area": x.get("areaInSquareMeters"),
        "rooms": ROOMS.get(str(x.get("roomsNumber") or ""), ""),
        "district": locs.get("district") or "",
        "sub": locs.get("residential") or "",
        "street": street.replace("ul. ", ""),
        "owner": bool(x.get("isPrivateOwner")),
        "agency": ((x.get("agency") or {}).get("name") or "").strip(),
        "created": x.get("createdAtFirst") or x.get("dateCreated") or "",
        "tags": [TAGS[t["value"]] for t in (x.get("tags") or []) if isinstance(t, dict) and t.get("value") in TAGS],
    }


def _session(http_factory):
    if _SESS["s"] is None:
        _SESS["s"] = http_factory()
    return _SESS["s"]


def find(sid):
    return next((s for s in DATA["searches"] if s["id"] == sid), None)


def add(url):
    s = {"id": secrets.token_hex(4), "url": normalize(url), "title": "", "seen": [], "hidden": [],
         "items": [], "total": None, "last_check": 0, "error": "", "first": True, "created": time.time()}
    with LOCK:
        DATA["searches"].insert(0, s)
        save()
    return s


def remove(sid):
    with LOCK:
        DATA["searches"] = [s for s in DATA["searches"] if s["id"] != sid]
        save()


def check(s, http_factory, on_new=None):
    """Открывает поиск и обновляет список. Новые = которых ещё не было в «seen»."""
    s["checking"] = True
    try:
        r = _session(http_factory).get(s["url"], timeout=40)
        if r.status_code in (403, 429):
            raise RuntimeError(f"HTTP {r.status_code}")
        r.raise_for_status()
        title, items, total = parse(r.text)
        with LOCK:
            if not s.get("title"):
                s["title"] = title
            s["items"], s["total"], s["error"] = items, total, ""
            s["last_check"] = time.time()
            ids = [i["id"] for i in items]
            if s.get("first"):                      # первый раз: всё, что есть сейчас, считаем просмотренным
                s["seen"] = ids
                s["first"] = False
                fresh = []
            else:
                fresh = [i for i in ids if i not in s["seen"] and i not in s["hidden"]]
            s["notified"] = list(set(s.get("notified") or []) | set(fresh))[-500:]
            save()
        if fresh and on_new:
            on_new(s, len(fresh))
        return s
    except Exception as e:
        s["error"] = str(e)[:200]
        s["last_check"] = time.time()
        raise
    finally:
        s["checking"] = False


def new_count(s):
    seen, hidden = set(s.get("seen") or []), set(s.get("hidden") or [])
    return sum(1 for i in s.get("items") or [] if i["id"] not in seen and i["id"] not in hidden)


def mark_seen(sid, ad=None):
    with LOCK:
        s = find(sid)
        if not s:
            return
        ids = [ad] if ad else [i["id"] for i in s.get("items") or []]
        s["seen"] = (list(dict.fromkeys((s.get("seen") or []) + ids)))[-3000:]
        save()


def hide(sid, ad):
    with LOCK:
        s = find(sid)
        if s and ad not in s["hidden"]:
            s["hidden"] = (s["hidden"] + [ad])[-3000:]
            save()


def summary():
    with LOCK:
        return [{"id": s["id"], "title": s.get("title") or "Otodom", "new": new_count(s), "error": s.get("error", ""),
                 "checking": bool(s.get("checking")), "last_check": s.get("last_check", 0)} for s in DATA["searches"]]


def detail(sid):
    with LOCK:
        s = find(sid)
        if not s:
            return None
        seen, hidden = set(s.get("seen") or []), set(s.get("hidden") or [])
        items = [dict(i, new=i["id"] not in seen) for i in s.get("items") or [] if i["id"] not in hidden]
        return {"id": s["id"], "title": s.get("title") or "Otodom", "url": s["url"], "items": items,
                "total": s.get("total"), "last_check": s.get("last_check", 0), "error": s.get("error", ""),
                "checking": bool(s.get("checking")), "new": new_count(s)}


def loop(http_factory, on_new, log):
    time.sleep(15)
    while True:
        for s in list(DATA["searches"]):
            if time.time() - (s.get("last_check") or 0) < CHECK_EVERY - 30:
                continue
            try:
                check(s, http_factory, on_new)
            except Exception as e:
                log("search:", s.get("title"), e)
            time.sleep(3)
        time.sleep(60)
