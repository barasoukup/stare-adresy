#!/usr/bin/env python3
"""Dotazy do dnešního katastru a adres (RÚIAN, veřejná služba ČÚZK, bez přihlášení).

Použití:
  ruian.py ku "Nová Ves"                 katastrální území podle jména (kód k.ú., obec)
  ruian.py cp <kód k.ú.> <č.p.>         dnešní adresa s tímto číslem popisným v k.ú. (bod)
  ruian.py st <kód k.ú.> <číslo>        dnešní stavební parcela „st. 4“ (i „4/2“): střed, výměra, adresy na ní
  ruian.py bod <lat> <lon>             co je dnes v bodě (parcela, k.ú., nejbližší adresa)
  ruian.py bod --sjtsk <X> <Y>         totéž pro bod v S-JTSK (např. střed mapy v aplikaci ČÚZK Archiv)
  ruian.py okoli <lat> <lon> [metrů]    stavební parcely a č.p. v okolí bodu (výchozí 60 m)
  ruian.py sjtsk <lat> <lon>            převod WGS84 → S-JTSK (souřadnice pro aplikaci ČÚZK Archiv)
  ruian.py kotva <k.ú.> <st.> <X> <Y>   přesnost otisku: bod S-JTSK přečtený na otisku vs. dnešní stavební parcela

Přidej --json pro strojový výstup. Souřadnice jsou WGS84 (jako na mapy.cz / Google).
"""
import json, math, sys, time, urllib.parse, urllib.request

for _s in (sys.stdout, sys.stderr):  # UTF-8 i na Windows (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://ags.cuzk.gov.cz/arcgis/rest/services/RUIAN/MapServer"
GEOM = "https://ags.cuzk.gov.cz/arcgis/rest/services/Utilities/Geometry/GeometryServer/project"
L_PARCELA, L_ADRESA, L_KU, L_OBEC = 5, 1, 7, 12
UA = {"User-Agent": "stare-adresy-skill/1.0 (genealogie, jednotlive dotazy)"}


def _post(url, params, pokusu=3):
    data = urllib.parse.urlencode({**params, "f": "json"}).encode()
    for i in range(pokusu):  # služba občas zavře spojení (WinError 10054) – zkusit znovu
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=UA), timeout=60) as r:
                res = json.load(r)
            break
        except (OSError, ValueError):
            if i == pokusu - 1:
                raise
            time.sleep(2 * (i + 1))
    if "error" in res:
        raise RuntimeError(f"ČÚZK vrátil chybu: {res['error']}")
    return res


def query(layer, where="1=1", fields="*", geometry=None, geom_type=None, distance=None, out_geom=False):
    p = {"where": where, "outFields": fields, "returnGeometry": str(out_geom).lower(), "outSR": 4326}
    if geometry is not None:
        p.update(geometry=json.dumps(geometry), geometryType=geom_type, inSR=geometry.get("spatialReference", {}).get("wkid", 4326),
                 spatialRel="esriSpatialRelIntersects")
        if distance:
            p.update(distance=distance, units="esriSRUnit_Meter")
    return _post(f"{BASE}/{layer}/query", p).get("features", [])


def point(lat, lon):
    return {"x": lon, "y": lat, "spatialReference": {"wkid": 4326}}


def sjtsk_to_wgs(x, y):
    """S-JTSK (EPSG:5514, záporná čísla jako v aplikacích ČÚZK) → (lat, lon)."""
    g = {"geometryType": "esriGeometryPoint", "geometries": [{"x": x, "y": y}]}
    r = _post(GEOM, {"geometries": json.dumps(g), "inSR": 5514, "outSR": 4326})["geometries"][0]
    return round(r["y"], 7), round(r["x"], 7)


def wgs_to_sjtsk(lat, lon):
    """(lat, lon) → S-JTSK (X, Y) jako v aplikacích ČÚZK – pro nastavení pohledu na otisk/kotvy."""
    g = {"geometryType": "esriGeometryPoint", "geometries": [{"x": lon, "y": lat}]}
    r = _post(GEOM, {"geometries": json.dumps(g), "inSR": 4326, "outSR": 5514})["geometries"][0]
    return round(r["x"], 1), round(r["y"], 1)


def centroid(rings):
    """Těžiště polygonu (vnější kruh) v lon/lat – na pár desítek metrů stačí rovinný výpočet."""
    ring = max(rings, key=len)
    lat0 = math.radians(ring[0][1])
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        x1, x2 = x1 * math.cos(lat0), x2 * math.cos(lat0)
        f = x1 * y2 - x2 * y1
        a += f; cx += (x1 + x2) * f; cy += (y1 + y2) * f
    if abs(a) < 1e-15:
        return ring[0][1], ring[0][0]
    return round(cy / (3 * a), 7), round(cx / (3 * a) / math.cos(lat0), 7)


