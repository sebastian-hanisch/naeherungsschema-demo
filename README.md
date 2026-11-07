# Runden und Gruppieren: ein Näherungsschema – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-naeherungsschema-demo.streamlit.app/)** -->

Stück 6 (gelb) der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Die Stücke davor haben FFD und seine Schranken untersucht; dieses Stück fragt umgekehrt, was ein **Näherungsschema** liefert, das große Pakete **rundet und gruppiert**, die gerundete Instanz **exakt** löst und die kleinen Pakete zuletzt auffüllt. Es ist ein gelbes Stück: Die Zahlen, die die Rechnung für eine garantierte Güte verlangt, sind rechnerisch absurd; die Demo zeigt, wie früh.

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
| Mehr Gruppen, weniger Verlust | Bei großen Paketen mit n = 100 und eps 0,2 liegt das Schema mit 5 / 10 / 25 Gruppen **12,82 / 6,14 / 2,14** Container über L2: Die Rundung kostet weniger, je feiner sie ist |
| Wie gut ist FFD selbst? | FFD liegt im Mittel nur **0,08 bis 1,14** Container über L2 (am meisten bei 200 mittleren Paketen); für ein Schema bleibt wenig zu holen |
| Wie wächst der Aufwand? | Mittlere Pakete, n = 50, eps 0,2: mit 5 / 10 / 25 Gruppen im Mittel **17 / 84 / 557** Muster und **670 / 2601 / 5886** Knoten der Tiefensuche |
| Wann reicht die Suche nicht? | In **739** von 5400 Läufen erreicht die Tiefensuche die Knotengrenze von 10 000 und beweist die gerundete Instanz nicht; bei 200 mittleren Paketen ist das in 7 von 9 Einstellungen in **allen** 50 Läufen so |
| Hält die obere Grenze? | In allen **4661** bewiesen gelösten Läufen ja; sie ist locker: Im Mittel liegt sie je Zelle und Einstellung **mindestens 2,08** Container über dem Ergebnis |
| Die Zahlen der Rechnung | Mit aufgerundet 1 / eps² Gruppen hat die gerundete Instanz bei eps 0,1 **197.949** Muster, bei 0,075 **18.558.311**, bei 0,05 **180.302.225.970** und bei 0,02 mehr als 10^29 (30 Stellen) |

**Die drei Handbeispiele** (Container: FFD, Optimum und das Schema für vier Einstellungen):

| Beispiel | FFD | Optimum | eps 0,25 / 3 | eps 0,25 / 4 | eps 0,25 / 6 | eps 0,1 / 12 |
|---|---|---|---|---|---|---|
| 1 | 5 | 5 | 6 | 5 | 5 | 5 |
| 2 | 6 | 5 | 6 | 6 | 6 | 5 |
| 3 | 5 | 5 | 5 | 5 | 5 | 5 |

**Container über L2** (Mittel; FFD und die neun Einstellungen als eps / Zahl der Gruppen):

| Verteilung | n | FFD | 0,5 / 4 | 0,34 / 3 | 0,34 / 6 | 0,25 / 4 | 0,25 / 8 | 0,25 / 16 | 0,2 / 5 | 0,2 / 10 | 0,2 / 25 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mittel | 20 | 0,40 | 0,40 | 0,40 | 0,40 | 0,42 | 0,40 | 0,40 | 0,42 | 0,34 | 0,38 |
| mittel | 50 | 0,38 | 0,38 | 0,38 | 0,38 | 0,58 | 0,60 | 0,42 | 0,78 | 0,66 | 0,40 |
| mittel | 100 | 0,68 | 0,68 | 0,68 | 0,68 | 0,94 | 1,00 | 0,82 | 1,24 | 1,20 | 0,78 |
| mittel | 200 | 1,14 | 1,14 | 1,14 | 1,14 | 1,62 | 1,90 | 1,58 | 2,44 | 2,24 | 1,48 |
| groß | 20 | 0,08 | 0,08 | 2,02 | 1,00 | 2,24 | 1,16 | 0,44 | 1,56 | 0,46 | 0,04 |
| groß | 50 | 0,30 | 0,30 | 6,76 | 3,04 | 6,96 | 3,32 | 1,40 | 5,36 | 2,88 | 0,70 |
| groß | 100 | 0,56 | 0,56 | 15,50 | 7,08 | 15,02 | 7,46 | 3,22 | 12,82 | 6,14 | 2,14 |
| groß | 200 | 0,66 | 0,66 | 30,64 | 15,94 | 32,76 | 15,34 | 7,16 | 26,06 | 12,68 | 4,98 |
| breit | 20 | 0,08 | 0,08 | 1,24 | 0,56 | 1,46 | 0,54 | 0,16 | 1,26 | 0,48 | 0,08 |
| breit | 50 | 0,16 | 0,16 | 4,66 | 2,06 | 4,90 | 2,34 | 1,04 | 4,30 | 1,84 | 0,46 |
| breit | 100 | 0,38 | 0,38 | 12,64 | 6,00 | 10,12 | 5,28 | 2,54 | 10,14 | 4,26 | 1,68 |
| breit | 200 | 0,42 | 0,44 | 29,54 | 11,68 | 22,76 | 11,46 | 5,78 | 20,52 | 9,80 | 4,02 |

