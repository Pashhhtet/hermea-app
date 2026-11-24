"""СВК: ежедневная сводка агента (лиды, публикации, показы, договоры, сделки).

Всё хранится в _program/app_svk.json:
  {"agent": "...", "defaults": {метрика: план на день},
   "days": {"2026-11-24": {"log": [{"id", "ts", "m", "d", "note"}],   # счётчики — события дня
                           "set": {метрика: значение},                # «на сегодня»: клиенты, ожидаемая комиссия…
                           "plan": {метрика: план}}}}                 # план дня, если менялся вручную
Счётчик дня = сумма событий, поэтому «−1» просто убирает последнее событие, и журнал всегда сходится.
Совместимо с Python 3.9.
"""
import datetime as dt
import json
import os
import secrets
import threading
import time

PATH = None
LOCK = threading.RLock()

# метрики, которые копятся событиями за день
COUNT = ("direct", "agents", "duty", "ads", "coop", "open", "excl", "shows_plan", "shows",
         "deposit", "main", "closed", "comm", "lost")
# метрики «на сегодня»: переносятся со вчерашнего дня, пока их не поменяли
SNAP = ("clients", "pending", "expected")
ALL = COUNT + SNAP
DEFAULTS = {"leads": 5, "direct": 5, "agents": 0, "duty": 0, "ads": 15, "coop": 1, "open": 2, "excl": 0,
            "deposit": 0, "main": 0, "closed": 0, "comm": 0, "lost": 0}
PLANNABLE = tuple(DEFAULTS)
MAX_ABS = 10_000_000


def init(prog_dir):
    global PATH
    PATH = os.path.join(prog_dir, "app_svk.json")


def _load():
    try:
        with open(PATH, encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict):
            d.setdefault("days", {})
            d.setdefault("defaults", {})
            d.setdefault("agent", "")
            return d
    except Exception:
        pass
    return {"agent": "", "defaults": {}, "days": {}}


def _save(d):
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, PATH)


def _day_ok(s):
    try:
        dt.date.fromisoformat(s)
        return True
    except Exception:
        return False


def _num(v, lo=-MAX_ABS, hi=MAX_ABS):
    try:
        x = float(v)
    except Exception:
        raise ValueError("bad number")
    if x != x or x < lo or x > hi:
        raise ValueError("bad number")
    return int(x) if x == int(x) else round(x, 2)


def defaults(d=None):
    d = d or _load()
    out = dict(DEFAULTS)
    for k, v in (d.get("defaults") or {}).items():
        if k in DEFAULTS and isinstance(v, (int, float)):
            out[k] = v
    return out


def _values(day):
    v = {k: 0 for k in COUNT}
    for e in day.get("log") or []:
        if e.get("m") in v:
            v[e["m"]] += e.get("d") or 0
    for k in COUNT:
        v[k] = max(0, v[k])
        if isinstance(v[k], float):
            v[k] = round(v[k], 2)
    return v


def _snap_before(d, day_s):
    """Последние известные значения «на сегодня» строго до этого дня."""
    out = {}
    for k in sorted(d["days"], reverse=True):
        if k >= day_s:
            continue
        for m, val in (d["days"][k].get("set") or {}).items():
            out.setdefault(m, val)
        if len(out) == len(SNAP):
            break
    return out


def since(d):
    """С какого дня считаем план: первый день, который вообще заполняли (раньше СВК в программе не вели)."""
    keys = [k for k in d["days"] if _day_ok(k)]
    first = min(keys) if keys else dt.date.today().isoformat()
    return min(first, d.get("since") or first)


def day_view(d, day_s, defs, start=None):
    day = d["days"].get(day_s) or {}
    v = _values(day)
    prev = _snap_before(d, day_s)
    own = day.get("set") or {}
    for m in SNAP:
        v[m] = own.get(m, prev.get(m, 0))
    v["leads"] = v["direct"] + v["agents"] + v["duty"]
    wd = dt.date.fromisoformat(day_s).weekday()
    start = start or since(d)
    plan = {k: (defs[k] if wd < 5 and day_s >= start else 0) for k in PLANNABLE}
    plan.update({k: val for k, val in (day.get("plan") or {}).items() if k in PLANNABLE})
    plan["shows"] = v["shows_plan"]                       # план показов — это назначенные
    for m in SNAP:                                       # план «на сегодня» — вчерашний факт
        plan[m] = prev.get(m, 0)
    return {"date": day_s, "v": v, "plan": plan, "log": day.get("log") or [],
            "touched": bool(day.get("log") or day.get("set")), "set": sorted(own)}