def dist_m(lat1, lon1, lat2, lon2):
    k = 111_320
    return math.hypot((lat2 - lat1) * k, (lon2 - lon1) * k * math.cos(math.radians(lat1)))


def ku(name):
    feats = query(L_KU, f"nazev like '{name.replace(chr(39), '')}%'", "kod,nazev,obec")
    out = []
    for f in feats:
        a = f["attributes"]
        ob = query(L_OBEC, f"kod={a['obec']}", "nazev")
        out.append({"ku_kod": a["kod"], "ku": a["nazev"], "obec_kod": a["obec"],
                    "obec": ob[0]["attributes"]["nazev"] if ob else "?"})
    return out


def ku_at(lat, lon):
    f = query(L_KU, geometry=point(lat, lon), geom_type="esriGeometryPoint", fields="kod,nazev")
    return (f[0]["attributes"]["kod"], f[0]["attributes"]["nazev"]) if f else (None, None)


def ku_geom(ku_kod):
    f = query(L_KU, f"kod={int(ku_kod)}", "kod,nazev", out_geom=True)
    if not f:
        raise SystemExit(f"Katastrální území s kódem {ku_kod} neexistuje.")
    return f[0]


def _adresa(f):
    a = f["attributes"]
    cev = "č.ev." in (a["adresa"] or "")  # číslo evidenční (chata, kůlna) – není číslo popisné
    return {"adresa": a["adresa"], "cp": None if cev else a["cislodomovni"], "cev": a["cislodomovni"] if cev else None,
            "lat": round(f["geometry"]["y"], 7),
            "lon": round(f["geometry"]["x"], 7), "adresni_misto": a["kod"]}


def cp(ku_kod, cislo):
    """Dnešní adresní místa s č.p. ležící v daném k.ú."""
    k = ku_geom(ku_kod)
    xs = [p[0] for r in k["geometry"]["rings"] for p in r]
    ys = [p[1] for r in k["geometry"]["rings"] for p in r]
    env = {"xmin": min(xs), "ymin": min(ys), "xmax": max(xs), "ymax": max(ys), "spatialReference": {"wkid": 4326}}
    feats = query(L_ADRESA, f"cislodomovni={int(cislo)}", "kod,adresa,cislodomovni", env, "esriGeometryEnvelope", out_geom=True)
    out = []
    for f in feats:
        a = _adresa(f)
        if a["cp"] is not None and ku_at(a["lat"], a["lon"])[0] == int(ku_kod):
            out.append(a)
    return out


def parcela_pod(lat, lon):
    """Na jaké parcele bod dnes leží: 'st. 5/1' (stavební) / 'p.č. 83/2' (pozemková) / None."""
    f = query(L_PARCELA, geometry=point(lat, lon), geom_type="esriGeometryPoint",
              fields="kmenovecislo,poddelenicisla,druhcislovanikod")
    if not f:
        return None
    a = f[0]["attributes"]
    num = f"{a['kmenovecislo']}" + (f"/{a['poddelenicisla']}" if a.get("poddelenicisla") else "")
    return ("st. " if a["druhcislovanikod"] == 1 else "p.č. ") + num


def _parcel_out(f):
    a = f["attributes"]
    lat, lon = centroid(f["geometry"]["rings"])
    adr = query(L_ADRESA, geometry={**f["geometry"], "spatialReference": {"wkid": 4326}},
                geom_type="esriGeometryPolygon", fields="kod,adresa,cislodomovni", out_geom=True)
    num = f"{a['kmenovecislo']}" + (f"/{a['poddelenicisla']}" if a.get("poddelenicisla") else "")
    return {"st": num, "stavebni": a["druhcislovanikod"] == 1, "vymera_m2": a["vymeraparcely"],
            "lat": lat, "lon": lon, "adresy": [_adresa(x) for x in adr], "obrys": f["geometry"]["rings"]}


def st(ku_kod, cislo):
    """Stavební parcela st. <cislo> v k.ú. dnes (druh číslování 1 = stavební parcela)."""
    kmen, _, pod = str(cislo).partition("/")
    where = f"katastralniuzemi={int(ku_kod)} and druhcislovanikod=1 and kmenovecislo={int(kmen)}"
    where += f" and poddelenicisla={int(pod)}" if pod else ""
    fields = "kmenovecislo,poddelenicisla,vymeraparcely,druhcislovanikod"
    return [_parcel_out(f) for f in query(L_PARCELA, where, fields, out_geom=True)]


def bod(lat, lon):
    fields = "kmenovecislo,poddelenicisla,vymeraparcely,druhcislovanikod,katastralniuzemi"
    par = query(L_PARCELA, geometry=point(lat, lon), geom_type="esriGeometryPoint", fields=fields, out_geom=True)
    near = query(L_ADRESA, geometry=point(lat, lon), geom_type="esriGeometryPoint", distance=150,
                 fields="kod,adresa,cislodomovni", out_geom=True)
    near = sorted((_adresa(f) for f in near), key=lambda a: dist_m(lat, lon, a["lat"], a["lon"]))
    for a in near:
        a["vzdalenost_m"] = round(dist_m(lat, lon, a["lat"], a["lon"]))
    kod, nazev = ku_at(lat, lon)
    return {"lat": lat, "lon": lon, "ku_kod": kod, "ku": nazev,
            "parcela": [_parcel_out(f) for f in par], "nejblizsi_adresy": near[:5]}


