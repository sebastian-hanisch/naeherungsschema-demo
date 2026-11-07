"""Setzt die README zusammen: Tabellen und Text der Annahmen kommen aus denselben Funktionen wie in der App (nur zum Schreiben der README, nicht Teil der Laufzeit).

    python dev/readme_bauen.py [ANZAHL_TESTS]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import nsg_algorithm as A  # noqa: E402
import nsg_constants as C  # noqa: E402
import nsg_evaluation as ev  # noqa: E402
from nsg_scenario import beispiel  # noqa: E402

ZELLEN = [(v, ni) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def einst_kopf():
    return [f"{ev.eps_text(eps)} / {h}" for eps, h in C.EINSTELLUNGEN]


def tabelle_ueber_l2():
    """Tabelle A: Container über L2 (Mittel) je Zelle für FFD und die neun Einstellungen."""
    ta = ["| Verteilung | n | FFD | " + " | ".join(einst_kopf()) + " |", "|---|---|---|" + "---|" * len(C.EINSTELLUNGEN)]
    for v, ni in ZELLEN:
        z = ev.zeile(v, ni)
        ta.append(f"| {C.VERTEILUNG_KURZ[v]} | {z['n']} | {de(z['ffd_ueber_l2'])} | " + " | ".join(de(e["ueber_l2"]) for e in z["einstellungen"]) + " |")
    return "\n".join(ta)


def tabelle_besser():
    """Tabelle B: Instanzen, in denen das Schema weniger / gleich viele / mehr Container braucht als FFD."""
    tb = ["| Verteilung | n | " + " | ".join(einst_kopf()) + " |", "|---|---|" + "---|" * len(C.EINSTELLUNGEN)]
    for v, ni in ZELLEN:
        z = ev.zeile(v, ni)
        tb.append(f"| {C.VERTEILUNG_KURZ[v]} | {z['n']} | " + " | ".join(f"{e['besser']} / {e['gleich']} / {e['schlechter']}" for e in z["einstellungen"]) + " |")
    return "\n".join(tb)


def tabelle_aufwand():
    """Tabelle C: Muster und Knoten (Mittel) und nicht bewiesene Läufe der Zellen mit n = 50."""
    tc = ["| Verteilung | eps / Gruppen | große Pakete | k | Muster | Knoten (Mittel) | Knoten (größter Lauf) | nicht bewiesen |", "|---|---|---|---|---|---|---|---|"]
    ni = C.MESS_N.index(50)
    for v in range(len(C.VERTEILUNGEN)):
        z = ev.zeile(v, ni)
        for e in z["einstellungen"]:
            tc.append(f"| {C.VERTEILUNG_KURZ[v]} | {ev.eps_text(e['eps'])} / {e['h']} | {de(e['gross'], 0)} | {de(e['k'], 1)} | {de(e['muster'], 0)} | {de(e['knoten'], 0)} | {e['knoten_max']} | {e['unbewiesen']} |")
    return "\n".join(tc)


def tabelle_theorie():
    td = ["| eps | Gruppen 1 / eps² | Pakete je Container | Zahl der Muster |", "|---|---|---|---|"]
    for r in ev.theorie_zeilen():
        muster = f"{r['muster']:,}".replace(",", ".") if r["muster"] < 10 ** 12 else f"{r['muster']:.2e} ({len(str(r['muster']))} Stellen)".replace(".", ",")
        td.append(f"| {ev.eps_text(r['eps'])} | {r['h']} | {r['je_container']} | {muster} |")
    return "\n".join(td)


def tabelle_grenze():
    """Tabelle E: bewiesen gelöst, Grenze gehalten, Luft (Zellen mit n = 50)."""
    te = ["| Verteilung | eps / Gruppen | bewiesen gelöst | Grenze gehalten | Luft |", "|---|---|---|---|---|"]
    ni = C.MESS_N.index(50)
    for v in range(len(C.VERTEILUNGEN)):
        z = ev.zeile(v, ni)
        for e in z["einstellungen"]:
            te.append(f"| {C.VERTEILUNG_KURZ[v]} | {ev.eps_text(e['eps'])} / {e['h']} | {e['bewiesen']} von {z['instanzen']} | {e['grenze_ok']} von {e['bewiesen']} | {'-' if e['luft'] is None else de(e['luft'])} |")
    return "\n".join(te)


def tabelle_beispiele():
    """Behälterzahl des Schemas in den drei Handbeispielen für typische Einstellungen."""
    kopf = [(0.25, 3), (0.25, 4), (0.25, 6), (0.1, 12)]
    tx = ["| Beispiel | FFD | Optimum | " + " | ".join(f"eps {ev.eps_text(e)} / {h}" for e, h in kopf) + " |", "|---|---|---|" + "---|" * len(kopf)]
    for b in range(3):
        inst = beispiel(b)
        sizes = list(inst.sizes)
        zeile = [str(len(A.ffd(sizes, inst.cap))), str(A.optimum(sizes, inst.cap))] + [str(A.schema(sizes, inst.cap, e, h).behaelter) for e, h in kopf]
        tx.append(f"| {b + 1} | " + " | ".join(zeile) + " |")
    return "\n".join(tx)


if __name__ == "__main__":
    vorlage = (ROOT / "dev" / "readme_vorlage.md").read_text(encoding="utf-8")
    anzahl = sys.argv[1] if len(sys.argv) > 1 else "TESTZAHL"
    text = (vorlage.replace("{{TABELLE_A}}", tabelle_ueber_l2()).replace("{{TABELLE_B}}", tabelle_besser()).replace("{{TABELLE_C}}", tabelle_aufwand()).replace("{{TABELLE_D}}", tabelle_theorie())
            .replace("{{TABELLE_E}}", tabelle_grenze()).replace("{{BEISPIELE}}", tabelle_beispiele()).replace("{{ANNAHMEN}}", C.ASSUMPTIONS_MARKDOWN).replace("{{TESTS}}", anzahl))
    (ROOT / "README.md").write_text(text, encoding="utf-8")
    print("README.md geschrieben")
