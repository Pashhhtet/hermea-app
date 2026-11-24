"""Модули сайтов для HERMEA.

get_listing(sess, url) -> dict с единым набором полей:
    site, id, title, rooms, area, district, sub, city, street,
    price, rent, deposit, build_year, flags (set), images [{url, plan}],
    watermark ("otodom" или None)
Совместимо с Python 3.9.
"""
import base64, html as htmlmod, json, re
from collections import OrderedDict
from urllib.parse import urlparse


# ----------------------------------------------------------------- helpers
def num(v):
    """'2 900 zł' -> 2900, '13500.00' -> 13500, None -> None"""
    if v is None or v == "" or v == []:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).replace("\xa0", " ")
    m = re.search(r"\d[\d \.]*(?:,\d+)?", s)
    if not m:
        return None
    s = m.group(0).replace(" ", "")
    if "," in s:
        s = s.split(",")[0]
    if s.count(".") == 1 and len(s.split(".")[1]) <= 2:
        s = s.split(".")[0]
    s = s.replace(".", "")
    return int(s) if s.isdigit() else None


def area_str(v):
    """'41,59 m²' -> '41.59', '58' -> '58'"""
    if v in (None, ""):
        return ""
    m = re.search(r"\d+(?:[.,]\d+)?", str(v))
    if not m:
        return ""
    s = m.group(0).replace(",", ".")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def rooms_str(v):
    if v in (None, ""):
        return ""
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "jeden": 1, "jedno": 1, "dwa": 2, "dwu": 2, "trzy": 3, "cztery": 4, "pięć": 5}
    s = str(v).lower()
    m = re.search(r"\d+", s)
    if m:
        return m.group(0)
    for k, n in words.items():
        if k in s:
            return str(n)
    return ""


def page_text(html):
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", "", html, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</dt>|</dd>|</td>|</th>|</span>|</h\d>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t).replace("\xa0", " ")
    return [re.sub(r"\s+", " ", l).strip() for l in t.split("\n") if l.strip()]


def label_value(lines, *labels):
    """Ищет 'Метка: значение' или метку и значение на следующей строке."""
    for i, l in enumerate(lines):
        low = l.lower()
        for lab in labels:
            if low.startswith(lab.lower()):
                rest = l[len(lab):].strip(" :")
                if rest:
                    return rest
                if i + 1 < len(lines):
                    return lines[i + 1]
    return None


def section(lines, start, ends):
    """Строки между первой, содержащей start, и первой после неё, содержащей что-то из ends."""
    a = next((n for n, l in enumerate(lines) if start in l), None)
    if a is None:
        return lines
    for n in range(a + 1, len(lines)):
        if any(e in lines[n] for e in ends):
            return lines[a:n]
    return lines[a:]


def rent_from_text(text):
    m = re.search(r"czynsz\w*\s+(?:administracyjn\w*|adm\.?|do wspólnoty|dla wspólnoty)[^\d]{0,25}(\d[\d \.]*)\s*(zł|pln)", text, re.I) \
        or re.search(r"(\d[\d \.]*)\s*(zł|pln)\s*(?:\+\s*)?czynsz\w*\s+adm", text, re.I) \
        or re.search(r"opłat\w*\s+administracyjn\w*[^\d]{0,25}(\d[\d \.]*)\s*(zł|pln)", text, re.I)
    return num(m.group(1)) if m else None


def deposit_from_text(text):
    m = re.search(r"kaucj\w*[^\d]{0,25}(\d[\d \.]*)\s*(zł|pln)", text, re.I)
    return num(m.group(1)) if m else None


FLAG_WORDS = [
    ("balcony", ["balkon", "loggia", "logia"]),
    ("terrace", ["taras"]),
    ("garden", ["ogród", "ogródek", "ogrodek"]),
    ("garage", ["garaż", "garaz", "miejsce postojowe", "miejsce parkingowe", "parking podziemny"]),
    ("lift", ["winda", "windą"]),
    ("furniture", ["umeblowane", "umeblowanie", "meble", "umeblowana"]),
    ("dishwasher", ["zmywark"]),
    ("washing_machine", ["pralk"]),
    ("air_conditioning", ["klimatyzac"]),
    ("security", ["ochrona", "monitoring", "teren zamknięty", "obiekt zamknięty", "osiedle zamknięte", "recepcja", "concierge"]),
    ("pets", ["zwierzęta mile", "zwierzęta akceptowane", "zgoda na zwierz", "przyjazne zwierzętom"]),
]


