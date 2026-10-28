#!/usr/bin/env python3
"""Seznam starých adres (obec + č.p.) a jejich poloha – soubor adresy.json, doplnění souřadnic a mapa.

Použití:
  adresy.py nova <soubor.json>                 založí prázdný seznam (když neexistuje)
  adresy.py pridej <soubor.json> klíč=hodnota … přidá / upraví adresu, např.
        id=nova-ves-46 obec="Nová Ves" cp=46 ku_kod=<kód k.ú.> rok=1847 osoby="Jan Novák (1847)"
        stp=4 skica=CHR473018390 skica_cp=46        (co jsi přečetl na indikační skice; bez skica_cp nejvýš B)
        sjtsk=-605511,-1081530                        (bod z císařského otisku v aplikaci ČÚZK Archiv)
        sjtsk=… bod=kotvy                              (bod spočtený z kotev skici – kotvy.py)
        lat=49.89 lon=16.38 metoda=ručně              (ruční poloha)
        dnesni_cp=neplati                              (dnešní dům s tímto č.p. prokazatelně není ten starý)
        cast="Město"                                   (část obce s vlastním číslováním, např. „č. 97 město“ v zápisu)
        vyrez_popis="…"                                (popisek pod výřezem, např. když výřez ukazuje prázdné místo)
  adresy.py dopln <soubor.json> [--znovu]       dopočítá polohu všem adresám bez souřadnic (--znovu: všem)
  adresy.py vypis <soubor.json>                 přehled s jistotou
  adresy.py mapa <soubor.json> [mapa.html]      mapa (Leaflet) + GeoJSON vedle souboru

Jistota:
  A  č.p. přečtené na skice (skica_cp) a jeho stavební parcela dnes nese stejné č.p. (nebo ručně ověřeno)
  B  poloha ze skici / otisku / kotev, ale dům dnes zanikl, č.p. je jinde, nebo č.p. na skice nepřečteno
  C  jen dnešní č.p. (bez skici – číslo se mohlo od 19. století změnit)
  D  jen obec / katastrální území
"""
import html, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I nepřidává složku skriptu
import ruian  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

SKICA_URL = "https://ags.cuzk.gov.cz/archiv/openmap.html?typ=skicic&idrastru={}"
CISLA = {"cp", "ku_kod", "rok", "skica_rok", "skica_cp"}
DESETINNA = {"lat", "lon"}


