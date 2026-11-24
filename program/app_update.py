"""Автообновление Hermea через GitHub.

В репозитории лежит manifest.json:
  {"version": "1.2.0",
   "notes": {"ru": "...", "uk": "...", "pl": "..."},
   "pip": ["пакет>=версия", ...],                      # если нужна новая библиотека
   "files": [{"path": "hermea.py", "src": "program/hermea.py", "sha256": "...", "exec": false}, ...]}
path — куда положить относительно папки _program («../Hermea.app/...» — само приложение).
Скачиваются только изменённые файлы, каждый проверяется по sha256; старые копии
сохраняются в _program/_backup/. Совместимо с Python 3.9.
"""
import hashlib
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.parse
import urllib.request

PROG = None
ROOT = None
STATE = {"state": "off", "version": None, "notes": None, "error": ""}
_MANIFEST = {"m": None}


def init(prog):
    global PROG, ROOT
    PROG = prog
    ROOT = os.path.dirname(prog)


def local_version():
    try:
        return open(os.path.join(PROG, "VERSION"), encoding="utf-8").read().strip() or "1.0.0"
    except Exception:
        return "1.0.0"


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v))[:3]) or (0,)


def conf():
    try:
        c = json.load(open(os.path.join(PROG, "update.json"), encoding="utf-8"))
        return c if c.get("repo") else None
    except Exception:
        return None


def _ctx():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _get(url, timeout=40):
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "Hermea-Updater"})
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        return r.read()


def _raw(c, path):
    # кириллица и пробелы в именах файлов («КАК ПОЛЬЗОВАТЬСЯ.txt») должны быть закодированы
    return (f"https://raw.githubusercontent.com/{c['repo']}/{c.get('branch') or 'main'}/"
            f"{urllib.parse.quote(path)}?t={int(time.time())}")


def check():
    c = conf()
    if not c:
        STATE.update(state="off", version=None, notes=None, error="")
        return STATE
    STATE.update(state="checking", error="")
    try:
        m = json.loads(_get(_raw(c, "manifest.json")))
        _MANIFEST["m"] = m
        if vtuple(m.get("version")) > vtuple(local_version()):
            STATE.update(state="available", version=m.get("version"), notes=m.get("notes") or {})
        else:
            STATE.update(state="latest", version=m.get("version"), notes=None)
    except Exception as e:
        STATE.update(state="error", error=str(e)[:200])
    return STATE


def _target(path):
    """Куда писать файл; только внутрь _program или Hermea.app."""
    p = os.path.realpath(os.path.join(PROG, path))
    prog, app = os.path.realpath(PROG), os.path.realpath(os.path.join(ROOT, "Hermea.app"))
    if not (p.startswith(prog + os.sep) or p.startswith(app + os.sep)):
        raise PermissionError(path)
    return p


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _missing_pip(specs):
    try:
        from importlib import metadata
    except Exception:
        return list(specs)
    miss = []
    for spec in specs:
        name = re.split(r"[<>=!~\[ ]", spec, 1)[0]
        try:
            have = metadata.version(name)
        except Exception:
            miss.append(spec)
            continue
        m = re.search(r">=\s*([\d.]+)", spec)
        if m and vtuple(have) < vtuple(m.group(1)):
            miss.append(spec)
    return miss


def apply(log=print):
    """Скачивает и ставит обновление. Возвращает новую версию; перезапуск делает вызывающий."""
    c = conf()
    m = _MANIFEST["m"] or json.loads(_get(_raw(c, "manifest.json")))
    STATE.update(state="installing", error="")
    try:
        new = []
        for f in m.get("files") or []:
            if sys.platform != "darwin" and (f["path"].startswith("../Hermea.app/") or f["path"].endswith(".command")):
                continue                           # Mac-обёртка на Windows не нужна
            dst = _target(f["path"])
            if os.path.exists(dst) and _sha(open(dst, "rb").read()) == f["sha256"]:
                continue
            data = _get(_raw(c, f["src"]))
            if _sha(data) != f["sha256"]:
                raise RuntimeError("sha256: " + f["path"])
            new.append((f, dst, data))
        backup = os.path.join(PROG, "_backup", f"{local_version()}_{time.strftime('%Y%m%d-%H%M%S')}")
        for f, dst, data in new:                      # сначала копии старых файлов
            if os.path.exists(dst):
                rel = os.path.relpath(dst, ROOT)
                os.makedirs(os.path.dirname(os.path.join(backup, rel)), exist_ok=True)
                shutil.copy2(dst, os.path.join(backup, rel))
        for f, dst, data in new:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            tmp = dst + ".new"
            with open(tmp, "wb") as fh:
                fh.write(data)
            if f.get("exec"):
                os.chmod(tmp, 0o755)
            os.replace(tmp, dst)
            log("обновлён файл:", f["path"])
        miss = _missing_pip(m.get("pip") or [])
        if miss:
            log("ставлю библиотеки:", miss)
            subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + miss, timeout=3600, check=True)
        with open(os.path.join(PROG, "VERSION"), "w", encoding="utf-8") as fh:
            fh.write(str(m.get("version")) + "\n")
        STATE.update(state="restarting", version=m.get("version"))
        return m.get("version")
    except Exception as e:
        STATE.update(state="error", error=str(e)[:200])
        raise
