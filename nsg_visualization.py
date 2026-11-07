"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import nsg_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.3), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def eps_h_text(eps, h) -> str:
    return "{} / {}".format("{:g}".format(eps).replace(".", ","), h)


def gruppen_farbe(g: int) -> str:
    return C.GRUPPEN_FARBEN[g % len(C.GRUPPEN_FARBEN)]


def build_runden(sizes, cap, schema, eps):
    """Alle Pakete absteigend sortiert als Balken: große Pakete in der Farbe ihrer Gruppe, kleine in Braun. Die schwarze Stufenlinie ist die gerundete Größe jeder Gruppe (das größte Paket der Gruppe),
    die rote gestrichelte Linie die Schwelle eps mal Kapazität. Der Abstand zwischen Balken und Stufe ist das, was die Rundung kostet."""
    ordnung = list(schema.gross) + list(schema.klein)
    gruppe_von = {i: g for g, grp in enumerate(schema.gruppen) for i in grp}
    farben = [gruppen_farbe(gruppe_von[i]) if i in gruppe_von else C.COLOR_KLEIN for i in ordnung]
    x = list(range(1, len(ordnung) + 1))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=[sizes[i] for i in ordnung], marker_color=farben, showlegend=False,
                         hovertext=[f"Paket {i + 1}: {sizes[i]}" + (f", Gruppe {gruppe_von[i] + 1}" if i in gruppe_von else ", klein") for i in ordnung], hoverinfo="text"))
    stufe_x, stufe_y = [], []
    pos = 0
    for grp, klasse in zip(schema.gruppen, schema.klassen):
        stufe_x += [pos + 0.5, pos + len(grp) + 0.5]
        stufe_y += [klasse, klasse]
        pos += len(grp)
    if stufe_x:
        fig.add_trace(go.Scatter(x=stufe_x, y=stufe_y, mode="lines", line=dict(color="black", width=2), showlegend=False, hovertemplate="gerundet auf %{y}<extra></extra>"))
    fig.add_hline(y=eps * cap, line=dict(color=C.COLOR_LINE, width=1.5, dash="dash"), annotation_text="Schwelle eps · Kapazität", annotation_position="top right")
    fig.update_xaxes(title_text="Pakete, absteigend sortiert")
    fig.update_yaxes(title_text=f"Größe (Kapazität {cap})", range=[0, cap * 1.05])
    return _base(fig, 320)


def build_container(sizes, bins, cap, schema=None, titel_praefix="C"):
    """Ein Balken je Container, darin die Pakete als gestapelte Segmente (große in der Farbe ihrer Gruppe, wenn `schema` gegeben ist, kleine braun, sonst alle grau), oben der freie Platz in Grau."""
    gruppe_von = {}
    kleine = set()
    if schema is not None:
        gruppe_von = {i: g for g, grp in enumerate(schema.gruppen) for i in grp}
        kleine = set(schema.klein)
    labels = [f"{titel_praefix}{b + 1}" for b in range(len(bins))]
    schichten = max((len(b) for b in bins), default=0)
    fig = go.Figure()
    for k in range(schichten):
        paket = [b[k] if k < len(b) else None for b in bins]
        farben = []
        for p in paket:
            if p is None:
                farben.append("rgba(0,0,0,0)")
            elif p in gruppe_von:
                farben.append(gruppen_farbe(gruppe_von[p]))
            elif p in kleine:
                farben.append(C.COLOR_KLEIN)
            else:
                farben.append(C.COLOR_FFD)
        fig.add_trace(go.Bar(x=labels, y=[sizes[p] if p is not None else 0 for p in paket], text=[str(sizes[p]) if p is not None else "" for p in paket], textposition="inside", insidetextanchor="middle",
                             marker=dict(color=farben, line=dict(color="white", width=1.5)), showlegend=False, hovertemplate="%{x}: Paket %{text}<extra></extra>"))
    frei = [cap - sum(sizes[i] for i in b) for b in bins]
    fig.add_trace(go.Bar(x=labels, y=frei, text=[f"frei {f}" if f > 0 else "" for f in frei], textposition="inside", insidetextanchor="middle", marker=dict(color=C.COLOR_FREE), showlegend=False,
                         hovertemplate="%{x}: %{y} frei<extra></extra>"))
    fig.add_hline(y=cap, line=dict(color=C.COLOR_LINE, width=2, dash="dash"))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text=f"Füllung (Kapazität {cap})", range=[0, cap * 1.05])
    return _base(fig)


def build_vergleich(werte):
    """Balken mit den Containerzahlen: `werte` = Liste (Name, Zahl, Farbe)."""
    fig = go.Figure(go.Bar(x=[n for n, _, _ in werte], y=[z for _, z, _ in werte], marker_color=[f for _, _, f in werte], text=[str(z) for _, z, _ in werte], textposition="outside",
                           hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.update_yaxes(title_text="Container", rangemode="tozero")
    return _base(fig, 260)


def build_messung(zeilen, titel):
    """Balken je Einstellung (eps und Gruppenzahl): mittlere Container über L2; die graue Linie ist FFD."""
    namen = [eps_h_text(z["eps"], z["h"]) for z in zeilen["einstellungen"]]
    fig = go.Figure(go.Bar(x=namen, y=[z["ueber_l2"] for z in zeilen["einstellungen"]], marker_color=C.SCHEMA_FARBEN[0], hovertemplate="eps / Gruppen %{x}: %{y:.2f}<extra></extra>"))
    fig.add_hline(y=zeilen["ffd_ueber_l2"], line=dict(color="gray", width=2, dash="dash"), annotation_text="FFD", annotation_position="top left")
    fig.update_xaxes(title_text="eps / Zahl der Gruppen")
    fig.update_yaxes(title_text=titel, rangemode="tozero")
    return _base(fig, 320)
