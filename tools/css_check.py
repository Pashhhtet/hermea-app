"""Проверка перед релизом: один и тот же CSS-класс не должен задаваться
в разных файлах (вкладки ломают друг другу вёрстку).

python3 tools/css_check.py  -> печатает совпадения, код выхода 1 если есть новые.
Разрешённые общие классы перечислены в SHARED (они общие намеренно).
"""
import re
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent / "program" / "app"

# классы, которые намеренно стилизуются в нескольких файлах (контекстные правки)
SHARED = {"seg", "tag", "pop"}


def blocks(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    for m in re.finditer(r"([^{}]+)\{", text):
        sel = m.group(1).strip()
        if sel.startswith("@") or not sel:
            continue
        yield sel


def first_classes(sel):
    """Классы, стоящие в начале каждого селектора (не уточнённые родителем)."""
    out = set()
    for part in sel.split(","):
        part = part.strip()
        part = re.sub(r"^html\[[^\]]*\]\s*", "", part)
        m = re.match(r"\.([A-Za-z0-9_-]+)", part)
        if m and " " not in part.split(":")[0].strip() and ">" not in part:
            out.add(m.group(1))
        elif m:
            out.add(m.group(1))
    return out


def sources():
    for p in sorted(APP.glob("*.css")):
        yield p.name, p.read_text(encoding="utf-8")
    html = (APP / "index.html").read_text(encoding="utf-8")
    for i, m in enumerate(re.finditer(r"<style[^>]*>(.*?)</style>", html, flags=re.S)):
        yield "index.html", m.group(1)


def main():
    seen = {}
    for name, text in sources():
        for sel in blocks(text):
            # только «голые» правила вида .cls{...} или .cls:hover / .cls.mod — именно они текут в другие вкладки
            for part in sel.split(","):
                part = re.sub(r"^html\[[^\]]*\]\s*", "", part.strip())
                m = re.match(r"\.([A-Za-z0-9_-]+)(?=[:.\[]|$)", part)
                if m:
                    seen.setdefault(m.group(1), set()).add(name)
    bad = {k: v for k, v in seen.items() if len(v) > 1 and k not in SHARED}
    for k, v in sorted(bad.items()):
        print(f".{k}: {', '.join(sorted(v))}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
