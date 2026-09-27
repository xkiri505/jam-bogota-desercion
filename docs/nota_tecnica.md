# Nota Técnica: Análisis Espacial de la Tasa de Deserción Escolar por UPL en Bogotá

## 1. Contexto y Objetivos
La deserción escolar es un desafío crítico para la política educativa de Bogotá. Esta solución analiza la distribución espacial del fenómeno utilizando la división por Unidades de Planeamiento Local (UPL), identificando patrones territoriales que faciliten la toma de decisiones focalizadas.

## 2. Metodología y Fuentes de Datos
* **Fuente de Datos:** Datos Abiertos Bogotá (*Tasa de Deserción por UPL*).
* **Formatos:** Archivo espacial en formato GeoJSON.
* **Procesamiento Geográfico:** Estandarización de sistemas de referencia de coordenadas a EPSG:4326 (WGS84) para garantizar compatibilidad con visores cartográficos web.
* **Imputación y Limpieza:** Tratamiento de datos nulos y estructuración de variables cuantitativas por tipo de establecimiento (Oficial / No Oficial).

## 3. Hallazgos Principales
* Se identifican diferencias significativas en la tasa de deserción entre UPL periféricas e intraurbanas.
* Las tasas de aprobación y reprobación muestran un comportamiento inversamente proporcional claro según la cobertura institucional oficial.

## 4. Arquitectura de la Solución
* **Procesamiento ETL:** Python, GeoPandas, Pandas.
* **Visor Interactivo:** Streamlit, Folium (Choropleth), Plotly Express.