def flags_from_text(text):
    low = text.lower()
    out = set()
    for flag, words in FLAG_WORDS:
        if any(w in low for w in words):
            out.add(flag)
    # «zwierzęta: nie» — не считаем
    if re.search(r"zwierz\w*\s*[:\-]?\s*nie\b", low):
        out.discard("pets")
    return out


def base_info(site, url):
    return {"site": site, "id": re.sub(r"\W+", "", url.rstrip("/").split("/")[-1])[-24:] or site,
            "title": "", "rooms": "", "area": "", "district": "", "sub": "", "city": "Warszawa",
            "street": "", "price": None, "rent": None, "deposit": None, "build_year": None,
            "flags": set(), "images": [], "watermark": None}


def uniq(seq):
    return list(OrderedDict.fromkeys(x for x in seq if x))


def ld_json(html):
    out = []
    for raw in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            out.append(json.loads(raw))
        except Exception:
            pass
    return out


# ----------------------------------------------------------------- Otodom
def parse_otodom(html, url):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("не нашёл данные объявления (Otodom мог показать капчу)")
    ad = json.loads(m.group(1))["props"]["pageProps"]["ad"]
    t = ad.get("target") or {}
    ch = {c.get("key"): c.get("value") for c in ad.get("characteristics") or []}
    locs = ((ad.get("location") or {}).get("reverseGeocoding") or {}).get("locations") or []
    by = {l.get("locationLevel"): l.get("name") for l in locs}
    i = base_info("otodom", url)
    ex = set(t.get("Extras_types") or []); eq = set(t.get("Equipment_types") or [])
    sec = set(t.get("Security_types") or [])
    flags = set()
    for k in ("balcony", "terrace", "garden", "garage", "lift"):
        if k in ex: flags.add(k)
    for k in ("furniture", "dishwasher", "washing_machine", "air_conditioning"):
        if k in eq or k in ex: flags.add(k)
    if sec & {"closed_area", "monitoring", "security"}: flags.add("security")
    i.update({
        "id": str(t.get("Id") or ad.get("id")),
        "title": ad.get("title") or "",
        "rooms": rooms_str((t.get("Rooms_num") or [ch.get("rooms_num")])[0]),
        "area": area_str(t.get("Area") or ch.get("m")),
        "district": by.get("district") or "",
        "sub": by.get("residential") or "",
        "city": by.get("city_or_village") or "Warszawa",
        "street": (((ad.get("location") or {}).get("address") or {}).get("street") or {}).get("name") or "",
        "price": num(t.get("Price") or ch.get("price")),
        "rent": num(t.get("Rent") or ch.get("rent")),
        "deposit": num(t.get("Deposit") or ch.get("deposit")),
        "build_year": t.get("Build_year"),
        "flags": flags,
        "images": [{"url": u, "plan": bool(im.get("isFloorPlan")), "room": im.get("roomType")}
                   for im in ad.get("images") or [] for u in [_img_url(im)] if u],
        "watermark": "otodom",
    })
    return i


def _img_url(im):
    """Otodom иногда не отдаёт размер 'large' — берём лучший из доступных."""
    if isinstance(im, str):
        return im
    for k in ("large", "original", "big", "medium", "url", "small", "thumbnail"):
        v = im.get(k)
        if isinstance(v, str) and v.startswith("http"):
            return v
    for v in im.values():
        if isinstance(v, str) and v.startswith("http"):
            return v
    return None


# ----------------------------------------------------------------- OLX
def parse_olx(html, url):
    m = re.search(r'window\.__PRERENDERED_STATE__\s*=\s*("(?:[^"\\]|\\.)*")', html)
    if not m:
        raise RuntimeError("не нашёл данные объявления OLX")
    ad = json.loads(json.loads(m.group(1)))["ad"]["ad"]
    p = {x.get("key"): x for x in ad.get("params") or []}
    pv = lambda k: (p.get(k) or {}).get("value")
    pn = lambda k: (p.get(k) or {}).get("normalizedValue")
    loc = ad.get("location") or {}
    i = base_info("olx", url)
    flags = flags_from_text((ad.get("title") or "") + " " + re.sub("<[^>]+>", " ", ad.get("description") or ""))
    if str(pn("winda")).lower() in ("tak", "yes"): flags.add("lift")
    if str(pn("furniture")).lower() in ("yes", "tak"): flags.add("furniture")
    park = pn("parking")
    if park and any("garaz" in str(x) or "podziemny" in str(x) for x in (park if isinstance(park, list) else [park])):
        flags.add("garage")
    if str(pn("pets")).lower() in ("tak", "yes"): flags.add("pets")
    else: flags.discard("pets")
    price = ((ad.get("price") or {}).get("regularPrice") or {}).get("value")
    rent = num(pv("rent"))
    i.update({
        "id": str(ad.get("id")),
        "title": ad.get("title") or "",
        "rooms": rooms_str(pv("rooms") or pn("rooms")),
        "area": area_str(pv("m") or pn("m")),
        "district": loc.get("districtName") or "",
        "city": loc.get("cityName") or "Warszawa",
        "price": num(price),
        "rent": rent if rent and rent > 1 else rent_from_text(re.sub("<[^>]+>", " ", ad.get("description") or "")),
        "deposit": deposit_from_text(re.sub("<[^>]+>", " ", ad.get("description") or "")),
        "flags": flags,
        "images": [{"url": u.replace(":443", ""), "plan": False} for u in ad.get("photos") or []],
    })
    return i


