#!/usr/bin/env python3
"""Prezentační mapa domů předků – stránka k prohlížení a sdílení (podklad ČÚZK bez externích dlaždic).

Použití: mapa.py <výstupní složka> <adresy.json> [další.json …] [--posuny]
Vytvoří ve výstupní složce index.html a podklady/*.jpg (ČÚZK základní mapa a letecký snímek: přehled území,
okolí každé obce a obec v plné podrobnosti) a files.json = seznam souborů k publikování
({"publikovaná/cesta": "zdrojový soubor"} – přesně tvar parametru `files` nástroje Artifact, s `root` = výstupní složka
není potřeba, cesty jsou absolutní). Výřezy skic (`vyrez` v adrese) se berou relativně ke složce prvního adresy.json.
Potřebuje ImageMagick (`magick`). Stažené dlaždice se ukládají do <výstup>/cache a znovu nestahují.

Na mapě: barva = jistota, při oddálení jedna značka na obec, přepínač mapa / letecký snímek, seznam s filtry,
výřezy skic (klik = zvětšení), odkaz na skicu v ČÚZK Archiv. --posuny přidá čárkované čáry k dnešnímu domu se stejným
č.p. (pro ladění; běžným uživatelům je nezobrazuj).

Vedle mapy vznikne domy.geojson – body domů pro jiné aplikace (např. mapu rodinného webu ze skillu rodokmen),
formát v reference/vystup.md.
"""
import glob, json, math, os, shutil, subprocess, sys, urllib.request, unicodedata, re

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "prezentace")
MAGICK = shutil.which("magick") or next(iter(sorted(glob.glob(r"C:\Program Files\ImageMagick-*\magick.exe"))), None)
DEST = ROOT = CACHE = OUT = None  # nastaví main()
SRC = {"ztm": "ZTM_WM", "orto": "ORTOFOTO_WM"}
UA = {"User-Agent": "stare-adresy-skill/1.0 (genealogie, jednorazovy podklad)"}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def tile_xy(lat, lon, z):
    n = 2 ** z
    r = math.radians(lat)
    return (lon + 180) / 360 * n, (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * n


def tile_latlon(x, y, z):
    n = 2 ** z
    lon = x / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lat, lon


def fetch(src, z, x, y):
    p = os.path.join(CACHE, src, str(z), str(x), f"{y}.jpg")
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        url = f"https://ags.cuzk.gov.cz/arcgis1/rest/services/{SRC[src]}/MapServer/tile/{z}/{y}/{x}"
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            open(p, "wb").write(r.read())
    return p


def podklad(name, lat0, lon0, lat1, lon1, z, quality=72):
    """Slepí dlaždice pokrývající obdélník; vrací [[jih, západ], [sever, východ]]."""
    x0, y1 = tile_xy(lat0, lon0, z)  # jih-západ
    x1, y0 = tile_xy(lat1, lon1, z)  # sever-východ
    xs, ys = range(int(x0), int(x1) + 1), range(int(y0), int(y1) + 1)
    for src in SRC:
        dst = os.path.join(OUT, f"{name}_{src}.jpg")
        klic = f"{z} {xs.start}-{xs.stop} {ys.start}-{ys.stop}"  # rozsah dlaždic; při změně bodů obrázek znovu
        meta = os.path.join(CACHE, f"{name}_{src}.rozsah")
        if os.path.exists(dst) and os.path.exists(meta) and open(meta).read() == klic:
            continue
        os.makedirs(CACHE, exist_ok=True)
        open(meta, "w").write(klic)
        rows = []
        for y in ys:
            row = os.path.join(CACHE, f"row_{src}_{z}_{y}_{name}.jpg")
            subprocess.run([MAGICK, *[fetch(src, z, x, y) for x in xs], "+append", row], check=True)
            rows.append(row)
        subprocess.run([MAGICK, *rows, "-append", "-strip", "-interlace", "Plane", "-quality", str(quality), dst], check=True)
        for r in rows:
            os.remove(r)
    s, w = tile_latlon(xs[0], ys[-1] + 1, z)
    n, e = tile_latlon(xs[-1] + 1, ys[0], z)
    return [[s, w], [n, e]], len(xs) * len(ys)


def bbox(pts, margin_m):
    lat = [p[0] for p in pts]; lon = [p[1] for p in pts]
    dlat = margin_m / 111320; dlon = margin_m / (111320 * math.cos(math.radians(sum(lat) / len(lat))))
    return min(lat) - dlat, min(lon) - dlon, max(lat) + dlat, max(lon) + dlon


def domy_geojson(data):
    """Body domů ve formátu pro jiné aplikace (reference/vystup.md)."""
    pole = ("id", "obec", "cp", "rok", "osoby", "jistota", "metoda", "skica", "skica_rok", "stp", "cteni", "vyrez",
            "poznamka", "presnost_m")
    feats = []
    for e in data:
        if e.get("lat") is None:
            continue
        p = {k: e[k] for k in pole if e.get(k) not in (None, "")}
        dn = e.get("dnes") or {}
        if dn.get("adresy"):
            p["dnes_na_miste"] = dn["adresy"]
        if dn.get("cp_vzdalenost_m") is not None and dn["cp_vzdalenost_m"] > 30:
            p["dnesni_cp_jinde_m"] = dn["cp_vzdalenost_m"]
        if e.get("skica"):
            mza = e["skica"].startswith("MOR")
            p["skica_url"] = (f"https://www.mza.cz/indikacniskici/skica/detail/{e['skica']}" if mza
                              else SKICA_URL.format(e["skica"]))
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [e["lon"], e["lat"]]},
                      "properties": p})
    return {"type": "FeatureCollection", "name": "domy_predku", "features": feats}


