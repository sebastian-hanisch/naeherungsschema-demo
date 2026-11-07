"""Abbildungen: Die Balken, Stufen und Farben zeigen genau, was sie zeigen sollen (an der Mini-Instanz von Hand)."""

import nsg_algorithm as A
import nsg_constants as C
import nsg_evaluation as ev
import nsg_visualization as V


def _mini_schema(mini):
    sizes, cap = mini
    return sizes, cap, A.schema(sizes, cap, 0.3, 2)


def test_runden_zeigt_alle_pakete_absteigend_die_stufen_und_die_schwelle(mini):
    sizes, cap, s = _mini_schema(mini)
    fig = V.build_runden(sizes, cap, s, 0.3)
    balken, stufe = fig.data[0], fig.data[1]
    assert list(balken.y) == [8, 7, 6, 5, 4, 3, 2, 2, 1] and list(balken.x) == list(range(1, 10))
    assert list(balken.marker.color) == [V.gruppen_farbe(0)] * 3 + [V.gruppen_farbe(1)] * 3 + [C.COLOR_KLEIN] * 3
    assert list(stufe.x) == [0.5, 3.5, 3.5, 6.5] and list(stufe.y) == [8, 8, 5, 5]                      # zwei Gruppen: gerundet auf 8 und auf 5
    schwelle = fig.layout.shapes[0]
    assert schwelle.y0 == schwelle.y1 == 3.0                                                         # eps 0,3 mal Kapazität 10
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_runden_ohne_grosse_pakete_hat_keine_stufe():
    s = A.schema([3, 3, 3, 2], 10, 0.5, 4)
    fig = V.build_runden([3, 3, 3, 2], 10, s, 0.5)
    assert len(fig.data) == 1 and list(fig.data[0].marker.color) == [C.COLOR_KLEIN] * 4


def test_container_zeigt_pakete_gruppenfarben_und_freien_platz(mini):
    sizes, cap, s = _mini_schema(mini)
    fig = V.build_container(sizes, [list(b) for b in s.bins], cap, s)
    labels = list(fig.data[0].x)
    assert labels == ["C1", "C2", "C3", "C4", "C5"]
    schichten = len(fig.data) - 1                                                   # eine Schicht je Platz im größten Container, dazu der freie Platz
    assert schichten == 3 and list(fig.data[0].y) == [8, 7, 6, 5, 3] and list(fig.data[1].y) == [2, 2, 0, 4, 0] and list(fig.data[2].y) == [0, 1, 0, 0, 0]
    assert list(fig.data[0].marker.color) == [V.gruppen_farbe(0)] * 3 + [V.gruppen_farbe(1)] * 2
    assert list(fig.data[1].marker.color) == [C.COLOR_KLEIN, C.COLOR_KLEIN, "rgba(0,0,0,0)", V.gruppen_farbe(1), "rgba(0,0,0,0)"]
    assert list(fig.data[-1].y) == [0, 0, 4, 1, 7] and fig.layout.barmode == "stack"                # freier Platz: C3 6 von 10, C4 9 von 10, C5 3 von 10


def test_container_ohne_schema_ist_einfarbig_grau(mini):
    sizes, cap = mini
    fig = V.build_container(sizes, A.ffd(sizes, cap), cap)
    assert set(fig.data[0].marker.color) == {C.COLOR_FFD} and list(fig.data[-1].y) == [0, 0, 0, 2]


def test_vergleich_und_messung():
    fig = V.build_vergleich([("Schema", 5, "#111"), ("FFD", 4, "#222")])
    assert list(fig.data[0].x) == ["Schema", "FFD"] and list(fig.data[0].y) == [5, 4] and fig.layout.xaxis.fixedrange
    zeilen = {"ffd_ueber_l2": 0.4, "einstellungen": [{"eps": e, "h": h, "ueber_l2": 0.1 * i} for i, (e, h) in enumerate(C.EINSTELLUNGEN)]}
    fig = V.build_messung(zeilen, "Titel")
    assert list(fig.data[0].x)[:3] == ["0,5 / 4", "0,34 / 3", "0,34 / 6"] and len(fig.data[0].y) == 9 and fig.layout.shapes[0].y0 == 0.4 and fig.layout.yaxis.fixedrange


def test_abbildungen_zur_analyse_der_app():
    a = ev.analyse(ev.Settings())
    assert len(V.build_runden(list(a.inst.sizes), a.inst.cap, a.schema, a.eps).data) == 2
    fig = V.build_container(list(a.inst.sizes), [list(b) for b in a.schema.bins], a.inst.cap, a.schema)
    assert len(list(fig.data[0].x)) == a.schema.behaelter == 6
