"""Договор о сотрудничестве Hermea (UA/PL): данные клиента накладываются на оригинальный PDF.

Шаблон — PDF компании — хранится только на компьютере: _program/templates/umowa_wspolpracy.pdf
(в нём данные директора, поэтому в репозиторий обновлений он не попадает).
Координаты полей сняты с шаблона «ДОГОВІР ПРО СПІВПРАЦЮ / UMOWA WSPÓŁPRACY» (4 стр., A4).
Совместимо с Python 3.9.
"""
import datetime as dt
import io
import os

PROG = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(PROG, "templates", "umowa_wspolpracy.pdf")
FONT = os.path.join(PROG, "fonts", "DejaVuSans.ttf")
PAGE_H = 841.92

# (страница, x0, x1, линия y сверху) — y как у pdfplumber (от верхнего края)
F = {
    "date_ua": (0, 84, 165, 91.9), "date_pl": (0, 371, 437, 91.7),
    "name_ua": (0, 40, 259, 215.0), "addr_ua": (0, 113, 259, 227.6), "id_ua": (0, 76, 217, 239.6),
    "name_pl": (0, 304, 513, 221.5), "addr_pl": (0, 348, 519, 235.0), "id_pl": (0, 304, 458, 258.4),
    "type_ua": (0, 70, 278, 485.4), "type_pl": (0, 343, 546, 501.7),
    "loc_ua": (0, 130, 280, 506.8), "loc_pl": (0, 363, 544, 523.8),
    "area_ua": (0, 91, 123, 528.0), "area_pl": (0, 383, 415, 546.0),
    "park_ua": (0, 141, 179, 549.5), "park_pl": (0, 389, 427, 567.8),
    "price_ua": (0, 73, 115, 570.9), "price_pl": (0, 339, 435, 589.9),
    "pct_ua": (1, 112, 141, 508.5), "pct_pl": (1, 393, 408, 512.1),
    "a_name": (3, 111, 350, 172.6), "a_addr": (3, 407, 548, 172.6), "a_addr2": (3, 44, 226, 188.4),
    "a_id": (3, 401, 510, 188.4), "a_pesel": (3, 86, 256, 204.3),
    "a_pct_ua": (3, 120, 152, 633.6), "a_pct_pl": (3, 362, 376, 645.6),
}
# приложение №1: таблица просмотренных объектов
ROW_TOP, ROW_H = 293.6, 27.4
COLS = {"date": (57, 113), "addr": (114, 347), "rooms": (348, 390), "rent": (391, 489)}
MAX_ROWS = 7


class ContractError(Exception):
    pass


def available():
    return os.path.isfile(TEMPLATE)


def save_template(data):
    if not data.startswith(b"%PDF"):
        raise ContractError("not_pdf")
    os.makedirs(os.path.dirname(TEMPLATE), exist_ok=True)
    tmp = TEMPLATE + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, TEMPLATE)


def _money(v):
    try:
        v = float(v)
    except Exception:
        return str(v or "")
    s = f"{v:,.0f}".replace(",", " ")
    return s


def fields_for(c, today=None):
    """Карточка клиента -> текст для каждого поля договора."""
    today = today or dt.date.today()
    date = today.strftime("%d.%m.%Y")
    pct = str(c.get("commission") or (100 if (c.get("package") or "").upper() == "COMFORT" else 70))
    ident = " ".join(x for x in [c.get("id_doc") or ""] if x)
    park = c.get("parking") or ""
    park_ua = {"yes": "так", "no": "ні", "": ""}.get(park, park)
    park_pl = {"yes": "tak", "no": "nie", "": ""}.get(park, park)
    return {
        "date_ua": date, "date_pl": date,
        "name_ua": c.get("name", ""), "addr_ua": c.get("address", ""), "id_ua": ident,
        "name_pl": c.get("name", ""), "addr_pl": c.get("address", ""), "id_pl": ident,
        "type_ua": c.get("type", ""), "type_pl": c.get("type", ""),
        "loc_ua": c.get("location", ""), "loc_pl": c.get("location", ""),
        "area_ua": str(c.get("area") or ""), "area_pl": str(c.get("area") or ""),
        "park_ua": park_ua, "park_pl": park_pl,
        "price_ua": _money(c.get("budget")) if c.get("budget") else "",
        "price_pl": _money(c.get("budget")) if c.get("budget") else "",
        "pct_ua": pct, "pct_pl": pct, "a_pct_ua": pct, "a_pct_pl": pct,
        "a_name": c.get("name", ""), "a_addr": c.get("address", ""), "a_addr2": "",
        "a_id": ident, "a_pesel": c.get("pesel", ""),
    }


def _fit(canvas, text, x0, x1, size, minsize=5.5):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    s = size
    while s > minsize and stringWidth(text, "HermeaSans", s) > (x1 - x0):
        s -= 0.25
    return s


def _draw(canvas, text, x0, x1, y_line, size=9.0, center=False):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    text = str(text or "").strip()
    if not text:
        return
    s = _fit(canvas, text, x0, x1, size)
    w = stringWidth(text, "HermeaSans", s)
    x = x0 + max(0, (x1 - x0 - w) / 2) if center else x0 + 1
    canvas.setFont("HermeaSans", s)
    canvas.drawString(x, PAGE_H - y_line + 2.2, text)


def build(client, out_path, today=None):
    """Заполняет договор и пишет PDF в out_path."""
    if not available():
        raise ContractError("no_template")
    try:
        from pypdf import PdfReader, PdfWriter
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas as rl_canvas
    except ImportError:
        raise ContractError("no_libs")
    if "HermeaSans" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("HermeaSans", FONT))
    reader = PdfReader(TEMPLATE)
    n = len(reader.pages)
    vals = fields_for(client, today)
    # адрес в приложении: что не влезло в первую строку — на вторую
    addr = vals["a_addr"]
    if addr and len(addr) > 30:
        cut = addr.rfind(" ", 0, 30)
        cut = cut if cut > 10 else 30
        vals["a_addr"], vals["a_addr2"] = addr[:cut], addr[cut:].strip()
    overlays = []
    for pi in range(n):
        buf = io.BytesIO()
        cv = rl_canvas.Canvas(buf, pagesize=(594.96, PAGE_H))
        cv.setFillColorRGB(0.05, 0.12, 0.35)            # тёмно-синий «как ручкой»
        for key, (p, x0, x1, y) in F.items():
            if p == pi:
                _draw(cv, vals.get(key, ""), x0, x1, y, center=key.startswith(("pct", "a_pct", "area", "park")))
        if pi == 3:
            for i, o in enumerate((client.get("viewed") or [])[:MAX_ROWS]):
                y = ROW_TOP + ROW_H * (i + 1) - 9
                rent = _money(o.get("rent")) + (f" + {_money(o.get('admin'))}" if o.get("admin") else "")
                for col, txt in (("date", o.get("date", "")), ("addr", o.get("address", "")),
                                 ("rooms", o.get("rooms", "")), ("rent", rent.strip())):
                    x0, x1 = COLS[col]
                    _draw(cv, txt, x0 + 2, x1 - 2, y, size=8.5, center=col != "addr")
        cv.save()
        overlays.append(PdfReader(io.BytesIO(buf.getvalue())).pages[0])
    w = PdfWriter()
    for pi, page in enumerate(reader.pages):
        page.merge_page(overlays[pi])
        w.add_page(page)
    tmp = out_path + ".tmp"
    with open(tmp, "wb") as f:
        w.write(f)
    os.replace(tmp, out_path)
    return out_path