def load(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def pridej(path, pairs):
    data = load(path)
    kv = {}
    for p in pairs:
        k, _, v = p.partition("=")
        if k in CISLA and v.strip().lstrip("-").isdigit():
            v = int(v)
        elif k in DESETINNA:
            v = float(v)
        elif k == "sjtsk":
            v = [float(x) for x in v.split(",")]
        kv[k] = v
    if "id" not in kv:
        kv["id"] = f"{kv.get('obec', 'x')}-{kv.get('cp', len(data) + 1)}".lower().replace(" ", "-")
    old = next((e for e in data if e["id"] == kv["id"]), None)
    if old:
        if {"stp", "sjtsk", "cp", "ku_kod"} & kv.keys() and not {"lat", "lon"} & kv.keys():
            for k in ("lat", "lon", "metoda", "jistota", "dnes", "zjisteni"):
                old.pop(k, None)  # změnil se podklad → polohu spočítat znovu
        old.update(kv)
    else:
        data.append(kv)
    save(path, data)
    print(("upraveno" if old else "přidáno") + f": {kv['id']}")


def _dnes(adresy, cp):
    names = [a["adresa"] for a in adresy]
    same = any(a["cp"] == cp for a in adresy) if cp else None
    return {"adresy": names, "stejne_cp": same}


def _dnes_cp(ku, cp, obec, cast=None):
    """Dnešní adresní místo s č.p. v k.ú.; při více částech obce dá přednost zadané části (cast), jinak té,
    která se jmenuje jako obec.

    Adresa části obce je „Část 6, 25722 Obec“, adresa hlavní části „č.p. 6, 25722 Obec“ – jméno obce je v obou
    (za PSČ), proto se rozhoduje podle začátku adresy: nejdřív „<obec> 6, …“, pak „č.p. 6, … <obec>“, pak ostatní."""
    dn = ruian.cp(ku, cp)
    if obec:
        jm = obec.split(" (")[0].lower()

        def poradi(a):
            zac = a["adresa"].split(",")[0].lower()
            if zac.startswith(jm):
                return 0
            if zac.startswith("č.p.") and jm in a["adresa"].lower():
                return 1
            return 2
        dn.sort(key=poradi)
    if cast:  # „Chodské náměstí 97, Město, 34401 Domažlice“ / „Město 97, 34401 …“
        c = cast.lower()
        dn.sort(key=lambda a: not any(k.strip().lower().startswith(c) for k in a["adresa"].split(",")[:2]))
    return dn


def _precteno(e):
    """Je č.p. na skice přečtené? (skica_cp = číslo z budovy nebo z „N° X“ na zahradě)"""
    return e.get("skica_cp") is not None and str(e["skica_cp"]) == str(e.get("cp"))


def _porovnej(e, lat, lon, notes):
    """Kde je dnešní dům se stejným č.p.? Uloží ho do e['dnes'] (pro čáru v mapě) a vrátí vzdálenost."""
    cp, ku = e.get("cp"), e.get("ku_kod")
    if not (cp and ku):
        return None
    dn = _dnes_cp(ku, cp, e.get("obec"), e.get("cast"))
    if not dn:
        notes.append(f"dnes v k.ú. č.p. {cp} není")
        return None
    d = ruian.dist_m(lat, lon, dn[0]["lat"], dn[0]["lon"])
    e["dnes"].update(cp_adresa=dn[0]["adresa"], cp_lat=dn[0]["lat"], cp_lon=dn[0]["lon"], cp_vzdalenost_m=round(d))
    notes.append(f"dnešní č.p. {cp} je {d:.0f} m odtud")
    return d


def _st_cislo(par):
    """'st. 404/1' → 404; pozemková parcela / nic → None."""
    if not par or not par.startswith("st. "):
        return None
    try:
        return int(par[4:].split("/")[0])
    except ValueError:
        return None


def _novostavba(ku, cp, par):
    """Stojí dnešní dům s tímto č.p. na mnohem novější st. parcele než jeho číselní sousedé (č.p. ±1…±3)?

    Ve městech dostávala novostavba často číslo dávno zbořeného domu – pak je dnešní dům úplně jinde.
    Vrací {"min_st", "sousede": [staré domy sousedních č.p.]} nebo None.
    """
    n = _st_cislo(par)
    if n is None:
        return None
    sous = []
    for c in (cp - 1, cp + 1, cp - 2, cp + 2, cp - 3, cp + 3):
        if c <= 0:
            continue
        for a in ruian.cp(ku, c)[:1]:
            p = ruian.parcela_pod(a["lat"], a["lon"])
            s = _st_cislo(p)
            if s is not None:
                sous.append({"cp": c, "adresa": a["adresa"].split(",")[0], "par": p, "st": s,
                             "lat": a["lat"], "lon": a["lon"]})
    stare = [s for s in sous if n > 2 * s["st"] and n - s["st"] > 500]
    if len(stare) < 2:  # aspoň dva sousedé stojí na výrazně starší parcele
        return None
    return {"min_st": min(s["st"] for s in stare), "sousede": sorted(stare, key=lambda s: s["cp"])}


def urci(e):
    """Doplní e['lat'], e['lon'], metoda, jistota, dnes, zjisteni. Vrací krátký popis."""
    cp, ku = e.get("cp"), e.get("ku_kod")
    notes = []
    if e.get("lat") is not None and e.get("metoda"):
        return "ponechána ruční poloha"
    if e.get("sjtsk"):  # bod z císařského otisku, nebo spočtený z kotev skici (bod=kotvy)
        zdroj = "kotvy" if e.get("bod") == "kotvy" else "otisk"
        lat, lon = ruian.sjtsk_to_wgs(*e["sjtsk"])
        b = ruian.bod(lat, lon)
        par = b["parcela"][0] if b["parcela"] else None
        e.update(lat=lat, lon=lon, metoda=zdroj, jistota="B")
        e["dnes"] = _dnes(par["adresy"] if par else [], cp)
        e["dnes"]["parcela"] = (("st. " if par["stavebni"] else "p.č. ") + par["st"]) if par else None
        if e.get("presnost_m"):
            notes.append(f"přesnost {'kotev' if zdroj == 'kotvy' else 'otisku'} asi {e['presnost_m']} m")
        if e["dnes"]["stejne_cp"] and _precteno(e):
            e["jistota"] = "A"
        elif e.get("dnesni_cp") == "neplati":
            notes.append("dnešní č.p. je jiný dům (ověřeno) – nesrovnáváno")
        elif not e["dnes"]["stejne_cp"]:
            d = _porovnej(e, lat, lon, notes)
            if d is not None and d <= 30 and _precteno(e):
                e["jistota"] = "A"
                notes.append("dnešní dům se stejným č.p. stojí na témže místě")
        if not _precteno(e):
            notes.append("č.p. na skice nepřečteno")
        e["zjisteni"] = notes
        kde = f"{e['dnes']['parcela']}, dnes {', '.join(e['dnes']['adresy']) or 'bez adresy'}"
        return "; ".join([f"bod ({zdroj}) → {kde}"] + notes) + f" → {e['jistota']}"
    if e.get("stp") and ku:
        res = ruian.st(ku, e["stp"])  # u rozdělené parcely (st. 85/1, 85/2) více dílů
        if res:
            hit = next(((p, a) for p in res for a in p["adresy"] if a["cp"] == cp), None)
            p = hit[0] if hit else res[0]
            pt = hit[1] if hit else p
            e.update(lat=pt["lat"], lon=pt["lon"], metoda="stp")
            e["dnes"] = _dnes([a for q in res for a in q["adresy"]], cp)
            e["dnes"]["parcela"] = ", ".join(f"st. {q['st']}" for q in res)
            if hit:
                e["jistota"] = "A"
                notes.append(f"st. {p['st']} dnes nese č.p. {cp}")
                if len(res) > 1:
                    notes.append("parcela je dnes rozdělená")
            else:
                e["jistota"] = "B"
                nese = ("nese " + ", ".join(e["dnes"]["adresy"])) if e["dnes"]["adresy"] else "je bez adresy"
                notes.append(f"st. {e['stp']} dnes existuje, ale {nese}")
                d = _porovnej(e, e["lat"], e["lon"], notes)
                if d is not None and d <= 30:  # tentýž statek, adresní bod je na novém dílu parcely
                    e["jistota"] = "A"
                    notes.append("tentýž statek – číslo zůstalo, parcela se dělila")
            if not _precteno(e):  # bez přečteného č.p. je shoda jen nepřímá
                e["jistota"] = "B"
                notes.append("č.p. na skice nepřečteno – poloha jen podle stavební parcely")
            elif e["jistota"] == "B":
                notes.append("ověř tvar a sousedy proti skice")
            e["zjisteni"] = notes
            return "; ".join(notes) + f" → {e['jistota']}"
        notes.append(f"st. {e['stp']} dnes neexistuje (přečíslováno / zbořeno) – najdi dům na císařském otisku (sjtsk=…)")
    if cp and ku and e.get("dnesni_cp") == "neplati":
        notes.append("dnešní č.p. je jiný dům (ověřeno) – nepoužito")
    elif cp and ku:
        dn = _dnes_cp(ku, cp, e.get("obec"), e.get("cast"))
        if dn:
            e.update(lat=dn[0]["lat"], lon=dn[0]["lon"], metoda="dnesni_cp", jistota="C",
                     dnes={"adresy": [a["adresa"] for a in dn], "stejne_cp": True})
            if len(dn) > 1 and e.get("cast"):
                notes.append(f"v k.ú. je víc adres s tímto č.p. – vybrána část „{e['cast']}“: {dn[0]['adresa']}")
            elif len(dn) > 1:
                jm = (e.get("obec") or "").split(" (")[0].lower()
                zac = dn[0]["adresa"].split(",")[0].lower()
                if jm and not zac.startswith(jm) and not zac.startswith("č.p."):
                    notes.append(f"v k.ú. je víc adres s tímto č.p. a žádná nenese jméno obce „{e.get('obec')}“ – "
                                 f"vybráno {dn[0]['adresa']}, NEJSPÍŠ JINÁ ČÁST OBCE: ověř, případně dnesni_cp=neplati")
                else:
                    notes.append(f"v k.ú. je víc adres s tímto č.p. – vybráno {dn[0]['adresa']}")
            par = ruian.parcela_pod(dn[0]["lat"], dn[0]["lon"])
            e["dnes"]["parcela"] = par
            if par and par.startswith("p.č."):
                # V k.ú. s přečíslovanými parcelami stojí na p.č. i staré domy – pak to nic neznamená.
                sous = [ruian.parcela_pod(a["lat"], a["lon"]) for c in (int(e["cp"]) - 1, int(e["cp"]) + 1) if c > 0
                        for a in ruian.cp(e["ku_kod"], c)[:1]]
                if sous and all(s and s.startswith("p.č.") for s in sous):
                    notes.append(f"dnešní dům stojí na pozemkové parcele ({par}), ale stejně i sousední č.p. – parcely tu "
                                 "byly nejspíš přečíslovány, o stáří domu to nic neříká; ověř na skice "
                                 "a polohu spočítej z kotev podle dnešních č.p. (kotvy.py, klíč „cp“)")
                else:
                    notes.append(f"dnešní dům stojí na pozemkové parcele ({par}) – vznikl nejspíš až po stabilním katastru, "
                                 "starý dům stál jinde")
            elif par:
                nov = _novostavba(ku, int(cp), par)
                if nov:
                    # Číslo staršího zbořeného domu dostala novostavba jinde – dnešní dům polohu neurčuje.
                    sous = nov["sousede"]
                    e.update(lat=sum(s["lat"] for s in sous) / len(sous), lon=sum(s["lon"] for s in sous) / len(sous),
                             metoda="sousede", jistota="D")
                    e["dnes"]["stejne_cp"] = False
                    e["zjisteni"] = notes + [
                        f"dnešní č.p. {cp} je NOVOSTAVBA ({par}, sousední staré domy stojí na st. {', '.join(str(x['st']) for x in sous)}) – "
                        "starý dům stál jinde, dnešní č.p. nepoužito",
                        "hledej na skice v řadě sousedů: " + ", ".join(f"č.p. {s['cp']} (dnes {s['adresa']}, {s['par']})"
                                                                      for s in sous),
                        "prozatím střed sousedních starých domů → D"]
                    roz = max(ruian.dist_m(a["lat"], a["lon"], b["lat"], b["lon"]) for a in sous for b in sous)
                    if roz > 250:  # čísla tu nejdou v řadě (přidělována postupně po městě)
                        e["zjisteni"].insert(-1, f"sousedé jsou od sebe {roz:.0f} m – čísla tu nejdou v souvislé řadě, "
                                                 "projdi skicu systematicky (bod je jen orientační)")
                    return "; ".join(e["zjisteni"])
                notes.append(f"dnešní dům stojí na {par} – ověř na skice, zda tam ~1840 stála budova se stejnou st. parcelou "
                             "(vysoké číslo st. parcely = spíš novější stavba)")
            e["zjisteni"] = notes
            return "; ".join(notes + ["jen podle dnešního č.p. → C"])
        notes.append(f"dnes v k.ú. č.p. {cp} není")
    if ku:
        k = ruian.ku_geom(ku)
        lat, lon = ruian.centroid(k["geometry"]["rings"])
        e.update(lat=lat, lon=lon, metoda="obec", jistota="D", dnes={"adresy": []})
        e["zjisteni"] = notes
        return "; ".join(notes + ["jen střed katastrálního území → D"])
    return "chybí ku_kod (zjisti: ruian.py ku \"Obec\")"


def pripoj_vyrezy(path, data):
    """Adresám bez pole `vyrez` připojí výřez `vyrezy/<id>.jpg`, pokud vedle adresy.json existuje."""
    slozka = os.path.dirname(os.path.abspath(path))
    for e in data:
        rel = f"vyrezy/{e['id']}.jpg"
        if not e.get("vyrez") and os.path.exists(os.path.join(slozka, rel)):
            e["vyrez"] = rel
            print(f"{e['id']:<24} připojen výřez {rel}")


def dopln(path, znovu=False):
    data = load(path)
    pripoj_vyrezy(path, data)
    save(path, data)
    for e in data:
        if e.get("lat") is not None and not znovu:
            continue
        if znovu and e.get("metoda") not in ("ručně",):
            for k in ("lat", "lon", "metoda", "jistota", "dnes", "zjisteni"):
                e.pop(k, None)
        try:
            msg = urci(e)
        except Exception as ex:  # síť / služba – ať se uloží aspoň zbytek
            msg = f"CHYBA: {ex}"
        print(f"{e['id']:<24} {msg}")
        save(path, data)


def vypis(path):
    for e in load(path):
        loc = f"{e['lat']:.6f}, {e['lon']:.6f}" if e.get("lat") is not None else "–"
        dnes = ", ".join((e.get("dnes") or {}).get("adresy", [])) or "–"
        print(f"{e.get('jistota', '?')}  {e['id']:<24} {e.get('obec', '')} č.p. {e.get('cp', '?'):<4} "
              f"{loc:<24} {e.get('metoda', ''):<10} dnes: {dnes}")


def geojson(data):
    feats = []
    for e in data:
        if e.get("lat") is None:
            continue
        props = {k: v for k, v in e.items() if k not in ("lat", "lon")}
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [e["lon"], e["lat"]]}, "properties": props})
    return {"type": "FeatureCollection", "features": feats}


