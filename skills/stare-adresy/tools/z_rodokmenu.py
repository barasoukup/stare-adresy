#!/usr/bin/env python3
"""Načte adresy „obec čp. X“ z projektu skillu rodokmen do seznamu adres (adresy.json).

Použití: z_rodokmenu.py <složka projektu rodokmenu> <adresy.json> [--od 1700] [--do 1925]

Čte `data/osoby.py` (předci P, příbuzní SIDE) – soubor se NEspouští, jen se rozebere (ast) – a z faktů `f`, textů `t`
a poznámek vybere zmínky „<obec> čp. <číslo>“ s rokem a osobou. Skloněné tvary obcí („v Lhotě“, „z Dlouhé
Vsi“) převede podle `data/mista.json` (pole `re`) na základní název; co nepozná, označí `obec_overit`.
Katastrální území doplní, je-li jednoznačné (jinak `ku_kandidati`). Existující adresy doplní (osoby, rok), nic nemaže.

Zmínky po roce --do (výchozí 1925) přeskočí: skici jsou z let 1824–1843 a mladší adresy patří často žijícím lidem.
Projekt rodokmenu nemění.
"""
import ast, json, os, re, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ruian  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

UP, LO = "A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ", "a-záčďéěíňóřšťúůýž"
SLOVO = rf"[{UP}][{LO}]+"
CP_RE = re.compile(rf"(?P<obec>{SLOVO}(?:[ -](?:{SLOVO}|u|nad|pod)){{0,3}}?)\s+(?:\([^)]*\)\s+)?"
                   rf"(?:čp\.|č\.\s?p\.)\s?(?P<cp>\d+)")
ROK_RE = re.compile(r"\b(1[5-9]\d\d)\b")


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _val(node):
    """Hodnota uzlu ast jen pro konstanty a seznamy konstant (nic se nespouští)."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_val(x) for x in node.elts]
    return None


def _zaznam(node):
    """dict(n=…, f=[…]) nebo {'n': …} → slovník konstant, jinak None."""
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "dict":
        return {k.arg: _val(k.value) for k in node.keywords if k.arg}
    if isinstance(node, ast.Dict):
        return {_val(k): _val(v) for k, v in zip(node.keys, node.values) if isinstance(_val(k), str)}
    return None


KONCOVKY = [("ích", "e"), ("ích", "y"), ("ově", "ov"), ("ě", "a"), ("ě", ""), ("é", "á"), ("ou", "á"), ("u", ""),
            ("a", ""), ("y", "a"), ("i", "e"), ("i", "")]


def varianty(text):
    """Možné základní tvary skloněného názvu: „Dlouhé Lhoty“ → „Dlouhá Lhota“, „Hradci“ → „Hradec“…"""
    slova = text.split()
    out = [text]
    for z, n in KONCOVKY:
        nova = [w[: -len(z)] + n if w.endswith(z) and w[:1].isupper() and len(w) > len(z) + 2 else w for w in slova]
        v = " ".join(nova)
        if v not in out:
            out.append(v)
    return out


def najdi_ku(text, misto=None):
    """(název, [kandidáti k.ú.]) podle shody názvu. Je-li jich víc a mista.json má přibližný bod obce (lat/lon),
    vybere nejbližší k.ú. (bod z OpenStreetMap bývá nepřesný – proto jen výběr mezi stejnojmennými, ne „k.ú. v bodě“)."""
    for v in varianty(text):
        kand = ruian.ku(v)
        presne = [k for k in kand if k["ku"] == v or k["ku"].startswith(v + " u ") or k["obec"] == v]
        if presne:
            if len(presne) > 1 and misto and misto.get("lat") is not None:
                def vzd(k):
                    lat, lon = ruian.centroid(ruian.ku_geom(k["ku_kod"])["geometry"]["rings"])
                    return ruian.dist_m(misto["lat"], misto["lon"], lat, lon)
                presne.sort(key=vzd)
                if vzd(presne[0]) < 15000:
                    return v, presne[:1]
            return v, presne
    return text, []


def osoby(path):
    """Seznam (číslo, jméno, roky, [texty]) z osoby.py."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):  # P = {8: dict(...), …}
            for k, v in zip(node.keys, node.values):
                z = _zaznam(v)
                if z and z.get("n") and isinstance(_val(k), int):
                    out.append((_val(k), z))
        elif isinstance(node, ast.Call) and getattr(node.func, "id", "") == "dict":
            z = _zaznam(node)  # SIDE: dict(k=…, n=…, t=…)
            if z and z.get("n") and "k" in z:
                out.append((z.get("k"), z))
    res, videno = [], set()
    for num, z in out:
        key = (num, z.get("n"))
        if key in videno:
            continue
        videno.add(key)
        texty = [t for t in (z.get("f") or []) if isinstance(t, str)]
        texty += [t for t in (z.get("t"), z.get("note")) if isinstance(t, str)]
        res.append((num, z["n"], z.get("y") or "", texty))
    return res


