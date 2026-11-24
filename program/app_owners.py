"""Собственники: кого из частных арендодателей Otodom стоит обзвонить первым (работа за 50% комиссии).

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

import app_market
import app_searches

FILE = None
LOCK = threading.RLock()
DATA = {"ads": {}, "last_scan": None}
STATE = {"state": "idle", "done": 0, "total": 0, "error": "", "phase": ""}
BASE = ("https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa/{d}"
        "?limit=72&by=LATEST&direction=DESC&isPrivateOwner=true&page={p}")
MAX_PAGES = 6            # до 432 частных объявлений на район
DETAIL_PER_DAY = 45      # сколько страниц объявлений открываем за проход (лучшие кандидаты)
DETAIL_TTL = 7           # дней — потом текст перечитываем
GONE_KEEP = 45           # снятые объявления храним столько дней (чтобы узнать повторную публикацию)
STATUSES = ("new", "called", "nocall", "agreed", "refused", "hidden")

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
            )
            out.append(i)
        except Exception:
            pass
    pages = ((sa.get("pagination") or {}).get("totalPages")) or 1
    return out, pages


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
    if a.get("pushed") and (_days(a["pushed"], today) or 99) <= 14:
        pts += 10
        why.append(["pushed", a["pushed"]])
    if a.get("promoted"):
        pts += 6
        why.append(["promoted", 1])
    mk = a.get("market")
    if mk is not None:
        if mk >= 6:
            pts += min(18, round(mk * 0.9))
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
        if ff and ff <= today:
            pts += 10
            why.append(["empty", ff])
        if d.get("desc_len", 999) < 250:
            pts += 5
            why.append(["short", d.get("desc_len")])
        if d.get("others", 0) >= 1:
            pts += 8
            why.append(["others", d["others"] + 1])
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
            if a.get("last_seen", "") < today:
                prints.setdefault(_print(a), []).append(a)
        for i in items:
            a = ads.get(i["id"])
            tot = i.get("total") or i.get("price")
            if a is None:
                a = ads[i["id"]] = {"id": i["id"], "first_seen": today, "status": "new", "prices": []}
                old = [o for o in prints.get(_print(i), []) if o["id"] != i["id"]]
                if old:
                    a["relisted"] = max(len(old), 1)
                    a["first_seen"] = min(o.get("first_seen", today) for o in old)
                    a["prices"] = list(old[0].get("prices") or [])
                    if old[0].get("status") not in (None, "new"):
                        a["status"], a["note"] = old[0]["status"], old[0].get("note", "")
            for k in ("title", "url", "img", "price", "rent", "total", "area", "rooms", "district", "sub",
                      "street", "created", "pushed", "promoted", "photos", "name", "slug", "tags"):
                a[k] = i.get(k)
            a["last_seen"] = today
            if tot and (not a["prices"] or a["prices"][-1][1] != tot):
                a["prices"].append([today, tot])
            a["drops"] = [[p[0], q[1], p[1]] for q, p in zip(a["prices"], a["prices"][1:]) if p[1] < q[1]]
            try:
                a["market"] = app_market.compare(a)
            except Exception:
                a["market"] = None
        # давно снятые — убираем
        for k in [k for k, a in ads.items() if (_days(a.get("last_seen"), today) or 0) > GONE_KEEP]:
            ads.pop(k, None)
        _rescore(today)


def _print(a):
    return ((a.get("street") or "").lower().strip(), round(float(a.get("area") or 0)), a.get("rooms") or "")


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
                    got, pages = parse_list(_get(sess, BASE.format(d=d, p=p)))
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
        if ok:
            merge(items)
            DATA["last_scan"] = _today()
            _save()
        # страницы объявлений: самые перспективные, у кого текст ещё не читали (или давно)
        STATE.update(phase="detail", done=0)
        with LOCK:
            cand = [a for a in DATA["ads"].values() if a.get("last_seen") == _today() and a.get("status") in ("new", None)
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
    finally:
        STATE.update(state="idle", phase="")


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
        a["gone"] = a.get("last_seen") != DATA.get("last_scan")
    counts = {s: sum(1 for a in ads if a.get("status") == s) for s in STATUSES}
    return {"items": live[:limit], "total": len(live), "counts": counts, "last_scan": DATA.get("last_scan"),
            "today": today, "state": STATE, "districts": app_market.DISTRICTS}


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
        if note is not None:
            a["note"] = str(note)[:500]
        _save()
        return prev, a.get("status")
