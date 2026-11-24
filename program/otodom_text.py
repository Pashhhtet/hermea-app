"""Длинное объявление на польском для Otodom/OLX — для квартир «без комиссии».

Текст собирается из фактов объявления (комнаты, метраж, этаж, оснащение, цены). Формулировки
чередуются от квартиры к квартире, чтобы объявления не были одинаковыми и не повторяли текст
собственника. Ничего не придумываем: чего нет в данных — того нет и в тексте.
"""
import datetime as dt
import hashlib
import re

ROOMS = {"1": "kawalerka", "2": "2-pokojowe mieszkanie", "3": "3-pokojowe mieszkanie",
         "4": "4-pokojowe mieszkanie", "5": "5-pokojowe mieszkanie"}
ROOMS_SHORT = {"1": "Kawalerka", "2": "2 pokoje", "3": "3 pokoje", "4": "4 pokoje", "5": "5 pokoi"}


def _pick(seed, options, k=0):
    h = int(hashlib.md5(f"{seed}:{k}".encode()).hexdigest(), 16)
    return options[h % len(options)]


def _zl(v):
    return f"{int(v):,}".replace(",", " ") + " zł"


def _floor(f, n):
    if not f:
        return ""
    if f in ("ground_floor", "floor_0"):
        return "na parterze"
    m = re.search(r"(\d+)", str(f))
    if not m:
        return ""
    s = f"na {m.group(1)}. piętrze"
    if n and str(n).isdigit():
        s += f" (z {n})" if str(n) != m.group(1) else " (ostatnim)"
    return s


def _area(a):
    try:
        x = float(str(a).replace(",", "."))
        return (f"{x:.0f}" if x == int(x) else f"{x:.1f}".replace(".", ",")) + " m²"
    except Exception:
        return ""


def title(i):
    r = ROOMS_SHORT.get(str(i.get("rooms") or ""), "Mieszkanie")
    f = set(i.get("flags") or [])
    extra = "z balkonem" if "balcony" in f else "z tarasem" if "terrace" in f else "z ogródkiem" if "garden" in f \
        else "z garażem" if "garage" in f else "z klimatyzacją" if "air_conditioning" in f else ""
    place = i.get("sub") or i.get("district") or i.get("city") or ""
    parts = [r, _area(i.get("area")), extra]
    t = " ".join(p for p in parts if p)
    if place:
        t += f", {place}"
    full = f"{t}, bez prowizji"
    if len(full) > 70:
        full = f"{r} {_area(i.get('area'))}, {place}, bez prowizji".strip()
    return full[:70]