def okoli(lat, lon, metru=60):
    fields = "kmenovecislo,poddelenicisla,vymeraparcely,druhcislovanikod"
    feats = query(L_PARCELA, "druhcislovanikod=1", fields, point(lat, lon), "esriGeometryPoint", metru, out_geom=True)
    out = [_parcel_out(f) for f in feats]
    for p in out:
        p["vzdalenost_m"] = round(dist_m(lat, lon, p["lat"], p["lon"]))
    return sorted(out, key=lambda p: p["vzdalenost_m"])


def _fmt_parcel(p):
    adr = "; ".join(a["adresa"] for a in p["adresy"]) or "bez adresy"
    d = f"  {p['vzdalenost_m']:>4} m" if "vzdalenost_m" in p else ""
    return f"st. {p['st']:<7} {p['vymera_m2']:>7.0f} m²  {p['lat']:.6f}, {p['lon']:.6f}{d}  {adr}"


def main(argv):
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if len(argv) < 2:
        print(__doc__); return
    cmd, args = argv[1], argv[2:]
    if cmd == "ku":
        res = ku(args[0])
        txt = [f"{r['ku_kod']}  {r['ku']:<32} obec {r['obec']}" for r in res] or ["Nic nenalezeno – zkus kratší začátek jména."]
    elif cmd == "cp":
        res = cp(args[0], args[1])
        for a in res:
            a["parcela"] = parcela_pod(a["lat"], a["lon"])
        txt = [f"{a['adresa']}  {a['lat']:.6f}, {a['lon']:.6f}  na {a['parcela'] or '?'}" for a in res]             or [f"V k.ú. {args[0]} dnes č.p. {args[1]} není."]
    elif cmd == "st":
        res = st(args[0], args[1])
        for p in res:
            p.pop("obrys", None) if not as_json else None
        txt = [_fmt_parcel(p) for p in res] or [f"Stavební parcela st. {args[1]} v k.ú. {args[0]} dnes neexistuje."]
    elif cmd == "bod":
        if args[0] == "--sjtsk":
            lat, lon = sjtsk_to_wgs(float(args[1]), float(args[2]))
        else:
            lat, lon = float(args[0]), float(args[1])
        res = bod(lat, lon)
        txt = [f"Bod {lat:.6f}, {lon:.6f}  k.ú. {res['ku']} ({res['ku_kod']})"]
        txt += ["  parcela: " + ("st. " if p["stavebni"] else "p.č. ") + _fmt_parcel(p)[4:] for p in res["parcela"]]
        txt += [f"  adresa {a['vzdalenost_m']:>4} m: {a['adresa']}" for a in res["nejblizsi_adresy"]]
        for p in res["parcela"]:
            p.pop("obrys", None) if not as_json else None
    elif cmd == "sjtsk":
        res = dict(zip(("x", "y"), wgs_to_sjtsk(float(args[0]), float(args[1]))))
        txt = [f"S-JTSK {res['x']}, {res['y']}"]
    elif cmd == "kotva":
        # kotva <k.ú.> <st. číslo> <X> <Y>: přesnost otisku – bod (S-JTSK) přečtený na otisku vs. dnešní parcela
        lat, lon = sjtsk_to_wgs(float(args[2]), float(args[3]))
        res = []
        for p in st(args[0], args[1]):
            inside = any(q["st"] == p["st"] and q["stavebni"] for q in bod(lat, lon)["parcela"])
            res.append({"st": p["st"], "vzdalenost_m": round(dist_m(lat, lon, p["lat"], p["lon"])), "uvnitr": inside,
                        "adresy": [a["adresa"] for a in p["adresy"]]})
        txt = [f"st. {r['st']}: bod z otisku je {r['vzdalenost_m']} m od středu dnešní parcely"
               f"{' (leží uvnitř)' if r['uvnitr'] else ''}  {'; '.join(r['adresy'])}" for r in res] \
            or [f"st. {args[1]} dnes neexistuje – vyber jinou kotvu"]
    elif cmd == "okoli":
        res = okoli(float(args[0]), float(args[1]), float(args[2]) if len(args) > 2 else 60)
        if not as_json:
            for p in res:
                p.pop("obrys", None)
        txt = [_fmt_parcel(p) for p in res] or ["V okolí není žádná stavební parcela – zvětši okruh."]
    else:
        print(__doc__); return
    print(json.dumps(res, ensure_ascii=False, indent=1) if as_json else "\n".join(txt))


if __name__ == "__main__":
    main(sys.argv)
