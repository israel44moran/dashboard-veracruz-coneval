"""
Pobreza, Salud y Educacion en Veracruz
Dashboard interactivo sobre los 212 municipios del estado, con datos
abiertos reales de CONEVAL 2015.
Ejecutar: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import numpy as np
from datetime import datetime

# ============================================================
# CONFIGURACION
# ============================================================
st.set_page_config(
    page_title="Veracruz — Pobreza, Salud y Educacion",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# TOKENS DE DISENO
# ============================================================
INK         = "#0E1218"
SURFACE     = "#171C24"
SURFACE_2   = "#1F2530"
BORDER      = "#2A3140"
RULE        = "#3A4258"
CREAM       = "#F2EDE3"
COOL        = "#9AA3B5"
MUTED       = "#5A6478"

AMBER       = "#D4A574"
AMBER_HI    = "#E8C9A0"
AMBER_DIM   = "#8B6E47"
AMBER_FILL  = "rgba(212, 165, 116, 0.08)"

GREEN       = "#7A9B7E"
RED         = "#C26B5E"
BLUE        = "#7088A8"

# ============================================================
# CARGA DE DATOS
# ============================================================
@st.cache_data
def cargar():
    if not os.path.exists("veracruz_municipios.csv"):
        return None, None, None
    df = pd.read_csv("veracruz_municipios.csv", dtype={"cvegeo": str})
    with open("veracruz_geo.json", encoding="utf-8") as f:
        geo = json.load(f)
    with open("metadata.json", encoding="utf-8") as f:
        meta = json.load(f)
    return df, geo, meta


df, geo, meta = cargar()

if df is None:
    st.error(
        "Faltan los datos. Corre primero:\n\n"
        "    python descargar_datos.py\n"
        "    python preparar_datos.py"
    )
    st.stop()


# ============================================================
# ESTILOS (consistente con el resto del portafolio)
# ============================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,300..700,0..100&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'DM Sans', sans-serif;
        background-color: {INK};
        color: {CREAM};
    }}
    #MainMenu, footer {{visibility: hidden;}}
    .block-container {{
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1340px;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background-color: {SURFACE};
        padding-top: 2rem;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {{
        color: {CREAM};
    }}
    [data-testid="stSidebar"] label {{
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        color: {MUTED} !important;
    }}

    .hero-eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; color: {AMBER};
        letter-spacing: 2px; text-transform: uppercase;
        margin: 0 0 0.5rem 0;
    }}
    .hero-title {{
        font-family: 'Fraunces', serif;
        font-weight: 500; font-size: 2.4rem;
        line-height: 1.05; letter-spacing: -1px;
        color: {CREAM}; margin: 0 0 0.6rem 0;
    }}
    .hero-deck {{
        font-family: 'DM Sans', sans-serif;
        font-size: 0.95rem; color: {COOL};
        margin: 0; max-width: 720px; line-height: 1.5;
    }}

    .meta-bar {{
        display: flex; gap: 3rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; color: {MUTED};
        text-transform: uppercase; letter-spacing: 1.5px;
        padding: 1rem 0;
        border-top: 1px solid {BORDER};
        border-bottom: 1px solid {BORDER};
        margin: 2rem 0;
    }}
    .meta-bar strong {{ color: {CREAM}; font-weight: 500; }}

    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0;
        border-top: 1px solid {BORDER};
        border-bottom: 1px solid {BORDER};
        margin: 2rem 0;
    }}
    .kpi-cell {{
        padding: 1.75rem 1.5rem 1.75rem 0;
        border-right: 1px solid {BORDER};
    }}
    .kpi-cell:first-child {{ padding-left: 0; }}
    .kpi-cell:last-child  {{ border-right: none; padding-right: 0; }}
    .kpi-cell-padded {{ padding-left: 1.5rem; }}
    .kpi-label {{
        font-family: 'DM Sans', sans-serif;
        font-size: 0.65rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 2px;
        color: {MUTED}; margin: 0 0 0.75rem 0;
    }}
    .kpi-number {{
        font-family: 'Fraunces', serif;
        font-weight: 400; font-size: 2.4rem;
        line-height: 1; letter-spacing: -1.5px;
        color: {CREAM}; margin: 0;
        font-feature-settings: 'tnum';
    }}
    .kpi-unit {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; color: {MUTED};
        text-transform: uppercase; letter-spacing: 1.5px;
        margin: 0.75rem 0 0 0;
        display: flex; align-items: center; gap: 6px;
    }}
    .kpi-tick {{
        display: inline-block; width: 8px; height: 1px;
        background: {AMBER};
    }}
    .kpi-delta {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem; font-weight: 500;
        letter-spacing: 0.5px;
    }}
    .kpi-delta.bad  {{ color: {RED}; }}
    .kpi-delta.good {{ color: {GREEN}; }}

    .section-block {{
        margin: 3rem 0 1.5rem 0;
        padding-top: 2rem;
        border-top: 1px solid {BORDER};
    }}
    .section-meta {{
        display: flex; align-items: baseline; gap: 1rem;
        margin-bottom: 0.5rem;
    }}
    .section-id {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem; color: {AMBER};
        letter-spacing: 1.5px; text-transform: uppercase;
    }}
    .section-divider {{ flex: 1; height: 1px; background: {BORDER}; }}
    .section-headline {{
        font-family: 'Fraunces', serif;
        font-weight: 500; font-size: 1.75rem;
        line-height: 1.1; letter-spacing: -0.5px;
        color: {CREAM}; margin: 0.5rem 0 0 0;
    }}
    .section-deck {{
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem; color: {COOL};
        margin: 0.5rem 0 0 0;
    }}

    .insight-callout {{
        background: {SURFACE};
        border: 1px solid {AMBER_DIM};
        border-left: 3px solid {AMBER};
        border-radius: 6px;
        padding: 1rem 1.3rem;
        margin: 1.5rem 0;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.9rem;
        color: {CREAM};
        line-height: 1.5;
    }}
    .insight-callout strong {{ color: {AMBER}; font-weight: 600; }}

    .colophon {{
        margin-top: 4rem;
        padding-top: 1.5rem;
        border-top: 2px solid {RULE};
        display: flex; justify-content: space-between;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; color: {MUTED};
        text-transform: uppercase; letter-spacing: 1.5px;
    }}

    .stSelectbox > div > div, .stMultiSelect > div > div {{
        background-color: {INK} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 4px !important;
        color: {CREAM} !important;
        font-family: 'JetBrains Mono', monospace !important;
    }}
    span[data-baseweb="tag"] {{
        background-color: {AMBER_DIM} !important;
        color: {CREAM} !important;
        border-radius: 2px !important;
    }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HERO
# ============================================================
st.markdown(f"""
<p class="hero-eyebrow">— ANALISIS SOCIOECONOMICO MUNICIPAL · CONEVAL {meta.get('anio', 2020)}</p>
<h1 class="hero-title">Pobreza, Salud y Educacion en Veracruz</h1>
<p class="hero-deck">
    Estudio sobre los <strong>{meta['n_municipios']} municipios</strong> de Veracruz, basado en la
    medicion mas reciente de pobreza municipal de CONEVAL ({meta.get('anio', 2020)}). Cubre
    pobreza, rezago educativo, acceso a servicios de salud, seguridad social, vivienda y
    alimentacion para <strong>{meta['poblacion_total']:,} habitantes</strong>, con desglose por
    grupo demografico (sexo, ambito rural/urbano, edad, poblacion indigena) y comparativa contra
    el promedio nacional.
