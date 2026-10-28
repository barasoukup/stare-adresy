---
name: stare-adresy
description: Geokodér starých adres z matrik 19. století – najde, kde stál dům „obec + číslo popisné“ podle indikačních skic a císařských otisků stabilního katastru (1824–1843) a porovná to s dnešním katastrem (RÚIAN). Výsledek jsou souřadnice s mírou jistoty, výřez skici a mapa. Použij, když se uživatel ptá „kde stál dům č.p. X v obci Y“, chce zanést domy předků z matrik do mapy, zjistit, jestli dnešní č.p. odpovídá tomu z matriky, nebo zmíní indikační skicu, stabilní katastr, císařský otisk. Funguje pro Čechy, Moravu i Slezsko.
---

# Staré adresy – kde stál dům předků

Matriky 18.–19. století uvádějí bydliště jako „obec + číslo popisné“. Dnešní č.p. často sedí, ale ne vždy:
domy zanikly, vesnice se přečíslovaly, číslo „putovalo“ s novostavbou. Tenhle skill zjistí polohu domu
**podle map stabilního katastru** (kolem roku 1840) a teprve pak ji porovná s dneškem.

**Složka skillu** (`SKILL_DIR`) je `${CLAUDE_SKILL_DIR}` – ukázal ti ji systém při načtení („Base directory“). Nástroje jsou v `tools/`,
podrobné návody v `reference/` – `skicy.md` (jak číst skicu a otisk v prohlížeči, **přečti před prvním čtením mapy**),
`zdroje.md` (služby ČÚZK, podmínky, kódy nalezených skic), `vystup.md` (formát výstupu pro jiné aplikace).

## Jak mluvit s uživatelem
Česky, stručně, bez žargonu (místo „st.p.“ poprvé „stavební parcela“). U každé adresy řekni výsledek jednou větou
(„Dům č.p. 23 stál kolem roku 1840 asi 70 m jihovýchodně od dnešního č.p. 23 – dnes je tam zahrada“) a míru jistoty.
„Nenašel jsem“ a „nejsem si jistý“ jsou plnohodnotné výsledky. Výřezy skic ukazuj – jsou krásné a přesvědčivé.

## Spouštění nástrojů
`python3 -I SKILL_DIR/tools/<nástroj>.py …` (Windows: `python -I -X utf8 …`; bez `-X utf8` se rozbije čeština).
Nástroje jsou jen standardní knihovna Pythonu ≥ 3.9 a volají veřejné služby ČÚZK (bez přihlášení).

| Nástroj | K čemu |
|---|---|
| `ruian.py ku "Obec"` | katastrální území (kód k.ú.) podle jména |
| `ruian.py cp <k.ú.> <č.p.>` | kde je **dnes** dům s tímto č.p. |
| `ruian.py st <k.ú.> <číslo>` | dnešní **stavební parcela** s číslem ze skici (střed, výměra, adresa na ní) |
| `ruian.py bod <lat> <lon>` / `bod --sjtsk X Y` | co je dnes v bodě (parcela, nejbližší adresy); S-JTSK = souřadnice z aplikace ČÚZK Archiv |
| `ruian.py okoli <lat> <lon> [m]` | stavební parcely a č.p. v okolí |
| `ruian.py kotva <k.ú.> <st.> X Y` | přesnost otisku: bod přečtený na otisku vs. dnešní parcela |
| `kotvy.py <k.ú.> <soubor.json>` | převod souřadnic prohlížeče skici ↔ mapa podle 3–5 kotev (stavební parcela `st`, nebo dnešní č.p. `cp` tam, kde jsou parcely přečíslované): kde na skice hledat dnešní parcelu/dům, nebo kde ve skutečnosti leží budova ze skici |
| `adresy.py nova/pridej/dopln/vypis <soubor.json>` | seznam adres a výpočet polohy (viz `adresy.py` bez parametrů) |
| `mapa.py <výstupní složka> <adresy.json>` | prezentační mapa pro uživatele (podklad ČÚZK, výřezy skic) – index.html + files.json k publikování + `domy.geojson` pro jiné aplikace |
| `z_rodokmenu.py <projekt rodokmenu> <adresy.json>` | načte adresy „obec čp. X“ z projektu skillu rodokmen (osoby.py, mista.json) |

