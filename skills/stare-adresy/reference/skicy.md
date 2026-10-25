# Jak číst indikační skicu a císařský otisk

Obojí je v mapové aplikaci **ČÚZK Archiv** – https://ags.cuzk.gov.cz/archiv/ . Otevírej ji ve vestavěném prohlížeči
(nástroje `mcp__Claude_Browser__*`, jinak Claude in Chrome). Čti po obrazovkách jako člověk; nic nestahuj hromadně.

**Než začneš:** zobraz panel prohlížeče – nástroj `mcp__ccd_view__show_pane` s `pane="preview"` (bývá odložený: načti
ho nejdřív přes ToolSearch `select:mcp__ccd_view__show_pane`), jinak požádej uživatele o Ctrl+Shift+B / Cmd+Shift+B. Skrytý panel nekreslí: skripty čekají do vypršení, snímky selhávají („page did not
finish rendering“). Měj otevřenou jen jednu kartu ČÚZK – druhá karta té první bere vykreslování.

**Který prohlížeč:** vestavěný panel bývá nízký (např. 900 × 350 px) – při čitelném měřítku je vidět jen pár domů
a `resize_window` mapu ArcGIS nezvětší (překreslí se do rohu). Claude in Chrome dá celé okno (1500 × 900) a čte se
mnohem rychleji; u některých skic (velká městská skica) ale Chrome při snímku obrazovky zamrzá („renderer frozen“,
stránka jinak běží) – pak přepni zpět do vestavěného panelu a požádej uživatele, ať ho zvětší. Okno Chromu musí být
vpředu, jinak snímky selhávají taky.

**Výpadek aplikace:** když panel „Výsledky“ po kliknutí do mapy ani po ~30 s neukáže počty a jen opakuje „Chvilku
strpení…“ (v konzoli `Failed to load layer 'Klady'`, dotazy vrací 499 Token Required), je problém na straně ČÚZK
(stalo se 25. 10. 2026 po celodenní práci – možná omezení počtu dotazů). Postup: 1) zkus kód skici v tabulce
v `zdroje.md` a prohlížeč `openmap.html` – ten bývá funkční i tehdy; 2) když kód neznáš, zapiš adresy jako C s poznámkou
„skica neověřena – aplikace ČÚZK nedostupná“, řekni to uživateli a nabídni pokračování později. Klíč neobcházej.

## 1. Najít skicu katastrálního území
1. Do pole „Najít adresu nebo místo“ napiš název k.ú. nebo dnešní adresu **i s PSČ** a vyber z nabídky položku
   se správným PSČ a obcí. Bez PSČ vyhledávání klidně skočí jinam („Lhota 18“ našlo ulici Lhota v jiném
   městě). U obcí bez ulic piš ve tvaru „č.p. 18, 56002 Lhota“. Zavři okénko „Výsledek vyhledávání“ (křížek).
2. Klikni do mapy uvnitř obce → vpravo panel „Výsledky“ s počty archiválií. Klikni na **Indikační skici**.
3. Objeví se karta „<číslo>-1 <obec> - dříve <německé jméno>“ s kódem (např. `CHR473018390`). Klik na náhled otevírá novou kartu, kterou
   prohlížeč může zablokovat – otevři ji proto přímo:
   `https://ags.cuzk.gov.cz/archiv/openmap.html?typ=skicic&idrastru=<KÓD>`
   (odkaz najdeš i skriptem: `[...document.querySelectorAll('a[href*=openmap]')].map(a=>a.href)`).
   Pro Slezsko je typ `skicis`. **Morava:** karta neodkazuje na `openmap`, ale na prohlížeč MZA
   `https://www.mza.cz/indikacniskici/skica/detail/MOR…` (rok je přímo v hlavičce stránky). Je to OpenSeadragon:
   instance `window.dragon`, `dragon.setFullPage(true)` ho roztáhne; přiblížení na místo
   `dragon.viewport.fitBounds(dragon.world.getItemAt(0).imageToViewportRectangle(x, y, w, h))` v pixelech obrázku
   (osa y dolů). Ves bývá na zvláštním listu ve větším měřítku. Značky jsou stejné jako v Čechách.
   **Rychle pro víc obcí najednou:** v hlavní aplikaci nastav pohled skriptem na obec (§2 „Pohyb skriptem“, S-JTSK z
   `ruian.py sjtsk <lat> <lon>`), klikni do mapy, počkej, až zmizí „Chvilku strpení…“, klikni na tlačítko
   Indikační skici (`calcite-button#btn_skicic` – tlačítko existuje až po skončení „Chvilku strpení…“) a vyčti odkazy
   `a[href*=openmap]`. Každý nový kód zapiš do tabulky v `zdroje.md`, ať se příště nemusí hledat.