MAP_HTML = """<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
 html,body,#map{height:100%;margin:0} body{font:14px/1.4 system-ui,sans-serif}
 .leg{background:#fff;padding:6px 10px;border-radius:6px;box-shadow:0 1px 4px #0003}
 .leg i{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px;vertical-align:-1px}
 .pop h3{margin:0 0 4px;font-size:15px} .pop small{color:#555} .pop img{max-width:260px;display:block;margin-top:6px}
</style></head><body><div id="map"></div>
<script>
const DATA = __DATA__;
const BARVA = {A:'#1a7f37',B:'#d4a017',C:'#d9480f',D:'#868e96'};
const POPIS = {A:'jistá poloha (skica = dnešní parcela i č.p.)',B:'podle skici / otisku',C:'jen dnešní č.p.',D:'jen obec'};
const METODA = {stp:'stavební parcela ze skici',otisk:'bod na císařském otisku',dnesni_cp:'dnešní č.p.',obec:'střed obce','ručně':'ručně'};
const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'});
const orto = L.tileLayer('https://ags.cuzk.gov.cz/arcgis1/rest/services/ORTOFOTO_WM/MapServer/tile/{z}/{y}/{x}',{maxZoom:20,attribution:'© ČÚZK'});
const ztm = L.tileLayer('https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM_WM/MapServer/tile/{z}/{y}/{x}',{maxZoom:18,attribution:'© ČÚZK'});
const kn = L.tileLayer.wms('https://services.cuzk.gov.cz/wms/local-km-wms.asp',{layers:'KN',format:'image/png',transparent:true,maxZoom:20,attribution:'katastr © ČÚZK'});
const map = L.map('map',{layers:[ztm]});
L.control.layers({'Základní mapa ČÚZK':ztm,'Letecký snímek':orto,'OpenStreetMap':osm},{'Dnešní katastr (parcely)':kn}).addTo(map);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pts = [];
for (const e of DATA) {
  if (e.lat == null) continue;
  const j = e.jistota || 'D';
  const m = L.circleMarker([e.lat, e.lon], {radius: 8, color: '#fff', weight: 2, fillColor: BARVA[j], fillOpacity: .95}).addTo(map);
  let h = `<div class="pop"><h3>${esc(e.obec)} č.p. ${esc(e.cp)}</h3>`;
  if (e.rok) h += `<div>v matrice: ${esc(e.rok)}</div>`;
  if (e.osoby) h += `<div>${esc(e.osoby)}</div>`;
  h += `<small>${esc(POPIS[j])} · ${esc(METODA[e.metoda] || e.metoda)}`;
  if (e.stp) h += ` · na skici st. p. ${esc(e.stp)}`;
  h += `</small>`;
  if (e.dnes && e.dnes.adresy && e.dnes.adresy.length) h += `<div><small>dnes: ${esc(e.dnes.adresy.join(', '))}</small></div>`;
  if (e.zjisteni && e.zjisteni.length) h += `<div><small>${esc(e.zjisteni.join('; '))}</small></div>`;
  if (e.poznamka) h += `<div>${esc(e.poznamka)}</div>`;
  if (e.vyrez) h += `<img src="${esc(e.vyrez)}" alt="výřez indikační skici">`;
  if (e.vyrez && e.vyrez_popis) h += `<div><small>${esc(e.vyrez_popis)}</small></div>`;
  if (e.skica) h += `<div><a href="https://ags.cuzk.gov.cz/archiv/openmap.html?typ=skicic&idrastru=${encodeURIComponent(e.skica)}" target="_blank" rel="noopener">indikační skica (ČÚZK Archiv)</a></div>`;
  m.bindPopup(h + '</div>');
  m.bindTooltip(`${esc(e.obec)} ${esc(e.cp)}`);
  pts.push([e.lat, e.lon]);
}
if (pts.length) map.fitBounds(pts, {padding: [40, 40], maxZoom: 17}); else map.setView([49.8, 15.5], 7);
const leg = L.control({position: 'bottomleft'});
leg.onAdd = () => { const d = L.DomUtil.create('div', 'leg'); d.innerHTML = Object.keys(POPIS).map(k => `<div><i style="background:${BARVA[k]}"></i>${k} – ${POPIS[k]}</div>`).join(''); return d; };
leg.addTo(map);
</script></body></html>
"""


def mapa(path, out=None):
    data = load(path)
    out = out or os.path.splitext(path)[0] + "_mapa.html"
    gj = os.path.splitext(path)[0] + ".geojson"
    with open(gj, "w", encoding="utf-8") as f:
        json.dump(geojson(data), f, ensure_ascii=False, indent=1)
    title = "Domy předků – " + ", ".join(sorted({e.get("obec", "") for e in data})[:3])
    page = MAP_HTML.replace("__TITLE__", html.escape(title)).replace(
        "__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"mapa: {out}\nGeoJSON: {gj}  ({sum(e.get('lat') is not None for e in data)} bodů)")


def main(argv):
    if len(argv) < 3:
        print(__doc__); return
    cmd, path = argv[1], argv[2]
    if cmd == "nova":
        if not os.path.exists(path):
            save(path, [])
        print(path)
    elif cmd == "pridej":
        pridej(path, argv[3:])
    elif cmd == "dopln":
        dopln(path, "--znovu" in argv)
    elif cmd == "vypis":
        vypis(path)
    elif cmd == "mapa":
        mapa(path, argv[3] if len(argv) > 3 else None)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv)
