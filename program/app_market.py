"""Рынок аренды Варшавы: раз в день снимок цен Otodom по районам, медианы и тренд.

Для каждого из 18 районов открывается поиск «аренда квартир, самые новые» (до 72 объявлений),
считаются медианы: цена в месяц (аренда + czynsz), zł/м², по комнатам, и число объявлений.
История хранится в _program/app_market.json — тренд появляется через несколько дней.
Совместимо с Python 3.9.
"""
import datetime as dt
import json
import os
import statistics
import threading
import time
import unicodedata

import app_searches

FILE = None
LOCK = threading.RLock()
DATA = {"days": {}}          # {"2026-11-24": {"bemowo": {...}, ...}}
BASE = "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa/{d}?limit=72&by=LATEST&direction=DESC"
DISTRICTS = {
    "bemowo": "Bemowo", "bialoleka": "Białołęka", "bielany": "Bielany", "mokotow": "Mokotów",
    "ochota": "Ochota", "praga-polnoc": "Praga-Północ", "praga-poludnie": "Praga-Południe",
    "rembertow": "Rembertów", "srodmiescie": "Śródmieście", "targowek": "Targówek", "ursus": "Ursus",
    "ursynow": "Ursynów", "wawer": "Wawer", "wesola": "Wesoła", "wilanow": "Wilanów", "wlochy": "Włochy",
    "wola": "Wola", "zoliborz": "Żoliborz",
}
STATE = {"state": "idle", "done": 0, "error": ""}
KEEP_DAYS = 400


def init(prog_dir):
    global FILE
    FILE = os.path.join(prog_dir, "app_market.json")
    try:
        DATA.update(json.load(open(FILE, encoding="utf-8")))
    except Exception:
        pass


def _save():
    with LOCK:
        days = DATA.get("days") or {}
        for k in sorted(days)[:-KEEP_DAYS]:
            days.pop(k, None)
        tmp = FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(DATA, f, ensure_ascii=False)
        os.replace(tmp, FILE)


def slug(name):
    """«Praga-Południe» -> «praga-poludnie»."""
    s = unicodedata.normalize("NFKD", (name or "").replace("ł", "l").replace("Ł", "L"))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower().strip()
    return "-".join(s.replace("–", "-").split()).replace("--", "-")


def url_slug(d):
    """В адресах Otodom у Праги двойной дефис: praga--poludnie."""
    return d.replace("praga-", "praga--", 1) if d.startswith("praga-") else d


def compare_total(item):
    """Цена «всего в месяц» против медианы района для того же числа комнат. -> % или None.
    (По zł/м² маленькие студии всегда выглядят «дороже рынка», поэтому здесь сравниваем сумму.)"""
    with LOCK:
        days = DATA.get("days") or {}
        if not days:
            return None
        last = days[max(days)]
    d = last.get(slug(item.get("district")))
    tot = item.get("total") or item.get("price")
    if not d or not tot:
        return None
    r = str(item.get("rooms") or "")
    r = r if r in ("1", "2", "3") else ("4" if r else "")
    ref = ((d.get("rooms") or {}).get(r) or {}).get("median") if r else None
    if not ref:
        return None
    return round((tot / ref - 1) * 100)


def _med(xs):
    xs = [x for x in xs if x]
    return round(statistics.median(xs)) if xs else None


def stats(items):
    rows = []
    for i in items:
        tot, area = i.get("total") or i.get("price"), i.get("area")
        if not tot or tot < 800 or tot > 40000:
            continue
        rows.append({"t": tot, "m2": (tot / area) if area and area > 8 else None, "r": i.get("rooms") or ""})
    out = {"n": len(rows), "median": _med([r["t"] for r in rows]),
           "m2": round(statistics.median([r["m2"] for r in rows if r["m2"]]), 1) if any(r["m2"] for r in rows) else None,
           "rooms": {}}
    for k in ("1", "2", "3", "4"):
        sel = [r for r in rows if (r["r"] == k if k != "4" else r["r"] not in ("", "1", "2", "3"))]
        if len(sel) >= 3:
            out["rooms"][k] = {"n": len(sel), "median": _med([r["t"] for r in sel]),
                               "m2": round(statistics.median([r["m2"] for r in sel if r["m2"]]), 1)
                               if any(r["m2"] for r in sel) else None}
    return out


