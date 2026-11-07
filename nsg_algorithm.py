"""Kern der Demo: FFD, die Schranken L1 und L2, das exakte Optimum (kleine Instanzen), die LP-Schranke und das Näherungsschema durch Runden und Gruppieren.

Pakete haben ganzzahlige Größen, Container die Kapazität `cap`; eine Packung ist eine Liste von Containern, jeder eine Liste von Paketnummern.

Das Schema (eigene Fassung in der Art von Fernandez de la Vega und Lueker, 1981; das Original wurde nicht gelesen):
  1. Kleine Pakete (Größe unter eps mal cap) werden beiseite gelegt.
  2. Die großen Pakete werden absteigend sortiert und in `h` Gruppen zu je k = aufgerundet(n_gross / h) aufeinanderfolgenden Paketen zerlegt (die letzte ist kleiner); jedes Paket wird auf das größte
     Paket seiner Gruppe aufgerundet. Die gerundete Instanz hat höchstens h verschiedene Größen.
  3. Die gerundete Instanz wird exakt gelöst (Tiefensuche über maximale Muster, mit Knotengrenze).
  4. Zurück: Jedes große Paket nimmt einen Platz seiner Gruppe in einem Container ein (es ist höchstens so groß wie der Platz).
  5. Die kleinen Pakete (absteigend) kommen mit First Fit in die Lücken der Container, sonst in neue."""

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog

import nsg_constants as C


# --- FFD und Schranken --------------------------------------------------------------------------------------------------------------------------


def ffd(sizes, cap: int) -> list:
    """First Fit Decreasing: größte zuerst (Gleichstand: kleinere Nummer zuerst), jedes Paket in den ersten Container mit genug Platz."""
    if any(s <= 0 or s > cap for s in sizes):
        raise ValueError("Paketgröße muss zwischen 1 und der Kapazität liegen")
    bins, loads = [], []
    for i in sorted(range(len(sizes)), key=lambda i: (-sizes[i], i)):
        s = sizes[i]
        for b, load in enumerate(loads):
            if load + s <= cap:
                bins[b].append(i)
                loads[b] += s
                break
        else:
            bins.append([i])
            loads.append(s)
    return bins


def container_pruefen(sizes, bins, cap: int) -> bool:
    """Unabhängiger Zulässigkeitsprüfer: jedes Paket genau einmal, keine Überfüllung, keine leeren Container."""
    gesehen = sorted(i for b in bins for i in b)
    return gesehen == list(range(len(sizes))) and all(b and sum(sizes[i] for i in b) <= cap for b in bins)


