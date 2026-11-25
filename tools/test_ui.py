"""Проверка интерфейса в настоящем браузере (нужны playwright и Chrome; на машинах коллег не запускается).
Открывает Hermea на тестовых данных, проходит все вкладки и основные экраны, ловит ошибки JavaScript
и сохраняет снимки в /tmp/hermea_ui/.

    python3 tools/test_ui.py      -> «UI OK» или ошибки
"""
import json
import os
import shutil
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_api  # noqa: E402

# консоль Windows (cp1252) не печатает кириллицу и польские буквы
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

OUT = "/tmp/hermea_ui"


def main():
    from playwright.sync_api import sync_playwright
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    root, p, base, tok = test_api.start()
    errors = []
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    # клиент с запросом, чтобы был подбор
    op.open(urllib.request.Request(base + "/api/client", data=json.dumps({"op": "create", "data": {
        "name": "Кристина Тест", "source": "direct", "budget": "4500", "location": "Мокотув, Вола", "type": "2 комнаты",
        "lang": "ua"}}).encode(), headers={"X-Hermea": tok, "Content-Type": "application/json"}), timeout=20).read()
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(executable_path=shutil.which("google-chrome") or None, args=["--no-proxy-server"])
            dark = b.new_page(viewport={"width": 1100, "height": 760}, color_scheme="dark")
            dark.on("pageerror", lambda e: errors.append("JS (тёмная тема): " + str(e)))
            dark.goto(f"{base}/?t={tok}")
            for mode in ("svk", "clients", "owners"):
                dark.click(f"#modes [data-mode={mode}]")
                dark.wait_for_timeout(900)
                if mode == "clients":
                    dark.click(".cl-item")
                    dark.wait_for_timeout(1000)
                dark.screenshot(path=f"{OUT}/dark_{mode}.png")
            dark.close()
            pg = b.new_page(viewport={"width": 1280, "height": 820})
            pg.on("pageerror", lambda e: errors.append("JS: " + str(e)))
            pg.on("console", lambda m: m.type == "error" and errors.append("console: " + m.text))
            pg.goto(f"{base}/?t={tok}")
            pg.wait_for_timeout(1200)
            pg.screenshot(path=f"{OUT}/1_photo.png")
            pg.click("#modes [data-mode=svk]")
            pg.wait_for_timeout(900)
            pg.screenshot(path=f"{OUT}/2_svk.png")
            pg.click("#modes [data-mode=clients]")
            pg.wait_for_timeout(900)
            pg.click(".cl-item")
            pg.wait_for_timeout(1200)
            pg.screenshot(path=f"{OUT}/3_client.png")
            if not pg.query_selector("#clMatch .mt-row"):
                errors.append("подбор не показал квартиры")
            # поле «Комнаты» со списком: выбор «3 комнаты» убирает двушки из подбора
            if not pg.query_selector('input[data-f=rooms][list="dl-rooms"]') or len(pg.query_selector_all("#dl-rooms option")) < 5:
                errors.append("нет поля «Комнаты» со списком")
            pg.fill("input[data-f=rooms]", "3 комнаты")
            pg.wait_for_timeout(1800)
            if pg.query_selector("#clMatch .mt-row"):
                errors.append("подбор не учёл комнаты")
            pg.fill("input[data-f=rooms]", "2 комнаты")
            pg.wait_for_timeout(1800)
            pg.screenshot(path=f"{OUT}/3b_client_rooms.png")
            pg.click("#modes [data-mode=market]")
            pg.wait_for_timeout(900)
            pg.screenshot(path=f"{OUT}/4_market.png")
            pg.click("#modes [data-mode=owners]")
            pg.wait_for_timeout(1200)
            pg.screenshot(path=f"{OUT}/5_owners.png")
            if len(pg.query_selector_all(".ow-row, #owList > li")) < 2:
                errors.append("собственники не показались")
            pg.click('.ow-row[data-id="1"] [data-act=script]')
            pg.wait_for_timeout(500)
            pg.screenshot(path=f"{OUT}/5b_owner_agencies.png")
            if len(pg.query_selector_all(".ow-ag-list li")) != 2:
                errors.append("копии у агентств не показались")
            pg.keyboard.press("Control+2")
            pg.wait_for_timeout(500)
            if "СВК" not in pg.title():
                errors.append("⌘2 не открыл СВК: " + pg.title())
            pg.click("#gear") if pg.query_selector("#gear") else None
            pg.wait_for_timeout(400)
            pg.screenshot(path=f"{OUT}/6_settings.png")
            b.close()
    finally:
        try:
            op.open(urllib.request.Request(base + "/api/quit", data=b"{}", headers={"X-Hermea": tok}), timeout=5)
        except Exception:
            pass
        try:
            p.communicate(timeout=10)
        except Exception:
            p.kill()
        shutil.rmtree(os.path.dirname(root), ignore_errors=True)
    for e in errors:
        print("FAIL", e)
    print("UI OK" if not errors else f"UI: ошибок {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
