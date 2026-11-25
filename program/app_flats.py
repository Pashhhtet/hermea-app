"""Папка «Квартиры»: готовые квартиры, их фото, описание (opis.txt) и пометки (.hermea.json),
плюс уменьшенные картинки для окна. Чистые операции с файлами, без сети. Совместимо с Python 3.9.
"""
import json
import os
import re
import sys
import threading
import time
from collections import OrderedDict

import cv2
import numpy as np

import hermea

ROOT = hermea.ROOT
KV = os.path.realpath(os.path.join(ROOT, "Квартиры"))
META = ".hermea.json"
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")
LOCK = threading.RLock()


def log(*a):
    try:
        sys.__stdout__.write(time.strftime("[%d.%m %H:%M:%S] ") + " ".join(str(x) for x in a) + "\n")
        sys.__stdout__.flush()
    except Exception:
        pass


def safe_join(base, rel):
    p = os.path.realpath(os.path.join(base, rel))
    if p != base and not p.startswith(base + os.sep):
        raise PermissionError("путь вне папки")
    return p


def natural_key(name):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def flat_photos(path):
    """Готовые фото квартиры: hermea/p1_hermea.jpg… или (ручная обработка) просто фото в папке."""
    ready = os.path.join(path, "hermea")
    if os.path.isdir(ready):
        names = [n for n in os.listdir(ready) if n.lower().endswith(IMG_EXT) and not n.startswith(".")]
        return ["hermea/" + n for n in sorted(names, key=natural_key)]
    names = [n for n in os.listdir(path) if n.lower().endswith(IMG_EXT) and not n.startswith(".")]
    return sorted(names, key=natural_key)


def read_meta(path):
    try:
        return json.load(open(os.path.join(path, META), encoding="utf-8"))
    except Exception:
        return {}


def write_meta(path, **upd):
    m = read_meta(path)
    m.update(upd)
    try:
        json.dump(m, open(os.path.join(path, META), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception as e:
        log("meta:", e)


def read_opis(path):
    p = os.path.join(path, "opis.txt")
    if not os.path.exists(p):
        return None, ""
    txt = hermea.read_text(p)
    if "\n---\n" in txt:
        body, tail = txt.split("\n---\n", 1)
    else:
        body, tail = txt, ""
    return body.strip("\n"), tail


def tail_value(tail, key):
    m = re.search(r"(?m)^" + re.escape(key) + r":\s*(.+)$", tail or "")
    return m.group(1).strip() if m else ""


def parse_facts(body):
    facts = []
    if not body:
        return facts
    for key, label in (("Оренда", "Аренда"), ("Адмін. платіж", "Czynsz"), ("Разом", "Всего"), ("Застава", "Залог")):
        m = re.search(re.escape(key) + r":\s*([^\n]+)", body)
        if m and m.group(1).strip() not in ("—", "-", ""):
            facts.append({"label": label, "value": m.group(1).strip(), "main": key == "Разом"})
    return facts


_FLATS_CACHE = {"key": None, "data": None}
STATE = {"version": 1}      # растёт, когда готова новая квартира: окно перечитывает список


def list_flats():
    if not os.path.isdir(KV):
        return []
    try:
        names = [n for n in os.listdir(KV) if not n.startswith((".", "_")) and os.path.isdir(os.path.join(KV, n))]
    except OSError:
        return []
    key = (STATE["version"], tuple(sorted((n, os.stat(os.path.join(KV, n)).st_mtime) for n in names)))
    if _FLATS_CACHE["key"] == key:
        return _FLATS_CACHE["data"]
    out = []
    for n in names:
        p = os.path.join(KV, n)
        try:
            photos = flat_photos(p)
            meta = read_meta(p)
            when = os.stat(p).st_mtime
            if meta.get("created"):
                try:
                    when = time.mktime(time.strptime(meta["created"], "%Y-%m-%d %H:%M"))
                except Exception:
                    pass
            body, tail = read_opis(p)
            url = meta.get("url") or tail_value(tail, "Оригинал")
            out.append({"f": n, "name": n, "count": len(photos),
                        "cover": f"{n}/{photos[0]}" if photos else None,
                        "when": when, "url": url,
                        "manual": "ручная обработка" in n})
        except Exception as e:
            log("flat", n, e)
    out.sort(key=lambda x: -x["when"])
    _FLATS_CACHE.update(key=key, data=out)
    return out


def flat_detail(name):
    p = safe_join(KV, name)
    if not os.path.isdir(p):
        raise FileNotFoundError("папки уже нет")
    meta = read_meta(p)
    mp = meta.get("photos") or {}
    items = []
    for rel in flat_photos(p):
        base = os.path.basename(rel)
        src = mp.get(base)
        orig = None
        if src and os.path.exists(os.path.join(p, "oryginal", src)):
            orig = f"{name}/oryginal/{src}"
        items.append({"f": f"{name}/{rel}", "orig": orig, "name": base})
    body, tail = read_opis(p)
    url = meta.get("url") or tail_value(tail, "Оригинал")
    oto = None
    try:
        oto = open(os.path.join(p, "opis_otodom.txt"), encoding="utf-8").read()
    except Exception:
        pass
    return {"f": name, "name": name, "photos": items, "opis": body, "has_opis": body is not None, "otodom": oto,
            "facts": parse_facts(body), "url": url, "site": meta.get("site") or tail_value(tail, "Сайт"),
            "telegram": meta.get("telegram"), "created": meta.get("created"), "kind": meta.get("kind")}


def find_flat_by_url(url):
    cu = hermea.clean_url(url)
    for f in list_flats():
        if f.get("url") and hermea.clean_url(f["url"]) == cu:
            return f["f"]
    return None


def today_stats(flats):
    t0 = time.mktime(time.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d"))
    today = [f for f in flats if f["when"] >= t0]
    return {"flats": len(today), "photos": sum(f["count"] for f in today)}


# ---------------------------------------------------------------- картинки для окна
_THUMBS = OrderedDict()


def thumb_bytes(path, w):
    st = os.stat(path)
    key = (path, st.st_mtime, w)
    with LOCK:
        if key in _THUMBS:
            _THUMBS.move_to_end(key)
            return _THUMBS[key]
    data = np.fromfile(path, np.uint8)
    flag = cv2.IMREAD_COLOR
    try:
        from PIL import Image
        side = max(Image.open(path).size)
        for f, fl in ((8, cv2.IMREAD_REDUCED_COLOR_8), (4, cv2.IMREAD_REDUCED_COLOR_4), (2, cv2.IMREAD_REDUCED_COLOR_2)):
            if side / f >= w * 1.05:
                flag = fl
                break
    except Exception:
        pass
    img = cv2.imdecode(data, flag)
    if img is None:
        raise ValueError("не картинка")
    h, wd = img.shape[:2]
    if max(h, wd) > w:
        k = w / max(h, wd)
        img = cv2.resize(img, (max(1, int(wd * k)), max(1, int(h * k))), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 86])
    b = buf.tobytes()
    with LOCK:
        _THUMBS[key] = b
        while len(_THUMBS) > 500:
            _THUMBS.popitem(last=False)
    return b


def small_jpg(jpg, w=560):
    img = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_REDUCED_COLOR_2)
    if img is None:
        return jpg
    h, wd = img.shape[:2]
    if max(h, wd) > w:
        k = w / max(h, wd)
        img = cv2.resize(img, (int(wd * k), int(h * k)), interpolation=cv2.INTER_AREA)
    return cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 84])[1].tobytes()
