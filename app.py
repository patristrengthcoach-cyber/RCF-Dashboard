import streamlit as st
import pandas as pd
import re

# ----------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard Cantera - Control de Carga",
    page_icon="⚽",
    layout="wide"
)

# ----------------------------------------------------
# URL DE TU GOOGLE SHEET (la de "edición", tal cual la copias del navegador)
# ----------------------------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fviYHi9OK10AnQJYjYIjXf2r6-URyb7ZWGJB7v3bWEA/edit?gid=1444133968#gid=1444133968"


def convertir_a_csv(url_editable: str) -> str:
    """
    Convierte la URL de edición de un Google Sheet en su URL de exportación CSV.
    - Extrae el ID del documento (lo que va después de /d/).
    - Extrae el 'gid' (identifica la PESTAÑA concreta dentro del Sheet), si existe.
    Esto es más seguro que un simple reemplazo de texto, porque también
    respeta la pestaña exacta que quieres leer (por si el Sheet tiene varias).
    """
    match_id = re.search(r"/d/([a-zA-Z0-9-_]+)", url_editable)
    if not match_id:
        raise ValueError("No se ha podido extraer el ID del Google Sheet de la URL proporcionada.")
    sheet_id = match_id.group(1)

    match_gid = re.search(r"gid=(\d+)", url_editable)
    gid = match_gid.group(1) if match_gid else "0"

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


CSV_URL = convertir_a_csv(SHEET_URL)


# ----------------------------------------------------
# CARGA DE DATOS
# @st.cache_data(ttl=600) -> guarda los datos en memoria 10 minutos (600 s).
# Pasado ese tiempo, la próxima vez que alguien abra la app,
# Streamlit vuelve a descargar el Sheet actualizado automáticamente.
# ----------------------------------------------------
@st.cache_data(ttl=600)
def cargar_datos(url_csv: str) -> pd.DataFrame:
    df = pd.read_csv(url_csv)
    return df


# ----------------------------------------------------
# INTERFAZ
# ----------------------------------------------------
st.title("⚽ Dashboard de Control de Carga - Cantera")
st.caption("Los datos se sincronizan automáticamente desde Google Sheets cada 10 minutos.")

col_a, col_b = st.columns([4, 1])
with col_b:
    if st.button("🔄 Forzar actualización ahora"):
        st.cache_data.clear()
        st.rerun()

try:
    df = cargar_datos(CSV_URL)

    st.success(f"✅ Conexión correcta. Se han cargado {df.shape[0]} filas y {df.shape[1]} columnas.")

    st.subheader("Datos crudos")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(
        "❌ No se han podido cargar los datos. Comprueba que el Google Sheet "
        "esté compartido como 'Cualquier persona con el enlace puede ver'."
    )
    st.exception(e)