## Odkud vzít adresy
- Uživatel je napíše (obec, č.p., rok, kdo tam žil).
- **Projekt skillu rodokmen** (složka s `data/osoby.py`): `z_rodokmenu.py <projekt> adresy.json` vytáhne všechny
  zmínky „obec čp. X“ (z celé doby; novodobé označí `novodobe`) i s osobami a roky a doplní katastrální území.
  Projekt rodokmenu nemění. Výsledek ukaž uživateli a projdi s ním položky `obec_overit` a `ku_kandidati` (nejasné
  obce, skloněné tvary jako „v Lhotách“ – sjednoť se základním tvarem, stejnojmenná k.ú.). Adresy bývají i jen
  v přepisech zápisů (bydliště snoubenců, dům porodu) a ne u osob – zeptej se, zda je projekt má u osob doplněné. Po hotovém
  geokódování mu řekni, že `domy.geojson` z `mapa.py` lze použít i v mapě rodinného webu (`reference/vystup.md`).

## Postup pro jednu adresu
Vstup: obec (jak je v matrice), č.p., rok zápisu, kdo tam žil. Ulož si ho hned: `adresy.py pridej adresy.json id=… obec=… cp=… rok=… osoby="…"`.

1. **Katastrální území.** `ruian.py ku "Nová Ves"` → kód. Matriční obec ≠ vždy dnešní obec: osady, německá jména
   („Neudorf“ = Nová Ves, „Böhmisch …“ = Česká …), k.ú. se často jmenuje s přívlastkem („Nová Ves u Města“)
   – hledej kratší začátek jména. **Víc obcí stejného jména** (běžné jméno vsi: i 14 k.ú.): vyber tu, která leží u farní
   obce nebo u jiných obcí z téže matriky – porovnej polohy (`ruian.py cp <k.ú.> 1` u kandidátů vs. známá obec), nehádej.
   Nejsi-li si jistý, zeptej se uživatele. Uživatel často uvede **farnost** (farní město), zatímco obce z matriky leží
   v jiných k.ú. s přívlastkem podle jiného města („Lhota u Jiného Města“) – hledej obec, ne farnost.
   U města zjisti, zda č.p. nepatří **předměstí** s vlastním číslováním (bývá samostatné k.ú. nebo samostatná skica).
   Doplň `ku_kod=`.
2. **Najdi skicu** – nejdřív v tabulce už nalezených skic (`reference/zdroje.md`), jinak v aplikaci ČÚZK Archiv; otevři
   ji v prohlížeči (postup a co dělat při výpadku aplikace v `reference/skicy.md`). Zapiš její ID (`skica=CHR…`)
   a rok vyhotovení (`skica_rok=`).
3. **Najdi dům na skice.** Běžné značení (skici Národního archivu): **černé číslo v budově = stavební parcela**,
   **červené číslo v budově nebo na dvoře = číslo popisné** (ne vždy je vepsané), „N° 23“ na zahradě a polích = patří
   k č.p. 23; ostatní červená čísla jsou pozemky. Na každé nové skice si klíč **nejdřív ověř na 2–3 domech**, které dnes
   mají stejné č.p. i st. parcelu (`ruian.py st`) – kraje se liší (`reference/skicy.md`, „Odchylky“).
   Přečti stavební parcelu (`stp=`) a **č.p., které na skice opravdu vidíš (`skica_cp=`)** – bez něj nástroj dá nejvýš B
   (shoda jen přes číslo parcely). Nejisté čtení zapiš do `cteni="…"` (ukáže se v mapě). Pak okolí (cesta, potok, kaple, sousední č.p.). Udělej výřez (`reference/skicy.md`).
   **Trojmístné číslo u budovy ve městě není automaticky parcela:** červené číslo ve dvoře nebo v budově vedle černého
   čísla stavební parcely je č.p., i když „vypadá“ jako číslo pozemku – vždy porovnej barvu a polohu s ověřenými sousedy.
   **Jména u polí** („N° 6 Novák Jos.“) jsou majitelé v době skici – výborná kontrola, že č.p. z matriky patří té rodině.
   **Ves chybí na skice svého k.ú.** (list ve skenu chybí, osada zakreslená na skice sousední obce): projdi skici
   sousedních k.ú. (`reference/skicy.md` §1) a císařský otisk – bývá úplnější.
   Při nejistotě čtení si přibliž víc, nehádej. **Kde hledat:** začni u dnešního domu se stejným č.p. (`ruian.py cp`)
   – často tam je; jinak čti sousední čísla, číslování jde obvykle po jedné straně vsi. Ve velké vsi nebo městě si
   nejdřív udělej kotvy (`kotvy.py`, `reference/skicy.md` §2b) – pak víš přesně, kam se na skice podívat.
