#!/usr/bin/env python3
"""HERMEA: обработка фото квартир.
Сайты: Otodom, OLX, Gratka, Morizon, Lento, Tabelaofert, Warsawhomes (+ попытка для любых других).

1. Вставь ссылки на объявления в «ссылки.txt» (по одной на строку).
2. Запусти «Запустить.command».

Для каждой квартиры в папке «Hermea Photo» появится отдельная папка:
    <Район, улица - N pok M m2>/
        hermea/     готовые фото (без знака Otodom, цветокоррекция, логотип)
        oryginal/   исходники
        opis.txt    черновик описания на украинском
Уже обработанные ссылки пропускаются (список в _program/готово.txt).
"""
import json, os, re, sys, time, traceback
from collections import OrderedDict
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sites  # noqa: E402
import rooms  # noqa: E402
import quality  # noqa: E402

PROG = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PROG)                    # папка «Hermea Photo»
LINKS_NAME = "ссылки.txt"
DONE = os.path.join(PROG, "готово.txt")
FONT = os.path.join(PROG, "CormorantGaramond-600.woff2")
LOGO_PNG = os.path.join(PROG, "logo.png")        # если положить свой логотип — будет использован он
MODEL = os.path.join(PROG, "big-lama.pt")
SR_MODEL = os.path.join(PROG, "realesr-general-x4v3.pth")
GOLD = (205, 168, 96)


def _find(name):
    """Файл может лежать и в _program, и уровнем выше — берём тот, что есть."""
    for d in (PROG, ROOT):
        for n in (name, name + ".txt"):   # Windows прячет расширения: бывает «telegram.txt.txt»
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return os.path.join(ROOT, name)


