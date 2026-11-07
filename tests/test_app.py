"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, stellt jede Auswahl
auf jeden ihrer Werte und die Zahlenfelder an ihre Grenzen und prüft, dass kein Python-Fehler auftritt (insbesondere `StreamlitDuplicateElementId`
bei mehreren Diagrammen ohne key= und `StreamlitAPIException` bei Auswahlen mit ungültigem Wert)."""

import os

from streamlit.testing.v1 import AppTest

import nsg_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
WUERFEL = "🎲 Neue Zufallsinstanz würfeln"


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texte(at):
    return [e.value for e in at.info] + [e.value for e in at.success] + [e.value for e in at.warning]


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_selectbox_value_does_not_raise():
    keys = [s.key for s in _fresh_app().selectbox]
    assert {"quelle_select", "verteilung_select", "eps_select", "exp_verteilung", "exp_n"} <= set(keys)
    werte = {"quelle_select": list(C.QUELLEN), "verteilung_select": list(range(len(C.VERTEILUNGEN))), "eps_select": list(range(len(C.EPS_WERTE))),
             "exp_verteilung": list(range(len(C.VERTEILUNGEN))), "exp_n": list(range(len(C.MESS_N)))}
    for key in keys:
        for wert in werte[key]:
            at = _fresh_app()
            at.selectbox(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_zahlenfelder_an_ihren_grenzen_loesen_keinen_fehler_aus():
    for key, werte in (("n_input", (C.N_MIN, 12, C.N_MAX)), ("seed_input", (0, C.SEED_MAX)), ("h_input", (C.H_MIN, 3, C.H_MAX))):
        for wert in werte:
            at = _fresh_app()
            at.selectbox(key="quelle_select").set_value(C.ZUFALL).run(timeout=TIMEOUT)
            at.number_input(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_wuerfeln_wechselt_vom_beispiel_zur_zufallsinstanz():
    at = _fresh_app()
    assert at.selectbox(key="quelle_select").value == 0
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == C.ZUFALL and not at.exception
    seed_vorher = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == C.ZUFALL and at.number_input(key="seed_input").value != seed_vorher


def test_standardansicht_zeigt_das_erwartete_verdikt():
    at = _fresh_app()
    texte = _texte(at)
    assert any("Das Schema braucht **6** Container, FFD 5. Das Schema braucht hier 1 mehr als FFD: Die Rundung kostet. Das Optimum ist **5**." in t for t in texte)
    assert any("Von 12 Paketen sind **8** groß (ab 0,25 mal der Kapazität); sie bilden 3 Gruppen zu je höchstens 3" in t for t in texte)
    assert any("Obere Grenze dieser Instanz:" in t and "Die Grenze hält." in t for t in texte)


def test_mehr_gruppen_aendern_das_ergebnis_wie_im_preset():
    at = _fresh_app()
    at.number_input(key="h_input").set_value(6).run(timeout=TIMEOUT)
    assert not at.exception and any("Das Schema braucht **5** Container, FFD 5. Beide gleich viele." in t for t in _texte(at))


def test_expander_und_experimente_stehen_unter_ihren_namen():
    at = _fresh_app()
    labels = [e.label for e in at.expander]
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels
    markdown = [m.value for m in at.markdown]
    for titel in ("### Experiment 1: Was liefert das Schema gegen FFD?", "### Experiment 2: Wie groß wird der Aufwand? (gemessen)",
                  "### Experiment 3: Wie groß werden die Zahlen, wenn man es so genau macht, wie die Rechnung verlangt? (Rechnung)", "### Experiment 4: Was sagt die obere Grenze?"):
        assert any(titel in m for m in markdown), titel
