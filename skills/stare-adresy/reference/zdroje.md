# Zdroje a služby (ověřeno 25. 10. 2026)

| Co | Kde | Přístup |
|---|---|---|
| Dnešní parcely, adresy, k.ú. (RÚIAN) | `https://ags.cuzk.gov.cz/arcgis/rest/services/RUIAN/MapServer` – vrstvy 1 AdresniMisto, 5 Parcela, 7 KatastralniUzemi, 12 Obec | veřejné REST `query`, bez klíče |
| Převod S-JTSK ↔ WGS84 | `https://ags.cuzk.gov.cz/arcgis/rest/services/Utilities/Geometry/GeometryServer/project` (5514 ↔ 4326) | veřejné |
| Indikační skici (Čechy NA, Morava MZA, Slezsko ZA Opava) | aplikace https://ags.cuzk.gov.cz/archiv/ , prohlížeč `archiv/openmap.html?typ=skicic&idrastru=<kód>` | jen přes aplikaci (služba `arcgis4/…/Archiv/*` chce token aplikace – **neobcházet**) |
| Císařské otisky napasované | tamtéž, vrstva „Císařské otisky“ (`archiv_spojene_cisarske_otisky`) | jen přes aplikaci |
| Indikační skici Moravy | https://www.mza.cz/indikacniskici/ | veřejný prohlížeč MZA |
| Dnešní katastrální mapa (podklad do mapy) | WMS `https://services.cuzk.gov.cz/wms/local-km-wms.asp`, vrstva `KN` | veřejné |
| Podkladové dlaždice | `https://ags.cuzk.gov.cz/arcgis1/rest/services/ZTM_WM/MapServer/tile/{z}/{y}/{x}` a `ORTOFOTO_WM` | veřejné |

Pole RÚIAN, která nástroje používají: Parcela `kmenovecislo`, `poddelenicisla`, `druhcislovanikod` (1 = stavební
parcela „st.“, 2 = pozemková), `katastralniuzemi`, `vymeraparcely`; AdresniMisto `cislodomovni`, `adresa`
(„Nová Ves 46, 56002 Město“, u čísel evidenčních „č.ev.“).

