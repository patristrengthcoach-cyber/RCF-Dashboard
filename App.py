import json
import math
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(
    page_title="RCF Juvenil A - Control de Carga",
    page_icon="⚽",
    layout="wide",
)

SHEET_ID = "1fviYHi9OK10AnQJYjYIjXf2r6-URyb7ZWGJB7v3bWEA"
GID = "1444133968"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

CATEGORIA = "Juvenil A"
NOMBRES_MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Posiciones de columna FIJAS, tal cual tu formulario (0 = columna A)
COL_TIMESTAMP = 0
COL_ID_NOMBRE = 1
COL_TIPO = 2          # "Responder en caso de:"
COL_FATIGA = 3        # Predisposición para entrenar
COL_SUENO = 4
COL_ORINA = 5
COL_ESTRES = 6
COL_MOLESTIA_MANANA = 7
COL_DOMS = 8
COL_DISPONIBLE = 9    # SI / NO
COL_RPE_ENTRENO = 10
COL_MOLESTIA_ENTRENO = 11
COL_RENDIMIENTO_ENTRENO = 12
COL_RPE_PARTIDO = 13
COL_MOLESTIA_PARTIDO = 14
COL_RENDIMIENTO_PARTIDO = 15

st.markdown(
    """
    <style>
    .stApp { background-color: #030712; }
    [data-testid="stMetricValue"] { font-weight: 800; }
    [data-testid="stMetricLabel"] { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: #d1d5db !important; }
    small { color: #d1d5db !important; }
    [data-testid="stMarkdownContainer"] p { color: #e5e7eb; }

    /* Filtros: misma estética oscura que el resto de cuadros */
    .st-key-filtros_box {
        background: linear-gradient(180deg, #0f172a 0%, #0a0f1c 100%) !important;
        border: 1px solid #1e293b !important; border-radius: 10px; padding: 0.35rem 0.6rem !important;
    }
    .st-key-filtros_box label, .st-key-filtros_box [data-testid="stMarkdownContainer"] p,
    .st-key-filtros_box [data-testid="stCaptionContainer"], .st-key-filtros_box [data-testid="stCaptionContainer"] * {
        color: #e5e7eb !important; font-weight: 600; font-size: 0.75rem !important;
    }
    .st-key-filtros_box [data-baseweb="select"] { font-size: 0.75rem !important; min-height: 2.1rem !important; }

    /* KPIs: caja muy resaltada */
    .st-key-kpi_box {
        background: linear-gradient(180deg, #0f172a 0%, #0a0f1c 100%) !important;
        border: 2px solid #155e63 !important;
        border-radius: 16px;
        padding: 1.1rem 0.75rem !important;
        box-shadow: 0 0 0 1px rgba(45,212,191,0.12), 0 10px 28px rgba(0,0,0,0.4);
    }

    /* Buscador y botones de la plantilla: más pequeños */
    [class*="st-key-buscar_input"] input { font-size: 0.8rem !important; padding: 0.35rem 0.6rem !important; color: #f1f5f9 !important; }
    [class*="st-key-borrar_sel"] button { font-size: 0.72rem !important; padding: 0.3rem 0.4rem !important; }
    [class*="st-key-verficha_"] button {
        font-size: 0.7rem !important; padding: 0.25rem 0.4rem !important;
        background-color: #0891b2 !important; border-color: #0891b2 !important; color: #ffffff !important;
    }
    [class*="st-key-verficha_"] button:hover { background-color: #0e7490 !important; border-color: #0e7490 !important; color: #ffffff !important; }

    /* Tarjetas de jugadores más compactas */
    .st-key-roster_scroll [data-testid="stVerticalBlockBorderWrapper"] { padding: 0.25rem 0.5rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CARGA DE DATOS
# ============================================================
@st.cache_data(ttl=600)
def cargar_datos_crudos() -> pd.DataFrame:
    return pd.read_csv(CSV_URL, header=0)


def valor(row, idx):
    if idx >= len(row):
        return None
    v = row.iloc[idx]
    return None if pd.isna(v) else v


def a_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parsear_id_nombre(texto):
    if texto is None:
        return None, None
    texto = str(texto).strip()
    partes = texto.split(" ", 1)
    if len(partes) == 2:
        return partes[0].strip(), partes[1].strip()
    return texto, texto


def color_carga(ua):
    if ua <= 200:
        return "#16a34a"
    if ua <= 400:
        return "#4ade80"
    if ua <= 600:
        return "#facc15"
    if ua <= 800:
        return "#fb923c"
    if ua <= 1000:
        return "#ef4444"
    return "#991b1b"


def color_escala_1_5(v):
    """1 = poco fatigado / nada estresado / sin DOMS (bueno) -> verde
    5 = muy fatigado / muy estresado / mucho DOMS (malo) -> rojo"""
    if v is None:
        return "#6b7280"
    if v <= 2:
        return "#16a34a"
    if v <= 3.2:
        return "#facc15"
    return "#ef4444"


def badge_escala(valor_num):
    color = color_escala_1_5(valor_num)
    texto = f"{valor_num:g}" if valor_num is not None else "—"
    return f"<span style='color:{color}; font-weight:800; font-size:1.4rem'>{texto}</span>"


def color_rpe(v):
    """RPE en escala 0-10 (Borg CR10): 0-3 suave, 4-5 moderado, 6-7 duro, 8-10 muy duro."""
    if v is None:
        return "#9ca3af"
    if v <= 3:
        return "#16a34a"
    if v <= 5:
        return "#facc15"
    if v <= 7:
        return "#fb923c"
    return "#ef4444"


def render_kpi(label, valor, color="#f1f5f9"):
    st.markdown(
        f"<div style='text-align:center; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.05em; "
        f"color:#9ca3af; font-weight:700;'>{label}</div>"
        f"<div style='text-align:center; font-size:1.8rem; font-weight:800; color:{color}; line-height:1.2;'>{valor}</div>",
        unsafe_allow_html=True,
    )


def render_section_title(texto):
    st.markdown(
        f"<div style='font-size:1.05rem; font-weight:800; color:#ffffff; "
        f"border-left:4px solid #10b981; padding-left:10px; margin:0.2rem 0 0.7rem 0;'>{texto}</div>",
        unsafe_allow_html=True,
    )


MINUTOS_ENTRENO_FILE = "minutos_entreno_guardado.json"
MINUTOS_PARTIDO_FILE = "minutos_partido_por_jugador.json"


def cargar_minutos_entreno_guardado():
    try:
        with open(MINUTOS_ENTRENO_FILE, "r") as f:
            return int(json.load(f).get("entreno", 75))
    except Exception:
        return 75


def guardar_minutos_entreno_en_disco(entreno):
    try:
        with open(MINUTOS_ENTRENO_FILE, "w") as f:
            json.dump({"entreno": entreno}, f)
        return True
    except Exception:
        return False


def cargar_minutos_partido_guardados():
    """Devuelve un diccionario {'idJugador|fecha': minutos}."""
    try:
        with open(MINUTOS_PARTIDO_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_minutos_partido_en_disco(id_jugador, fecha, minutos):
    datos = cargar_minutos_partido_guardados()
    datos[f"{id_jugador}|{fecha}"] = minutos
    try:
        with open(MINUTOS_PARTIDO_FILE, "w") as f:
            json.dump(datos, f)
        return True
    except Exception:
        return False


def ordenar_semanas_desc(semanas):
    def fecha_de_semana(s):
        try:
            return pd.to_datetime(s.replace("Semana ", ""), dayfirst=True)
        except Exception:
            return pd.Timestamp.min
    return sorted(semanas, key=fecha_de_semana, reverse=True)


def procesar_registros(df_raw: pd.DataFrame):
    """Convierte las filas crudas del Form en registros clasificados por tipo,
    y mantiene un 'último estado conocido' (wellness/disponibilidad/molestias) por jugador,
    igual que hacía tu Code.gs original con MASTER_ANALISIS."""

    filas = []
    for _, row in df_raw.iterrows():
        ts_raw = valor(row, COL_TIMESTAMP)
        if ts_raw is None:
            continue
        ts = pd.to_datetime(ts_raw, dayfirst=True, errors="coerce")
        if pd.isna(ts):
            continue

        id_j, nombre = parsear_id_nombre(valor(row, COL_ID_NOMBRE))
        if not id_j:
            continue

        tipo_raw = str(valor(row, COL_TIPO) or "").strip().upper()
        if "WELLNESS" in tipo_raw:
            tipo = "WELLNESS"
        elif "ENTREN" in tipo_raw:
            tipo = "ENTRENO"
        elif "PARTIDO" in tipo_raw or "COMPETICION" in tipo_raw:
            tipo = "PARTIDO"
        else:
            tipo = "OTRO"

        inicio_semana = ts - pd.Timedelta(days=ts.weekday())
        fila = {
            "timestamp": ts,
            "fecha": ts.strftime("%d/%m/%Y"),
            "semana": f"Semana {inicio_semana.strftime('%d/%m/%Y')}",
            "mes": NOMBRES_MESES[ts.month - 1],
            "idJugador": id_j,
            "nombre": nombre,
            "tipo": tipo,
        }

        if tipo == "WELLNESS":
            fila["fatiga"] = a_float(valor(row, COL_FATIGA))
            fila["sueno"] = a_float(valor(row, COL_SUENO))
            fila["orina"] = a_float(valor(row, COL_ORINA))
            fila["estres"] = a_float(valor(row, COL_ESTRES))
            fila["doms"] = a_float(valor(row, COL_DOMS))
            escalas = [v for v in [fila["fatiga"], fila["sueno"], fila["estres"], fila["doms"]] if v is not None]
            fila["wellness_score"] = sum(escalas) / len(escalas) if escalas else None
            disp_raw = valor(row, COL_DISPONIBLE)
            fila["disponible"] = str(disp_raw).strip().upper() if disp_raw is not None else None
            mol = valor(row, COL_MOLESTIA_MANANA)
            fila["molestias"] = str(mol).strip() if mol not in (None, "") else "Sin molestias"
            fila["rpe"] = None

        elif tipo == "ENTRENO":
            fila["rpe"] = a_float(valor(row, COL_RPE_ENTRENO))
            mol = valor(row, COL_MOLESTIA_ENTRENO)
            fila["molestias"] = str(mol).strip() if mol not in (None, "") else "Sin molestias"
            fila["rendimiento"] = a_float(valor(row, COL_RENDIMIENTO_ENTRENO))

        elif tipo == "PARTIDO":
            fila["rpe"] = a_float(valor(row, COL_RPE_PARTIDO))
            mol = valor(row, COL_MOLESTIA_PARTIDO)
            fila["molestias"] = str(mol).strip() if mol not in (None, "") else "Sin molestias"
            fila["rendimiento"] = a_float(valor(row, COL_RENDIMIENTO_PARTIDO))

        else:
            continue  # fila sin tipo reconocible, se ignora

        filas.append(fila)

    df = pd.DataFrame(filas)
    if df.empty:
        return df, {}

    df = df.sort_values("timestamp")

    # "Último estado conocido" por jugador, recorriendo cronológicamente (igual que el .gs original)
    estados = {}
    for _, r in df.iterrows():
        idj = r["idJugador"]
        if idj not in estados:
            estados[idj] = {"wellness": None, "disponibilidad": "DISPONIBLE", "molestias": "Sin molestias"}
        if r["tipo"] == "WELLNESS":
            if r.get("wellness_score") is not None:
                estados[idj]["wellness"] = r["wellness_score"]
            if r.get("disponible") in ("SI", "NO"):
                estados[idj]["disponibilidad"] = "DISPONIBLE" if r["disponible"] == "SI" else "NO DISPONIBLE"
        estados[idj]["molestias"] = r.get("molestias", estados[idj]["molestias"])

    return df, estados


@st.cache_data(ttl=600)
def cargar_y_procesar():
    df_raw = cargar_datos_crudos()
    return procesar_registros(df_raw)


# ============================================================
# ACWR — misma fórmula que en el ejemplo (carga aguda 7d / carga crónica media hasta 4 semanas)
# ============================================================
def calcular_acwr(historial_srpe: pd.DataFrame, timestamp_ref: pd.Timestamp):
    if historial_srpe.empty:
        return "N/A", "verde"

    primer_registro = historial_srpe["timestamp"].min()
    dias_en_bd = (timestamp_ref - primer_registro).days
    semanas_activas = max(1, math.ceil(dias_en_bd / 7))
    divisor_cronico = min(semanas_activas, 4)

    agudo = historial_srpe[
        (historial_srpe["timestamp"] >= timestamp_ref - pd.Timedelta(days=6))
        & (historial_srpe["timestamp"] <= timestamp_ref)
    ]["srpe"].sum()
    cronico = historial_srpe[
        (historial_srpe["timestamp"] >= timestamp_ref - pd.Timedelta(days=27))
        & (historial_srpe["timestamp"] <= timestamp_ref)
    ]["srpe"].sum()

    media_cronica = cronico / divisor_cronico if divisor_cronico else 0
    if media_cronica == 0:
        return (">2.00", "rojo") if agudo > 0 else ("N/A", "verde")

    acwr = agudo / media_cronica
    if acwr > 1.5:
        color = "rojo"
    elif acwr >= 1.3 or acwr < 0.8:
        color = "amarillo"
    else:
        color = "verde"
    return f"{acwr:.2f}", color


# ============================================================
# CABECERA
# ============================================================
col_logo, col_titulo = st.columns([1, 8])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=70)
    else:
        st.markdown("<div style='font-size:2.5rem'>⚽</div>", unsafe_allow_html=True)
with col_titulo:
    st.markdown(
        "<div style='font-size:1.9rem; font-weight:900; color:#ffffff; letter-spacing:0.01em; line-height:1.15;'>RACING CLUB DE FERROL</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"DIRECCIÓN DE RENDIMIENTO Y SALUD • {CATEGORIA.upper()}")

with st.spinner("Estableciendo conexión con el Google Sheet..."):
    try:
        df, estados = cargar_y_procesar()
    except Exception as e:
        st.error("❌ No se han podido cargar los datos. Revisa que el Sheet siga siendo público para lectura.")
        st.exception(e)
        st.stop()

if df.empty:
    st.warning("Conexión correcta, pero todavía no hay respuestas registradas en el formulario.")
    st.stop()

# ============================================================
# VISTA (botones resaltados) + MINUTOS DE ENTRENO (global, con guardado)
# ============================================================
if "vista_key" not in st.session_state:
    st.session_state["vista_key"] = "wellness"

minutos_guardados_entreno = cargar_minutos_entreno_guardado()

col_vista, col_min = st.columns([2, 1])
with col_vista:
    cv1, cv2, cv3 = st.columns(3)
    with cv1:
        if st.button("🧠 Wellness", use_container_width=True,
                      type="primary" if st.session_state["vista_key"] == "wellness" else "secondary"):
            st.session_state["vista_key"] = "wellness"
            st.rerun()
    with cv2:
        if st.button("⚽ RPE Entrenamiento", use_container_width=True,
                      type="primary" if st.session_state["vista_key"] == "rpe_entreno" else "secondary"):
            st.session_state["vista_key"] = "rpe_entreno"
            st.rerun()
    with cv3:
        if st.button("🔥 RPE Partido", use_container_width=True,
                      type="primary" if st.session_state["vista_key"] == "rpe_partido" else "secondary"):
            st.session_state["vista_key"] = "rpe_partido"
            st.rerun()
with col_min:
    cmin1, cmin2 = st.columns([1, 0.4])
    with cmin1:
        minutos_entreno = st.number_input("Min. Entreno (equipo)", min_value=1, value=minutos_guardados_entreno, step=5)
    with cmin2:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        if st.button("💾", help="Guardar minutos de entreno para próximas visitas", key="guardar_min_entreno"):
            if guardar_minutos_entreno_en_disco(minutos_entreno):
                st.toast("Minutos de entreno guardados ✅")
            else:
                st.toast("No se pudo guardar ❌")

vista_key = st.session_state["vista_key"]

minutos_partido_guardados = cargar_minutos_partido_guardados()

# calcular sRPE: entreno usa minutos globales, partido usa minutos guardados por jugador+partido
df_sesiones_todas = df[df["tipo"].isin(["ENTRENO", "PARTIDO"])].copy()


def _calcular_srpe(r):
    if r["rpe"] is None:
        return None
    if r["tipo"] == "ENTRENO":
        return r["rpe"] * minutos_entreno
    mins = minutos_partido_guardados.get(f"{r['idJugador']}|{r['fecha']}")
    return None if mins is None else r["rpe"] * mins


df_sesiones_todas["srpe"] = df_sesiones_todas.apply(_calcular_srpe, axis=1)
df_sesiones = df_sesiones_todas.dropna(subset=["srpe"])  # solo registros con carga calculable

timestamp_ref = df["timestamp"].max()

# ============================================================
# FILTROS (Mes -> Semana -> Día en cascada — categoría única: Juvenil A)
# ============================================================
meses_disponibles = sorted(df["mes"].unique(), key=lambda m: NOMBRES_MESES.index(m))

with st.container(border=True, key="filtros_box"):
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        mes_sel = st.selectbox("Mes", ["TODOS"] + meses_disponibles)

    df_para_semanas = df if mes_sel == "TODOS" else df[df["mes"] == mes_sel]
    semanas_disponibles = ordenar_semanas_desc(df_para_semanas["semana"].unique().tolist())
    with col_f2:
        semana_sel = st.selectbox("Semana", ["TODOS"] + semanas_disponibles)

    df_para_dias = df_para_semanas if semana_sel == "TODOS" else df_para_semanas[df_para_semanas["semana"] == semana_sel]
    dias_disponibles = sorted(
        df_para_dias["fecha"].unique(), key=lambda d: pd.to_datetime(d, dayfirst=True), reverse=True
    )
    with col_f3:
        dia_sel = st.selectbox(
            "Día",
            ["TODOS"] + dias_disponibles,
            help="Elige un día concreto para ver TODOS los registros de ese día por separado "
                 "(útil si hubo doble sesión y un jugador respondió 2 veces).",
        )

if vista_key == "wellness":
    df_vista = df[df["tipo"] == "WELLNESS"].copy()
elif vista_key == "rpe_entreno":
    df_vista = df_sesiones[df_sesiones["tipo"] == "ENTRENO"].copy()
else:
    df_vista = df_sesiones_todas[df_sesiones_todas["tipo"] == "PARTIDO"].copy()
    df_vista["tiene_minutos"] = df_vista.apply(
        lambda r: f"{r['idJugador']}|{r['fecha']}" in minutos_partido_guardados, axis=1
    )

if mes_sel != "TODOS":
    df_vista = df_vista[df_vista["mes"] == mes_sel]
if semana_sel != "TODOS":
    df_vista = df_vista[df_vista["semana"] == semana_sel]
if dia_sel != "TODOS":
    df_vista = df_vista[df_vista["fecha"] == dia_sel]

# ============================================================
# ROSTER
# - Si no hay un día concreto seleccionado: 1 fila por jugador (su registro más reciente).
# - Si hay un día concreto seleccionado: se muestran TODOS los registros de ese día,
#   incluidos los casos de doble sesión (2 registros del mismo jugador el mismo día).
# ============================================================
if dia_sel == "TODOS":
    if not df_vista.empty:
        idx_ultimo = df_vista.groupby("idJugador")["timestamp"].idxmax()
        roster = df_vista.loc[idx_ultimo].copy()
    else:
        roster = df_vista.copy()
else:
    roster = df_vista.sort_values("timestamp").copy()
    if not roster.empty:
        roster["hora"] = roster["timestamp"].dt.strftime("%H:%M")

acwr_vals, color_vals = [], []
for _, jrow in roster.iterrows():
    hist = df_sesiones[df_sesiones["idJugador"] == jrow["idJugador"]]
    acwr, color = calcular_acwr(hist, timestamp_ref)
    acwr_vals.append(acwr)
    color_vals.append(color)
roster["acwr"] = acwr_vals
roster["colorRiesgo"] = color_vals
roster["disponibilidad"] = roster["idJugador"].map(lambda i: estados.get(i, {}).get("disponibilidad", "DISPONIBLE"))
roster["molestias_estado"] = roster["idJugador"].map(lambda i: estados.get(i, {}).get("molestias", "Sin molestias"))

orden_riesgo = {"rojo": 0, "amarillo": 1, "verde": 2}
roster["orden"] = roster["colorRiesgo"].map(orden_riesgo)
roster = roster.sort_values("orden")

# ============================================================
# KPIs
# ============================================================
disponibles = int((roster["disponibilidad"] == "DISPONIBLE").sum())
bajas = roster.shape[0] - disponibles
alertas_rojo = int((roster["colorRiesgo"] == "rojo").sum())

if vista_key == "wellness":
    label_kpi1, valor_kpi1 = "Registros de Wellness", f"{roster.shape[0]} Reg."
else:
    total = df_vista.shape[0]
    con_rpe = int(df_vista["rpe"].notna().sum())
    pct = round(con_rpe / total * 100) if total > 0 else 0
    label_kpi1, valor_kpi1 = "Tasa de Respuesta RPE", f"{pct}%"

with st.container(border=True, key="kpi_box"):
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_kpi(label_kpi1, valor_kpi1)
    with k2:
        render_kpi("Disponibles", disponibles, "#22c55e")
    with k3:
        render_kpi("No disponible / Bajas", bajas, "#ef4444")
    with k4:
        if vista_key == "wellness" and "wellness_score" in roster.columns:
            media_w_serie = roster["wellness_score"].dropna()
            if not media_w_serie.empty:
                media_w = media_w_serie.mean()
                render_kpi("Media Wellness Grupal", f"{media_w:.1f}", color_escala_1_5(media_w))
            else:
                render_kpi("Media Wellness Grupal", "—")
        else:
            rpe_medio_serie = df_vista["rpe"].dropna() if "rpe" in df_vista.columns else pd.Series(dtype=float)
            if not rpe_medio_serie.empty:
                media_rpe = rpe_medio_serie.mean()
                render_kpi("RPE Medio", f"{media_rpe:.1f}", color_rpe(media_rpe))
            else:
                render_kpi("RPE Medio", "—")
    with k5:
        render_kpi("Alertas Críticas ACWR", alertas_rojo, "#ef4444")

st.divider()

# ============================================================
# ROSTER + FICHA INDIVIDUAL
# ============================================================
col_izq, col_der = st.columns([5, 7])
emoji_riesgo = {"rojo": "🔴", "amarillo": "🟡", "verde": "🟢"}
jugador_sel_id, fila_jugador = None, None

with col_izq:
    render_section_title("👥 Monitoreo de Plantilla")
    if roster.empty:
        st.info("Sin registros para el filtro activo.")
    else:
        indices_disponibles = roster.index.tolist()
        if "jugador_sel_idx" not in st.session_state:
            st.session_state["jugador_sel_idx"] = indices_disponibles[0]
        elif (
            st.session_state["jugador_sel_idx"] is not None
            and st.session_state["jugador_sel_idx"] not in indices_disponibles
        ):
            st.session_state["jugador_sel_idx"] = indices_disponibles[0]

        col_buscar, col_borrar = st.columns([3, 1])
        with col_buscar:
            busqueda = st.text_input(
                "Buscar", placeholder="🔍 Buscar jugador por nombre...", label_visibility="collapsed", key="buscar_input"
            )
        with col_borrar:
            if st.button("✕ Borrar", use_container_width=True, key="borrar_sel"):
                st.session_state["jugador_sel_idx"] = None
                st.rerun()

        roster_visible = roster[roster["nombre"].str.contains(busqueda, case=False, na=False, regex=False)] if busqueda else roster

        with st.container(height=520, key="roster_scroll"):
            if roster_visible.empty:
                st.caption("Ningún jugador coincide con la búsqueda.")
            for idx_fila, row in roster_visible.iterrows():
                es_actual = idx_fila == st.session_state["jugador_sel_idx"]
                with st.container(border=True):
                    cc1, cc2, cc3 = st.columns([1, 5, 2])
                    with cc1:
                        st.markdown(f"<div style='font-size:1.15rem; text-align:center'>{emoji_riesgo[row['colorRiesgo']]}</div>", unsafe_allow_html=True)
                    with cc2:
                        prefijo = "▶ " if es_actual else ""
                        st.markdown(
                            f"<div style='font-size:0.82rem; font-weight:700; color:#f1f5f9; line-height:1.3;'>{prefijo}[{row['idJugador']}] {row['nombre']}</div>",
                            unsafe_allow_html=True,
                        )
                        sub_fecha = row["hora"] if dia_sel != "TODOS" else row["fecha"]
                        if vista_key == "wellness":
                            val_dia = row.get("wellness_score")
                            color_dia = color_escala_1_5(val_dia)
                            etiqueta_dia = "Wellness"
                            val_txt = f"{val_dia:g}" if val_dia is not None else "—"
                        elif vista_key == "rpe_partido" and not row.get("tiene_minutos", False):
                            color_dia = "#ef4444"
                            etiqueta_dia = ""
                            val_txt = "No convocado"
                        else:
                            val_dia = row.get("rpe")
                            color_dia = color_rpe(val_dia)
                            etiqueta_dia = "RPE"
                            val_txt = f"{val_dia:g}" if val_dia is not None else "—"
                        st.markdown(
                            f"<div style='font-size:0.65rem; color:#9ca3af; line-height:1.4;'>{sub_fecha} · "
                            f"<span style='color:{color_dia}; font-weight:700;'>{etiqueta_dia} {val_txt}</span></div>",
                            unsafe_allow_html=True,
                        )
                    with cc3:
                        st.markdown(
                            f"<div style='font-size:0.6rem; color:#9ca3af; text-align:right;'>ACWR</div>"
                            f"<div style='font-size:0.9rem; font-weight:800; text-align:right;'>{row['acwr']}</div>",
                            unsafe_allow_html=True,
                        )
                    if es_actual:
                        st.markdown("<span style='color:#10b981; font-weight:700; font-size:0.7rem'>✓ Seleccionado</span>", unsafe_allow_html=True)
                    else:
                        if st.button("Ver ficha →", key=f"verficha_{idx_fila}", use_container_width=True):
                            st.session_state["jugador_sel_idx"] = idx_fila
                            st.rerun()

        idx_sel = st.session_state["jugador_sel_idx"]
        fila_jugador = roster.loc[idx_sel] if idx_sel is not None else None
        jugador_sel_id = fila_jugador["idJugador"] if fila_jugador is not None else None

with col_der:
    render_section_title("🩺 Ficha Individual")
    if fila_jugador is None:
        st.info("Selecciona un futbolista del roster para ver su ficha.")
    else:
      with st.container(border=True):
        st.markdown(
            f"<div style='font-size:1.5rem; font-weight:900; color:#ffffff; line-height:1.2;'>{fila_jugador['nombre']}</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"CÓDIGO DE REGISTRO: {jugador_sel_id} · Último registro: {fila_jugador['fecha']}")

        etiquetas_color = {"rojo": "Pico de Estrés (Peligro)", "amarillo": "Precaución", "verde": "Sweet Spot (Adaptación)"}
        st.markdown(
            f"**ACWR: {fila_jugador['acwr']}** {emoji_riesgo[fila_jugador['colorRiesgo']]} "
            f"— {etiquetas_color[fila_jugador['colorRiesgo']]}"
        )

        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                color_disp = "#22c55e" if fila_jugador["disponibilidad"] == "DISPONIBLE" else "#ef4444"
                render_kpi("Disponibilidad", fila_jugador["disponibilidad"], color_disp)
        with c2:
            with st.container(border=True):
                mol_val = fila_jugador["molestias_estado"]
                color_mol = "#fb923c" if mol_val and mol_val != "Sin molestias" else "#9ca3af"
                render_kpi("Molestias", mol_val, color_mol)

        if vista_key == "wellness":
            st.markdown("**Detalle Wellness de hoy**")
            cw1, cw2, cw3, cw4, cw5 = st.columns(5)
            with cw1:
                with st.container(border=True):
                    render_kpi("Fatiga", fila_jugador.get("fatiga") if fila_jugador.get("fatiga") is not None else "—", color_escala_1_5(fila_jugador.get("fatiga")))
            with cw2:
                with st.container(border=True):
                    render_kpi("Sueño", fila_jugador.get("sueno") if fila_jugador.get("sueno") is not None else "—", color_escala_1_5(fila_jugador.get("sueno")))
            with cw3:
                with st.container(border=True):
                    render_kpi("Estrés", fila_jugador.get("estres") if fila_jugador.get("estres") is not None else "—", color_escala_1_5(fila_jugador.get("estres")))
            with cw4:
                with st.container(border=True):
                    render_kpi("DOMS", fila_jugador.get("doms") if fila_jugador.get("doms") is not None else "—", color_escala_1_5(fila_jugador.get("doms")))
            with cw5:
                with st.container(border=True):
                    orina_val = fila_jugador.get("orina")
                    color_orina = "#ef4444" if orina_val is not None and orina_val >= 9 else "#f1f5f9"
                    render_kpi("Orina", orina_val if orina_val is not None else "—", color_orina)
                    if orina_val is not None and orina_val >= 9:
                        st.markdown("<div style='text-align:center; color:#ef4444; font-size:0.65rem; font-weight:700'>⚠️ Posible sangre</div>", unsafe_allow_html=True)

        elif vista_key == "rpe_partido":
            clave_partido = f"{jugador_sel_id}|{fila_jugador['fecha']}"
            tiene_min = fila_jugador.get("tiene_minutos", False)
            with st.container(border=True):
                st.markdown(f"**⚽ Minutos jugados — Partido del {fila_jugador['fecha']}**")
                if not tiene_min:
                    st.markdown("<span style='color:#ef4444; font-weight:800;'>🔴 No convocado (sin minutos guardados)</span>", unsafe_allow_html=True)
                cmp1, cmp2 = st.columns([2, 1])
                with cmp1:
                    valor_previo = int(minutos_partido_guardados.get(clave_partido, 0))
                    minutos_este_partido = st.number_input(
                        "Minutos jugados", min_value=0, max_value=130, value=valor_previo, step=5,
                        label_visibility="collapsed", key=f"min_p_{clave_partido}",
                    )
                with cmp2:
                    if st.button("💾 Guardar", key=f"guardar_p_{clave_partido}", use_container_width=True):
                        if guardar_minutos_partido_en_disco(jugador_sel_id, fila_jugador["fecha"], minutos_este_partido):
                            st.toast("Minutos del partido guardados ✅")
                            st.rerun()
                        else:
                            st.toast("No se pudo guardar ❌")

            st.markdown("**Detalle del último registro**")
            cr1, cr2 = st.columns(2)
            with cr1:
                with st.container(border=True):
                    rpe_val = fila_jugador.get("rpe")
                    render_kpi("RPE", rpe_val if rpe_val is not None else "—", color_rpe(rpe_val))
            with cr2:
                with st.container(border=True):
                    rend_val = fila_jugador.get("rendimiento")
                    render_kpi("Rendimiento (1-10)", rend_val if rend_val is not None else "—", "#f1f5f9")

        else:
            st.markdown("**Detalle del último registro**")
            cr1, cr2 = st.columns(2)
            with cr1:
                with st.container(border=True):
                    rpe_val = fila_jugador.get("rpe")
                    render_kpi("RPE", rpe_val if rpe_val is not None else "—", color_rpe(rpe_val))
            with cr2:
                with st.container(border=True):
                    rend_val = fila_jugador.get("rendimiento")
                    render_kpi("Rendimiento (1-10)", rend_val if rend_val is not None else "—", "#f1f5f9")

        with st.container(border=True):
            st.markdown("**Evolución de la Carga (sRPE, últimos 7 días)**")
            leyenda_ua = "".join(
                f"<span style='display:inline-flex; align-items:center; margin-right:10px; font-size:0.68rem; color:#cbd5e1;'>"
                f"<span style='width:9px; height:9px; border-radius:50%; background:{c}; display:inline-block; margin-right:4px;'></span>{t}</span>"
                for c, t in [
                    ("#16a34a", "0-200 Regenerativo"),
                    ("#4ade80", "200-400 Baja"),
                    ("#facc15", "400-600 Moderada"),
                    ("#fb923c", "600-800 Alta"),
                    ("#ef4444", "800-1000 Muy Alta"),
                    ("#991b1b", ">1000 Riesgo"),
                ]
            )
            st.markdown(f"<div style='margin-bottom:6px; line-height:1.8;'>{leyenda_ua}</div>", unsafe_allow_html=True)

            historial = df_sesiones[
                (df_sesiones["idJugador"] == jugador_sel_id)
                & (df_sesiones["timestamp"] >= timestamp_ref - pd.Timedelta(days=6))
                & (df_sesiones["timestamp"] <= timestamp_ref)
            ].sort_values("timestamp")
            if historial.empty:
                st.caption("Sin sesiones de Entreno/Partido en los últimos 7 días para este jugador.")
            else:
                colores_puntos = [color_carga(v) for v in historial["srpe"]]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=historial["fecha"], y=historial["srpe"], mode="lines+markers",
                    line=dict(color="#64748b", width=2),
                    marker=dict(color=colores_puntos, size=13, line=dict(color="#0f172a", width=1.5)),
                    fill="tozeroy", fillcolor="rgba(100,116,139,0.08)",
                    hovertemplate="Carga: %{y:.0f} UA<extra></extra>",
                ))
                fig.update_layout(
                    template="plotly_dark", height=260, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zeroline=False, linecolor="rgba(255,255,255,0.1)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.03)", zeroline=False, linecolor="rgba(255,255,255,0.1)", nticks=4),
                )
                st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# CARGA POR DÍA DE LA SEMANA — Entreno vs Partido
# ============================================================
render_section_title("📊 Carga por Día de la Semana — Entrenamiento vs Partido")
with st.container(border=True):
    df_chart = df_sesiones.copy()
    if mes_sel != "TODOS":
        df_chart = df_chart[df_chart["mes"] == mes_sel]

    if df_chart.empty:
        st.caption("Sin datos de carga para este filtro.")
    else:
        df_chart["dia_semana"] = df_chart["timestamp"].dt.dayofweek.map(lambda d: DIAS_SEMANA[d])

        if jugador_sel_id:
            df_chart_jugador = df_chart[df_chart["idJugador"] == jugador_sel_id]
            resumen = df_chart_jugador.groupby(["dia_semana", "tipo"])["srpe"].sum().unstack(fill_value=0)
            subtitulo = f"Individual — {fila_jugador['nombre']}"
        else:
            resumen = df_chart.groupby(["dia_semana", "tipo"])["srpe"].mean().unstack(fill_value=0)
            subtitulo = f"Media del equipo — {CATEGORIA}"
        st.caption(f"Análisis de carga para: {subtitulo}")

        resumen = resumen.reindex(DIAS_SEMANA).fillna(0)

        fig_semana = go.Figure()
        if "ENTRENO" in resumen.columns:
            fig_semana.add_trace(go.Bar(
                name="Entrenamiento", x=resumen.index, y=resumen["ENTRENO"], marker_color="#10b981",
                hovertemplate="%{x}<br>Entrenamiento: %{y:.0f} UA<extra></extra>",
            ))
        if "PARTIDO" in resumen.columns:
            fig_semana.add_trace(go.Bar(
                name="Partido", x=resumen.index, y=resumen["PARTIDO"], marker_color="#ef4444",
                hovertemplate="%{x}<br>Partido: %{y:.0f} UA<extra></extra>",
            ))
        fig_semana.update_layout(
            template="plotly_dark", height=280, barmode="group", bargap=0.3, bargroupgap=0.15,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.15)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, nticks=4, showticklabels=True),
        )
        st.plotly_chart(fig_semana, use_container_width=True)
