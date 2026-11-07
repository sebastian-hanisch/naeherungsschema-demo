"""Kern an der Mini-Instanz von Hand und an den Handbeispielen der App (DEMO-PLAYBOOK §1b).

Handrechnung Mini-Instanz (Größen 8, 7, 6, 5, 4, 3, 2, 2, 1, Kapazität 10, Gesamtgröße 38):
  FFD: 8 -> C1; 7 -> C2; 6 -> C3; 5 -> C4; 4 -> C3 (6 + 4); 3 -> C2 (7 + 3); 2 -> C1 (8 + 2); 2 -> C4 (5 + 2); 1 -> C4 (7 + 1 = 8).   => [[0, 6], [1, 5], [2, 4], [3, 7, 8]], 4 Container
  L1 = aufgerundet(38 / 10) = 4, L2 = 4, Optimum 4.
Schema mit eps = 0,3 und h = 2 Gruppen:
  1. Klein sind die Pakete unter 3: die 2, 2 und 1 (Nummern 6, 7, 8). Groß: 8, 7, 6, 5, 4, 3 (Nummern 0 bis 5; ein Paket der Größe 3 ist gerade groß).
  2. Sechs große Pakete in zwei Gruppen: k = 3, Gruppe 1 = 8, 7, 6, gerundet auf 8; Gruppe 2 = 5, 4, 3, gerundet auf 5. Gerundete Instanz: drei Pakete der Größe 8, drei der Größe 5.
  3. Maximale Muster der Größen (8, 5): (1, 0) (Rest 2, kein weiteres Paket passt) und (0, 2) (genau voll); (0, 1) ist nicht maximal, ein zweites 5 passt. Drei 8er brauchen drei Container;
     drei 5er zwei (ein Muster (0, 2) und ein Container mit einer 5): gerundet 5 Container. Die Schranke L2 der gerundeten Instanz ist 5 (drei 8er allein, zwei 5er brauchen nach den Lücken noch
     zwei Container), also ist der Wurzelknoten schon bewiesen: 1 Knoten.
  4. Zurück: Die Muster in der Reihenfolge der Suche (1, 0), (1, 0), (1, 0), (0, 2), (0, 1): C1 bekommt das Paket 0 (8), C2 Paket 1 (7), C3 Paket 2 (6); C4 die ersten zwei der Gruppe 2 (Pakete 3 und 4: 5 + 4),
     C5 das Paket 5 (3).
  5. Klein (absteigend: 2, 2, 1): 2 -> C1 (8 + 2 = 10); 2 -> C2 (7 + 2 = 9); 1 -> C2 (9 + 1 = 10).   => [[0, 6], [1, 7, 8], [2], [3, 4], [5]], 5 Container (FFD 4)
Obere Grenze: max(FFD + k, aufgerundet(38 / (0,7 mal 10)) + 1) = max(4 + 3, aufgerundet(5,43) + 1 = 7) = 7; das Schema braucht 5.
Gruppenzahl der Rechnung: aufgerundet(1 / eps^2): eps 0,5 -> 4, 0,4 -> 7 (6,25), 0,34 -> 9 (8,65), 0,3 -> 12 (11,1), 0,25 -> 16, 0,2 -> 25, 0,15 -> 45 (44,4), 0,1 -> 100.
Tiefensuche an einer Instanz, in der FFD verliert: Größen (4, 3) mit den Mengen (2, 4), Kapazität 10: FFD 4 + 4, 3 + 3 + 3, 3 gibt 3 Container, das Optimum ist 2 mit (1, 2) zweimal (4 + 3 + 3 = 10). Muster mit einer
  4: (1, 2) (voll) und (2, 0) (Rest 2, die 3 passt nicht); nach Füllung zuerst (1, 2). Knoten: Wurzel, ein Kind, das Ziel = 3; danach bricht die Suche ab, weil 2 Container die Schranke erreichen."""

import pytest

import nsg_algorithm as A
import nsg_constants as C


def test_ffd_und_die_schranken_der_mini_instanz(mini):
    sizes, cap = mini
    assert A.ffd(sizes, cap) == [[0, 6], [1, 5], [2, 4], [3, 7, 8]]
    assert A.l1(sizes, cap) == 4 and A.l2(sizes, cap) == 4 and A.optimum(sizes, cap) == 4
    assert A.container_pruefen(sizes, A.ffd(sizes, cap), cap)