**Schema gegen FFD** (Zahl der Instanzen von 50 mit weniger / gleich vielen / mehr Containern als FFD):

| Verteilung | n | 0,5 / 4 | 0,34 / 3 | 0,34 / 6 | 0,25 / 4 | 0,25 / 8 | 0,25 / 16 | 0,2 / 5 | 0,2 / 10 | 0,2 / 25 |
|---|---|---|---|---|---|---|---|---|---|---|
| mittel | 20 | 0 / 50 / 0 | 0 / 50 / 0 | 0 / 50 / 0 | 0 / 49 / 1 | 0 / 50 / 0 | 0 / 50 / 0 | 0 / 49 / 1 | 3 / 47 / 0 | 1 / 49 / 0 |
| mittel | 50 | 0 / 50 / 0 | 0 / 50 / 0 | 0 / 50 / 0 | 0 / 40 / 10 | 0 / 39 / 11 | 0 / 48 / 2 | 0 / 30 / 20 | 0 / 36 / 14 | 2 / 45 / 3 |
| mittel | 100 | 0 / 50 / 0 | 0 / 50 / 0 | 0 / 50 / 0 | 0 / 38 / 12 | 0 / 34 / 16 | 1 / 41 / 8 | 0 / 23 / 27 | 0 / 24 / 26 | 2 / 41 / 7 |
| mittel | 200 | 0 / 50 / 0 | 0 / 50 / 0 | 0 / 50 / 0 | 0 / 26 / 24 | 0 / 12 / 38 | 0 / 28 / 22 | 0 / 3 / 47 | 0 / 5 / 45 | 0 / 33 / 17 |
| groß | 20 | 0 / 50 / 0 | 0 / 4 / 46 | 0 / 16 / 34 | 0 / 3 / 47 | 0 / 9 / 41 | 0 / 32 / 18 | 0 / 5 / 45 | 1 / 29 / 20 | 2 / 48 / 0 |
| groß | 50 | 0 / 50 / 0 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 7 / 43 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 30 / 20 |
| groß | 100 | 0 / 50 / 0 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 1 / 49 |
| groß | 200 | 0 / 50 / 0 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 |
| breit | 20 | 0 / 50 / 0 | 0 / 10 / 40 | 0 / 28 / 22 | 0 / 4 / 46 | 0 / 28 / 22 | 0 / 46 / 4 | 0 / 8 / 42 | 0 / 30 / 20 | 0 / 50 / 0 |
| breit | 50 | 0 / 50 / 0 | 0 / 0 / 50 | 0 / 4 / 46 | 0 / 1 / 49 | 0 / 4 / 46 | 0 / 16 / 34 | 0 / 0 / 50 | 0 / 3 / 47 | 0 / 35 / 15 |
| breit | 100 | 0 / 50 / 0 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 1 / 49 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 7 / 43 |
| breit | 200 | 0 / 49 / 1 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 | 0 / 0 / 50 |

**Aufwand** (Zellen mit n = 50: große Pakete, k, Muster und Knoten der Tiefensuche im Mittel, Knoten im größten Lauf, Läufe von 50 ohne Beweis nach 10 000 Knoten):

