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
import time
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
        local = os.environ.get("LOCALAPPDATA", "")
        for exe in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.join(local, r"Google\Chrome\Application\chrome.exe"),
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
            if os.path.exists(exe):
                subprocess.Popen([exe, "--app=" + url, "--window-size=1400,920", "--no-first-run",
                                  "--no-default-browser-check"])
                return
        os.startfile(url)  # noqa
    else:
        import webbrowser
        webbrowser.open(url)


# заголовок окна всегда содержит «Hermea —» (например «(2) Hermea — Собственники»)
WINDOW_MARK = "Hermea \u2014"
FOCUS_MAC = """
set mark to "%s"
repeat with appRef in {"Google Chrome", "Microsoft Edge", "Brave Browser", "Chromium"}
  set appName to contents of appRef
  if application appName is running then
    tell application appName
      repeat with w in windows
        if title of w contains mark then
          try
            set minimized of w to false
          end try
          set index of w to 1
          activate
          return "ok"
        end if
      end repeat
    end tell
  end if
end repeat
return "none"
"""


def window_is_open(url):
    """Спросить работающую программу, открыто ли её окно сейчас (в том числе свёрнутое)."""
    try:
        base, token = url.split("/?t=")
        with NO_PROXY.open(f"{base}/api/window?t={token}", timeout=1.5) as r:
            import json
            return bool(json.loads(r.read()).get("open"))
    except Exception:
        return False


def focus_window():
    """Повторный клик по значку: развернуть уже открытое окно Hermea и вывести вперёд. -> True, если нашли."""
    try:
        if sys.platform == "darwin":
            r = subprocess.run(["osascript", "-e", FOCUS_MAC % WINDOW_MARK], capture_output=True, text=True, timeout=8)
            return r.stdout.strip() == "ok"
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            found = []

            @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            def each(hwnd, _):
                if user32.IsWindowVisible(hwnd):
                    n = user32.GetWindowTextLengthW(hwnd)
                    buf = ctypes.create_unicode_buffer(n + 1)
                    user32.GetWindowTextW(hwnd, buf, n + 1)
                    if WINDOW_MARK in buf.value:
                        found.append(hwnd)
                        return False
                return True

            user32.EnumWindows(each, 0)
            if not found:
                return False
            h = found[0]
            user32.ShowWindow(h, 9 if user32.IsIconic(h) else 5)     # 9 — развернуть свёрнутое, 5 — показать
            user32.SetForegroundWindow(h)
            return True
    except Exception:
        pass
    return False


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


def move_out_of_desktop(restarted):
    """macOS не пускает программу, запущенную из Hermea.app, в защищённый «Рабочий стол» —
    поэтому окно открывалось через Терминал. Один раз переносим «Hermea Photo» в домашнюю папку
    (она не защищена), на столе оставляем ссылку на папку и перезапускаемся уже оттуда."""
    if sys.platform != "darwin" or os.environ.get("HERMEA_NO_MOVE"):
        return
    root = os.path.realpath(ROOT)
    desk = os.path.realpath(os.path.expanduser("~/Desktop"))
    if os.path.dirname(root) != desk:
        return
    new = os.path.join(os.path.realpath(os.path.expanduser("~")), os.path.basename(root))
    if os.path.exists(new):
        return
    try:
        os.rename(root, new)
    except OSError as e:
        sys.stderr.write(f"перенос папки не удался: {e}\n")
        return
    try:
        os.symlink(new, root)                           # на рабочем столе — ссылка на папку
    except OSError:
        pass
    try:
        with open(os.path.join(new, "_program", "app_log.txt"), "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%d.%m %H:%M:%S')}] папка перенесена: {root} -> {new}\n")
    except OSError:
        pass
    env = dict(os.environ)
    if restarted:
        env["HERMEA_RESTART"] = "1"
    py = os.path.join(new, "_program", ".venv", "bin", "python")
    if not os.path.exists(py):
        py = sys.executable
    os.execve(py, [py, "-W", "ignore", os.path.join(new, "_program", "hermea_app.py")] + sys.argv[1:], env)


def main():
    restarted = os.environ.pop("HERMEA_RESTART", None)    # перезапуск после обновления: окно уже открыто
    move_out_of_desktop(restarted)
    url = None if restarted else running_instance()
    if url:
        # программа уже работает: показываем её окно, а новое открываем, только если окна нет
        if "--no-window" not in sys.argv and not (window_is_open(url) and focus_window()):
            open_window(url)
        return
    rotate_log()
    if "--detach" in sys.argv:
        daemonize()
    if sys.stdout is None or sys.stderr is None:   # Windows, запуск без консоли (pythonw): пишем в журнал
        lf = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
        sys.stdout = sys.stderr = sys.__stdout__ = sys.__stderr__ = lf
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
