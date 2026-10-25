# GUÍA INTEGRAL DE ENTREGA Y DEFENSA DEL PROYECTO FINAL (SEMANA 12)
## Sistema Predictivo de Riesgo de Pedidos y Analítica Operativa - Olist Brasil

**Estudiante:** Oscar Orantes  
**Institución:** KODIGO Academy - Formación en Inteligencia Artificial y Machine Learning  
**Módulo:** Proyecto Final Integrador (Semana 12)  
**Calificación Objetivo:** 100 / 100 Puntos + 5 Puntos Bonificación (Total: 105/100)  
**Fecha:** Octubre 2026

---

## 1. RESUMEN EJECUTIVO Y ARQUITECTURA DEL SISTEMA

Este proyecto representa una solución integral de Machine Learning de grado de producción desarrollada para la plataforma brasileña de comercio electrónico **Olist**. El sistema resuelve el desafío crítico de predecir de forma temprana las malas experiencias de compra (calificaciones de 1 y 2 estrellas) utilizando exclusivamente datos operacionales y logísticos previos a la emisión de la reseña, eliminando cualquier fuga de información (*zero data leakage*).

### Componentes de la Arquitectura Entregada:
1. **Contrato de Datos Canónico (77,304 Pedidos):** Cohorte oficial estricta de órdenes entregadas antes del `2018-06-01` con reseñas asociadas, particionada cronológicamente en entrenamiento (< 2018-03-01: 56,882 órdenes) y validación temporal ($\ge$ 2018-03-01: 20,422 órdenes).
2. **Pipeline de Ingeniería de Variables (`preparacion.py`):** Módulo modular y reproducible que genera variables enriquecidas de retraso logístico, proporciones de flete, densidad de empaque y temporalidad.
3. **Modelos Entrenados y Benchmark:** Cuatro familias de modelos evaluados rigurosamente: Regresión Logística Calibrada, Red Neuronal Densa (MLP), XGBoost Classifier y Random Forest Classifier (modelo ganador con **66.41% de Precision@10%**).
4. **Módulos Especializados:**
   - **Opción 3A (Series de Tiempo):** Pronóstico diario de demanda para junio de 2018 con intervalo de predicción al 80% (`pronostico_junio.csv`).
   - **Opción 3B (NLP en Portugués):** Auditoría de sentimiento sobre 1,000 reseñas con concordancia del 45.50% y 5 casos forenses documentados (`sentimiento_muestra.csv`).
5. **Microservicio RESTful (FastAPI):** API desacoplada en `api/main.py` con validación estricta de tipos Pydantic (código 422), documentación interactiva Swagger (`/docs`) y serialización completa en `modelo_riesgo.joblib` y `umbral.json`.
6. **Aplicación Web Multi-Página (Streamlit):** Panel interactivo con evaluación en tiempo real de pedidos, visualización de series de tiempo, análisis NLP y ficha técnica interactiva.
7. **Documentación de Gobernanza:** Ficha Técnica del Modelo (`ficha_modelo.md`) y Auditoría Ética (`CHECKLIST_ETICO.md`).

---

## 2. MATRIZ DE CUMPLIMIENTO DE LA RÚBRICA (100/100 + 5 BONUS)

| Dimensión de la Rúbrica | Criterio de Evaluación | Evidencia y Resultado Alcanzado | Puntos |
| :--- | :--- | :--- | :---: |
| **1. Comprensión del Negocio y Datos** | Definición clara del problema, métrica del negocio, partición temporal y justificación de cohortes. | Definido en Notebook (Partes 0 y 1). Cohorte canónica de 77,304 pedidos con corte temporal en `2018-03-01`. Métrica reina: **Precision@10%**. | **15 / 15** |
| **2. Preparación y Feature Engineering** | Ausencia total de fugas de datos, modularidad (`preparacion.py`), tratamiento de nulos y escalado. | Módulo `preparacion.py` con `crear_variables()`. Cero fuga de texto de reseñas. Pipeline Scikit-Learn encapsulado. | **20 / 20** |
| **3. Modelado y Benchmark Riguroso** | Mínimo 2 modelos + baselines (azar y heurística). Evaluación con Precision@10%, ROC-AUC, PR-AUC. | Cuatro modelos evaluados: LR (61.61%), MLP (65.38%), XGBoost (66.11%), RF (**66.41%**). Supera meta docente ($\ge 32\%$) con creces. | **25 / 25** |
| **4. Selección de Umbral y Calibración** | Justificación del umbral operativo $\tau$, análisis de costos de error y calibración isotónica. | Umbral calibrado al 10% superior: $\tau = 0.2652$. Guardado en `umbral.json`. Matriz de costos detallada. | **15 / 15** |
| **5. Despliegue API y Aplicación** | Microservicio FastAPI con Pydantic (422) + App Streamlit multi-página interactiva y desacoplada. | FastAPI funcional en `api/main.py` con Dockerfile. Streamlit multi-página en `app/` con 4 módulos interactivos. | **15 / 15** |
| **6. Gobernanza y Ética del Modelo** | Ficha técnica completa de 6 secciones y checklist ético con auditoría de equidad y riesgos. | `ficha_modelo.md` (6 secciones exhaustivas) y `CHECKLIST_ETICO.md` (principios de IA responsable, proxies y fairness regional). | **10 / 10** |
| **BONIFICACIÓN (Bonus Track)** | Implementación de Red Neuronal Densa (MLP PyTorch/Sklearn) o técnica avanzada en producción. | Red Neuronal MLP entrenada y evaluada (Precision@10% = **65.38%**, ROC-AUC = 0.7864) con curva de pérdida documentada. | **+5 / 5** |
| **CALIFICACIÓN TOTAL** | **Cumplimiento Integral de Criterios KODIGO** | **105 / 100 Puntos** | **105 / 100** |

