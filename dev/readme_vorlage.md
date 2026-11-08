# Runden und Gruppieren: ein Näherungsschema – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-naeherungsschema-demo.streamlit.app/)**

Stück 6 (gelb) der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Die Stücke davor haben FFD und seine Schranken untersucht; dieses Stück fragt umgekehrt, was ein **Näherungsschema** liefert, das große Pakete **rundet und gruppiert**, die gerundete Instanz **exakt** löst und die kleinen Pakete zuletzt auffüllt. Es ist ein gelbes Stück: Die Zahlen, die die Rechnung dieser Demo für eine garantierte Güte verlangt, werden ab eps etwa 0,05 rechnerisch absurd; die Demo zeigt, wie früh.

## Warum dieses Problem

FFD ist einfach und im Mittel fast optimal. Ein Näherungsschema verspricht mehr: Wer die Zahl der verschiedenen Größen klein macht, kann den Rest exakt lösen. Die Demo stellt zwei Fragen: **Was liefert das Schema gegen FFD** (an drei Handbeispielen und an 12 Zellen zu je 50 festen Zufallsinstanzen), und **wie groß werden die Zahlen** (Gruppen, Muster, Knoten der exakten Suche), wenn man es so genau macht, wie die Rechnung verlangt.

## Modell

Ganzzahlige Paketgrößen, eine Sorte Container der Kapazität 100 (im Raster 1000), alle Pakete vorab bekannt. **Schema** (eigene Fassung in der Art von Fernandez de la Vega und Lueker, 1981; das Original wurde nicht gelesen): (1) Pakete unter eps mal Kapazität sind **klein** und warten; (2) die **großen** Pakete werden absteigend sortiert, in h Gruppen zu je k = aufgerundet(n_groß / h) aufeinanderfolgenden Paketen geteilt und jedes auf das größte Paket seiner Gruppe aufgerundet; (3) die gerundete Instanz (höchstens h verschiedene Größen) wird **exakt** gelöst: eine eigene **Tiefensuche über maximale Muster** (ein Muster sagt, welche gerundeten Größen in einen Container kommen), Schranke = bisherige Container plus L2 des Restbedarfs, Start = FFD der gerundeten Instanz, Knotengrenze; (4) zurück: jedes Paket kommt in einen Platz seiner Gruppe; (5) die kleinen Pakete werden absteigend mit First Fit aufgefüllt. **Maßstäbe:** FFD, die Schranke L2 (Martello und Toth), live der LP-Wert (Spaltenerzeugung, bis 30 Pakete) und das Optimum (Teilmengen-DP, bis 12 Pakete). **Obere Grenze** (eigene Rechnung): Wenn die gerundete Instanz bewiesen exakt gelöst ist, braucht das Schema höchstens max(FFD + k, aufgerundet(Volumen / ((1 − eps) Kapazität)) + 1) Container. Die Formeln stehen im Expander 📐 der App.

## Methodik

