# Jam Bogotá - Análisis Espacial de Deserción Escolar por UPL

Solución analítica reproducible e interactiva desarrollada para la Jam de Datos de Bogotá.

## 📁 Estructura del Repositorio
* `data/raw/`: Datos GeoJSON originales descargados de Datos Abiertos Bogotá.
* `data/processed/`: GeoJSON estandarizado (EPSG:4326) listo para uso en el visor.
* `notebooks/`: Notebook de Jupyter (`01_procesamiento.ipynb`) para la limpieza y transformación.
* `outputs/`: Gráficos y mapas exportados.
* `docs/`: Nota técnica del proyecto.
* `app.py`: Aplicación web interactiva desarrollada en Streamlit.
* `requirements.txt`: Lista de dependencias del proyecto.

## 🚀 Instrucciones de Ejecución

1. **Clonar el repositorio y entrar a la carpeta:**
   ```bash
   cd jam-bogota-desercion
2. Crear y activar el entorno virtual (Windows)
   python -m venv venv
.\venv\Scripts\activate
3. Instalar dependencias
Bash
pip install -r requirements.txt
4. Ejecutar el Visor Web Interactivo
Bash
streamlit run app.py
