"""Konstanten: Regler-Grenzen, Beispiele, Raster, Farben und Presets."""

CAP = 100                 # Kapazität der Beispiele und der zufälligen Live-Instanz
OPT_LIMIT = 12            # so viele Pakete darf das exakte Optimum live höchstens haben
LP_LIMIT = 30             # so viele Pakete darf die LP-Schranke live höchstens haben (die Spaltenerzeugung wird bei mehr Paketen zu langsam)
N_MIN, N_MAX, DEFAULT_N = 6, 60, 30
SEED_MAX, DEFAULT_SEED = 999999, 7
RUND_TOL = 1e-6           # Toleranz beim Aufrunden des LP-Wertes
KNOTEN_LIVE = 5_000       # Knotengrenze der Tiefensuche live; danach gilt die gerundete Instanz als „nicht bewiesen“
KNOTEN_RASTER = 10_000    # Knotengrenze im Messraster
MUSTER_GRENZE = 100_000   # so viele Muster werden höchstens gezählt (danach „mindestens“)
MUSTER_KNOTEN = 50_000    # so viele Muster darf die Liste eines Knotens der Tiefensuche höchstens haben; mehr: Abbruch, nicht bewiesen

EPS_WERTE = (0.5, 0.4, 0.34, 0.3, 0.25, 0.2, 0.15, 0.1)     # Schwelle: Pakete unter eps mal Kapazität sind „klein“
EPS_TEXT = {i: f"{e:g}".replace(".", ",") for i, e in enumerate(EPS_WERTE)}
H_MIN, H_MAX = 1, 60      # Zahl der Gruppen
THEORIE_CAP = 10_000      # Kapazität, mit der die Zahl der Muster in der Rechnung der Demo gezählt wird

# --- Beispiele (Größen, Kapazität): zwölf Pakete aus Zufallsinstanzen (Größen 10 bis 60, Kapazität 100) --------------------------------------------
# 0 (Seed 22): FFD 5, L1 5, Optimum 5; mit eps 0,25 und drei Gruppen braucht das Schema 6, mit vier oder sechs Gruppen 5.
# 1 (Seed 17): FFD 6, L1 5, Optimum 5; mit eps 0,25 und drei, vier oder sechs Gruppen 6, mit eps 0,1 und zwölf Gruppen (k = 1, keine Rundung) 5.
# 2 (Seed 1): FFD 5, Optimum 5; das Schema trifft das Optimum mit jeder Einstellung.
BEISPIELE = {
    0: ((18, 25, 11, 49, 38, 21, 54, 17, 57, 51, 32, 60), 100),
    1: ((43, 36, 29, 33, 28, 21, 59, 55, 55, 44, 52, 27), 100),
    2: ((18, 46, 58, 14, 26, 17, 41, 58, 38, 40, 51, 34), 100),
}
QUELLEN = {0: "Beispiel 1 (zwölf Pakete)", 1: "Beispiel 2 (zwölf andere Pakete)", 2: "Beispiel 3 (zwölf weitere Pakete)", 3: "Zufällige Instanz"}
ZUFALL = 3

VERTEILUNGEN = (
    ("mittel", "mittlere Pakete (10 bis 50 % der Kapazität)", 0.10, 0.50),
    ("gross", "große Pakete (20 bis 80 %)", 0.20, 0.80),
    ("breit", "breit gestreute Pakete (1 bis 90 %)", 0.01, 0.90),
)
VERTEILUNG_KURZ = ("mittel", "groß", "breit")
VERTEILUNG_LANG = ("mittlere Pakete", "große Pakete", "breit gestreute Pakete")

# --- Messraster, vorberechnet in nsg_precomputed.json -------------------------------------------------------------------------------------------
MESS_CAP = 1000
MESS_N = (20, 50, 100, 200)
INSTANZEN = 50
EINSTELLUNGEN = ((0.5, 4), (0.34, 3), (0.34, 6), (0.25, 4), (0.25, 8), (0.25, 16), (0.2, 5), (0.2, 10), (0.2, 25))     # (eps, Zahl der Gruppen)
THEORIE_EPS = (0.5, 0.4, 0.34, 0.3, 0.25, 0.2, 0.15, 0.1, 0.075, 0.05, 0.02)
STICHPROBE_J = (0, 1, 2)                  # Instanzen jeder Zelle, die einzeln gespeichert und in den Tests frisch nachgerechnet werden

COLOR_KLEIN = "#9d755d"
COLOR_FFD = "#9e9e9e"
COLOR_FREE = "rgba(150,150,150,0.35)"
COLOR_LINE = "#c0392b"
GRUPPEN_FARBEN = ("#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756", "#72b7b2", "#9d755d", "#bab0ac", "#eeca3b", "#ff9da6")
SCHEMA_FARBEN = {0: "#2F6B65", 1: "#4c78a8", 2: "#f58518"}