def get(frm, to):
    if not (_day_ok(frm) and _day_ok(to)):
        raise ValueError("bad date")
    a, b = dt.date.fromisoformat(frm), dt.date.fromisoformat(to)
    if b < a or (b - a).days > 400:
        raise ValueError("bad range")
    with LOCK:
        d = _load()
    defs = defaults(d)
    start = since(d)
    days = []
    x = a
    while x <= b:
        days.append(day_view(d, x.isoformat(), defs, start))
        x += dt.timedelta(days=1)
    return {"agent": d.get("agent") or "", "defaults": defs, "days": days, "since": start, "today": dt.date.today().isoformat()}


def _day(d, day_s):
    if not _day_ok(day_s):
        raise ValueError("bad date")
    return d["days"].setdefault(day_s, {"log": [], "set": {}, "plan": {}})


def apply(op):
    """Одна правка. Возвращает обновлённый день."""
    kind = op.get("op")
    day_s = str(op.get("date") or "")
    with LOCK:
        d = _load()
        if kind == "agent":
            d["agent"] = str(op.get("name") or "")[:60]
        elif kind == "defaults":
            cur = d.setdefault("defaults", {})
            for k, v in (op.get("values") or {}).items():
                if k in DEFAULTS:
                    cur[k] = _num(v, 0)
        else:
            day = _day(d, day_s)
            m = op.get("m")
            if kind == "add":
                if m not in COUNT:
                    raise ValueError("bad metric")
                n = _num(op.get("d", 1))
                if n > 0:
                    day.setdefault("log", []).append({
                        "id": secrets.token_hex(4), "ts": int(time.time()), "m": m, "d": n,
                        "note": str(op.get("note") or "")[:200]})
                elif n < 0:                               # «−1»: убираем последнее событие этой метрики
                    log = day.setdefault("log", [])
                    for i in range(len(log) - 1, -1, -1):
                        if log[i].get("m") == m:
                            ev = log[i]
                            if ev.get("d", 0) > 1 and m not in ("comm",):
                                ev["d"] -= 1
                            else:
                                log.pop(i)
                            break
            elif kind == "fix":                           # ввели число руками: событие-поправка
                if m not in COUNT:
                    raise ValueError("bad metric")
                want = _num(op.get("value"), 0)
                have = _values(day)[m]
                if want != have:
                    day.setdefault("log", []).append({
                        "id": secrets.token_hex(4), "ts": int(time.time()), "m": m, "d": round(want - have, 2),
                        "note": "", "fix": True})
            elif kind == "set":
                if m not in SNAP:
                    raise ValueError("bad metric")
                day.setdefault("set", {})[m] = _num(op.get("value"), 0)
            elif kind == "plan":
                if m not in PLANNABLE:
                    raise ValueError("bad metric")
                if op.get("value") in (None, ""):
                    day.setdefault("plan", {}).pop(m, None)
                else:
                    day.setdefault("plan", {})[m] = _num(op.get("value"), 0)
            elif kind == "undo":
                eid = op.get("id")
                day["log"] = [e for e in day.get("log") or [] if e.get("id") != eid]
            elif kind == "note":
                for e in day.get("log") or []:
                    if e.get("id") == op.get("id"):
                        e["note"] = str(op.get("note") or "")[:200]
            else:
                raise ValueError("bad op")
            if not day.get("log") and not day.get("set") and not day.get("plan"):
                d["days"].pop(day_s, None)
        if not d.get("since") and d["days"]:
            d["since"] = min(min(d["days"]), dt.date.today().isoformat())
        _save(d)
        defs = defaults(d)
        return day_view(d, day_s, defs) if _day_ok(day_s) else {"ok": True}


def today_touched():
    with LOCK:
        d = _load()
    day = d["days"].get(dt.date.today().isoformat()) or {}
    return bool(day.get("log") or day.get("set"))