def read_text(path):
    """Читает текстовый файл в любой кодировке, которую мог выбрать Блокнот."""
    raw = open(path, "rb").read()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    if len(raw) > 4 and raw[1:2] == b"\x00" and raw[3:4] == b"\x00":
        return raw.decode("utf-16-le")
    for enc in ("utf-8-sig", "cp1251", "cp1250"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", "ignore")


# ======================================================================= сеть
def http():
    from curl_cffi import requests
    s = requests.Session(impersonate="chrome")
    s.headers.update({"Accept-Language": "pl-PL,pl;q=0.9"})
    return s


def folder_name(i):
    area = i["sub"] or i["district"]
    street = i["street"].replace("ul. ", "")
    place = ", ".join(x for x in [area, street if street != area else ""] if x)
    size = " ".join(x for x in [f"{i['rooms']} pok" if i.get("rooms") else "", f"{i['area']} m2" if i.get("area") else ""] if x)
    name = " - ".join(x for x in [place, size] if x) or f"{i['site']} {i['id']}"
    name = re.sub(r'[\\/:*?"<>|]', "", name).strip() or i["id"]
    path = os.path.join(ROOT, "Квартиры", name)
    if os.path.exists(path):              # квартиру обрабатывают повторно — новая папка, старую не трогаем
        base = path = f"{path} ({i['id']})"
        n = 2
        while os.path.exists(path):
            path = f"{base} {n}"
            n += 1
    return path


def pln(v):
    return f"{v:,}".replace(",", " ") + " zł" if v is not None else "—"


NO_FEE_LINE = "🔥 БЕЗ КОМІСІЇ ДЛЯ ОРЕНДАРЯ 🔥"


def opis(i, no_fee=False):
    place = ", ".join(x for x in [i["district"], i["sub"]] if x)
    lines = ([NO_FEE_LINE, ""] if no_fee else []) + [" | ".join(x for x in [f"🏡 {i['rooms']} кімн." if i.get("rooms") else "🏡",
                                     f"{i['area']} м²" if i.get("area") else "", place] if x),
             f"📍 {i['street'] + ', ' if i['street'] else ''}{i['city']}"]
    feats = []
    f = set(i.get("flags") or [])
    b = [n for k, n in [("balcony", "балкон"), ("terrace", "тераса"), ("garden", "сад"),
                        ("garage", "паркомісце в гаражі"), ("lift", "ліфт")] if k in f]
    if b: feats.append("✨ " + ", ".join(b).capitalize())
    a = (["мебльована"] if "furniture" in f else []) + \
        [n for k, n in [("dishwasher", "посудомийка"), ("washing_machine", "пральна машина"),
                        ("air_conditioning", "кондиціонер")] if k in f]
    if a: feats.append("🛋 " + ", ".join(a).capitalize())
    if "security" in f:
        feats.append("🛡 Охорона / закритий комплекс")
    elif i.get("build_year") and str(i["build_year"]).isdigit() and int(i["build_year"]) >= 2018:
        feats.append(f"🏗 Новобудова {i['build_year']}")
    if "pets" in f and len(feats) < 3:
        feats.append("🐾 Можна з тваринами")
    lines += feats[:3]
    total = (i["price"] or 0) + (i["rent"] or 0) if i["price"] else None
    lines += ["", f"💰 Оренда: {pln(i['price'])}", f"🏢 Адмін. платіж: {pln(i['rent'])}",
              f"📌 Разом: {pln(total)}", f"🔐 Застава: {pln(i['deposit'])}", "", "📩 Запрошую на перегляд!"]
    return "\n".join(lines) + "\n"

# ======================================================================= watermark
def watermark_mask(img):
    h, w = img.shape[:2]
    x0, x1 = 4, int(0.175 * w) + 6
    y0, y1 = int(h - 10 - 0.034 * w) - 6, h - 3
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    roi = g[y0:y1, x0:x1]
    bg = cv2.medianBlur(roi.astype(np.uint8), 31).astype(np.float32)
    m = ((roi > 225) | (roi - bg > 35)).astype(np.uint8) * 255
    mask = np.zeros((h, w), np.uint8)
    mask[y0:y1, x0:x1] = m
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=max(3, w // 400))
    if (m > 0).mean() > 0.6:
        mask[y0:y1, x0:x1] = 255
    return mask


class Lama:
    def __init__(self, path):
        import torch
        torch.set_num_threads(max(1, os.cpu_count() or 4))
        self.torch = torch
        self.model = torch.jit.load(path, map_location="cpu").eval()

    def __call__(self, img, mask):
        torch = self.torch
        ys, xs = np.where(mask > 0)
        if len(xs) == 0:
            return img
        h, w = img.shape[:2]
        pad = 160
        cx1 = min(w, xs.max() + pad)
        cy0 = max(0, ys.min() - pad)
        crop, mcrop = img[cy0:h, 0:cx1], mask[cy0:h, 0:cx1]
        ch, cw = crop.shape[:2]
        ph, pw = (8 - ch % 8) % 8, (8 - cw % 8) % 8
        c = cv2.copyMakeBorder(crop, 0, ph, 0, pw, cv2.BORDER_REFLECT)
        mm = cv2.copyMakeBorder(mcrop, 0, ph, 0, pw, cv2.BORDER_REFLECT)
        t = torch.from_numpy(cv2.cvtColor(c, cv2.COLOR_BGR2RGB)).permute(2, 0, 1)[None].float() / 255
        tm = torch.from_numpy((mm > 0).astype(np.float32))[None, None]
        with torch.no_grad():
            out = self.model(t, tm)[0].permute(1, 2, 0).numpy()
        out = cv2.cvtColor(np.clip(out * 255, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)[:ch, :cw]
        res = img.copy()
        soft = cv2.GaussianBlur(mcrop.astype(np.float32) / 255, (0, 0), 1.5)[..., None]
        res[cy0:h, 0:cx1] = (out * soft + crop * (1 - soft)).astype(np.uint8)
        return res

# ======================================================================= colour
# Белый чуть тёплый (b≈+4). Яркость поднимаем умеренно: раньше всё тянулось к одной
# яркости (~0.74) и белое выжигалось, а шум сжатия Otodom превращался в «зерно».
TARGET_A, TARGET_B = 1.2, 3.5      # светлые стены: чуть тёплые, как на хороших объявлениях


def white_balance(lab):
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    ch = np.hypot(A, B)
    lo = np.percentile(L, 45)
    sel = (L > lo) & (L < 250) & (ch < max(np.percentile(ch, 40), 6))
    if sel.sum() < 500:
        sel = (L > lo) & (L < 250)
    ma, mb = float(np.median(A[sel])), float(np.median(B[sel]))
    da = np.clip(TARGET_A - ma, -9, 9)
    db = np.clip(TARGET_B - mb, -14, 8)
    # сдвиг сильнее в светлом (там видна «грязь»), слабее в тенях — дерево остаётся живым
    wgt = np.clip((L - 40) / 120, 0.35, 1.0)
    lab[..., 1] += da * wgt
    lab[..., 2] += db * wgt
    return lab


def tame_cast(lab, k=0.9):
    """Жёлто-розовая подсветка ламп на светлых стенах/потолке -> к «чуть тёплому белому».
    Насыщенные вещи (дерево, подушки, картины) не трогаем."""
    L = lab[..., 0] / 255
    A, B = lab[..., 1] - 128, lab[..., 2] - 128
    dA, dB = A - TARGET_A, B - TARGET_B
    ch = np.hypot(dA, dB)
    ang = np.degrees(np.arctan2(B, A))
    warm = ((ang > -35) & (ang < 110)).astype(np.float32)
    wl = np.clip((L - 0.42) / 0.2, 0, 1)
    c0 = 12 + 22 * np.clip((L - 0.6) / 0.25, 0, 1)
    wc = np.clip(1 - (ch - c0) / 14, 0, 1)
    w = cv2.GaussianBlur(warm * wl * wc, (0, 0), 3) * k
    lab[..., 1] = 128 + TARGET_A + dA * (1 - w)
    lab[..., 2] = 128 + TARGET_B + dB * (1 - w)
    return lab


def tone(lab):
    """Мягко: тени чуть светлее, середина подтягивается не больше чем на ~7 пунктов,
    светлые стены и белая мебель сохраняют свой рисунок (без сжатия светов)."""
    L = lab[..., 0] / 255.0
    eps = 1e-3
    h, w = L.shape
    logL = np.log(L + eps)
    r = max(8, int(max(h, w) * 0.02))
    small = cv2.resize(logL.astype(np.float32), (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    base = cv2.resize(cv2.bilateralFilter(small, 0, 0.35, r / 4), (w, h), interpolation=cv2.INTER_LINEAR)
    detail = logL - base
    mid = np.percentile(base, 60)
    # тени поднимаем только ниже середины, светлое не трогаем
    lift = np.where(base < mid, (mid - base) * 0.12, 0.0)
    L2 = np.clip(np.exp(base + lift + detail) - eps, 0, 1)
    m = float(np.median(L2))
    target = m + float(np.clip(0.70 - m, 0, 0.12)) * 0.6
    g = np.log(max(target, 1e-3)) / np.log(max(m, 1e-3)) if 0.02 < m < 0.98 else 1.0
    g = float(np.clip(g, 0.82, 1.0))
    L3 = L2 ** g
    gain = (L3 + 0.02) / (L + 0.02)
    lab[..., 0] = np.clip(L3 * 255, 0, 255)
    sat = np.clip(gain, 0.85, 1.4) ** 0.3
    lab[..., 1] = (lab[..., 1] - 128) * sat + 128
    lab[..., 2] = (lab[..., 2] - 128) * sat + 128
    return lab


def vibrance(img, amt=0.12):
    """Мягкая насыщенность: бледные цвета чуть живее, яркие не трогаем. float BGR -> float BGR."""
    hsv = cv2.cvtColor(np.clip(img.astype(np.float32) / 255.0, 0, 1), cv2.COLOR_BGR2HSV)
    s = hsv[..., 1]
    hsv[..., 1] = np.clip(s + amt * s * (1 - s) * 2, 0, 1)
    return np.clip(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR) * 255.0, 0, 255)


def clarity(img, amt=0.18):
    """Локальный контраст в средних тонах. float BGR -> float BGR."""
    lab = quality.lab_f(img)
    L = lab[..., 0]
    r = max(img.shape[:2]) / 80
    blur = cv2.GaussianBlur(L, (0, 0), r)
    mid = 1 - np.abs(L / 255 - 0.5) * 2          # меньше всего в самых светлых и тёмных
    lab[..., 0] = np.clip(L + (L - blur) * amt * np.clip(mid, 0.2, 1), 0, 255)
    return quality.bgr_f(lab)


def enhance(img):
    """Естественный светлый интерьер: чистый белый, чуть светлее тени, без пересвета и «зерна».
    Яркость поднимаем умеренно, светлые поверхности не выжигаем, мелкий шум сжатия не усиливаем."""
    lab = quality.lab_f(img)                             # всё в float — без «ступенек» на белом
    med = float(np.median(lab[..., 0])) / 2.55          # уже светлое фото трогаем ещё мягче
    soft = float(np.clip((med - 55) / 15, 0, 1))
    lab = white_balance(lab)
    lab = tame_cast(lab, 0.7)
    lab = tone(lab)
    out = quality.bgr_f(np.clip(lab, 0, 255))
    out = clarity(out, 0.10 - 0.06 * soft)
    out = vibrance(out, 0.08 - 0.05 * soft)
    return out


def is_floor_plan(img):
    small = cv2.resize(img, (200, 200), interpolation=cv2.INTER_AREA)
    _, counts = np.unique((small // 32).reshape(-1, 3), axis=0, return_counts=True)
    return counts.max() / counts.sum() > 0.7

# ======================================================================= logo
def add_logo(img_bgr):
    im = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    W, H = im.size
    s = min(W, H)
    margin = int(s * 0.035)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if os.path.exists(LOGO_PNG):
        lg = Image.open(LOGO_PNG).convert("RGBA")
        lh = int(s * 0.16)
        lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
        blk_w, blk_h = lg.size
        bx, by = W - margin - blk_w, H - margin - blk_h
        layer.paste(lg, (bx, by), lg)
    else:
        fh = ImageFont.truetype(FONT, int(s * 0.085))
        ft = ImageFont.truetype(FONT, int(s * 0.034))
        word, spacing = "HERMEA", int(s * 0.034 * 0.32)
        widths = [ft.getbbox(c)[2] - ft.getbbox(c)[0] for c in word]
        tw = sum(widths) + spacing * (len(word) - 1)
        hb = fh.getbbox("H"); hw, hh = hb[2] - hb[0], hb[3] - hb[1]
        tb = ft.getbbox("H"); th = tb[3] - tb[1]
        gap = int(s * 0.022)
        blk_w, blk_h = max(tw, hw), hh + gap + th
        bx, by = W - margin - blk_w, H - margin - blk_h
        d = ImageDraw.Draw(layer)
        d.text((bx + (blk_w - hw) / 2 - hb[0], by - hb[1]), "H", font=fh, fill=GOLD + (255,))
        x = bx + (blk_w - tw) / 2
        for c, cw in zip(word, widths):
            d.text((x - ft.getbbox(c)[0], by + hh + gap - tb[1]), c, font=ft, fill=GOLD + (255,))
            x += cw + spacing
    # без тёмного пятна за знаком: только тонкая тень по контуру букв, чтобы знак читался на белом
    glow = layer.split()[3].filter(ImageFilter.GaussianBlur(max(2, s // 500)))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 255)); g.putalpha(glow.point(lambda v: int(v * 0.6)))
    im = Image.alpha_composite(Image.alpha_composite(im, g), layer)
    return cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)

# ======================================================================= Telegram
TG_CONF = _find("telegram.txt")


def tg_config():
    global TG_CONF
    TG_CONF = _find("telegram.txt")
    conf = {}
    if os.path.exists(TG_CONF):
        for line in read_text(TG_CONF).splitlines():
            line = line.strip().lstrip("\ufeff")
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                conf[k.strip().upper()] = v.strip().strip('"').strip("'").strip("<>").replace(" ", "")
    return conf.get("TOKEN", ""), conf.get("CHAT_ID", "")


def _ssl_ctx():
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def tg_call(token, method, fields=None, files=None):
    import urllib.request, urllib.error, uuid
    url = f"https://api.telegram.org/bot{token}/{method}"
    for attempt in range(5):
        if files:
            b = uuid.uuid4().hex
            body = bytearray()
            for k, v in (fields or {}).items():
                body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
            for k, (name, data) in files.items():
                body += (f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\n'
                         f'Content-Type: image/jpeg\r\n\r\n').encode() + data + b"\r\n"
            body += f"--{b}--\r\n".encode()
            req = urllib.request.Request(url, data=bytes(body),
                                         headers={"Content-Type": f"multipart/form-data; boundary={b}"})
        else:
            req = urllib.request.Request(url, data=json.dumps(fields or {}).encode(),
                                         headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120, context=_ssl_ctx()) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            res = json.loads(e.read() or b"{}")
            params = res.get("parameters") or {}
            if params.get("migrate_to_chat_id") and fields and "chat_id" in fields:
                fields["chat_id"] = str(params["migrate_to_chat_id"])
                _save_chat(fields["chat_id"])
                continue
            wait = params.get("retry_after")
            if wait:
                time.sleep(wait + 1)
                continue
            raise RuntimeError(res.get("description") or str(e))
        except (urllib.error.URLError, OSError) as e:
            if attempt >= 4:
                raise RuntimeError(f"нет связи с Telegram ({e})")
            wait = (3, 8, 20, 45)[attempt]
            print(f"    нет связи с Telegram, жду {wait} с...", flush=True)
            time.sleep(wait)
            continue
    raise RuntimeError("Telegram: слишком много попыток")


def tg_find_chat(token):
    """Если CHAT_ID пустой — ищем чаты, где бот видел сообщения."""
    res = tg_call(token, "getUpdates")
    chats = {}
    for u in res.get("result", []):
        m = u.get("message") or u.get("channel_post") or u.get("my_chat_member") or {}
        c = m.get("chat")
        if c:
            chats.pop(c["id"], None)          # последний чат, где писали боту, — в конце
            chats[c["id"]] = c.get("title") or c.get("first_name") or str(c["id"])
    return chats


def _save_chat(chat):
    txt = read_text(TG_CONF) if os.path.exists(TG_CONF) else "TOKEN=\nCHAT_ID=\n"
    if re.search(r"(?m)^CHAT_ID\s*=", txt):
        txt = re.sub(r"(?m)^CHAT_ID\s*=.*$", f"CHAT_ID={chat}", txt)
    else:
        txt = txt.rstrip("\n") + f"\nCHAT_ID={chat}\n"
    open(TG_CONF, "w", encoding="utf-8").write(txt)


def tg_setup():
    token, chat = tg_config()
    if not os.path.exists(TG_CONF):
        print(f"Telegram: выключен — не нашёл файл telegram.txt (искал рядом с программой).")
        return None, None
    if not token:
        print(f"Telegram: выключен — в telegram.txt пустая строка TOKEN= ({TG_CONF})")
        return None, None
    if not re.fullmatch(r"\d{5,}:[A-Za-z0-9_-]{20,}", token):
        print(f"Telegram: TOKEN выглядит неправильно ({token[:12]}...). Скопируй его из @BotFather целиком.")
        return None, None
    try:
        me = tg_call(token, "getMe")["result"]
    except Exception as e:
        msg = str(e)
        if any(x in msg for x in ("Unauthorized", "Not Found", "401", "404")):
            print("Telegram: токен не принят Telegram. Проверь TOKEN в telegram.txt (может, бота пересоздали).")
        else:
            print(f"Telegram: нет связи с Telegram ({msg}).")
            print("  Возможно, интернет или рабочая сеть блокирует Telegram. Продолжаю без отправки.")
        return None, None
    bot = "@" + me.get("username", "bot")
    if chat:
        return token, chat
    try:
        tg_call(token, "deleteWebhook")
    except Exception:
        pass
    chats = tg_find_chat(token)
    if not chats:
        print(f"Telegram: бот {bot} пока не знает, в какой чат слать.")
        print(f"  Сейчас напиши /start в нужном чате (бот {bot} должен быть в нём). Жду до 2 минут...")
        for _ in range(40):
            time.sleep(3)
            chats = tg_find_chat(token)
            if chats:
                break
    if not chats:
        print("  Не дождался сообщения. Продолжаю без отправки, в следующий раз попробуй снова.")
        return None, None
    items = list(chats.items())
    if len(items) == 1:
        cid, title = items[0]
    else:
        print("Telegram: бот видит несколько чатов:")
        for n, (cid, title) in enumerate(items, 1):
            print(f"  {n}. {title}")
        while True:
            a = input(f"  Введи номер чата (1-{len(items)}) и нажми Enter: ").strip()
            if a.isdigit() and 1 <= int(a) <= len(items):
                cid, title = items[int(a) - 1]
                break
    _save_chat(cid)
    print(f"Telegram: буду слать в «{title}». Сохранил в telegram.txt")
    try:
        tg_call(token, "sendMessage", {"chat_id": cid, "text": "✅ HERMEA подключена к этому чату"})
    except Exception as e:
        print(f"  ✗ не смог написать в чат: {e}")
        return None, None
    return token, tg_config()[1] or str(cid)


TG_MAX_PHOTOS = 10      # в Telegram уходит не больше 10 фото (одним альбомом)
TG_CAPTION_MAX = 1024   # лимит подписи Telegram


def tg_send(token, chat, folder):
    chat = tg_config()[1] or chat
    ready = os.path.join(folder, "hermea")
    photos = sorted((p for p in os.listdir(ready) if p.lower().endswith(".jpg")),
                    key=lambda f: int(re.sub(r"\D", "", f) or 0))[:TG_MAX_PHOTOS]
    text = open(os.path.join(folder, "opis.txt"), encoding="utf-8").read().split("\n---\n")[0].strip()
    caption = text if len(text) <= TG_CAPTION_MAX else None
    if len(photos) == 1:
        fields = {"chat_id": chat}
        if caption:
            fields["caption"] = caption
        tg_call(token, "sendPhoto", fields, {"photo": (photos[0], open(os.path.join(ready, photos[0]), "rb").read())})
    elif photos:
        media = [{"type": "photo", "media": f"attach://f{i}"} for i in range(len(photos))]
        if caption:
            media[0]["caption"] = caption
        files = {f"f{i}": (p, open(os.path.join(ready, p), "rb").read()) for i, p in enumerate(photos)}
        tg_call(token, "sendMediaGroup", {"chat_id": chat, "media": json.dumps(media, ensure_ascii=False)}, files)
    if not caption:   # описание длиннее лимита подписи — отдельным сообщением
        tg_call(token, "sendMessage", {"chat_id": chat, "text": text})

PENDING = os.path.join(PROG, "telegram_ne_otpravleno.txt")


def tg_pending_add(folder):
    with open(PENDING, "a", encoding="utf-8") as f:
        f.write(folder + "\n")


def tg_pending_flush(token, chat):
    """Досылает квартиры, которые не ушли в Telegram из-за обрыва связи."""
    if not os.path.exists(PENDING):
        return
    items = [l.strip() for l in read_text(PENDING).splitlines() if l.strip()]
    items = list(OrderedDict.fromkeys(i for i in items if os.path.isdir(i)))
    if not items:
        os.remove(PENDING)
        return
    print(f"Telegram: досылаю {len(items)} квартир(ы), которые не ушли в прошлый раз...")
    left = []
    for folder in items:
        try:
            tg_send(token, chat, folder)
            print(f"  ✓ {os.path.basename(folder)}")
            time.sleep(2)
        except Exception as e:
            print(f"  ✗ {os.path.basename(folder)}: {e}")
            left.append(folder)
    if left:
        open(PENDING, "w", encoding="utf-8").write("\n".join(left) + "\n")
    else:
        os.remove(PENDING)


# ======================================================================= main
NET_WAITS = (3, 8, 20, 45)   # паузы между повторами, если пропал интернет


def hi_res(url):
    """Otodom/OLX по умолчанию отдают 1280px с сильным сжатием — просим 2560px, качество 92."""
    if "apollo.olxcdn.com" in url:
        return url.split(";")[0] + ";s=2560x1920;q=92"
    return url


def download(sess, url):
    tries = [url]
    if hi_res(url) != url:
        tries.insert(0, hi_res(url))
    if "/adpics/original/" in url:
        tries.append(url.replace("/adpics/original/", "/adpics/large/"))
    last = None
    for u in tries:
        for n, wait in enumerate((0,) + NET_WAITS):
            if wait:
                print(f"      нет связи, жду {wait} с и пробую ещё раз...", flush=True)
                time.sleep(wait)
            try:
                r = sess.get(u, timeout=60)
                if r.status_code == 200 and len(r.content) > 2000:
                    return r.content
                last = f"код {r.status_code}"
                if r.status_code < 500 and r.status_code != 429:
                    break          # 404 и т.п. — повтор не поможет
            except Exception as e:
                last = e
    raise RuntimeError(f"не скачал фото ({last})")


def with_retries(fn, what):
    last = None
    for wait in (0,) + NET_WAITS:
        if wait:
            print(f"    нет связи ({what}), жду {wait} с и пробую ещё раз...", flush=True)
            time.sleep(wait)
        try:
            return fn()
        except Exception as e:
            last = e
            msg = str(e)
            # ошибки сети — повторяем; остальные (нет данных, капча и т.п.) — сразу наверх
            if not any(x in msg for x in ("connect", "Connect", "resolve", "getaddrinfo", "timed out",
                                          "Timeout", "timeout", "Network", "network", "reset",
                                          "Errno", "SSL", "EOF", "curl: (")):
                raise
    raise last


_LAMA = None
_ROOMS = None
_SR = False


def super_res():
    global _SR
    if _SR is False:
        _SR = None
        if os.path.exists(SR_MODEL):
            try:
                _SR = quality.SuperRes(SR_MODEL)
            except Exception as e:
                print(f"  (нейросеть чёткости не загрузилась: {e})")
        else:
            print("  (нет нейросети чёткости — запусти установку ещё раз)")
    return _SR


def room_classifier():
    global _ROOMS
    if _ROOMS is None:
        _ROOMS = rooms.RoomClassifier(PROG)
        if not _ROOMS.ok:
            print(f"  (кухню первой не ставлю: {_ROOMS.why}. Запусти установку ещё раз.)")
    return _ROOMS


def lama():
    global _LAMA
    if _LAMA is None:
        _LAMA = Lama(MODEL)
    return _LAMA


def process_photo(img, plan=False, watermark=None):
    """Одно фото: водяной знак, выравнивание, цвет, резкость, логотип -> (jpg, пометки)."""
    if watermark == "otodom":
        img = lama()(img, watermark_mask(img))
    tags = []
    if not plan:
        img, how = quality.straighten(img)
        if how == "ok":
            tags.append("выровнено")
    # без нейросетевого «увеличения»: оно делало фото мыльными и «нарисованными»
    side = max(img.shape[:2])
    if side < 1280:
        img, _ = quality.upscale_to(img, 1280, None)
    if not plan:
        # «квадратики» сжатия Otodom на стенах и потолке: чистим до и после цветокоррекции
        img, _ = quality.deblock(img)
        img = enhance(img)
        img, flat = quality.deblock(img)
        img = quality.sharpen(img, amount=0.3, radius=0.8, threshold=3)
        img = quality.dither(img, flat)
    img = add_logo(img)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 93])
    return buf.tobytes(), tags


def _kitchen_first(done, clf):
    kitchens = [i for i, d in enumerate(done) if d["label"] == "kitchen"]
    if kitchens:
        best = max(kitchens, key=lambda i: done[i]["kitchen"])
        done.insert(0, done.pop(best))
    elif clf.ok:
        print("    кухню на фото не нашёл — порядок как есть")


def process_listing(sess, url, progress=None, no_fee=False):
    """progress(событие, **данные) — для окна приложения (Hermea.app); в консоли не нужен."""
    def emit(ev, **kw):
        if progress:
            progress(ev, **kw)
    info = with_retries(lambda: sites.get_listing(sess, url), "страница объявления")
    out = folder_name(info)
    existed = os.path.exists(out)
    orig, ready = os.path.join(out, "oryginal"), os.path.join(out, "hermea")
    os.makedirs(orig, exist_ok=True); os.makedirs(ready, exist_ok=True)
    seen, total, done = set(), len(info["images"]), []
    emit("listing", info=info, out=out, total=total, existed=existed)
    clf = room_classifier()
    for k, im in enumerate(info["images"], 1):
        emit("photo_start", k=k, total=total)
        try:
            data = download(sess, im["url"])
        except Exception as e:
            print(f"    ✗ фото {k}: {e}")
            continue
        if data in seen:          # одинаковые фото в объявлении
            continue
        seen.add(data)
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if img is None or min(img.shape[:2]) < 200:
            continue
        ext = (re.search(r"\.(webp|jpe?g|png)", im["url"].lower()) or [None, "jpg"])[1]
        open(os.path.join(orig, f"{k:02d}.{ext}"), "wb").write(data)
        plan = bool(im.get("plan")) or is_floor_plan(img)
        label, kitchen = (None, 0.0) if plan else clf.classify(img)
        if not clf.ok and str(im.get("room") or "").upper() == "KITCHEN":   # подсказка Otodom
            label, kitchen = "kitchen", 1.0
        jpg, tags = process_photo(img, plan, info.get("watermark"))
        done.append({"jpg": jpg, "label": label, "kitchen": kitchen, "src": f"{k:02d}.{ext}"})
        if label == "kitchen":
            tags.append("кухня")
        emit("photo", k=k, n=len(done), total=total, jpg=done[-1]["jpg"], label=label)
        print(f"    фото {len(done)}/{total}" + (f" ({', '.join(tags)})" if tags else ""), flush=True)
    if not done:
        raise RuntimeError("ни одно фото не обработалось")
    _kitchen_first(done, clf)      # кухня — первой; остальные в исходном порядке
    for n, d in enumerate(done, 1):
        open(os.path.join(ready, f"p{n}_hermea.jpg"), "wb").write(d["jpg"])
    n = len(done)
    try:   # какое готовое фото из какого оригинала — для сравнения «до/после» в приложении
        meta = {"url": url, "site": info["site"], "id": info["id"], "created": time.strftime("%Y-%m-%d %H:%M"),
                "photos": {f"p{i}_hermea.jpg": d["src"] for i, d in enumerate(done, 1)}}
        with open(os.path.join(out, ".hermea.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=1)
    except Exception:
        pass
    with open(os.path.join(out, "opis.txt"), "w", encoding="utf-8") as f:
        f.write(opis(info, no_fee))
        f.write(f"\n---\nЧерновик, проверь перед публикацией.\nСайт: {info['site']}\nОригинал: {url}\nЗаголовок: {info['title']}\n")
    with open(DONE, "a", encoding="utf-8") as f:
        f.write(info["id"] + "\t" + url + "\n")
    return out, n


def read_photo_file(path):
    """Фото с телефона: JPG/PNG/HEIC, с учётом поворота из EXIF. -> BGR или None."""
    try:                                    # HEIC на Windows: библиотека pillow-heif (ставит установщик)
        import pillow_heif
        pillow_heif.register_heif_opener()
    except Exception:
        pass
    try:
        from PIL import ImageOps
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    except Exception:
        pass
    if sys.platform == "darwin":            # HEIC с iPhone: переводим в JPG встроенной утилитой macOS
        import subprocess, tempfile
        tmp = os.path.join(tempfile.gettempdir(), f"hermea_{os.getpid()}_{time.time_ns()}.jpg")
        try:
            subprocess.run(["sips", "-s", "format", "jpeg", path, "--out", tmp],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            if os.path.exists(tmp):
                return cv2.imdecode(np.fromfile(tmp, np.uint8), cv2.IMREAD_COLOR)
        except Exception:
            pass
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    return cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)


def local_folder(name):
    name = re.sub(r'[\\/:*?"<>|]', "", name or "").strip() or time.strftime("Свои фото %d.%m %H-%M")
    path = os.path.join(ROOT, "Квартиры", name)
    base, n = path, 2
    while os.path.exists(path):
        path = f"{base} ({n})"
        n += 1
    return path


def process_local(name, files, progress=None, no_fee=False):
    """Свои фото (с телефона после показа): та же обработка, без водяного знака и без описания с сайта."""
    def emit(ev, **kw):
        if progress:
            progress(ev, **kw)
    import shutil
    out = local_folder(name)
    orig, ready = os.path.join(out, "oryginal"), os.path.join(out, "hermea")
    os.makedirs(orig, exist_ok=True); os.makedirs(ready, exist_ok=True)
    total, done = len(files), []
    emit("listing", info={"price": None, "rent": None, "deposit": None}, out=out, total=total, existed=False)
    clf = room_classifier()
    for k, path in enumerate(files, 1):
        emit("photo_start", k=k, total=total)
        img = read_photo_file(path)
        if img is None or min(img.shape[:2]) < 200:
            print(f"    ✗ фото {k}: не открывается")
            continue
        h, w = img.shape[:2]
        if max(h, w) > 2560:                # фото с телефона огромные — уменьшаем до 2560
            s = 2560 / max(h, w)
            img = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        ext = os.path.splitext(path)[1].lower() or ".jpg"
        src = f"{k:02d}{ext}"
        shutil.copyfile(path, os.path.join(orig, src))
        plan = is_floor_plan(img)
        label, kitchen = (None, 0.0) if plan else clf.classify(img)
        jpg, tags = process_photo(img, plan, None)
        done.append({"jpg": jpg, "label": label, "kitchen": kitchen, "src": src})
        emit("photo", k=k, n=len(done), total=total, jpg=jpg, label=label)
        print(f"    фото {len(done)}/{total}", flush=True)
    if not done:
        shutil.rmtree(out, ignore_errors=True)
        raise RuntimeError("ни одно фото не обработалось")
    _kitchen_first(done, clf)
    for n, d in enumerate(done, 1):
        open(os.path.join(ready, f"p{n}_hermea.jpg"), "wb").write(d["jpg"])
    title = os.path.basename(out)
    with open(os.path.join(out, "opis.txt"), "w", encoding="utf-8") as f:
        f.write((NO_FEE_LINE + "\n\n" if no_fee else "") + f"🏡 {title}\n\n📩 Запрошую на перегляд!\n\n---\nСвои фото, описание впиши сам.\n")
    try:
        meta = {"kind": "local", "created": time.strftime("%Y-%m-%d %H:%M"),
                "photos": {f"p{i}_hermea.jpg": d["src"] for i, d in enumerate(done, 1)}}
        with open(os.path.join(out, ".hermea.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=1)
    except Exception:
        pass
    return out, len(done)


def clean_url(u):
    u = u.strip()
    # у OLX и Otodom хвост «?search_reason=...» не нужен, у остальных сайтов параметры оставляем
    if any(d in u for d in ("otodom.pl", "olx.pl", "gratka.pl", "morizon.pl", "tabelaofert.pl", "lento.pl")):
        u = u.split("?")[0].split("#")[0]
    return u



DATE_RE = re.compile(r"^\s*=+\s*(\d{2}\.\d{2}\.\d{4})\s*=+\s*$")


def mark_new_day(links, done):
    """Перед первой новой ссылкой дня вставляет строку с сегодняшней датой."""
    today = time.strftime("%d.%m.%Y")
    lines = read_text(links).splitlines()
    first_new = None
    for k, l in enumerate(lines):
        u = l.strip().lstrip("\ufeff")
        if u.startswith("http") and clean_url(u) not in done:
            first_new = k
            break
    if first_new is None:
        return
    last_date = None
    for l in lines[:first_new]:
        m = DATE_RE.match(l)
        if m:
            last_date = m.group(1)
    if last_date == today:
        return
    head = ([""] if first_new > 0 and lines[first_new - 1].strip() else [])
    lines[first_new:first_new] = head + [f"===== {today} ====="]
    with open(links, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    links = _find(LINKS_NAME)
    if not os.path.exists(links):
        open(links, "w").close()
    urls = [u.strip().lstrip("\ufeff") for u in read_text(links).splitlines() if u.strip().lstrip("\ufeff").startswith("http")]
    done = open(DONE, encoding="utf-8").read() if os.path.exists(DONE) else ""
    try:
        mark_new_day(links, done)
    except Exception as e:
        print(f"  (не смог поставить дату в ссылках: {e})")
    todo = list(OrderedDict.fromkeys(u for u in urls if clean_url(u) not in done))
    if not todo and not os.path.exists(PENDING):
        print("Новых ссылок нет. Вставь ссылки в «ссылки.txt» и запусти снова.")
        return
    tg_wanted = bool(tg_config()[0])
    tg_token, tg_chat = tg_setup()
    if tg_token:
        print("Telegram: отправка включена.")
        tg_pending_flush(tg_token, tg_chat)
    if not todo:
        print("Новых ссылок нет. Вставь ссылки в «ссылки.txt» и запусти снова.")
        return
    print(f"Квартир к обработке: {len(todo)}.", flush=True)
    sess = http()
    ok, fail = 0, []
    for i, u in enumerate(todo, 1):
        print(f"\n[{i}/{len(todo)}] {u}", flush=True)
        try:
            out, n = process_listing(sess, clean_url(u))
            print(f"  ✓ {n} фото → {os.path.basename(out)}")
            if tg_wanted and not tg_token:
                tg_pending_add(out)
                print("    Telegram сейчас недоступен — дошлю при следующем запуске")
            if tg_token:
                try:
                    tg_send(tg_token, tg_chat, out)
                    print("  ✓ отправлено в Telegram")
                except Exception as e:
                    print(f"  ✗ Telegram: {e}")
                    print("    дошлю эту квартиру в Telegram при следующем запуске программы")
                    tg_pending_add(out)
            ok += 1
        except Exception as e:
            print(f"  ✗ ошибка: {e}")
            traceback.print_exc(limit=1)
            fail.append(u)
        time.sleep(2)
    print(f"\nГотово: {ok} из {len(todo)}.")
    if fail:
        print("Не получилось (попробуй ещё раз позже):\n  " + "\n  ".join(fail))


def test_telegram():
    print("=== Проверка Telegram ===")
    token, chat = tg_config()
    print("Файл настроек:", TG_CONF, "— есть" if os.path.exists(TG_CONF) else "— НЕ НАЙДЕН")
    print("TOKEN:", (token[:10] + "..." + token[-4:]) if token else "ПУСТО")
    print("CHAT_ID:", chat or "пусто (программа найдёт сама)")
    t, c = tg_setup()
    if not t:
        print("\n✗ Отправка не работает — причина написана выше.")
        return
    tg_call(t, "sendMessage", {"chat_id": c, "text": "✅ HERMEA: проверка связи — всё работает"})
    print(f"\n✓ Всё работает: тестовое сообщение отправлено в чат {c}.")


if __name__ == "__main__":
    if "--test-telegram" in sys.argv:
        try:
            test_telegram()
        except Exception as e:
            print(f"\n✗ Ошибка: {e}")
    else:
        main()
