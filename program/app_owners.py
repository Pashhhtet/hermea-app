"""Собственники: кого из частных арендодателей Otodom и OLX стоит обзвонить первым (работа за 50% комиссии).

Раз в день (пока окно открыто) программа проходит по 18 районам Варшавы и собирает частные
объявления (isPrivateOwner=true). Для каждого считается оценка 0–100: чем дольше квартира не
сдаётся, чем дороже рынка, чем хуже объявление и чем больше собственник платит за продвижение —
тем больше ему нужен агент. По лучшим кандидатам открывается страница объявления: текст
(«bez pośredników» — минус, «biura mile widziane» — плюс), дата освобождения, другие объявления.
Статусы звонков хранятся в _program/app_owners.json. Совместимо с Python 3.9.
"""
import datetime as dt
import html as htmlmod
import json
import os
import re
import threading
import time

import app_copies
import app_market
import app_searches

FILE = None
LOCK = threading.RLock()
DATA = {"ads": {}, "last_scan": None}
STATE = {"state": "idle", "done": 0, "total": 0, "error": "", "phase": ""}
BASE = ("https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa/{d}"
        "?limit=72&by=LATEST&direction=DESC&isPrivateOwner=true&page={p}")
MAX_PAGES = 6            # до 432 частных объявлений на район
# OLX: открытый список объявлений сайта, только частные лица, самые новые; описание приходит сразу
OLX_API = ("https://www.olx.pl/api/v1/offers/?offset={o}&limit=50&category_id=15&city_id=17871"
           "&owner_type=private&sort_by=created_at:desc")
OLX_PAGES = 20           # OLX отдаёт не больше 1000 объявлений на один поиск
OLX_ROOMS = {"one": "1", "two": "2", "three": "3", "four": "4"}
DETAIL_PER_DAY = 45      # сколько страниц объявлений открываем за проход (лучшие кандидаты)
DETAIL_TTL = 7           # дней — потом текст перечитываем
COPIES_PER_DAY = 40      # сколько объявлений за проход проверяем на копии у агентств (лучшие кандидаты)
COPIES_TTL = 3           # дней — потом ищем копии снова (агентства выставляют позже собственника)
GONE_KEEP = 45           # снятые объявления храним столько дней (чтобы узнать повторную публикацию)
STATUSES = ("new", "called", "nocall", "agreed", "refused", "hidden")
CALL_STATUSES = ("called", "nocall", "agreed", "refused")

NEG = [r"bez\s+po[sś]rednik", r"bez\s+biur", r"bez\s+agencj", r"biura\s+(nieruchomo[sś]ci\s+)?prosz[eę]\s+(o\s+)?nie",
       r"agencj\w*\s+prosz[eę]\s+(o\s+)?nie", r"po[sś]rednik\w*\s+prosz[eę]\s+(o\s+)?nie",
       r"nie\s+wsp[oó][lł]pracuj\w*\s+z\s+(biur|agencj|po[sś]rednik)", r"po[sś]rednikom\s+dzi[eę]kuj",
       r"biurom\s+dzi[eę]kuj", r"agencjom\s+dzi[eę]kuj", r"tylko\s+bezpo[sś]rednio", r"oferta\s+tylko\s+dla\s+najemc"]
POS = [r"biura\s+mile\s+widziane", r"agencj\w*\s+mile\s+widzian", r"wsp[oó][lł]prac\w*\s+z\s+biur",
       r"zapraszam\s+(r[oó]wnie[zż]\s+)?(biura|agencj|po[sś]rednik)", r"po[sś]rednicy\s+mile\s+widziani",
       r"prowizj\w*\s+(dla\s+biura\s+)?(p[lł]ac[eę]|pokrywa|po\s+stronie\s+w[lł]a[sś]ciciela)"]


def init(prog_dir):
    global FILE
    FILE = os.path.join(prog_dir, "app_owners.json")
    try:
        DATA.update(json.load(open(FILE, encoding="utf-8")))
    except Exception:
        pass
    # пересчёт при запуске: свежие медианы рынка и новые веса оценки
    with LOCK:
        for a in DATA["ads"].values():
            try:
                a["market"] = app_market.compare_total(a)
            except Exception:
                pass
        _rescore()


