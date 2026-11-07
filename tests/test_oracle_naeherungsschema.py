"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 30 Sekunden.

  Tiefensuche der gerundeten Instanz  gegen  (a) das exakte Optimum per Teilmengen-DP über die ausgeschriebenen Pakete (kleine Instanzen), (b) ein ganzzahliges Programm über alle maximalen Muster
                                             (scipy milp), eine ganz andere Methode.
  Maximale Muster                      gegen  die Aufzählung aller Vielfachheitsvektoren mit Prüfung der Maximalität; die Zählung gegen die Länge der Liste, die DP-Zählung aller Muster gegen die Aufzählung.
  Schema                               gegen  ein Nachrechnen aus den Teilergebnissen: gerundete Größen nie unter den echten, jedes große Paket in einem Platz, in den es passt, Ergebnis nie unter L2, bei k = 1 und
                                              ohne kleine Pakete gleich dem Optimum, obere Grenze gehalten.
  LP-Wert                              gegen  das LP über alle Muster, ausgeschrieben und mit linprog gelöst (ohne Spaltenerzeugung).
"""

import itertools
import random

import numpy as np
import pytest
from scipy.optimize import LinearConstraint, linprog, milp

import nsg_algorithm as A
from nsg_evaluation import grenze


def zufall(n, lo, hi, cap, seed):
    rng = random.Random(seed)
    return [rng.randint(max(1, int(lo * cap)), int(hi * cap)) for _ in range(n)]


# --- Tiefensuche gegen DP und gegen ein ganzzahliges Programm -----------------------------------------------------------------------------


def klassen_instanz(rng, m, cap):
    groessen = sorted({rng.randint(cap // 6, cap - 1) for _ in range(m)}, reverse=True)
    return groessen, [rng.randint(1, 3) for _ in groessen]


def test_tiefensuche_gegen_teilmengen_dp():
    rng = random.Random(11)
    geprueft = 0
    for _ in range(60):
        cap = rng.choice((10, 20, 30))
        groessen, bedarf = klassen_instanz(rng, rng.randint(1, 4), cap)
        ausgeschrieben = [g for g, b in zip(groessen, bedarf) for _ in range(b)]
        if len(ausgeschrieben) > 11:
            continue
        lsg = A.loese_gerundet(groessen, bedarf, cap, 100_000)
        assert lsg.bewiesen and lsg.anzahl == A.optimum(ausgeschrieben, cap, limit=11), (groessen, bedarf, cap)
        # die Muster decken den Bedarf genau oder mit Überschuss
        for j, b in enumerate(bedarf):
            assert sum(mu[j] for mu in lsg.muster) >= b
        geprueft += 1
    assert geprueft >= 40


def milp_optimum(groessen, bedarf, cap):
    muster = A.maximale_muster(groessen, cap)
    if not muster:
        return 0
    res = milp(c=np.ones(len(muster)), constraints=LinearConstraint(np.array(muster, dtype=float).T, lb=np.array(bedarf, dtype=float), ub=np.inf), integrality=np.ones(len(muster)), bounds=(0, np.inf))
    assert res.status == 0
    return round(res.fun)


def test_tiefensuche_gegen_ein_ganzzahliges_programm_ueber_alle_maximalen_muster():
    rng = random.Random(23)
    verschieden_viel = 0
    for _ in range(40):
        cap = rng.choice((100, 200))
        groessen, bedarf = klassen_instanz(rng, rng.randint(2, 7), cap)
        lsg = A.loese_gerundet(groessen, [b * 3 for b in bedarf], cap, 100_000)
        if not lsg.bewiesen:
            continue
        assert lsg.anzahl == milp_optimum(groessen, [b * 3 for b in bedarf], cap), (groessen, bedarf, cap)
        verschieden_viel += lsg.knoten > 1
    assert verschieden_viel >= 5                                  # in einigen Instanzen musste wirklich gesucht werden (mehr als der Wurzelknoten)


# --- Muster ----------------------------------------------------------------------------------------------------------------------------


def alle_vektoren(groessen, cap):
    grenzen = [cap // g for g in groessen]
    for v in itertools.product(*[range(b + 1) for b in grenzen]):
        if sum(c * g for c, g in zip(v, groessen)) <= cap:
            yield v


def test_maximale_muster_und_zaehlungen_gegen_die_aufzaehlung():
    rng = random.Random(5)
    for _ in range(40):
        cap = rng.choice((10, 20, 30))
        groessen = sorted({rng.randint(2, cap) for _ in range(rng.randint(1, 4))}, reverse=True)
        vektoren = list(alle_vektoren(groessen, cap))
        maximal = [v for v in vektoren if all(g > cap - sum(c * gg for c, gg in zip(v, groessen)) for g in groessen)]
        assert sorted(A.maximale_muster(groessen, cap)) == sorted(maximal), (groessen, cap)
        assert A.muster_zaehlen(groessen, cap, grenze=10 ** 9) == len(maximal)
        assert A.muster_zahl_alle(groessen, cap) == len(vektoren) - 1                # ohne das leere Muster


# --- Schema ----------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("eps,h", [(0.5, 4), (0.34, 3), (0.25, 4), (0.25, 8), (0.2, 5), (0.2, 25), (0.1, 12)])
def test_schema_nachgerechnet_aus_den_teilergebnissen(eps, h):
    for seed in range(12):
        n = random.Random(seed).choice((15, 30, 60))
        sizes = zufall(n, 0.05, 0.7, 1000, seed + 100)
        s = A.schema(sizes, 1000, eps, h, 20_000)
        assert A.container_pruefen(sizes, [list(b) for b in s.bins], 1000)
        # gerundete Größen: jede Gruppe wird auf ihr größtes Paket gerundet (nie unter den echten Größen)
        for grp, klasse in zip(s.gruppen, s.klassen):
            assert all(sizes[i] <= klasse for i in grp) and klasse == max(sizes[i] for i in grp)
        assert [len(g) for g in s.gruppen][:-1] == [s.k] * (len(s.gruppen) - 1) and sum(len(g) for g in s.gruppen) == len(s.gross)
        assert set(s.gross) | set(s.klein) == set(range(n)) and not set(s.gross) & set(s.klein)
        assert all(sizes[i] * 10_000 >= round(eps * 10_000) * 1000 for i in s.gross) and all(sizes[i] * 10_000 < round(eps * 10_000) * 1000 for i in s.klein)
        assert s.behaelter >= A.l2(sizes, 1000) and len(s.verschieden) <= h and s.behaelter >= s.gerundet
        if s.bewiesen:
            assert s.behaelter <= grenze(sum(sizes), 1000, eps, len(A.ffd(sizes, 1000)), s.k), (eps, h, seed)


def test_schema_mit_so_vielen_gruppen_wie_paketen_und_ohne_kleine_ist_das_optimum():
    rng = random.Random(7)
    geprueft = 0
    for _ in range(40):
        n = rng.randint(4, 11)
        cap = 100
        sizes = [rng.randint(10, 70) for _ in range(n)]
        s = A.schema(sizes, cap, 0.1, n, 100_000)                     # alle Pakete sind groß (ab 10), jede Gruppe ein Paket
        assert s.klein == () and s.k == 1 and s.bewiesen
        assert s.behaelter == A.optimum(sizes, cap, limit=11), (sizes,)
        geprueft += 1
    assert geprueft == 40


def test_schema_ist_deterministisch():
    sizes = zufall(40, 0.1, 0.5, 1000, 3)
    assert A.schema(sizes, 1000, 0.2, 10, 5000) == A.schema(sizes, 1000, 0.2, 10, 5000)


def test_gruppe_ein_container_je_gruppe_gibt_die_zusatzgrenze_k():
    """Die Behauptung der Grenze (gerundet höchstens Optimum plus k) an kleinen Instanzen mit bekanntem Optimum."""
    rng = random.Random(31)
    for _ in range(50):
        n = rng.randint(6, 11)
        sizes = [rng.randint(10, 60) for _ in range(n)]
        h = rng.randint(1, 5)
        s = A.schema(sizes, 100, 0.1, h, 100_000)
        opt = A.optimum(sizes, 100, limit=11)
        assert s.bewiesen and s.gerundet <= opt + s.k and s.behaelter >= opt, (sizes, h)


# --- LP-Wert ----------------------------------------------------------------------------------------------------------------------------


def lp_ausgeschrieben(sizes, cap):
    groessen = sorted(set(sizes))
    bedarf = np.array([sizes.count(g) for g in groessen], dtype=float)
    muster = [v for v in alle_vektoren(groessen, cap) if sum(v) > 0]
    res = linprog(np.ones(len(muster)), A_ub=-np.array(muster, dtype=float).T, b_ub=-bedarf, bounds=(0, None), method="highs")
    return float(res.fun)


def test_lp_wert_gegen_das_ausgeschriebene_lp():
    rng = random.Random(9)
    for _ in range(25):
        cap = rng.choice((20, 30, 40))
        sizes = [rng.randint(3, cap - 2) for _ in range(rng.randint(3, 12))]
        assert A.lp_wert(sizes, cap) == pytest.approx(lp_ausgeschrieben(sizes, cap), abs=1e-6), (sizes, cap)


def test_schranken_und_lp_nie_ueber_dem_optimum_und_l1_nie_ueber_dem_lp():
    rng = random.Random(13)
    for _ in range(30):
        sizes = [rng.randint(5, 60) for _ in range(rng.randint(5, 11))]
        opt = A.optimum(sizes, 100, limit=11)
        lp = A.lp_wert(sizes, 100)
        assert A.l1(sizes, 100) <= A.l2(sizes, 100) <= opt and sum(sizes) / 100 - 1e-9 <= lp <= opt + 1e-9 and A.lp_aufgerundet(lp) <= opt
