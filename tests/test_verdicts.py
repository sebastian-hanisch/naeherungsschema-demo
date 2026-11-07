"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen (kleiner als nach Rundung auf zwei Stellen, Gleichstand) und jede genannte Zahl direkt."""

from dataclasses import replace

import nsg_algorithm as A
import nsg_constants as C
import nsg_evaluation as ev
from nsg_scenario import Instance

SIZES = [8, 7, 6, 5, 4, 3, 2, 2, 1]                  # Mini-Instanz der Tests: FFD 4, Schema (eps 0,3, h 2) 5, Optimum 4


def _a(eps_index=3, h=2, opt=4, lp=None, sizes=SIZES, cap=10, **aender):
    inst = Instance(tuple(sizes), cap)
    eps = C.EPS_WERTE[eps_index]
    sc = A.schema(list(sizes), cap, eps, h)
    ffd = A.ffd(list(sizes), cap)
    a = ev.Analysis(inst, eps, h, sc, tuple(tuple(b) for b in ffd), A.l1(list(sizes), cap), A.l2(list(sizes), cap), lp, opt, ev.theorie_gruppen(eps),
                    ev.grenze(sum(sizes), cap, eps, len(ffd), sc.k), ev.Settings(eps_index=eps_index, h=h))
    return replace(a, **aender)


def test_aktuell_schema_schlechter_ist_eine_warnung_mit_optimum():
    kind, text = ev.verdict_aktuell(_a())
    assert kind == "warning" and text == "Das Schema braucht **5** Container, FFD 4. Das Schema braucht hier 1 mehr als FFD: Die Rundung kostet. Das Optimum ist **4**."


def test_aktuell_gleich_und_besser():
    a = _a(sizes=[4, 4, 3, 3, 3, 3], eps_index=5, h=6, opt=2)           # eps 0,2: alle groß, k = 1: Schema 2, FFD 3
    kind, text = ev.verdict_aktuell(a)
    assert kind == "success" and text == "Das Schema braucht **2** Container, FFD 3. Das Schema ist hier besser als FFD. Das Optimum ist **2**."
    kind, text = ev.verdict_aktuell(_a(sizes=[5, 5, 5, 5], eps_index=3, h=2, opt=2))
    assert kind == "info" and text == "Das Schema braucht **2** Container, FFD 2. Beide gleich viele. Das Optimum ist **2**."


def test_aktuell_ohne_optimum_nennt_l2_und_ohne_grosse_pakete_ist_es_first_fit():
    kind, text = ev.verdict_aktuell(_a(opt=None))
    assert "Die Schranke L2 ist 4." in text and "Das Optimum" not in text
    kind, text = ev.verdict_aktuell(_a(sizes=[3, 3, 3, 2], eps_index=0, h=4, opt=2))
    assert kind == "info" and text == "Alle Pakete sind kleiner als 0,5 mal der Kapazität: Das Schema ist hier nur First Fit der absteigend sortierten Pakete und braucht **2** Container, FFD 2. Das Optimum ist **2**."


def test_aktuell_unbewiesene_gerundete_instanz_wird_genannt():
    a = _a()
    a = replace(a, schema=replace(a.schema, bewiesen=False, knoten=5000))
    assert ev.verdict_aktuell(a)[1].endswith(" Die gerundete Instanz ist nach 5000 Knoten nicht bewiesen exakt gelöst.")


def test_aufwand_verdikt_mit_den_zahlen_und_dem_k1_zweig():
    kind, text = ev.verdict_aufwand(_a())
    assert kind == "info"
    assert text == ("Von 9 Paketen sind **6** groß (ab 0,3 mal der Kapazität); sie bilden 2 Gruppen zu je höchstens 3 und haben **2** verschiedene gerundete Größen mit **2** maximalen Mustern; "
                    "die Tiefensuche brauchte 1 Knoten. Die Rechnung der Demo verlangt für eps = 0,3 aufgerundet 1 / eps² = **12** Gruppen; hier sind es 2.")
    kind, text = ev.verdict_aufwand(_a(h=6))
    assert text.endswith("Mit so vielen Gruppen ist jedes große Paket eine eigene (k = 1): Es wird nicht gerundet, das Schema löst die großen Pakete exakt.")
    assert ev.verdict_aufwand(_a(sizes=[2, 2], eps_index=0, h=3, opt=1))[1] == "Es gibt keine großen Pakete, also keine Gruppen und keine Muster."