4. Rok skici je na titulním listu (levý horní list, „…1838“). Kód ho obsahuje: prefix kraje + číslo + **rok** + 0
   (CHR3600**1838**0, HRA4470**1840**0, KRM3460**1841**0, MOR1169**1834**0) – u důležitých adres ověř na titulním listu.
   „Informace o archiválii…“ rok neuvádí.
5. Jedno k.ú. může mít víc skic (dvě části, předměstí) – projdi všechny karty.
6. **Města:** zastavěná část (intravilán) bývá na **zvláštních listech ve větším měřítku**, v prohlížeči jako samostatný
   blok listů stranou (často vlevo dole, s německým jménem města). Na hlavních listech je na místě
   města prázdné místo.

## 2. Číst skicu
- Prohlížeč skládá listy vedle sebe; souřadnice v něm **nejsou skutečné** (jen pozice listů). Sever je nahoře.
- **Ovládání:**
  - přibližuj kolečkem (`computer` → `scroll` up, 2–5 kroků) **přímo nad cílem** – bod pod kurzorem zůstane na místě;
    po každém kroku počkej 4–7 s na načtení,
  - **netahej myší** (tažení „odletí“ daleko mimo skicu) a **neklikej do skici** (kliknutí označí list pro nákup
    v e-shopu; druhé kliknutí výběr zruší). Šipky na klávesnici posunou jen o kousek,
  - když je cíl u okraje obrazovky: oddal kolečkem (scroll down) nad **opačným** okrajem – cíl se posune ke středu –
    a pak přibliž nad cílem. Ztratíš-li se, domeček vlevo nahoře vrátí celý pohled,
  - čísla jsou čitelná při `view.scale` asi 2300–4700 (statek má na obrazovce 60–100 px); při větším přiblížení
    (1200–1600) se už jen zvětšuje rozmazaný sken. `zoom` v nástroji jen ořízne snímek (nezvětší).
  - **měřítko má pevné stupně** podle skici (např. 4731 / 2365 / 1182 nebo 5677 / 2838): nastavené `v.scale` přeskočí
    na nejbližší stupeň. Skutečné `v.scale` čti až po načtení a pixely převáděj na souřadnice až potom,
  - **po otevření `openmap.html` je ~5–15 s bílá plocha**, než se načte první obrázek – počkej, neklikej.
- **Pohyb skriptem** (rychlejší než kolečko, hlavně ve městě): `view.goTo()` se často nedokončí. Spolehlivé je
  ```js
  const v=document.querySelector('arcgis-map').view; v.scale=2838;
  v.center={type:'point',x:9140,y:-35650,spatialReference:v.spatialReference};
  ```
  Prohlížeč skici je **jeden obrázek pro celý výřez** (ne dlaždice): po skoku skriptem se nový obrázek někdy nenačte
  (zůstane rozmazaný nebo bílý). Pomůže kliknout na „+“/„−“ (`button[aria-label=Přiblížit]`), nebo stránku znovu
  načíst a pohled nastavit hned po `await v.when()`. **Bílá plocha s modrými okraji listů nemusí znamenat prázdno** –
  může jen nebýt načtená. Pohled převáděj na souřadnice až když `v.stationary` je true.
- **Snímek obrazovky kolísá** (800×600, 640×480 vložený do rámce, jindy výřez 1:1). Před každým přepočtem pixelů na
  souřadnice zkontroluj skutečnou velikost snímku (je uvedená ve výsledku) a `k = innerWidth / šířka snímku`;
  chybný poměr dal jednou chybu 50 m. Snímek s `scale` < 1 mění rámec dalšího snímku – raději nepoužívat.
- **Prohlížeč se překresluje jen v kartě, která je vpředu, a jen když je panel prohlížeče zobrazený.** Víc pomocníků
  v jednom prohlížeči se navzájem blokuje (polovina snímků selže) – skici procházej v jednom vlákně. Je to i otázka
  ohleduplnosti: podmínky ČÚZK dovolují zablokovat toho, kdo služby přetěžuje (SKILL.md, Hranice).
