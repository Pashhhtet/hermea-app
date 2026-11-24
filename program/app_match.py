"""Подбор квартир под клиента: запрос из карточки (бюджет, районы, комнаты, площадь) сверяется
со всеми объявлениями, которые программа и так собирает: собственники Otodom и OLX, свежие
объявления всех районов (снимок «Рынка») и «Слежу за поиском».

Районы и комнаты понимаются из свободного текста на русском, украинском и польском:
«Мокотув, Вола», «центр», «2-3 комнаты», «kawalerka». Совместимо с Python 3.9.
"""
import datetime as dt
import re
import unicodedata

# основа названия района (без диакритики, нижний регистр) -> район
ALIASES = {
    "bemowo": [r"bemow", r"бемов"],
    "bialoleka": [r"bialolek", r"бялол[еёо]к", r"бiлол[еє]к", r"бялолєк", r"tarchomin", r"тархомин"],
    "bielany": [r"bielan", r"бел[яа]н", r"бял[яа]н", r"б[іє]лян"],
    "mokotow": [r"mokot", r"мокот"],
    "ochota": [r"ochot", r"охот"],
    "praga-polnoc": [r"praga[\s-]*poln", r"прага[\s-]*(п[уо]лн|север|півн)", r"stara\s+praga"],
    "praga-poludnie": [r"praga[\s-]*polud", r"прага[\s-]*(п[оу]луд|южн|півд)", r"saska\s+kep", r"саск", r"gocław|goclaw", r"гоцлав"],
    "rembertow": [r"rembert", r"рембер"],
    "srodmiescie": [r"srodmiesc", r"centrum", r"центр", r"[сш]р[оу]дм[еєія]", r"muran[oó]w", r"муранов"],
    "targowek": [r"targow", r"таргув", r"таргов"],
    "ursus": [r"ursus", r"урсус"],
    "ursynow": [r"ursyn", r"урс[иы]н", r"урсін", r"kabat", r"кабат"],
    "wawer": [r"wawer", r"вавер"],
    "wesola": [r"wesol", r"вес[оe]л"],
    "wilanow": [r"wilan", r"вил[яа]н", r"вілян"],
    "wlochy": [r"wloch", r"влох"],
    "wola": [r"\bwola\b", r"\bwoli\b", r"\bвол[аяюиеу]\b", r"\bволі\b"],
    "zoliborz": [r"zolib", r"ж[оу]либ"],
}
PRAGA = r"\bpraga\b|\bпраг[аиуе]\b"           # просто «Прага» — обе Праги
WORD_ROOMS = [
    (r"kawalerk|студи|studio|однок[оі]м|одноком|1[\s-]*(к|ком|кім|pok)|однуш", {"1"}),
    (r"двух|двух?к[оі]м|двок[іо]м|dwupok|dwa\s+pok|2[\s-]*(к|ком|кім|pok)|двушк", {"2"}),
    (r"тр[её]х|тр[ьи]ох|trzypok|trzy\s+pok|3[\s-]*(к|ком|кім|pok)|трешк|трёшк", {"3"}),
    (r"четыр|чотир|czterop|4[\s-]*(к|ком|кім|pok)", {"4"}),
]


def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").replace("ł", "l").replace("Ł", "L"))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def districts_of(text):
    t = norm(text)
    out = {d for d, pats in ALIASES.items() if any(re.search(p, t) for p in pats)}
    if re.search(PRAGA, t) and not out & {"praga-polnoc", "praga-poludnie"}:
        out |= {"praga-polnoc", "praga-poludnie"}
    return out


def rooms_of(text):
    t = norm(text)
    if not t.strip():
        return set()
    out = set()
    m = re.search(r"\b([1-5])\s*[-–/]\s*([1-5])\b", t)          # «2-3»
    if m:
        a, b = sorted((int(m.group(1)), int(m.group(2))))
        out |= {str(k) for k in range(a, b + 1)}
    m = re.search(r"\b([1-4])\s*\+", t)                       # «2+»
    if m:
        out |= {str(k) for k in range(int(m.group(1)), 5)}
    for pat, val in WORD_ROOMS:
        if re.search(pat, t):
            out |= val
    if not out:
        m = re.fullmatch(r"\s*([1-5])\s*", t)                  # просто «2»
        if m:
            out.add(m.group(1))
    return out