</p>
""", unsafe_allow_html=True)


# ============================================================
# PANEL LATERAL — Selector de indicador y filtros
# ============================================================
INDICADORES = meta["indicadores_metadata"]

with st.sidebar:
    st.markdown(f"""
    <div style="padding: 0 0 1rem 0; border-bottom: 1px solid {BORDER}; margin-bottom: 1rem;">
        <p style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: {AMBER}; letter-spacing: 2px; text-transform: uppercase; margin: 0;">— Controles</p>
        <p style="font-family: 'Fraunces'; font-style: italic; font-size: 1.2rem; color: {CREAM}; margin: 0.3rem 0 0 0;">Configuracion</p>
    </div>
    """, unsafe_allow_html=True)

    indicador_default = "pobreza"
    indicador_seleccionado = st.selectbox(
        "Indicador para mapa y rankings",
        options=list(INDICADORES.keys()),
        format_func=lambda k: f"{INDICADORES[k]['nombre']} ({INDICADORES[k]['categoria']})",
        index=list(INDICADORES.keys()).index(indicador_default),
    )

    st.markdown(
        f'<p style="font-family: \'DM Sans\'; font-size: 0.78rem; color: {COOL}; '
        f'margin: 0.3rem 0 1rem 0; line-height: 1.4;">'
        f"{INDICADORES[indicador_seleccionado]['descripcion']}</p>",
        unsafe_allow_html=True,
    )

    n_top = st.slider("Mostrar Top N municipios", 5, 30, 10)

    rango_poblacion = st.slider(
        "Filtrar por poblacion del municipio",
        min_value=0,
        max_value=int(df["poblacion"].max()),
        value=(0, int(df["poblacion"].max())),
        step=5000,
    )


# Aplicar filtros
df_f = df[(df["poblacion"] >= rango_poblacion[0]) &
          (df["poblacion"] <= rango_poblacion[1])].copy()


# ============================================================
# BARRA META
# ============================================================
ind_meta = INDICADORES[indicador_seleccionado]
prom_nac = meta["promedios_nacionales"].get(indicador_seleccionado, None)
prom_ver = round(
    (df_f[indicador_seleccionado] * df_f["poblacion"]).sum() / df_f["poblacion"].sum(),
    2
) if df_f["poblacion"].sum() > 0 else 0

st.markdown(f"""
<div class="meta-bar">
    <div>EMITIDO &nbsp;·&nbsp; <strong>{datetime.now().strftime("%d %b %Y").upper()}</strong></div>
    <div>FUENTE &nbsp;·&nbsp; <strong>CONEVAL 2015</strong></div>
    <div>MUNICIPIOS &nbsp;·&nbsp; <strong>{len(df_f)} de {len(df)}</strong></div>
    <div>INDICADOR ACTIVO &nbsp;·&nbsp; <strong>{ind_meta['nombre']}</strong></div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# KPIs — VERACRUZ VS NACIONAL
