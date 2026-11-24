"""Чёткость и геометрия фото для HERMEA.

straighten(img)        — выпрямляет вертикали (стены, двери, шкафы) и горизонт.
SuperRes(path).run(img) — нейросетевое увеличение маленьких фото (Real-ESRGAN, лёгкая модель).
sharpen(img)           — резкость только по яркости, без усиления шума и цветных ореолов.
Совместимо с Python 3.9.
"""
import math
import os

import cv2
import numpy as np


# =================================================================== геометрия
def _segments(gray):
    h, w = gray.shape
    k = 1000.0 / max(h, w)
    small = cv2.resize(gray, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA) if k < 1 else gray
    k = small.shape[1] / w
    blur = cv2.GaussianBlur(small, (3, 3), 0)
    edges = cv2.Canny(blur, 40, 120)
    sh = small.shape[0]
    lines = cv2.HoughLinesP(edges, 1, np.pi / 720, threshold=60,
                            minLineLength=int(sh * 0.12), maxLineGap=int(sh * 0.012) + 2)
    if lines is None:
        return np.zeros((0, 4))
    return np.asarray(lines).reshape(-1, 4).astype(np.float64) / k


def _vertical_vp(segs, w, h):
    """Точка схода вертикалей (однородные координаты в нормированной системе) + уверенность."""
    if len(segs) == 0:
        return None, 0
    dx, dy = segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1]
    length = np.hypot(dx, dy)
    ang = np.degrees(np.arctan2(np.abs(dx), np.abs(dy)))          # 0 = строго вертикаль
    sel = (ang < 20) & (length > 0.12 * h)
    s, L = segs[sel], length[sel]
    if len(s) < 4 or L.sum() < 0.9 * h:
        return None, 0
    c, f = np.array([w / 2.0, h / 2.0]), float(max(w, h))
    p1 = np.c_[(s[:, :2] - c) / f, np.ones(len(s))]
    p2 = np.c_[(s[:, 2:] - c) / f, np.ones(len(s))]
    lines = np.cross(p1, p2)
    lines /= np.linalg.norm(lines[:, :2], axis=1, keepdims=True)
    wts = L / L.max()
    keep = np.ones(len(lines), bool)
    v = None
    for _ in range(4):
        A = lines[keep] * np.sqrt(wts[keep])[:, None]
        _, _, vt = np.linalg.svd(A)
        v = vt[-1]
        # угол между отрезком и направлением на точку схода
        mid = (p1[:, :2] + p2[:, :2]) / 2
        if abs(v[2]) > 1e-9:
            d = v[:2] / v[2] - mid
        else:
            d = np.tile(v[:2], (len(mid), 1))
        seg_dir = p2[:, :2] - p1[:, :2]
        cosang = np.abs((d * seg_dir).sum(1)) / (np.linalg.norm(d, axis=1) * np.linalg.norm(seg_dir, axis=1) + 1e-12)
        err = np.degrees(np.arccos(np.clip(cosang, -1, 1)))
        new_keep = err < 1.5
        if new_keep.sum() < 4:
            return None, 0
        if (new_keep == keep).all():
            break
        keep = new_keep
    support = (L[keep]).sum() / max(L.sum(), 1e-9)
    if keep.sum() < 4 or support < 0.5 or L[keep].sum() < 0.9 * h:
        return None, 0
    return v, support


def _inner_crop(quad, aspect):
    """Самый большой прямоугольник заданного соотношения сторон внутри четырёхугольника."""
    poly = quad.astype(np.float32).reshape(-1, 1, 2)
    cx, cy = quad.mean(0)
    best = None
    for dx in (0.0, -0.03, 0.03):
        for dy in (0.0, -0.03, 0.03):
            span = quad.max(0) - quad.min(0)
            ccx, ccy = cx + dx * span[0], cy + dy * span[1]
            lo, hi = 0.0, float(span[0])
            for _ in range(30):
                mid = (lo + hi) / 2
                ww, hh = mid, mid / aspect
                pts = [(ccx - ww / 2, ccy - hh / 2), (ccx + ww / 2, ccy - hh / 2),
                       (ccx + ww / 2, ccy + hh / 2), (ccx - ww / 2, ccy + hh / 2)]
                if all(cv2.pointPolygonTest(poly, (float(x), float(y)), False) >= 0 for x, y in pts):
                    lo = mid
                else:
                    hi = mid
            if best is None or lo > best[0]:
                best = (lo, ccx, ccy)
    ww = best[0]
    hh = ww / aspect
    return best[1] - ww / 2, best[2] - hh / 2, ww, hh