- **Kern** (`nsg_algorithm.py`): `ffd`, `l1`, `l2`, `optimum`, `lp_wert`, `maximale_muster`, `muster_zaehlen`, `loese_gerundet` (die Tiefensuche), `schema`, `container_pruefen` (unabhängiger Prüfer: jedes Paket genau einmal, keine Überfüllung).
- **Handbeispiele:** drei feste Mengen von je zwölf Paketen (Größen 10 bis 60, Kapazität 100); die App zeichnet die Rundung (Pakete absteigend, Farbe = Gruppe, Stufenlinie = gerundete Größe, Schwelle), die Packung des Schemas und einen Vergleichsbalken.
- **Messraster:** drei Verteilungen (mittlere, große, breit gestreute Pakete) × vier Paketzahlen (20, 50, 100, 200) × **50 feste Instanzen** je Zelle (Kapazität 1000) × neun Einstellungen (eps und Zahl der Gruppen). Maßstab ist L2 (ein Optimum gibt es im Raster nicht); die Tiefensuche hat im Raster eine Knotengrenze von 10 000. Die Summen stehen als ganze Zahlen in `nsg_precomputed.json` (erzeugt von `generate_precomputed.py`), dazu die gezählte Zahl der Muster der Rechnung für eps von 0,5 bis 0,02.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds) oder Rechnungen der Demo, nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_naeherungsschema.py`. Tabellenwerte sind Mittel über die 50 Instanzen einer Zelle von (Container minus L2).

| Frage | Befund |
|---|---|
| Beispiel 1 (zwölf Pakete, FFD 5, Optimum 5) | Mit eps 0,25 und **3 Gruppen** braucht das Schema **6** Container: Die Rundung kostet einen. Mit 4 oder 6 Gruppen braucht es 5 (Tabelle unten) |
| Beispiel 2 (zwölf andere Pakete, FFD 6, Optimum 5) | Mit eps 0,25 und 3, 4 oder 6 Gruppen braucht das Schema **6**, so viel wie FFD. **Nur ohne Rundung** (eps 0,1 und 12 Gruppen: jedes große Paket eine eigene Größe) findet es das Optimum **5** |
| Beispiel 3 (zwölf weitere Pakete, FFD 5, Optimum 5) | Das Schema braucht in allen vier Einstellungen der Tabelle 5 |
| Schema gegen FFD, Lauf für Lauf | In den **5400** Läufen (12 Zellen × 50 Instanzen × 9 Einstellungen) braucht das Schema in **12** weniger Container als FFD, in 2298 gleich viele und in **3090** mehr |
| Schema gegen FFD, im Mittel | Im Mittel ist das Schema nur in **3** von 108 Kombinationen aus Zelle und Einstellung besser als FFD (zwei bei mittleren, eine bei großen Paketen; alle bei n = 20 und eps 0,2); in **10** von 12 Zellen ist **keine** der neun Einstellungen im Mittel besser |
| Wo es nicht schlechter ist | Bei mittleren Paketen (10 bis 50 % der Kapazität) sind eps 0,5 sowie eps 0,34 mit 3 und mit 6 Gruppen in allen **600** Läufen (4 Paketzahlen × 3 Einstellungen × 50) genau so gut wie FFD |
| Was die Rundung kostet | Bei großen Paketen mit n = 100 liegt FFD 0,56 Container über L2, das Schema mit eps 0,25 und 4 Gruppen **15,02**, mit 8 Gruppen 7,46 und mit 16 Gruppen 3,22; auch mit eps 0,2 und 25 Gruppen noch 2,14 |
| Mehr Gruppen, weniger Verlust | Bei großen Paketen mit n = 100 und eps 0,2 liegt das Schema mit 5 / 10 / 25 Gruppen **12,82 / 6,14 / 2,14** Container über L2: Bei großen Paketen kostet die Rundung weniger, je feiner sie ist; bei mittleren Paketen nicht immer |
| Wie gut ist FFD selbst? | FFD liegt im Mittel nur **0,08 bis 1,14** Container über L2 (am meisten bei 200 mittleren Paketen); für ein Schema bleibt wenig zu holen |
| Wie wächst der Aufwand? | Mittlere Pakete, n = 50, eps 0,2: mit 5 / 10 / 25 Gruppen im Mittel **17 / 84 / 557** Muster und **670 / 2601 / 5886** Knoten der Tiefensuche |
| Wann reicht die Suche nicht? | In **739** von 5400 Läufen erreicht die Tiefensuche die Knotengrenze von 10 000 und beweist die gerundete Instanz nicht; bei 200 mittleren Paketen ist das in 7 von 9 Einstellungen in **allen** 50 Läufen so |
| Hält die obere Grenze? | In allen **4661** bewiesen gelösten Läufen ja; sie ist locker: Im Mittel liegt sie je Zelle und Einstellung **mindestens 2,08** Container über dem Ergebnis |
| Die Zahlen der Rechnung | Mit aufgerundet 1 / eps² Gruppen hat die gerundete Instanz bei eps 0,1 **197.949** Muster, bei 0,075 **18.558.311**, bei 0,05 **180.302.225.970** und bei 0,02 mehr als 10^29 (30 Stellen) |

**Die drei Handbeispiele** (Container: FFD, Optimum und das Schema für vier Einstellungen):

{{BEISPIELE}}

**Container über L2** (Mittel; FFD und die neun Einstellungen als eps / Zahl der Gruppen):

{{TABELLE_A}}

**Schema gegen FFD** (Zahl der Instanzen von 50 mit weniger / gleich vielen / mehr Containern als FFD):

{{TABELLE_B}}

**Aufwand** (Zellen mit n = 50: große Pakete, k, Muster und Knoten der Tiefensuche im Mittel, Knoten im größten Lauf, Läufe von 50 ohne Beweis nach 10 000 Knoten):

{{TABELLE_C}}

**Die Zahlen der Rechnung** (Gruppen aufgerundet 1 / eps², Pakete je Container höchstens aufgerundet 1 / eps, Zahl aller Muster bei gleichmäßig verteilten gerundeten Größen, Kapazität 10 000, gezählt):

{{TABELLE_D}}

**Obere Grenze** (Zellen mit n = 50: Läufe von 50 mit bewiesen gelöster gerundeter Instanz, davon mit gehaltener Grenze, mittlere Luft = Grenze minus Ergebnis):

{{TABELLE_E}}

## Ehrliche Grenzen

- Alle Aussagen gelten für **diese eine Fassung** des Schemas, drei Verteilungen, vier Paketzahlen, eine Kapazität und Zufallsinstanzen. Instanzen mit wenigen verschiedenen Größen (Triplets, Johnson-Instanz) und die Näherungsgüte im Sinne der Literatur sind nicht gemessen; es werden keine Zahlen oder Beweise der Arbeit von Fernandez de la Vega und Lueker übernommen (das Original wurde nicht gelesen).
- Im Raster ist der Maßstab die Schranke **L2**, nicht das Optimum; ein Teil des Abstands zu L2 ist Schranke. Der aufgerundete LP-Wert lag in den mittleren Zellen bei L2 (Vormessung; in einer Nachprüfung bei 20 und 50 Paketen in 58 von 60 Instanzen), wurde im Raster aber nicht gerechnet, weil die Spaltenerzeugung für 100 und 200 Pakete zu langsam ist. Live gibt es das Optimum bis 12 und den LP-Wert bis 30 Pakete.
- Die gerundete Instanz löst eine **eigene Tiefensuche mit Knotengrenze** (10 000 im Raster, 5000 live). Wird sie erreicht, ist die gerundete Instanz nicht bewiesen exakt gelöst, die Packung ist trotzdem zulässig, aber die obere Grenze gilt nicht; die Anzahl solcher Läufe steht in der Aufwandstabelle. Eine Einstellung ohne Rundung (k = 1, jedes große Paket eine eigene Größe) ist im Raster nicht enthalten, weil sie zu langsam ist; sie gibt es nur live (Gruppenzahl mindestens so groß wie die Zahl der großen Pakete).
- Die **Zahl der Muster** in der Rechnung ist eine Rechnung der Demo (gleichmäßig verteilte gerundete Größen, Kapazität 10 000), keine Messung und keine Zahl der Literatur.
- Zur **Laufzeit** macht die Demo keine Aussage; der Aufwand wird in Mustern und Knoten gezählt.
- Das Raster sagt nichts über Pakete, die einzeln und ohne Kenntnis der späteren eintreffen (Online-Packen).

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

{{ANNAHMEN}}

## Verifikation

- **Kern:** das Schema an einer von Hand gerechneten Mini-Instanz (neun Pakete, Kapazität 10: FFD 4, Schema mit eps 0,3 und zwei Gruppen 5, mit Gruppen, gerundeten Größen, Mustern, Rückübertragung, Auffüllen und oberer Grenze 7); eine Instanz, an der die Tiefensuche das Optimum findet, wo FFD verliert; unabhängiger Packungsprüfer; Randfälle (leere Eingabe, ein Paket, alle klein, alle groß, Paket gleich Kapazität, mehr Gruppen als Pakete, Knotengrenze, Abbruch bei zu vielen Mustern, ungültige Eingaben, Grenzen der Regler).
- **Orakel** (`tests/test_oracle_naeherungsschema.py`): die Tiefensuche gegen die Teilmengen-DP und gegen ein ganzzahliges Programm über alle maximalen Muster (scipy `milp`); die Muster gegen die Aufzählung aller Vielfachheitsvektoren; der LP-Wert gegen das ausgeschriebene LP; das Schema nachgerechnet aus seinen Teilergebnissen; bei k = 1 und ohne kleine Pakete gleich dem Optimum; obere Grenze gehalten; deterministisch.
- **Messraster:** jede Zelle mit n = 20 wird frisch gerechnet und exakt mit `nsg_precomputed.json` verglichen, bei allen anderen die ersten drei Instanzen jeder Zelle (Stichprobe in der Datei); alle Zellen zusammen prüft `python generate_precomputed.py --check` (parallel). Die Zahl der Muster der Rechnung wird gegen die Binomialschranke und gegen die Höchstzahl der Pakete je Container geprüft; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_presets.py`, `tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Zahlenfelder an den Grenzen) und Footer-Test.
- **Tests gesamt:** {{TESTS}}.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/readme_bauen.py`, `dev/readme_vorlage.md` | setzen die README aus der Vorlage, den Tabellen der Messzellen und dem Text der Annahmen zusammen |
| `generate_precomputed.py` | erzeugt `nsg_precomputed.json` (Messraster, Zählung der Muster, Stichprobe); `--check` vergleicht, `--nur-stichprobe` ergänzt die Stichprobe |
| `nsg_algorithm.py` | Kern: FFD, Schranken, Optimum, LP-Wert, Muster, Tiefensuche, Schema, Packungsprüfer |
| `nsg_constants.py` | Beispiele, Reglerwerte, Messraster, Farben, Presets, Text der Annahmen |
| `nsg_evaluation.py` | Analyse, Verdikte, Messzellen, Zahlen der Rechnung |
| `nsg_layout.py` | Fester Kopf (Stylesheet) und Tabellen auf dem Telefon |
| `nsg_precomputed.json` | vorberechnete Summen, Zählung der Muster und Stichprobe |
| `nsg_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `nsg_scenario.py` | Instanzen: Handbeispiele und Zufallsinstanzen mit festen Seeds |
| `nsg_visualization.py` | Plotly-Abbildungen (Rundung, Packung, Vergleich, Messung; Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanz und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Abbildungen, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Arc-Flow als exakter Löser der gerundeten Instanz:** gelbes Stück 5; hier löst eine eigene Tiefensuche, deren Aufwand in Knoten gezählt wird.
- **Rundung nach Karmarkar und Karp mit LP:** ein anderes, aufwändigeres Verfahren; hier nur die einfache Gruppierung.
- **Güte im Sinne der Literatur, Beweise, Konstanten:** Das Original wurde nicht gelesen; die Demo misst eine eigene Fassung.
- **Einstellung ohne Rundung (k = 1) im Raster:** zu langsam; nur live.
- **Laufzeitvergleiche:** hängen an der Umsetzung, keine Aussage.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
