"""Проверка окна-сервера целиком: запускает Hermea на временной папке с тестовыми данными
и проходит по всем маршрутам, которыми пользуются вкладки. Сеть не нужна (HERMEA_OFFLINE=1).

    python3 tools/test_api.py              -> «API OK» или список ошибок, код выхода 1
"""
import datetime as dt
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

# консоль Windows (cp1252) не печатает кириллицу и польские буквы
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "program")
SKIP = {".venv", "__pycache__", "models", "_backup", "templates", "_test_color"}
FAILS = []


def check(name, cond, extra=""):
    if not cond:
        FAILS.append(f"{name} {extra}".strip())
        print("FAIL", name, extra)


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def make_root():
    root = os.path.join(tempfile.mkdtemp(prefix="hermea_api_"), "Hermea Photo")
    prog = os.path.join(root, "_program")
    shutil.copytree(SRC, prog, ignore=lambda d, names: [n for n in names if n in SKIP or n.endswith((".pt", ".pth"))])
    for f in os.listdir(prog):
        if f.startswith("app_") and f.endswith(".json") or f in ("telegram.txt", ".app_port"):
            os.remove(os.path.join(prog, f))
    # одна готовая квартира
    import cv2
    import numpy as np
    flat = os.path.join(root, "Квартиры", "Mokotów, Puławska - 2 pok 45 m2")
    os.makedirs(os.path.join(flat, "hermea"))
    for k in range(2):
        img = np.full((300, 400, 3), 120 + k * 40, np.uint8)
        # cv2.imwrite на Windows не понимает русские буквы в пути — пишем байты сами
        open(os.path.join(flat, "hermea", f"p{k + 1}_hermea.jpg"), "wb").write(cv2.imencode(".jpg", img)[1].tobytes())
    open(os.path.join(flat, "opis.txt"), "w", encoding="utf-8").write(
        "Квартира на Мокотуві\nОренда: 3 800 zł\nРазом: 4 300 zł\n\n---\nОригинал: https://www.otodom.pl/pl/oferta/test-ID4TEST\n")
    json.dump({"created": time.strftime("%Y-%m-%d %H:%M"), "url": "https://www.otodom.pl/pl/oferta/test-ID4TEST"},
              open(os.path.join(flat, ".hermea.json"), "w", encoding="utf-8"))
    # собственники: одно с Otodom, одно с OLX
    today = dt.date.today().isoformat()
    ad = {"title": "Test", "url": "https://www.otodom.pl/pl/oferta/a-ID1", "img": None, "price": 4000, "rent": 400,
          "total": 4400, "area": 45, "rooms": "2", "district": "Mokotów", "street": "Puławska", "created": "2026-10-01",
          "first_seen": "2026-10-01", "last_seen": today, "status": "new", "photos": 8, "name": "Anna", "tags": []}
    olx = dict(ad, id="olx-2", url="https://www.olx.pl/d/oferta/b-ID2.html", src="olx", street="", district="Wola",
               total=4100, price=3700, detail={"desc_len": 400, "neg": False, "pos": False, "checked": today, "others": 0,
                                               "snippet": "Mieszkanie", "free_from": "", "deposit": None, "owner_id": ""})
    copies = {"checked": today, "items": [
        {"src": "otodom", "url": "https://www.otodom.pl/pl/oferta/c-ID3", "agency": "Two Steps Agency", "price": 4100, "how": "photo", "dist": 18, "ours": False},
        {"src": "olx", "url": "https://www.olx.pl/d/oferta/d-ID4.html", "agency": "Biuro Test", "price": 4000, "how": "place", "dist": 95, "ours": False}]}
    json.dump({"ads": {"1": dict(ad, id="1", copies=copies), "olx-2": olx}, "last_scan": today},
              open(os.path.join(prog, "app_owners.json"), "w", encoding="utf-8"))
    return root, prog