def _save():
    with LOCK:
        tmp = FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(DATA, f, ensure_ascii=False)
        os.replace(tmp, FILE)


def _today():
    return dt.date.today().isoformat()


def _days(since, until=None):
    try:
        a = dt.date.fromisoformat(str(since)[:10])
    except Exception:
        return None
    b = dt.date.fromisoformat(until) if until else dt.date.today()
    return (b - a).days


# ---------------------------------------------------------------- разбор Otodom
def _next_data(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("no data")
    return json.loads(m.group(1))["props"]["pageProps"]


def parse_list(html):
    pp = _next_data(html)
    sa = (pp.get("data") or {}).get("searchAds") or {}
    out = []
    for x in sa.get("items") or []:
        try:
            if not x.get("isPrivateOwner"):
                continue
            i = app_searches.item(x)
            i.update(
                created=(x.get("createdAtFirst") or x.get("dateCreated") or "")[:10],
                pushed=(x.get("pushedUpAt") or "")[:10],
                promoted=bool(x.get("isPromoted")),
                photos=x.get("totalPossibleImages") or len(x.get("images") or []),
                name=((x.get("advertOwner") or {}).get("name") or "").strip(),
                slug=x.get("slug") or "",
                floor=x.get("floorNumber") or "",
                imgs=[im.get("url") for im in (x.get("images") or []) if isinstance(im, dict) and im.get("url")][:3],
            )
            out.append(i)
        except Exception:
            pass
    pages = ((sa.get("pagination") or {}).get("totalPages")) or 1
    return out, pages


def _olx_param(ad, key):
    for p in ad.get("params") or []:
        if p.get("key") == key:
            return p.get("value") or {}
    return {}


def _desc_detail(desc, today, others=0, free_from=""):
    low = desc.lower()
    return {"desc_len": len(desc), "neg": any(re.search(p, low) for p in NEG),
            "pos": any(re.search(p, low) for p in POS), "free_from": free_from, "deposit": None,
            "owner_id": "", "others": others, "snippet": desc[:280], "checked": today}


def parse_olx(data, today=None):
    """Ответ OLX (/api/v1/offers) -> объявления в том же виде, что и Otodom (id с приставкой olx-)."""
    today = today or _today()
    out = []
    for ad in data.get("data") or []:
        try:
            if ad.get("business") or "otodom.pl" in str(ad.get("external_url") or ""):
                continue                      # агентство или копия объявления с Otodom (его мы уже видим)
            if re.search(r"\b(lokal|biur[oa]|gara[zż]|magazyn|pok[oó]j\s+(do|dla|w\s+mieszkaniu)|miejsce\s+postojowe)\b",
                         (ad.get("title") or "").lower()) and not re.search(r"mieszkani|kawalerk|apartament", (ad.get("title") or "").lower()):
                continue                      # не квартира (помещение, комната, гараж)
            price = _num(_olx_param(ad, "price").get("value"))
            rent = _num(_olx_param(ad, "rent").get("key"))
            rent = rent if rent and rent > 1 else None
            area = _num(_olx_param(ad, "m").get("key"))
            rooms = OLX_ROOMS.get(str(_olx_param(ad, "rooms").get("key") or ""), "")
            photos = ad.get("photos") or []
            img = None
            if photos:
                img = (photos[0].get("link") or "").replace(":443", "").replace("{width}x{height}", "640x480") or None
            loc = ad.get("location") or {}
            created = (ad.get("created_time") or "")[:10]
            refreshed = (ad.get("pushup_time") or "")[:10]          # платное поднятие (обычное обновление не считаем)
            promo = ad.get("promotion") or {}
            desc = _text(ad.get("description") or "")
            pets = str(_olx_param(ad, "pets").get("key") or "").lower()
            out.append({
                "id": "olx-" + str(ad.get("id")), "src": "olx",
                "title": ad.get("title") or "", "url": ad.get("url") or "", "img": img,
                "price": price, "rent": rent, "total": (price or 0) + (rent or 0) if price else None,
                "area": area, "rooms": rooms,
                "district": ((loc.get("district") or {}).get("name") or ""), "sub": "", "street": "",
                "created": created, "pushed": refreshed if refreshed and refreshed > created else "",
                "promoted": bool(promo.get("top_ad") or promo.get("highlighted") or promo.get("urgent")),
                "photos": len(photos), "name": ((ad.get("user") or {}).get("name") or "").strip(),
                "slug": "", "tags": ["pets"] if pets in ("tak", "yes") else [], "floor": "",
                "imgs": [p.get("link") for p in photos if p.get("link")][:3],
                "_user": str((ad.get("user") or {}).get("id") or ""), "_desc": desc,
            })
        except Exception:
            pass
    return out


def _text(s):
    s = re.sub(r"<(br|/p|/li|/div)[^>]*>", "\n", s or "", flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = htmlmod.unescape(s)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", s)).strip()


def parse_detail(html):
    ad = _next_data(html).get("ad") or {}
    ch = {c.get("key"): c.get("value") for c in ad.get("characteristics") or [] if isinstance(c, dict)}
    owner = ad.get("owner") or {}
    desc = _text(ad.get("description") or "")
    low = desc.lower()
    neg = [p for p in NEG if re.search(p, low)]
    pos = [p for p in POS if re.search(p, low)]
    others = ad.get("userAdverts") or []
    return {
        "desc_len": len(desc),
        "neg": bool(neg), "pos": bool(pos),
        "free_from": (ch.get("free_from") or "")[:10],
        "deposit": _num(ch.get("deposit")),
        "owner_id": str(owner.get("id") or ""),
        "others": len(others) if isinstance(others, list) else 0,
        "snippet": desc[:280],
        "checked": _today(),
    }


def _num(v):
    try:
        return int(float(str(v).replace(" ", "").replace(",", ".")))
    except Exception:
        return None


# ---------------------------------------------------------------- оценка
def score(a, today=None):
    """-> (0..100, [причины]) — насколько собственнику сейчас нужен агент."""
    today = today or _today()
    pts, why = 20, []
    age = _days(a.get("created"), today)
    seen = _days(a.get("first_seen"), today) or 0
    # сколько квартира на рынке сейчас: свежая дата публикации надёжна, старая (объявление
    # переиспользуют годами) — тогда считаем от нашего первого обнаружения
    days = age if age is not None and age <= 120 else seen
    a["days"] = days
    if days >= 5:
        pts += min(30, round((days - 4) * 1.1))
        why.append(["days", days])
    elif days <= 1 and (age is not None and age <= 1):
        pts -= 6
    if age is not None and age > 120:
        pts += 6
        why.append(["old", age // 30])
    drops = a.get("drops") or []
    if drops:
        total = sum(d[1] - d[2] for d in drops)
        pts += min(25, 12 + 6 * (len(drops) - 1))
        why.append(["drop", total])
    if a.get("relisted"):
        pts += 15
        why.append(["relisted", a["relisted"]])
    if a.get("pushed") and (_days(a["pushed"], today) or 99) <= 7 and days >= 14:
        pts += 5                          # старое объявление, а собственник всё ещё поднимает его
        why.append(["pushed", a["pushed"]])
    if a.get("promoted"):
        pts += 6
        why.append(["promoted", 1])
    mk = a.get("market")
    if mk is not None:
        if mk >= 8:
            pts += min(15, round(mk * 0.5))
            why.append(["above", mk])
        elif mk <= -10:
            pts -= 8                      # дешевле рынка — сдастся само
    ph = a.get("photos") or 0
    if ph and ph <= 3:
        pts += 12
        why.append(["photos", ph])
    elif ph and ph <= 6:
        pts += 6
        why.append(["photos", ph])
    d = a.get("detail") or {}
    if d:
        if d.get("neg"):
            pts -= 45
            why.append(["neg", 1])
        if d.get("pos"):
            pts += 18
            why.append(["pos", 1])
        ff = d.get("free_from")
        if ff and (_days(ff, today) or 0) >= 14:     # «свободна с» давно прошла — стоит пустая
            pts += 8
            why.append(["empty", ff])
        if d.get("desc_len", 999) < 250:
            pts += 5
            why.append(["short", d.get("desc_len")])
        n = d.get("others", 0)
        if 1 <= n <= 4:                   # несколько квартир: сдаёт регулярно, агент экономит ему время
            pts += 8
            why.append(["others", n + 1])
        elif n >= 5:                      # много объявлений — скорее всего компания со своими условиями
            why.append(["many", n + 1])
    cp = [c for c in ((a.get("copies") or {}).get("items") or []) if not c.get("ours")]
    sure = [c for c in cp if c.get("how") == "photo"]
    if sure:                              # те же фото у агентств — с агентами работает
        pts += 10
        why.append(["agency", len(sure)])
    elif cp:                              # совпали только улица, этаж и площадь — агент сверит по ссылке
        why.append(["agency_maybe", len(cp)])
    return max(0, min(100, pts)), why


def _rescore(today=None):
    for a in DATA["ads"].values():
        a["score"], a["why"] = score(a, today)


# ---------------------------------------------------------------- сбор
def _get(sess, url):
    r = sess.get(url, timeout=40)
    if r.status_code in (403, 429):
        raise RuntimeError(f"HTTP {r.status_code}")
    r.raise_for_status()
    return r.text


def merge(items, today=None):
    """Добавляет найденные сегодня объявления в базу: цены, повторные публикации."""
    today = today or _today()
    with LOCK:
        ads = DATA["ads"]
        # отпечаток квартиры: улица + площадь + комнаты (для повторной публикации с новым id)
        prints = {}
        for a in ads.values():
            if a.get("last_seen", "") < today and _print(a):
                prints.setdefault(_print(a), []).append(a)
        for i in items:
            a = ads.get(i["id"])
            tot = i.get("total") or i.get("price")
            if a is None:
                a = ads[i["id"]] = {"id": i["id"], "first_seen": today, "status": "new", "prices": []}
                old = [o for o in prints.get(_print(i), []) if o["id"] != i["id"]] if _print(i) else []
                if old:
                    a["relisted"] = max(len(old), 1)
                    a["first_seen"] = min(o.get("first_seen", today) for o in old)
                    a["prices"] = list(old[0].get("prices") or [])
                    if old[0].get("status") not in (None, "new"):
                        a["status"], a["note"] = old[0]["status"], old[0].get("note", "")
            for k in ("title", "url", "img", "price", "rent", "total", "area", "rooms", "district", "sub",
                      "street", "created", "pushed", "promoted", "photos", "name", "slug", "tags", "src",
                      "floor", "imgs"):
                a[k] = i.get(k)
            if i.get("_detail"):                       # OLX: описание пришло вместе со списком
                a["detail"] = i["_detail"]
            a["last_seen"] = today
            if tot and (not a["prices"] or a["prices"][-1][1] != tot):
                a["prices"].append([today, tot])
            a["drops"] = [[p[0], q[1], p[1]] for q, p in zip(a["prices"], a["prices"][1:]) if p[1] < q[1]]
            try:
                a["market"] = app_market.compare_total(a)
            except Exception:
                a["market"] = None
        # давно снятые — убираем
        for k in [k for k, a in ads.items() if (_days(a.get("last_seen"), today) or 0) > GONE_KEEP]:
            ads.pop(k, None)
        _rescore(today)


def _print(a):
    street = (a.get("street") or "").lower().strip()
    if not street:                    # без улицы (OLX) не угадать, та ли это квартира
        return None
    return (street, round(float(a.get("area") or 0)), a.get("rooms") or "")


def scan(http_factory, log=print, pause=3.5):
    """Полный проход: списки по районам, затем страницы лучших кандидатов."""
    if STATE["state"] == "running":
        return
    STATE.update(state="running", done=0, total=len(app_market.DISTRICTS), error="", phase="list")
    sess = http_factory()
    items, ok = [], 0
    try:
        for d in app_market.DISTRICTS:
            p, pages = 1, 1
            while p <= min(pages, MAX_PAGES):
                try:
                    got, pages = parse_list(_get(sess, BASE.format(d=app_market.url_slug(d), p=p)))
                    items += got
                    ok += 1
                except Exception as e:
                    log("собственники:", d, p, e)
                    STATE["error"] = str(e)[:120]
                    if "HTTP 4" in str(e):
                        break
                p += 1
                time.sleep(pause)
            STATE["done"] += 1
        # OLX: частные объявления всей Варшавы
        STATE.update(phase="olx", done=0, total=OLX_PAGES)
        olx = []
        for k in range(OLX_PAGES):
            try:
                got = parse_olx(json.loads(_get(sess, OLX_API.format(o=k * 50))))
                olx += got
                ok += 1
                if not got:
                    break
            except Exception as e:
                log("собственники OLX:", k, e)
                STATE["error"] = str(e)[:120]
                break
            STATE["done"] += 1
            time.sleep(pause)
        users = {}
        for i in olx:
            if i["_user"]:
                users[i["_user"]] = users.get(i["_user"], 0) + 1
        seen_ids = set()
        for i in olx:
            if i["id"] in seen_ids:
                continue
            seen_ids.add(i["id"])
            i["_detail"] = _desc_detail(i.pop("_desc"), _today(), others=max(0, users.get(i.pop("_user"), 1) - 1))
            items.append(i)
        if ok:
            merge(items)
            DATA["last_scan"] = _today()
            _save()
        # страницы объявлений: самые перспективные, у кого текст ещё не читали (или давно)
        STATE.update(phase="detail", done=0)
        with LOCK:
            cand = [a for a in DATA["ads"].values() if a.get("last_seen") == _today() and a.get("status") in ("new", None)
                    and a.get("src") != "olx"
                    and (not a.get("detail") or (_days(a["detail"].get("checked")) or 0) > DETAIL_TTL)]
            cand.sort(key=lambda a: -a.get("score", 0))
            cand = cand[:DETAIL_PER_DAY]
        STATE["total"] = len(cand)
        for a in cand:
            try:
                det = parse_detail(_get(sess, a["url"]))
                with LOCK:
                    a["detail"] = det
                    a["score"], a["why"] = score(a)
            except Exception as e:
                log("собственники: объявление", a.get("id"), e)
                if "HTTP 4" in str(e):
                    break
            STATE["done"] += 1
            time.sleep(pause)
        _save()
        # та же квартира у агентств: лучшие кандидаты, у кого не проверяли (или давно)
        with LOCK:
            cand = [a for a in DATA["ads"].values() if a.get("last_seen") == _today() and a.get("status") in ("new", None)
                    and _stale(a, COPIES_TTL)]
            cand.sort(key=lambda a: -a.get("score", 0))
            cand = cand[:COPIES_PER_DAY]
        STATE.update(phase="copies", done=0, total=len(cand))
        for a in cand:
            if not _copies(a, sess, log, pause):
                break
            STATE["done"] += 1
            time.sleep(pause)
        _save()
    finally:
        STATE.update(state="idle", phase="")


def _stale(a, ttl):
    """Пора искать копии снова: не искали, давно, или искали без фото и этажа (объявление собрано до 1.12)."""
    res = a.get("copies") or {}
    d = _days(res.get("checked"))
    return d is None or d > ttl or (not res.get("full") and bool(a.get("imgs")))


def _copies(a, sess, log=print, pause=3.5):
    """Ищет ту же квартиру у агентств и пересчитывает оценку. -> False, если сайт начал отказывать."""
    try:
        res = app_copies.find(a, sess, _get, pause=pause, log=log)
    except Exception as e:                # ошибка в поиске копий не должна ломать сбор собственников
        log("копии:", a.get("id"), e)
        return True
    if "HTTP 4" in (res.get("error") or ""):
        return False
    with LOCK:
        a["copies"] = res
        a["score"], a["why"] = score(a)
    return True


def check_copies(ad_id, http_factory, log=print):
    """Проверка одного объявления по кнопке. -> результат (copies)."""
    with LOCK:
        a = DATA["ads"].get(str(ad_id))
    if not a:
        raise KeyError(ad_id)
    res = app_copies.find(a, http_factory(), _get, pause=1.0, log=log)
    with LOCK:
        a["copies"] = res
        a["score"], a["why"] = score(a)
        _save()
    return res


def loop(http_factory, log):
    """Раз в день, пока окно открыто (после рыночного снимка)."""
    time.sleep(240)
    while True:
        try:
            if DATA.get("last_scan") != _today():
                scan(http_factory, log)
        except Exception as e:
            log("собственники:", e)
            STATE.update(state="idle", error=str(e)[:120])
        time.sleep(3600)


# ---------------------------------------------------------------- для окна
def public(limit=200):
    today = _today()
    with LOCK:
        ads = [dict(a) for a in DATA["ads"].values()]
    live = [a for a in ads if a.get("last_seen") == DATA.get("last_scan") or a.get("status") in ("called", "agreed")]
    live.sort(key=lambda a: (a.get("status") == "hidden", -(a.get("score") or 0)))
    for a in live:
        a.pop("prices", None)
        a.pop("imgs", None)
        a["gone"] = a.get("last_seen") != DATA.get("last_scan")
    counts = {s: sum(1 for a in ads if a.get("status") == s) for s in STATUSES}
    return {"items": live[:limit], "total": len(live), "counts": counts, "last_scan": DATA.get("last_scan"),
            "today": today, "state": STATE, "districts": app_market.DISTRICTS, "stats": stats(7)}


def set_status(ad_id, status=None, note=None):
    with LOCK:
        a = DATA["ads"].get(str(ad_id))
        if not a:
            raise KeyError(ad_id)
        prev = a.get("status")
        if status:
            if status not in STATUSES:
                raise ValueError(status)
            a["status"] = status
            a["status_at"] = _today()
            if status in CALL_STATUSES and status != prev:      # журнал звонков для статистики
                DATA.setdefault("log", []).append([_today(), status, a.get("district") or "", a.get("src") or "otodom", str(ad_id)])
                DATA["log"] = DATA["log"][-5000:]
        if note is not None:
            a["note"] = str(note)[:500]
        _save()
        return prev, a.get("status")


def stats(days=7):
    """Звонки собственникам за последние дни: по дням, итоги, районы. Одно объявление = один итог
    (последний статус за период), чтобы «не дозвонился → согласен» не считался дважды."""
    today = dt.date.today()
    span = [(today - dt.timedelta(days=k)).isoformat() for k in range(days - 1, -1, -1)]
    with LOCK:
        log = list(DATA.get("log") or [])
        logged = {e[4] for e in log}
        # статусы, поставленные до появления журнала
        for a in DATA["ads"].values():
            if a.get("status") in CALL_STATUSES and a.get("status_at") and str(a.get("id")) not in logged:
                log.append([a["status_at"], a["status"], a.get("district") or "", a.get("src") or "otodom", str(a.get("id"))])
    last = {}
    for e in log:
        if e[0] >= span[0]:
            last[e[4]] = e                       # журнал идёт по времени: остаётся последний итог
    per_day = {d: {k: 0 for k in CALL_STATUSES} for d in span}
    tot = {k: 0 for k in CALL_STATUSES}
    dist = {}
    for e in last.values():
        if e[0] in per_day:
            per_day[e[0]][e[1]] += 1
        tot[e[1]] += 1
        x = dist.setdefault(e[2] or "?", {"n": 0, "agreed": 0})
        x["n"] += 1
        x["agreed"] += e[1] == "agreed"
    talked = tot["called"] + tot["agreed"] + tot["refused"]
    top = sorted(dist.items(), key=lambda kv: (-kv[1]["agreed"], -kv[1]["n"]))[:4]
    return {"days": [{"day": d, **per_day[d]} for d in span], "total": tot, "calls": sum(tot.values()),
            "talked": talked, "rate": round(tot["agreed"] * 100 / talked) if talked else None,
            "districts": [{"name": k, **v} for k, v in top]}


def new_strong(threshold=75):
    """Сколько сильных собственников (оценка ≥ 75) появилось с прошлого утра. Первый раз (и при первом
    появлении OLX) только запоминаем, чтобы не объявить сразу сотни «новых»."""
    with LOCK:
        last = DATA.get("last_scan")
        strong = {k: a for k, a in DATA["ads"].items() if a.get("last_seen") == last
                  and (a.get("score") or 0) >= threshold and a.get("status") in (None, "new")}
        first = "announced" not in DATA
        ann = set(DATA.get("announced") or [])
        olx_first = not DATA.get("olx_seen") and any(a.get("src") == "olx" for a in strong.values())
        fresh = [] if first else [k for k, a in strong.items() if k not in ann and not (olx_first and a.get("src") == "olx")]
        DATA["announced"] = list(ann | set(strong))[-6000:]
        if any(a.get("src") == "olx" for a in DATA["ads"].values()):
            DATA["olx_seen"] = True
        _save()
    return len(fresh)
