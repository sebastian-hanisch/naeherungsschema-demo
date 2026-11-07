"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen, jeder Hilfetext stimmt mit der Rechnung überein."""

import nsg_constants as C
import nsg_evaluation as ev
import nsg_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_defaults_of_the_widgets_equal_the_default_settings():
    s = ev.Settings()
    schluessel = ("quelle_select", "verteilung_select", "n_input", "seed_input", "eps_select", "h_input")
    assert [P.SETTING_SPECS[k].default for k in schluessel] == [s.quelle, s.verteilung, s.n, s.seed, s.eps_index, s.h]


def _a(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_presets_behaupten_nur_was_stimmt():
    eins = _a("Beispiel 1: eps 0,25, 3 Gruppen")
    assert (eins.schema.behaelter, len(eins.ffd), eins.opt, len(eins.schema.gross), len(eins.schema.verschieden)) == (6, 5, 5, 8, 3)
    h1 = C.PRESET_HELP["Beispiel 1: eps 0,25, 3 Gruppen"]
    assert "das Optimum ist 5 und FFD findet es" in h1 and "acht großen Pakete auf nur drei Größen und braucht 6" in h1
    zwei = _a("Beispiel 1: eps 0,25, 6 Gruppen")
    assert zwei.schema.behaelter == 5 and "braucht wieder 5" in C.PRESET_HELP["Beispiel 1: eps 0,25, 6 Gruppen"]
    drei = _a("Beispiel 2: eps 0,1, 12 Gruppen (ohne Rundung)")
    assert (drei.schema.behaelter, len(drei.ffd), drei.opt, drei.schema.k, len(drei.schema.gross)) == (5, 6, 5, 1, 12) and drei.schema.bewiesen
    h3 = C.PRESET_HELP["Beispiel 2: eps 0,1, 12 Gruppen (ohne Rundung)"]
    assert "FFD braucht 6, das Optimum ist 5" in h3 and "mit zwölf Gruppen ist jedes Paket eine eigene Gruppe".lower() in h3.lower() and "exakt: 5, besser als FFD" in h3
    vier = _a("Beispiel 2: eps 0,25, 6 Gruppen")
    assert vier.schema.behaelter == 6 == len(vier.ffd) and "6 Container wie FFD" in C.PRESET_HELP["Beispiel 2: eps 0,25, 6 Gruppen"]
    fuenf = _a("Zufällig, 30 mittlere Pakete, eps 0,2, 25 Gruppen")
    assert (fuenf.schema.behaelter, len(fuenf.ffd), fuenf.schema.knoten, fuenf.theorie_h, fuenf.inst.n) == (10, 10, 83, 25, 30)
    h5 = C.PRESET_HELP["Zufällig, 30 mittlere Pakete, eps 0,2, 25 Gruppen"]
    assert "schon 83 Knoten" in h5 and "beide 10" in h5 and "(10 bis 50 % der Kapazität)" in h5 and "so vielen, wie die Rechnung der Demo für eps = 0,2 verlangt" in h5