PRESETS = {
    "Beispiel 1: eps 0,25, 3 Gruppen": {"quelle": 0, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED, "eps_index": 4, "h": 3},
    "Beispiel 1: eps 0,25, 6 Gruppen": {"quelle": 0, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED, "eps_index": 4, "h": 6},
    "Beispiel 2: eps 0,1, 12 Gruppen (ohne Rundung)": {"quelle": 1, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED, "eps_index": 7, "h": 12},
    "Beispiel 2: eps 0,25, 6 Gruppen": {"quelle": 1, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED, "eps_index": 4, "h": 6},
    "Zufällig, 30 mittlere Pakete, eps 0,2, 25 Gruppen": {"quelle": ZUFALL, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED, "eps_index": 5, "h": 25},
}
PRESET_HELP = {
    "Beispiel 1: eps 0,25, 3 Gruppen": "Zwölf Pakete, das Optimum ist 5 und FFD findet es. Das Schema rundet die acht großen Pakete auf nur drei Größen und braucht 6: Die Rundung kostet einen Container.",
    "Beispiel 1: eps 0,25, 6 Gruppen": "Dieselben Pakete mit sechs Gruppen: Die Rundung ist feiner, das Schema braucht wieder 5.",
    "Beispiel 2: eps 0,1, 12 Gruppen (ohne Rundung)": "Zwölf andere Pakete: FFD braucht 6, das Optimum ist 5. Mit zwölf Gruppen ist jedes Paket eine eigene Gruppe, es wird nicht gerundet, und das Schema löst die großen Pakete exakt: 5, besser als FFD.",
    "Beispiel 2: eps 0,25, 6 Gruppen": "Dieselben Pakete mit der Rundung: 6 Container wie FFD. Das Schema schlägt FFD nur, wenn es kaum rundet.",
    "Zufällig, 30 mittlere Pakete, eps 0,2, 25 Gruppen": "Dreißig zufällige Pakete (10 bis 50 % der Kapazität): Mit 25 Gruppen, so vielen, wie die Rechnung der Demo für eps = 0,2 verlangt, braucht die Tiefensuche schon 83 Knoten; FFD und das Schema brauchen beide 10.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen. Das Schema ist eine eigene Fassung in der Art von Fernandez de la Vega und Lueker (1981), das Original wurde nicht gelesen: Pakete unter eps mal Kapazität sind klein und werden zuletzt mit First Fit eingefüllt; die großen Pakete werden absteigend sortiert, in h Gruppen zu je k aufeinanderfolgenden Paketen geteilt und auf das größte Paket der Gruppe aufgerundet; die gerundete Instanz wird exakt gelöst. **Die gerundete Instanz löst eine eigene Tiefensuche über maximale Muster** (mit Knotengrenze), kein ganzzahliges Programm eines Lösers.

**Grenzen.** Das Messraster hat drei Größenbereiche und vier Paketzahlen (20, 50, 100, 200) mit je {INSTANZEN} Instanzen (Kapazität {MESS_CAP}) und neun Einstellungen des Schemas; ein Optimum gibt es dort nicht, der Maßstab ist die Schranke L2 und FFD. Live rechnet die Demo bis {N_MAX} Pakete, das Optimum bis {OPT_LIMIT} und die LP-Schranke bis {LP_LIMIT} Pakete. Die Tiefensuche hat eine Knotengrenze ({KNOTEN_LIVE} live, {KNOTEN_RASTER} im Raster); wird sie erreicht, ist die gerundete Instanz nicht bewiesen exakt gelöst, und die obere Grenze der Demo gilt dann nicht. Die Zahl der Muster in der Rechnung der Demo (Experiment 3) zählt alle Muster bei gleichmäßig verteilten gerundeten Größen und Kapazität {THEORIE_CAP}; sie ist eine Rechnung, keine Messung an Instanzen. Weitere Schemata, andere Gruppierungen und die Näherungsgüte im Sinne der Literatur kommen nicht vor.

**Bekannte Probleme und Unsicherheiten.** Die Ergebnisse hängen von der Knotengrenze ab, nicht vom Rechner. Die Aufwandszahlen sind Muster und Knoten, keine Zeiten. Dass das Schema selten besser als FFD ist, gilt für diese Verteilungen und Einstellungen; bei anderen Verteilungen kann es anders ausfallen. Die Demo wurde im Browser bedient (Presets, Würfel-Button, Regler auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
