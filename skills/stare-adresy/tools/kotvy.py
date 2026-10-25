#!/usr/bin/env python3
"""Převod mezi souřadnicemi prohlížeče skici a skutečnou mapou podle kotev (podobnostní transformace).

Prohlížeč indikační skici (openmap.html) má jen vlastní souřadnice listů. V rámci jednoho bloku listů
(pozor: intravilán měst bývá samostatný blok ve větším měřítku) jsou ale s mapou lineárně svázané.
Stačí 2 kotvy, lépe 3–5: budovy, které na skice přečteš (stavební parcela) a které dnes existují.
Kde se čísla stavebních parcel nezachovala (Žamberk, přestavěné čtvrti), použij místo "st" klíč "cp":
dům, jehož č.p. na skice přečteš a který dnes stojí na stejném místě (poloha = dnešní adresní bod).

Použití:
  kotvy.py <ku_kod> <soubor.json>
      soubor: {"kotvy": [{"st": "89", "skica": [8183.96, -32617.1]}, {"cp": 269, "skica": […]}, …],
               "body":  [{"id": "cp-221", "skica": [x, y]}, …],          (bod ze skici → mapa)
               "hledej": [{"id": "st-157", "st": "157"}, {"id": "dnes-256", "cp": 256}, …]}
                                                                  (dnešní parcela / dnešní dům → kde je na skice)
      "skica" = souřadnice z prohlížeče skici (view.toMap, viz reference/skicy.md).
      Vypíše chyby kotev v metrech (kotvu s chybou > 2× průměr vyřaď – špatně přečtená / přečíslovaná),
      polohu bodů v WGS84 a S-JTSK a souřadnice skici, kde hledat dnešní parcely.
"""
import json, math, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ruian  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")


def wgs_to_sjtsk(pts):
    g = {"geometryType": "esriGeometryPoint", "geometries": [{"x": lon, "y": lat} for lat, lon in pts]}
    r = ruian._post(ruian.GEOM, {"geometries": json.dumps(g), "inSR": 4326, "outSR": 5514})["geometries"]
    return [(p["x"], p["y"]) for p in r]


def fit(src, dst):
    """Podobnostní transformace dst = s·R·src + t (nejmenší čtverce). Vrací funkci a inverzi."""
    n = len(src)
    mx, my = sum(p[0] for p in src) / n, sum(p[1] for p in src) / n
    ux, uy = sum(p[0] for p in dst) / n, sum(p[1] for p in dst) / n
    sxx = sxy = ss = 0.0
    for (x, y), (u, v) in zip(src, dst):
        x, y, u, v = x - mx, y - my, u - ux, v - uy
        sxx += x * u + y * v
        sxy += x * v - y * u
        ss += x * x + y * y
    a, b = sxx / ss, sxy / ss  # a = s·cos, b = s·sin
    fwd = lambda x, y: (a * (x - mx) - b * (y - my) + ux, b * (x - mx) + a * (y - my) + uy)
    d = a * a + b * b
    inv = lambda u, v: (mx + (a * (u - ux) + b * (v - uy)) / d, my + (-b * (u - ux) + a * (v - uy)) / d)
    return fwd, inv, math.sqrt(d), math.degrees(math.atan2(b, a))


def main(argv):
    if len(argv) < 3:
        print(__doc__); return
    ku, cfg = argv[1], json.load(open(argv[2], encoding="utf-8"))
    src, real, names = [], [], []
    for k in cfg["kotvy"]:
        if "cp" in k:   # kotva podle dnešního č.p. (adresní bod) – pro k.ú. s přečíslovanými parcelami
            p = ruian.cp(ku, k["cp"]); nm = f"č.p. {k['cp']}"
            if len(p) > 1:
                print(f"kotva {nm}: v k.ú. je víc domů s tímto číslem – vynechávám"); continue
        else:
            p = ruian.st(ku, k["st"]); nm = f"st. {k['st']}"
        if not p:
            print(f"kotva {nm}: dnes neexistuje – vynechávám"); continue
        lat = sum(q["lat"] for q in p) / len(p); lon = sum(q["lon"] for q in p) / len(p)
        src.append(tuple(k["skica"])); real.append((lat, lon)); names.append(nm)
    if len(src) < 2:
        raise SystemExit("Potřebuji aspoň 2 platné kotvy.")
    dst = wgs_to_sjtsk(real)
    fwd, inv, s, rot = fit(src, dst)
    print(f"měřítko {s:.4f} m na jednotku skici, natočení {rot:.1f}°, kotev {len(src)}")
    for nm, p, q in zip(names, src, dst):
        u, v = fwd(*p)
        print(f"  kotva {nm:<10} chyba {math.hypot(u - q[0], v - q[1]):5.1f} m")
    if len(src) == 2:
        print("  (jen 2 kotvy – chybu nejde ověřit, přidej třetí)")
    for b in cfg.get("body", []):
        X, Y = fwd(*b["skica"])
        lat, lon = ruian.sjtsk_to_wgs(X, Y)
        print(f"bod {b['id']}: {lat:.6f}, {lon:.6f}   S-JTSK {X:.1f},{Y:.1f}")
    for h in cfg.get("hledej", []):
        if "cp" in h:
            for p in ruian.cp(ku, h["cp"]):
                (X, Y), = wgs_to_sjtsk([(p["lat"], p["lon"])])
                x, y = inv(X, Y)
                print(f"hledej {h.get('id', h['cp'])}: dnešní {p['adresa']} je na skice kolem [{x:.1f}, {y:.1f}]")
            continue
        for p in ruian.st(ku, h["st"]):
            (X, Y), = wgs_to_sjtsk([(p["lat"], p["lon"])])
            x, y = inv(X, Y)
            print(f"hledej {h.get('id', h['st'])}: dnešní st. {p['st']} je na skice kolem [{x:.1f}, {y:.1f}]")


if __name__ == "__main__":
    main(sys.argv)