# ----------------------------------------------------------------- Gratka / Morizon (одна платформа)
def nuxt_payload(html):
    m = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    arr = json.loads(m.group(1))
    cache = {}
    wrappers = ("Reactive", "ShallowReactive", "Ref", "ShallowRef", "EmptyRef", "Set", "Map", "Date", "NuxtError")

    def res(i, depth=0):
        if not isinstance(i, int) or isinstance(i, bool) or depth > 80 or i < 0 or i >= len(arr):
            return i
        if i in cache:
            return cache[i]
        v = arr[i]
        if isinstance(v, list):
            if v and isinstance(v[0], str) and v[0] in wrappers:
                out = res(v[1], depth + 1) if len(v) > 1 else None
            else:
                out = [res(x, depth + 1) for x in v]
        elif isinstance(v, dict):
            out = {}
            cache[i] = out
            for k, x in v.items():
                out[k] = res(x, depth + 1)
            return out
        else:
            out = v
        cache[i] = out
        return out
    return res(0)


def _b64url(s):
    try:
        return base64.b64decode(s + "=" * (-len(s) % 4)).decode()
    except Exception:
        try:
            return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)).decode()
        except Exception:
            return None


def parse_gratka(html, url, site="gratka"):
    p = nuxt_payload(html)
    d = None
    if p:
        for k, v in (p.get("data") or {}).items():
            if str(k).startswith("property-details") and isinstance(v, dict):
                d = ((v.get("data") or {}).get("propertyData"))
                if d:
                    break
    if not d:
        raise RuntimeError("не нашёл данные объявления " + site)
    info = {x.get("label", "").lower(): x.get("value") for x in
            (d.get("detailedInformation") or []) + (d.get("buildingDetailedInformation") or [])
            if isinstance(x, dict)}
    def lv(*keys):
        for k, v in info.items():
            if any(k.startswith(x) for x in keys):
                return v
        return None
    loc = (d.get("location") or {}).get("location") or []
    labels = " ".join(str(x.get("label", "")) for x in
                      (d.get("equipments") or []) + (d.get("facilities") or []) + (d.get("utilities") or [])
                      if isinstance(x, dict))
    det = " ".join(f"{k}: {v}" for k, v in info.items() if str(v).lower() not in ("nie", "brak"))
    flags = flags_from_text(labels + " " + det + " " + str(d.get("title") or ""))
    imgs = []
    for ph in d.get("photos") or []:
        u = _b64url(ph.get("id", "")) if isinstance(ph, dict) else None
        if u: imgs.append({"url": u, "plan": False})
    for ph in d.get("plans") or []:
        u = _b64url(ph.get("id", "")) if isinstance(ph, dict) else None
        if u: imgs.append({"url": u, "plan": True})
    i = base_info(site, url)
    i.update({
        "id": str(d.get("id") or d.get("idOnFrontend") or i["id"]),
        "title": d.get("title") or "",
        "rooms": rooms_str(d.get("numberOfRoomsCount") or d.get("numberOfRooms")),
        "area": area_str(d.get("area")),
        "city": loc[1] if len(loc) > 1 else "Warszawa",
        "district": loc[2] if len(loc) > 2 else "",
        "sub": loc[3] if len(loc) > 3 else "",
        "street": (d.get("location") or {}).get("street") or "",
        "price": num((d.get("price") or {}).get("amount")),
        "rent": num(lv("czynsz", "opłaty")) or rent_from_text(re.sub("<[^>]+>", " ", str(d.get("description") or ""))),
        "deposit": num(lv("kaucja")) or deposit_from_text(re.sub("<[^>]+>", " ", str(d.get("description") or ""))),
        "build_year": num(lv("rok budowy")),
        "flags": flags,
        "images": imgs,
    })
    return i