def _vertical_vp_ransac(segs, w, h, iters=600, tol=1.6, seed=7):
    """Точка схода вертикалей через RANSAC по парам отрезков. -> (v, support) или (None, 0)."""
    if len(segs) == 0:
        return None, 0
    dx, dy = segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1]
    length = np.hypot(dx, dy)
    ang = np.degrees(np.arctan2(np.abs(dx), np.abs(dy)))
    sel = (ang < 25) & (length > 0.08 * h)
    s, L = segs[sel], length[sel]
    if len(s) < 4 or L.sum() < 0.8 * h:
        return None, 0
    c, f = np.array([w / 2.0, h / 2.0]), float(max(w, h))
    p1 = np.c_[(s[:, :2] - c) / f, np.ones(len(s))]
    p2 = np.c_[(s[:, 2:] - c) / f, np.ones(len(s))]
    lines = np.cross(p1, p2)
    lines /= np.linalg.norm(lines[:, :2], axis=1, keepdims=True)
    mid = (p1[:, :2] + p2[:, :2]) / 2
    seg_dir = p2[:, :2] - p1[:, :2]
    seg_dir /= np.linalg.norm(seg_dir, axis=1, keepdims=True)

    def errs(v):
        if abs(v[2]) > 1e-9:
            d = v[:2] / v[2] - mid
        else:
            d = np.tile(v[:2], (len(mid), 1))
        d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-12
        return np.degrees(np.arccos(np.clip(np.abs((d * seg_dir).sum(1)), -1, 1)))

    rng = np.random.default_rng(seed)
    wts = L / L.sum()
    best, best_score = None, 0
    # кандидат «вертикали уже параллельны»
    cands = [np.array([0.0, 1.0, 0.0])]
    for _ in range(iters):
        i, j = rng.choice(len(s), 2, replace=False, p=wts)
        v = np.cross(lines[i], lines[j])
        if np.linalg.norm(v) < 1e-12:
            continue
        cands.append(v / np.linalg.norm(v))
    for v in cands:
        if v[1] < 0:
            v = -v
        # точка схода должна быть «снизу или сверху», не сбоку
        if abs(math.degrees(math.atan2(v[0], v[1]))) > 12:
            continue
        sc = L[errs(v) < tol].sum()
        if sc > best_score:
            best, best_score = v, sc
    if best is None:
        return None, 0
    keep = errs(best) < tol
    for _ in range(3):
        A = lines[keep] * np.sqrt(L[keep] / L.max())[:, None]
        _, _, vt = np.linalg.svd(A)
        v = vt[-1]
        v = v if v[1] >= 0 else -v
        nk = errs(v) < tol
        if nk.sum() < 4:
            break
        best, keep = v, nk
    support = L[keep].sum() / L.sum()
    if keep.sum() < 4 or support < 0.35 or L[keep].sum() < 0.8 * h:
        return None, 0
    return best, support


MAX_ROT = 10.0
MAX_K = 1.15
MIN_KEEP = 0.9        # отрезаем по краям не больше 10% — иначе фото «приближается» и мылится
MAX_STRETCH = 1.12    # низ кадра не должен растягиваться относительно верха больше чем на 12%