def test_gross_und_klein_mit_exakter_schwelle():
    assert A.ist_gross(3, 10, 0.3) and not A.ist_gross(2, 10, 0.3)
    assert A.ist_gross(3, 30, 0.1)                      # 0,1 mal 30 ist in Gleitkomma 3,0000000000000004: hier exakt gerechnet
    assert A.ist_gross(34, 100, 0.34) and not A.ist_gross(33, 100, 0.34) and A.ist_gross(340, 1000, 0.34) and not A.ist_gross(339, 1000, 0.34)
    assert A.ist_gross(50, 100, 0.5) and not A.ist_gross(49, 100, 0.5)


def test_gruppen_bilden_von_hand():
    assert A.gruppen_bilden([10, 9, 8, 7, 6, 5, 4], 3) == (3, [[0, 1, 2], [3, 4, 5], [6]])
    assert A.gruppen_bilden([10, 9, 8, 7], 4) == (1, [[0], [1], [2], [3]])
    assert A.gruppen_bilden([10, 9, 8, 7], 9) == (1, [[0], [1], [2], [3]])                  # mehr Gruppen als Pakete: jedes Paket eine Gruppe
    assert A.gruppen_bilden([10, 9, 8, 7], 1) == (4, [[0, 1, 2, 3]])
    assert A.gruppen_bilden([], 3) == (0, [])


def test_maximale_muster_und_ihre_zahlen_von_hand():
    assert A.maximale_muster([8, 5], 10) == [(1, 0), (0, 2)]
    assert A.maximale_muster([6, 4, 3], 10) == [(1, 1, 0), (1, 0, 1), (0, 2, 0), (0, 1, 2), (0, 0, 3)]
    assert A.muster_zaehlen([8, 5], 10) == 2 and A.muster_zaehlen([6, 4, 3], 10) == 5
    assert A.muster_zaehlen([6, 4, 3], 10, grenze=3) == 3                              # bei der Grenze hört das Zählen auf
    assert A.muster_zahl_alle([8, 5], 10) == 3 and A.muster_zahl_alle([6, 4, 3], 10) == 10      # alle Muster ohne das leere: (8), (5), (5, 5) und die zehn des zweiten Beispiels
    assert A.maximale_muster([], 10) == [()]                                           # ohne Größen gibt es genau ein (leeres) Muster


def test_gerundete_instanz_von_hand_exakt_gelöst():
    lsg = A.loese_gerundet([8, 5], [3, 3], 10)
    assert lsg.muster == ((1, 0), (1, 0), (1, 0), (0, 2), (0, 1)) and lsg.anzahl == 5 and lsg.bewiesen and lsg.knoten == 1


def test_tiefensuche_findet_das_optimum_wo_ffd_verliert():
    assert len(A.ffd([4, 4, 3, 3, 3, 3], 10)) == 3
    lsg = A.loese_gerundet([4, 3], [2, 4], 10)
    assert lsg.muster == ((1, 2), (1, 2)) and lsg.anzahl == 2 and lsg.bewiesen and lsg.knoten == 3


def test_schema_auf_der_mini_instanz_von_hand(mini):
    sizes, cap = mini
    s = A.schema(sizes, cap, 0.3, 2)
    assert s.gross == (0, 1, 2, 3, 4, 5) and s.klein == (6, 7, 8)
    assert s.gruppen == ((0, 1, 2), (3, 4, 5)) and s.k == 3 and s.klassen == (8, 5) and s.verschieden == (8, 5) and s.bedarf == (3, 3)
    assert s.muster == 2 and s.gerundet == 5 and s.bewiesen and s.knoten == 1
    assert s.bins == ((0, 6), (1, 7, 8), (2,), (3, 4), (5,)) and s.behaelter == 5
    assert A.container_pruefen(sizes, [list(b) for b in s.bins], cap)


