"""
Utilidades comunes para la aplicación Streamlit de Olist.
Oscar Orantes - Proyecto Final Semana 12.
"""

import json
import os
import sys
import joblib
import pandas as pd
import requests
import streamlit as st

# Rutas base y registro de preparacion.py en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from preparacion import crear_variables  # noqa: F401, E402

DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(BASE_DIR, "modelo_riesgo.joblib")
UMBRAL_PATH = os.path.join(BASE_DIR, "umbral.json")


def obtener_api_url() -> str:
    """Obtiene la URL de la API desde st.secrets, variable de entorno o URL de producción en Render."""
    try:
        if "API_URL" in st.secrets:
            return str(st.secrets["API_URL"]).rstrip("/")
    except Exception:
        pass
    return os.environ.get(
        "API_URL", "https://olist-proyecto-final.onrender.com"
    ).rstrip("/")


API_DEFAULT_URL = obtener_api_url()


def configurar_pagina(titulo="Olist E-Commerce Analytics", icono="📦"):
    st.set_page_config(
        page_title=titulo,
        page_icon=icono,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-size: 1.05rem;
            color: #4B5563;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background-color: #F8FAFC;
            border-left: 5px solid #3B82F6;
            padding: 1rem 1.2rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def cargar_modelo():
    """Carga el pipeline entrenado y el umbral calibrado."""
    pipeline = None
    umbral = 0.2611

    if os.path.exists(MODEL_PATH):
        try:
            pipeline = joblib.load(MODEL_PATH)
        except Exception as e:
            st.error(f"Error cargando pipeline local: {e}")

    if os.path.exists(UMBRAL_PATH):
        try:
            with open(UMBRAL_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                umbral = float(
                    data.get("umbral", data.get("umbral_10_operativo", 0.2611))
                )
        except Exception:
            pass

    return pipeline, umbral


@st.cache_data
def cargar_datos_pronostico():
    path = os.path.join(DATA_DIR, "pronostico_junio.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "pronostico" in df.columns and "pedidos_pronosticados" not in df.columns:
            df["pedidos_pronosticados"] = df["pronostico"]
        if "bajo" in df.columns and "intervalo_inferior_80" not in df.columns:
            df["intervalo_inferior_80"] = df["bajo"]
        if "alto" in df.columns and "intervalo_superior_80" not in df.columns:
            df["intervalo_superior_80"] = df["alto"]
        return df
    return pd.DataFrame()


@st.cache_data
def cargar_datos_sentimiento():
    path = os.path.join(DATA_DIR, "sentimiento_muestra.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "coincide" not in df.columns and {
            "sentimiento_estrellas",
            "sentimiento_modelo",
        }.issubset(df.columns):
            df["coincide"] = df["sentimiento_estrellas"].astype(str) == df[
                "sentimiento_modelo"
            ].astype(str)
        return df
    return pd.DataFrame()


def predecir_riesgo(pedido_dict, usar_api=True, api_url=None):
    """
    Realiza inferencia de riesgo de mala reseña.
    Intenta primero vía API FastAPI; si no responde, muestra aviso claro y usa el modelo local joblib.
    """
    target_url = (api_url or obtener_api_url()).rstrip("/")
    aviso_api = None

    if usar_api:
        try:
            res = requests.post(
                f"{target_url}/riesgo", json=pedido_dict, timeout=65.0
            )
            if res.status_code == 200:
                data = res.json()
                prob = float(
                    data.get(
                        "probabilidad",
                        data.get("probabilidad_mala_resena", 0.0),
                    )
                )
                umbral = float(
                    data.get("umbral", data.get("umbral_operativo_10", 0.2611))
                )
                es_alto = bool(
                    data.get("riesgo_alto", data.get("es_alto_riesgo", prob >= umbral))
                )
                if prob >= 0.50:
                    nivel = "Alto"
                elif es_alto:
                    nivel = "Medio-Alto (Accionable)"
                elif prob >= 0.15:
                    nivel = "Medio-Bajo"
                else:
                    nivel = "Bajo"

                data.setdefault("probabilidad", round(prob, 4))
                data.setdefault("probabilidad_mala_resena", round(prob, 4))
                data.setdefault("umbral", round(umbral, 4))
                data.setdefault("umbral_operativo_10", round(umbral, 4))
                data.setdefault("riesgo_alto", es_alto)
                data.setdefault("es_alto_riesgo", es_alto)
                data.setdefault("nivel_riesgo", nivel)
                data.setdefault(
                    "modelo_version",
                    "RandomForest-Calibrado-v1.0 (FastAPI Render)",
                )
                data["aviso_api"] = None
                return data, f"API FastAPI ({target_url})"
            else:
                aviso_api = (
                    f"La API en {target_url} devolvió HTTP {res.status_code}: {res.text}. "
                    "Se activó el pipeline local de respaldo."
                )
        except Exception as exc:
            aviso_api = (
                f"No fue posible conectar con la API en {target_url} ({type(exc).__name__}). "
                "La API puede estar despertando en Render o fuera de línea; se utilizó el pipeline local de respaldo."
            )

    # Inferencia local directa con modelo_riesgo.joblib
    pipeline, umbral = cargar_modelo()
    if pipeline is None:
        raise RuntimeError("No se encontró el modelo local ni la API disponible.")

    df_input = pd.DataFrame([pedido_dict])
    prob = float(pipeline.predict_proba(df_input)[0, 1])
    es_alto = bool(prob >= umbral)

    if prob >= 0.50:
        nivel = "Alto"
    elif prob >= umbral:
        nivel = "Medio-Alto (Accionable)"
    elif prob >= 0.15:
        nivel = "Medio-Bajo"
    else:
        nivel = "Bajo"

    segmento = (
        "Decil 10 (Máximo Riesgo Operacional)"
        if es_alto
        else "Riesgo Estándar / Normal"
    )
    accion = (
        "Intervención prioritaria proactiva dentro de las primeras 2 horas tras la entrega física."
        if es_alto
        else "Seguimiento estándar por correo electrónico / encuesta digital."
    )

    return {
        "order_id": pedido_dict.get("order_id", "ord_local"),
        "probabilidad": round(prob, 4),
        "probabilidad_mala_resena": round(prob, 4),
        "riesgo_alto": es_alto,
        "es_alto_riesgo": es_alto,
        "nivel_riesgo": nivel,
        "umbral": round(umbral, 4),
        "umbral_operativo_10": round(umbral, 4),
        "segmento_operativo": segmento,
        "accion_recomendada": accion,
        "modelo_version": "RandomForest-Calibrado-v1.0 (Local Pipeline Fallback)",
        "aviso_api": aviso_api,
    }, "Pipeline Local (Scikit-Learn Joblib)"