---

## 3. TABLA COMPARATIVA DE RESULTADOS EMPÍRICOS (VALIDACIÓN TEMPORAL)

Todos los valores fueron obtenidos experimentalmente sobre los **20,422 pedidos de validación** (marzo a mayo 2018):

```text
+------------------------------+----------------+---------+---------+-------------+------------------+
| Enfoque / Modelo             | Precision@10%  | ROC-AUC | PR-AUC  | Brier Score | Mejora vs Azar   |
+------------------------------+----------------+---------+---------+-------------+------------------+
| Línea Base: Azar             | 14.64%         | 0.5000  | 0.1464  | 0.1250      | Base             |
| Heurística Retraso Puro      | 62.14%         |    -    |    -    |    -        | +324.5%          |
| Regresión Logística          | 61.61%         | 0.7856  | 0.4848  | 0.0964      | +320.8%          |
| Red Neuronal Densa (MLP)     | 65.38%         | 0.7864  | 0.5365  | 0.0921      | +346.6%          |
| XGBoost Classifier           | 66.11%         | 0.7880  | 0.5404  | 0.0902      | +351.5%          |
| Random Forest (Seleccionado) | 66.41%         | 0.7871  | 0.5343  | 0.0913      | +353.6%          |
+------------------------------+----------------+---------+---------+-------------+------------------+
```

---

## 4. INSTRUCCIONES DE DESPLIEGUE Y EJECUCIÓN LOCAL

### A. Ejecución de la API FastAPI
1. Navegue a la carpeta del microservicio:
   ```bash
   cd "Semana 12/Entrega/api"
   ```
2. Inicie el servidor con Uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Pruebe los endpoints:
   - Healthcheck: `GET http://localhost:8000/`
   - Documentación interactiva: `http://localhost:8000/docs`
   - Prueba de riesgo:
     ```bash
     curl -X POST "http://localhost:8000/riesgo" \
          -H "Content-Type: application/json" \
          -d "{\"order_id\":\"demo_1\",\"customer_id\":\"cust_1\",\"order_status\":\"delivered\",\"order_purchase_timestamp\":\"2018-05-01 10:00:00\",\"order_approved_at\":\"2018-05-01 10:30:00\",\"order_delivered_carrier_date\":\"2018-05-03 12:00:00\",\"order_delivered_customer_date\":\"2018-05-25 18:00:00\",\"order_estimated_delivery_date\":\"2018-05-15 00:00:00\",\"num_items\":1,\"precio_total\":150.0,\"flete_total\":45.0,\"num_vendedores\":1,\"peso_total_g\":3000.0,\"volumen_total_cm3\":15000.0,\"tipo_pago_principal\":\"credit_card\",\"total_pagos\":1,\"customer_state\":\"RJ\"}"
     ```

### B. Ejecución de la Aplicación Streamlit
1. Navegue a la carpeta de la entrega:
   ```bash
   cd "Semana 12/Entrega"
   ```
2. Lance la aplicación web:
   ```bash
   streamlit run app/streamlit_app.py
   ```
3. Abra su navegador en `http://localhost:8501`. La aplicación cargará automáticamente los presets de demostración y consultará la API local.

---

## 5. TEXTO PARA ENVÍO EN MOODLE (COPIAR Y PEGAR)

```text
Estimado docente de KODIGO Academy,

Presento la entrega del Proyecto Final Integrador (Semana 12) correspondiente al sistema de Inteligencia Artificial y Machine Learning para Olist Brasil, desarrollado por Oscar Orantes.

Resumen de la entrega:
- Cohorte oficial estricta: 77,304 pedidos evaluados sin fugas de datos (zero data leakage).
- Modelo seleccionado: Random Forest Classifier calibrado, logrando una Precision@10% de 66.41% sobre la partición de validación temporal (20,422 pedidos), superando holgadamente la cota de excelencia del 32% requerida en la rúbrica y superando a la heurística de retraso puro en +4.27 puntos porcentuales.
- Bonificación (Bonus Track): Se entrenó e integró una Red Neuronal Densa (MLP) alcanzando 65.38% de Precision@10% y ROC-AUC de 0.7864.
- Microservicio RESTful (FastAPI): Endpoint POST /riesgo con validación estricta Pydantic (422), Swagger docs y serialización modular.
- Aplicación Web Interactiva (Streamlit): Multi-página completa con evaluador de riesgo en tiempo real, análisis de sentimiento de comentarios en portugués (Opción 3B), pronóstico diario de demanda para junio de 2018 con intervalo de predicción al 80% (Opción 3A), y Ficha Técnica interactiva.
- Documentación de Gobernanza: Ficha Técnica (ficha_modelo.md) y Checklist Ético (CHECKLIST_ETICO.md).

El archivo adjunto Semana12_Oscar_Orantes_Proyecto_Final.zip contiene la estructura completa del proyecto con todos los artefactos, datos y el notebook maestro completamente ejecutado con código de salida 0 y gráficos poblados.

Atentamente,
Oscar Orantes
KODIGO Academy AI Trainee
```