| Verteilung | eps / Gruppen | große Pakete | k | Muster | Knoten (Mittel) | Knoten (größter Lauf) | nicht bewiesen |
|---|---|---|---|---|---|---|---|
| mittel | 0,5 / 4 | 0 | 0,1 | 0 | 0 | 1 | 0 |
| mittel | 0,34 / 3 | 20 | 7,2 | 6 | 120 | 335 | 0 |
| mittel | 0,34 / 6 | 20 | 3,8 | 19 | 1087 | 4711 | 0 |
| mittel | 0,25 / 4 | 32 | 8,3 | 10 | 712 | 2136 | 0 |
| mittel | 0,25 / 8 | 32 | 4,4 | 36 | 2697 | 10000 | 7 |
| mittel | 0,25 / 16 | 32 | 2,4 | 152 | 4337 | 10000 | 15 |
| mittel | 0,2 / 5 | 37 | 7,9 | 17 | 670 | 3680 | 0 |
| mittel | 0,2 / 10 | 37 | 4,1 | 84 | 2601 | 10000 | 4 |
| mittel | 0,2 / 25 | 37 | 2,0 | 557 | 5886 | 10000 | 26 |
| groß | 0,5 / 4 | 25 | 6,5 | 4 | 1 | 1 | 0 |
| groß | 0,34 / 3 | 38 | 13,0 | 3 | 5 | 36 | 0 |
| groß | 0,34 / 6 | 38 | 6,8 | 8 | 8 | 218 | 0 |
| groß | 0,25 / 4 | 45 | 11,8 | 4 | 16 | 149 | 0 |
| groß | 0,25 / 8 | 45 | 6,1 | 15 | 62 | 932 | 0 |
| groß | 0,25 / 16 | 45 | 3,1 | 56 | 665 | 10000 | 2 |
| groß | 0,2 / 5 | 50 | 10,0 | 7 | 25 | 438 | 0 |
| groß | 0,2 / 10 | 50 | 5,0 | 28 | 374 | 6612 | 0 |
| groß | 0,2 / 25 | 50 | 2,0 | 268 | 1054 | 10000 | 4 |
| breit | 0,5 / 4 | 22 | 5,8 | 4 | 1 | 1 | 0 |
| breit | 0,34 / 3 | 31 | 10,7 | 3 | 2 | 25 | 0 |
| breit | 0,34 / 6 | 31 | 5,6 | 7 | 2 | 27 | 0 |
| breit | 0,25 / 4 | 36 | 9,4 | 4 | 6 | 57 | 0 |
| breit | 0,25 / 8 | 36 | 4,9 | 13 | 27 | 268 | 0 |
| breit | 0,25 / 16 | 36 | 2,8 | 36 | 30 | 812 | 0 |
| breit | 0,2 / 5 | 39 | 8,3 | 6 | 6 | 54 | 0 |
| breit | 0,2 / 10 | 39 | 4,3 | 24 | 15 | 253 | 0 |
| breit | 0,2 / 25 | 39 | 2,0 | 127 | 49 | 1626 | 0 |

**Die Zahlen der Rechnung** (Gruppen aufgerundet 1 / eps², Pakete je Container höchstens aufgerundet 1 / eps, Zahl aller Muster bei gleichmäßig verteilten gerundeten Größen, Kapazität 10 000, gezählt):

| eps | Gruppen 1 / eps² | Pakete je Container | Zahl der Muster |
|---|---|---|---|
| 0,5 | 4 | 2 | 5 |
| 0,4 | 7 | 2 | 11 |
| 0,34 | 9 | 2 | 15 |
| 0,3 | 12 | 3 | 30 |
| 0,25 | 16 | 4 | 69 |
| 0,2 | 25 | 5 | 252 |
| 0,15 | 45 | 6 | 2.204 |
| 0,1 | 100 | 10 | 197.949 |
| 0,075 | 178 | 13 | 18.558.311 |
| 0,05 | 400 | 20 | 180.302.225.970 |
| 0,02 | 2500 | 50 | 2,33e+29 (30 Stellen) |

**Obere Grenze** (Zellen mit n = 50: Läufe von 50 mit bewiesen gelöster gerundeter Instanz, davon mit gehaltener Grenze, mittlere Luft = Grenze minus Ergebnis):

