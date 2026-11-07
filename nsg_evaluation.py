"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in nsg_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import nsg_algorithm as A
import nsg_constants as C
from nsg_scenario import Instance, quelle_instanz, raster_instanz

PRECOMPUTED = Path(__file__).resolve().parent / "nsg_precomputed.json"


@dataclass(frozen=True)
class Settings:
    quelle: int = 0
    verteilung: int = 0
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    eps_index: int = 4          # Index in C.EPS_WERTE (0,25)
    h: int = 3                  # Zahl der Gruppen


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    eps: float
    h: int
    schema: A.Schema
    ffd: tuple            # Container der Packung von FFD
    l1: int
    l2: int
    lp: object            # LP-Wert (float) oder None, wenn die Instanz live zu groß ist
    opt: object           # Optimum (int) oder None bei mehr als OPT_LIMIT Paketen
    theorie_h: int        # Gruppenzahl aufgerundet(1 / eps^2) der Rechnung der Demo
    grenze: int           # obere Grenze max(FFD + k, aufgerundet(Volumen / ((1 - eps) cap)) + 1) für die Zahl der Container des Schemas
    settings: Settings


def eps_text(eps: float) -> str:
    return f"{eps:g}".replace(".", ",")


def theorie_gruppen(eps: float) -> int:
    return A.theorie_gruppen(eps)


def grenze(volumen: int, cap: int, eps: float, ffd_zahl: int, k: int) -> int:
    """Obere Grenze für die Containerzahl des Schemas, wenn die gerundete Instanz exakt gelöst ist: Entweder öffnen die kleinen Pakete keinen neuen Container; dann ist die Zahl höchstens die der gerundeten
    Instanz, und die ist höchstens das Optimum plus k, also höchstens FFD plus k (die k Pakete der größten Gruppe in je einem eigenen Container, alle anderen passen in eine Packung der Originalpakete).
    Oder sie öffnen einen: dann sind alle Container bis auf den letzten über (1 - eps) cap gefüllt, die Zahl ist höchstens aufgerundet(Volumen / ((1 - eps) cap)) + 1."""
    return max(ffd_zahl + k, math.ceil(volumen / ((1 - eps) * cap) - 1e-9) + 1)


def analyse(s: Settings) -> Analysis:
    inst = quelle_instanz(s.quelle, s.verteilung, s.n, s.seed)
    sizes = list(inst.sizes)
    eps = C.EPS_WERTE[s.eps_index]
    schema = A.schema(sizes, inst.cap, eps, s.h, C.KNOTEN_LIVE)
    assert A.container_pruefen(sizes, [list(b) for b in schema.bins], inst.cap)
    ffd = A.ffd(sizes, inst.cap)
    lp = A.lp_wert(sizes, inst.cap) if inst.n <= C.LP_LIMIT else None
    return Analysis(inst, eps, s.h, schema, tuple(tuple(b) for b in ffd), A.l1(sizes, inst.cap), A.l2(sizes, inst.cap), lp, A.optimum(sizes, inst.cap), theorie_gruppen(eps),
                    grenze(sum(sizes), inst.cap, eps, len(ffd), schema.k), s)


def theorie_groessen(eps: float, h: int, cap: int) -> list:
    """h gleichmäßig zwischen eps mal cap und cap verteilte Größen (absteigend, verschieden): die Größen, mit denen die Rechnung der Demo die Zahl der Muster zählt."""
    if h == 1:
        return [cap]
    return sorted({round(eps * cap + i * (cap - eps * cap) / (h - 1)) for i in range(h)}, reverse=True)


@lru_cache(maxsize=None)
def theorie_muster(eps: float, cap: int = C.THEORIE_CAP) -> int:
    """Zahl aller Muster, wenn die gerundeten Größen gleichmäßig zwischen eps mal cap und cap liegen und es aufgerundet(1 / eps^2) Gruppen gibt (Zählung per DP, ohne Aufzählung)."""
    return A.muster_zahl_alle(theorie_groessen(eps, theorie_gruppen(eps), cap), cap)