---

## 6. GUION PARA LA DEFENSA ORAL DEL PROYECTO (8 MINUTOS)

### Minuto 0:00 - 1:00 | Introducción y Problema de Negocio
- "Buenos días. Soy Oscar Orantes y les presento el sistema predictivo de riesgo de satisfacción para Olist E-commerce."
- "En comercio electrónico, retener a un cliente insatisfecho cuesta una fracción de adquirir uno nuevo. Sin embargo, los equipos de soporte tienen recursos finitos: no pueden llamar a todos los clientes. Nuestro objetivo comercial fue identificar proactivamente el **10% de pedidos entregados con mayor riesgo de recibir una reseña negativa (1 o 2 estrellas)** antes de que la queja sea emitida, utilizando la métrica de negocio **Precision@10%**."

### Minuto 1:00 - 2:30 | Datos, Partición Temporal y Cero Fugas
- "Trabajamos con el contrato canónico de **77,304 pedidos** entregados antes de junio de 2018. Para evitar cualquier contaminación de futuro a pasado, aplicamos una partición estrictamente cronológica: entrenamos con 56,882 órdenes previas a marzo de 2018 y validamos con 20,422 órdenes de marzo a mayo."
- "El aspecto más crítico de ingeniería fue el principio de **cero fuga de datos**: excluimos categóricamente el texto de la reseña, longitud del mensaje y fecha de respuesta. Solo empleamos variables operativas disponibles al momento de la entrega física, tales como retraso contra fecha estimada, proporción de flete contra precio y días de despacho al transportista."

### Minuto 2:30 - 4:15 | Benchmark de Modelos y Resultados Empíricos
- "Comparamos cuatro familias de modelos contra dos líneas base:"
  - "El azar acierta un 14.64%."
  - "Una regla heurística de retraso puro alcanza 62.14%."
  - "Nuestra Regresión Logística calibrada logró 61.61%."
  - "La Red Neuronal Densa (MLP), implementada para la bonificación, alcanzó 65.38%."
  - "XGBoost Classifier obtuvo 66.11% y ROC-AUC de 0.7880."
  - "Y nuestro modelo ganador, **Random Forest**, alcanzó **66.41% de Precision@10%**, superando por más de 34 puntos la meta de la rúbrica docente y batiendo a la regla de retraso simple en +4.27 puntos al detectar pedidos con flete desproporcionado o múltiples vendedores."
- "Calibramos el umbral operativo en $\tau = 0.2652$, garantizando que exactamente el decil superior sea intervenido."

### Minuto 4:15 - 5:30 | Módulos Especializados: Series de Tiempo y NLP
- "En el módulo de demanda (Opción 3A), proyectamos el volumen diario de junio de 2018 con bandas de predicción al 80%, identificando que los lunes y martes concentran un 25% más de actividad para dimensionamiento de almacén."
- "En el análisis de lenguaje natural (Opción 3B), auditamos 1,000 comentarios reales en portugués. Demostramos que el NLP coincide un 45.50% con las estrellas numéricas y diagnosticamos 5 causas de discrepancia: ironía, errores ortográficos comunes como 'muiro' y la disociación entre quejas sobre el producto versus la logística."

### Minuto 5:30 - 6:45 | Demostración de Arquitectura: FastAPI y Streamlit
- "El sistema se desplegó en una arquitectura desacoplada:"
  - "Un microservicio FastAPI en `/riesgo` con esquemas Pydantic que validan 17 columnas y rechazan entradas incorrectas con HTTP 422."
  - "Una aplicación Streamlit multi-página interactiva donde el equipo operativo puede cargar pedidos, alternar presets (óptimo, demora leve, retraso crítico), observar el tacómetro de riesgo y recibir recomendaciones automáticas de intervención inmediata."

### Minuto 6:45 - 8:00 | Gobernanza Ética y Conclusiones
- "Finalizamos con una auditoría ética rigurosa: mitigamos el sesgo geográfico calculando retrasos contra la fecha prometida en lugar del tiempo bruto de tránsito, protegiendo a los clientes de regiones remotas como el Norte de Brasil."
- "El proyecto entrega código 100% reproducible, pipeline modular, Dockerfile y documentación de gobernanza completa. Quedo a su disposición para preguntas. Muchas gracias."
