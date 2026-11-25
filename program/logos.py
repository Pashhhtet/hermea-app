"""Логотипы других агентств на фото объявления (кнопка «Другое агентство»).

Агентство ставит свой знак на все фото объявления в одно и то же место, а комнаты на фото разные.
Поэтому сравниваем фото между собой: перепады яркости (края), которые есть на всех снимках в одной
точке и в одну сторону, — это логотип; края мебели и стен от фото к фото меняются и гасят друг друга.
Найденное место потом стирает та же нейросеть LaMa, что убирает знак Otodom (hermea.Lama).

Нужно хотя бы 3 фото одного формата. Совместимо с Python 3.9.
"""
import cv2
import numpy as np

WORK = 720                 # ширина, на которой ищем (быстро и достаточно точно)
MIN_PHOTOS = 3


def _group_key(img):
    h, w = img.shape[:2]
    return round(w / h, 2)


def _grads(img, size):
    g = cv2.cvtColor(cv2.resize(img, size, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 0.8)
    return cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)


def _consensus(imgs):
    """Карта «одинаковых краёв» для фото одного формата (на рабочем размере) -> float32.
    Край засчитывается, только если он есть почти на всех фото в этой точке и в одну сторону."""
    h, w = imgs[0].shape[:2]
    size = (WORK, max(8, int(round(WORK * h / w))))
    gx, gy = [], []
    for im in imgs:
        x, y = _grads(im, size)
        n = float(np.percentile(np.hypot(x, y), 95)) + 1e-3     # фото разной контрастности -> к одной шкале
        gx.append(x * (40 / n))
        gy.append(y * (40 / n))
    gx, gy = np.stack(gx), np.stack(gy)
    sx, sy = gx.sum(0), gy.sum(0)
    norm = np.hypot(sx, sy) + 1e-3
    ux, uy = sx / norm, sy / norm                          # общее направление края в точке
    proj = gx * ux + gy * uy                               # сила края каждого фото вдоль общего направления
    # самое слабое из фото (при 6+ фото прощаем одно: на планировке или крупном плане знак мог не попасть)
    k = 1 if len(imgs) >= 6 else 0
    return np.sort(proj, axis=0)[k], size


def _mask_from_map(m, size):
    """Карта совпадений -> маска логотипа на рабочем размере (uint8 0/255) или None."""
    w, h = size
    # шкала: 40 — сильный край на обычном фото; случайные совпадения комнат редко выше 7 и одиночные
    seed = (m > 7).astype(np.uint8)
    if seed.sum() < 40:                           # ничего общего на всех фото нет
        return None
    # буквы и значок логотипа — много коротких краёв рядом: склеиваем в одно пятно
    k = max(3, w // 90)
    blob = cv2.morphologyEx(seed, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k * 3, k * 3)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(blob, 8)
    keep = np.zeros_like(blob)
    total = w * h
    for c in range(1, n):
        x, y, bw, bh, area = stats[c]
        edges = int(seed[lab == c].sum())
        # мелкий шум, редкие случайные точки, длинные линии (рамка, край кадра) и половина фото — не логотип
        if edges < 40 or edges < 0.06 * area or area < total * 0.0008 or area > total * 0.22:
            continue
        if (bw > 0.9 * w and bh < 0.04 * h) or (bh > 0.9 * h and bw < 0.04 * w):
            continue
        keep[lab == c] = 1
    if not keep.any():
        return None
    # всё пятно логотипа целиком (буквы вместе с промежутками, значок вместе с серединой) и с запасом:
    # у полупрозрачных букв края размыты, узкая маска оставляет светлые следы
    keep = _fill_holes(keep)
    keep = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k + 1, k + 1)))
    return keep * 255


def _fill_holes(m):
    """Замкнутые фигуры (круг, рамка значка) заливаем целиком: края нашлись, середина — тоже логотип."""
    h, w = m.shape
    flood = np.zeros((h + 2, w + 2), np.uint8)
    inv = (1 - m).astype(np.uint8)
    cv2.floodFill(inv, flood, (0, 0), 2)
    return np.where(inv == 1, 1, m).astype(np.uint8)


def find_masks(imgs, skip=None):
    """imgs: список BGR одного объявления. skip: индексы фото, по которым не искать (планировки).
    -> список масок (uint8 0/255 размера своего фото) или None там, где логотип не найден."""
    skip = set(skip or [])
    groups = {}
    for i, im in enumerate(imgs):
        if im is not None and i not in skip:
            groups.setdefault(_group_key(im), []).append(i)
    found = {}
    for key, idx in groups.items():
        if len(idx) < MIN_PHOTOS:
            continue
        m, size = _consensus([imgs[i] for i in idx])
        mask = _mask_from_map(m, size)
        if mask is not None:
            found[key] = mask
    out = []
    for im in imgs:
        mask = found.get(_group_key(im)) if im is not None else None
        if mask is None:
            out.append(None)
            continue
        h, w = im.shape[:2]
        out.append(cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST))
    return out
