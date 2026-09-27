import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Visor Deserción UPL - Bogotá", layout="wide")

st.title("📊 Visor Interactivo: Tasa de Deserción Escolar por UPL en Bogotá")
st.markdown("Análisis espacial y caracterización por Unidades de Planeamiento Local (UPL).")

# Diccionario para mapear nombres técnicos a nombres amigables
NOMBRES_METRICAS = {
    "TtotalDeserOf_UPL": "Tasa Deserción Total (Oficial)",
    "TtotalDeserNOf_UPL": "Tasa Deserción Total (No Oficial)",
    "TtotalAprOf_UPL": "Tasa Aprobación Total (Oficial)",
    "TtotalAprNOf_UPL": "Tasa Aprobación Total (No Oficial)",
    "TtotalReprOf_UPL": "Tasa Reprobación Total (Oficial)",
    "TtotalReprNOf_UPL": "Tasa Reprobación Total (No Oficial)"
}

# Cargar datos procesados
@st.cache_data
def load_data():
    path = "data/processed/desercion_upl_procesado.geojson"
    gdf = gpd.read_file(path)
    
    # Convertir columnas tipo datetime a string
    for col in gdf.columns:
        if str(gdf[col].dtype).startswith('datetime') or col.lower() == 'fecha':
            gdf[col] = gdf[col].astype(str)
            
    return gdf

try:
    gdf = load_data()

    # Sidebar: Filtros e información
    st.sidebar.header("🔍 Filtros y Opciones")
    
    # Filtrar solo columnas existentes en el dataset que estén en nuestro diccionario
    metric_cols = [c for c in NOMBRES_METRICAS.keys() if c in gdf.columns]
    
    if not metric_cols:
        metric_cols = [c for c in gdf.columns if c.startswith("Ttotal")]

    # Selector con nombres legibles
    selected_metric_key = st.sidebar.selectbox(
        "Seleccione la variable a analizar:",
        options=metric_cols,
        format_func=lambda x: NOMBRES_METRICAS.get(x, x)
    )
    
    nombre_legible = NOMBRES_METRICAS.get(selected_metric_key, selected_metric_key)

    # Layout de 2 columnas
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(f"🗺️ Mapa Coroplético: {nombre_legible}")
        
        # Crear mapa centrado en Bogotá
        m = folium.Map(location=[4.6097, -74.0817], zoom_start=11, tiles="CartoDB positron")
        
        # Agregar capa GeoJSON
        folium.Choropleth(
            geo_data=gdf,
            name="choropleth",
            data=gdf,
            columns=["CODIGO_UPL", selected_metric_key],
            key_on="feature.properties.CODIGO_UPL",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=nombre_legible,
        ).add_to(m)

        # Tooltip para ver detalles al pasar el mouse
        style_function = lambda x: {'fillColor': '#ffffff00', 'color':'#000000', 'weight': 0.5}
        highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'weight': 1, 'fillOpacity': 0.2}
        
        info = folium.features.GeoJson(
            gdf,
            style_function=style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip=folium.features.GeoJsonTooltip(
                fields=["CODIGO_UPL", selected_metric_key],
                aliases=["UPL:", "Valor (%):"],
                style="background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
            )
        )
        m.add_child(info)
        
        st_folium(m, width=700, height=500)

    with col2:
        st.subheader("📈 Ranking por UPL")
        df_sorted = gdf.sort_values(by=selected_metric_key, ascending=False).head(10)
        fig = px.bar(
            df_sorted,
            x=selected_metric_key,
            y="CODIGO_UPL",
            orientation="h",
            title=f"Top 10 UPLs con mayor {nombre_legible}",
            labels={selected_metric_key: "Porcentaje (%)", "CODIGO_UPL": "UPL"},
            color=selected_metric_key,
            color_continuous_scale="Reds"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Resumen de Datos")
    st.dataframe(gdf[["CODIGO_UPL"] + metric_cols].head(10))

except Exception as e:
    st.error(f"Error al cargar la aplicación: {e}")