4. **Spočítej polohu:** `adresy.py dopln adresy.json`. Nástroj zkusí v tomto pořadí:
   - stavební parcela dnes existuje, stojí na ní (nebo do 30 m) dům se stejným č.p. **a** č.p. jsi na skice přečetl
     (`skica_cp`) → **A**; bez přečteného č.p. jen **B** (shoda je jen přes číslo parcely),
   - parcela existuje, ale dnešní č.p. je jiné / žádné → **B** a výzva k ověření (číslo parcely mohlo být přiděleno znovu),
   - (u A se ukládá poloha dnešního adresního bodu domu; jinak střed parcely nebo bod z kotev / otisku),
   - parcela dnes neexistuje → poloha jen podle dnešního č.p. (**C**) s upozorněním → pokračuj krokem 5.
   U výsledku C nástroj řekne, na jaké parcele dnešní dům stojí: pozemková parcela (p.č.) = dům je mladší než katastr,
   starý stál jinde; vysoké číslo st. parcely = spíš novější stavba. **Novostavbu nástroj vyřadí sám:** stojí-li dnešní
   dům na st. parcele výrazně vyšší (> 2× a o > 500) než aspoň dva číselní sousedé (č.p. ±1…±3), je to číslo zbořeného
   domu přidělené znovu jinde – dnešní dům se nepoužije, bod je zatím uprostřed těch starých sousedů (**D**, metoda
   `sousede`) a výpis je vyjmenuje. Starý dům pak hledej na skice v jejich řadě (č.p. jdou ve městě po ulicích) – ne
   u dnešního domu. (Česká Třebová č.p. 93: dnes st. 1096 na Benešově, sousedé 91 a 95 na st. 404 a 390 u Tyršova nám.)
5. **Když parcela nesedí nebo zanikla: císařský otisk.** V aplikaci Archiv zapni vrstvu „Císařské otisky“ (je napasovaná
   na dnešní mapu, čísla stavebních parcel na ní jsou stejná jako na skice), najdi tutéž budovu a přečti souřadnice
   S-JTSK (`reference/skicy.md`). **Vždy ověř přesnost kotvou:** přečti stejně i sousední budovu, jejíž stavební
   parcela dnes existuje, a porovnej s `ruian.py st` – rozdíl (obvykle 5–20 m) zapiš jako `presnost_m=`. Pak
   `adresy.py pridej … sjtsk=X,Y` a znovu `dopln`. Výsledek **B** (A, pokud na bodě dnes stojí stejné č.p.).
   Rychlejší alternativa bez otisku: máš-li pro skicu kotvy, `kotvy.py` s položkou `body` spočítá polohu budovy
   přímo ze souřadnic skici (přesnost = chyba kotev, obvykle 5–15 m).
   Když je jisté, že dnešní dům s tímto č.p. je jiný (číslo předěleno) a starý dům jsi nenašel, zapiš
   `dnesni_cp=neplati` – v mapě pak bude jen obec (D), ne zavádějící bod.
6. **Porovnej s rokem.** Skica je z let 1824–1843. Zápis z matriky výrazně starší (před ~1805) nebo mladší (po ~1880)
   může mít jiné číslování – řekni to a navrhni ověření (rok skici vs. rok zápisu; sousední zápisy z matrik; pozemková kniha).
   **Adresy z 20. století** (zhruba po 1900) neber ze stabilního katastru: dům té doby obvykle stojí dodnes, takže
   výchozí je dnešní č.p. (`ruian.py cp`, ručně `jistota=A` po kontrole na ortofotu, že dům není novostavba).
   Skicu otevři jen tehdy, když dnešní dům s tímto číslem zjevně vznikl později (číslo přidělené znovu po zbourání,
   přečíslování obce) – i pak je skica spíš vodítko než doklad. Postup pro novodobé adresy viz níže
   („Adresy po roce ~1880“). Starší adresy (do ~1880) zkoušej přes skicu i tehdy, když dnešní č.p. nesedí.