def main(argv):
    if len(argv) < 3:
        print(__doc__); return
    proj, out = argv[1], argv[2]
    od = int(argv[argv.index("--od") + 1]) if "--od" in argv else 1700
    do = int(argv[argv.index("--do") + 1]) if "--do" in argv else 1925
    mista_p = os.path.join(proj, "data", "mista.json")
    mista = json.load(open(mista_p, encoding="utf-8")) if os.path.exists(mista_p) else {}
    pat = [(name, re.compile(e["re"])) for name, e in mista.items() if e.get("re")]

    def zaklad(text):
        for name, p in pat:
            if p.search(text):
                return name, True
        return text, False

    ku_cache = {}

    def normalizuj(text):
        """Skloněný text → (základní název, kandidáti k.ú., známá obec?)."""
        if text not in ku_cache:
            name, znamo = zaklad(text)
            try:
                nazev, kand = najdi_ku(name, mista.get(name))
            except Exception as ex:  # síť – ať se uloží aspoň zbytek
                print("  ruian:", ex); nazev, kand = name, []
            ku_cache[text] = (nazev if not znamo else name, kand, znamo or bool(kand))
        return ku_cache[text]

    zminky = {}
    for num, jmeno, roky, texty in osoby(os.path.join(proj, "data", "osoby.py")):
        for t in texty:
            for m in CP_RE.finditer(t):
                roky_t = [int(r) for r in ROK_RE.findall(t)] or [int(r) for r in ROK_RE.findall(roky)][:1]
                rok = min(roky_t) if roky_t else None
                if rok and not od <= rok <= do:
                    continue
                obec, kand, znamo = normalizuj(m.group("obec"))
                cp = int(m.group("cp"))
                z = zminky.setdefault((obec, cp), {"obec": obec, "cp": cp, "roky": set(), "osoby": [], "znamo": znamo,
                                                   "texty": [], "kand": kand})
                if rok:
                    z["roky"].add(rok)
                popis = f"{jmeno}" + (f" ({rok})" if rok else "")
                if popis not in z["osoby"]:
                    z["osoby"].append(popis)
                z["texty"].append(t[:120])

    data = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else []
    podle_id = {e["id"]: e for e in data}
    nove = upr = 0
    for (obec, cp), z in sorted(zminky.items(), key=lambda x: (x[0][0], x[0][1])):
        eid = f"{slug(obec)}-{cp}"
        e = podle_id.get(eid)
        if e is None:
            e = {"id": eid, "obec": obec, "cp": cp}
            data.append(e); podle_id[eid] = e; nove += 1
        else:
            upr += 1
        if z["roky"]:
            e["rok"] = min(z["roky"] | ({e["rok"]} if isinstance(e.get("rok"), int) else set()))
        stare = [o.strip() for o in (e.get("osoby") or "").split(";") if o.strip()]
        e["osoby"] = "; ".join(stare + [o for o in z["osoby"] if o not in stare])
        e["zdroj_rodokmen"] = z["texty"][:5]
        if not z["znamo"]:
            e["obec_overit"] = "název obce z textu – ověř základní tvar (není v mista.json ani v RÚIAN)"
        if "ku_kod" not in e:
            kand = z["kand"]
            if len(kand) == 1:
                e["ku_kod"] = kand[0]["ku_kod"]
            elif kand:
                e["ku_kandidati"] = [f"{k['ku_kod']} {k['ku']} (obec {k['obec']})" for k in kand[:8]]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"{out}: {nove} nových, {upr} doplněných adres ({len(zminky)} zmínek z rodokmenu, roky {od}–{do})")
    for e in data:
        if e["id"] in {f"{slug(o)}-{c}" for o, c in zminky}:
            stav = e.get("ku_kod") or ("? " + " | ".join(e.get("ku_kandidati", [])[:3]) if e.get("ku_kandidati") else "k.ú. nenalezeno")
            pozn = "  OVĚŘ NÁZEV" if e.get("obec_overit") else ""
            print(f"  {e['id']:<24} {e.get('rok', ''):<5} {stav}{pozn}")


if __name__ == "__main__":
    main(sys.argv)