# ----------------------------------------------------------------- Lento
def parse_lento(html, url):
    lines = page_text(html)
    i = base_info("lento", url)
    m = re.search(r'id="thumbnails-gallery"(.*?)</div>', html, re.S)
    block = m.group(1) if m else ""
    imgs = re.findall(r'href="(https://st-lento\.pl/adpics/(?:large|original)/[^"]+)"', block)
    if not imgs:   # одно фото без галереи
        mm = re.search(r'<img src="(https://st-lento\.pl/adpics/original/[^"]+)"', html)
        imgs = [mm.group(1)] if mm else []
    imgs = uniq(u.replace("/adpics/large/", "/adpics/original/") for u in imgs)
    title = ""
    for ld in ld_json(html):
        if isinstance(ld, dict) and ld.get("@type") == "RealEstateListing":
            title = ld.get("name") or ""
    desc = title
    for ld in ld_json(html):
        if isinstance(ld, dict) and ld.get("@type") == "RealEstateListing":
            desc += " " + (ld.get("description") or "")
    mid = re.search(r",(\d+)\.html", url)
    i.update({
        "id": mid.group(1) if mid else i["id"],
        "title": title,
        "rooms": rooms_str(label_value(lines, "Liczba pokoi")),
        "area": area_str(label_value(lines, "Powierzchnia")),
        "price": num(label_value(lines, "Cena")),
        "rent": num(label_value(lines, "Czynsz")) or rent_from_text(desc),
        "deposit": num(label_value(lines, "Kaucja")) or deposit_from_text(desc),
        "street": (label_value(lines, "Ulica") or "")[:60],
        "district": (label_value(lines, "Dzielnica") or "")[:40],
        "flags": flags_from_text(desc),
        "images": [{"url": u, "plan": False} for u in imgs],
    })
    return i


# ----------------------------------------------------------------- Tabelaofert
def parse_tabela(html, url):
    lines = page_text(html)
    i = base_info("tabelaofert", url)
    lead = None
    title = ""
    for ld in ld_json(html):
        if isinstance(ld, dict) and ld.get("image") and not lead:
            lead = ld.get("image")
            title = ld.get("name") or ""
    imgs = []
    if lead:
        orig = re.sub(r"/thumb_[^,/]+,", "/", lead)
        prefix = re.sub(r"-\d+\.(webp|jpe?g|png)$", "", orig)
        imgs = uniq(u for u in re.findall(r'https://content\.tabelaofert\.pl/[^"\'\s,)]+?\.(?:webp|jpe?g|png)', html)
                    if u.startswith(prefix))
    if not imgs:
        imgs = uniq(u for u in re.findall(r'https://content\.tabelaofert\.pl/\d+-/[^"\'\s,)]+?\.(?:webp|jpe?g)', html)
                    if "logo" not in u and "thumb_" not in u)
    place = []
    for n, l in enumerate(lines):
        if "oferta nr" in l and n + 1 < len(lines):
            place = [x.strip() for x in lines[n + 1].split(",") if x.strip()]
            break
    body = section(lines, "Najważniejsze informacje", ["Pokaż cały opis", "Treść ogłoszenia nie stanowi"])
    desc = " ".join(body)
    m_price = re.search(r"(\d[\d \xa0]{2,})\s*zł", " ".join(str(ld.get("description", "")) for ld in ld_json(html) if isinstance(ld, dict)))
    mid = re.search(r",(\d+)$", url.rstrip("/"))
    i.update({
        "id": mid.group(1) if mid else i["id"],
        "title": title,
        "rooms": rooms_str(label_value(lines, "Liczba pokoi")),
        "area": area_str(label_value(lines, "Powierzchnia")),
        "price": num(m_price.group(1)) if m_price else num(label_value(lines, "Cena")),
        "rent": rent_from_text(desc),
        "deposit": num(label_value(body, "Kaucja")) or deposit_from_text(desc),
        "city": place[0] if place else "Warszawa",
        "district": place[1] if len(place) > 2 else "",
        "sub": place[2] if len(place) > 3 else "",
        "street": place[-1] if len(place) > 1 else "",
        "flags": flags_from_text(desc),
        "images": [{"url": u, "plan": False} for u in imgs],
    })
    return i


