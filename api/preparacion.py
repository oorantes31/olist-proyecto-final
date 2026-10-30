"""Modulo de preparacion de datos y feature engineering para Olist.

Proyecto Final AIMLF1 - Oscar Orantes
Este modulo contiene la transformacion oficial de atributos derivada
del contrato de 18 columnas (17 predictoras + mala_resena).
Garantiza cero fuga de datos (data leakage) al momento de la entrega fisica.
"""

import numpy as np
import pandas as pd


def parse_fechas(df):
    """Convierte las columnas de timestamp a formato datetime si vienen como texto."""
    cols_fecha = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    df_out = df.copy()
    for col in cols_fecha:
        if col in df_out.columns:
            s = pd.to_datetime(df_out[col], errors="coerce")
            if getattr(s.dt, "tz", None) is not None:
                s = s.dt.tz_localize(None)
            df_out[col] = s
    return df_out


def crear_variables(df):
    """Transforma el DataFrame con las columnas del contrato de Olist

    generando caracteristicas operacionales, logisticas y comerciales
    disponibles al instante de la entrega fisica del pedido.

    Parametros:
    -----------
    df : pd.DataFrame
        DataFrame con las columnas del contrato (minimo las 17 predictoras).

    Retorna:
    --------
    pd.DataFrame
        DataFrame enriquecido con variables derivadas listas para el pipeline.
    """
    df_proc = parse_fechas(df)

    # 1. Variables de tiempo operacional (en dias)
    # Retraso real vs fecha prometida (positivo = entrega tardia)
    retraso_seg = (
        df_proc["order_delivered_customer_date"] - df_proc["order_estimated_delivery_date"]
    ).dt.total_seconds()
    dias_retraso = retraso_seg / 86400.0

    # Duracion total desde compra hasta entrega al cliente
    tiempo_entrega_seg = (
        df_proc["order_delivered_customer_date"] - df_proc["order_purchase_timestamp"]
    ).dt.total_seconds()
    dias_entrega = tiempo_entrega_seg / 86400.0

    # Tiempo de despacho del vendedor (desde aprobacion hasta entrega a transportista)
    despacho_seg = (
        df_proc["order_delivered_carrier_date"] - df_proc["order_approved_at"]
    ).dt.total_seconds()
    dias_despacho = despacho_seg / 86400.0

    # Tiempo de transito del transportista (carrier hasta cliente)
    transito_seg = (
        df_proc["order_delivered_customer_date"] - df_proc["order_delivered_carrier_date"]
    ).dt.total_seconds()
    dias_transito = transito_seg / 86400.0

    # Plazo prometido estimado original
    plazo_estimado_seg = (
        df_proc["order_estimated_delivery_date"] - df_proc["order_purchase_timestamp"]
    ).dt.total_seconds()
    dias_plazo_estimado = plazo_estimado_seg / 86400.0

    # 2. Indicadores booleanos / binarios
    es_entrega_tardia = (dias_retraso > 0).astype(float)
    entrega_adelantada = (dias_retraso < -3.0).astype(float)

    # 3. Geografica interestatal
    est_cliente = df_proc["estado_cliente"].fillna("SP").astype(str)
    est_vendedor = df_proc["estado_vendedor"].fillna("SP").astype(str)
    mismo_estado = (est_cliente == est_vendedor).astype(float)

    # 4. Ratios financieros y fisicos
    precio = pd.to_numeric(df_proc["precio_total"], errors="coerce").fillna(0.0)
    flete = pd.to_numeric(df_proc["flete_total"], errors="coerce").fillna(0.0)
    peso = pd.to_numeric(df_proc["peso_total_g"], errors="coerce").fillna(0.0)
    items = pd.to_numeric(df_proc["n_items"], errors="coerce").fillna(1.0).clip(lower=1.0)

    ratio_flete_precio = flete / (precio + 1e-4)
    precio_promedio_item = precio / items
    peso_promedio_item = peso / items

    # 5. Rellenar nulos razonables en numericas
    cuotas = pd.to_numeric(df_proc["cuotas_max"], errors="coerce").fillna(1.0)
    fotos = pd.to_numeric(df_proc["fotos_promedio"], errors="coerce").fillna(1.0)
    vendedores = pd.to_numeric(df_proc["n_vendedores"], errors="coerce").fillna(1.0)

    # 6. Agrupacion de categorias de producto para mitigar cardinalidad
    top_categorias = [
        "cama_mesa_banho",
        "beleza_saude",
        "esporte_lazer",
        "moveis_decoracao",
        "informatica_acessorios",
        "utilidades_domesticas",
        "relogios_presentes",
        "telefonia",
        "automotivo",
        "brinquedos",
    ]
    cat_serie = df_proc["categoria"].fillna("outros").astype(str).str.lower()
    categoria_clean = cat_serie.where(cat_serie.isin(top_categorias), other="outros")

    # 7. Construccion del DataFrame final de variables
    X_out = pd.DataFrame(
        {
            "dias_retraso": dias_retraso.fillna(0.0),
            "dias_entrega": dias_entrega.fillna(0.0),
            "dias_despacho": dias_despacho.fillna(0.0),
            "dias_transito": dias_transito.fillna(0.0),
            "dias_plazo_estimado": dias_plazo_estimado.fillna(0.0),
            "es_entrega_tardia": es_entrega_tardia,
            "entrega_adelantada": entrega_adelantada,
            "mismo_estado": mismo_estado,
            "n_items": items,
            "n_vendedores": vendedores,
            "precio_total": precio,
            "flete_total": flete,
            "peso_total_g": peso,
            "fotos_promedio": fotos,
            "cuotas_max": cuotas,
            "ratio_flete_precio": ratio_flete_precio,
            "precio_promedio_item": precio_promedio_item,
            "peso_promedio_item": peso_promedio_item,
            "estado_cliente": est_cliente,
            "estado_vendedor": est_vendedor,
            "tipo_pago": df_proc["tipo_pago"].fillna("credit_card").astype(str),
            "categoria": categoria_clean,
        },
        index=df.index,
    )

    return X_out
