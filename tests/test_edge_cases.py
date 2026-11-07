"""Randfälle: leere Eingabe, ein Paket, alle klein, alle groß, Paket gleich Kapazität, mehr Gruppen als Pakete, Knotengrenze, ungültige Eingaben, Grenzen der Regler."""

import pytest

import nsg_algorithm as A
import nsg_constants as C
import nsg_evaluation as ev
from nsg_scenario import Instance, live_instanz, raster_instanz, raster_seed, zufallsinstanz


def test_leere_eingabe():
    s = A.schema([], 10, 0.3, 3)
    assert s.bins == () and s.behaelter == 0 and s.gross == () and s.klein == () and s.muster == 0 and s.bewiesen
    assert A.ffd([], 10) == [] and A.l1([], 10) == 0 and A.l2([], 10) == 0 and A.optimum([], 10) == 0 and A.lp_wert([], 10) == 0.0


def test_ein_paket_gross_und_klein():
    gross = A.schema([7], 10, 0.3, 3)
    assert gross.bins == ((0,),) and gross.gruppen == ((0,),) and gross.k == 1 and gross.behaelter == 1
    klein = A.schema([2], 10, 0.3, 3)
    assert klein.bins == ((0,),) and klein.gross == () and klein.klein == (0,) and klein.behaelter == 1


def test_paket_gleich_der_kapazitaet_hat_einen_eigenen_container():
    s = A.schema([10, 10, 4, 3], 10, 0.3, 2)
    assert A.container_pruefen([10, 10, 4, 3], [list(b) for b in s.bins], 10) and s.behaelter == 3          # zwei volle Container, dann 4 + 3


def test_nur_kleine_pakete_sind_first_fit_absteigend_und_alle_grossen_sind_das_exakte_optimum():
    sizes = [2, 2, 2, 1, 1, 1, 1]                                   # Summe 10: genau ein Container
    s = A.schema(sizes, 10, 0.5, 4)
    assert s.gross == () and s.bins == ((0, 1, 2, 3, 4, 5, 6),) and s.behaelter == 1
    assert A.schema(sizes + [1], 10, 0.5, 4).bins == ((0, 1, 2, 3, 4, 5, 6), (7,))
    alle_gross = A.schema([6, 5, 5, 4, 4, 3], 10, 0.2, 6)
    assert alle_gross.klein == () and alle_gross.behaelter == A.optimum([6, 5, 5, 4, 4, 3], 10)


def test_mehr_gruppen_als_grosse_pakete_ist_dasselbe_wie_genau_so_viele():
    sizes = [9, 8, 7, 6, 5, 4]
    a, b, c = A.schema(sizes, 10, 0.3, 6), A.schema(sizes, 10, 0.3, 30), A.schema(sizes, 10, 0.3, 60)
    assert a == b == c and a.k == 1 and len(a.gruppen) == 6


def test_eine_gruppe_rundet_alle_grossen_pakete_auf_das_groesste():
    s = A.schema([9, 8, 7, 6, 5, 4], 10, 0.3, 1)
    assert s.k == 6 and s.klassen == (9,) and s.verschieden == (9,) and s.bedarf == (6,) and s.behaelter == 6          # sechs Pakete der Größe 9: je ein Container


def test_gleiche_groessen_in_verschiedenen_gruppen_werden_zusammengefasst():
    s = A.schema([5, 5, 5, 5, 5, 5], 10, 0.3, 3)
    assert len(s.gruppen) == 3 and s.klassen == (5, 5, 5) and s.verschieden == (5,) and s.bedarf == (6,) and s.behaelter == 3


def test_knotengrenze_macht_die_gerundete_instanz_unbewiesen_aber_liefert_eine_packung():
    sizes = zufallsinstanz(0.1, 0.5, 100, 4, 1000).sizes
    s = A.schema(list(sizes), 1000, 0.2, 25, 3)
    assert not s.bewiesen and s.knoten == 3 and A.container_pruefen(list(sizes), [list(b) for b in s.bins], 1000)
    gross = A.schema(list(sizes), 1000, 0.2, 25, 10 ** 6)
    assert gross.bewiesen or gross.knoten == 10 ** 6


def test_zu_viele_muster_in_einem_knoten_brechen_die_suche_ab():
    sizes = list(zufallsinstanz(0.1, 0.5, 60, 2, 1000).sizes)
    s = A.schema(sizes, 1000, 0.1, 60, 10 ** 9)
    assert A.container_pruefen(sizes, [list(b) for b in s.bins], 1000) and s.muster <= C.MUSTER_GRENZE
    assert A.muster_zaehlen(list(s.verschieden), 1000) == s.muster


def test_ungueltige_instanzen_werden_abgelehnt():
    for sizes, cap in (((0, 3), 10), ((11,), 10), ((3.5,), 10), (("a",), 10), ((3,), 0)):
        with pytest.raises(ValueError):
            Instance(sizes, cap)


def test_zufallsinstanzen_und_raster_seeds():
    for v, (_name, _text, lo, hi) in enumerate(C.VERTEILUNGEN):
        for n in (C.N_MIN, C.N_MAX):
            inst = live_instanz(v, n, 5)
            assert inst.n == n and all(max(1, int(lo * C.CAP)) <= s <= int(hi * C.CAP) for s in inst.sizes) and inst.cap == C.CAP
    assert len({raster_seed(v, ni, j) for v in range(3) for ni in range(4) for j in range(C.INSTANZEN)}) == 3 * 4 * C.INSTANZEN
    assert raster_instanz(1, 2, 3).n == C.MESS_N[2] and raster_instanz(1, 2, 3).cap == C.MESS_CAP and raster_instanz(1, 2, 3) == raster_instanz(1, 2, 3)


def test_analyse_an_den_grenzen_der_regler():
    for quelle in C.QUELLEN:
        for eps_index in (0, len(C.EPS_WERTE) - 1):
            for h in (C.H_MIN, 7, C.H_MAX):
                a = ev.analyse(ev.Settings(quelle, 2, C.N_MIN if quelle == C.ZUFALL else 12, C.SEED_MAX if h == 7 else 0, eps_index, h))
                assert A.container_pruefen(list(a.inst.sizes), [list(b) for b in a.schema.bins], a.inst.cap) and a.schema.behaelter >= a.l2
                assert (a.opt is None) == (a.inst.n > C.OPT_LIMIT) and (a.lp is None) == (a.inst.n > C.LP_LIMIT)
    a = ev.analyse(ev.Settings(C.ZUFALL, 0, C.N_MAX, 1, 7, C.H_MAX))                     # größte Live-Instanz, feinste Einstellung
    assert A.container_pruefen(list(a.inst.sizes), [list(b) for b in a.schema.bins], a.inst.cap) and a.opt is None and a.lp is None


def test_theorie_zeilen_aus_den_gespeicherten_daten_sind_ganze_zahlen_und_wachsen():
    zeilen = ev.theorie_zeilen()
    assert [z["eps"] for z in zeilen] == list(C.THEORIE_EPS) and all(isinstance(z["muster"], int) for z in zeilen)
    assert all(a["muster"] <= b["muster"] for a, b in zip(zeilen, zeilen[1:]))
