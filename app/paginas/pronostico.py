"""
Módulo de Pronóstico de Demanda Diaria (Junio 2018).
Oscar Orantes - Proyecto Final Semana 12.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from comun import cargar_datos_pronostico

def render():
    st.markdown('<div class="main-title">📈 Pronóstico de Demanda Diaria</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Proyección de volumen de pedidos diarios para Junio de 2018 con intervalo '
        'de predicción al 80% (Opción 3A - Serie de Tiempo Operativa).</div>',
        unsafe_allow_html=True
    )

    df_pron = cargar_datos_pronostico()
    if df_pron.empty:
        st.warning("No se encontró el archivo de datos de pronóstico (pronostico_junio.csv).")
        return

    # Cálculos clave
    df_pron["fecha"] = pd.to_datetime(df_pron["fecha"])
    total_proyectado = int(df_pron["pedidos_pronosticados"].sum())
    promedio_diario = float(df_pron["pedidos_pronosticados"].mean())
    max_dia = df_pron.loc[df_pron["pedidos_pronosticados"].idxmax()]
    min_dia = df_pron.loc[df_pron["pedidos_pronosticados"].idxmin()]

    # Métricas superiores
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pedidos Proyectados Junio", f"{total_proyectado:,}")
    col2.metric("Promedio Diario Esperado", f"{promedio_diario:.1f} pedidos/día")
    col3.metric("Día Pico Proyectado", f"{max_dia['fecha'].strftime('%d-%b')} ({int(max_dia['pedidos_pronosticados'])} ped.)")
    col4.metric("MAE Baseline Ingenuo (Val)", "55.58 pedidos/día")

    st.markdown("---")

    # Gráfica interactiva con Plotly
    st.subheader("📊 Serie de Tiempo: Proyección con Banda de Confianza al 80%")

    fig = go.Figure()

    # Banda superior
    fig.add_trace(go.Scatter(
        x=df_pron["fecha"],
        y=df_pron["intervalo_superior_80"],
        mode="lines",
        line=dict(width=0),
        name="Límite Superior (80%)",
        showlegend=False
    ))

    # Banda inferior con relleno hacia la superior
    fig.add_trace(go.Scatter(
        x=df_pron["fecha"],
        y=df_pron["intervalo_inferior_80"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(59, 130, 246, 0.20)",
        name="Intervalo Predicción 80%",
        showlegend=True
    ))

    # Línea central pronosticada
    fig.add_trace(go.Scatter(
        x=df_pron["fecha"],
        y=df_pron["pedidos_pronosticados"],
        mode="lines+markers",
        line=dict(color="#1D4ED8", width=3),
        marker=dict(size=6, color="#1E40AF"),
        name="Pronóstico Central"
    ))

    fig.update_layout(
        title="Proyección Diaria de Pedidos Olist - Junio 2018",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Pedidos",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabla detallada y desglose por día de la semana
    st.subheader("🗓️ Desglose Diario y Planificación de Capacidad")
    
    col_t1, col_t2 = st.columns([3, 2])
    
    with col_t1:
        st.markdown("**Tabla Detallada de Pronóstico:**")
        df_display = df_pron.copy()
        df_display["fecha"] = df_display["fecha"].dt.strftime("%Y-%m-%d")
        st.dataframe(df_display, use_container_width=True, height=280)

    with col_t2:
        st.markdown("**Patrón por Día de la Semana:**")
        df_pron["dia_semana"] = df_pron["fecha"].dt.day_name()
        resumen_semanal = df_pron.groupby("dia_semana")["pedidos_pronosticados"].mean().round(1).reset_index()
        orden_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        resumen_semanal["orden"] = resumen_semanal["dia_semana"].map(lambda x: orden_dias.index(x) if x in orden_dias else 99)
        resumen_semanal = resumen_semanal.sort_values("orden").drop(columns=["orden"])
        resumen_semanal.columns = ["Día de la Semana", "Promedio Pedidos"]
        st.dataframe(resumen_semanal, use_container_width=True)

    st.markdown("### 📦 Recomendaciones para Operaciones y Almacén")
    st.markdown("""
    - **Picos de Principio de Semana**: Los lunes y martes registran el mayor flujo de pedidos (+25% sobre el fin de semana). Se recomienda reforzar el personal de empaquetado en bodegas aliadas esos días.
    - **Gestión de Stock de Seguridad**: Con un límite superior que alcanza picos de ~300 pedidos/día, la red logística debe contar con capacidad de absorción flexible.
    - **Sincronización con Colectas**: Coordinar horarios de recolección matutina con Correios para evitar cuellos de botella que generen demoras tempranas.
    """)

if __name__ == "__main__":
    render()
