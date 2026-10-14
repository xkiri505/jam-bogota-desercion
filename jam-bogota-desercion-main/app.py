import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64

st.set_page_config(
    page_title="Visor Espacial de Deserción Escolar | Bogotá",
    page_icon="🎓",
    layout="wide"
)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

b64_bogota = get_base64_image("assets/logo_bogota.png")
b64_compensar = get_base64_image("assets/compensar_logo.webp")

st.markdown("""
    <style>
        .header-container {
            background: linear-gradient(135deg, #003366 0%, #C8102E 100%);
            padding: 24px 30px;
            border-radius: 12px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
        }
        .header-title {
            font-size: 26px;
            font-weight: 800;
            margin: 0;
            color: #FFFFFF;
            text-align: center;
        }
        .header-subtitle {
            font-size: 14px;
            margin-top: 6px;
            color: #FCD116;
            font-weight: 600;
            text-align: center;
        }
        .kpi-card {
            background-color: #FFFFFF;
            border-left: 5px solid #F37021;
            padding: 18px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            text-align: center;
        }
        .kpi-title {
            font-size: 12px;
            text-transform: uppercase;
            color: #6C757D;
            font-weight: 700;
        }
        .kpi-value {
            font-size: 26px;
            font-weight: 800;
            color: #003366;
        }
        .block-container {
            padding-top: 1.8rem;
        }
    </style>
""", unsafe_allow_html=True)

DICT_UPLS = {
    'UPL01': 'Sumapaz', 'UPL02': 'Cuenca del Tunjuelo', 'UPL03': 'Arborizadora', 
    'UPL04': 'Lucero', 'UPL05': 'Usme - Entrenubes', 'UPL06': 'Cerros Orientales',
    'UPL07': 'Torca', 'UPL08': 'Britalia', 'UPL09': 'Suba', 'UPL10': 'Tibabuyes',
    'UPL11': 'Engativá', 'UPL12': 'Fontibón', 'UPL13': 'Tintal', 'UPL14': 'Patio Bonito',
    'UPL15': 'Porvenir', 'UPL16': 'Edén', 'UPL17': 'Bosa', 'UPL18': 'Kennedy',
    'UPL19': 'Tunjuelito', 'UPL20': 'Rafael Uribe', 'UPL21': 'San Cristóbal',
    'UPL22': 'Restrepo', 'UPL23': 'Centro Histórico', 'UPL24': 'Chapinero',
    'Usaquén': 'Usaquén', 'UPL26': 'Toberín', 'UPL27': 'Niza', 'UPL28': 'Rincón de Suba',
    'UPL29': 'Tabora', 'UPL30': 'Salitre', 'UPL31': 'Puente Aranda', 
    'UPL32': 'Teusaquillo', 'UPL33': 'Barrios Unidos'
}

@st.cache_data
def load_data():
    gdf = gpd.read_file('data/processed/desercion_upl_procesado.geojson')
    
    if 'CODIGO_UPL' in gdf.columns:
        gdf['CODIGO_UPL'] = gdf['CODIGO_UPL'].astype(str).str.strip().str.upper()
        gdf['Nombre_UPL'] = gdf['CODIGO_UPL'].map(DICT_UPLS).fillna(gdf['CODIGO_UPL'])
    else:
        gdf['Nombre_UPL'] = 'Desconocido'
        
    for col in gdf.columns:
        if pd.api.types.is_datetime64_any_dtype(gdf[col]) or gdf[col].dtype == 'object':
            gdf[col] = gdf[col].astype(str)
            
    return gdf

try:
    gdf = load_data()
except Exception:
    st.error("No se pudo cargar el archivo procesado. Asegúrate de ejecutar el notebook primero.")
    st.stop()

st.sidebar.markdown("### ⚙️ Filtros y Opciones")
tipo_oferta = st.sidebar.radio(
    "Seleccione el tipo de oferta educativa:",
    ("Tasa Total (Oficial)", "Colegios Oficiales", "Colegios No Oficiales")
)

col_deser = [c for c in gdf.columns if 'deser' in c.lower() or 'tasa' in c.lower()]
col_tasa = col_deser[0] if col_deser else gdf.select_dtypes(include=['float64', 'int64']).columns[0]

