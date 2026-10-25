"""
Módulo de Ficha Técnica del Modelo (Model Card).
Oscar Orantes - Proyecto Final Semana 12.
"""

import streamlit as st
import pandas as pd

def render():
    st.markdown('<div class="main-title">📄 Ficha Técnica del Modelo (Model Card)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Documentación estándar para transparencia, reproducibilidad y gobernanza '
        'del sistema de IA para Olist E-Commerce.</div>',
        unsafe_allow_html=True
    )

    t1, t2, t3, t4, t5, t6 = st.tabs([
        "1. Propósito", 
        "2. Datos", 
        "3. Desempeño", 
        "4. Limitaciones (OOD)", 
        "5. Ética y Equidad", 
        "6. Gobernanza"
    ])

    with t1:
        st.subheader("1. Propósito y Usuarios Destinados")
        st.markdown("""
        - **Objetivo Principal**: Identificar con anticipación pedidos entregados en Olist que presentan un alto riesgo de recibir una reseña negativa (calificación de 1 o 2 estrellas).
        - **Caso de Uso Operativo**: Permitir que el equipo de Experiencia al Cliente (CX) y Operaciones Logísticas focalice sus recursos de atención en el 10% de pedidos más críticos antes de que el cliente emita un comentario público negativo.
        - **Usuarios Previstos**:
          - Analistas de Operaciones Logísticas y Monitoreo de Transportistas.
          - Representantes de Atención al Cliente y Retención.
          - Sistemas de mensajería automatizada (bots de seguimiento y compensación).
        - **Uso No Previsto**:
          - No debe usarse para cancelar pedidos ni penalizar unilateralmente a vendedores sin una investigación previa.
          - No debe utilizarse para discriminar o negar servicio a compradores según su ubicación geográfica.
        """)

    with t2:
        st.subheader("2. Datos de Entrenamiento y Validación")
        st.markdown("""
        - **Población Total**: 77,304 órdenes entregadas antes del 1 de junio de 2018 con reseñas registradas en Olist.
        - **Estrategia de Partición Temporal** (Zero Data Leakage):
          - **Entrenamiento**: 56,882 órdenes (compras realizadas antes del 1 de marzo de 2018). Tasa de mala reseña: **13.15%**.
          - **Validación / Prueba Temporal**: 20,422 órdenes (compras realizadas a partir del 1 de marzo de 2018). Tasa de mala reseña: **14.64%**.
        - **Variables de Entrada (17 columnas raw sin fuga)**:
          - *Fechas*: compra, aprobación, entrega a transportista, entrega a cliente, entrega estimada.
          - *Transaccionales*: número de ítems, precio total, flete total, vendedores, peso en gramos, volumen en cm³, tipo de pago, cuotas.
          - *Geográficas*: estado federativo del cliente (UF).
          - **Exclusiones Críticas**: Se eliminaron completamente el texto de la reseña, longitud del comentario y fecha de respuesta de la reseña para evitar fugas futuras de información.
        """)

    with t3:
        st.subheader("3. Desempeño Cuantitativo del Modelo")
        st.markdown("""
        Evaluación estricta sobre el conjunto de validación temporal (20,422 pedidos) con el 10% de mayor riesgo focalizado:
        """)
        
        df_comp = pd.DataFrame([
            {"Enfoque / Modelo": "Línea Base: Azar", "Precision@10%": "14.64%", "ROC-AUC": "0.5000", "PR-AUC": "0.1464", "Mejora vs Azar": "0.0%"},
            {"Enfoque / Modelo": "Regla Heurística (Retraso)", "Precision@10%": "62.14%", "ROC-AUC": "-", "PR-AUC": "-", "Mejora vs Azar": "+324.5%"},
            {"Enfoque / Modelo": "Regresión Logística", "Precision@10%": "61.61%", "ROC-AUC": "0.7856", "PR-AUC": "0.4848", "Mejora vs Azar": "+320.8%"},
            {"Enfoque / Modelo": "Red Neuronal Densa (MLP)", "Precision@10%": "65.38%", "ROC-AUC": "0.7864", "PR-AUC": "0.5365", "Mejora vs Azar": "+346.6%"},
            {"Enfoque / Modelo": "XGBoost Classifier", "Precision@10%": "66.11%", "ROC-AUC": "0.7880", "PR-AUC": "0.5404", "Mejora vs Azar": "+351.5%"},
            {"Enfoque / Modelo": "Random Forest (Ganador)", "Precision@10%": "66.41%", "ROC-AUC": "0.7871", "PR-AUC": "0.5343", "Mejora vs Azar": "+353.6%"}
        ])
        st.dataframe(df_comp, use_container_width=True)
        st.success(
            "🏆 **Modelo Seleccionado**: Random Forest Classifier con calibración de probabilidad isotónica. "
            "Alcanza **66.41% de precisión en el 10% superior de mayor riesgo**, superando ampliamente la meta docente ($\ge 32.0\%$) "
            "y superando a la heurística de retraso puro en +4.27 puntos porcentuales absolutos."
        )

    with t4:
        st.subheader("4. Limitaciones y Condiciones Fuera de Distribución (OOD)")
        st.markdown("""
        - **Huelga Nacional de Camioneros (Mayo 2018)**: El dataset captura el impacto de la huelga en Brasil de mayo de 2018, lo que elevó la tasa de retrasos y quejas en la partición de validación.
        - **Condiciones Fuera de Distribución**:
          - Compras con estados de pedido no entregados (`canceled`, `unavailable`) requieren modelos separados.
          - Eventos atípicos de demanda masiva como Black Friday o Navidad alteran la relación volumen-retraso.
          - Nuevas categorías de productos o transportistas con SLA no registrados históricamente.
        """)

    with t5:
        st.subheader("5. Consideraciones Éticas y Equidad Geográfica")
        st.markdown("""
        - **Auditoría de Equidad Regional**:
          - Se evaluó el desempeño en estados del Sureste (SP, RJ) vs Norte/Nordeste (BA, PA, AM).
          - Los estados del Norte experimentan tiempos de tránsito naturalmente más largos por infraestructura física.
        - **Medidas Anti-Sesgo**:
          - Se utiliza la diferencia entre fecha prometida y real (`dias_retraso_vs_estimado`), en lugar del tiempo absoluto de viaje, para no estigmatizar pedidos de regiones alejadas que llegaron dentro de su plazo prometido.
          - No se aplican decisiones automatizadas adversas al comprador (ej. recargos discriminatorios).
        """)

    with t6:
        st.subheader("6. Gobernanza, Mantenimiento y Reentrenamiento")
        st.markdown("""
        - **Frecuencia de Reentrenamiento**: Mensual, incorporando las órdenes del mes anterior con ventana rodante de 12 meses.
        - **Métricas de Monitoreo en Producción**:
          - *Data Drift*: Kolmogorov-Smirnov en tiempos de entrega y distribución de flete.
          - *Concept Drift*: Monitoreo semanal de la tasa de reseñas negativas reales observadas en el decil clasificado de alto riesgo.
          - Si la Precision@10% desciende por debajo del 50%, se activa alerta de recalibración del umbral $\\tau$.
        - **Responsable Técnico**: Oscar Orantes (Machine Learning Engineer Trainee).
        """)

if __name__ == "__main__":
    render()
