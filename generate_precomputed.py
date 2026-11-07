"""Erzeugt nsg_precomputed.json: das Messraster (drei Verteilungen × Paketzahlen 20, 50, 100, 200 × 50 feste Instanzen × neun Einstellungen des Schemas), die Zählung der Muster in der Rechnung der Demo
(für eps von 0,5 bis 0,02) und die Stichprobe (die ersten Instanzen jeder Zelle einzeln, für die Tests).

    python generate_precomputed.py                         # rechnet alles neu (mehrere Prozesse)
    python generate_precomputed.py --nur-stichprobe        # ergänzt in der vorhandenen Datei nur die Stichprobe
    python generate_precomputed.py --check                 # rechnet das Raster (parallel) nach und vergleicht mit der Datei (die Zählung der Muster nicht)

Die Knotengrenze der Tiefensuche steht in nsg_constants.py (KNOTEN_RASTER); Ergebnisse hängen von ihr ab, nicht vom Rechner."""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import nsg_constants as C
import nsg_evaluation as ev


def _zelle(args):
    v, ni = args
    t = time.perf_counter()
    return v, ni, ev.messzelle(v, ni), time.perf_counter() - t


def _stichprobe_zelle(args):
    v, ni = args
    return ev.zelle_schluessel(v, ni), {str(j): ev.messzelle(v, ni, [j]) for j in C.STICHPROBE_J}


def _frisch(args):
    v, ni = args
    return ev.zelle_schluessel(v, ni), ev.messzelle(v, ni)


def _pool():
    return ProcessPoolExecutor(max(1, min(6, (os.cpu_count() or 2) // 2)))


def _zellen():
    return [(v, ni) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]


def theorie_zaehlen() -> dict:
    """Zahl der Muster je eps (als Zeichenkette, die Zahlen werden groß), gezählt mit ev.theorie_muster."""
    return {str(e): str(ev.theorie_muster(e)) for e in C.THEORIE_EPS}


def stichprobe_ergaenzen(daten: dict) -> None:
    with _pool() as pool:
        daten["stichprobe"] = dict(pool.map(_stichprobe_zelle, _zellen()))


def erzeugen() -> dict:
    daten = {"instanzen": C.INSTANZEN, "cap": C.MESS_CAP, "knoten_raster": C.KNOTEN_RASTER, "theorie": theorie_zaehlen(), "zellen": {}}
    with _pool() as pool:
        for v, ni, z, sekunden in pool.map(_zelle, _zellen()):
            daten["zellen"][ev.zelle_schluessel(v, ni)] = z
            print(f"{ev.zelle_schluessel(v, ni)}: {sekunden:.0f} s", flush=True)
    stichprobe_ergaenzen(daten)
    return daten


def schreiben(daten: dict) -> None:
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED.name)


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    schlecht = 0
    with _pool() as pool:
        for schl, frisch in pool.map(_frisch, _zellen()):
            if frisch != gespeichert["zellen"][schl]:
                schlecht += 1
                print("ABWEICHUNG", schl, flush=True)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(pruefen())
    if "--nur-stichprobe" in sys.argv:
        d = json.loads(ev.PRECOMPUTED.read_text(encoding="utf-8"))
        stichprobe_ergaenzen(d)
        schreiben(d)
        sys.exit(0)
    schreiben(erzeugen())
