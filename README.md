# 🇧🇷 Proyecto Final Olist E-Commerce: Predicción de Riesgo, Sentimiento NLP, Pronóstico y Auditoría Ética

**Autor:** Oscar Orantes  
**Programa:** AI Machine Learning Trainee 1 — KODIGO Academy (Semana 12)  

---

## 🔗 Enlaces Oficiales de Despliegue (Producción)

| Componente | Enlace Público |
| :--- | :--- |
| 🌐 **Aplicación Interactiva (Streamlit Community Cloud)** | **[https://olist-proyecto-final-ulises-orantes.streamlit.app/](https://olist-proyecto-final-ulises-orantes.streamlit.app/)** |
| ⚙️ **API RESTful (Render)** | **[https://olist-proyecto-final.onrender.com](https://olist-proyecto-final.onrender.com)** |
| 📖 **Documentación Interactiva Swagger (`/docs`)** | **[https://olist-proyecto-final.onrender.com/docs](https://olist-proyecto-final.onrender.com/docs)** |
| 💻 **Repositorio GitHub** | **[https://github.com/oorantes31/olist-proyecto-final](https://github.com/oorantes31/olist-proyecto-final)** |

---

## 🎯 Descripción del Proyecto

Sistema integral de analítica predictiva y toma de decisiones operativas para **Olist** (el mayor conector de pequeñas tiendas en marketplaces de Brasil), diseñado para responder **qué pedidos acabados de entregar tienen mayor probabilidad de dejar una mala reseña (1 o 2 estrellas)** antes de que el cliente publique su calificación, permitiendo al equipo de atención al cliente intervenir el **10% más riesgoso**.

El proyecto abarca cinco componentes de extremo a extremo:
1. **Preparación de Datos y Contrato sin Fuga (`preparacion.py`)**: Integración de las 7 tablas relacionales de Olist (77,304 pedidos entregados antes del 1 de junio de 2018), partición estrictamente temporal (Entrenamiento `< 2018-03-01`: 56,882 pedidos; Validación `>= 2018-03-01`: 20,422 pedidos) y exclusión total de variables post-entrega (`review_comment_message`, `review_answer_timestamp`).
2. **Clasificación de Riesgo de Mala Reseña (`modelo_riesgo.joblib` + `umbral.json`)**: Comparación de 5 enfoques (Azar, Regla Heurística de Retraso, Regresión Logística, Random Forest, XGBoost y Red Neuronal Densa MLP). El modelo ganador calibrado alcanza **66.41% de Precisión en el 10% priorizado** (frente a **14.64%** del azar, una mejora de **4.5x**, y superando ampliamente la meta del 32%).
3. **Pronóstico de Demanda Diaria (`pronostico_junio.csv`)**: Serie de tiempo con rezagos (`lag_1`, `lag_7`, `lag_14`, media móvil de 7 días y calendario) evaluada en mayo de 2018 y proyectada para los 30 días de junio de 2018 con intervalo de predicción al 80%.
4. **Análisis de Sentimiento en Portugués (`sentimiento_muestra.csv`)**: Evaluación de concordancia entre sentimiento por estrellas y modelo NLP sobre 1,000 reseñas reales en portugués, con auditoría forense de discrepancias.
5. **Explicabilidad (SHAP), Auditoría de Equidad Geográfica y Despliegue Cloud (`api/` + `app/`)**: Microservicio RESTful en **FastAPI** publicado en **Render** y aplicación interactiva multipágina (`st.navigation`) en **Streamlit Community Cloud**.

---

## 📁 Estructura del Repositorio

```text
├── Orantes_Oscar_Proyecto_Final.ipynb  # Notebook principal ejecutado (Partes 1 a 4)
├── preparacion.py                      # Transformador de variables (FunctionTransformer)
├── modelo_riesgo.joblib                # Pipeline completo entrenado y calibrado
├── umbral.json                         # Umbral operativo del 10% superior (0.2611)
├── pronostico_junio.csv                # Pronóstico de 30 días (junio 2018) con banda 80%
├── sentimiento_muestra.csv             # Muestra de 1,000 reseñas con sentimiento NLP
├── api_url.txt                         # URL pública del microservicio en Render
├── app_url.txt                         # URL pública de la aplicación en Streamlit Cloud
├── api/                                # Microservicio FastAPI para Render
│   ├── main.py                         # Endpoints GET / y POST /riesgo (contrato 17 cols)
│   ├── preparacion.py                  # Módulo de ingeniería de características
│   ├── modelo_riesgo.joblib            # Pipeline serializado
│   ├── umbral.json                     # Umbral operativo
│   └── requirements.txt                # Dependencias con versiones exactas (==)
└── app/                                # Aplicación multipágina para Streamlit Cloud
    ├── streamlit_app.py                # Punto de entrada con st.navigation (4 páginas)
    ├── comun.py                        # Cliente API con respaldo local y caché
    ├── preparacion.py                  # Módulo de ingeniería de características
    ├── modelo_riesgo.joblib            # Pipeline local de respaldo
    ├── umbral.json                     # Umbral operativo
    ├── requirements.txt                # Dependencias de la app
    ├── data/                           # Datos precalculados para páginas de NLP y Pronóstico
    │   ├── pronostico_junio.csv
    │   └── sentimiento_muestra.csv
    └── paginas/                        # Módulos de las 4 páginas de la aplicación
        ├── riesgo.py                   # 1. Evaluación de riesgo en vivo (POST /riesgo)
        ├── comentarios.py              # 2. Análisis de sentimiento vs estrellas (NLP)
        ├── pronostico.py               # 3. Pronóstico de demanda junio 2018 (80% IC)
        └── ficha.py                    # 4. Ficha técnica (Model Card) y ética
```

---

## 🚀 Cómo Ejecutar Localmente

### 1. Levantar la API (FastAPI)
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Documentación interactiva disponible en `http://localhost:8000/docs`.

### 2. Levantar la Aplicación (Streamlit)
```bash
cd app
pip install -r requirements.txt
streamlit run streamlit_app.py
```
La aplicación se abrirá en `http://localhost:8501`.