def test_obere_grenze_der_mini_instanz_von_hand(mini):
    from nsg_evaluation import grenze

    sizes, cap = mini
    assert grenze(sum(sizes), cap, 0.3, 4, 3) == 7                                    # max(4 + 3, aufgerundet(38 / 7) + 1 = 7)
    assert grenze(100, 10, 0.5, 5, 1) == 21 and grenze(100, 10, 0.5, 30, 2) == 32       # 100 / 5 = 20, +1; FFD + k = 32
    assert A.schema(sizes, cap, 0.3, 2).behaelter <= 7


def test_theorie_gruppen_von_hand():
    assert [A.theorie_gruppen(e) for e in (0.5, 0.4, 0.34, 0.3, 0.25, 0.2, 0.15, 0.1)] == [4, 7, 9, 12, 16, 25, 45, 100]


def test_schema_ohne_grosse_pakete_ist_first_fit_der_kleinen():
    s = A.schema([3, 3, 3, 2], 10, 0.5, 4)
    assert s.gross == () and s.klein == (0, 1, 2, 3) and s.gruppen == () and s.k == 0 and s.muster == 0 and s.gerundet == 0
    assert s.bins == ((0, 1, 2), (3,)) and s.behaelter == 2 and s.bewiesen


def test_schema_ohne_kleine_pakete_ist_die_exakte_loesung():
    s = A.schema([4, 4, 3, 3, 3, 3], 10, 0.2, 6)               # k = 1: jede Größe für sich, keine Rundung
    assert s.klein == () and s.k == 1 and s.behaelter == 2 and s.gerundet == 2 and len(A.ffd([4, 4, 3, 3, 3, 3], 10)) == 3


def test_schema_auf_dem_handbeispiel_der_konstanten():
    beispiele = {0: (22, [(0.25, 3, 6), (0.25, 4, 5), (0.25, 6, 5), (0.1, 12, 5)]), 1: (17, [(0.25, 3, 6), (0.25, 4, 6), (0.25, 6, 6), (0.1, 12, 5)])}
    for index, (_seed, faelle) in beispiele.items():
        sizes, cap = C.BEISPIELE[index]
        for eps, h, erwartet in faelle:
            s = A.schema(list(sizes), cap, eps, h)
            assert s.behaelter == erwartet and s.bewiesen, (index, eps, h)
    assert [len(A.ffd(list(C.BEISPIELE[i][0]), 100)) for i in (0, 1, 2)] == [5, 6, 5] and [A.optimum(list(C.BEISPIELE[i][0]), 100) for i in (0, 1, 2)] == [5, 5, 5]
    assert A.schema(list(C.BEISPIELE[2][0]), 100, 0.5, 4).behaelter == 5


def test_lp_wert_von_hand():
    # Größen 4 (viermal) und 3 (einmal), Kapazität 10: Muster (4, 4), (4, 3, 3), (3, 3, 3); Muster dürfen eine Größe öfter enthalten, als sie vorkommt (Standard des Schnittproblems).
    # Mit dem Muster (4, 3, 3) im Gewicht 0,5 (deckt eine halbe Vier und die Drei) und (4, 4) im Gewicht 1,75 (deckt 3,5 Vieren) ist der Wert 2,25; ein Muster nur aus Paketen, die es gibt (4, 3), käme auf 2,5.
    assert A.lp_wert([4, 4, 4, 4, 3], 10) == pytest.approx(2.25)
    assert A.lp_wert([], 10) == 0.0 and A.lp_wert([5, 5], 10) == pytest.approx(1.0) and A.lp_wert([6, 6], 10) == pytest.approx(2.0)
    assert A.lp_aufgerundet(2.25) == 3 and A.lp_aufgerundet(3.0000004) == 3 and A.lp_aufgerundet(3.01) == 4


def test_ungueltige_eingaben_werden_abgelehnt(mini):
    sizes, cap = mini
    with pytest.raises(ValueError):
        A.schema([11], 10, 0.3, 2)
    with pytest.raises(ValueError):
        A.schema([0, 3], 10, 0.3, 2)
    with pytest.raises(ValueError):
        A.schema(sizes, cap, 0.0, 2)
    with pytest.raises(ValueError):
        A.schema(sizes, cap, 1.0, 2)
    with pytest.raises(ValueError):
        A.schema(sizes, cap, 0.3, 0)
    with pytest.raises(ValueError):
        A.ffd([11], 10)
