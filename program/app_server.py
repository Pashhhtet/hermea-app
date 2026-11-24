"""Сервер окна Hermea «Обработка фото» (запускается из hermea_app.py).

Только для этого компьютера: слушает 127.0.0.1, каждый запрос проверяется секретным ключом.
Совместимо с Python 3.9.
"""
import io
import json
import os
import queue
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import traceback
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import cv2
import numpy as np

import hermea
import app_i18n
import app_searches
import app_svk
import app_clients
import app_contract
import app_market
import app_owners
import app_update
from app_i18n import tr

PROG = hermea.PROG
ROOT = hermea.ROOT
KV = os.path.realpath(os.path.join(ROOT, "Квартиры"))
UI_DIR = os.path.join(PROG, "app")
PORT_FILE = os.path.join(PROG, ".app_port")
SETTINGS_FILE = os.path.join(PROG, "app_settings.json")
META = ".hermea.json"
IDLE_EXIT = 180
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")

TOKEN = os.environ.get("HERMEA_TOKEN") or secrets.token_urlsafe(18)   # после обновления ключ тот же
SRV = None
PORT = 0
LOCK = threading.RLock()
JOBS = []                 # все задания этого запуска (новые в конце)
Q = queue.Queue()
CURRENT = None            # задание, которое обрабатывается сейчас
LAST_SEEN = time.time()
CLOSED_AT = 0.0           # окно закрыли (страница прислала «пока»)
FLATS_VERSION = 1
TG = {"state": "checking", "key": "tg_checking", "hint_key": "", "bot": "", "detail": ""}
SETTINGS = {"telegram": True, "theme": "auto", "lang": "ru", "scale": 100, "agent_name": "", "agent_level": 30}
UPLOAD_ROOT = os.path.join(__import__("tempfile").gettempdir(), "hermea_uploads")
WARM = {"state": "idle"}


def log(*a):
    try:
        sys.__stdout__.write(time.strftime("[%d.%m %H:%M:%S] ") + " ".join(str(x) for x in a) + "\n")
        sys.__stdout__.flush()
    except Exception:
        pass


# ======================================================================= вывод программы
class Tee(io.TextIOBase):
    """Всё, что печатает hermea.py, идёт в журнал файла и в журнал текущего задания."""

    def __init__(self, base):
        self.base = base
        self.buf = ""

    def writable(self):
        return True

    def write(self, s):
        try:
            self.base.write(s)
            self.base.flush()
        except Exception:
            pass
        job = CURRENT
        if job is not None and threading.current_thread() is WORKER:
            self.buf += s
            while "\n" in self.buf:
                line, self.buf = self.buf.split("\n", 1)
                if line.strip():
                    job.log.append(line.strip())
                    del job.log[:-200]
        return len(s)

    def flush(self):
        try:
            self.base.flush()
        except Exception:
            pass


# ======================================================================= настройки
def load_settings():
    try:
        SETTINGS.update(json.load(open(SETTINGS_FILE, encoding="utf-8")))
    except Exception:
        pass
    apply_lang()


def apply_lang():
    if SETTINGS.get("lang") not in app_i18n.LANGS:
        SETTINGS["lang"] = "ru"
    app_i18n.CURRENT["lang"] = SETTINGS["lang"]


