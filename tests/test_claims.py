"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (nsg_precomputed.json): jede Zelle mit n = 20 frisch gerechnet, bei allen Zellen die gespeicherte Stichprobe (die ersten Instanzen einzeln); alle Zellen vollständig prüft
  `python generate_precomputed.py --check` (parallel).
* Die Zahlen der Rechnung (Experiment 3) werden gegen Aufzählung und Schranke geprüft.
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
import math
from pathlib import Path

import pytest

import nsg_algorithm as A
import nsg_constants as C
import nsg_evaluation as ev
from nsg_scenario import raster_instanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))
KLEINE_ZELLEN = [(v, ni) for v, ni in ZELLEN if C.MESS_N[ni] <= 20]


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def alle():
    return {(v, ni): ev.zeile(v, ni) for v, ni in ZELLEN}


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == C.INSTANZEN == 50 and daten["cap"] == C.MESS_CAP == 1000 and daten["knoten_raster"] == C.KNOTEN_RASTER == 10_000
    assert set(daten["zellen"]) == {ev.zelle_schluessel(v, ni) for v, ni in ZELLEN} and len(ZELLEN) == 12
    assert set(daten["stichprobe"]) == set(daten["zellen"])
    assert set(daten["theorie"]) == {str(e) for e in C.THEORIE_EPS}
    for v, ni in ZELLEN:
        assert set(daten["stichprobe"][ev.zelle_schluessel(v, ni)]) == {str(j) for j in C.STICHPROBE_J}
        assert len(daten["zellen"][ev.zelle_schluessel(v, ni)]["einstellung"]) == len(C.EINSTELLUNGEN) == 9


@pytest.mark.parametrize("v,ni", KLEINE_ZELLEN)
def test_jede_zelle_mit_n_20_stimmt_mit_frischer_rechnung(v, ni):
    assert ev.messzelle(v, ni) == ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_stichprobe_stimmt_mit_frischer_rechnung_und_ist_teil_der_zelle(v, ni):
    daten = ev.vorberechnet()
    schluessel = ev.zelle_schluessel(v, ni)
    proben = daten["stichprobe"][schluessel]
    for j in (0,) if C.MESS_N[ni] >= 200 else C.STICHPROBE_J:                  # bei 200 Paketen reicht die erste Instanz (die anderen prüft --check mit der ganzen Zelle)
        assert ev.messzelle(v, ni, [j]) == proben[str(j)]
    ganze = daten["zellen"][schluessel]
    for j in C.STICHPROBE_J:                                                    # jede Stichprobe ist höchstens so groß wie die ganze Zelle (Summen) und deren Zählungen sind kleiner
        assert proben[str(j)]["referenz"]["ffd"] <= ganze["referenz"]["ffd"]
        for p, g in zip(proben[str(j)]["einstellung"], ganze["einstellung"]):
            assert p["behaelter"] <= g["behaelter"] and p["knoten_max"] <= g["knoten_max"] and p["bewiesen"] <= g["bewiesen"]


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_summen_der_zelle_sind_in_sich_stimmig(v, ni):
    z = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]
    k = C.INSTANZEN
    assert z["referenz"]["l1"] <= z["referenz"]["l2"] <= z["referenz"]["ffd"]
    for (eps, h), o in zip(C.EINSTELLUNGEN, z["einstellung"]):
        assert o["besser"] + o["gleich"] + o["schlechter"] == k
        assert o["bewiesen"] + o["unbewiesen"] == k and o["grenze_ok"] <= o["bewiesen"] and o["luft"] >= 0
        assert o["behaelter"] >= z["referenz"]["l2"]                                                  # nie unter der Schranke
        assert o["knoten_max"] <= C.KNOTEN_RASTER + 1 and o["knoten"] <= k * (C.KNOTEN_RASTER + 1)
        assert o["gross"] >= 0 and o["k"] >= 0


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_die_obere_grenze_haelt_in_jedem_bewiesen_geloesten_lauf(v, ni):
    z = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]
    assert all(o["grenze_ok"] == o["bewiesen"] for o in z["einstellung"])


def test_raster_instanzen_sind_fest_und_haben_die_richtige_form():
    for v, ni in ZELLEN:
        inst = raster_instanz(v, ni, 0)
        assert inst.n == C.MESS_N[ni] and inst.cap == C.MESS_CAP
        _name, _text, lo, hi = C.VERTEILUNGEN[v]
        assert all(max(1, int(lo * C.MESS_CAP)) <= s <= int(hi * C.MESS_CAP) for s in inst.sizes)


# --- Zahlen der Rechnung (Experiment 3) ----------------------------------------------------------------------------------------------------