def test_grenzverdikt_gehalten_unbewiesen_und_verletzt():
    kind, text = ev.verdict_grenze(_a())
    assert kind == "success" and text == "Obere Grenze dieser Instanz: max(FFD + k, aufgerundet(Volumen / ((1 − eps) Kapazität)) + 1) = max(4 + 3, …) = **7**; das Schema braucht 5. Die Grenze hält."
    a = _a()
    kind, text = ev.verdict_grenze(replace(a, schema=replace(a.schema, bewiesen=False)))
    assert kind == "info" and text.endswith("Die gerundete Instanz ist nicht bewiesen exakt gelöst, die Grenze gilt dann nicht.")
    kind, text = ev.verdict_grenze(replace(a, grenze=4))
    assert kind == "warning" and text.endswith("Die Grenze ist verletzt (das darf nicht vorkommen).")


def test_grenze_funktion_nimmt_das_groessere_der_beiden_zweige():
    assert ev.grenze(38, 10, 0.3, 4, 3) == 7 and ev.grenze(1000, 100, 0.5, 5, 1) == 21 and ev.grenze(10, 100, 0.2, 9, 4) == 13


# --- Messraster ----------------------------------------------------------------------------------------------------------------------------


def _e(eps, h, ueber, besser=0, gleich=40, schlechter=0, muster=10.0, knoten=100.0, knoten_max=500, unbewiesen=0, gross=20.0, k=2.0, bewiesen=40, grenze_ok=40, luft=3.0):
    return {"eps": eps, "h": h, "behaelter": 20 + ueber, "ueber_l2": ueber, "besser": besser, "gleich": gleich, "schlechter": schlechter, "muster": muster, "knoten": knoten, "knoten_max": knoten_max,
            "unbewiesen": unbewiesen, "gross": gross, "k": k, "bewiesen": bewiesen, "grenze_ok": grenze_ok, "luft": luft}


def _z(ffd_ueber=0.40, werte=None):
    werte = werte or [0.40, 0.41, 0.50, 0.55, 0.30, 0.45, 0.60, 0.50, 0.42]
    return {"verteilung": 0, "name": "mittlere Pakete", "n": 50, "instanzen": 40, "ffd": 16.0, "l2": 15.6, "ffd_ueber_l2": ffd_ueber,
            "einstellungen": [_e(eps, h, w) for (eps, h), w in zip(C.EINSTELLUNGEN, werte)]}


def test_messung_verdikt_erfolg_wenn_irgendeine_einstellung_im_mittel_besser_ist():
    z = _z()
    z["einstellungen"][4] = _e(0.25, 8, 0.30, besser=4, gleich=34, schlechter=2)
    kind, text = ev.verdict_messung(z)
    assert kind == "success"
    assert text == ("Für mittlere Pakete mit n = 50 liegt FFD im Mittel 0.40 Container über L2 (40 Instanzen); die neun Einstellungen des Schemas liegen zwischen 0.30 und 0.60. "
                    "Das beste Schema (eps 0,25, 8 Gruppen) gewinnt gegen FFD in 4, verliert in 2 Instanzen. In 1 von 9 Einstellungen ist das Schema im Mittel besser als FFD.")