SKICA_URL = "https://ags.cuzk.gov.cz/archiv/openmap.html?typ=skicic&idrastru={}"


def main(dest, files, posuny=False):
    global DEST, ROOT, CACHE, OUT
    if not MAGICK:
        raise SystemExit("Chybí ImageMagick (magick) – nainstaluj ho, je potřeba ke slepení podkladů.")
    DEST = os.path.abspath(dest); ROOT = os.path.dirname(os.path.abspath(files[0]))
    CACHE = os.path.join(DEST, "cache"); OUT = os.path.join(DEST, "podklady")
    data, seen = [], {}
    for f in files:
        for e in json.load(open(f, encoding="utf-8")):
            if e["id"] in seen:
                data[seen[e["id"]]] = e
            else:
                seen[e["id"]] = len(data); data.append(e)
    os.makedirs(OUT, exist_ok=True)
    obce, layers, publish = {}, [], {}
    for e in data:
        if e.get("lat") is not None:
            obce.setdefault(e.get("obec", "?"), []).append((e["lat"], e["lon"]))
    for obec, pts in obce.items():
        s, w, n, e_ = bbox(pts, 180)
        for z in (17, 16, 15):  # nejvyšší zvětšení, které se vejde do ~70 dlaždic
            x0, y1 = tile_xy(s, w, z); x1, y0 = tile_xy(n, e_, z)
            if (int(x1) - int(x0) + 1) * (int(y1) - int(y0) + 1) <= 70:
                break
        b, cnt = podklad(slug(obec), s, w, n, e_, z)
        layers.append({"obec": obec, "bounds": b, "z": z, "img": slug(obec), "od": 14.5})
        # širší okolí obce ve střední podrobnosti – pro přiblížení 12,5–14,5
        s2, w2, n2, e2 = bbox(pts, 1500)
        b2, cnt2 = podklad(slug(obec) + "-okoli", s2, w2, n2, e2, 14, 70)
        layers.append({"obec": obec, "bounds": b2, "z": 14, "img": slug(obec) + "-okoli", "od": 12})
        print(f"{obec:<20} z{z} {cnt} dlaždic, okolí z14 {cnt2}")
    # přehled ve dvou podrobnostech: celé území (z10) a hlavní shluk kolem mediánu (z13, do ~130 dlaždic)
    allp = [p for v in obce.values() for p in v]
    medlat = sorted(p[0] for p in allp)[len(allp) // 2]; medlon = sorted(p[1] for p in allp)[len(allp) // 2]
    near = [p for p in allp if abs(p[0] - medlat) < 0.3 and abs(p[1] - medlon) < 0.45]
    s, w, n, e_ = bbox(allp, 30000)
    b, cnt = podklad("prehled-cr", s, w, n, e_, 10, 70)
    overview = [{"obec": "", "bounds": b, "z": 10, "img": "prehled-cr"}]
    print(f"přehled území z10 {cnt} dlaždic")
    s, w, n, e_ = bbox(near, 2500)
    for z in (13, 12):
        x0, y1 = tile_xy(s, w, z); x1, y0 = tile_xy(n, e_, z)
        if (int(x1) - int(x0) + 1) * (int(y1) - int(y0) + 1) <= 130:
            break
    b, cnt = podklad("prehled-okoli", s, w, n, e_, z, 68)
    overview.append({"obec": "", "bounds": b, "z": z, "img": "prehled-okoli"})
    print(f"přehled okolí z{z} {cnt} dlaždic")
    for f in os.listdir(OUT):
        publish[f"podklady/{f}"] = os.path.join(OUT, f)
    os.makedirs(os.path.join(DEST, "vyrezy"), exist_ok=True)
    for e in data:  # výřezy zkopírovat k mapě, ať složka funguje i lokálně (index.html otevřený z disku)
        if e.get("vyrez"):
            p = os.path.join(ROOT, e["vyrez"])
            if os.path.exists(p):
                rel = "vyrezy/" + os.path.basename(p)
                cil = os.path.join(DEST, "vyrezy", os.path.basename(p))
                if os.path.abspath(p) != os.path.abspath(cil):
                    shutil.copy2(p, cil)
                e["vyrez"] = rel
                publish[rel] = cil
            else:
                e.pop("vyrez")
    css = open(os.path.join(TPL, "leaflet.css"), encoding="utf-8").read()
    tpl = open(os.path.join(TPL, "sablona.html"), encoding="utf-8").read()
    tpl = tpl.replace("/*POSUNY*/false", "true" if posuny else "false")
    with open(os.path.join(DEST, "domy.geojson"), "w", encoding="utf-8") as f:
        json.dump(domy_geojson(data), f, ensure_ascii=False, indent=1)
    page = (tpl.replace("/*LEAFLET_CSS*/", css)
               .replace("/*DATA*/", json.dumps({"adresy": data, "podklady": overview + layers}, ensure_ascii=False)
                        .replace("</", "<\\/")))
    open(os.path.join(DEST, "index.html"), "w", encoding="utf-8").write(page)
    publish = {k: os.path.abspath(v) for k, v in publish.items()}
    json.dump(publish, open(os.path.join(DEST, "files.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    size = sum(os.path.getsize(p) for p in publish.values())
    print(f"index.html + {len(publish)} souborů, {size / 1e6:.1f} MB; adres {len(data)}, s polohou {len(allp)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    args = [a for a in sys.argv[1:] if a != "--posuny"]
    main(args[0], args[1:], posuny="--posuny" in sys.argv)
