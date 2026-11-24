"""Перезвоны: вставил ссылку (можно сразу с телефоном и заметкой) — квартира, телефон и дата
«когда перезвонить» сохраняются; в нужный день утром приходит напоминание.
Поиск по номеру: когда звонят — набираешь последние цифры и видишь, что за квартира.
Хранится в _program/app_calls.json. Python 3.9.
"""
import datetime as dt
import json
import os
import re
import secrets
import threading
import time

FILE = None
LOCK = threading.RLock()
DATA = {"items": [], "notified": ""}
REMIND_AT = (9, 30)

URL_RE = re.compile(r"https?://\S+")
PHONE_RE = re.compile(r"(?:(?:\+|00)\s?48[\s-]?)?(?<!\d)(\d{3})[\s-]?(\d{3})[\s-]?(\d{3})(?!\d)")

WEEKDAYS = [
    ("понедельник", "понеділок", "poniedział", "пн", "pon"),
    ("вторник", "вівтор", "wtor", "вт", "wt"),
    ("сред", "серед", "środ", "srod", "ср", "śr"),
    ("четверг", "четвер", "czwart", "чт", "czw"),
    ("пятниц", "п'ятниц", "пʼятниц", "piąt", "piat", "пт", "pt"),
    ("суббот", "субот", "sobot", "сб", "sob"),
    ("воскрес", "неділ", "niedziel", "вс", "нд", "nd", "ndz"),
]


def init(prog_dir):
    global FILE
    FILE = os.path.join(prog_dir, "app_calls.json")
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


def today():
    return dt.date.today()


def norm_phone(s):
    d = re.sub(r"\D", "", s or "")
    if d.startswith("0048"):
        d = d[4:]
    if len(d) == 11 and d.startswith("48"):
        d = d[2:]
    return d


def pretty_phone(d):
    d = norm_phone(d)
    return f"{d[:3]} {d[3:6]} {d[6:]}" if len(d) == 9 else d


def find_phone(text):
    for m in PHONE_RE.finditer(text or ""):
        return "".join(m.groups())
    return ""


def parse_date(text, base=None):
    """«в пятницу», «завтра», «28.11», «через 3 дня», «jutro»… -> date или None."""
    base = base or today()
    t = (text or "").lower().replace("’", "'")
    if re.search(r"послезавтра|післязавтра|pojutrze", t):
        return base + dt.timedelta(days=2)
    if re.search(r"завтра|jutro", t):
        return base + dt.timedelta(days=1)
    if re.search(r"сегодня|сьогодні|dzi[sś]|dzisiaj", t):
        return base
    m = re.search(r"через\s+(\d+)\s*(дн|день|дні|днів)|za\s+(\d+)\s*dni", t)
    if m:
        return base + dt.timedelta(days=int(m.group(1) or m.group(3)))
    if re.search(r"через\s+неделю|через\s+тиждень|za\s+tydzień", t):
        return base + dt.timedelta(days=7)
    m = re.search(r"(?<!\d)(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?(?!\d)", t)
    if m:
        d, mo = int(m.group(1)), int(m.group(2))
        y = int(m.group(3)) if m.group(3) else base.year
        if y < 100:
            y += 2000
        try:
            r = dt.date(y, mo, d)
            if not m.group(3) and r < base - dt.timedelta(days=60):
                r = dt.date(y + 1, mo, d)
            return r
        except ValueError:
            pass
    words = re.findall(r"[a-zа-яіїєґśłąęóźżćń'ʼ]+", t)
    for wd, names in enumerate(WEEKDAYS):
        for w in words:
            if any(w == n or (len(n) > 3 and w.startswith(n)) for n in names):
                ahead = (wd - base.weekday()) % 7 or 7
                return base + dt.timedelta(days=ahead)
    return None


def split_text(text):
    """Вставленный текст -> (url, телефон, дата, заметка)."""
    text = text or ""
    m = URL_RE.search(text)
    url = m.group(0).rstrip(").,") if m else ""
    rest = URL_RE.sub(" ", text)
    phone = find_phone(rest)
    rest_np = PHONE_RE.sub(" ", rest)
    rest_np = re.sub(r"\btel\.?\s*:?", " ", rest_np, flags=re.I)
    when = parse_date(rest_np)
    note = re.sub(r"\s+", " ", rest_np).strip(" ,.-:")
    return url, phone, when, note