def l1(sizes, cap: int) -> int:
    """Volumenschranke: Summe der Größen durch die Kapazität, aufgerundet."""
    return -(-sum(sizes) // cap) if sizes else 0


def _l2_alpha(sizes, cap: int, alpha: int) -> int:
    j1 = [s for s in sizes if s > cap - alpha]
    j2 = [s for s in sizes if cap - alpha >= s and 2 * s > cap]
    j3 = [s for s in sizes if 2 * s <= cap and s >= alpha]
    frei = len(j2) * cap - sum(j2)
    extra = max(0, -(-(sum(j3) - frei) // cap)) if j3 else 0
    return len(j1) + len(j2) + extra


def l2(sizes, cap: int) -> int:
    """Schranke L2 nach Martello und Toth: Maximum von L1 und L(alpha) über alpha = 0 und alle Paketgrößen bis zur halben Kapazität."""
    best = l1(sizes, cap)
    for alpha in {0} | {s for s in sizes if 2 * s <= cap}:
        best = max(best, _l2_alpha(sizes, cap, alpha))
    return best


def optimum(sizes, cap: int, limit: int = C.OPT_LIMIT):
    """Kleinste mögliche Containerzahl per Teilmengen-DP, oder None, wenn mehr als `limit` Pakete vorliegen."""
    n = len(sizes)
    if n > limit:
        return None
    if n == 0:
        return 0
    full = (1 << n) - 1
    inf = (n + 1, cap + 1)
    dp = [inf] * (full + 1)
    dp[0] = (1, 0)
    for mask in range(full + 1):
        b, last = dp[mask]
        if b > n:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            s = sizes[i]
            nxt = (b, last + s) if last + s <= cap else (b + 1, s)
            m2 = mask | (1 << i)
            if nxt < dp[m2]:
                dp[m2] = nxt
    return dp[full][0]


def lp_wert(sizes, cap: int, tol: float = 1e-9) -> float:
    """LP-Schranke (Gilmore und Gomory) per Spaltenerzeugung: Die Pakete werden nach gleichen Größen zusammengefasst, die Spalten sind zulässige Muster, der Preis eines neuen Musters kommt aus einem
    unbeschränkten Rucksack-DP. Gibt den (nicht gerundeten) LP-Wert zurück; er ist eindeutig. Die Muster dürfen eine Größe öfter enthalten, als sie vorkommt (Standard beim Schnittproblem); bei wenigen Paketen kann der Wert deshalb
    unter dem LP-Wert aus Stück 4 dieser Reihe liegen, der jedes Paket nur einmal zulässt."""
    if not sizes:
        return 0.0
    groessen = sorted(set(sizes))
    bedarf = np.array([sizes.count(s) for s in groessen], dtype=float)
    m = len(groessen)
    sz = np.array(groessen)
    spalten = []
    for i in range(m):
        col = [0] * m
        col[i] = cap // groessen[i]
        spalten.append(col)
    for _ in range(2000):
        res = linprog(np.ones(len(spalten)), A_ub=-np.array(spalten, dtype=float).T, b_ub=-bedarf, bounds=(0, None), method="highs")
        if res.status != 0:
            raise RuntimeError(f"LP nicht gelöst: {res.message}")
        y = -res.ineqlin.marginals
        beste = np.zeros(cap + 1)
        arg = -np.ones(cap + 1, dtype=int)
        for c in range(1, cap + 1):
            ok = sz <= c
            if ok.any():
                cand = beste[c - sz[ok]] + y[ok]
                j = int(np.argmax(cand))
                if cand[j] > beste[c - 1] + 1e-15:
                    beste[c] = cand[j]
                    arg[c] = int(np.nonzero(ok)[0][j])
                else:
                    beste[c] = beste[c - 1]
                    arg[c] = -2
        if beste[cap] <= 1 + tol:
            return float(res.fun)
        col = [0] * m
        c = cap
        while c > 0:
            a = arg[c]
            if a == -2:
                c -= 1
            elif a < 0:
                break
            else:
                col[a] += 1
                c -= groessen[a]
        spalten.append(col)
    raise RuntimeError("Spaltenerzeugung ohne Ende")


def lp_aufgerundet(wert: float) -> int:
    """Aufgerundeter LP-Wert mit Toleranz für Rundungsfehler des Lösers (RUND_TOL)."""
    return math.ceil(wert - C.RUND_TOL)


# --- Muster und die exakte Lösung der gerundeten Instanz -----------------------------------------------------------------------------------------


def maximale_muster(groessen, cap: int) -> list:
    """Alle maximalen Muster: Vielfachheiten (je Größe der absteigend sortierten verschiedenen Größen) mit Summe höchstens cap, zu denen kein weiteres Paket irgendeiner Größe mehr passt."""
    m = len(groessen)
    muster, aktuell = [], [0] * m

    def rec(i, rest):
        if i == m:
            if all(g > rest for g in groessen):
                muster.append(tuple(aktuell))
            return
        for c in range(rest // groessen[i], -1, -1):
            aktuell[i] = c
            rec(i + 1, rest - c * groessen[i])
        aktuell[i] = 0

    rec(0, cap)
    return muster


def muster_zaehlen(groessen, cap: int, grenze: int = C.MUSTER_GRENZE) -> int:
    """Zahl der maximalen Muster (wie `maximale_muster`), aber ohne die Muster zu speichern; hört bei `grenze` Mustern auf und gibt dann `grenze` zurück (es sind mindestens so viele)."""
    m = len(groessen)
    zaehler = [0]

    def rec(i, rest):
        if zaehler[0] >= grenze:
            return
        if i == m:
            if all(g > rest for g in groessen):
                zaehler[0] += 1
            return
        for c in range(rest // groessen[i], -1, -1):
            rec(i + 1, rest - c * groessen[i])

    rec(0, cap)
    return zaehler[0]


def muster_zahl_alle(groessen, cap: int) -> int:
    """Zahl aller Muster (Vielfachheiten, auch nicht maximale, ohne das leere Muster) mit Summe höchstens cap: Zählung per DP über die Summe, ohne die Muster aufzuzählen."""
    wege = [0] * (cap + 1)
    wege[0] = 1
    for g in groessen:
        for c in range(g, cap + 1):
            wege[c] += wege[c - g]
    return sum(wege) - 1


class _Abbruch(Exception):
    """Die Liste der Muster eines Knotens wird zu lang (C.MUSTER_KNOTEN): Die Suche hört auf, die gerundete Instanz gilt als nicht bewiesen."""


def _untere_schranke(bedarf, groessen, cap: int) -> int:
    liste = [g for g, b in zip(groessen, bedarf) for _ in range(b)]
    return l2(liste, cap) if liste else 0


def _muster_mit(j, bedarf, groessen, cap: int) -> list:
    """Alle Muster, die mindestens ein Paket der Größe j (der ersten noch nötigen Größe) enthalten und bezüglich des restlichen Bedarfs maximal sind: kein weiteres noch nötiges Paket passt mehr.
    Absteigend nach Füllung, dann lexikographisch absteigend (gefüllte Container zuerst)."""
    m = len(groessen)
    ergebnis, aktuell = [], [0] * m

    def rec(i, rest):
        if i == m:
            if aktuell[j] >= 1 and all(aktuell[x] >= bedarf[x] or groessen[x] > rest for x in range(m)):
                ergebnis.append(tuple(aktuell))
                if len(ergebnis) > C.MUSTER_KNOTEN:
                    raise _Abbruch()
            return
        hoechst = min(bedarf[i], rest // groessen[i])
        for c in range(hoechst, -1, -1):
            if i == j and c == 0:
                continue
            aktuell[i] = c
            rec(i + 1, rest - c * groessen[i])
        aktuell[i] = 0

    rec(j, cap)
    ergebnis.sort(key=lambda mu: (-sum(c * g for c, g in zip(mu, groessen)), tuple(-c for c in mu)))
    return ergebnis


@dataclass(frozen=True)
class Loesung:
    muster: tuple         # je Container ein Muster (Vielfachheiten je Größe)
    anzahl: int           # Zahl der Container
    bewiesen: bool        # True: nachgewiesen die kleinste Zahl; False: Knotengrenze erreicht, beste gefundene Lösung
    knoten: int           # Zahl der besuchten Knoten der Tiefensuche (das Maß für den Aufwand)


def loese_gerundet(groessen, bedarf, cap: int, knotengrenze: int = C.KNOTEN_LIVE) -> Loesung:
    """Löst die gerundete Instanz exakt: `groessen` absteigend und verschieden, `bedarf[i]` Pakete der Größe i. Tiefensuche: Der nächste Container enthält ein Paket der größten noch nötigen Größe und ist
    bezüglich des Restbedarfs maximal; Schranke: bisherige Container plus L2 des Restbedarfs; Ausgangspunkt ist FFD auf der gerundeten Instanz. Bei Knotengrenze: beste gefundene Lösung, nicht bewiesen."""
    groessen = list(groessen)
    m = len(groessen)
    if m == 0:
        return Loesung((), 0, True, 0)
    liste = [(g, i) for i, (g, b) in enumerate(zip(groessen, bedarf)) for _ in range(b)]
    start = ffd([g for g, _ in liste], cap)
    beste = [[tuple(sum(1 for p in b if liste[p][1] == i) for i in range(m)) for b in start]]
    bestzahl = [len(start)]
    knoten = [0]
    besucht = {}

    def rec(rest, pfad):
        if knoten[0] >= knotengrenze:
            return
        knoten[0] += 1
        j = next((i for i in range(m) if rest[i] > 0), None)
        if j is None:
            if len(pfad) < bestzahl[0]:
                bestzahl[0] = len(pfad)
                beste[0] = list(pfad)
            return
        if len(pfad) + _untere_schranke(rest, groessen, cap) >= bestzahl[0]:
            return
        if besucht.get(rest, 10 ** 9) <= len(pfad):
            return
        besucht[rest] = len(pfad)
        for mu in _muster_mit(j, rest, groessen, cap):
            pfad.append(mu)
            rec(tuple(r - c for r, c in zip(rest, mu)), pfad)
            pfad.pop()
            if bestzahl[0] <= len(pfad) + _untere_schranke(rest, groessen, cap):
                break

    bewiesen = True
    try:
        rec(tuple(bedarf), [])
    except _Abbruch:
        bewiesen = False
    return Loesung(tuple(beste[0]), bestzahl[0], bewiesen and knoten[0] < knotengrenze, knoten[0])


# --- Das Schema ------------------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Schema:
    bins: tuple           # Container (Paketnummern) der fertigen Packung
    gross: tuple          # Nummern der großen Pakete, absteigend nach Größe
    klein: tuple          # Nummern der kleinen Pakete, absteigend nach Größe
    gruppen: tuple        # je Gruppe die Nummern ihrer Pakete (aus `gross`)
    k: int                # Gruppengröße
    klassen: tuple        # gerundete Größe je Gruppe
    verschieden: tuple    # verschiedene gerundete Größen, absteigend
    bedarf: tuple         # Zahl der Pakete je verschiedener gerundeter Größe
    muster: int           # Zahl der maximalen Muster der gerundeten Größen (höchstens C.MUSTER_GRENZE: bei dieser Zahl heißt es „mindestens“)
    gerundet: int         # Zahl der Container der gerundeten Instanz (kleinste gefundene)
    bewiesen: bool        # gerundete Instanz nachweislich exakt gelöst
    knoten: int           # Knoten der Tiefensuche
    behaelter: int        # Zahl der Container der fertigen Packung


def ist_gross(groesse: int, cap: int, eps: float) -> bool:
    """Ein Paket ist groß, wenn es mindestens eps mal Kapazität hat; exakt gerechnet mit eps auf vier Dezimalstellen (kein Gleitkomma-Gleichstand bei 0,3 mal 10 oder 0,1 mal 30)."""
    return groesse * 10_000 >= round(eps * 10_000) * cap


def gruppen_bilden(gross_sortiert, h: int):
    """Gruppen aus je k aufeinanderfolgenden Paketen (absteigend sortiert); gibt (k, Liste der Gruppen als Positionslisten in `gross_sortiert`) zurück."""
    n = len(gross_sortiert)
    if n == 0:
        return 0, []
    k = -(-n // max(1, h))
    return k, [list(range(a, min(a + k, n))) for a in range(0, n, k)]


def schema(sizes, cap: int, eps: float, h: int, knotengrenze: int = C.KNOTEN_LIVE) -> Schema:
    """Das Schema mit der Schwelle eps und der Gruppenzahl h; siehe das Modul."""
    if any(s <= 0 or s > cap for s in sizes):
        raise ValueError("Paketgröße muss zwischen 1 und der Kapazität liegen")
    if not 0 < eps < 1 or h < 1:
        raise ValueError("eps liegt zwischen 0 und 1, h ist mindestens 1")
    gross = sorted((i for i in range(len(sizes)) if ist_gross(sizes[i], cap, eps)), key=lambda i: (-sizes[i], i))
    klein = sorted((i for i in range(len(sizes)) if not ist_gross(sizes[i], cap, eps)), key=lambda i: (-sizes[i], i))
    k, pos = gruppen_bilden(gross, h)
    gruppen = [[gross[p] for p in g] for g in pos]
    klassen = [sizes[g[0]] for g in gruppen]                       # gerundete Größe = größtes Paket der Gruppe
    verschieden = sorted(set(klassen), reverse=True)
    bedarf = [sum(len(g) for g, kl in zip(gruppen, klassen) if kl == v) for v in verschieden]
    muster_zahl = muster_zaehlen(verschieden, cap) if verschieden else 0
    lsg = loese_gerundet(verschieden, bedarf, cap, knotengrenze)
    freie = {v: [] for v in verschieden}
    for g, kl in zip(gruppen, klassen):
        freie[kl] += g
    bins = []
    for mu in lsg.muster:
        inhalt = []
        for v, c in zip(verschieden, mu):
            for _ in range(c):
                if freie[v]:
                    inhalt.append(freie[v].pop(0))
        if inhalt:
            bins.append(inhalt)
    if any(freie.values()):
        raise RuntimeError("nicht alle großen Pakete untergebracht")
    last = [sum(sizes[i] for i in b) for b in bins]
    for i in klein:
        for b in range(len(bins)):
            if last[b] + sizes[i] <= cap:
                bins[b].append(i)
                last[b] += sizes[i]
                break
        else:
            bins.append([i])
            last.append(sizes[i])
    return Schema(tuple(tuple(b) for b in bins), tuple(gross), tuple(klein), tuple(tuple(g) for g in gruppen), k, tuple(klassen), tuple(verschieden), tuple(bedarf), muster_zahl, lsg.anzahl,
                  lsg.bewiesen, lsg.knoten, len(bins))


def theorie_gruppen(eps: float) -> int:
    """Gruppenzahl h = aufgerundet(1 / eps^2), die die Gütegrenze (1 + eps) des Schemas in der Rechnung der Demo verlangt."""
    return math.ceil(1 / eps ** 2 - 1e-9)
