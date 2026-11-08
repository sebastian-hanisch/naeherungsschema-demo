"""Packen: Runden und Gruppieren, ein Näherungsschema - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Gelbes Stück 6 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Ein Näherungsschema in der Art von Fernandez de la Vega und Lueker: kleine Pakete beiseite, große Pakete in Gruppen auf die größte Größe
der Gruppe aufrunden, die wenigen gerundeten Größen exakt lösen, zurückübertragen, die kleinen Pakete auffüllen. Was liefert das, und wie groß werden die Zahlen? Das Messraster (vorberechnet in
nsg_precomputed.json) zeigt es an Zufallsinstanzen.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import nsg_constants as C
from nsg_evaluation import (
    Settings,
    analyse,
    eps_text,
    theorie_zeilen,
    verdict_aktuell,
    verdict_aufwand,
    verdict_aufwand_raster,
    verdict_grenze,
    verdict_messung,
    verdict_theorie,
    zeile,
)
from nsg_layout import dunkles_design, kopf_css
from nsg_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from nsg_visualization import build_container, build_messung, build_runden, build_vergleich

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in nsg_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧮 Runden und Gruppieren: ein Näherungsschema")
st.markdown(
    """
Wie weit kommt man mit einem **Näherungsschema** für das Packen von Paketen in Container? Die Idee: Die vielen verschiedenen Größen werden zu **wenigen** zusammengefasst (Runden und Gruppieren), die wenigen löst man **exakt**, den Rest füllt man auf. Zwei Fragen: **Was liefert das Schema gegen FFD**, und **wie groß werden die Zahlen**, wenn man es so genau macht, wie die Rechnung es verlangt? Die Antwort steht in den Messungen unten; sie fällt für das Schema nicht schmeichelhaft aus.