# ----------------------------------------------------------------- warsawhomes.pl и любые WordPress-сайты
def parse_wordpress(html, url, site):
    host = urlparse(url).netloc
    lines = page_text(html)
    i = base_info(site, url)
    urls = re.findall(r'https?://%s/wp-content/uploads/[^"\'\s,)]+?\.(?:jpe?g|png|webp)' % re.escape(host), html)
    groups = OrderedDict()
    for u in urls:
        name = u.rsplit("/", 1)[-1].lower()
        if any(x in name for x in ("logo", "fav", "icon", "cropped-", "avatar", "banner")):
            continue
        b = re.sub(r"-(\d+x\d+|scaled)(?=\.\w+$)", "", u)
        groups.setdefault(b, set()).add(u)

    def best(variants):
        def size(u):
            if "-scaled." in u: return 10 ** 9
            m = re.search(r"-(\d+)x(\d+)\.\w+$", u)
            return int(m.group(1)) * int(m.group(2)) if m else 10 ** 8
        return max(variants, key=size)
    imgs = [best(v) for v in groups.values()]
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    title = htmlmod.unescape(t.group(1).split(" - ")[0].strip()) if t else ""
    body = section(lines, title, ["Pokaż na mapie", "Jak przebiega", "Zapytaj o", "Formularz", "Copyright"]) if title else lines
    if len(body) < 3:
        body = lines
    desc = " ".join(body)
    price = None
    for l in body:
        m = re.fullmatch(r"(\d[\d \.]*)\s*(PLN|zł)(\s*/\s*(mies|m-c)\w*)?", l, re.I)
        if m:
            price = num(m.group(1)); break
    rent = rent_from_text(desc)
    dep = deposit_from_text(desc)
    area = re.search(r"(\d+(?:[.,]\d+)?)\s*(m²|m2|mkw)", label_value(lines, "Powierzchnia") or desc)
    rooms = re.search(r"(\d+)[\s-]*(pokoj|pokoi|pok\.)", desc, re.I)
    street = ""
    if "," in title:
        street = title.split(",")[-1].strip()
    i.update({
        "title": title,
        "rooms": rooms.group(1) if rooms else "",
        "area": area_str(area.group(1)) if area else "",
        "price": price,
        "rent": rent,
        "deposit": dep,
        "street": street,
        "district": title.split(",")[0].strip() if "," in title else "",
        "flags": flags_from_text(desc),
        "images": [{"url": u, "plan": False} for u in imgs],
    })
    return i


# ----------------------------------------------------------------- запасной вариант для любых сайтов
def parse_generic(html, url):
    host = urlparse(url).netloc
    if "/wp-content/uploads/" in html:
        return parse_wordpress(html, url, host.replace("www.", ""))
    lines = page_text(html)
    i = base_info(host.replace("www.", ""), url)
    imgs = re.findall(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html)
    imgs += re.findall(r'https?://[^"\'\s,()]+?\.(?:jpe?g|webp)', html)
    imgs = [u for u in uniq(imgs) if not re.search(r"logo|icon|fav|avatar|thumb|sprite|banner|\d{2,3}x\d{2,3}\.", u, re.I)]
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    desc = " ".join(lines)
    area = re.search(r"(\d+(?:[.,]\d+)?)\s*(m²|m2)", desc)
    i.update({"title": htmlmod.unescape(t.group(1).strip()) if t else "",
              "area": area_str(area.group(1)) if area else "",
              "flags": flags_from_text(desc),
              "images": [{"url": u, "plan": False} for u in imgs[:40]]})
    return i


PARSERS = [
    ("otodom.pl", parse_otodom),
    ("olx.pl", parse_olx),
    ("gratka.pl", lambda h, u: parse_gratka(h, u, "gratka")),
    ("morizon.pl", lambda h, u: parse_gratka(h, u, "morizon")),
    ("lento.pl", parse_lento),
    ("tabelaofert.pl", parse_tabela),
    ("warsawhomes.pl", lambda h, u: parse_wordpress(h, u, "warsawhomes")),
]


def parser_for(url):
    host = urlparse(url).netloc.lower()
    for dom, fn in PARSERS:
        if host == dom or host.endswith("." + dom):
            return fn
    return parse_generic


def get_listing(sess, url):
    r = sess.get(url, timeout=40)
    if r.status_code in (403, 429):
        raise RuntimeError(f"сайт временно не пускает программу (код {r.status_code}), попробуй позже")
    r.raise_for_status()
    final = str(getattr(r, "url", url) or url)   # OLX иногда перенаправляет на Otodom
    info = parser_for(final)(r.text, final)
    if not info["images"]:
        raise RuntimeError("не нашёл фото на странице")
    return info