def theorie_zeilen(daten: dict | None = None) -> list:
    """Experiment 2: je eps die Gruppenzahl der Rechnung, die höchste Zahl großer Pakete je Container und die Zahl der Muster (aus den vorberechneten Daten, als ganze Zahlen)."""
    daten = daten or vorberechnet()
    return [{"eps": e, "h": theorie_gruppen(e), "je_container": math.floor(1 / e + 1e-9), "muster": int(daten["theorie"][str(e)])} for e in C.THEORIE_EPS]


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def verdict_aktuell(a: Analysis) -> tuple[str, str]:
    """Verdikt zum Lauf: Container des Schemas gegen FFD, L2 und, wo bekannt, das Optimum; bei nicht bewiesener gerundeter Instanz mit Hinweis."""
    b, f = a.schema.behaelter, len(a.ffd)
    ziel = f" Das Optimum ist **{a.opt}**." if a.opt is not None else f" Die Schranke L2 ist {a.l2}."
    kopf = f"Das Schema braucht **{b}** Container, FFD {f}."
    if not a.schema.gross:
        return "info", f"Alle Pakete sind kleiner als {C.EPS_TEXT[a.settings.eps_index]} mal der Kapazität: Das Schema ist hier nur First Fit der absteigend sortierten Pakete und braucht **{b}** Container, FFD {f}." + ziel
    hinweis = "" if a.schema.bewiesen else f" Die gerundete Instanz ist nach {a.schema.knoten} Knoten nicht bewiesen exakt gelöst."
    if b < f:
        return "success", kopf + " Das Schema ist hier besser als FFD." + ziel + hinweis
    if b == f:
        return "info", kopf + " Beide gleich viele." + ziel + hinweis
    return "warning", kopf + f" Das Schema braucht hier {b - f} mehr als FFD: Die Rundung kostet." + ziel + hinweis


def verdict_aufwand(a: Analysis) -> tuple[str, str]:
    """Verdikt zum Aufwand: große Pakete, Gruppen, gerundete Größen, Muster und Knoten dieses Laufs, dazu die Gruppenzahl der Rechnung für dasselbe eps."""
    s = a.schema
    if not s.gross:
        return "info", "Es gibt keine großen Pakete, also keine Gruppen und keine Muster."
    teil = (f"Von {a.inst.n} Paketen sind **{len(s.gross)}** groß (ab {C.EPS_TEXT[a.settings.eps_index]} mal der Kapazität); sie bilden {len(s.gruppen)} Gruppen zu je höchstens {s.k} und haben "
            f"**{len(s.verschieden)}** verschiedene gerundete Größen mit **{s.muster}** maximalen Mustern; die Tiefensuche brauchte {s.knoten} Knoten. "
            f"Die Rechnung der Demo verlangt für eps = {C.EPS_TEXT[a.settings.eps_index]} aufgerundet 1 / eps² = **{a.theorie_h}** Gruppen; hier sind es {a.h}.")
    if a.h >= len(s.gross):
        return "info", teil + " Mit so vielen Gruppen ist jedes große Paket eine eigene (k = 1): Es wird nicht gerundet, das Schema löst die großen Pakete exakt."
    return "info", teil