def save_settings():
    try:
        json.dump(SETTINGS, open(SETTINGS_FILE, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception as e:
        log("settings:", e)


# ======================================================================= квартиры
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


def list_flats():
    if not os.path.isdir(KV):
        return []
    try:
        names = [n for n in os.listdir(KV) if not n.startswith((".", "_")) and os.path.isdir(os.path.join(KV, n))]
    except OSError:
        return []
    key = (FLATS_VERSION, tuple(sorted((n, os.stat(os.path.join(KV, n)).st_mtime) for n in names)))
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
    return {"f": name, "name": name, "photos": items, "opis": body, "has_opis": body is not None,
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


# ======================================================================= картинки
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


# ======================================================================= Telegram
def tg_check():
    token, chat = hermea.tg_config()
    if not token:
        TG.update(state="off", key="tg_off", hint_key="tg_off_hint", detail="")
        return
    TG.update(state="checking", key="tg_checking", hint_key="", detail="")
    try:
        me = hermea.tg_call(token, "getMe")["result"]
    except Exception as e:
        msg = str(e)
        if any(x in msg for x in ("Unauthorized", "Not Found", "401", "404")):
            TG.update(state="error", key="tg_bad_token", hint_key="tg_bad_token_hint", detail="")
        else:
            TG.update(state="error", key="tg_no_net", hint_key="", detail=msg[:200])
        return
    bot = "@" + me.get("username", "bot")
    if not chat:
        chat = tg_pick_chat(token)
    if not chat:
        TG.update(state="nochat", key="tg_nochat", hint_key="tg_nochat_hint", bot=bot, detail="")
        _tg_wait_chat()
        return
    TG.update(state="ok", key="tg_ok", hint_key="tg_ok_hint", bot=bot, detail="")


def tg_pick_chat(token):
    """CHAT_ID пустой: берём чат, где боту последним написали /start, сохраняем и здороваемся."""
    try:
        hermea.tg_call(token, "deleteWebhook")
    except Exception:
        pass
    try:
        chats = hermea.tg_find_chat(token)
    except Exception as e:
        log("telegram:", e)
        return ""
    if not chats:
        return ""
    cid, title = list(chats.items())[-1]
    hermea._save_chat(cid)
    log(f"telegram: выбран чат «{title}» ({cid})")
    try:
        hermea.tg_call(token, "sendMessage", {"chat_id": cid, "text": "✅ HERMEA подключена к этому чату"})
    except Exception as e:
        log("telegram:", e)
    return str(cid)


_TG_WAIT = {"on": False}


def _tg_wait_chat():
    """Пока чат не выбран — каждые 10 секунд (до 15 минут) смотрим, не написали ли боту /start."""
    if _TG_WAIT["on"]:
        return
    _TG_WAIT["on"] = True

    def run():
        try:
            for _ in range(90):
                time.sleep(10)
                token, chat = hermea.tg_config()
                if not token:
                    return
                if chat or tg_pick_chat(token):
                    tg_check()
                    return
        finally:
            _TG_WAIT["on"] = False
    threading.Thread(target=run, daemon=True).start()


def tg_public():
    return {"state": TG["state"], "text": tr(TG["key"]),
            "hint": tr(TG["hint_key"], bot=TG.get("bot", "")) if TG.get("hint_key") else TG.get("detail", "")}


def tg_ready():
    token, chat = hermea.tg_config()
    return (token, chat) if (token and chat and TG.get("state") in ("ok", "checking", "error")) else (None, None)


def pending_list():
    if not os.path.exists(hermea.PENDING):
        return []
    try:
        items = [l.strip() for l in hermea.read_text(hermea.PENDING).splitlines() if l.strip()]
    except Exception:
        return []
    return [os.path.basename(i) for i in OrderedDict.fromkeys(items) if os.path.isdir(i)]


# ======================================================================= задания
class Cancelled(Exception):
    pass


class Job:
    def __init__(self, url, telegram, kind="url", files=None, title="", upload_dir=None, no_fee=False):
        self.id = secrets.token_hex(4)
        self.no_fee = bool(no_fee)    # «без комиссии» — строка сверху в описании
        self.kind = kind             # url — объявление с сайта; local — свои фото
        self.files = files or []
        self.title = title
        self.upload_dir = upload_dir
        self.url = url
        self.telegram = telegram
        self.status = "queued"       # queued → running → done / error / cancelled
        self.step = "queued"         # listing → photos → saving → telegram → done
        self.total = 0
        self.k = 0
        self.n = 0
        self.name = ""
        self.out = None
        self.existed = True
        self.thumbs = []
        self.facts = []
        self.log = []
        self.error = ""
        self.tg = ""
        self.tg_error = ""
        self.cancel = False
        self.created = time.time()
        self.started = None
        self.finished = None
        self.hidden = False

    def public(self):
        return {"id": self.id, "kind": self.kind, "title": self.title, "url": self.url, "status": self.status, "step": self.step,
                "total": self.total, "k": self.k, "n": self.n, "name": self.name,
                "f": os.path.basename(self.out) if self.out else None,
                "facts": self.facts, "error": self.error, "tg": self.tg, "tg_error": self.tg_error,
                "telegram": self.telegram, "log": self.log[-6:], "started": self.started,
                "finished": self.finished, "thumbs": len(self.thumbs), "no_fee": self.no_fee}


def facts_from_info(i):
    f = []
    pr, rent = i.get("price"), i.get("rent")
    if pr:
        f.append({"label": "Аренда", "value": hermea.pln(pr), "main": False})
    if rent:
        f.append({"label": "Czynsz", "value": hermea.pln(rent), "main": False})
    if pr:
        f.append({"label": "Всего", "value": hermea.pln(pr + (rent or 0)), "main": True})
    if i.get("deposit"):
        f.append({"label": "Залог", "value": hermea.pln(i["deposit"]), "main": False})
    return f


_SESS = {"s": None}


def session():
    if _SESS["s"] is None:
        _SESS["s"] = hermea.http()
    return _SESS["s"]


def add_to_links(url):
    """Ссылку дописываем и в «ссылки.txt» (с датой дня) — как раньше, чтобы был общий список."""
    url = hermea.clean_url(url)
    try:
        path = hermea._find(hermea.LINKS_NAME)
        txt = hermea.read_text(path) if os.path.exists(path) else ""
        if hermea.clean_url(url) in txt or url in txt:
            return
        today = time.strftime("%d.%m.%Y")
        dates = re.findall(r"(?m)^\s*=+\s*(\d{2}\.\d{2}\.\d{4})\s*=+\s*$", txt)
        add = ""
        if txt and not txt.endswith("\n"):
            add += "\n"
        if not dates or dates[-1] != today:
            add += f"\n===== {today} =====\n"
        add += url + "\n"
        with open(path, "a", encoding="utf-8") as f:
            f.write(add)
    except Exception as e:
        log("links:", e)


def notify(title, text):
    if os.name == "nt":                      # Windows: всплывающее уведомление у часов
        ps = ("Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; "
              "$n = New-Object System.Windows.Forms.NotifyIcon; $n.Icon = [System.Drawing.SystemIcons]::Information; "
              "$n.Visible = $true; $n.ShowBalloonTip(8000, $env:HN_T, $env:HN_X, 'Info'); Start-Sleep -Seconds 9; $n.Dispose()")
        try:
            subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                             env=dict(os.environ, HN_T=title, HN_X=text), creationflags=0x08000000,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return
    if sys.platform != "darwin":
        return
    def esc(s):
        return s.replace("\\", "\\\\").replace('"', '\\"')
    try:
        subprocess.Popen(["osascript", "-e",
                          f'display notification "{esc(text)}" with title "{esc(title)}" sound name "Glass"'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def friendly(e):
    msg = str(e) or e.__class__.__name__
    low = msg.lower()
    if "curl_cffi" in msg:
        return tr("err_lib")
    if "не нашёл данные" in msg or "капч" in msg:
        return tr("err_no_data")
    if "не пускает" in msg or " 403" in msg or " 429" in msg:
        return tr("err_blocked")
    if "не нашёл фото" in msg:
        return tr("err_no_photos")
    if "ни одно фото" in msg:
        return tr("err_none_processed")
    if any(x in low for x in ("connect", "resolve", "timed out", "timeout", "network", "curl: (", "ssl")):
        return tr("err_net")
    return msg[0].upper() + msg[1:]


def run_job(job):
    global CURRENT, FLATS_VERSION
    job.status, job.step, job.started = "running", "listing", time.time()
    CURRENT = job
    log("▶", job.url or job.title)

    def progress(ev, **kw):
        if ev == "listing":
            job.out, job.existed = kw["out"], kw.get("existed", True)
            job.name = os.path.basename(job.out)
            job.total = kw["total"]
            job.facts = facts_from_info(kw["info"])
            job.step = "photos"
        elif ev == "photo_start":
            job.k = kw["k"]
        elif ev == "photo":
            job.k, job.n = kw["k"], kw["n"]
            try:
                job.thumbs.append(small_jpg(kw["jpg"]))
            except Exception:
                job.thumbs.append(kw["jpg"])
            if job.k >= job.total:
                job.step = "saving"
        if job.cancel:
            raise Cancelled()

    try:
        token, chat = tg_ready()
        if token and job.telegram and pending_list():
            try:
                hermea.tg_pending_flush(token, chat)
            except Exception as e:
                log("pending:", e)
        if job.kind == "local":
            out, n = hermea.process_local(job.title, job.files, progress=progress, no_fee=job.no_fee)
        else:
            out, n = hermea.process_listing(session(), hermea.clean_url(job.url), progress=progress, no_fee=job.no_fee)
        job.out, job.n, job.name = out, n, os.path.basename(out)
        if job.kind == "url":
            add_to_links(job.url)
        write_meta(out, created=time.strftime("%Y-%m-%d %H:%M"))
        if job.telegram:
            job.step = "telegram"
            token, chat = tg_ready()
            if token:
                try:
                    hermea.tg_send(token, chat, out)
                    job.tg = "sent"
                    write_meta(out, telegram={"ok": True, "at": time.strftime("%Y-%m-%d %H:%M")})
                except Exception as e:
                    job.tg, job.tg_error = "pending", str(e)
                    hermea.tg_pending_add(out)
                    write_meta(out, telegram={"ok": False, "error": str(e)[:300]})
            elif hermea.tg_config()[0]:
                job.tg, job.tg_error = "pending", tg_public()["text"]
                hermea.tg_pending_add(out)
            else:
                job.tg = "off"
        else:
            job.tg = "skipped"
        job.status, job.step = "done", "done"
        log("✓", job.name, n, "фото", "telegram:", job.tg)
        notify(tr("done_title"), tr("done_text", name=job.name, n=n) + (tr("done_tg") if job.tg == "sent" else ""))
    except Cancelled:
        job.status, job.step = "cancelled", "cancelled"
        remove_partial(job, always=True)
        log("✗ отменено", job.url or job.title)
    except Exception as e:
        job.status, job.error = "error", friendly(e)
        log("✗", job.url or job.title, e)
        traceback.print_exc()
        remove_partial(job)
        notify(tr("fail_title"), job.error[:120])
    finally:
        if job.upload_dir:
            shutil.rmtree(job.upload_dir, ignore_errors=True)
        job.finished = time.time()
        CURRENT = None
        with LOCK:
            FLATS_VERSION += 1


def remove_partial(job, always=False):
    """Убираем недоделанную папку — только если её создало это задание."""
    out = job.out
    if not out or job.existed or not os.path.isdir(out):
        return
    if not out.startswith(KV + os.sep) and not os.path.realpath(out).startswith(KV + os.sep):
        return
    ready = os.path.join(out, "hermea")
    empty = not os.path.isdir(ready) or not [n for n in os.listdir(ready) if not n.startswith(".")]
    if always or empty:
        shutil.rmtree(out, ignore_errors=True)


def warm_up():
    """Заранее загружаем нейросети, чтобы первая квартира шла быстрее."""
    WARM["state"] = "loading"
    try:
        hermea.room_classifier()
    except Exception as e:
        log("rooms:", e)
    try:
        hermea.lama()
    except Exception as e:
        log("lama:", e)
    WARM["state"] = "ready"


def worker_loop():
    time.sleep(1.5)
    try:
        warm_up()
    except Exception:
        traceback.print_exc()
    while True:
        job = Q.get()
        if job.status != "queued":
            continue
        try:
            run_job(job)
        except Exception:
            traceback.print_exc()
        time.sleep(1)


WORKER = threading.Thread(target=worker_loop, name="worker", daemon=True)


def busy():
    return CURRENT is not None or any(j.status == "queued" for j in JOBS)


def extract_links(text):
    urls = []
    for u in re.findall(r"https?://[^\s<>\"']+", text or ""):
        u = u.rstrip(".,;)»”'\"")
        if u not in urls:
            urls.append(u)
    return urls


def create_jobs(text, force, telegram, no_fee=False):
    urls = extract_links(text)
    if not urls:
        return {"error": tr("no_links")}
    searches = [u for u in urls if app_searches.is_search_url(u)]
    if searches and len(searches) == len(urls):         # вставили ссылку на поиск, а не на объявление
        return {"search": searches[0]}
    done = open(hermea.DONE, encoding="utf-8").read() if os.path.exists(hermea.DONE) else ""
    added, dups = [], []
    for u in urls:
        cu = hermea.clean_url(u)
        active = [j for j in JOBS if j.kind == "url" and hermea.clean_url(j.url) == cu
                  and j.status in ("queued", "running")]
        if active:
            dups.append({"url": u, "f": None, "active": True})
            continue
        if not force and cu in done:
            dups.append({"url": u, "f": find_flat_by_url(u), "active": False})
            continue
        j = Job(u, telegram, no_fee=no_fee)
        with LOCK:
            JOBS.append(j)
        Q.put(j)
        added.append(j.public())
    return {"added": added, "dups": dups}


UPLOAD_RE = re.compile(r"^[a-z0-9]{8,40}$")


def save_upload(uid, name, data):
    if not UPLOAD_RE.match(uid or ""):
        raise PermissionError("upload id")
    d = os.path.join(UPLOAD_ROOT, uid)
    os.makedirs(d, exist_ok=True)
    base = re.sub(r"[^\w.\- ]", "_", os.path.basename(name or "photo.jpg"))[-80:] or "photo.jpg"
    n = len(os.listdir(d)) + 1
    with open(os.path.join(d, f"{n:03d}_{base}"), "wb") as f:
        f.write(data)
    return n


def create_local(uid, title, telegram, no_fee=False):
    if not UPLOAD_RE.match(uid or ""):
        raise PermissionError("upload id")
    d = os.path.join(UPLOAD_ROOT, uid)
    files = sorted(os.path.join(d, n) for n in os.listdir(d)) if os.path.isdir(d) else []
    if not files:
        return {"error": tr("upload_none")}
    j = Job("", telegram, kind="local", files=files, title=(title or "").strip()[:120], upload_dir=d, no_fee=no_fee)
    with LOCK:
        JOBS.append(j)
    Q.put(j)
    return {"added": [j.public()], "dups": []}


# ======================================================================= поиски и обновления
def search_session():
    return hermea.http()


def on_search_drop(s, items):
    i = items[0]
    d = (s.get("drops") or {}).get(i["id"]) or {}
    notify(tr("drop_title"), tr("drop_text", n=len(items), name=i.get("title") or "", was=d.get("from", ""), now=d.get("to", "")))


# ======================================================================= клиенты и договор
CLIENTS_DIR = os.path.join(ROOT, "Клиенты")


def svk_events(evs):
    """События из карточки клиента -> СВК за сегодня. Возвращает, что добавили (для подсказки в окне)."""
    added = []
    day = time.strftime("%Y-%m-%d")
    for ev in evs or []:
        try:
            app_svk.apply(dict(ev, date=day))
            added.append(ev["m"])
        except Exception as e:
            log("svk:", e)
    return added


def safe_name(s):
    s = re.sub(r'[\\/:*?"<>|\n\r\t]+', " ", s or "").strip()
    return re.sub(r"\s+", " ", s)[:80] or "Клиент"


def client_op(body):
    op, cid = body.get("op"), body.get("id")
    if op == "create":
        c, ev = app_clients.create(body.get("data") or {})
    elif op == "update":
        c, ev = app_clients.update(cid, body.get("data") or {})
    elif op == "delete":
        app_clients.delete(cid)
        return {"ok": True}
    elif op == "viewed":
        c, ev = app_clients.viewed(cid, body.get("data") or {})
    elif op == "contract":
        c = app_clients.get(cid)
        if not c:
            raise KeyError(cid)
        folder = os.path.join(CLIENTS_DIR, safe_name(c.get("name")))
        os.makedirs(folder, exist_ok=True)
        out = os.path.join(folder, f"Umowa {safe_name(c.get('name'))} {time.strftime('%d.%m.%Y')}.pdf")
        try:
            app_contract.build(c, out)
        except app_contract.ContractError as e:
            return {"error": tr("contract_" + str(e))}
        c, ev = app_clients.mark_contract(cid)
        open_path(out)
        return {"client": c, "svk": svk_events(ev), "file": os.path.relpath(out, ROOT)}
    else:
        raise ValueError("bad op")
    return {"client": c, "svk": svk_events(ev)}


def on_search_new(s, n):
    notify(tr("search_new_title"), tr("search_new_text", n=n, name=s.get("title") or "Otodom"))


def search_check_now(sid):
    s = app_searches.find(sid)
    if not s:
        return
    try:
        app_searches.check(s, search_session, on_search_new)
    except Exception as e:
        log("search:", e)


def update_loop():
    time.sleep(8)
    while True:
        try:
            app_update.check()
        except Exception as e:
            log("update:", e)
        time.sleep(6 * 3600)


def svk_reminder_loop():
    """В будни в 18:00 напоминаем закрыть день в СВК (если окно открыто)."""
    sent = ""
    while True:
        time.sleep(60)
        try:
            now = time.localtime()
            day = time.strftime("%Y-%m-%d", now)
            if now.tm_wday < 5 and now.tm_hour == 18 and sent != day:
                sent = day
                notify(tr("svk_remind_title"), tr("svk_remind_text"))
        except Exception as e:
            log("svk:", e)


def update_public():
    st = dict(app_update.STATE)
    notes = st.get("notes") or {}
    st["notes"] = notes.get(SETTINGS.get("lang")) or notes.get("ru") or "" if isinstance(notes, dict) else str(notes)
    st["current"] = app_update.local_version()
    st["configured"] = bool(app_update.conf())
    return st


def do_update():
    try:
        app_update.apply(log)
    except Exception as e:
        log("update failed:", e)
        traceback.print_exc()
        return
    threading.Timer(1.0, restart).start()


def restart():
    """Перезапуск после обновления: тот же порт и ключ — окно просто перезагрузится."""
    log("перезапуск после обновления")
    env = dict(os.environ, HERMEA_PORT=str(PORT), HERMEA_TOKEN=TOKEN, HERMEA_RESTART="1")
    try:
        SRV.server_close()
    except Exception:
        pass
    sys.stdout.flush()
    if os.name == "nt":                      # на Windows exec не заменяет процесс — запускаем новый и выходим
        subprocess.Popen([sys.executable, "-W", "ignore", os.path.join(PROG, "hermea_app.py")], env=env,
                         creationflags=0x08000000, close_fds=True)
        os._exit(0)
    os.execve(sys.executable, [sys.executable, "-W", "ignore", os.path.join(PROG, "hermea_app.py")], env)


# ======================================================================= HTTP
def state():
    flats = list_flats()
    with LOCK:
        key = lambda j: hermea.clean_url(j.url) if j.kind == "url" else "local:" + j.id
        ok_urls = {key(j) for j in JOBS if j.status in ("done", "queued", "running")}
        jobs = [j.public() for j in JOBS
                if not j.hidden and (j.status in ("queued", "running")
                                     or (j.finished and time.time() - j.finished < 3600))
                and not (j.status == "error" and key(j) in ok_urls)][-12:]
    return {"busy": busy(), "jobs": jobs, "tg": tg_public(), "settings": SETTINGS, "pending": pending_list(),
            "today": today_stats(flats), "flats_version": FLATS_VERSION, "warm": WARM["state"],
            "searches": app_searches.summary(), "update": update_public(), "version": app_update.local_version(),
            "svk_touched": app_svk.today_touched()}


def open_path(path, reveal=False):
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-R", path] if reveal else ["open", path])
    elif os.name == "nt":
        if reveal:
            subprocess.Popen(["explorer", "/select,", path])
        else:
            os.startfile(path)  # noqa
    else:
        subprocess.Popen(["xdg-open", os.path.dirname(path) if reveal else path])


class Handler(BaseHTTPRequestHandler):
    server_version = "Hermea"
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    # --- helpers
    def _send(self, code, body, ctype="application/json; charset=utf-8", cache=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache or "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _host_ok(self):
        return self.headers.get("Host", "") in (f"127.0.0.1:{PORT}", f"localhost:{PORT}")

    def _token_ok(self, q):
        t = self.headers.get("X-Hermea") or (q.get("t") or [""])[0] or ""
        return secrets.compare_digest(t, TOKEN)

    def _seen(self):
        global LAST_SEEN
        LAST_SEEN = time.time()

    # --- GET
    def do_GET(self):
        try:
            u = urlparse(self.path)
            q = parse_qs(u.query)
            if not self._host_ok():
                return self._send(403, {"error": "host"})
            path = u.path
            if path == "/api/hello":
                return self._send(200, b"hermea" if self._token_ok(q) else b"no", "text/plain")
            if path.startswith("/app/"):
                name = os.path.basename(path)
                fp = os.path.join(UI_DIR, name)
                types = {".woff2": "font/woff2", ".png": "image/png", ".svg": "image/svg+xml", ".ico": "image/x-icon",
                         ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
                ext = os.path.splitext(name)[1]
                if ext in types and os.path.isfile(fp):
                    # скрипты и стили не кэшируем: после обновления окно должно взять новые
                    return self._send(200, open(fp, "rb").read(), types[ext], "no-cache" if ext in (".js", ".css") else "max-age=3600")
                return self._send(404, {"error": "нет файла"})
            if path == "/logo.png":
                return self._send(200, open(hermea.LOGO_PNG, "rb").read(), "image/png", "max-age=3600")
            if not self._token_ok(q):
                return self._send(403, {"error": tr("open_via_app")} if path.startswith("/api")
                                  else "<h3 style='font-family:sans-serif'>" + tr("open_via_app") + "</h3>",
                                  "application/json; charset=utf-8" if path.startswith("/api") else "text/html; charset=utf-8")
            self._seen()
            if path == "/":
                html = open(os.path.join(UI_DIR, "index.html"), encoding="utf-8").read().replace("__TOKEN__", TOKEN)
                html = html.replace("__BOOT__", json.dumps(SETTINGS, ensure_ascii=False))
                return self._send(200, html, "text/html; charset=utf-8")
            if path == "/api/state":
                return self._send(200, state())
            if path == "/api/flats":
                flats = list_flats()
                return self._send(200, {"flats": flats, "version": FLATS_VERSION, "today": today_stats(flats)})
            if path == "/api/search":
                d = app_searches.detail((q.get("id") or [""])[0])
                return self._send(200, d) if d else self._send(404, {"error": tr("search_not_found")})
            if path == "/api/svk":
                return self._send(200, app_svk.get((q.get("from") or [""])[0], (q.get("to") or [""])[0]))
            if path == "/api/clients":
                return self._send(200, {"clients": app_clients.summary(), "template": app_contract.available()})
            if path == "/api/client":
                c = app_clients.get((q.get("id") or [""])[0])
                return self._send(200, {"client": c}) if c else self._send(404, {"error": tr("client_not_found")})
            if path == "/api/market":
                return self._send(200, app_market.summary())
            if path == "/api/owners":
                return self._send(200, app_owners.public())
            if path == "/api/flat":
                return self._send(200, flat_detail((q.get("f") or [""])[0]))
            if path == "/img":
                fp = safe_join(KV, (q.get("f") or [""])[0])
                w = int((q.get("w") or ["0"])[0] or 0)
                if not os.path.isfile(fp):
                    return self._send(404, {"error": "нет фото"})
                if w <= 0:
                    ext = os.path.splitext(fp)[1].lower()
                    ctype = {".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")
                    return self._send(200, open(fp, "rb").read(), ctype, "max-age=600")
                return self._send(200, thumb_bytes(fp, min(max(w, 64), 2400)), "image/jpeg", "max-age=600")
            if path == "/live":
                jid = (q.get("j") or [""])[0]
                i = int((q.get("i") or ["0"])[0])
                job = next((j for j in JOBS if j.id == jid), None)
                if job and 0 <= i < len(job.thumbs):
                    return self._send(200, job.thumbs[i], "image/jpeg", "max-age=3600")
                return self._send(404, {"error": "нет"})
            return self._send(404, {"error": "не найдено"})
        except PermissionError:
            return self._send(403, {"error": tr("no_access")})
        except FileNotFoundError as e:
            return self._send(404, {"error": str(e)})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            traceback.print_exc()
            try:
                return self._send(500, {"error": friendly(e)})
            except Exception:
                pass

    # --- POST
    def do_POST(self):
        try:
            u = urlparse(self.path)
            if not self._host_ok() or not self._token_ok(parse_qs(u.query)):
                return self._send(403, {"error": tr("no_access")})
            if u.path == "/api/bye":                 # окно закрывают
                global CLOSED_AT
                CLOSED_AT = time.time()
                return self._send(200, {"ok": True})
            self._seen()
            n = int(self.headers.get("Content-Length") or 0)
            path = u.path
            if path == "/api/upload":                # своё фото: тело запроса — сам файл
                if n > 150 * 1024 * 1024:
                    return self._send(413, {"error": tr("upload_big")})
                q = parse_qs(u.query)
                data = self.rfile.read(n)
                k = save_upload((q.get("u") or [""])[0], (q.get("n") or ["photo.jpg"])[0], data)
                return self._send(200, {"ok": True, "n": k})
            if path == "/api/contract_template":      # тело запроса — PDF шаблона договора
                if n > 30 * 1024 * 1024:
                    return self._send(413, {"error": tr("upload_big")})
                try:
                    app_contract.save_template(self.rfile.read(n))
                except app_contract.ContractError as e:
                    return self._send(400, {"error": tr("contract_" + str(e))})
                return self._send(200, {"ok": True})
            body = json.loads(self.rfile.read(n) or b"{}") if n else {}
            if path == "/api/client":
                return self._send(200, client_op(body))
            if path == "/api/market_refresh":
                if app_market.STATE.get("state") != "running":
                    threading.Thread(target=app_market.snapshot, args=(search_session, log), daemon=True).start()
                return self._send(200, {"ok": True})
            if path == "/api/svk":
                return self._send(200, app_svk.apply(body))
            if path == "/api/owners":
                op = body.get("op")
                if op == "scan":
                    if app_owners.STATE.get("state") != "running":
                        threading.Thread(target=app_owners.scan, args=(search_session, log), daemon=True).start()
                    return self._send(200, {"ok": True})
                if op == "status":
                    try:
                        app_owners.set_status(body.get("id"), body.get("status"), body.get("note"))
                    except (KeyError, ValueError):
                        return self._send(404, {"error": tr("owner_not_found")})
                    return self._send(200, {"ok": True})
                return self._send(400, {"error": "op"})
            if path == "/api/ping":
                return self._send(200, {"ok": True})
            if path == "/api/create":
                tg = bool(body.get("telegram", SETTINGS.get("telegram", True)))
                return self._send(200, create_jobs(body.get("text", ""), bool(body.get("force")), tg, bool(body.get("no_fee"))))
            if path in ("/api/cancel", "/api/remove"):
                job = next((j for j in JOBS if j.id == body.get("id")), None)
                if not job:
                    return self._send(404, {"error": tr("job_not_found")})
                if job.status == "queued":
                    job.status, job.step = "cancelled", "cancelled"
                    job.finished = time.time()
                elif job.status == "running":
                    job.cancel = True
                return self._send(200, {"ok": True})
            if path == "/api/dismiss":
                job = next((j for j in JOBS if j.id == body.get("id")), None)
                if job and job.status not in ("queued", "running"):
                    job.hidden = True
                return self._send(200, {"ok": True})
            if path == "/api/settings":
                if "telegram" in body:
                    SETTINGS["telegram"] = bool(body["telegram"])
                if body.get("theme") in ("auto", "light", "dark"):
                    SETTINGS["theme"] = body["theme"]
                if body.get("lang") in app_i18n.LANGS:
                    SETTINGS["lang"] = body["lang"]
                    apply_lang()
                if body.get("scale") in (80, 90, 100, 110):
                    SETTINGS["scale"] = body["scale"]
                if "agent_name" in body:
                    SETTINGS["agent_name"] = str(body["agent_name"] or "")[:60]
                if body.get("agent_level") in (30, 40, 45, 50):
                    SETTINGS["agent_level"] = body["agent_level"]
                save_settings()
                return self._send(200, SETTINGS)
            if path == "/api/create_local":
                tg = bool(body.get("telegram", SETTINGS.get("telegram", True)))
                return self._send(200, create_local(body.get("u", ""), body.get("name", ""), tg, bool(body.get("no_fee"))))
            if path == "/api/search_add":
                url = (body.get("url") or "").strip()
                if not app_searches.is_search_url(url):
                    return self._send(400, {"error": tr("search_bad")})
                s = app_searches.add(url)
                threading.Thread(target=search_check_now, args=(s["id"],), daemon=True).start()
                return self._send(200, {"id": s["id"]})
            if path == "/api/search_check":
                s = app_searches.find(body.get("id"))
                if not s:
                    return self._send(404, {"error": tr("search_not_found")})
                try:
                    app_searches.check(s, search_session, on_search_new)
                except Exception as e:
                    return self._send(502, {"error": tr("search_fail", e=friendly(e))})
                return self._send(200, app_searches.detail(s["id"]))
            if path == "/api/search_seen":
                app_searches.mark_seen(body.get("id"), body.get("ad"))
                return self._send(200, {"ok": True})
            if path == "/api/search_hide":
                app_searches.hide(body.get("id"), body.get("ad"))
                return self._send(200, {"ok": True})
            if path == "/api/search_remove":
                app_searches.remove(body.get("id"))
                return self._send(200, {"ok": True})
            if path == "/api/update_check":
                app_update.check()
                return self._send(200, update_public())
            if path == "/api/update_apply":
                if busy():
                    return self._send(409, {"error": tr("wait_busy")})
                if app_update.STATE.get("state") != "available":
                    app_update.check()
                if app_update.STATE.get("state") != "available":
                    err = tr("upd_off") if not app_update.conf() else (update_public().get("error") or "—")
                    return self._send(400, {"error": err})
                threading.Thread(target=do_update, daemon=True).start()
                return self._send(200, {"ok": True})
            if path == "/api/open":
                what = body.get("what", "folder")
                if what == "root":
                    open_path(KV if os.path.isdir(KV) else ROOT)
                    return self._send(200, {"ok": True})
                if what == "url":
                    url = body.get("url") or flat_detail(body.get("f", "")).get("url")
                    if url and url.startswith("http"):
                        subprocess.Popen(["open", url]) if sys.platform == "darwin" else __import__("webbrowser").open(url)
                        return self._send(200, {"ok": True})
                    return self._send(404, {"error": tr("no_url")})
                fp = safe_join(KV, body.get("f", ""))
                if not os.path.exists(fp):
                    return self._send(404, {"error": tr("folder_gone")})
                open_path(fp, reveal=(what == "photo"))
                return self._send(200, {"ok": True})
            if path == "/api/opis":
                p = safe_join(KV, body.get("f", ""))
                fp = os.path.join(p, "opis.txt")
                _, tail = read_opis(p)
                text = (body.get("text") or "").replace("\r\n", "\n").strip("\n") + "\n"
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(text + ("\n---\n" + tail if tail else ""))
                return self._send(200, {"ok": True})
            if path == "/api/telegram":
                p = safe_join(KV, body.get("f", ""))
                token, chat = hermea.tg_config()
                if not (token and chat):
                    return self._send(400, {"error": tg_public()["hint"] or tr("tg_not_set")})
                if not os.path.exists(os.path.join(p, "opis.txt")) or not os.path.isdir(os.path.join(p, "hermea")):
                    return self._send(400, {"error": tr("no_opis")})
                try:
                    hermea.tg_send(token, chat, p)
                except Exception as e:
                    return self._send(502, {"error": "Telegram: " + str(e)})
                write_meta(p, telegram={"ok": True, "at": time.strftime("%Y-%m-%d %H:%M")})
                return self._send(200, {"ok": True})
            if path == "/api/flush":
                token, chat = hermea.tg_config()
                if not (token and chat):
                    return self._send(400, {"error": tr("tg_not_set")})
                hermea.tg_pending_flush(token, chat)
                return self._send(200, {"ok": True, "left": pending_list()})
            if path == "/api/tgcheck":
                threading.Thread(target=tg_check, daemon=True).start()
                return self._send(200, {"ok": True})
            if path == "/api/quit":
                if busy():
                    return self._send(409, {"error": tr("wait_busy")})
                self._send(200, {"ok": True})
                threading.Timer(0.5, shutdown).start()
                return
            return self._send(404, {"error": "не найдено"})
        except PermissionError:
            return self._send(403, {"error": tr("no_access")})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            traceback.print_exc()
            try:
                return self._send(500, {"error": friendly(e)})
            except Exception:
                pass


def shutdown():
    log("выход")
    try:
        if open(PORT_FILE, encoding="utf-8").read().split()[0] == str(PORT):
            os.remove(PORT_FILE)
    except Exception:
        pass
    os._exit(0)


def watchdog():
    """Закрываемся, когда окна нет и работы нет: сразу после закрытия окна или через 3 минуты тишины."""
    while True:
        time.sleep(2)
        if busy():
            continue
        now = time.time()
        closed = CLOSED_AT and LAST_SEEN < CLOSED_AT and now - CLOSED_AT > 4
        if closed or now - LAST_SEEN > IDLE_EXIT:
            shutdown()


def serve(open_window_fn=None, preferred_port=47615, running_instance=None):
    global PORT, SRV
    load_settings()
    app_searches.init(PROG)
    app_update.init(PROG)
    app_svk.init(PROG)
    app_clients.init(PROG)
    app_market.init(PROG)
    app_owners.init(PROG)
    app_searches.ON_DROP["fn"] = on_search_drop
    app_searches.COMPARE["fn"] = app_market.compare
    if os.environ.get("HERMEA_PORT"):
        preferred_port = int(os.environ["HERMEA_PORT"])
    srv = None
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", preferred_port), Handler)
    except OSError:
        url = running_instance() if running_instance else None
        if url:                       # второй запуск успел раньше — просто показываем его окно
            if open_window_fn:
                open_window_fn(url)
            return
        srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    srv.daemon_threads = True
    SRV = srv
    PORT = srv.server_address[1]
    with open(PORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"{PORT} {TOKEN}\n")
    sys.stdout = Tee(sys.__stdout__)
    log(f"Hermea: окно на порту {PORT}")
    WORKER.start()
    threading.Thread(target=tg_check, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()
    threading.Thread(target=app_searches.loop, args=(search_session, on_search_new, log), daemon=True).start()
    threading.Thread(target=update_loop, daemon=True).start()
    threading.Thread(target=svk_reminder_loop, daemon=True).start()
    threading.Thread(target=app_market.loop, args=(search_session, log), daemon=True).start()
    threading.Thread(target=app_owners.loop, args=(search_session, log), daemon=True).start()
    url = f"http://127.0.0.1:{PORT}/?t={TOKEN}"
    if open_window_fn:
        threading.Thread(target=open_window_fn, args=(url,), daemon=True).start()
    else:
        print(url, flush=True)
    try:
        srv.serve_forever(poll_interval=0.5)
    finally:
        shutdown()