7. **Výstup:** `adresy.py vypis` (přehled) a `mapa.py <složka> adresy.json` (prezentační mapa). Mapu zveřejni
   nástrojem Artifact: `file_path` = `<složka>/index.html`, `files` = obsah `<složka>/files.json` (podklady a výřezy).
   Stránka nesmí načítat cizí dlaždice, proto si podklady ČÚZK stahuje předem (potřebuje ImageMagick); hotová mapa
   má kolem 20 MB na 70 adres. Výřezy skic ukládej do `vyrezy/` vedle adresy.json (`vyrez=vyrezy/<id>.jpg`).
   Výstupní složku dej do pracovní složky projektu (Artifact přijímá jen soubory pod ní nebo ve scratchpadu);
   `<složka>/cache/` jsou stažené dlaždice – nepublikují se, `files.json` je nezahrnuje.
   Pro jiné aplikace (rodinný web) je `<složka>/domy.geojson` (formát `reference/vystup.md`). Čáry k dnešním domům se
   stejným č.p. jsou jen pro ladění (`mapa.py … --posuny`) – uživatele matou, posun je popsaný v textu u domu.

## Adresy po roce ~1880 (novodobé, `novodobe: true` ze `z_rodokmenu.py`)
Skica je pro ně stará; dům ale často stál ještě v 1. polovině 20. století a pomohou pozdější zdroje:
1. **Dnešní č.p.** (`ruian.py cp`) → zatím **C**, jen když dům není novostavba (viz krok 4 – vyřazená novostavba platí
   i tady: hledej v řadě sousedů nebo v adresáři). Ve městech s ulicemi zápis často uvádí i ulici („Nádražní ul.“).
2. **Adresář města** z doby kolem zápisu (Adressbuch, Adresář). Obsahuje (a) **seznam domů podle č.p.** po částech
   města s ulicí a majitelem a (b) **seznam ulic s čísly popisnými**. Ztotožnění ulice: vezmi z adresáře *ostatní* č.p.
   téže staré ulice a podívej se, kde dnes stojí (`ruian.py cp`) – stojí-li většina v jedné dnešní ulici, je to ona
   (přejmenování). Dnešní dům se stejným č.p. ve stejné (přejmenované) ulici → **A**; dům zanikl → bod na místě v té
   ulici (**B/C** podle opory) a zdroj do `poznamka`. Kde adresáře hledat: `reference/zdroje.md`.
3. **Dům dnes neexistuje:** neumisťuj ho jen podle mezery v číselné řadě. Zkontroluj strukturu dnešní katastrální mapy:
   zbořená řada domů zanechá úzké parcely domů a zahrádek; velký nepravidelný pozemek tam řadu nepodporuje. Bez opory
   zůstává **D** (jen obec) s vysvětlením.
4. **Co nepomáhá** (ověřeno 27. 10. 2026): Státní mapa 1 : 5 000 (vydání 1951–1988) a Mapa evidence nemovitostí mají
   jen obrysy a čísla parcel, **ne č.p.**; samostatné listy císařského otisku (`openmap.html?typ=cioc…`) jsou stav
   ~1840 bez dodatků. Pozdější revize skic (reambulace 1869–1881) má jen část k.ú. – v seznamu skic v aplikaci Archiv
   je pak druhý kód s jiným rokem (např. `…018720`).

## Místa, kde známe jen obec
Uživatelé chtějí v mapě i předky, u nichž je jen obec bez č.p. („rodem z Nové Vsi“). Zapiš je jako samostatný záznam
`id=<obec>-obec obec=…` bez `cp`, `ku_kod=…`, `lat/lon` = střed k.ú., `metoda=obec jistota=D` a v `osoby` všechny lidi
z té obce (jeden bod na obec). Nezdvojuj obec, kde už dům téže osoby je. Nejisté obce (s „(?)“, nejasné ztotožnění,
mimo ČR) do mapy nedávej – vypiš je uživateli k rozhodnutí.

## Míra jistoty (pole `jistota`)
- **A** – č.p. přečtené na skice a dnešní dům s tímto č.p. stojí na téže parcele nebo do 30 m (nebo ručně potvrzeno).
- **B** – poloha ze skici / otisku, ale dnešní stav je jiný (dům zanikl, číslo se přesunulo). Uveď přesnost.
- **C** – jen dnešní č.p., skica nepřečtena. Platí často, ale není to doklad.
- **D** – jen obec (střed k.ú.), nebo jen část obce (osada, předměstí – bod na popisu části v mapě, `presnost_m`).

