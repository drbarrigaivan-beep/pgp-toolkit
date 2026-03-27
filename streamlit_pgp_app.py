import io
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PGP Toolkit", page_icon="📊", layout="wide")

MIN_AFILIADOS_COLS = ["afiliado_id", "edad", "sexo"]
MIN_SERVICIOS_COLS = ["afiliado_id", "fecha", "tipo_servicio", "costo"]

DISCLAIMER = """
Esta herramienta genera una estimación preliminar con fines analíticos.
No reemplaza validación actuarial, legal o financiera.
"""

def normalize_columns(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

def clean_afiliados(df):
    df = normalize_columns(df)
    df["edad"] = pd.to_numeric(df["edad"], errors="coerce")
    df = df.dropna(subset=["afiliado_id", "edad", "sexo"])
    return df

def clean_servicios(df):
    df = normalize_columns(df)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["costo"] = pd.to_numeric(df["costo"], errors="coerce")
    df = df.dropna()
    return df

def estimate_pgp(afiliados, servicios, factor, margen):
    total_afiliados = afiliados["afiliado_id"].nunique()
    costo_total = servicios["costo"].sum()
    base = costo_total / max(total_afiliados, 1)
    pgp = base * factor * (1 + margen)
    return round(pgp, 2), round(base, 2)

def build_note(entidad, periodo, base, pgp):
    return f"""
# Nota técnica preliminar de PGP

Entidad: {entidad}
Periodo: {periodo}

Costo per cápita base: ${base}
PGP estimada: ${pgp}

Generado con PGP Toolkit — versión preliminar
"""

st.title("PGP Toolkit")
st.subheader("De datos a nota técnica en minutos")
st.warning(DISCLAIMER)

with st.sidebar:
    entidad = st.text_input("Entidad", "Proyecto PGP")
    periodo = st.text_input("Periodo", "2025")
    factor = st.number_input("Factor riesgo", 0.5, 3.0, 1.0)
    margen = st.number_input("Margen", 0.0, 1.0, 0.1)

col1, col2 = st.columns(2)

with col1:
    afiliados_file = st.file_uploader("Afiliados CSV")

with col2:
    servicios_file = st.file_uploader("Servicios CSV")

if afiliados_file and servicios_file:
    afiliados = clean_afiliados(load_csv(afiliados_file))
    servicios = clean_servicios(load_csv(servicios_file))

    pgp, base = estimate_pgp(afiliados, servicios, factor, margen)

    st.success("Datos procesados")

    st.metric("PGP estimada", f"${pgp}")
    st.metric("Costo per cápita", f"${base}")

    note = build_note(entidad, periodo, base, pgp)

    st.download_button("Descargar nota", note, "nota.md")

else:
    st.info("Carga ambos archivos para comenzar")