def verdict_grenze(a: Analysis) -> tuple[str, str]:
    """Verdikt zur oberen Grenze: das Ergebnis liegt darunter (bei bewiesen gelöster gerundeter Instanz immer); die Grenze selbst ist nie besser als FFD plus k."""
    b = a.schema.behaelter
    teil = f"Obere Grenze dieser Instanz: max(FFD + k, aufgerundet(Volumen / ((1 − eps) Kapazität)) + 1) = max({len(a.ffd)} + {a.schema.k}, …) = **{a.grenze}**; das Schema braucht {b}."
    if not a.schema.bewiesen:
        return "info", teil + " Die gerundete Instanz ist nicht bewiesen exakt gelöst, die Grenze gilt dann nicht."
    return ("success" if b <= a.grenze else "warning"), teil + (" Die Grenze hält." if b <= a.grenze else " Die Grenze ist verletzt (das darf nicht vorkommen).")


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def messzelle(verteilung: int, n_index: int, instanzen=None) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen, damit der Vergleich exakt ist) über INSTANZEN feste Instanzen (oder nur über die Nummern `instanzen`).

    referenz: Summen der Container von FFD und der Schranke L2. einstellung[i] zu C.EINSTELLUNGEN[i]: behaelter (Summe), besser, gleich, schlechter (Zahl der Instanzen gegenüber FFD), muster (Summe),
    knoten (Summe), knoten_max, unbewiesen (Zahl), gross (Summe der großen Pakete), k (Summe der Gruppengrößen), bewiesen (Zahl der bewiesen gelösten), grenze_ok (davon mit Ergebnis höchstens
    obere Grenze), luft (Summe von obere Grenze minus Ergebnis über die bewiesenen)."""
    out = {"referenz": {"ffd": 0, "l2": 0, "l1": 0}, "einstellung": [{"behaelter": 0, "besser": 0, "gleich": 0, "schlechter": 0, "muster": 0, "knoten": 0, "knoten_max": 0, "unbewiesen": 0,
                                                                          "gross": 0, "k": 0, "bewiesen": 0, "grenze_ok": 0, "luft": 0} for _ in C.EINSTELLUNGEN]}
    for j in (range(C.INSTANZEN) if instanzen is None else instanzen):
        inst = raster_instanz(verteilung, n_index, j)
        sizes = list(inst.sizes)
        f = len(A.ffd(sizes, inst.cap))
        out["referenz"]["ffd"] += f
        out["referenz"]["l2"] += A.l2(sizes, inst.cap)
        out["referenz"]["l1"] += A.l1(sizes, inst.cap)
        for i, (eps, h) in enumerate(C.EINSTELLUNGEN):
            sc = A.schema(sizes, inst.cap, eps, h, C.KNOTEN_RASTER)
            assert A.container_pruefen(sizes, [list(b) for b in sc.bins], inst.cap)
            o = out["einstellung"][i]
            b = sc.behaelter
            o["behaelter"] += b
            o["besser"] += b < f
            o["gleich"] += b == f
            o["schlechter"] += b > f
            o["muster"] += sc.muster
            o["knoten"] += sc.knoten
            o["knoten_max"] = max(o["knoten_max"], sc.knoten)
            o["unbewiesen"] += not sc.bewiesen
            o["gross"] += len(sc.gross)
            o["k"] += sc.k
            if sc.bewiesen:
                g = grenze(sum(sizes), inst.cap, eps, f, sc.k)
                o["bewiesen"] += 1
                o["grenze_ok"] += b <= g
                o["luft"] += g - b
    return out


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Zählungen einer Zelle aus den vorberechneten Summen."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    k = daten["instanzen"]
    ref = z["referenz"]
    zeilen = []
    for (eps, h), o in zip(C.EINSTELLUNGEN, z["einstellung"]):
        zeilen.append({"eps": eps, "h": h, "behaelter": o["behaelter"] / k, "ueber_l2": (o["behaelter"] - ref["l2"]) / k, "besser": o["besser"], "gleich": o["gleich"], "schlechter": o["schlechter"],
                       "muster": o["muster"] / k, "knoten": o["knoten"] / k, "knoten_max": o["knoten_max"], "unbewiesen": o["unbewiesen"], "gross": o["gross"] / k, "k": o["k"] / k,
                       "bewiesen": o["bewiesen"], "grenze_ok": o["grenze_ok"], "luft": o["luft"] / o["bewiesen"] if o["bewiesen"] else None})
    return {"verteilung": verteilung, "name": C.VERTEILUNG_LANG[verteilung], "n": C.MESS_N[n_index], "instanzen": k, "ffd": ref["ffd"] / k, "l2": ref["l2"] / k, "ffd_ueber_l2": (ref["ffd"] - ref["l2"]) / k,
            "einstellungen": zeilen}


def verdict_messung(z: dict) -> tuple[str, str]:
    """Experiment 1: in wie vielen der Einstellungen ist das Schema im Mittel besser als FFD (auf zwei Stellen gerundet), und wie viele Instanzen hat das beste Schema gegen FFD gewonnen? FFD gegen L2 als Maßstab."""
    f = round(z["ffd_ueber_l2"], 2)
    zeilen = z["einstellungen"]
    besser = [e for e in zeilen if round(e["ueber_l2"], 2) < f]
    bester = min(zeilen, key=lambda e: (round(e["ueber_l2"], 2), -e["h"], e["eps"]))
    teil = (f"Für {z['name']} mit n = {z['n']} liegt FFD im Mittel {f:.2f} Container über L2 ({z['instanzen']} Instanzen); die neun Einstellungen des Schemas liegen zwischen "
            f"{min(round(e['ueber_l2'], 2) for e in zeilen):.2f} und {max(round(e['ueber_l2'], 2) for e in zeilen):.2f}. Das beste Schema (eps {eps_text(bester['eps'])}, {bester['h']} Gruppen) gewinnt gegen FFD in "
            f"{bester['besser']}, verliert in {bester['schlechter']} Instanzen.")
    if besser:
        return "success", teil + f" In {len(besser)} von {len(zeilen)} Einstellungen ist das Schema im Mittel besser als FFD."
    return "warning", teil + " In keiner Einstellung ist das Schema im Mittel besser als FFD."


def verdict_aufwand_raster(z: dict) -> tuple[str, str]:
    """Experiment 2: Muster und Knoten der gerundeten Instanz in der Zelle: wie stark wachsen sie von der kleinsten zur größten Gruppenzahl bei eps = 0,2 (5 / 10 / 25 Gruppen)?"""
    e = [x for x in z["einstellungen"] if x["eps"] == 0.2]
    teil = (f"Für {z['name']} mit n = {z['n']} wachsen bei eps = 0,2 die Muster der gerundeten Instanz mit {e[0]['h']} / {e[1]['h']} / {e[2]['h']} Gruppen im Mittel von {e[0]['muster']:.0f} über "
            f"{e[1]['muster']:.0f} auf {e[2]['muster']:.0f}, die Knoten der Tiefensuche von {e[0]['knoten']:.0f} über {e[1]['knoten']:.0f} auf {e[2]['knoten']:.0f}.")
    unb = sum(x["unbewiesen"] for x in z["einstellungen"])
    return ("warning" if unb else "info"), teil + (f" In {unb} der {len(z['einstellungen']) * z['instanzen']} Läufe war die gerundete Instanz nach {C.KNOTEN_RASTER} Knoten nicht bewiesen gelöst." if unb else "")


def verdict_theorie(zeilen: list) -> tuple[str, str]:
    """Experiment 3: ab welchem eps zählt die Rechnung der Demo mehr als eine Million Muster (und mehr als 10^12)?"""
    millionen = next((z for z in zeilen if z["muster"] > 10 ** 6), None)
    billionen = next((z for z in zeilen if z["muster"] > 10 ** 12), None)
    teil = (f"Mit aufgerundet 1 / eps² Gruppen hat die gerundete Instanz bei eps = {eps_text(zeilen[0]['eps'])} {zeilen[0]['muster']} Muster und bei eps = {eps_text(zeilen[-1]['eps'])} "
            f"{zeilen[-1]['muster']:.2e} (Stellen: {len(str(zeilen[-1]['muster']))}).")
    if millionen and billionen:
        return "warning", teil + f" Über eine Million Muster gibt es ab eps = {eps_text(millionen['eps'])}, über 10^12 ab eps = {eps_text(billionen['eps'])}: Das Schema ist nur für große eps berechenbar."
    return "info", teil