def build(i, today=None):
    today = today or dt.date.today().isoformat()
    seed = i.get("id") or i.get("title") or "x"
    f = set(i.get("flags") or [])
    eq = set(i.get("equipment") or [])
    rooms = str(i.get("rooms") or "")
    kind = ROOMS.get(rooms, "mieszkanie")
    area = _area(i.get("area"))
    district, sub, street = i.get("district") or "", i.get("sub") or "", i.get("street") or ""
    where = district + (f" ({sub})" if sub and sub != district else "")
    desc = (i.get("desc") or "").lower()

    adj = _pick(seed, ["przytulne", "zadbane", "jasne", "funkcjonalne", "komfortowe"])
    if rooms == "1":
        adj = {"przytulne": "przytulna", "zadbane": "zadbana", "jasne": "jasna",
               "funkcjonalne": "funkcjonalna", "komfortowe": "komfortowa"}[adj]
    lead = _pick(seed, ["Do wynajęcia", "Oferujemy do wynajęcia", "Na wynajem czeka"], 1)
    s1 = f"{lead} {adj} {kind}" + (f" o powierzchni {area}" if area else "")
    if where:
        s1 += f" w dzielnicy {where}"
    if street:
        s1 += f", przy {street if street.lower().startswith(('ul.', 'al.', 'pl.')) else 'ul. ' + street}"
    s1 += "."
    fl = _floor(i.get("floor"), i.get("floors"))
    by = str(i.get("build_year") or "")
    by = by if by.isdigit() and int(by) >= 1990 else ""
    lift = "lift" in f
    if fl:
        s2 = f"Mieszkanie znajduje się {fl}" + (f" w budynku z {by} roku" if by else "") + (" z windą" if lift else "") + "."
    elif by:
        s2 = f"Budynek z {by} roku" + (", z windą" if lift else "") + "."
    else:
        s2 = "W budynku jest winda." if lift else ""
    if "security" in f:
        s2 += (" " if s2 else "") + _pick(seed, ["Osiedle jest zamknięte i monitorowane.",
                                                  "Budynek jest monitorowany, a teren zamknięty."], 2)

    items = []
    if "furniture" in f:
        items.append("pełne umeblowanie")
    kit = [n for k, n in [("stove", "kuchenka"), ("oven", "piekarnik"), ("fridge", "lodówka"),
                          ("dishwasher", "zmywarka")] if k in eq or (k == "dishwasher" and "dishwasher" in f)]
    if kit:
        items.append("kuchnia wyposażona: " + ", ".join(kit))
    if "washing_machine" in f:
        items.append("pralka")
    if "tv" in eq:
        items.append("telewizor")
    if "air_conditioning" in f:
        items.append(_pick(seed, ["klimatyzacja, która daje komfort w upalne dni", "klimatyzacja"], 3))
    if "balcony" in f:
        items.append("balkon")
    if "terrace" in f:
        items.append("taras")
    if "garden" in f:
        items.append("ogródek")
    if "garage" in f:
        items.append("miejsce parkingowe w garażu")
    if {"internet", "cable-television"} & eq or "internet" in desc:
        items.append("internet")

    near = []
    if "metro" in desc:
        near.append("stacja metra")
    if re.search(r"tramwaj|autobus|przystan|komunikacj", desc):
        near.append("przystanki komunikacji miejskiej")
    if re.search(r"\bpark|las\b|lasu|zieleń|zielon", desc):
        near.append("tereny zielone")
    if re.search(r"sklep|biedronk|lidl|żabk|galeri|centrum handlow", desc):
        near.append("sklepy")
    if re.search(r"szkoł|przedszkol", desc):
        near.append("szkoły i przedszkola")
    loc = ""
    if near:
        loc = _pick(seed, ["W pobliżu: ", "W okolicy znajdziesz: ", "Blisko: "], 4) + ", ".join(near) + "."

    cond = []
    if i.get("price"):
        c = f"najem: {_zl(i['price'])}"
        if i.get("rent"):
            c += f" + czynsz administracyjny {_zl(i['rent'])}"
        cond.append(c)
    if i.get("deposit"):
        cond.append(f"kaucja: {_zl(i['deposit'])}")
    ff = i.get("free_from") or ""
    cond.append(f"dostępne od {dt.date.fromisoformat(ff).strftime('%d.%m.%Y')}" if ff and ff > today else "dostępne od zaraz")
    if "pets" in f:
        cond.append("zwierzęta akceptowane")
    cond.append("dla najemcy bez prowizji, wynagrodzenie agencji pokrywa właściciel")

    out = [title(i), "", s1]
    if s2:
        out.append(s2)
    if items:
        out += ["", _pick(seed, ["W mieszkaniu:", "Co oferuje mieszkanie:", "Wyposażenie i udogodnienia:"], 5)]
        out += [f"• {x}" for x in items]
    if loc:
        out += ["", loc]
    out += ["", "Warunki:"] + [f"• {x}" for x in cond]
    out += ["", _pick(seed, ["Zapraszam na prezentację! Chętnie odpowiem na pytania i umówię dogodny termin.",
                             "Zapraszam na oglądanie, termin dopasuję do Państwa.",
                             "Chętnie pokażę mieszkanie, zapraszam do kontaktu!"], 6)]
    return "\n".join(out) + "\n"