# Detectar columnas de oficial y no oficial para la brecha
col_oficial = [c for c in gdf.columns if 'oficial' in c.lower() and 'no' not in c.lower()]
col_no_oficial = [c for c in gdf.columns if 'no_oficial' in c.lower() or 'no-oficial' in c.lower() or 'privad' in c.lower()]

col_oficial_str = col_oficial[0] if col_oficial else col_tasa
col_no_oficial_str = col_no_oficial[0] if col_no_oficial else col_tasa

if tipo_oferta == "Colegios Oficiales":
    col_tasa = col_oficial_str
elif tipo_oferta == "Colegios No Oficiales":
    col_tasa = col_no_oficial_str

gdf[col_tasa] = pd.to_numeric(gdf[col_tasa], errors='coerce').fillna(0)
gdf[col_oficial_str] = pd.to_numeric(gdf[col_oficial_str], errors='coerce').fillna(0)
gdf[col_no_oficial_str] = pd.to_numeric(gdf[col_no_oficial_str], errors='coerce').fillna(0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros Avanzados")

min_slider = float(gdf[col_tasa].min())
max_slider = float(gdf[col_tasa].max())
rango_tasa = st.sidebar.slider(
    "Filtrar por rango de tasa (%):",
    min_value=min_slider,
    max_value=max_slider,
    value=(min_slider, max_slider)
)

lista_upls = sorted(gdf['Nombre_UPL'].unique().tolist())
upls_seleccionadas = st.sidebar.multiselect(
    "Filtrar localidades específicas:",
    options=lista_upls,
    default=lista_upls
)

# --- PANEL DEL SIMULADOR EN SIDEBAR (PROBLEMÁTICA 4) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Simulador de Retención Escolar")
meta_reduccion = st.sidebar.slider(
    "Meta de reducción de deserción (%):",
    min_value=0.0,
    max_value=5.0,
    value=1.0,
    step=0.1,
    help="Proyecta cuántos estudiantes permanecerían en las aulas si se reduce la deserción según esta meta."
)

gdf_filtrado = gdf[
    (gdf[col_tasa] >= rango_tasa[0]) & 
    (gdf[col_tasa] <= rango_tasa[1]) & 
    (gdf['Nombre_UPL'].isin(upls_seleccionadas))
].copy()

if len(gdf_filtrado) == 0:
    st.warning("No hay UPLs que coincidan con los filtros seleccionados.")
    st.stop()

min_val_global = float(gdf[col_tasa].min())
max_val_global = float(gdf[col_tasa].max())
rango_amplitud = max_val_global - min_val_global

if rango_amplitud == 0:
    bins_mapa = [min_val_global - 0.1, min_val_global + 0.1]
else:
    bins_mapa = [
        min_val_global,
        min_val_global + rango_amplitud * 0.2,
        min_val_global + rango_amplitud * 0.4,
        min_val_global + rango_amplitud * 0.6,
        min_val_global + rango_amplitud * 0.8,
        max_val_global + 0.1
    ]

def obtener_color_por_tasa(tasa, b_list):
    if len(b_list) <= 2:
        return '#800026'
    if tasa <= b_list[1]:
        return '#ffffcc'
    elif tasa <= b_list[2]:
        return '#fed98d'
    elif tasa <= b_list[3]:
        return '#fe9929'
    elif tasa <= b_list[4]:
        return '#d7301f'
    else:
        return '#800026'

# Cabecera
img_bogota_html = f'<img src="data:image/png;base64,{b64_bogota}" style="height: 85px; width: auto; display: block; border-radius: 6px;">' if b64_bogota else ''
img_compensar_html = f'<img src="data:image/png;base64,{b64_compensar}" style="height: 95px; width: auto; display: block; filter: drop-shadow(0px 3px 6px rgba(0,0,0,0.3));">' if b64_compensar else ''

# Cabecera limpia y optimizada para Streamlit
st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #003366 0%, #C8102E 100%); padding: 24px 30px; border-radius: 12px; color: white; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: space-between; gap: 20px;">
        <div style="display: flex; align-items: center; min-width: 150px;">
            <img src="data:image/png;base64,{b64_bogota}" style="height: 85px; width: auto; display: block; border-radius: 6px;">
        </div>
        <div style="flex-grow: 1; padding: 0 15px; text-align: center;">
            <div style="font-size: 26px; font-weight: 800; margin: 0; color: #FFFFFF;">Visor Espacial de Deserción Escolar en Bogotá</div>
            <div style="font-size: 14px; margin-top: 6px; color: #FCD116; font-weight: 600;">Fundación Universitaria Compensar — Jam Bogotá | Análisis Territorial & Equidad Educativa</div>
        </div>
        <div style="display: flex; align-items: center; justify-content: flex-end; min-width: 150px;">
            <img src="data:image/webp;base64,{b64_compensar}" style="height: 95px; width: auto; display: block; filter: drop-shadow(0px 3px 6px rgba(0,0,0,0.3);">
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# KPIs Principales
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_upl = len(gdf_filtrado)
promedio_desercion = round(gdf_filtrado[col_tasa].mean(), 2)
max_val_filtrado = float(gdf_filtrado[col_tasa].max()) if len(gdf_filtrado) > 0 else 0
max_desercion = round(max_val_filtrado, 2)

col_colegios = [c for c in gdf.columns if 'colegio' in c.lower()]
total_colegios = int(pd.to_numeric(gdf_filtrado[col_colegios[0]], errors='coerce').sum()) if col_colegios else 0

# Estimación del Simulador (Problema 4)
estudiantes_estimados = total_colegios * 450  # Promedio estimado de estudiantes por plantel
estudiantes_rescatados = int(estudiantes_estimados * (meta_reduccion / 100))

with kpi1:
    st.markdown(f'<div class="kpi-card" style="border-left-color: #003366;"><div class="kpi-title">UPLs Analizadas</div><div class="kpi-value">{total_upl}</div></div>', unsafe_allow_html=True)

with kpi2:
    st.markdown(f'<div class="kpi-card" style="border-left-color: #C8102E;"><div class="kpi-title">Promedio ({tipo_oferta})</div><div class="kpi-value">{promedio_desercion}%</div></div>', unsafe_allow_html=True)

with kpi3:
    st.markdown(f'<div class="kpi-card" style="border-left-color: #FCD116;"><div class="kpi-title">Máxima Registrada</div><div class="kpi-value">{max_desercion}%</div></div>', unsafe_allow_html=True)

with kpi4:
    st.markdown(f'<div class="kpi-card" style="border-left-color: #28A745;"><div class="kpi-title">Impacto Estimado (-{meta_reduccion}%)</div><div class="kpi-value">+{estudiantes_rescatados} Est.</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_mapa, col_grafico = st.columns([3, 2])

with col_mapa:
    st.subheader(f"🗺️ Distribución Territorial: {tipo_oferta}")
    
    m = folium.Map(location=[4.30, -74.15], zoom_start=9, tiles="OpenStreetMap")
    
    choropleth = folium.Choropleth(
        geo_data=gdf_filtrado,
        name='choropleth',
        data=gdf_filtrado,
        columns=['CODIGO_UPL', col_tasa],
        key_on='feature.properties.CODIGO_UPL',
        fill_color='YlOrRd',
        fill_opacity=0.85,
        line_opacity=0.4,
        legend_name=f'{tipo_oferta} (%)',
        bins=bins_mapa
    )
    choropleth.add_to(m)
    
    if hasattr(choropleth, '_children'):
        for key in list(choropleth._children.keys()):
            if 'color_map' in key:
                del choropleth._children[key]
    
    folium.GeoJson(
        gdf_filtrado,
        style_function=lambda x: {'fillColor': '#00000000', 'color': '#000000', 'weight': 0.5},
        tooltip=folium.GeoJsonTooltip(
            fields=['Nombre_UPL', col_tasa],
            aliases=['UPL:', 'Valor (%):'],
            localize=True
        )
    ).add_to(m)
    
    st_folium(m, width='100%', height=480)
    
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; background-color: #FFFFFF; padding: 8px 12px; border-radius: 6px; color: #333333; font-size: 12px; font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <span><b>Escala de Color:</b></span>
            <span style="display: flex; align-items: center; gap: 4px;"><span style="background: #ffffcc; width: 14px; height: 14px; display: inline-block; border: 1px solid #ccc;"></span> Bajo</span>
            <span style="display: flex; align-items: center; gap: 4px;"><span style="background: #fed98d; width: 14px; height: 14px; display: inline-block;"></span> Moderado-Bajo</span>
            <span style="display: flex; align-items: center; gap: 4px;"><span style="background: #fe9929; width: 14px; height: 14px; display: inline-block;"></span> Moderado</span>
            <span style="display: flex; align-items: center; gap: 4px;"><span style="background: #d7301f; width: 14px; height: 14px; display: inline-block;"></span> Alto</span>
            <span style="display: flex; align-items: center; gap: 4px;"><span style="background: #800026; width: 14px; height: 14px; display: inline-block;"></span> Crítico</span>
        </div>
    """, unsafe_allow_html=True)

with col_grafico:
    st.subheader(f"📊 Ranking ({tipo_oferta})")
    
    df_sorted = gdf_filtrado.sort_values(by=col_tasa, ascending=False).copy()
    df_sorted['CODIGO_UPL'] = df_sorted['CODIGO_UPL'].astype(str)
    df_sorted['Color_Barra'] = df_sorted[col_tasa].apply(lambda x: obtener_color_por_tasa(x, bins_mapa))
    
    fig = px.bar(
        df_sorted,
        x=col_tasa,
        y='Nombre_UPL',
        orientation='h',
        text_auto='.1f',
        labels={col_tasa: 'Valor %', 'Nombre_UPL': 'UPL'}
    )
    
    fig.update_traces(marker_color=df_sorted['Color_Barra'], textposition='outside')
    
    fig.update_layout(
        margin=dict(l=0, r=20, t=10, b=0),
        yaxis=dict(autorange="reversed", title="", type='category', tickfont=dict(size=10)),
        xaxis=dict(title=f'{tipo_oferta} (%)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=11, color="#FFFFFF"),
        height=520
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- SECCIÓN DE ANÁLISIS ESTRATÉGICO Y BRECHA (PROBLEMÁTICA 3 & 4) ---
st.subheader("⚖️ Análisis de Brecha Institucional & Simulación de Reducción")

tab1, tab2 = st.tabs(["⚖️ Brecha Oficial vs. No Oficial", "🔮 Simulación de Impacto por UPL"])

with tab1:
    df_brecha = gdf_filtrado.sort_values(by=col_oficial_str, ascending=False).copy()
    
    fig_brecha = go.Figure()
    fig_brecha.add_trace(go.Bar(
        x=df_brecha['Nombre_UPL'],
        y=df_brecha[col_oficial_str],
        name='Colegios Oficiales',
        marker_color='#C8102E'
    ))
    fig_brecha.add_trace(go.Bar(
        x=df_brecha['Nombre_UPL'],
        y=df_brecha[col_no_oficial_str],
        name='Colegios No Oficiales',
        marker_color='#003366'
    ))
    
    fig_brecha.update_layout(
        barmode='group',
        xaxis_title="UPL",
        yaxis_title="Tasa de Deserción (%)",
        height=400,
        margin=dict(l=20, r=20, t=20, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_brecha, use_container_width=True)
    st.info("💡 **Interpretación de Equidad:** Permite identificar en qué territorios el sector público enfrenta mayores retos de deserción frente a la oferta privada para orientar alianzas y subsidios.")

with tab2:
    df_sim = gdf_filtrado.sort_values(by=col_tasa, ascending=False).copy()
    df_sim['Tasa_Actual'] = df_sim[col_tasa]
    df_sim['Tasa_Proyectada'] = (df_sim[col_tasa] - meta_reduccion).clip(lower=0)
    
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Bar(
        x=df_sim['Nombre_UPL'],
        y=df_sim['Tasa_Actual'],
        name='Tasa Actual (%)',
        marker_color='#D7301F'
    ))
    fig_sim.add_trace(go.Bar(
        x=df_sim['Nombre_UPL'],
        y=df_sim['Tasa_Proyectada'],
        name=f'Tasa Proyectada (-{meta_reduccion}%)',
        marker_color='#28A745'
    ))
    
    fig_sim.update_layout(
        barmode='group',
        xaxis_title="UPL",
        yaxis_title="Tasa de Deserción (%)",
        height=400,
        margin=dict(l=20, r=20, t=20, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_sim, use_container_width=True)
    st.success(f"🎯 **Meta Seleccionada:** Al reducir la deserción en un **{meta_reduccion}%**, se mantendrían aproximadamente **{estudiantes_rescatados} jóvenes** dentro del sistema educativo en las UPLs seleccionadas.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #ADB5BD;'>Desarrollado para la <b>Jam Bogotá</b> | Fundación Universitaria Compensar — 2026</p>", unsafe_allow_html=True)