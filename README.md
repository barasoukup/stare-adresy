# Staré adresy – kde stál dům předků

Skill pro [Claude Code](https://claude.com/claude-code), který najde, **kde stál dům „obec + číslo popisné“ z matrik
18.–19. století**. Dům dohledá na indikačních skicách a císařských otiscích **stabilního katastru (1824–1843)**
v archivní aplikaci ČÚZK a porovná ho s dnešním katastrem (RÚIAN).

Proč to nestačí podle dnešní adresy: čísla popisná se od 19. století často změnila. Domy zanikly, vesnice se
přečíslovaly a ve městech dostaly číslo zaniklého domu novostavby i stovky metrů daleko. Při testu na 69 adresách
z jednoho rodokmenu stál zhruba každý pátý dům jinde než dnešní dům se stejným číslem.

**Co dostanete:**
- polohu domu s mírou jistoty (A jistá · B podle skici, dnes jinak · C jen dnešní č.p. · D jen obec),
- výřez indikační skice s domem a odkaz na skicu v archivu,
- informaci, zda dnešní dům se stejným číslem stojí na stejném místě, nebo jinde,
- interaktivní mapu (podklad ČÚZK, výřezy skic, filtry) a soubor `domy.geojson` pro jiné aplikace.

## Instalace

V Claude Code:
```
/plugin marketplace add barasoukup/stare-adresy
/plugin install stare-adresy@stare-adresy
```
Aktualizace: `/plugin marketplace update stare-adresy`, pak `/plugin` → aktualizovat.

Bez pluginů: stáhněte repozitář (Code → Download ZIP) a složku `plugins/stare-adresy/skills/stare-adresy`
zkopírujte do `~/.claude/skills/`.

**Potřebujete:** Python 3.9+ (jen standardní knihovna), ImageMagick (`magick`, jen pro mapu) a prohlížeč, který
Claude ovládá (vestavěný prohlížeč v aplikaci Claude, nebo Claude in Chrome). Skici se čtou z obrazovky – bez
prohlížeče skill umí jen část práce (dnešní katastr a mapu).

## Použití

Stačí se zeptat, třeba:
> V matrice mám předky z Přívratu, dům č.p. 68 (křest 1835). Kde ten dům stál?

nebo
> Projdi adresy v mém rodokmenu a udělej mapu domů předků.

Používáte-li skill **rodokmen** (průvodce rodokmenem z českých matrik od jiného autora), stare-adresy si
umí adresy načíst přímo z jeho projektu (`data/osoby.py`) a mapa domů jde použít i na rodinném webu
(viz `reference/vystup.md`). Projekt rodokmenu přitom nemění.

**Čas:** je-li kód skici obce známý (návod obsahuje tabulku nalezených skic), ves se třemi adresami zabere asi
10 minut. Hledání domů, jejichž číslo dnes neplatí, ve velké vsi nebo ve městě může trvat hodinu.

## Zdroje a pravidla

- **ČÚZK Archiv** (ags.cuzk.gov.cz/archiv) – indikační skici (vlastník: Národní archiv, Moravský zemský archiv,
  Zemský archiv v Opavě) a císařské otisky. Skill je čte **jen v prohlížeči jako člověk, v jednom vlákně**,
  neobchází přístupový klíč aplikace a nic hromadně nestahuje. Podmínky ČÚZK dovolují zablokovat toho, kdo služby
  přetěžuje – prosím, nespouštějte víc souběžných agentů nad aplikací Archiv.
- **RÚIAN, Základní mapa ČR, Ortofoto ČR** – otevřená data ČÚZK (CC BY 4.0), zdroj „ČÚZK“.
- **Výřezy skic** jsou badatelské kopie pro vlastní potřebu. Při zveřejnění uveďte zdroj (např. „Národní archiv,
  Indikační skici, CHR473018390; ČÚZK – on-line“); pro tisk a publikace si kvalitní sken objednejte u archivu.

Podrobnosti v `plugins/stare-adresy/skills/stare-adresy/reference/zdroje.md`.

## Licence

MIT (viz `LICENSE`). Obsahuje styly Leaflet 1.9.4 (BSD 2-Clause).

Chyby a nápady: [Issues](https://github.com/barasoukup/stare-adresy/issues).