def snapshot(http_factory, log=print, pause=4.0):
    """Снимает все районы (несколько минут, с паузами — чтобы не нагружать сайт)."""
    day = dt.date.today().isoformat()
    STATE.update(state="running", done=0, error="")
    sess = http_factory()
    res = {}
    for d in DISTRICTS:
        try:
            r = sess.get(BASE.format(d=url_slug(d)), timeout=40)
            if r.status_code in (403, 429):
                raise RuntimeError(f"HTTP {r.status_code}")
            r.raise_for_status()
            _, items, total = app_searches.parse(r.text)
            st = stats(items)
            st["total"] = total
            res[d] = st
        except Exception as e:
            log("рынок:", d, e)
            STATE["error"] = str(e)[:120]
        STATE["done"] += 1
        time.sleep(pause)
    if res:
        with LOCK:
            DATA.setdefault("days", {})[day] = res
            _save()
    STATE.update(state="idle")
    return res


def _day_ago(days, n):
    """Ближайший снимок не позже чем n дней назад."""
    target = (dt.date.today() - dt.timedelta(days=n)).isoformat()
    old = [k for k in days if k <= target]
    return days[max(old)] if old else None


def _chg(a, b):
    if not a or not b:
        return None
    return round((a / b - 1) * 100, 1)


def summary():
    with LOCK:
        days = dict(DATA.get("days") or {})
    if not days:
        return {"since": None, "last": None, "districts": [], "city": None, "state": STATE}
    last_day = max(days)
    last = days[last_day]
    w, m = _day_ago(days, 7), _day_ago(days, 30)
    out = []
    for d, name in DISTRICTS.items():
        x = last.get(d)
        if not x:
            continue
        hist = [{"day": k, "m2": (days[k].get(d) or {}).get("m2")} for k in sorted(days)[-60:]]
        out.append({
            "id": d, "name": name, "n": x.get("n"), "total": x.get("total"), "median": x.get("median"),
            "m2": x.get("m2"), "rooms": x.get("rooms") or {},
            "w": _chg(x.get("m2"), ((w or {}).get(d) or {}).get("m2")) if w is not last else None,
            "m": _chg(x.get("m2"), ((m or {}).get(d) or {}).get("m2")) if m is not last else None,
            "supply_w": _chg(x.get("total"), ((w or {}).get(d) or {}).get("total")) if w is not last else None,
            "hist": hist,
        })
    m2s = [x["m2"] for x in out if x["m2"]]
    city = {"m2": round(statistics.median(m2s), 1) if m2s else None,
            "rooms": {k: _med([x["rooms"][k]["median"] for x in out if k in x["rooms"]]) for k in ("1", "2", "3", "4")},
            "w": _med([x["w"] for x in out if x["w"] is not None]) if any(x["w"] is not None for x in out) else None,
            "m": _med([x["m"] for x in out if x["m"] is not None]) if any(x["m"] is not None for x in out) else None}
    return {"since": min(days), "last": last_day, "days": len(days), "districts": out, "city": city, "state": STATE}


def compare(item):
    """Насколько объявление дороже/дешевле медианы района (по комнатам, если есть данные). -> % или None."""
    with LOCK:
        days = DATA.get("days") or {}
        if not days:
            return None
        last = days[max(days)]
    d = last.get(slug(item.get("district")))
    if not d or not item.get("area") or not (item.get("total") or item.get("price")):
        return None
    tot = item.get("total") or item.get("price")
    m2 = tot / item["area"]
    ref = ((d.get("rooms") or {}).get(str(item.get("rooms"))) or {}).get("m2") or d.get("m2")
    if not ref:
        return None
    return round((m2 / ref - 1) * 100)


def loop(http_factory, log):
    """Раз в день (при открытом окне): если сегодняшнего снимка нет — снимаем."""
    time.sleep(90)
    while True:
        try:
            if dt.date.today().isoformat() not in (DATA.get("days") or {}):
                snapshot(http_factory, log)
        except Exception as e:
            log("рынок:", e)
            STATE.update(state="idle", error=str(e)[:120])
        time.sleep(3600)