## Už nalezené indikační skici (kód pro `openmap.html?typ=skicic&idrastru=<kód>`)
| k.ú. (kód) | skica | rok | poznámka |
|---|---|---|---|
| Svinná u České Třebové (671703) | CHR473018390 | 1839 | |
| Přívrat (736384) | CHR360018380 | 1838 | |
| Česká Třebová (621757) | CHR490018390 | 1839 | město na zvláštních listech vlevo dole; okolí Nového náměstí (č.p. 168–176) v prohlížeči kolem x 3300–4800, y −32600…−33200 (dva listy, nepřekrývají se); č.p. 89–95 na západní straně dnešního Tyršova nám. (st. 390–406) x 4100–4900, y −28400…−29700; sv. Kateřina / U Kostelíčka (č.p. 315 = st. 477) x 9700–10300, y −29400…−29800. Čísla po městě nejdou v řadě (314 u náměstí, 315 u sv. Kateřiny, 322 na Litomyšlské) |
| Parník (621820) | CHR318018390 | 1839 | č.p. se jen zčásti zachovala: st. 53 = č.p. 45, st. 50 = č.p. 75 jako dnes, ale v horní části (J. Pácla) st. 64 = č.p. 9 (dnes 632), st. 65 = č.p. 8 (dnes 83) – přečíslováno po 1839 |
| Kozlov u České Třebové (671690) | CHR210018390 | 1839 | ves na rohu listů |
| Dlouhá Třebová (626503) | CHR226018390 | 1839 | otisk tu nenačítá |
| Řetová (745359) | CHR379018390 | 1839 | „Gross Ritte“ |
| Vlčkov (783838) | CHR526018390 | 1839 | |
| Hylváty (775339) | CHR139018390 | 1839 | |
| Předměstí (734322) – i Dolní Lhota | CHR355018390 | 1839 | víc osad na jedné skice; Studenec („Studenetz“, st. 67 = dnes č.p. 6) kolem x 11700–12900, y −10700…−11700 |
| Svojanov (761141) | CHR470018390 | 1839 | městečko („Markt Swojanow“) kolem x 10900–11800, y −14800…−15400; kotvy podle dnešních č.p. i st. parcel nesedí (chyba 35–370 m) – čísla i parcely nejspíš přečíslované |
| Žamberk (794368) | HRA447018400 | 1840 | město na zvláštních listech („Stadt Senftenberg“, blok vlevo dole); dnešní st. parcely přečíslované. Souřadnice prohlížeče: kostel sv. Václava a Nádražní/Kostelní (č.p. 52–70) x 1700–2600, y −31700…−32300; Jiráskovo nám. (č.p. 250–273) x 3400–3900, y −29600…−30000; východní okraj u Tyršovy (č.p. 286–308) x 4700–5200, y −30300…−31000 |
| Šestajovice u Prahy (762385) | KRM346018410 | 1841 | ves na rohu 4 listů |
| Ostrov u Lanškrouna (715999) | CHR276018390 | 1839 | „Michelsdorf“ |
| Dolní Libchavy (629553) | CHR252018390 | 1839 | |
| Morašice u Litomyšle (698407) | CHR283018390 | 1839 | |
| Koldín (668036) | HRA200018390 | 1839 | |
| Krumsín (675202) | MOR116918340 | 1834 | MZA: mza.cz/indikacniskici/skica/detail/MOR116918340 |
| Zhoř u České Třebové (792900) | CHR566018390 | 1839 | sign. NA 9254-1 |
| Čtyřkoly (624331) | BER426018400 | 1840 | „Vierrad“; osada Javorník (téže k.ú.) na skenu chybí – jen na císařském otisku |
| Lštění (624357) | BER247018400 | 1840 | i osada Dubsko (dnes k.ú. Přestavlky u Čerčan, jiná čísla parcel); revize BER247018720 (1872) |
| Přestavlky u Čerčan (735191) | KRM317018410 | 1841 | silně opravovaná |
| Chříč (654558) | RAK171018410 | 1841 | „Křzitz“ |
| Lhota u Chříče (654566) | RAK182018410 | 1841 | |
| Studená u Chříče (654582) | RAK339018410 | 1841 | |
| Příčina (735825) | RAK273018410 | 1841 | |
| Všesulov (787477) | RAK306018410 | 1841 | č.p. u budov nevepsána, parcely dnes přečíslované |
| Petrovice u Rakovníka (719927) | RAK252018410 | 1841 | silně revidovaná |
| Klučov (666645) | KRM154018410 | 1841 | ves na dvou listech (posunuté o ~20 m); dnes bez starých st. parcel – kotvy podle č.p. 3–7 (západní řada) a 10–12; č.p. 3 = st. 4, 7 = st. 10, 8 = st. 12 (zaniklé) |
| Bylany u Českého Brodu (653985) | KRM021018410 | 1841 | „Billan“; dnes bez st. parcel; západní řada č.p. 22–26 sedí s dneškem (26 = st. 4, 24 = st. 6), východní strana návsi přečíslovaná |
| Lipany (683957) | KRM227018410 | 1841 | č.p. 9 = st. 12 (dnes st. 12/2) |
| Brněnec (609927) | CHR026018390 | 1839 | je to skica Bělé nad Svitavou („Deutsch Biela“) – střední ze tří částí je „Böhmisch Brnenec / Brünnlitz“; st. parcely se zachovaly (213 = č.p. 11, 216 = č.p. 10, 219 = č.p. 3) |
| Domažlice (630853) | KLA467018380 | 1838 | vnitřní město na zvláštním bloku listů dole („Stadt Taus“, větší měřítko); st. parcely se zachovaly (st. 170 = č.p. 51, st. 113 = č.p. 97, st. 115 = č.p. 96 Chodský hrad); vedlejší list vlevo je předměstí s vlastními č.p. |
| Mělník (692816) | BOL308018420 | 1842 | i předměstí a osady Podolí, Okrouhlík, Rybáře, Chloumek; Chloumek a sv. Jan kolem x 9500–11500, y −6800…−8500 (vlastníci psaní „N° x v Glo.“); Podolí („Podoll“, vlastní č.p., zahrady „N° x v Pod.“) podél silnice x 5200–6800, y −16000…−17400 (č.p. 52–56 x ≈ 5300, 61–66 x ≈ 5800–6000, 24–32 x ≈ 6200–6800); Okrouhlík („Okrauhlik“, ohrazená osada, č.p. 1–16) x 2500–3100, y −13900…−14500. St. parcely dnes přečíslované – kotvy: kostel sv. Jana na Chloumečku [10934, −7251.3] ↔ S-JTSK [−733069.8, −1012106], kostel Nejsv. Trojice na Chloumku [13751.8, −7945.1] ↔ [−732397.8, −1012352.5] (měřítko 0,247 m/j., natočení −6,3°; ověřeno ulicí Okrouhlík) |

