# FICHA TÉCNICA DEL MODELO (MODEL CARD)
## Sistema Predictivo de Riesgo de Pedidos y Satisfacción del Cliente - Olist Brasil

**Autor:** Oscar Orantes  
**Institución:** KODIGO Academy - AI Machine Learning Trainee  
**Módulo:** Proyecto Final Integrador (Semana 12)  
**Fecha:** Octubre 2026  
**Versión del Modelo:** v1.0.0 (Producción)

---

### 1. PROPÓSITO Y USUARIOS DESTINADOS

- **Propósito Principal:**
  El modelo tiene como objetivo predecir de forma temprana la probabilidad de que un pedido entregado en el marketplace de Olist reciba una reseña negativa o insatisfecha (calificación de 1 o 2 estrellas, etiquetada como `mala_resena = 1`).
- **Caso de Uso Operativo (Intervención del Top 10%):**
  Dado que los equipos de soporte y experiencia al cliente (CX) disponen de un ancho de banda finito, el sistema está calibrado para seleccionar proactivamente el **10% de pedidos entregados de mayor riesgo** ($\tau = 0.2652$). Sobre este subconjunto focalizado, el equipo ejecuta acciones de mitigación inmediata (contacto vía WhatsApp/SMS, emisión preventiva de cupones de compensación del 15%, o escalamiento con la transportista) antes de que el comprador publique una queja pública.
- **Usuarios Destinados:**
  - Equipos de Operaciones Logísticas y Monitoreo de Transportistas de Olist.
  - Especialistas de Retención y Experiencia de Usuario (CX).
  - Sistemas automatizados de mensajería proactiva (CRM / Webhooks).
- **Usos Fuera de Alcance y Prohibidos:**
  - **No penalizar unilateralmente a vendedores:** El puntaje de riesgo del pedido no debe emplearse para dar de baja tiendas aliadas sin una auditoría de causa raíz (retraso de transportista vs empaque).
  - **No discriminación de compradores:** Está estrictamente prohibido utilizar el modelo para rechazar transacciones o aplicar sobrecargos a clientes en función de su ubicación geográfica o nivel socioeconómico.

---

### 2. DATOS DE ENTRENAMIENTO Y PARTICIÓN TEMPORAL

- **Población Total del Contrato:**
  Se construyó la cohorte oficial estricta de **77,304 pedidos** entregados antes del 1 de junio de 2018 con reseñas registradas en la base de datos de Olist.
- **Estrategia de Partición Temporal (Evitación de Data Leakage):**
  Para simular fielmente el entorno de producción y evitar la contaminación del futuro en el pasado, se aplicó una partición cronológica sobre `order_purchase_timestamp`:
  - **Conjunto de Entrenamiento:** 56,882 pedidos (compras realizadas antes del `2018-03-01`).  
    - Tasa base de malas reseñas: **13.15%**.
  - **Conjunto de Validación / Prueba Temporal:** 20,422 pedidos (compras realizadas entre el `2018-03-01` y el `2018-05-31`).  
    - Tasa base de malas reseñas: **14.64%** (refleja condiciones del mundo real con aumento de estrés logístico previo a junio de 2018).
- **Variables de Entrada (17 Columnas Raw Procesadas sin Fugas):**
  - *Temporales / Logísticas:* `dias_entrega_real`, `dias_entrega_estimada`, `dias_retraso_vs_estimado`, `dias_despacho_vendedor`, `entrega_fin_semana`.
  - *Comerciales y Carga:* `precio_total`, `flete_total`, `ratio_flete_precio`, `precio_por_item`, `peso_total_g`, `volumen_total_cm3`, `densidad_carga`.
  - *Operativas / Pago:* `num_items`, `num_vendedores`, `total_pagos`, `tipo_pago_principal`.
  - *Geográficas:* `customer_state`.
- **Integridad y Cero Fugas (Leakage-Free):**
  Se eliminaron categóricamente el texto de la reseña, título, longitud de caracteres y fecha de respuesta. Todas las variables predictivas se calculan a partir de eventos ocurridos antes o en el momento exacto de la entrega al cliente.

---

### 3. DESEMPEÑO CUANTITATIVO Y BENCHMARKING

La evaluación se realizó sobre el conjunto de validación temporal completo (**20,422 pedidos**). La métrica reina del negocio es **Precision@10%** (porcentaje de aciertos de malas reseñas en el decil superior de pedidos clasificados como de mayor riesgo).