- **Značky na skice** (ověřeno na několika skicách Národního archivu z Chrudimského kraje):
  - budova: žlutá = dřevěná, růžová/červená = zděná,
  - **černé číslo v budově = stavební parcela**, **červené číslo v budově = číslo popisné** (vepsané bývá u většiny
    domů; v některých vsích jen u některých),
  - **„N° 23“** (černě, ručně) na zahradě, dvoře nebo poli = parcela patří k **domu č.p. 23**; u polí často i jméno
    majitele („Novak Franz N° 74“),
  - ostatní **červená čísla** = pozemkové parcely (pole, zahrady, louky, cesty),
  - velká písmena B, D, E … = trati, tučné jméno (německé jméno vsi) = obec, jména sousedních obcí na okraji,
  - modré kroužky a čísla tužkou (šedá, tenká, často škrtnutá) = pozdější úpravy a revize, nečti je jako č.p.;
    vybledlé, ale **perem psané** červené číslo ve stejném rukopisu jako sousední č.p. je původní – pomůže, když
    zapadá do řady sousedních č.p. a dnešní dům na místě nese totéž číslo,
  - **dvě červená čísla v jedné budově** (např. 409 a menší 450) = pozdější přečíslování; zapiš obě,
  - **budovy dokreslené později** (v jedné vsi st. 60–64, dnes č.p. 50–53): mívají vyšší čísla st. parcel a žádné č.p.;
    shoda dnešního č.p. s takovou parcelou neznamená, že dům na skice to číslo měl.
- **Než začneš číst, ověř si klíč na dvou třech domech**, které dnes mají stejné č.p. i st. parcelu (`ruian.py st`).
  V jedné vsi to zprvu vypadalo, že červená čísla jsou pozemky, ale st. 21/22/24/25 = č.p. 22/23/25/26 sedí s dneškem –
  červené číslo u budovy je č.p. (a „7“ v rukopisu bývá ve skutečnosti „2“).
- **Odchylky:** na kouřimské skice (KRM) jsou červená čísla v zahradách **pozemkové parcely**, č.p. je jen
  ve dvoře u černého čísla st. parcely. Ve městech bývá červené č.p. psané podél budovy, i vzhůru nohama.
- **Hledání č.p. ve městě:** č.p. jdou v souvislých řadách podél ulic. Řadu sleduj přes „N° X“ na zahradách při
  `scale` ~5700, pak přibliž na ~2800. Rychlý předtest přes otisk: stála na místě dnešního domu v roce ~1840 budova
  se stejným číslem st. parcely? Když je tam pole, dům je mladší než skica a dnešní č.p. je jediná stopa (C).
- **Číslo na okraji listu:** sousední listy se na okrajích překrývají – budova u okraje bývá nakreslená na obou.
  Přečti ji na obou a výsledky spoj (st. 56 na dvou listech, na každém půlka čísla).
- **Vybledlé červené číslo** zvýrazni na snímku – vždy na snímku v čitelném měřítku (2300–4700), z rozmazaného
  snímku při ~1200 zvýraznění nic nevytáhne:
  `magick <snímek.jpg> -crop 200x200+x+y +repage -resize 250% -modulate 100,260 -sigmoidal-contrast 6x50% <výstup.png>`
  (zesílí sytost a kontrast, červená vystoupí). I tak je to čtení „nejisté“ – zapiš do `cteni=`.
- Když je víc budov se stejným „N°“ (stodola, výměnek), dům je obvykle ta s červeným č.p., u cesty nebo zděná.
- U čtení si piš i sousedy (č.p. a stavební parcely vedle). Slouží jako kotvy a kontrola.

