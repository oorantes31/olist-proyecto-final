"""
Aplicación Principal Streamlit - Olist E-Commerce Analytics.
Oscar Orantes - Proyecto Final Semana 12.
"""

import os
import sys

# Agregar la carpeta app al sys.path para importaciones relativas
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import streamlit as st
from comun import configurar_pagina
from paginas import riesgo, comentarios, pronostico, ficha

# Configuración global de página
configurar_pagina(titulo="Olist Analytics | Oscar Orantes", icono="🇧🇷")

# Definición de las 4 páginas requeridas con st.navigation
pg = st.navigation(
    [
        st.Page(
            riesgo.render,
            title="Riesgo de Pedidos",
            icon="🛡️",
            url_path="riesgo",
            default=True,
        ),
        st.Page(
            comentarios.render,
            title="Comentarios (NLP)",
            icon="💬",
            url_path="comentarios",
        ),
        st.Page(
            pronostico.render,
            title="Pronóstico Junio 2018",
            icon="📈",
            url_path="pronostico",
        ),
        st.Page(
            ficha.render,
            title="Ficha del Modelo y Ética",
            icon="📄",
            url_path="ficha",
        ),
    ]
)

with st.sidebar:
    st.markdown("### 🇧🇷 Olist Intelligence Platform")
    st.caption(
        "**Autor:** Oscar Orantes  \n"
        "**Programa:** KODIGO AI ML  \n"
        "**Proyecto Final:** Olist E-Commerce"
    )
    st.markdown("---")

pg.run()