def straighten(img, verbose=False):
    """Бережное выпрямление: наклон убираем, вертикали сводим настолько, насколько можно
    без заметной обрезки и без «растянутой» мебели. Пикселей не увеличиваем больше чем на ~5%."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    segs = _segments(gray)
    v, conf = _vertical_vp_ransac(segs, w, h)
    if v is None:                                   # запасной способ — прежний
        v, conf = _vertical_vp(segs, w, h)
        if v is not None and v[1] < 0:
            v = -v
    if v is None:
        return img, "пропуск"
    vx, vy, vw = v
    theta = math.atan2(vx, vy)
    if abs(math.degrees(theta)) > MAX_ROT:
        return img, "пропуск (угол)"
    dist = math.hypot(vx, vy)
    inv_d = vw / dist if dist > 1e-12 else 0.0
    c, f = np.array([w / 2.0, h / 2.0]), float(max(w, h))
    N = np.array([[1 / f, 0, -c[0] / f], [0, 1 / f, -c[1] / f], [0, 0, 1]])
    corners = np.array([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]], float)
    k_full = max(-MAX_K, min(MAX_K, inv_d))
    # сначала пробуем полный наклон + сколько получится вертикалей, потом уменьшаем всё
    plans = [(1.0, s) for s in (1.0, 0.8, 0.65, 0.5, 0.4, 0.3, 0.2, 0.12, 0.0)]
    plans += [(r, 0.0) for r in (0.75, 0.5, 0.3)]
    for rs, ks in plans:
        k = k_full * ks
        rot = theta * rs
        if abs(k) < 0.01 and abs(math.degrees(rot)) < 0.15:
            return img, "ровно"
        cr, sr = math.cos(rot), math.sin(rot)
        R = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
        K = np.array([[1, 0, 0], [0, 1, 0], [0, -k, 1]])
        Hn = K @ R
        qq = Hn @ N @ corners.T
        if qq[2].min() <= 0:
            continue
        qq = (qq[:2] / qq[2]).T
        if not np.isfinite(qq).all():
            continue
        x0, y0, cw, ch = _inner_crop(qq, w / h)
        S = np.array([[w / cw, 0, -x0 * w / cw], [0, h / ch, -y0 * h / ch], [0, 0, 1]])
        H = S @ Hn @ N
        pre = np.linalg.inv(H) @ corners.T
        pre = (pre[:2] / pre[2]).T.astype(np.float32)
        keep = cv2.contourArea(pre) / (w * h)
        # насколько низ увеличен относительно верха (вертикальное растяжение мебели)
        ys = [y0, y0 + ch]
        den = [1.0 + k * y / (1.0 - 0) for y in ys]          # знаменатель после K в координатах результата
        stretch = max(den) / max(min(den), 1e-6)
        if keep >= MIN_KEEP and stretch <= MAX_STRETCH:
            out = cv2.warpPerspective(img, H, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
            how = (f"поворот {math.degrees(rot):+.1f}° из {math.degrees(theta):+.1f}°, вертикали {k:+.2f} из {inv_d:+.2f}, "
                   f"в кадре {keep:.0%}, растяжение {stretch:.2f}")
            return out, how if verbose else "ok"
    return img, "пропуск (без потерь нельзя)"


# =================================================================== чёткость
class SuperRes:
    """Real-ESRGAN realesr-general-x4v3 (SRVGGNetCompact), ~5 МБ, работает на процессоре."""

    def __init__(self, path):
        import torch
        import torch.nn as nn
        self.torch = torch
        sd = torch.load(path, map_location="cpu")
        sd = sd.get("params_ema", sd.get("params", sd))
        n_conv = (max(int(k.split(".")[1]) for k in sd) - 2) // 2

        class Net(nn.Module):
            def __init__(self):
                super().__init__()
                body = [nn.Conv2d(3, 64, 3, 1, 1), nn.PReLU(64)]
                for _ in range(n_conv):
                    body += [nn.Conv2d(64, 64, 3, 1, 1), nn.PReLU(64)]
                body += [nn.Conv2d(64, 3 * 16, 3, 1, 1)]
                self.body = nn.ModuleList(body)
                self.up = nn.PixelShuffle(4)

            def forward(self, x):
                out = x
                for m in self.body:
                    out = m(out)
                out = self.up(out)
                return out + nn.functional.interpolate(x, scale_factor=4, mode="nearest")

        self.net = Net()
        self.net.load_state_dict(sd, strict=True)
        self.net.eval()
        self.device = "cpu"
        try:   # на Mac с процессором Apple считаем на видеочипе — в разы быстрее
            if torch.backends.mps.is_available():
                self.net.to("mps")
                self.net(torch.zeros(1, 3, 16, 16, device="mps"))
                self.device = "mps"
        except Exception:
            self.net.to("cpu")
            self.device = "cpu"

    def run(self, img, tile=256, pad=12):
        torch = self.torch
        h, w = img.shape[:2]
        x = torch.from_numpy(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).permute(2, 0, 1).float()[None] / 255
        out = torch.zeros(1, 3, h * 4, w * 4)
        with torch.no_grad():
            for y0 in range(0, h, tile):
                for x0 in range(0, w, tile):
                    ya, xa = max(0, y0 - pad), max(0, x0 - pad)
                    yb, xb = min(h, y0 + tile + pad), min(w, x0 + tile + pad)
                    try:
                        o = self.net(x[:, :, ya:yb, xa:xb].to(self.device)).float().cpu()
                    except Exception:
                        self.net.to("cpu"); self.device = "cpu"
                        o = self.net(x[:, :, ya:yb, xa:xb])
                    ty, tx = (y0 - ya) * 4, (x0 - xa) * 4
                    th, tw = (min(h, y0 + tile) - y0) * 4, (min(w, x0 + tile) - x0) * 4
                    out[:, :, y0 * 4:y0 * 4 + th, x0 * 4:x0 * 4 + tw] = o[:, :, ty:ty + th, tx:tx + tw]
        res = (out[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)
        return cv2.cvtColor(res, cv2.COLOR_RGB2BGR)


def sharpen(img, amount=0.55, radius=1.1, threshold=3):
    """Резкость только по яркости, с порогом — шум и плоские стены не трогает."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    L = lab[..., 0].astype(np.float32)
    blur = cv2.GaussianBlur(L, (0, 0), radius)
    detail = L - blur
    mask = np.clip((np.abs(detail) - threshold) / threshold, 0, 1)
    lab[..., 0] = np.clip(L + amount * detail * mask, 0, 255).astype(np.uint8)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def upscale_to(img, target, sr=None):
    """Довести длинную сторону до target. Маленькие фото — нейросетью, остальные — Lanczos."""
    h, w = img.shape[:2]
    used = False
    if sr is not None and max(h, w) < SR_LIMIT:
        try:
            up = sr.run(img)
            used = True
        except Exception:
            up = img
    else:
        up = img
    k = target / max(up.shape[:2])
    size = (round(up.shape[1] * k), round(up.shape[0] * k))
    interp = cv2.INTER_AREA if k < 1 else cv2.INTER_LANCZOS4
    out = cv2.resize(up, size, interpolation=interp)
    if used:   # чуть смешиваем с обычным увеличением — убирает «нарисованность»
        base = cv2.resize(img, size, interpolation=cv2.INTER_LANCZOS4)
        out = cv2.addWeighted(out, 0.85, base, 0.15, 0)
    return out, used


SR_LIMIT = 1500   # фото меньше этого по длинной стороне увеличиваем нейросетью