| Verteilung | eps / Gruppen | bewiesen gelöst | Grenze gehalten | Luft |
|---|---|---|---|---|
| mittel | 0,5 / 4 | 50 von 50 | 50 von 50 | 15,74 |
| mittel | 0,34 / 3 | 50 von 50 | 50 von 50 | 8,48 |
| mittel | 0,34 / 6 | 50 von 50 | 50 von 50 | 8,44 |
| mittel | 0,25 / 4 | 50 von 50 | 50 von 50 | 8,08 |
| mittel | 0,25 / 8 | 43 von 50 | 43 von 43 | 5,33 |
| mittel | 0,25 / 16 | 35 von 50 | 35 von 35 | 5,51 |
| mittel | 0,2 / 5 | 50 von 50 | 50 von 50 | 7,50 |
| mittel | 0,2 / 10 | 46 von 50 | 46 von 46 | 4,24 |
| mittel | 0,2 / 25 | 24 von 50 | 24 von 24 | 4,33 |
| groß | 0,5 / 4 | 50 von 50 | 50 von 50 | 24,10 |
| groß | 0,34 / 3 | 50 von 50 | 50 von 50 | 6,66 |
| groß | 0,34 / 6 | 50 von 50 | 50 von 50 | 9,30 |
| groß | 0,25 / 4 | 50 von 50 | 50 von 50 | 5,10 |
| groß | 0,25 / 8 | 50 von 50 | 50 von 50 | 4,56 |
| groß | 0,25 / 16 | 48 von 50 | 48 von 48 | 6,48 |
| groß | 0,2 / 5 | 50 von 50 | 50 von 50 | 4,94 |
| groß | 0,2 / 10 | 50 von 50 | 50 von 50 | 3,00 |
| groß | 0,2 / 25 | 46 von 50 | 46 von 46 | 5,04 |
| breit | 0,5 / 4 | 50 von 50 | 50 von 50 | 22,24 |
| breit | 0,34 / 3 | 50 von 50 | 50 von 50 | 7,10 |
| breit | 0,34 / 6 | 50 von 50 | 50 von 50 | 9,50 |
| breit | 0,25 / 4 | 50 von 50 | 50 von 50 | 4,62 |
| breit | 0,25 / 8 | 50 von 50 | 50 von 50 | 5,20 |
| breit | 0,25 / 16 | 50 von 50 | 50 von 50 | 6,50 |
| breit | 0,2 / 5 | 50 von 50 | 50 von 50 | 4,14 |
| breit | 0,2 / 10 | 50 von 50 | 50 von 50 | 3,92 |
| breit | 0,2 / 25 | 50 von 50 | 50 von 50 | 5,26 |

## Ehrliche Grenzen

- Alle Aussagen gelten für **diese eine Fassung** des Schemas, drei Verteilungen, vier Paketzahlen, eine Kapazität und Zufallsinstanzen. Instanzen mit wenigen verschiedenen Größen (Triplets, Johnson-Instanz) und die Näherungsgüte im Sinne der Literatur sind nicht gemessen; es werden keine Zahlen oder Beweise der Arbeit von Fernandez de la Vega und Lueker übernommen (das Original wurde nicht gelesen).
- Im Raster ist der Maßstab die Schranke **L2**, nicht das Optimum; ein Teil des Abstands zu L2 ist Schranke. Der aufgerundete LP-Wert lag in den mittleren Zellen bei L2 (Vormessung), wurde im Raster aber nicht gerechnet, weil die Spaltenerzeugung für 100 und 200 Pakete zu langsam ist. Live gibt es das Optimum bis 12 und den LP-Wert bis 30 Pakete.
- Die gerundete Instanz löst eine **eigene Tiefensuche mit Knotengrenze** (10 000 im Raster, 5000 live). Wird sie erreicht, ist die gerundete Instanz nicht bewiesen exakt gelöst, die Packung ist trotzdem zulässig, aber die obere Grenze gilt nicht; die Anzahl solcher Läufe steht in der Aufwandstabelle. Eine Einstellung ohne Rundung (k = 1, jedes große Paket eine eigene Größe) ist im Raster nicht enthalten, weil sie zu langsam ist; sie gibt es nur live (Gruppenzahl mindestens so groß wie die Zahl der großen Pakete).
- Die **Zahl der Muster** in der Rechnung ist eine Rechnung der Demo (gleichmäßig verteilte gerundete Größen, Kapazität 10 000), keine Messung und keine Zahl der Literatur.
- Zur **Laufzeit** macht die Demo keine Aussage; der Aufwand wird in Mustern und Knoten gezählt.
- Das Raster sagt nichts über Pakete, die einzeln und ohne Kenntnis der späteren eintreffen (Online-Packen).

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen. Das Schema ist eine eigene Fassung in der Art von Fernandez de la Vega und Lueker (1981), das Original wurde nicht gelesen: Pakete unter eps mal Kapazität sind klein und werden zuletzt mit First Fit eingefüllt; die großen Pakete werden absteigend sortiert, in h Gruppen zu je k aufeinanderfolgenden Paketen geteilt und auf das größte Paket der Gruppe aufgerundet; die gerundete Instanz wird exakt gelöst. **Die gerundete Instanz löst eine eigene Tiefensuche über maximale Muster** (mit Knotengrenze), kein ganzzahliges Programm eines Lösers.

