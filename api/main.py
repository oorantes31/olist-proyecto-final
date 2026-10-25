"""Microservicio de Inferencia de Riesgo Olist - FastAPI.

Proyecto Final AIMLF1 - Oscar Orantes
Expone endpoints RESTful para la predicción del riesgo de mala reseña
cumpliendo estrictamente el contrato de 17 columnas de entrada.
"""

import json
import os
import sys
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Asegurar que preparacion.py sea importable antes de cargar el modelo joblib
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from preparacion import crear_variables  # noqa: F401, E402

# Inicialización de FastAPI con documentación OpenAPI
app = FastAPI(
    title="Olist Proactive Risk API",
    description="API para detección temprana de riesgo de mala reseña (1-2 estrellas) en Olist.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(BASE_DIR, "modelo_riesgo.joblib")
UMBRAL_PATH = os.path.join(BASE_DIR, "umbral.json")

modelo = None
umbral_riesgo = 0.2611

if os.path.exists(MODEL_PATH):
    modelo = joblib.load(MODEL_PATH)

if os.path.exists(UMBRAL_PATH):
    with open(UMBRAL_PATH, "r", encoding="utf-8") as f:
        datos_u = json.load(f)
        umbral_riesgo = float(
            datos_u.get("umbral", datos_u.get("umbral_10_operativo", 0.2611))
        )

CONTRATO_PREDICTORES = [
    "order_id",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "estado_cliente",
    "n_items",
    "n_vendedores",
    "precio_total",
    "flete_total",
    "peso_total_g",
    "fotos_promedio",
    "categoria",
    "estado_vendedor",
    "tipo_pago",
    "cuotas_max",
]


class PedidoEntrada(BaseModel):
    order_id: str = Field(
        ...,
        description="Identificador único del pedido",
        examples=["e481f51cbdc54678b7cc49136f2d6af7"],
    )
    order_purchase_timestamp: str = Field(
        ...,
        description="Fecha y hora de compra",
        examples=["2017-10-02 10:56:33"],
    )
    order_approved_at: Optional[str] = Field(
        None,
        description="Fecha y hora de aprobación",
        examples=["2017-10-02 11:07:15"],
    )
    order_delivered_carrier_date: Optional[str] = Field(
        None,
        description="Fecha de entrega al carrier",
        examples=["2017-10-04 19:55:00"],
    )
    order_delivered_customer_date: str = Field(
        ...,
        description="Fecha de entrega al cliente",
        examples=["2017-10-10 21:25:13"],
    )
    order_estimated_delivery_date: str = Field(
        ...,
        description="Fecha estimada de entrega",
        examples=["2017-10-18 00:00:00"],
    )
    estado_cliente: str = Field(
        ..., description="Estado brasileño del cliente (UF)", examples=["SP"]
    )
    n_items: int = Field(
        ..., ge=1, description="Número total de artículos", examples=[1]
    )
    n_vendedores: int = Field(
        ..., ge=1, description="Número de vendedores únicos", examples=[1]
    )
    precio_total: float = Field(
        ..., ge=0.0, description="Suma total de precios en reales (BRL)", examples=[135.0]
    )
    flete_total: float = Field(
        ..., ge=0.0, description="Suma total de flete en reales (BRL)", examples=[18.5]
    )
    peso_total_g: float = Field(
        ..., ge=0.0, description="Peso total en gramos", examples=[1200.0]
    )
    fotos_promedio: float = Field(
        2.0, ge=0.0, description="Promedio de fotos del producto", examples=[2.0]
    )
    categoria: Optional[str] = Field(
        "cama_mesa_banho",
        description="Categoría principal del artículo",
        examples=["cama_mesa_banho"],
    )
    estado_vendedor: Optional[str] = Field(
        "SP", description="Estado brasileño del vendedor (UF)", examples=["SP"]
    )
    tipo_pago: Optional[str] = Field(
        "credit_card", description="Tipo de pago principal", examples=["credit_card"]
    )
    cuotas_max: int = Field(
        1, ge=1, description="Máximo de cuotas del pedido", examples=[1]
    )


class RespuestaRiesgo(BaseModel):
    order_id: str
    probabilidad: float
    riesgo_alto: bool
    umbral: float
    segmento_operativo: str
    accion_recomendada: str
    probabilidad_mala_resena: float
    es_alto_riesgo: bool
    nivel_riesgo: str
    umbral_operativo_10: float
    modelo_version: str


@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "ok",
        "service": "Olist Proactive Risk API",
        "version": "1.0.0",
        "model_loaded": modelo is not None,
        "umbral_top_10": round(umbral_riesgo, 4),
    }


@app.post(
    "/riesgo",
    response_model=RespuestaRiesgo,
    status_code=status.HTTP_200_OK,
    tags=["Inferencia"],
)
def evaluar_riesgo_pedido(pedido: PedidoEntrada):
    if modelo is None:
        raise HTTPException(
            status_code=503, detail="El modelo predictivo no se encuentra cargado."
        )

    datos = pedido.model_dump()
    fila_df = pd.DataFrame([datos], columns=CONTRATO_PREDICTORES)

    try:
        proba = float(modelo.predict_proba(fila_df)[:, 1][0])
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error durante el preprocesamiento: {str(e)}"
        )

    riesgo_alto = bool(proba >= umbral_riesgo)

    if proba >= 0.50:
        nivel = "Alto"
    elif riesgo_alto:
        nivel = "Medio-Alto (Accionable)"
    elif proba >= 0.15:
        nivel = "Medio-Bajo"
    else:
        nivel = "Bajo"

    if riesgo_alto:
        segmento = "Decil 10 (Máximo Riesgo Operacional)"
        accion = (
            "Intervención prioritaria proactiva dentro de las primeras 2 horas "
            "tras la entrega física (contacto WhatsApp y cupón preventivo)."
        )
    else:
        segmento = "Riesgo Estándar / Normal"
        accion = "Seguimiento estándar por correo electrónico / encuesta digital."

    return RespuestaRiesgo(
        order_id=pedido.order_id,
        probabilidad=round(proba, 4),
        riesgo_alto=riesgo_alto,
        umbral=round(umbral_riesgo, 4),
        segmento_operativo=segmento,
        accion_recomendada=accion,
        probabilidad_mala_resena=round(proba, 4),
        es_alto_riesgo=riesgo_alto,
        nivel_riesgo=nivel,
        umbral_operativo_10=round(umbral_riesgo, 4),
        modelo_version="RandomForest-Calibrado-v1.0 (FastAPI Render)",
    )