**Víc částí obce v jednom k.ú.** (ves + osady se stejnými č.p.): `dopln` vybírá adresu podle jména v poli `obec`
(„Osada 6, … Obec“ vs. „č.p. 6, … Obec“). Pojmenuj `obec` jako dnešní část obce; když nástroj napíše „NEJSPÍŠ JINÁ
ČÁST OBCE“, dnešní č.p. patří jiné osadě – nepoužívej ho (`dnesni_cp=neplati`).
Města s vlastním číslováním čtvrtí (Vnitřní Město, předměstí – např. Domažlice mají č.p. 97 pětkrát): přečti v zápisu,
kterou část uvádí („č. 97 město“), a zadej ji `cast="Město"` – `dopln` pak vybere adresu „…, Město, …“.

## Co zapsat k adrese (`adresy.json`)
`id, obec, cp, rok, osoby, ku_kod, skica, skica_rok, stp, skica_cp, cteni, sjtsk, bod, presnost_m, vyrez, poznamka`
– zbytek (`lat, lon, metoda, jistota, dnes, zjisteni`) doplní `dopln`; v `dnes` je i poloha dnešního domu se stejným
č.p. (`cp_lat`, `cp_lon`, `cp_vzdalenost_m`), když je jinde – mapa ho spojí čárkovanou čarou. Ruční poloha: `lat=… lon=… metoda=ručně jistota=A`.

## Víc adres najednou
Postupuj po obcích (jedna skica = jedna obec). Skici procházej v jednom vlákně – vestavěný prohlížeč se překresluje
jen v kartě vpředu, takže souběžní pomocníci se blokují. Pomocníky lze použít na přípravu (k.ú., dnešní polohy,
otisk), ne na souběžné čtení skic. Čas: je-li kód skici známý, ves se 3 adresami zabere ~10 minut; hledání domů,
jejichž č.p. dnes neplatí, ve velké vsi nebo městě i hodinu.

## Hranice a podmínky ČÚZK (ověřeno 25. 10. 2026, podrobně `reference/zdroje.md`)
- **Síťové služby ČÚZK** (RÚIAN, mapové podklady, prohlížení v aplikaci Archiv) jsou zdarma, i komerčně, „pokud rozsah
  užití není na újmu poskytovatele“. Kdo **přetěžuje infrastrukturu, může být technicky zablokován**. Proto:
  - skici čti **v jednom vlákně**, nikdy víc pomocníků najednou v aplikaci Archiv; mezi kroky nech stránku dokreslit,
    neopakuj načítání ve smyčce; po práci kartu zavři,
  - `ruian.py` a `mapa.py` volej po rozumných dávkách (desítky adres, ne tisíce); `mapa.py` si dlaždice ukládá do cache.
- **Skici a otisky** jsou v aplikaci za přístupovým klíčem pro jejich vlastní aplikaci – **čti je jen v prohlížeči jako
  člověk**, klíč neobcházej, služby `arcgis4` nevolej skripty, nic hromadně nestahuj. Ovládat pohled skriptem uvnitř
  otevřené stránky (`view.center`, `view.scale`) je v pořádku – je to totéž jako posun myší.
- **Archiválie (data ÚAZK)** se jako soubory poskytují jen přes E-shop za úplatu (Zásady ZÚ 2026, čl. 3). Prohlížení
  je zdarma; výřez ze snímku obrazovky ber jako **badatelskou kopii pro vlastní potřebu**. Indikační skici patří
  archivům (Čechy Národní archiv, Morava MZA, Slezsko ZA Opava).
- **Zveřejnění:** soukromá mapa pro rodinu je v pořádku. Na veřejný web výřezy skic jen s citací („Národní archiv,
  Indikační skici, CHR473018390; ČÚZK – on-line, Archiv“), u větší publikace (kniha, článek, tisk) doporuč požádat
  archiv o souhlas / objednat kvalitní sken. Podklady ČÚZK (ZTM, ortofoto, RÚIAN) jsou otevřená data CC BY 4.0 – vždy
  uveď „ČÚZK“ (u služeb „ČÚZK – on-line“). `mapa.py` to do mapy píše sám.
- Kdo dům vlastnil, skica neřekne (jen č.p.). To je v písemném operátu a pozemkových knihách (archiv).
