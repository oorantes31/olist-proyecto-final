"""
Módulo de Evaluación de Riesgo en Tiempo Real (Parte 2 y Parte 5).
Oscar Orantes - Proyecto Final Semana 12.
Cumple estrictamente el contrato de 17 columnas hacia POST /riesgo.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from comun import predecir_riesgo, obtener_api_url


ESTADOS_BR = [
    "SP", "RJ", "MG", "RS", "PR", "BA", "SC", "GO", "PE", "ES",
    "CE", "PA", "MT", "MA", "MS", "PB", "PI", "RN", "AL", "SE",
    "TO", "RO", "AM", "AC", "AP", "RR",
]

CATEGORIAS_OLIST = [
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
    "outros",
]


def render():
    st.markdown(
        '<div class="main-title">🛡️ Clasificador de Riesgo de Pedidos</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtitle">Predicción temprana de probabilidad de reseña negativa (1-2 estrellas) '
        "al momento de la entrega física, con umbral operativo calibrado para el 10% de mayor riesgo.</div>",
        unsafe_allow_html=True,
    )

    default_url = obtener_api_url()

    with st.sidebar:
        st.subheader("⚙️ Conexión con API")
        modo_api = st.checkbox("Consultar API FastAPI (/riesgo)", value=True)
        api_url = st.text_input("URL del Microservicio API", value=default_url)

        st.markdown("---")
        st.markdown(
            """
            **Umbral Operativo (Top 10%):**
            - $\\tau = 0.2611$ (10% priorizado)
            - Precisión en 10%: **66.41%**
            - Tasa base (azar): **14.64%**
            - Mejora vs Azar: **4.5x (+353.6%)**
            """
        )

    if "preset_riesgo" not in st.session_state:
        st.session_state["preset_riesgo"] = "optimo"

    st.subheader("📋 Casos de Prueba Rápidos (Presets)")
    col_p1, col_p2, col_p3 = st.columns(3)

    if col_p1.button(
        "🟢 Caso A: Entrega Óptima a Tiempo", use_container_width=True
    ):
        st.session_state["preset_riesgo"] = "optimo"
    if col_p2.button(
        "🟡 Caso B: Multi-ítem / Flete Elevado", use_container_width=True
    ):
        st.session_state["preset_riesgo"] = "medio"
    if col_p3.button(
        "🔴 Caso C: Pedido Severamente Retrasado", use_container_width=True
    ):
        st.session_state["preset_riesgo"] = "retrasado"

    preset = st.session_state["preset_riesgo"]

    if preset == "retrasado":
        def_dias_despacho = 6
        def_dias_transito = 24
        def_dias_estimados = 16
        def_precio = 180.0
        def_flete = 65.0
        def_peso = 4500.0
        def_estado_cli = "RJ"
        def_estado_ven = "SP"
        def_items = 2
        def_vendedores = 2
        def_cat = "moveis_decoracao"
    elif preset == "medio":
        def_dias_despacho = 4
        def_dias_transito = 16
        def_dias_estimados = 15
        def_precio = 95.0
        def_flete = 42.0
        def_peso = 2800.0
        def_estado_cli = "BA"
        def_estado_ven = "SP"
        def_items = 2
        def_vendedores = 1
        def_cat = "informatica_acessorios"
    else:
        def_dias_despacho = 1
        def_dias_transito = 5
        def_dias_estimados = 14
        def_precio = 135.0
        def_flete = 18.5
        def_peso = 1200.0
        def_estado_cli = "SP"
        def_estado_ven = "SP"
        def_items = 1
        def_vendedores = 1
        def_cat = "cama_mesa_banho"

    st.subheader("📝 Datos Operativos del Pedido (Contrato de 17 Columnas)")

    with st.form("form_pedido"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("##### 📦 Geografía y Producto")
            order_id = st.text_input("Order ID", value=f"ord_{preset}_001")
            estado_cliente = st.selectbox(
                "Estado del Cliente (UF)",
                ESTADOS_BR,
                index=ESTADOS_BR.index(def_estado_cli),
            )
            estado_vendedor = st.selectbox(
                "Estado del Vendedor (UF)",
                ESTADOS_BR,
                index=ESTADOS_BR.index(def_estado_ven),
            )
            categoria = st.selectbox(
                "Categoría del Producto",
                CATEGORIAS_OLIST,
                index=CATEGORIAS_OLIST.index(def_cat),
            )
            fotos_promedio = st.number_input(
                "Fotos promedio del producto",
                min_value=0.0,
                max_value=15.0,
                value=2.0,
                step=1.0,
            )

        with col2:
            st.markdown("##### ⏱️ Cronograma y Logística")
            fecha_base = datetime(2018, 5, 10, 10, 0, 0)
            dias_despacho = st.number_input(
                "Días hasta entrega al transportista",
                min_value=0,
                max_value=30,
                value=def_dias_despacho,
            )
            dias_transito = st.number_input(
                "Días totales hasta entrega al cliente",
                min_value=1,
                max_value=60,
                value=def_dias_transito,
            )
            dias_estimados = st.number_input(
                "Plazo de entrega prometido (días)",
                min_value=1,
                max_value=60,
                value=def_dias_estimados,
            )

            ts_purchase = fecha_base
            ts_approved = ts_purchase + timedelta(minutes=45)
            ts_carrier = ts_purchase + timedelta(days=int(dias_despacho))
            ts_delivered = ts_purchase + timedelta(days=int(dias_transito))
            ts_estimated = ts_purchase + timedelta(days=int(dias_estimados))

            retraso_calculado = (
                ts_delivered - ts_estimated
            ).total_seconds() / 86400.0
            if retraso_calculado > 0:
                st.warning(
                    f"⚠️ Retraso de {retraso_calculado:.1f} días frente a la fecha prometida."
                )
            else:
                st.success(
                    f"✅ Entregado {abs(retraso_calculado):.1f} días antes de la fecha prometida."
                )

        with col3:
            st.markdown("##### 💰 Ítems y Finanzas")
            n_items = st.number_input(
                "Número de artículos (n_items)",
                min_value=1,
                max_value=20,
                value=def_items,
            )
            n_vendedores = st.number_input(
                "Número de vendedores (n_vendedores)",
                min_value=1,
                max_value=10,
                value=def_vendedores,
            )
            precio_total = st.number_input(
                "Precio total artículos (BRL)",
                min_value=5.0,
                max_value=5000.0,
                value=float(def_precio),
            )
            flete_total = st.number_input(
                "Costo total de flete (BRL)",
                min_value=0.0,
                max_value=1000.0,
                value=float(def_flete),
            )
            peso_total_g = st.number_input(
                "Peso total (gramos)",
                min_value=0.0,
                max_value=50000.0,
                value=float(def_peso),
            )
            tipo_pago = st.selectbox(
                "Tipo de pago",
                ["credit_card", "boleto", "voucher", "debit_card"],
                index=0,
            )
            cuotas_max = st.number_input(
                "Cuotas de pago (cuotas_max)", min_value=0, max_value=24, value=1
            )

        submitted = st.form_submit_button(
            "🚀 Evaluar Riesgo de Pedido", use_container_width=True
        )

    if submitted:
        pedido_payload = {
            "order_id": order_id,
            "order_purchase_timestamp": ts_purchase.strftime("%Y-%m-%d %H:%M:%S"),
            "order_approved_at": ts_approved.strftime("%Y-%m-%d %H:%M:%S"),
            "order_delivered_carrier_date": ts_carrier.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "order_delivered_customer_date": ts_delivered.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "order_estimated_delivery_date": ts_estimated.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "estado_cliente": estado_cliente,
            "n_items": int(n_items),
            "n_vendedores": int(n_vendedores),
            "precio_total": float(precio_total),
            "flete_total": float(flete_total),
            "peso_total_g": float(peso_total_g),
            "fotos_promedio": float(fotos_promedio),
            "categoria": categoria,
            "estado_vendedor": estado_vendedor,
            "tipo_pago": tipo_pago,
            "cuotas_max": int(cuotas_max),
        }

        try:
            with st.spinner("Consultando motor predictivo de riesgo..."):
                resultado, origen = predecir_riesgo(
                    pedido_payload, usar_api=modo_api, api_url=api_url
                )

            if resultado.get("aviso_api"):
                st.warning(f"⚠️ {resultado['aviso_api']}")

            prob = resultado["probabilidad_mala_resena"]
            umbral = resultado["umbral_operativo_10"]
            es_alto = resultado["es_alto_riesgo"]
            nivel = resultado["nivel_riesgo"]
            version = resultado.get("modelo_version", "v1.0")

            st.markdown("---")
            st.markdown("### 📊 Resultado del Diagnóstico de Riesgo")
            st.caption(
                f"Motor de inferencia utilizado: **{origen}** | Versión: **{version}**"
            )

            r_col1, r_col2, r_col3, r_col4 = st.columns(4)
            r_col1.metric("Probabilidad de Mala Reseña", f"{prob*100:.1f}%")
            r_col2.metric("Umbral Operativo (Top 10%)", f"{umbral*100:.1f}%")
            r_col3.metric("Nivel de Riesgo", nivel)
            r_col4.metric(
                "¿Contactar al Cliente?",
                "SÍ (PRIORIDAD)" if es_alto else "NO (ESTÁNDAR)",
            )

            st.write("**Probabilidad Estimada frente al Umbral Operativo:**")
            st.progress(min(max(prob, 0.0), 1.0))

            if es_alto:
                st.error(
                    f"🚨 **RECOMENDACIÓN: CONTACTAR AL CLIENTE INMEDIATAMENTE** — "
                    f"La probabilidad estimada de mala reseña (**{prob*100:.1f}%**) supera el umbral "
                    f"operativo del 10% más riesgoso (**{umbral*100:.1f}%**)."
                )
                st.markdown(
                    """
                    **Protocolo de Intervención Proactiva (Antes de la Reseña):**
                    1. 📱 **Contacto proactivo en < 2 horas**: Enviar mensaje personalizado reconociendo la demora o fricción en la entrega.
                    2. 🎟️ **Compensación preventiva**: Ofrecer cupón de descuento o reembolso parcial del flete.
                    3. 🚚 **Auditoría de transportista**: Registrar incidencia logística en la ruta correspondiente.
                    """
                )
            else:
                st.success(
                    f"🟢 **RECOMENDACIÓN: FLUJO POSTVENTA ESTÁNDAR** — "
                    f"La probabilidad de mala reseña (**{prob*100:.1f}%**) está por debajo del umbral "
                    f"de intervención (**{umbral*100:.1f}%**). No requiere llamada prioritaria."
                )

            st.markdown("#### 🔍 Factores Operativos Calculados del Pedido")
            d_col1, d_col2, d_col3 = st.columns(3)
            d_col1.metric(
                "Retraso frente al estimado",
                f"{retraso_calculado:+.1f} días",
                delta="Tardío" if retraso_calculado > 0 else "A tiempo",
                delta_color="inverse" if retraso_calculado > 0 else "normal",
            )
            prop_flete = (flete_total / (precio_total + 1e-4)) * 100
            d_col2.metric(
                "Ratio Flete / Precio",
                f"{prop_flete:.1f}%",
                delta="Alto" if prop_flete > 35 else "Normal",
                delta_color="inverse" if prop_flete > 35 else "normal",
            )
            d_col3.metric(
                "Ruta Logística",
                f"{estado_vendedor} → {estado_cliente}",
                delta="Interestatal"
                if estado_vendedor != estado_cliente
                else "Local (Mismo Estado)",
            )

            with st.expander("🔌 Ver Payload Enviado (17 columnas) y Respuesta JSON"):
                c_json1, c_json2 = st.columns(2)
                c_json1.markdown("**Payload JSON (`POST /riesgo`):**")
                c_json1.json(pedido_payload)
                c_json2.markdown("**Respuesta JSON:**")
                c_json2.json(resultado)

        except Exception as e:
            st.error(f"Error procesando la inferencia: {e}")


if __name__ == "__main__":
    render()
