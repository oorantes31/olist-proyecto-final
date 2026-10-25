"""
Módulo de Análisis de Sentimiento de Comentarios.
Oscar Orantes - Proyecto Final Semana 12.
"""

import streamlit as st
import pandas as pd
from comun import cargar_datos_sentimiento

def render():
    st.markdown('<div class="main-title">💬 Análisis de Sentimiento de Reseñas</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Evaluación de concordancia entre calificación por estrellas y modelo NLP '
        'sobre muestra de 1,000 comentarios reales en portugués (Opción 3B).</div>',
        unsafe_allow_html=True
    )

    df_sent = cargar_datos_sentimiento()
    
    if df_sent.empty:
        st.warning("No se encontró el archivo de datos de sentimiento (sentimiento_muestra.csv).")
        return

    # Métricas globales
    total = len(df_sent)
    coincidencias = (df_sent["coincide"] == True).sum()
    pct_coincidencia = (coincidencias / total) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Muestra Analizada", f"{total:,} reseñas")
    col2.metric("Acuerdo Estrellas vs NLP", f"{pct_coincidencia:.2f}%")
    col3.metric("Discrepancias Auditadas", f"{(total - coincidencias):,} ({(100 - pct_coincidencia):.2f}%)")
    col4.metric("Idioma Base", "Portugués (pt-BR)")

    st.markdown("---")
    
    # Matriz de Acuerdo / Cruzada
    st.subheader("📊 Matriz Cruzada: Calificación por Estrellas vs Sentimiento NLP")
    tabla_cruzada = pd.crosstab(
        df_sent["review_score"],
        df_sent["sentimiento_modelo"],
        margins=True,
        margins_name="Total"
    )
    st.dataframe(tabla_cruzada, use_container_width=True)

    # Filtros interactivos
    st.subheader("🔍 Explorador de Reseñas y Comentarios")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        filtro_estrellas = st.multiselect("Filtrar por Estrellas:", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])
    with f_col2:
        filtro_sent = st.multiselect("Filtrar por Sentimiento Modelo:", ["negative", "neutral", "positive"], default=["negative", "neutral", "positive"])
    with f_col3:
        solo_discrepancias = st.checkbox("Mostrar únicamente discrepancias", value=False)

    df_filtrado = df_sent[
        (df_sent["review_score"].isin(filtro_estrellas)) &
        (df_sent["sentimiento_modelo"].isin(filtro_sent))
    ]
    if solo_discrepancias:
        df_filtrado = df_filtrado[df_filtrado["coincide"] == False]

    st.caption(f"Mostrando {len(df_filtrado)} de {total} registros filtrados.")
    st.dataframe(
        df_filtrado[["review_score", "sentimiento_estrellas", "sentimiento_modelo", "coincide", "review_comment_message"]],
        use_container_width=True,
        height=300
    )

    st.markdown("---")
    st.subheader("🔬 Auditoría Cualitativa de 5 Casos de Discrepancia Críticos")
    
    casos = [
        {
            "caso": 1,
            "texto": "SEM QUEIXAS",
            "score": 5,
            "estrellas": "positive",
            "nlp": "neutral",
            "diagnostico": "Comentario extremadamente conciso. Al no contener adjetivos de entusiasmo ('otimo', 'maravilhoso'), el modelo lexico/NLP lo clasifica como neutral a pesar de que para un humano 'sin quejas' implica satisfacción plena."
        },
        {
            "caso": 2,
            "texto": "demora na entrega. e produto pesado demais",
            "score": 3,
            "estrellas": "neutral",
            "nlp": "negative",
            "diagnostico": "Disociación entre servicio y producto. El cliente sufrió demora y producto pesado, asignó 3 estrellas (indiferente), pero su lenguaje fue 100% negativo. Refleja cómo las estrellas suavizan reclamos verbales."
        },
        {
            "caso": 3,
            "texto": "Fui muiro bem atendido.",
            "score": 5,
            "estrellas": "positive",
            "nlp": "neutral",
            "diagnostico": "Error ortográfico común ('muiro' en lugar de 'muito'). Los analizadores sin corrección ortográfica o lematización fonética pierden el intensificador clave, cayendo en polaridad neutra."
        },
        {
            "caso": 4,
            "texto": "A LOJA É MUITO CONFIÁVEL E ATENCIOSA.",
            "score": 5,
            "estrellas": "positive",
            "nlp": "neutral",
            "diagnostico": "Lenguaje formal y en mayúsculas. Los tokenizadores estándar a veces penalizan las mayúsculas continuas o diccionarios corporativos que no mapean 'confiável' como sentimiento afectivo extremo."
        },
        {
            "caso": 5,
            "texto": "oi e como fica o produto,que ate agora não chegou.",
            "score": 2,
            "estrellas": "negative",
            "nlp": "neutral",
            "diagnostico": "Reclamo estructurado en forma interrogativa sin groserías ni insultos explícitos. Para el clasificador gramatical es una consulta informativa neutra; para operaciones es un cliente furioso con retraso crítico."
        }
    ]

    for c in casos:
        with st.expander(f"Caso {c['caso']}: \"{c['texto']}\" (Estrellas: {c['score']}⭐ vs NLP: {c['nlp']})"):
            st.markdown(f"**Texto de la Reseña:** `{c['texto']}`")
            st.markdown(f"**Sentimiento por Estrellas:** `{c['estrellas']}` | **Sentimiento Predicho por Modelo:** `{c['nlp']}`")
            st.info(f"**Diagnóstico Forense:** {c['diagnostico']}")

    st.markdown("### 💡 Implicaciones Estratégicas para Olist")
    st.markdown("""
    1. **Prevalencia de las Estrellas como Ground Truth**: Las estrellas numéricas reflejan la evaluación neta final del comprador.
    2. **Necesidad de Modelos Aspect-Based**: Se requiere segmentar el comentario entre satisfacción con el vendedor, con el producto y con la logística.
    3. **Enriquecimiento del Pipeline de Riesgo**: Por esta razón, el modelo predictivo de riesgo se diseñó **sin fugas de información** usando únicamente variables operativas previas a la reseña.
    """)

if __name__ == "__main__":
    render()
