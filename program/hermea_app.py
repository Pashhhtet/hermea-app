#!/usr/bin/env python3
"""Hermea — окно «Обработка фото».

Запускается из Hermea.app (двойной клик). Открывает окно, где можно вставить ссылку
на объявление и нажать «Создать»: фото и описание появятся в папке «Квартиры»,
а всё вместе уйдёт в Telegram — так же, как при запуске «Запустить.command».

Внутри это маленький сервер только для этого компьютера (127.0.0.1) и страница в окне Chrome.
Окно можно закрыть посреди работы — обработка закончится сама, придёт уведомление.
Совместимо с Python 3.9.
"""
import os
import sys
import json
import time
import secrets
import subprocess
import urllib.request

PROG = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PROG)
UI_DIR = os.path.join(PROG, "app")
PORT_FILE = os.path.join(PROG, ".app_port")
LOG_FILE = os.path.join(PROG, "app_log.txt")
SETTINGS_FILE = os.path.join(PROG, "app_settings.json")
PREFERRED_PORT = 47615
IDLE_EXIT = 180          # сек без открытого окна и без работы — программа сама закрывается
NO_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


# ======================================================================= запуск окна
def window_url(port, token):
    return f"http://127.0.0.1:{port}/?t={token}"


def open_window(url):
    """Окно без адресной строки (режим приложения Chrome); если Chrome нет — обычный браузер."""
    devnull = subprocess.DEVNULL
    if sys.platform == "darwin":
        for app in ("Google Chrome", "Microsoft Edge", "Brave Browser", "Chromium"):
            try:
                r = subprocess.run(["open", "-na", app, "--args", "--app=" + url, "--window-size=1400,920",
                                    "--no-first-run", "--no-default-browser-check"],
                                   stdout=devnull, stderr=devnull, timeout=20)
                if r.returncode == 0:
                    return
            except Exception:
                pass
        subprocess.run(["open", url], stdout=devnull, stderr=devnull)
    elif os.name == "nt":
        for exe in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
            if os.path.exists(exe):
                subprocess.Popen([exe, "--app=" + url, "--window-size=1400,920"])
                return
        os.startfile(url)  # noqa
    else:
        import webbrowser
        webbrowser.open(url)


def running_instance():
    """Если окно-сервер уже запущен — вернуть его адрес (второй экземпляр не нужен)."""
    try:
        port, token = open(PORT_FILE, encoding="utf-8").read().split()
        with NO_PROXY.open(f"http://127.0.0.1:{port}/api/hello?t={token}", timeout=1.5) as r:
            if r.read() == b"hermea":
                return window_url(port, token)
    except Exception:
        pass
    return None


def rotate_log():
    try:
        if os.path.getsize(LOG_FILE) > 2_000_000:
            os.replace(LOG_FILE, LOG_FILE + ".old")
    except OSError:
        pass


def daemonize():
    """Отцепиться от Hermea.app, чтобы приложение можно было открыть снова, пока идёт работа."""
    if os.name != "posix":
        return
    if os.fork() > 0:
        os._exit(0)
    os.setsid()
    if os.fork() > 0:
        os._exit(0)
    os.chdir(PROG)
    fd = os.open(os.devnull, os.O_RDWR)
    os.dup2(fd, 0)
    lf = os.open(LOG_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    os.dup2(lf, 1)
    os.dup2(lf, 2)


def main():
    restarted = os.environ.pop("HERMEA_RESTART", None)    # перезапуск после обновления: окно уже открыто
    url = None if restarted else running_instance()
    if url:
        if "--no-window" not in sys.argv:
            open_window(url)
        return
    rotate_log()
    if "--detach" in sys.argv:
        daemonize()
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    import app_server   # тяжёлые библиотеки (OpenCV, нейросети) грузим уже после отцепления
    app_server.serve(open_window_fn=None if ("--no-window" in sys.argv or restarted) else open_window,
                     preferred_port=PREFERRED_PORT, running_instance=running_instance)


if __name__ == "__main__":
    main()
