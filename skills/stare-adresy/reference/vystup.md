# Výstup pro jiné aplikace (např. web ze skillu rodokmen)

`mapa.py` ukládá vedle mapy soubor **`domy.geojson`** – GeoJSON FeatureCollection, jeden bod (WGS84, `[lon, lat]`)
na každou adresu s polohou. Je to jediné rozhraní mezi tímto skillem a jinými nástroji: kdo ho čte, nepotřebuje
znát vnitřek skillu, a skill nesahá do cizích projektů.

Vlastnosti bodu (`properties`), chybějící hodnoty se vynechávají:

| pole | význam |
|---|---|
| `id` | klíč adresy (`nova-ves-46`) |
| `obec`, `cp` | obec a číslo popisné, jak je v matrice; bez `cp` = předek, u něhož známe jen obec (jistota D, bod obce) |
| `rok` | rok zápisu v matrice (nejstarší) |
| `osoby` | kdo tam žil (text) |
| `jistota` | `A` jistá poloha · `B` podle skici, dnes jinak / č.p. nepřečteno · `C` jen dnešní č.p. · `D` jen obec |
| `metoda` | `stp` stavební parcela, `otisk`, `kotvy`, `dnesni_cp`, `obec`, `ručně` |
| `skica`, `skica_rok`, `skica_url` | kód indikační skici, rok, odkaz na prohlížeč (ČÚZK Archiv / MZA) |
| `stp` | stavební parcela na skice |
| `cteni` | upozornění na nejisté čtení |
| `vyrez` | relativní cesta k výřezu skici (`vyrezy/<id>.jpg`, vedle adresy.json) |
| `poznamka` | slovní popis pro člověka |
| `presnost_m` | odhad přesnosti polohy |
| `dnes_na_miste` | dnešní adresy na tomtéž místě |
| `dnesni_cp_jinde_m` | dnešní dům se stejným č.p. stojí jinde – o kolik metrů (číslo bylo přeneseno) |

Doporučení pro zobrazení: barva podle `jistota`; `D` (jen obec) kreslit jako obec, ne jako dům; u výřezu uvést zdroj
(„Národní archiv, Indikační skici, <skica>; ČÚZK – on-line“). Podklad map ČÚZK uvádět „ČÚZK“.

**Vstup ze skillu rodokmen:** `z_rodokmenu.py <projekt> adresy.json` načte zmínky „obec čp. X“ z `data/osoby.py`
(bez spuštění souboru) a skloněné názvy převede podle `data/mista.json`. Projekt rodokmenu nemění.
