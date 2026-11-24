"""Клиенты-наниматели: карточки, просмотренные объекты, связь со СВК.

Хранится только на этом компьютере: _program/app_clients.json (личные данные — паспорт, PESEL —
никогда не уходят в репозиторий обновлений). Совместимо с Python 3.9.
"""
import datetime as dt
import json
import os
import secrets
import threading
import time

FILE = None
LOCK = threading.RLock()
TEXT = ("name", "phone", "email", "address", "id_doc", "pesel", "lang", "source", "package", "status",
        "type", "location", "area", "parking", "budget", "residents", "children", "pets", "move_in", "term",
        "income", "okazjonalny", "must", "not_considered", "extra", "notes", "lost_reason", "commission")
STATUSES = ("new", "search", "shows", "contract", "deal", "lost")


def init(prog_dir):
    global FILE
    FILE = os.path.join(prog_dir, "app_clients.json")


def _load():
    try:
        d = json.load(open(FILE, encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("clients"), list):
            return d
    except Exception:
        pass
    return {"clients": []}


def _save(d):
    tmp = FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, FILE)


def _clean(body):
    out = {}
    for k in TEXT:
        if k in body:
            v = body[k]
            out[k] = (str(v).strip()[:400] if v is not None else "")
    if out.get("status") and out["status"] not in STATUSES:
        out.pop("status")
    if "package" in out and out["package"] not in ("", "SMART", "COMFORT"):
        out["package"] = ""
    return out


def summary():
    with LOCK:
        d = _load()
    out = []
    for c in d["clients"]:
        out.append({k: c.get(k, "") for k in ("id", "name", "phone", "status", "package", "budget", "location",
                                               "source", "created", "updated", "lang")}
                   | {"viewed": len(c.get("viewed") or []), "contract_at": c.get("contract_at")})
    out.sort(key=lambda c: (c["status"] in ("deal", "lost"), -(c.get("updated") or 0)))
    return out


def get(cid):
    with LOCK:
        for c in _load()["clients"]:
            if c.get("id") == cid:
                return c
    return None


def create(body):
    """-> (клиент, события для СВК)"""
    with LOCK:
        d = _load()
        c = {"id": secrets.token_hex(5), "created": time.time(), "updated": time.time(), "status": "new",
             "lang": "ua", "source": "direct", "viewed": []}
        c.update(_clean(body))
        d["clients"].append(c)
        _save(d)
    ev = [{"op": "add", "m": c["source"] if c.get("source") in ("direct", "agents", "duty") else "direct", "d": 1,
           "note": c.get("name") or ""}]
    return c, ev


def update(cid, body):
    with LOCK:
        d = _load()
        for c in d["clients"]:
            if c.get("id") == cid:
                before = c.get("status")
                c.update(_clean(body))
                c["updated"] = time.time()
                _save(d)
                ev = []
                if c.get("status") == "lost" and before != "lost":
                    ev.append({"op": "add", "m": "lost", "d": 1,
                               "note": ", ".join(x for x in (c.get("name"), c.get("lost_reason")) if x)})
                if c.get("status") == "deal" and before != "deal":
                    ev.append({"op": "add", "m": "main", "d": 1, "note": c.get("name") or ""})
                return c, ev
    raise KeyError(cid)


def delete(cid):
    with LOCK:
        d = _load()
        d["clients"] = [c for c in d["clients"] if c.get("id") != cid]
        _save(d)


def viewed(cid, body):
    """Добавить/удалить просмотренный объект. Новый просмотр = «показ проведён» в СВК."""
    with LOCK:
        d = _load()
        for c in d["clients"]:
            if c.get("id") != cid:
                continue
            lst = c.setdefault("viewed", [])
            ev = []
            if body.get("remove"):
                c["viewed"] = [o for o in lst if o.get("id") != body["remove"]]
            else:
                o = {"id": secrets.token_hex(4),
                     "date": str(body.get("date") or dt.date.today().strftime("%d.%m.%Y"))[:20],
                     "address": str(body.get("address") or "")[:160], "rooms": str(body.get("rooms") or "")[:4],
                     "rent": str(body.get("rent") or "")[:10], "admin": str(body.get("admin") or "")[:10],
                     "link": str(body.get("link") or "")[:400]}
                lst.append(o)
                if c.get("status") in ("new", "search"):
                    c["status"] = "shows"
                ev.append({"op": "add", "m": "shows", "d": 1, "note": f"{c.get('name', '')}: {o['address']}".strip(": ")})
            c["updated"] = time.time()
            _save(d)
            return c, ev
    raise KeyError(cid)


def mark_contract(cid):
    """Договор сформирован. Первый раз — «договор клиент–агентство» в СВК."""
    with LOCK:
        d = _load()
        for c in d["clients"]:
            if c.get("id") == cid:
                first = not c.get("contract_at")
                c["contract_at"] = c.get("contract_at") or time.time()
                if c.get("status") in ("new", "search", "shows"):
                    c["status"] = "contract"
                c["updated"] = time.time()
                _save(d)
                return c, ([{"op": "add", "m": "coop", "d": 1, "note": c.get("name") or ""}] if first else [])
    raise KeyError(cid)


def all_clients():
    with LOCK:
        return list(_load()["clients"])


def match_mark(cid, seen=None, skip=None):
    """Подбор: отметить показанные варианты (seen) или убрать неподходящий (skip)."""
    with LOCK:
        d = _load()
        for c in d["clients"]:
            if c.get("id") != cid:
                continue
            if seen:
                c["match_seen"] = list(dict.fromkeys((c.get("match_seen") or []) + [str(x) for x in seen]))[-1500:]
            if skip:
                c["match_skip"] = list(dict.fromkeys((c.get("match_skip") or []) + [str(skip)]))[-1500:]
            _save(d)
            return c
    raise KeyError(cid)