def test_zaehlung_der_muster_stimmt_mit_der_aufzaehlung_bei_kleinen_eps():
    for eps, cap in ((0.5, 100), (0.4, 100), (0.34, 100)):
        groessen = ev.theorie_groessen(eps, ev.theorie_gruppen(eps), cap)
        zaehl = sum(1 for kombi in itertools.product(*[range(cap // g + 1) for g in groessen]) if 0 < sum(m * g for m, g in zip(kombi, groessen)) <= cap)
        assert A.muster_zahl_alle(groessen, cap) == zaehl


def test_zahl_der_muster_ist_hoechstens_die_binomialschranke_und_nie_mehr_als_floor_1_durch_eps_pakete_je_container():
    for eps in C.THEORIE_EPS:
        h = ev.theorie_gruppen(eps)
        je = math.floor(1 / eps + 1e-9)
        groessen = ev.theorie_groessen(eps, h, C.THEORIE_CAP)
        assert min(groessen) >= round(eps * C.THEORIE_CAP) and max(groessen) == C.THEORIE_CAP
        muster = ev.theorie_muster(eps)
        assert 0 < muster <= math.comb(len(groessen) + je, je) - 1                                      # Vielfachheiten mit höchstens je Paketen aus höchstens h Größen


def test_gespeicherte_theorie_stimmt_mit_der_zaehlung_fuer_kleine_eps_und_wachst():
    theorie = ev.vorberechnet()["theorie"]
    for e in (0.5, 0.4, 0.34, 0.3, 0.25, 0.2, 0.15, 0.1):                                               # die Zählung ist schnell genug
        assert int(theorie[str(e)]) == ev.theorie_muster(e)
    zeilen = ev.theorie_zeilen()
    assert [z["eps"] for z in zeilen] == list(C.THEORIE_EPS) and all(a["muster"] < b["muster"] for a, b in zip(zeilen, zeilen[1:]))
    assert zeilen[0]["muster"] == 5 and zeilen[-1]["muster"] > 10 ** 29


# --- README -----------------------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_steht_wortlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_readme_hat_keine_platzhalter_und_keine_mutationszahlen():
    for stoerer in ("TODO:", "{{", "TESTZAHL", "Mutation", "mutiert"):
        assert stoerer not in README.replace("<!-- TODO nach dem Deploy", ""), stoerer


def _alle_einstellungen():
    return [(v, ni, e, z) for (v, ni), z in alle().items() for e in z["einstellungen"]]


def _fett(text):
    return f"**{text}**" in README


def test_befund_laeufe_gegen_ffd_und_zellen_im_mittel():
    laeufe = [(e["besser"], e["gleich"], e["schlechter"]) for _, _, e, _ in _alle_einstellungen()]
    summe = [sum(x[i] for x in laeufe) for i in range(3)]
    assert sum(summe) == len(ZELLEN) * len(C.EINSTELLUNGEN) * C.INSTANZEN == 5400 and summe == [12, 2298, 3090]
    assert "**5400** Läufe" in README and _fett("12") and "2298 gleich viele" in README and _fett("3090")
    besser = [(v, ni, e["eps"], e["h"]) for v, ni, e, z in _alle_einstellungen() if round(e["ueber_l2"], 2) < round(z["ffd_ueber_l2"], 2)]
    assert len(besser) == 3 and len(ZELLEN) * len(C.EINSTELLUNGEN) == 108
    assert sorted(besser) == [(0, 0, 0.2, 10), (0, 0, 0.2, 25), (1, 0, 0.2, 25)] and all(C.MESS_N[ni] == 20 for _, ni, _, _ in besser)
    zellen_ohne = [k for k, z in alle().items() if not any(round(e["ueber_l2"], 2) < round(z["ffd_ueber_l2"], 2) for e in z["einstellungen"])]
    assert len(zellen_ohne) == 10 and "in **10** von 12 Zellen ist **keine**" in README and _fett("3") and "von 108 Kombinationen" in README


def test_befund_mittlere_pakete_mit_grossem_eps_sind_so_gut_wie_ffd():
    gleich = 0
    for ni in range(len(C.MESS_N)):
        z = ev.zeile(0, ni)
        for e in z["einstellungen"]:
            if (e["eps"], e["h"]) in ((0.5, 4), (0.34, 3), (0.34, 6)):
                assert (e["besser"], e["gleich"], e["schlechter"]) == (0, 50, 0)
                gleich += e["gleich"]
    assert gleich == 600 and "allen **600** Läufen" in README


def test_befund_rundung_kostet_bei_grossen_paketen():
    z = ev.zeile(1, C.MESS_N.index(100))
    ueber = {(e["eps"], e["h"]): e["ueber_l2"] for e in z["einstellungen"]}
    assert de(z["ffd_ueber_l2"]) == "0,56" and de(ueber[(0.25, 4)]) == "15,02" and de(ueber[(0.25, 8)]) == "7,46" and de(ueber[(0.25, 16)]) == "3,22" and de(ueber[(0.2, 25)]) == "2,14"
    assert "FFD 0,56 Container über L2, das Schema mit eps 0,25 und 4 Gruppen **15,02**, mit 8 Gruppen 7,46 und mit 16 Gruppen 3,22; auch mit eps 0,2 und 25 Gruppen noch 2,14" in README
    assert [de(ueber[(0.2, h)]) for h in (5, 10, 25)] == ["12,82", "6,14", "2,14"] and "**12,82 / 6,14 / 2,14**" in README
    assert ueber[(0.2, 5)] > ueber[(0.2, 10)] > ueber[(0.2, 25)] and ueber[(0.25, 4)] > ueber[(0.25, 8)] > ueber[(0.25, 16)]


def test_befund_ffd_liegt_nahe_an_l2():
    werte = [round(z["ffd_ueber_l2"], 2) for z in alle().values()]
    assert min(werte) == 0.08 and max(werte) == 1.14 and alle()[(0, 3)]["ffd_ueber_l2"] == pytest.approx(1.14) and "**0,08 bis 1,14**" in README


def test_befund_aufwand_wachst_mit_der_gruppenzahl():
    z = ev.zeile(0, C.MESS_N.index(50))
    e = [x for x in z["einstellungen"] if x["eps"] == 0.2]
    assert [x["h"] for x in e] == [5, 10, 25]
    assert [f"{x['muster']:.0f}" for x in e] == ["17", "84", "557"] and [f"{x['knoten']:.0f}" for x in e] == ["670", "2601", "5886"]
    assert "**17 / 84 / 557** Muster und **670 / 2601 / 5886** Knoten" in README


def test_befund_nicht_bewiesene_laeufe_und_obere_grenze():
    unb = sum(e["unbewiesen"] for _, _, e, _ in _alle_einstellungen())
    bew = sum(e["bewiesen"] for _, _, e, _ in _alle_einstellungen())
    ok = sum(e["grenze_ok"] for _, _, e, _ in _alle_einstellungen())
    assert unb == 739 and bew == 4661 and ok == bew and unb + bew == 5400
    assert "In **739** von 5400 Läufen" in README and "allen **4661** bewiesen gelösten Läufen" in README
    z = ev.zeile(0, C.MESS_N.index(200))
    assert sum(1 for e in z["einstellungen"] if e["unbewiesen"] == C.INSTANZEN) == 7 and "7 von 9 Einstellungen in **allen** 50 Läufen" in README
    luft = [e["luft"] for _, _, e, _ in _alle_einstellungen() if e["luft"] is not None]
    assert round(min(luft), 2) == 2.08 and "**mindestens 2,08**" in README


def test_befund_zahlen_der_rechnung_stehen_in_der_readme():
    muster = {z["eps"]: z["muster"] for z in ev.theorie_zeilen()}
    assert muster[0.1] == 197949 and muster[0.075] == 18558311 and muster[0.05] == 180302225970 and len(str(muster[0.02])) == 30 and muster[0.02] > 10 ** 29
    for text in ("**197.949**", "**18.558.311**", "**180.302.225.970**", "mehr als 10^29 (30 Stellen)"):
        assert text in README
    assert "| 0,1 | 100 | 10 | 197.949 |" in README and "| 0,02 | 2500 | 50 | 2,33e+29 (30 Stellen) |" in README


def test_handbeispiele_stehen_in_der_readme():
    erwartung = {0: (5, 5, [6, 5, 5, 5]), 1: (6, 5, [6, 6, 6, 5]), 2: (5, 5, [5, 5, 5, 5])}
    from nsg_scenario import beispiel
    for b, (ffd, opt, schema) in erwartung.items():
        sizes, cap = list(beispiel(b).sizes), beispiel(b).cap
        assert len(A.ffd(sizes, cap)) == ffd and A.optimum(sizes, cap) == opt
        assert [A.schema(sizes, cap, e, h).behaelter for e, h in ((0.25, 3), (0.25, 4), (0.25, 6), (0.1, 12))] == schema
        assert f"| {b + 1} | {ffd} | {opt} | " + " | ".join(map(str, schema)) + " |" in README


def test_tabellen_der_readme_stammen_aus_den_messzellen():
    for v, ni in ZELLEN:
        z = ev.zeile(v, ni)
        assert f"| {C.VERTEILUNG_KURZ[v]} | {z['n']} | {de(z['ffd_ueber_l2'])} | " + " | ".join(de(e["ueber_l2"]) for e in z["einstellungen"]) + " |" in README
        assert f"| {C.VERTEILUNG_KURZ[v]} | {z['n']} | " + " | ".join(f"{e['besser']} / {e['gleich']} / {e['schlechter']}" for e in z["einstellungen"]) + " |" in README