## 2b. Kotvy – kde na skice hledat a kde budova ve skutečnosti leží
Každý list skici má v prohlížeči vlastní měřítko a natočení (sousední listy jedné skici 0,233 a 0,253 m na jednotku; natočení
1–2°, jinde i 6–14°). **Kotvy ber ze stejného listu jako cíl** a kolem něj, nikdy přes spoj listů – jinak chyby
vyskočí na desítky metrů. Na spoji listů bývá mezera a
budovy rozříznuté. Body spočtené z kotev zapisuj `sjtsk=X,Y bod=kotvy`.
1. Přečti na skice 3–5 budov, jejichž stavební parcela **dnes existuje** (`ruian.py st <k.ú.> <číslo>`; nejlépe malé
   parcely – u velkých je střed daleko od budovy). Kotvy rozlož do okolí cíle. **Nejlepší kotvy** jsou budovy, u nichž
   jsi na skice přečetl i č.p. a to sedí s dnešním č.p. na téže parcele – číslo parcely mohlo být přiděleno znovu
   jinde (v jednom případě chyba 66 m). Parcela s lomítkem (`st. 5` → dnes `5/1`, `5/2`) se bere jako průměr dílů.
2. Souřadnice prohlížeče skici zjistíš stejným skriptem jako u otisku (§3 bod 4) – v prohlížeči skici vrací
   souřadnice listů (např. `[8183.96, -32617.1]`).
3. Zapiš do JSON a spusť `kotvy.py <k.ú.> kotvy.json`:
   ```json
   {"kotvy": [{"st": "89", "skica": [8183.96, -32617.1]}, {"st": "91", "skica": [8330.08, -33124.69]}],
    "hledej": [{"id": "dnes-221", "st": "157"}],
    "body": [{"id": "cp-19", "skica": [x, y]}]}
   ```
   Výstup: chyba každé kotvy (vyřaď tu s chybou > 2× ostatní), kde na skice leží dnešní parcela (`hledej`) a kde ve
   skutečnosti leží bod ze skici (`body`, WGS84 + S-JTSK pro `sjtsk=`).
4. Kde je bod `hledej` na obrazovce:
   ```js
   const v=document.querySelector('arcgis-map').view, k=innerWidth/800;
   const s=v.toScreen({type:'point',x:9140,y:-35650,spatialReference:v.spatialReference}); [s.x/k, s.y/k]
   ```
   Je-li mimo obrazovku (y > 600), oddal nad horním okrajem a zkus znovu; pak přibliž kolečkem přímo nad ním.

### Výřez skici
Snímek obrazovky se uloží jako soubor (cesta je ve výsledku nástroje). Ořízni ho ImageMagickem:
`magick <snímek.jpg> -crop 300x220+250+300 +repage vyrezy/<id>.jpg` (šířka×výška+x+y v pixelech snímku 800×600).
Pod výřez vždy zdroj: „Národní archiv, Indikační skici, <kód>, kolem <rok>“.

### Hledání ve městě – „sleduj řadu“
Konskripční čísla jdou ve městě v souvislých řadách podél ulic (např. 103 → 116 na západ, 134 → 151 → 165
→ 176 zpět na východ). Najdi známé číslo poblíž, přečti 2–3 sousedy, urči směr a posouvej pohled po řadě
(`v.center` o kus dál ve směru řady, pak „−“ a „+“ pro načtení). Pole „N° X Jméno“ na okrajích ukazují, kam řada
pokračuje. Takhle se dá dojít k domu i přes 60 čísel za ~10 obrazovek.
- **Kotvy podle dnešních č.p.:** kde se čísla st. parcel nezachovala (k.ú. nově zmapované), vezmi za kotvy domy, jejichž č.p. na
  skice přečteš a dnes stojí na stejném místě, a zapiš je do `kotvy.py` klíčem `"cp"` místo `"st"`
  (`{"cp": 269, "skica": [x, y]}`; poloha = dnešní adresní bod). I `hledej` umí `"cp"` – ukáže, kde na skice leží dnešní
  dům s tím číslem. Domy, jejichž dnešní č.p. je jinde (číslo přidělené znovu novostavbě), vynech – poznáš je podle velké chyby kotvy
  nebo podle toho, že dnešní dům leží úplně jinde než jeho sousedé ze skice. Kotvy ber z téhož listu jako cíl.
- **„Dnešní dům stojí na pozemkové parcele“ neznamená vždy nový dům:** v k.ú. s přečíslovanými parcelami stojí
  na p.č. i domy z doby skici. V jednom městě stály takové domy 3–8 m od dnešních domů se stejným číslem. `adresy.py` to pozná
  podle sousedních č.p. a upozorní; rozhodne skica.
- **Čísla se ve městech přidělovala znovu:** zaniklý dům předá číslo novostavbě i 500–1000 m daleko (ve dvou zkoumaných městech
  i v jedné vsi se to stalo opakovaně). U měst proto dnešní č.p. bez skici skoro nic neznamená.