# ============================================================
def delta_label(val_ver, val_nac):
    if val_nac is None or val_ver is None:
        return ""
    delta = round(val_ver - val_nac, 1)
    sign = "+" if delta > 0 else ""
    cls = "bad" if delta > 0 else "good"
    arrow = "↑" if delta > 0 else "↓"
    return f'<span class="kpi-delta {cls}">{arrow} {sign}{delta} pp vs nacional</span>'


def prom_pond(col):
    """Promedio ponderado por poblacion."""
    if col not in df_f.columns or df_f["poblacion"].sum() == 0:
        return 0
    return round((df_f[col] * df_f["poblacion"]).sum() / df_f["poblacion"].sum(), 1)


pct_pobreza = prom_pond("pobreza")
pct_plp = prom_pond("plp")
personas_pobreza = int(round(pct_pobreza / 100 * df_f["poblacion"].sum()))

prom_indicador_ver = prom_pond(indicador_seleccionado)
prom_indicador_nac = meta["promedios_nacionales"].get(indicador_seleccionado)

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-cell">
        <p class="kpi-label">Poblacion analizada</p>
        <p class="kpi-number">{df_f['poblacion'].sum():,.0f}</p>
        <p class="kpi-unit"><span class="kpi-tick"></span> Habitantes en {len(df_f)} municipios</p>
    </div>
    <div class="kpi-cell kpi-cell-padded">
        <p class="kpi-label">% Pobreza multidimensional</p>
        <p class="kpi-number">{pct_pobreza}%</p>
        <p class="kpi-unit"><span class="kpi-tick"></span> {personas_pobreza:,} personas en pobreza</p>
        {delta_label(pct_pobreza, meta['promedios_nacionales'].get('pobreza'))}
    </div>
    <div class="kpi-cell kpi-cell-padded">
        <p class="kpi-label">Bajo linea de pobreza por ingreso</p>
        <p class="kpi-number">{pct_plp}%</p>
        <p class="kpi-unit"><span class="kpi-tick"></span> No alcanzan la canasta basica</p>
        {delta_label(pct_plp, meta['promedios_nacionales'].get('plp'))}
    </div>
    <div class="kpi-cell kpi-cell-padded">
        <p class="kpi-label">Indicador activo</p>
        <p class="kpi-number">{prom_indicador_ver:.1f}%</p>
        <p class="kpi-unit"><span class="kpi-tick"></span> {ind_meta['nombre']}</p>
        {delta_label(prom_indicador_ver, prom_indicador_nac) if prom_indicador_nac is not None else ''}
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# UTILIDADES DE GRAFICA
# ============================================================
def apply_chart_style(fig, height=380):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color=CREAM, size=12),
        height=height,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER,
                   tickfont=dict(color=COOL, size=10, family="JetBrains Mono, monospace"),
                   linecolor=BORDER, showgrid=False),
        yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER,
                   tickfont=dict(color=COOL, size=10, family="JetBrains Mono, monospace"),
                   linecolor=BORDER, showgrid=True, gridwidth=1),
        legend=dict(font=dict(color=CREAM, size=11), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=SURFACE_2, bordercolor=BORDER,
                        font=dict(color=CREAM, family="JetBrains Mono, monospace", size=11)),
    )
    return fig