def add(text, fetch=None):
    """fetch(url) -> info объявления (или исключение). Возвращает новую запись."""
    url, phone, when, note = split_text(text)
    if not url and not phone:
        raise ValueError("no_url")
    info = {}
    if url and fetch:
        try:
            info = fetch(url) or {}
        except Exception:
            info = {}
    if not phone:
        phone = find_phone(info.get("desc") or "")
    with LOCK:
        if url:
            for it in DATA["items"]:
                if it.get("url") == url and it.get("status") != "done":
                    it.update(phone=norm_phone(phone) or it.get("phone", ""),
                              note=(it.get("note", "") + ("\n" if it.get("note") and note else "") + note).strip(),
                              remind=when.isoformat() if when else it.get("remind", ""))
                    _save()
                    return it
        it = {"id": secrets.token_hex(4), "url": url, "phone": norm_phone(phone), "note": note,
              "remind": when.isoformat() if when else "", "status": "open", "created": time.time(),
              "title": info.get("title") or "", "img": (info.get("images") or [""])[0] if info.get("images") else info.get("img", ""),
              "price": info.get("price"), "rent": info.get("rent"),
              "district": info.get("district") or "", "sub": info.get("sub") or "",
              "street": info.get("street") or "", "rooms": info.get("rooms") or "", "area": info.get("area") or ""}
        DATA["items"].insert(0, it)
        _save()
        return it


def add_from(item, note="", when=None):
    """Из вкладки «Собственники»: данные уже есть, телефона нет."""
    with LOCK:
        for it in DATA["items"]:
            if it.get("url") == item.get("url") and it.get("status") != "done":
                return it
        it = {"id": secrets.token_hex(4), "url": item.get("url", ""), "phone": "", "note": note,
              "remind": when.isoformat() if when else "", "status": "open", "created": time.time(),
              "title": item.get("title", ""), "img": item.get("img", ""), "price": item.get("price"),
              "rent": item.get("rent"), "district": item.get("district", ""), "sub": item.get("sub", ""),
              "street": item.get("street", ""), "rooms": item.get("rooms", ""), "area": item.get("area", "")}
        DATA["items"].insert(0, it)
        _save()
        return it


def update(cid, **kw):
    with LOCK:
        it = next((x for x in DATA["items"] if x["id"] == cid), None)
        if not it:
            raise KeyError(cid)
        if "phone" in kw:
            it["phone"] = norm_phone(kw["phone"])
        if "note" in kw:
            it["note"] = str(kw["note"])[:2000]
        if "remind" in kw:
            r = str(kw["remind"] or "")
            if r and not re.match(r"^\d{4}-\d{2}-\d{2}$", r):
                d = parse_date(r)
                r = d.isoformat() if d else ""
            it["remind"] = r
        if "status" in kw and kw["status"] in ("open", "done"):
            it["status"] = kw["status"]
            it["done_at"] = time.time() if kw["status"] == "done" else None
        _save()
        return it


def delete(cid):
    with LOCK:
        DATA["items"] = [x for x in DATA["items"] if x["id"] != cid]
        _save()


def due(day=None):
    day = (day or today()).isoformat()
    with LOCK:
        return [x for x in DATA["items"] if x.get("status") == "open" and x.get("remind") and x["remind"] <= day]


def due_count():
    return len(due())


def public():
    with LOCK:
        items = [dict(x, phone_pretty=pretty_phone(x.get("phone", ""))) for x in DATA["items"]]
    return {"items": items, "today": today().isoformat(), "due": due_count()}


def loop(notify, log):
    """Утром (9:30) — одно напоминание со списком, кому сегодня перезвонить."""
    while True:
        try:
            now = dt.datetime.now()
            d = now.date().isoformat()
            if (now.hour, now.minute) >= REMIND_AT and DATA.get("notified") != d:
                lst = due()
                if lst:
                    names = [(x.get("title") or x.get("street") or pretty_phone(x.get("phone", "")))[:40] for x in lst[:4]]
                    notify(len(lst), names)
                DATA["notified"] = d
                _save()
        except Exception as e:
            log("перезвоны:", e)
        time.sleep(60)