**Jiné cesty ke kódu (ověřeno 25. 10. 2026):** veřejný seznam kódů pro Čechy neexistuje. Kód (CHR/HRA/KRM… + číslo + rok)
nejde odvodit – prostřední číslo neodpovídá abecedě ani signatuře; **kódy nezkoušej naslepo** (byl by to průzkum služby
mimo aplikaci). Signatura Národního archivu („<číslo>-1 <obec>“, řazeno abecedně podle německého jména obce) se hodí pro objednávku skenu u NA (`digi.nacr.cz/formis/formular.php?sign=<signatura>`),
ne pro prohlížeč. Morava: veřejný seznam MZA podle písmen (`mza.cz/indikacniskici/skica/?letter=S`). Jinak jen
vyhledání v aplikaci Archiv – při výpadku počkat (25. 10. 2026 trval výpadek vyhledávání asi 1–2 hodiny).
Výpadek se pozná tak, že panel „Výsledky“ zůstane na „Chvilku strpení…“ a dotazy aplikace na `arcgis4/…/Archiv/klady/MapServer/*/query`
vracejí `{"error":{"code":499,"message":"Token Required"}}` (aplikace je posílá bez tokenu; 28. 10. 2026 nepomohlo ani znovunačtení).
Je to chyba na straně ČÚZK – **token nedoplňuj a službu neobcházej**, jen počkej a zkus to později. 28. 10. 2026 vyhledávání ve vestavěném prohlížeči aplikace dál vracelo 499, ale v uživatelově Chromu (Claude in Chrome) fungovalo – zkus jiný prohlížeč, prohlížeč skic (`openmap.html`) pak jde i ve vestavěném.

## Pozdější zdroje pro novodobé adresy (ověřeno 27. 10. 2026)
| Co | Kde | Poznámka |
|---|---|---|
| Adresáře měst (Adressbuch) – seznam domů podle č.p. s ulicí a majitelem, seznam ulic s č.p. | GenWiki `wiki.genealogy.net/<Město>/Adressbuch_<rok>` → odkaz „Digitalisat“; Martin-Opitz-Bibliothek `digital.martin-opitz-bibliothek.de` (vyhledávání, prohlížeč Kitodo) | sudetská města (Ústí 1926 i s okresem a městskými částmi). Strany lze otevřít jako obrázek IIIF: `…/?eID=tx_dlf_pageview_restriction_proxy&use=thumbnails&url=http%3A%2F%2F127.0.0.1%3A8182%2Fiiif%2F2%2F<id>_volume%252F<00094>_<id>.jpg%2Fpct%3A0%2C0%2C100%2C52%2F1400%2C%2F0%2Fdefault.jpg` (výřez horní poloviny, šířka 1400) – čti po jednotlivých stranách, ne hromadně |
| Sčítací operáty 1921 | FamilySearch (katalog podle okresu) | čísla domů s ulicí; vyžaduje přihlášení |
| Státní mapa 1 : 5 000 (1951–2000), Mapa evidence nemovitostí | ČÚZK Archiv (vrstva / `openmap.html?typ=sm5…`, `typ=menkyc…`) | **bez č.p.** – jen obrysy budov, čísla parcel a popisy částí obcí (pomůže umístit osadu/předměstí) |

Starý web archivnimapy.cuzk.cz / .gov.cz už neexistuje (DNS nenalezeno) – nepoužívej staré návody s ním.

## Podmínky (přečteno 25. 10. 2026)
- **Podmínky poskytování síťových služeb ČÚZK** (cuzk.gov.cz → Předpisy → Podmínky poskytování prostorových dat a síťových
  služeb): služby otevřené, užití komerční i nekomerční bez omezení, „pokud rozsah užití není na újmu poskytovatele“;
  povinnost uvést „ČÚZK – on-line“ při užití prohlížecí služby ve vlastním produktu; ČÚZK může dočasně omezit přístup
  a uživateli, který „přetěžuje technologickou infrastrukturu ČÚZK“, v tom zabránit technickými prostředky.
- **Podmínky poskytování prostorových dat ČÚZK:** otevřená data (RÚIAN, ZABAGED, Ortofoto ČR, státní mapová díla…)
  zdarma pod CC BY 4.0, uvádět zdroj „ČÚZK, rok“.
- **Zásady užívání dat a služeb ZÚ** (ZÚ-01256/2026-13310, 23. 3. 2026, geoportal.cuzk.cz/Dokumenty/Podminky.pdf):
  čl. 1.3 archiválie ÚAZK podle zákona o archivnictví 499/2004 Sb.; čl. 3 data ÚAZK jen na žádost přes E-shop a po
  zaplacení; čl. 7.3 síťové služby zdarma, při „nepřiměřeném přetěžování“ zábrana technickými prostředky.
- O automatizovaném přístupu ani o snímcích obrazovky z aplikace Archiv podmínky nic výslovně neříkají; skill proto
  drží „jako člověk v prohlížeči, jedno vlákno, žádné hromadné stahování“.
- Aplikace Archiv: „Indikační skici nejsou vlastnictvím Zeměměřického úřadu“ – vlastníkem je příslušný archiv.

Data RÚIAN: ČÚZK, licence CC BY 4.0 – na mapě uveď „ČÚZK“.