def test_messung_verdikt_warnung_wenn_keine_einstellung_besser_ist_und_gleich_nach_rundung_zaehlt_nicht():
    z = _z(werte=[0.40, 0.41, 0.50, 0.55, 0.404, 0.45, 0.60, 0.50, 0.42])                 # 0,404 rundet auf 0,40: nicht besser als FFD 0,40
    kind, text = ev.verdict_messung(z)
    assert kind == "warning" and text.endswith("In keiner Einstellung ist das Schema im Mittel besser als FFD.")
    z = _z(ffd_ueber=0.406, werte=[0.40, 0.41, 0.50, 0.55, 0.30, 0.45, 0.60, 0.50, 0.42])  # FFD rundet auf 0,41: 0,40 und 0,30 sind besser
    assert ev.verdict_messung(z)[0] == "success" and "In 2 von 9" in ev.verdict_messung(z)[1]


def test_aufwand_raster_verdikt_mit_wachstum_und_unbewiesenen():
    z = _z()
    for e, (muster, knoten) in zip([x for x in z["einstellungen"] if x["eps"] == 0.2], ((16.9, 1030.0), (90.9, 3021.8), (633.8, 10870.6))):
        e["muster"], e["knoten"] = muster, knoten
    kind, text = ev.verdict_aufwand_raster(z)
    assert kind == "info"
    assert text == ("Für mittlere Pakete mit n = 50 wachsen bei eps = 0,2 die Muster der gerundeten Instanz mit 5 / 10 / 25 Gruppen im Mittel von 17 über 91 auf 634, "
                    "die Knoten der Tiefensuche von 1030 über 3022 auf 10871.")
    z["einstellungen"][5]["unbewiesen"] = 9
    z["einstellungen"][8]["unbewiesen"] = 18
    kind, text = ev.verdict_aufwand_raster(z)
    assert kind == "warning" and text.endswith("In 27 der 360 Läufe war die gerundete Instanz nach 10000 Knoten nicht bewiesen gelöst.")


def test_theorie_verdikt_nennt_die_schwellen_fuer_eine_million_und_10_hoch_12():
    zeilen = [{"eps": e, "h": ev.theorie_gruppen(e), "je_container": int(1 / e), "muster": m} for e, m in zip((0.5, 0.2, 0.1, 0.075, 0.05), (5, 252, 197949, 18558311, 180302225970))]
    kind, text = ev.verdict_theorie(zeilen)
    assert kind == "info"                                         # 1,8 mal 10^11 sind unter 10^12: kein zweiter Schwellwert
    zeilen[-1]["muster"] = 233007216880531891122960639811
    kind, text = ev.verdict_theorie(zeilen)
    assert kind == "warning" and "Über eine Million Muster gibt es ab eps = 0,075, über 10^12 ab eps = 0,05" in text and "2.33e+29" in text and "(Stellen: 30)" in text
    assert text.startswith("Mit aufgerundet 1 / eps² Gruppen hat die gerundete Instanz bei eps = 0,5 5 Muster und bei eps = 0,05")


def test_zeile_rechnet_mittel_und_zaehlungen_aus_den_summen():
    einst = [{"behaelter": 800, "besser": 4, "gleich": 40, "schlechter": 6, "muster": 500, "knoten": 2000, "knoten_max": 99, "unbewiesen": 3, "gross": 1000, "k": 120, "bewiesen": 47,
              "grenze_ok": 47, "luft": 188} for _ in C.EINSTELLUNGEN]
    daten = {"instanzen": 50, "cap": 1000, "theorie": {}, "zellen": {"mittel|50": {"referenz": {"ffd": 790, "l2": 770, "l1": 760}, "einstellung": einst}}}
    z = ev.zeile(0, 1, daten)
    assert z["n"] == 50 and z["instanzen"] == 50 and z["ffd"] == 15.8 and z["l2"] == 15.4 and z["ffd_ueber_l2"] == 0.4
    e = z["einstellungen"][0]
    assert (e["behaelter"], e["ueber_l2"], e["muster"], e["knoten"], e["gross"], e["k"], e["luft"]) == (16.0, 0.6, 10.0, 40.0, 20.0, 2.4, 4.0) and e["besser"] == 4 and e["unbewiesen"] == 3
    einst[0]["bewiesen"] = 0
    assert ev.zeile(0, 1, daten)["einstellungen"][0]["luft"] is None