| Modelo / Enfoque | Precision@10% | ROC-AUC | PR-AUC | Brier Score | Mejora vs Azar | Mejora vs Regla Retraso |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Línea Base 1: Azar** | 14.64% | 0.5000 | 0.1464 | 0.1250 | 0.0% | -76.4% |
| **Línea Base 2: Regla de Retraso Puro** | 62.14% | - | - | - | +324.5% | 0.0% |
| **Regresión Logística Calibrada** | 61.61% | 0.7856 | 0.4848 | 0.0964 | +320.8% | -0.87% |
| **Red Neuronal Densa (MLP PyTorch/Sklearn)** | 65.38% | 0.7864 | 0.5365 | 0.0921 | +346.6% | +5.22% |
| **XGBoost Classifier** | 66.11% | **0.7880** | **0.5404** | **0.0902** | +351.5% | +6.38% |
| **Random Forest Classifier (Seleccionado)** | **66.41%** | 0.7871 | 0.5343 | 0.0913 | **+353.6%** | **+6.86%** |

- **Criterio de Victoria y Calibración:**
  - El modelo ganador es **Random Forest** (seguido muy de cerca por XGBoost con diferencia inferior al 0.3%).
  - Su **Precision@10% es de 66.41%**, superando en **+34.41 puntos porcentuales** la cota de excelencia exigida por la rúbrica docente ($\ge 0.32$).
  - Frente al baseline de retraso puro (62.14%), el modelo demuestra capturar factores multivariados sutiles (costo excesivo de flete, pedidos multi-ítem y demoras de despacho del vendedor) que la heurística de retraso ignora por completo.
  - **Umbral Operativo Calibrado:** $\tau = 0.2652$.

---

### 4. LIMITACIONES, LÍMITES CONOCIDOS Y CONDICIONES FUERA DE DISTRIBUCIÓN (OOD)

- **Impacto de la Huelga Nacional de Camioneros (Greve dos Caminhoneiros, Mayo 2018):**
  Durante las últimas semanas de mayo de 2018, Brasil experimentó un bloqueo masivo de carreteras que paralizó el transporte nacional. Esto causó un repunte exógeno en los tiempos de tránsito. Si bien el modelo manejó robustamente este período elevando el score de riesgo por retraso, en situaciones de fuerza mayor la tasa de falsos positivos en flete y logística puede incrementarse temporalmente.
- **Limitaciones de Dominio (OOD):**
  - **Órdenes Canceladas o No Entregadas:** El modelo fue entrenado sobre pedidos con estado `delivered`. Para pedidos cancelados o en disputa previa, se requiere un clasificador específico.
  - **Picos Estacionales No Vistos:** Temporadas extremas como Black Friday generan dinámicas de expectativa de entrega diferentes a las observadas en el primer trimestre.
  - **Nuevas Categorías:** Productos de gran volumen (muebles pesados) con transportistas no tradicionales pueden requerir factores de ajuste local.

---

### 5. CONSIDERACIONES ÉTICAS Y AUDITORÍA DE EQUIDAD

- **Disparidad Geográfica (Sureste vs Norte/Nordeste):**
  Brasil presenta una profunda asimetría de infraestructura: los estados del Sureste (SP, RJ, MG) concentran los centros de distribución, logrando entregas en 3-7 días, mientras que estados del Norte y Nordeste (AM, PA, BA) promedian 18-30 días.
- **Medidas de Equidad Implementadas:**
  - Para evitar penalizar sistemáticamente a las regiones remotas, la variable logística principal es **`dias_retraso_vs_estimado`** (desviación respecto a la promesa al cliente) y no los días brutos de viaje. Si un pedido a Manaos tarda 25 días pero se prometieron 30, el modelo no lo marca como retrasado.
  - No se emplean códigos postales de nivel micro para evitar sesgos socioeconómicos (redlining digital).
- **Supervisión Humana (Human-in-the-Loop):**
  El sistema se utiliza como soporte para la priorización de ayuda, **nunca para denegación de servicios o penalizaciones automatizadas**.

---

### 6. GOBERNANZA, MANTENIMIENTO Y REENTRENAMIENTO

- **Frecuencia de Reentrenamiento:**
  Se establece un ciclo de reentrenamiento **mensual**, agregando los datos del mes vencido y manteniendo una ventana rodante de 12 meses históricos.
- **Métricas de Monitoreo en Tiempo Real:**
  - *Monitoreo de Data Drift:* Test Kolmogorov-Smirnov diario sobre variables continuas (`dias_retraso`, `ratio_flete_precio`).
  - *Monitoreo de Concept Drift:* Seguimiento semanal de la tasa de reseñas 1-2 estrellas entre los pedidos alertados en producción.
  - *Gatillo de Alerta Operativa:* Si la Precision@10% observada cae por debajo del 50% durante dos semanas consecutivas, se activa una revisión obligatoria y recalibración de $\tau$.
- **Responsables de Gobernanza:**
  - **Propietario del Modelo:** Oscar Orantes (AI Machine Learning Trainee).
  - **Interlocutor de Negocio:** Lead de Operaciones y Experiencia al Cliente de Olist.
