"""Все проверки перед релизом одной командой.

    python3 tools/check.py          быстрые проверки + сервер (≈15 с)
    python3 tools/check.py --ui     ещё и окно в Chrome (нужен playwright)

Проверки, для которых нет инструмента на этой машине (ruff, node, playwright), пропускаются с пометкой.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = sys.executable


def run(name, cmd, optional_tool=None):
    if optional_tool and not shutil.which(optional_tool):
        print(f"--   {name}: пропущено (нет {optional_tool})")
        return True
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    ok = r.returncode == 0
    print(("OK   " if ok else "FAIL ") + name)
    if not ok:
        print((r.stdout + r.stderr)[-4000:])
    return ok


def main():
    steps = [
        ("Python: ошибки и неопределённые имена", ["ruff", "check", "program", "tools", "--select", "F,E9,PLE",
                                                   "--target-version", "py39", "--quiet"], "ruff"),
        ("CSS: вкладки не перебивают друг друга", [PY, "tools/css_check.py"], None),
        ("JS: синтаксис и переводы ru/uk/pl", ["node", "tools/js_check.js", "program/app/index.html", "program/app"], "node"),
        ("Части программы", [PY, "tools/test_units.py"], None),
        ("Сервер: все адреса окна", [PY, "tools/test_api.py"], None),
    ]
    if "--ui" in sys.argv:
        steps.append(("Окно в Chrome", [PY, "tools/test_ui.py"], None))
    ok = all([run(*s) for s in steps])
    print("ВСЁ В ПОРЯДКЕ" if ok else "ЕСТЬ ОШИБКИ")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