**Grenzen.** Das Messraster hat drei Größenbereiche und vier Paketzahlen (20, 50, 100, 200) mit je 50 Instanzen (Kapazität 1000) und neun Einstellungen des Schemas; ein Optimum gibt es dort nicht, der Maßstab ist die Schranke L2 und FFD. Live rechnet die Demo bis 60 Pakete, das Optimum bis 12 und die LP-Schranke bis 30 Pakete. Die Tiefensuche hat eine Knotengrenze (5000 live, 10000 im Raster); wird sie erreicht, ist die gerundete Instanz nicht bewiesen exakt gelöst, und die obere Grenze der Demo gilt dann nicht. Die Zahl der Muster in der Rechnung der Demo (Experiment 3) zählt alle Muster bei gleichmäßig verteilten gerundeten Größen und Kapazität 10000; sie ist eine Rechnung, keine Messung an Instanzen. Weitere Schemata, andere Gruppierungen und die Näherungsgüte im Sinne der Literatur kommen nicht vor.

**Bekannte Probleme und Unsicherheiten.** Die Ergebnisse hängen von der Knotengrenze ab, nicht vom Rechner. Die Aufwandszahlen sind Muster und Knoten, keine Zeiten. Dass das Schema selten besser als FFD ist, gilt für diese Verteilungen und Einstellungen; bei anderen Verteilungen kann es anders ausfallen. Die Demo wurde im Browser bedient (Presets, Würfel-Button, Regler auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät.

## Verifikation

- **Kern:** das Schema an einer von Hand gerechneten Mini-Instanz (neun Pakete, Kapazität 10: FFD 4, Schema mit eps 0,3 und zwei Gruppen 5, mit Gruppen, gerundeten Größen, Mustern, Rückübertragung, Auffüllen und oberer Grenze 7); eine Instanz, an der die Tiefensuche das Optimum findet, wo FFD verliert; unabhängiger Packungsprüfer; Randfälle (leere Eingabe, ein Paket, alle klein, alle groß, Paket gleich Kapazität, mehr Gruppen als Pakete, Knotengrenze, Abbruch bei zu vielen Mustern, ungültige Eingaben, Grenzen der Regler).
- **Orakel** (`tests/test_oracle_naeherungsschema.py`): die Tiefensuche gegen die Teilmengen-DP und gegen ein ganzzahliges Programm über alle maximalen Muster (scipy `milp`); die Muster gegen die Aufzählung aller Vielfachheitsvektoren; der LP-Wert gegen das ausgeschriebene LP; das Schema nachgerechnet aus seinen Teilergebnissen; bei k = 1 und ohne kleine Pakete gleich dem Optimum; obere Grenze gehalten; deterministisch.
- **Messraster:** jede Zelle mit n = 20 wird frisch gerechnet und exakt mit `nsg_precomputed.json` verglichen, bei allen anderen die ersten drei Instanzen jeder Zelle (Stichprobe in der Datei); alle Zellen zusammen prüft `python generate_precomputed.py --check` (parallel). Die Zahl der Muster der Rechnung wird gegen die Binomialschranke und gegen die Höchstzahl der Pakete je Container geprüft; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_presets.py`, `tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Zahlenfelder an den Grenzen) und Footer-Test.
- **Tests gesamt:** 147.

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