def section_header(section_id, title, subtitle):
    st.markdown(f"""
    <div class="section-block">
        <div class="section-meta">
            <span class="section-id">— {section_id}</span>
            <div class="section-divider"></div>
        </div>
        <p class="section-headline">{title}</p>
        <p class="section-deck">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# MAPA 01 — CHOROPLETH MUNICIPAL
# ============================================================
section_header("MAPA 01 / GEOGRAFIA",
               f"Distribucion territorial — {ind_meta['nombre']}",
               f"Cada municipio de Veracruz coloreado segun el indicador seleccionado. "
               f"Pasa el cursor por encima para ver detalles. Cambia el indicador desde el panel lateral.")

fig_map = px.choropleth_mapbox(
    df_f,
    geojson=geo,
    locations="cvegeo",
    color=indicador_seleccionado,
    featureidkey="properties.CVEGEO",
    hover_name="municipio",
    hover_data={
        "cvegeo": False,
        indicador_seleccionado: ":.1f",
        "poblacion": ":,",
    },
    color_continuous_scale=[
        [0.0, "#1F2530"],
        [0.2, "#5A4030"],
        [0.5, AMBER_DIM],
        [0.8, AMBER],
        [1.0, AMBER_HI],
    ],
    range_color=(df[indicador_seleccionado].min(), df[indicador_seleccionado].max()),
    mapbox_style="carto-darkmatter",
    zoom=5.6,
    center={"lat": 19.3, "lon": -96.5},
    opacity=0.85,
    labels={indicador_seleccionado: ind_meta["nombre"] + " (%)"},
)
fig_map.update_layout(
    height=560,
    paper_bgcolor=INK,
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(
        title=dict(text=f"{ind_meta['nombre']}<br>(%)",
                   font=dict(color=COOL, size=10, family="JetBrains Mono, monospace")),
        tickfont=dict(color=COOL, size=10, family="JetBrains Mono, monospace"),
        thickness=14, len=0.7, x=1.02,
    ),
    hoverlabel=dict(bgcolor=SURFACE_2, bordercolor=BORDER,
                    font=dict(color=CREAM, family="JetBrains Mono, monospace", size=11)),
)
st.plotly_chart(fig_map, use_container_width=True)


# ============================================================
# GRAFICA 02 — COMPARATIVA VERACRUZ vs NACIONAL POR INDICADOR
# ============================================================
section_header("GRAFICA 02 / BENCHMARK",
               "Veracruz vs promedio nacional",
               "Diferencia en puntos porcentuales por cada indicador. "
               "Barras arriba del cero = Veracruz esta peor que el promedio del pais.")

benchmark = []
for codigo, info in INDICADORES.items():
    if codigo in df_f.columns:
        ver_val = (df_f[codigo] * df_f["poblacion"]).sum() / df_f["poblacion"].sum()
        nac_val = meta["promedios_nacionales"].get(codigo)
        if nac_val is None:
            continue
        benchmark.append({
            "indicador": info["nombre"],
            "categoria": info["categoria"],
            "veracruz": round(ver_val, 1),
            "nacional": round(nac_val, 1),
            "diff_pp": round(ver_val - nac_val, 1),
        })
bm_df = pd.DataFrame(benchmark).sort_values("diff_pp", ascending=True)

colors_bm = [RED if d > 0 else GREEN for d in bm_df["diff_pp"]]

fig_bm = go.Figure()
fig_bm.add_trace(go.Bar(
    x=bm_df["diff_pp"], y=bm_df["indicador"],
    orientation="h",
    marker=dict(color=colors_bm, line=dict(width=0)),
    text=[f"{'+' if v > 0 else ''}{v} pp" for v in bm_df["diff_pp"]],
    textposition="outside",
    textfont=dict(color=CREAM, family="JetBrains Mono, monospace", size=10),
    hovertemplate="<b>%{y}</b><br>Veracruz: %{customdata[0]}%<br>Nacional: %{customdata[1]}%<extra></extra>",
    customdata=np.column_stack([bm_df["veracruz"], bm_df["nacional"]]),
))
fig_bm.add_vline(x=0, line=dict(color=BORDER, width=1.5))
fig_bm = apply_chart_style(fig_bm, height=460)
fig_bm.update_layout(
    yaxis=dict(showgrid=False, tickfont=dict(color=CREAM, size=11, family="DM Sans, sans-serif")),
    xaxis=dict(title="Diferencia (pp) — Veracruz menos Nacional",
               title_font=dict(size=10, color=MUTED),
               showgrid=True, gridcolor=BORDER),
)
st.plotly_chart(fig_bm, use_container_width=True)

# Insight automatico
peor_diff = bm_df.iloc[-1]
mejor_diff = bm_df.iloc[0]
st.markdown(f"""
<div class="insight-callout">
    <strong>Observacion:</strong> Veracruz esta peor que el promedio nacional en
    <strong>{(bm_df['diff_pp'] > 0).sum()} de {len(bm_df)} indicadores</strong>. La brecha mas
    grande es <strong>{peor_diff['indicador']}</strong> ({peor_diff['veracruz']}% en Veracruz vs
    {peor_diff['nacional']}% nacional, <strong>+{peor_diff['diff_pp']} puntos porcentuales</strong>).
</div>
""", unsafe_allow_html=True)


# ============================================================
# GRAFICA 03 — TOP MUNICIPIOS POR INDICADOR
# ============================================================
section_header("GRAFICA 03 / RANKING",
               f"Top {n_top} municipios — {ind_meta['nombre']}",
               "Municipios donde el indicador es mas alto (mas critico) y mas bajo (mejor situacion).")

col_peor, col_mejor = st.columns(2, gap="large")

with col_peor:
    st.markdown(f"""<p style="font-family: 'DM Sans'; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; color: {RED}; margin: 0.5rem 0 0.5rem 0;">— PEORES (MAS ALTO)</p>""", unsafe_allow_html=True)
    peores = df_f.nlargest(n_top, indicador_seleccionado)[["municipio", indicador_seleccionado, "poblacion"]]
    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(
        x=peores[indicador_seleccionado], y=peores["municipio"],
        orientation="h",
        marker=dict(color=RED, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in peores[indicador_seleccionado]],
        textposition="outside",
        textfont=dict(color=CREAM, family="JetBrains Mono, monospace", size=10),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}%<br>Poblacion: %{customdata:,}<extra></extra>",
        customdata=peores["poblacion"],
    ))
    fig_p = apply_chart_style(fig_p, height=max(360, n_top * 26))
    fig_p.update_layout(
        yaxis=dict(categoryorder="total ascending", showgrid=False,
                   tickfont=dict(color=CREAM, size=10, family="DM Sans, sans-serif")),
        xaxis=dict(showgrid=True, gridcolor=BORDER),
    )
    st.plotly_chart(fig_p, use_container_width=True)

with col_mejor:
    st.markdown(f"""<p style="font-family: 'DM Sans'; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; color: {GREEN}; margin: 0.5rem 0 0.5rem 0;">— MEJORES (MAS BAJO)</p>""", unsafe_allow_html=True)
    mejores = df_f.nsmallest(n_top, indicador_seleccionado)[["municipio", indicador_seleccionado, "poblacion"]]
    fig_m = go.Figure()
    fig_m.add_trace(go.Bar(
        x=mejores[indicador_seleccionado], y=mejores["municipio"],
        orientation="h",
        marker=dict(color=GREEN, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in mejores[indicador_seleccionado]],
        textposition="outside",
        textfont=dict(color=CREAM, family="JetBrains Mono, monospace", size=10),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}%<br>Poblacion: %{customdata:,}<extra></extra>",
        customdata=mejores["poblacion"],
    ))
    fig_m = apply_chart_style(fig_m, height=max(360, n_top * 26))
    fig_m.update_layout(
        yaxis=dict(categoryorder="total descending", showgrid=False,
                   tickfont=dict(color=CREAM, size=10, family="DM Sans, sans-serif")),
        xaxis=dict(showgrid=True, gridcolor=BORDER),
    )
    st.plotly_chart(fig_m, use_container_width=True)


# ============================================================
# GRAFICA 04 — HISTOGRAMA DE DISTRIBUCION
# ============================================================
section_header("GRAFICA 04 / DISTRIBUCION",
               f"Como se reparten los 212 municipios — {ind_meta['nombre']}",
               "Histograma del indicador a traves de los municipios. "
               "Una distribucion sesgada a la derecha indica que la mayoria de municipios tiene valores altos.")

fig_h = go.Figure()
fig_h.add_trace(go.Histogram(
    x=df_f[indicador_seleccionado],
    nbinsx=25,
    marker=dict(color=AMBER, line=dict(color=INK, width=1)),
    hovertemplate="Rango: %{x}%<br>Municipios: %{y}<extra></extra>",
))
mediana = df_f[indicador_seleccionado].median()
fig_h.add_vline(x=mediana, line=dict(color=CREAM, width=2, dash="dash"),
                annotation=dict(text=f"Mediana: {mediana:.1f}%",
                                font=dict(color=CREAM, size=11, family="JetBrains Mono, monospace"),
                                bgcolor=INK, bordercolor=AMBER, borderwidth=1, borderpad=4))
if prom_indicador_nac is not None:
    fig_h.add_vline(x=prom_indicador_nac, line=dict(color=BLUE, width=2, dash="dot"),
                    annotation=dict(text=f"Nacional: {prom_indicador_nac}%",
                                    font=dict(color=BLUE, size=11, family="JetBrains Mono, monospace"),
                                    bgcolor=INK, bordercolor=BLUE, borderwidth=1, borderpad=4,
                                    yshift=-25))

fig_h = apply_chart_style(fig_h, height=380)
fig_h.update_layout(
    xaxis=dict(title=f"{ind_meta['nombre']} (%)",
               title_font=dict(size=10, color=MUTED),
               showgrid=True, gridcolor=BORDER),
    yaxis=dict(title="Numero de municipios",
               title_font=dict(size=10, color=MUTED)),
    bargap=0.08,
)
st.plotly_chart(fig_h, use_container_width=True)


# ============================================================
# GRAFICA 05 — CORRELACION ENTRE INDICADORES
# ============================================================
section_header("GRAFICA 05 / CORRELACION",
               "Pobreza, rezago educativo y acceso a salud",
               "Cada burbuja es un municipio. Eje X: % rezago educativo. Eje Y: % pobreza. "
               "Tamaño = poblacion. Color = % sin acceso a salud.")

fig_sc = go.Figure()
fig_sc.add_trace(go.Scatter(
    x=df_f["ic_rezedu"], y=df_f["pobreza"],
    mode="markers",
    marker=dict(
        size=np.sqrt(df_f["poblacion"]) / 25 + 5,
        color=df_f["ic_asalud"],
        colorscale=[
            [0.0, GREEN],
            [0.5, AMBER],
            [1.0, RED],
        ],
        showscale=True,
        colorbar=dict(
            title=dict(text="Sin acceso<br>a salud (%)",
                       font=dict(color=COOL, size=10, family="JetBrains Mono, monospace")),
            tickfont=dict(color=COOL, size=10, family="JetBrains Mono, monospace"),
            thickness=12, len=0.85, x=1.02,
        ),
        line=dict(color=INK, width=0.5),
        opacity=0.8,
    ),
    text=df_f["municipio"],
    customdata=np.column_stack([df_f["poblacion"], df_f["ic_asalud"]]),
    hovertemplate=(
        "<b>%{text}</b><br>"
        "Pobreza: %{y:.1f}%<br>"
        "Rezago educativo: %{x:.1f}%<br>"
        "Sin salud: %{customdata[1]:.1f}%<br>"
        "Poblacion: %{customdata[0]:,}<extra></extra>"
    ),
))

fig_sc = apply_chart_style(fig_sc, height=520)
fig_sc.update_layout(
    xaxis=dict(title="% con rezago educativo",
               title_font=dict(size=10, color=MUTED),
               showgrid=True, gridcolor=BORDER),
    yaxis=dict(title="% en pobreza",
               title_font=dict(size=10, color=MUTED),
               showgrid=True, gridcolor=BORDER),
)
st.plotly_chart(fig_sc, use_container_width=True)

# Correlacion numerica
corr_edu = df_f["ic_rezedu"].corr(df_f["pobreza"])
corr_salud = df_f["ic_asalud"].corr(df_f["pobreza"])
st.markdown(f"""
<div class="insight-callout">
    <strong>Coeficientes de correlacion (Pearson):</strong>
    Pobreza vs Rezago educativo = <strong>{corr_edu:.2f}</strong>,
    Pobreza vs Sin acceso a salud = <strong>{corr_salud:.2f}</strong>.
    Valores cerca de 1 indican que cuando uno sube, el otro tambien.
    {("La pobreza y el rezago educativo van fuertemente de la mano en Veracruz." if corr_edu > 0.6 else "")}
</div>
""", unsafe_allow_html=True)


# ============================================================
# GRAFICA 06 — DESGLOSE POR GRUPO DEMOGRAFICO (NUEVO EN 2020)
# ============================================================
section_header("GRAFICA 06 / DESGLOSE",
               f"{ind_meta['nombre']} por grupo demografico",
               "CONEVAL 2020 publica los indicadores desglosados por subgrupos. "
               "Este grafico revela como la pobreza y las carencias afectan distinto a "
               "hombres vs mujeres, zonas rurales vs urbanas, distintas edades y poblacion indigena.")

if os.path.exists("veracruz_grupos.csv"):
    grupos = pd.read_csv("veracruz_grupos.csv")
    g_filt = grupos[grupos["indicador"] == indicador_seleccionado].copy()
    # Promedio ponderado por grupo (a nivel estatal)
    resumen_grupo = (
        g_filt.groupby(["grupo", "categoria_grupo"], as_index=False)
              .apply(lambda x: pd.Series({
                  "valor": (x["valor"] * x["poblacion_grupo"]).sum() / x["poblacion_grupo"].sum(),
                  "poblacion": x["poblacion_grupo"].sum(),
              }), include_groups=False)
              .reset_index(drop=True)
    )

    # Ordenar por categoria luego por valor
    cat_orden = {"Sexo": 0, "Ambito": 1, "Edad": 2, "Hablante": 3}
    resumen_grupo["_ord_cat"] = resumen_grupo["categoria_grupo"].map(cat_orden).fillna(99)
    resumen_grupo = resumen_grupo.sort_values(["_ord_cat", "valor"], ascending=[True, False])

    # Color por categoria
    color_map = {"Sexo": BLUE, "Ambito": GREEN, "Edad": AMBER, "Hablante": RED}
    colors_g = [color_map.get(c, MUTED) for c in resumen_grupo["categoria_grupo"]]

    # Promedio total estatal para linea de referencia
    prom_estatal = (df_f[indicador_seleccionado] * df_f["poblacion"]).sum() / df_f["poblacion"].sum()

    fig_g = go.Figure()
    fig_g.add_trace(go.Bar(
        x=resumen_grupo["valor"], y=resumen_grupo["grupo"],
        orientation="h",
        marker=dict(color=colors_g, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in resumen_grupo["valor"]],
        textposition="outside",
        textfont=dict(color=CREAM, family="JetBrains Mono, monospace", size=10),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}%<br>Categoria: %{customdata}<extra></extra>",
        customdata=resumen_grupo["categoria_grupo"],
    ))
    fig_g.add_vline(
        x=prom_estatal,
        line=dict(color=CREAM, width=1.5, dash="dash"),
        annotation=dict(text=f"Promedio Veracruz: {prom_estatal:.1f}%",
                        font=dict(color=CREAM, size=10, family="JetBrains Mono, monospace"),
                        bgcolor=INK, bordercolor=AMBER, borderwidth=1, borderpad=4),
    )
    fig_g = apply_chart_style(fig_g, height=440)
    fig_g.update_layout(
        yaxis=dict(showgrid=False, autorange="reversed",
                   tickfont=dict(color=CREAM, size=11, family="DM Sans, sans-serif")),
        xaxis=dict(title=f"{ind_meta['nombre']} (%)",
                   title_font=dict(size=10, color=MUTED),
                   showgrid=True, gridcolor=BORDER),
    )
    st.plotly_chart(fig_g, use_container_width=True)

    # Insight automatico — encontrar el grupo mas afectado vs el menos afectado
    grupo_max = resumen_grupo.loc[resumen_grupo["valor"].idxmax()]
    grupo_min = resumen_grupo.loc[resumen_grupo["valor"].idxmin()]
    diff = grupo_max["valor"] - grupo_min["valor"]
    st.markdown(f"""
    <div class="insight-callout">
        <strong>Brecha demografica:</strong> en {ind_meta['nombre'].lower()}, el grupo mas afectado
        es <strong>{grupo_max['grupo']}</strong> ({grupo_max['valor']:.1f}%) y el menos afectado es
        <strong>{grupo_min['grupo']}</strong> ({grupo_min['valor']:.1f}%). La diferencia es de
        <strong>{diff:.1f} puntos porcentuales</strong> — una desigualdad considerable dentro del
        mismo estado.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# TABLA ANEXO
# ============================================================
section_header("ANEXO / TABLA",
               "Catalogo completo de los 212 municipios",
               "Datos detallados para descargar y analizar por separado.")

cols_tabla = ["municipio", "poblacion", "pobreza", "plp",
              "ic_rezedu", "ic_asalud", "ic_segsoc", "ic_cv", "ic_sbv", "ic_ali"]
cols_tabla = [c for c in cols_tabla if c in df_f.columns]
sort_col = indicador_seleccionado if indicador_seleccionado in cols_tabla else "pobreza"
tabla_show = df_f[cols_tabla].sort_values(sort_col, ascending=False)
tabla_show.columns = ["Municipio", "Poblacion", "% Pobreza", "% Linea pobreza",
                       "% Rezago edu", "% Sin salud", "% Sin seg soc", "% Vivienda mala",
                       "% Sin serv basicos", "% Sin alimentacion"][:len(cols_tabla)]

with st.expander("Abrir tabla detallada"):
    st.dataframe(tabla_show, use_container_width=True, height=500)
    csv = tabla_show.to_csv(index=False).encode("utf-8")
    st.download_button("DESCARGAR CSV", csv, "veracruz_municipios_filtrados.csv", "text/csv")


# ============================================================
# PIE
# ============================================================
st.markdown(f"""
<div class="colophon">
    <div>PROYECTO 5 · VERACRUZ</div>
    <div>FUENTE · CONEVAL {meta.get('anio', 2020)} + CONABIO 2023</div>
    <div>PYTHON · STREAMLIT · PLOTLY</div>
</div>
""", unsafe_allow_html=True)