def start():
    """Тестовая папка + запущенный сервер -> (root, процесс, адрес, ключ)."""
    root, prog = make_root()
    env = dict(os.environ, HERMEA_OFFLINE="1", HERMEA_PORT=str(free_port()), PYTHONDONTWRITEBYTECODE="1",
               PYTHONIOENCODING="utf-8")
    p = subprocess.Popen([sys.executable, os.path.join(prog, "hermea_app.py"), "--no-window"], cwd=prog, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    port_file = os.path.join(prog, ".app_port")
    for _ in range(60):
        if os.path.exists(port_file) and open(port_file).read().strip():
            break
        time.sleep(0.5)
    port, tok = open(port_file, encoding="utf-8").read().split()
    return root, p, f"http://127.0.0.1:{port}", tok


def main():
    root, p, base, tok = start()
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def req(path, body=None, token=True, raw=False):
        h = {"X-Hermea": tok} if token else {}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        try:
            r = op.open(urllib.request.Request(base + path, data=data, headers=h), timeout=30)
            b = r.read()
            return r.status, (b if raw else json.loads(b or b"{}"))
        except urllib.error.HTTPError as e:
            b = e.read()
            try:
                return e.code, json.loads(b)
            except Exception:
                return e.code, b

    try:
        # защита
        check("без ключа 403", req("/api/state", token=False)[0] == 403)
        check("POST без ключа 403", req("/api/settings", {"theme": "dark"}, token=False)[0] == 403)
        # страница и файлы интерфейса
        s, html = req("/", raw=True)
        html = html.decode("utf-8")
        check("главная страница", s == 200 and "__TOKEN__" not in html and "__BOOT__" not in html)
        import re
        for ref in re.findall(r'(?:src|href)="(/app/[^"]+)"', html):
            check("файл " + ref, req(ref, raw=True)[0] == 200)
        # общие экраны
        s, st = req("/api/state")
        check("state", s == 200 and "jobs" in st, str(s))
        s, fl = req("/api/flats")
        check("flats", s == 200 and len(fl.get("flats", [])) == 1, str(fl)[:200])
        f = fl["flats"][0]["f"]
        s, fd = req("/api/flat?f=" + urllib.request.quote(f))
        check("flat", s == 200 and len(fd.get("photos", [])) == 2 and fd.get("facts"), str(fd)[:200])
        check("img", req("/img?w=200&f=" + urllib.request.quote(fd["photos"][0]["f"]), raw=True)[0] == 200)
        check("img вне папки 403/404", req("/img?f=../../etc/passwd", raw=True)[0] in (403, 404))
        s, _ = req("/api/opis", {"f": f, "text": "Новый текст\nОренда: 3 900 zł"})
        check("opis сохранить", s == 200)
        check("opis прочитать", "Новый текст" in (req("/api/flat?f=" + urllib.request.quote(f))[1].get("opis") or ""))
        # настройки
        s, sett = req("/api/settings", {"theme": "dark", "lang": "uk", "scale": 90, "agent_name": "Павел"})
        check("settings", s == 200 and sett.get("lang") == "uk" and sett.get("scale") == 90)
        req("/api/settings", {"lang": "ru", "scale": 100})
        # СВК
        today = dt.date.today().isoformat()
        s, sv = req("/api/svk?from=" + today + "&to=" + today)
        check("svk get", s == 200, str(sv)[:200])
        s, sv = req("/api/svk", {"op": "add", "date": today, "m": "ads", "d": 1})
        check("svk add", s == 200, str(sv)[:200])
        # клиенты и подбор
        s, r = req("/api/client", {"op": "create", "data": {"name": "Тест Клиент", "source": "direct", "budget": "4500",
                                                             "location": "Мокотув, Вола", "type": "2 комнаты"}})
        check("client create", s == 200 and r.get("client"), str(r)[:200])
        cid = r["client"]["id"]
        s, r = req("/api/client", {"op": "update", "id": cid, "data": {"phone": "+48 500 600 700"}})
        check("client update", s == 200 and r["client"].get("phone"))
        s, r = req("/api/clients")
        check("clients", s == 200 and len(r.get("clients", [])) == 1 and r.get("match_new", {}).get(cid) == 2, str(r)[:300])
        s, m = req("/api/match?id=" + cid)
        check("match", s == 200 and m.get("total") == 2, str(m)[:300])
        check("match skip", req("/api/match", {"id": cid, "skip": "olx-2"})[0] == 200)
        check("match после skip", req("/api/match?id=" + cid)[1].get("total") == 1)
        check("match чужой id 404", req("/api/match?id=nope")[0] == 404)
        s, r = req("/api/client", {"op": "viewed", "id": cid, "data": {"date": "25.11.2026", "address": "ul. Test 1",
                                                                       "rooms": "2", "rent": "3500"}})
        check("client viewed", s == 200, str(r)[:200])
        check("client delete", req("/api/client", {"op": "delete", "id": cid})[0] == 200)
        # рынок, собственники, перезвоны
        check("market", req("/api/market")[0] == 200)
        s, o = req("/api/owners")
        check("owners", s == 200 and o.get("total") == 2 and "stats" in o, str(o)[:200])
        s, r = req("/api/owners", {"op": "status", "id": "1", "status": "agreed", "note": "50%"})
        check("owners status", s == 200, str(r)[:200])
        check("owners stats", req("/api/owners")[1]["stats"]["total"]["agreed"] == 1)
        s, r = req("/api/owners", {"op": "copies", "id": "1"})
        check("owners copies: без сети не ходим на сайты", s == 503, str(r)[:200])
        s, r = req("/api/calls", {"op": "add", "text": "+48 535 016 721 завтра перезвонить"})
        check("calls add", s == 200, str(r)[:200])
        s, c = req("/api/calls")
        check("calls list", s == 200 and len(c.get("items", [])) == 1, str(c)[:200])
        k = c["items"][0]["id"]
        check("calls update", req("/api/calls", {"op": "update", "id": k, "note": "ok", "status": "done"})[0] == 200)
        check("calls delete", req("/api/calls", {"op": "delete", "id": k})[0] == 200)
        check("ping", req("/api/ping", {})[0] == 200)
        check("неизвестный адрес 404", req("/api/nothing")[0] == 404)
        s, w = req("/api/window")
        check("окно открыто (для повторного клика по значку)", s == 200 and w.get("open") is True, str(w))
        check("окно без ключа 403", req("/api/window", token=False)[0] == 403)
        req("/api/bye", {})
        check("после закрытия окна — закрыто", req("/api/window")[1].get("open") is False)
    finally:
        try:
            req("/api/quit", {})
        except Exception:
            pass
        try:
            out = p.communicate(timeout=10)[0].decode("utf-8", "replace")
        except Exception:
            p.kill()
            out = p.communicate()[0].decode("utf-8", "replace")
        if "Traceback" in out:
            FAILS.append("в выводе сервера есть ошибка")
            print(out[-3000:])
        shutil.rmtree(os.path.dirname(root), ignore_errors=True)
    print("API OK" if not FAILS else f"API: ошибок {len(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