## 3. Císařský otisk – poloha v dnešní mapě
Otisk = barevná kopie téže mapy, **napasovaná na dnešní souřadnice**. Má stejná čísla stavebních parcel, často bez č.p.
1. V hlavní aplikaci vyhledej adresu poblíž, zavři okénko výsledku.
2. Pravý panel, ikona **+ („Doplňky“)** → „Celoplošné vrstvy“ → přepni **Císařské otisky** (kliknutí na popisek;
   `find "Císařské otisky"` dá odkaz). Zavři panel.
3. Přibliž, až čteš čísla budov (měřítko ~1 : 2 000, `view.scale` ≈ 1890). Najdi budovu se stavební parcelou ze skici.
4. Souřadnice bodu na obrazovce zjistíš skriptem. **Pozor: snímek obrazovky je zmenšený** (stránka má obvykle 1024 px,
   snímek 800 px) a mapa nezačíná na horním okraji – proto přepočet:
   ```js
   const v=document.querySelector('arcgis-map').view, r=v.container.getBoundingClientRect(), k=innerWidth/800;
   const at=(sx,sy)=>{const p=v.toMap({x:sx*k-r.left,y:sy*k-r.top});return [Math.round(p.x*10)/10,Math.round(p.y*10)/10]};
   ({dum: at(337,318), kotva: at(145,430)})   // pixely ze snímku obrazovky 800×600
   ```
   Výsledek je S-JTSK (záporná čísla, např. `[-605383.4, -1081450.4]`).
   (`k` počítej ze skutečné šířky snímku – je uvedená u každého snímku.)
5. **Kotva = kontrola přesnosti.** Stejně přečti střed sousední budovy, jejíž stavební parcela dnes existuje
   a nese stejné č.p.: `ruian.py kotva <k.ú.> <st.> X Y` vypíše vzdálenost od středu dnešní parcely a zda bod
   leží uvnitř. To je přesnost (ve vsích obvykle 3–13 m). Je-li kotva posunutá o víc než
   ~25 m stejným směrem jako okolí, odečti ten posun i od hledaného domu a napiš to do poznámky.
6. `adresy.py pridej adresy.json id=… sjtsk=X,Y presnost_m=10` → `adresy.py dopln adresy.json`.

**Otisk nemusí pokrývat každé k.ú.** (některá k.ú.: vrstva je zapnutá, ale nekreslí nic – aplikace si stáhne jen popis
vrstvy). Pak zbývají kotvy na skice.

## 4. Kontrola dnešní mapou
`ruian.py okoli <lat> <lon> 60` vypíše stavební parcely a č.p. kolem. Pomáhá poznat, že dům „přeskočil“
(stejné číslo dnes o kus dál), nebo že na místě dnes stojí jiné č.p.

## Časté pasti
- **Rok:** skici 1824–1843 (Čechy kolem 1838–1842). Konskripční číslování od 1770/71, v mnoha vsích přečíslováno
  kolem 1805–1806 a znovu při růstu obce. Matriční zápis z 1790 může mít jiné č.p. než skica.
- **Město × předměstí:** města měla často oddělená číslování (vnitřní město, předměstí); zkontroluj, ke které skice
  a k.ú. adresa patří.
- **Číslo evidenční** (č.ev., chaty) není číslo popisné – nástroj je od č.p. odlišuje.
- **Víc adres se stejným č.p. v jednom k.ú.** (osada s vlastním číslováním × sousední ves): nástroj dá přednost adrese, která obsahuje
  jméno obce z pole `obec` – pojmenuj `obec` tak, jak se jmenuje dnešní část obce.
- **K.ú. bez starých čísel st. parcel** (dnešní parcely přečíslované) – kotvy se stavebními parcelami nejdou; použij
  v `kotvy.py` kotvy podle dnešních č.p. (klíč `cp`) – dnešní adresní body domů, které na skice přečteš i s č.p., nebo použij otisk.
- **Rozdělené parcely** (`st. 2/1`, `2/2`): původní st. 2 se později rozdělila; dům 1840 je některá z částí –
  rozhodni podle tvaru na otisku.
- Dnešní parcela stejného čísla, ale na úplně jiném místě = číslo bylo přiděleno znovu (k.ú. prošlo novým mapováním).