def _int(v):
    try:
        n = int(re.sub(r"[^\d]", "", str(v or "")) or 0)
        return n or None
    except Exception:
        return None


def criteria(c):
    """Что понимаем из карточки клиента."""
    budget = _int(c.get("budget"))
    if budget and budget < 500:
        budget = None
    area = _int(c.get("area"))
    if area and area > 400:
        area = None
    text_rooms = " ".join(str(c.get(k) or "") for k in ("type",))
    return {
        "budget": budget, "area": area,
        "rooms": sorted(rooms_of(text_rooms)),
        "districts": sorted(districts_of(" ".join(str(c.get(k) or "") for k in ("location", "must")))),
        "parking": c.get("parking") == "yes",
        "pets": bool(re.search(r"[a-zа-яіїє]", norm(c.get("pets"))) and not re.fullmatch(
            r"\s*(нет|ні|nie|no|-|без|brak)\s*", norm(c.get("pets")))),
    }


def _slug(name):
    s = norm(name).strip()
    return "-".join(s.replace("–", "-").split()).replace("--", "-")


def _days(s):
    try:
        return (dt.date.today() - dt.date.fromisoformat(str(s)[:10])).days
    except Exception:
        return None


def _fp(i):
    return (_slug(i.get("district")), str(i.get("rooms") or ""), round(float(i.get("area") or 0)),
            int(i.get("total") or i.get("price") or 0) // 50)


def match(c, pools, limit=15):
    """pools: [(объявления, источник)], источник: owner | olx | market | search.
    -> {"criteria", "items", "total", "empty": причина или ""}"""
    cr = criteria(c)
    if not cr["budget"] and not cr["districts"] and not cr["rooms"]:
        return {"criteria": cr, "items": [], "total": 0, "empty": "need"}
    viewed = {str(v.get("link") or "").split("?")[0] for v in c.get("viewed") or [] if v.get("link")}
    skip = set(c.get("match_skip") or [])
    seen = set(c.get("match_seen") or [])
    best, prints = {}, {}
    for items, src in pools:
        for i in items:
            url = str(i.get("url") or "").split("?")[0]
            iid = str(i.get("id") or url)
            if not url or url in viewed or iid in skip or i.get("status") in ("refused", "hidden", "nocall"):
                continue
            tot = i.get("total") or i.get("price")
            if not tot:
                continue
            b = cr["budget"]
            if b and not (b * 0.55 <= tot <= b * 1.07):
                continue
            if cr["rooms"] and str(i.get("rooms") or "") not in cr["rooms"]:
                continue
            if cr["districts"] and _slug(i.get("district")) not in cr["districts"]:
                continue
            if cr["area"] and (i.get("area") or 0) < cr["area"] * 0.95:
                continue
            pts, why = 0.0, []
            age = _days(i.get("created"))
            if age is not None and age <= 2:
                pts += 3; why.append("fresh")
            elif age is not None and age <= 7:
                pts += 1.5
            private = src in ("owner", "olx") or i.get("owner")
            if private:
                pts += 2; why.append("owner")
            if i.get("status") == "agreed":
                pts += 5; why.append("agreed")
            if b:
                pts += max(0.0, 2 - abs(b * 0.92 - tot) / b * 6)
            tags = set(i.get("tags") or [])
            if cr["parking"] and "parking" in tags:
                pts += 1; why.append("parking")
            if cr["pets"] and "pets" in tags:
                pts += 1; why.append("pets")
            out = {k: i.get(k) for k in ("title", "url", "img", "price", "rent", "area", "rooms", "district",
                                         "street", "created", "agency")}
            out.update(id=iid, total=tot, src="olx" if (src == "olx" or str(iid).startswith("olx-")) else src,
                       private=bool(private), agreed=i.get("status") == "agreed", why=why, pts=round(pts, 2),
                       new=iid not in seen, days=age)
            fp = _fp(i)
            prev = prints.get(fp)
            if prev is not None:                 # та же квартира в другом источнике: оставляем лучшую версию
                if best[prev]["pts"] >= out["pts"]:
                    continue
                best.pop(prev, None)
            if iid in best and best[iid]["pts"] >= out["pts"]:
                continue
            best[iid] = out
            prints[fp] = iid
    items = sorted(best.values(), key=lambda x: (-x["pts"], x["total"]))
    return {"criteria": cr, "items": items[:limit], "total": len(items), "empty": "" if items else "none"}