Weiter unten: der Abschnitt **🔬 Experimente**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert das Schema", expanded=True):
    st.markdown(
        """
1. **Klein beiseite:** Pakete unter **eps** mal Kapazität sind klein und warten bis zum Schluss.
2. **Gruppieren und runden:** Die großen Pakete werden absteigend sortiert und in **h Gruppen** zu je k aufeinanderfolgenden Paketen zerlegt. Jedes Paket wird auf das **größte Paket seiner Gruppe aufgerundet**. Übrig bleiben höchstens h verschiedene Größen (die schwarze Stufenlinie im ersten Bild).
3. **Exakt lösen:** Für die gerundeten Größen wird die kleinste Containerzahl gesucht, über alle **Muster** (so kann ein Container gefüllt sein). Das macht eine Tiefensuche; ihr Aufwand wird in **Knoten** gezählt, nicht in Sekunden.
4. **Zurück:** Jedes echte Paket nimmt einen Platz seiner Gruppe ein; es ist höchstens so groß wie der Platz.
5. **Auffüllen:** Die kleinen Pakete kommen mit First Fit in die Lücken, sonst in neue Container.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Pakete**")
    quelle = st.selectbox("Instanz", list(C.QUELLEN), format_func=C.QUELLEN.get, key="quelle_select", help="Die drei Beispiele haben je zwölf feste Pakete (Kapazität 100). Die Zufallsinstanz folgt den Reglern darunter.")
    verteilung = st.selectbox("Größen der Zufallsinstanz", list(range(len(C.VERTEILUNGEN))), format_func=lambda i: C.VERTEILUNGEN[i][1], key="verteilung_select", help="Gilt nur für die Zufallsinstanz.")
    n = st.number_input("Zahl der Pakete (Zufallsinstanz)", *bounds("n_input"), key="n_input", step=1, help="Gilt nur für die Zufallsinstanz. Live wird bis 60 Pakete gerechnet.")
    seed = st.number_input("Startzahl der Zufallsinstanz", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt nur bei der Zufallsinstanz.")
    st.button("🎲 Neue Zufallsinstanz würfeln", width="stretch", on_click=randomize_seed)
    st.markdown("**Schema**")
    eps_index = st.selectbox("Schwelle eps (klein unter eps mal Kapazität)", list(range(len(C.EPS_WERTE))), format_func=lambda i: C.EPS_TEXT[i], key="eps_select",
                             help="Pakete unter eps mal Kapazität sind klein und werden zuletzt aufgefüllt; je kleiner eps, desto mehr Pakete sind groß.")
    h = st.number_input("Zahl der Gruppen h", *bounds("h_input"), key="h_input", step=1,
                        help="In so viele Gruppen werden die großen Pakete geteilt. Ab so vielen Gruppen, wie es große Pakete gibt, ist jedes Paket eine eigene Gruppe und es wird nicht gerundet.")

sync_query_params({"quelle_select": int(quelle), "verteilung_select": int(verteilung), "n_input": int(n), "seed_input": int(seed), "eps_select": int(eps_index), "h_input": int(h)})

settings = Settings(int(quelle), int(verteilung), int(n), int(seed), int(eps_index), int(h))
a = _analysis(settings)
s = a.schema

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
m1.metric("Container (Schema)", s.behaelter, delta=s.behaelter - len(a.ffd), delta_color="inverse", help="Delta: Container des Schemas minus Container von FFD.")
m2.metric("Container (FFD)", len(a.ffd), delta="Vergleich", delta_color="off")
m3.metric("Untere Schranke L2", a.l2, delta="Volumen: " + str(a.l1), delta_color="off")
if a.opt is not None:
    m4.metric("Optimum (exakt)", a.opt, delta="Referenz", delta_color="off")
elif a.lp is not None:
    m4.metric("LP-Schranke", f"{a.lp:.2f}", delta="aufgerundet " + str(-(-int(a.lp * 1000 - 1e-6) // 1000)), delta_color="off")
else:
    m4.metric("Optimum / LP", "nicht berechnet", delta="live nur bis 12 / 30 Pakete", delta_color="off")
st.caption(f"{a.inst.n} Pakete, Kapazität {a.inst.cap}, Gesamtgröße {sum(a.inst.sizes)}. Schema mit eps = {eps_text(a.eps)} und {a.h} Gruppen.")

st.markdown("**Runden:** Die Balken sind die Pakete, absteigend sortiert; die Farbe ist die Gruppe (braun: klein). Die schwarze Stufe ist die Größe, auf die jede Gruppe aufgerundet wird.")
st.plotly_chart(build_runden(list(a.inst.sizes), a.inst.cap, s, a.eps), width="stretch", key="runden_chart")
st.markdown("**Packung des Schemas** (Farbe = Gruppe, braun = klein aufgefüllt):")
st.plotly_chart(build_container(list(a.inst.sizes), [list(b) for b in s.bins], a.inst.cap, s), width="stretch", key="schema_chart")
vergleich = [("Schema", s.behaelter, C.SCHEMA_FARBEN[0]), ("FFD", len(a.ffd), C.COLOR_FFD), ("L2", a.l2, "#4c78a8")]
if a.opt is not None:
    vergleich.append(("Optimum", a.opt, "#7b5ea7"))
st.plotly_chart(build_vergleich(vergleich), width="stretch", key="vergleich_chart")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was liefert das Schema, und was kostet es?")
kind, text = verdict_aktuell(a)
getattr(st, kind)(text)
kind, text = verdict_aufwand(a)
getattr(st, kind)(text)
kind, text = verdict_grenze(a)
getattr(st, kind)(text)
st.caption("Die obere Grenze gilt nur, wenn die gerundete Instanz bewiesen exakt gelöst ist; sie ist nie besser als FFD plus k, also kein Vorteil gegenüber FFD (siehe 📐).")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experimente: Gilt das für viele Instanzen?")
st.caption(f"Gemessen an je {C.INSTANZEN} festen Zufallsinstanzen pro Zelle, Kapazität {C.MESS_CAP}, neun Einstellungen des Schemas (eps / Zahl der Gruppen). Die Zahlen sind vorberechnet (`generate_precomputed.py`); der Maßstab ist die Schranke L2.")
e1, e2 = st.columns(2)
ver = e1.selectbox("Größen der Pakete", list(range(len(C.VERTEILUNGEN))), index=0, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
ni = e2.selectbox("Zahl der Pakete n", list(range(len(C.MESS_N))), index=1, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
z = zeile(int(ver), int(ni))

st.markdown("### Experiment 1: Was liefert das Schema gegen FFD?")
st.plotly_chart(build_messung(z, "Container über L2 (Mittel)"), width="stretch", key="exp_chart")
tab = ["| eps / Gruppen | Container über L2 | besser als FFD | gleich | schlechter |", "|---|---|---|---|---|"]
for r in z["einstellungen"]:
    tab.append(f"| {eps_text(r['eps'])} / {r['h']} | {r['ueber_l2']:.2f} | {r['besser']} | {r['gleich']} | {r['schlechter']} |")
tab.append(f"| FFD | {z['ffd_ueber_l2']:.2f} | - | - | - |")
st.markdown("\n".join(tab))
st.caption(f"Mittlere Container über L2 und Zahl der Instanzen (von {z['instanzen']}), in denen das Schema weniger, gleich viele oder mehr Container braucht als FFD.")
kind, text = verdict_messung(z)
getattr(st, kind)(text)

st.markdown("### Experiment 2: Wie groß wird der Aufwand? (gemessen)")
tab2 = ["| eps / Gruppen | große Pakete | Gruppengröße k | Muster | Knoten (Mittel) | Knoten (größter Lauf) | nicht bewiesen |", "|---|---|---|---|---|---|---|"]
for r in z["einstellungen"]:
    tab2.append(f"| {eps_text(r['eps'])} / {r['h']} | {r['gross']:.0f} | {r['k']:.1f} | {r['muster']:.0f} | {r['knoten']:.0f} | {r['knoten_max']} | {r['unbewiesen']} |")
st.markdown("\n".join(tab2))
st.caption(f"Mittel über die Instanzen der Zelle. Muster: maximale Muster der gerundeten Größen; Knoten: Knoten der Tiefensuche (Grenze {C.KNOTEN_RASTER}); „nicht bewiesen“: Läufe, in denen die Grenze erreicht wurde.")
kind, text = verdict_aufwand_raster(z)
getattr(st, kind)(text)

st.markdown("### Experiment 3: Wie groß werden die Zahlen, wenn man es so genau macht, wie die Rechnung verlangt? (Rechnung)")
tz = theorie_zeilen()
tab3 = ["| eps | Gruppen 1 / eps² | Pakete je Container | Zahl der Muster |", "|---|---|---|---|"]
for r in tz:
    muster = f"{r['muster']:,}".replace(",", ".") if r["muster"] < 10 ** 12 else f"{r['muster']:.2e} ({len(str(r['muster']))} Stellen)"
    tab3.append(f"| {eps_text(r['eps'])} | {r['h']} | {r['je_container']} | {muster} |")
st.markdown("\n".join(tab3))
st.caption(f"Die Rechnung der Demo: Mit aufgerundet 1 / eps² Gruppen hat die gerundete Instanz so viele Größen; die Muster sind alle Möglichkeiten, einen Container mit solchen Größen zu füllen (Kapazität {C.THEORIE_CAP}, die Größen gleichmäßig zwischen eps mal Kapazität und Kapazität, per Zählen, nicht per Aufzählen).")
kind, text = verdict_theorie(tz)
getattr(st, kind)(text)

st.markdown("### Experiment 4: Was sagt die obere Grenze?")
tab4 = ["| eps / Gruppen | k (Mittel) | bewiesen gelöst | Grenze gehalten | Luft (Grenze minus Ergebnis) |", "|---|---|---|---|---|"]
for r in z["einstellungen"]:
    luft = "-" if r["luft"] is None else f"{r['luft']:.2f}"
    tab4.append(f"| {eps_text(r['eps'])} / {r['h']} | {r['k']:.1f} | {r['bewiesen']} von {z['instanzen']} | {r['grenze_ok']} von {r['bewiesen']} | {luft} |")
st.markdown("\n".join(tab4))
st.caption("Die obere Grenze max(FFD + k, aufgerundet(Volumen / ((1 − eps) Kapazität)) + 1) gilt, wenn die gerundete Instanz bewiesen exakt gelöst ist. Sie ist nie besser als FFD plus k: Das Schema hat gegenüber FFD keine bessere Zusage, nur den Zusatz k.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Eine eigene Fassung des Schemas** | Die Literatur kennt feinere Schemata (und andere Gruppierungen); die Demo misst nur diese eine Fassung und gibt keine Güte der Literatur wieder. |
| **Die gerundete Instanz wird durch eine Tiefensuche gelöst** | Mit vielen Gruppen und großen Instanzen erreicht die Suche die Knotengrenze: Dann ist die gerundete Instanz nicht bewiesen exakt gelöst, und die obere Grenze gilt nicht. |
| **Die Größen sind zufällig verteilt** | Nur drei Verteilungen sind gemessen. Instanzen mit wenigen verschiedenen Größen (Triplets, Johnson-Instanz) kann das Schema mit wenigen Gruppen ohne Rundungsverlust lösen, wenn die Gruppen die gleichen Größen zusammenfassen; sonst verliert es auch dort. Das misst die Demo nicht. |
| **Kein Optimum im Raster** | Der Maßstab ist die Schranke L2, nicht das Optimum; ein Teil des Abstands ist Schranke. Live gibt es das Optimum bis 12 Pakete. |
| **Aufwand in Mustern und Knoten** | Zeiten hängen an der Umsetzung (Python); die Demo macht keine Laufzeitaussage. |
| **Alle Pakete sind vor dem Packen bekannt** | Wer jedes Paket sofort einsortieren muss, kann nicht gruppieren. Das ist Online-Packen. Mehr dazu: [Online](https://sebastianhanisch.net/konzepte-online-algorithmen.html). |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Pakete mit ganzzahligen Größen $s_i \in \{1, \dots, C\}$ und Container der Kapazität $C$. *Gesucht:* eine Packung in möglichst wenige Container.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Pakete |
| $s_i$ | Größe von Paket $i$ |
| $C$ | Kapazität eines Containers |
| $\varepsilon$ | Schwelle: Pakete mit $s_i < \varepsilon C$ sind klein |
| $h$ | Zahl der Gruppen der großen Pakete, $k = \lceil n_{\mathrm{gr}} / h \rceil$ die Gruppengröße |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Containern |

**Gruppieren und runden.** Die großen Pakete $L$ ($s_i \ge \varepsilon C$, $n_{\mathrm{gr}} = |L|$) werden absteigend sortiert und in Gruppen $G_1, \dots, G_h$ zu je $k$ aufeinanderfolgenden Paketen geteilt (die letzte kleiner). Jedes Paket aus $G_j$ wird auf $u_j = \max_{i \in G_j} s_i$ aufgerundet. Die gerundete Instanz $R$ hat höchstens $h$ verschiedene Größen; jede Packung von $R$ ist auch eine Packung von $L$ (die echten Pakete sind kleiner).

**Muster.** Ein Muster ist ein Vektor $p \in \mathbb{N}^m$ mit $\sum_j p_j u_j \le C$ ($m \le h$ verschiedene Größen), maximal, wenn kein weiteres Paket passt. Die gerundete Instanz ist exakt gelöst, wenn die kleinste Zahl von Mustern $\sum_t p^{(t)} \ge b$ gefunden ist ($b_j$ Zahl der Pakete der Größe $u_j$).

**Obere Grenze.** (1) Löscht man die erste Gruppe $G_1$ aus $R$, passt jede Größe $u_j$ ($j \ge 2$) in ein Paket der Gruppe $G_{j-1}$ von $L$ ($u_j \le \min G_{j-1}$, $|G_{j-1}| = k \ge |G_j|$); also braucht $R \setminus G_1$ höchstens $\mathrm{OPT}$ Container, und die $k$ Pakete von $G_1$ je einen eigenen: $\mathrm{OPT}(R) \le \mathrm{OPT} + k$. (2) Öffnen die kleinen Pakete (alle $< \varepsilon C$) mit First Fit einen neuen Container, sind alle früheren Container über $(1 - \varepsilon) C$ gefüllt: Die Zahl ist höchstens $\lceil \sum_i s_i / ((1 - \varepsilon) C) \rceil + 1$. Mit $\mathrm{OPT} \le \mathrm{FFD}$ folgt: Container des Schemas $\le \max(\mathrm{FFD} + k,\ \lceil \sum_i s_i / ((1 - \varepsilon) C) \rceil + 1)$, wenn $R$ exakt gelöst ist. Diese Grenze ist nie besser als $\mathrm{FFD} + k$.

**Gruppenzahl der Rechnung.** Mit $h = \lceil 1 / \varepsilon^2 \rceil$ Gruppen und $\mathrm{OPT} \ge \varepsilon\, n_{\mathrm{gr}}$ (jedes große Paket ist mindestens $\varepsilon C$) ist $k \le \varepsilon\, \mathrm{OPT} + 1$: der Zusatz $k$ ist höchstens ein Anteil $\varepsilon$ des Optimums plus 1. Dafür gibt es $h$ gerundete Größen und bis zu $\lfloor 1/\varepsilon \rfloor$ Pakete je Container; die Zahl der Muster wächst mit $\binom{h + \lfloor 1/\varepsilon \rfloor}{\lfloor 1/\varepsilon \rfloor}$ (nach oben beschränkt, hier gezählt, nicht aufgezählt).

**Schranken.** $L_1 = \lceil \sum_i s_i / C \rceil$; $L_2$ nach Martello und Toth (siehe Stück 2 dieser Reihe); der LP-Wert nach Gilmore und Gomory per Spaltenerzeugung (Stück 4), der aufgerundete LP-Wert ist eine Schranke, kein Optimum.

**Literatur** (nur Name und Gegenstand, aus dem Gedächtnis, Original nicht gelesen). Fernandez de la Vega und Lueker (1981) beschreiben ein asymptotisches Näherungsschema für das eindimensionale Packen durch Gruppieren und Runden. Die Demo übernimmt daraus keine Zahl, keine Konstante und keine Gütegarantie; alle Zahlen sind selbst gemessen oder gerechnet.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
