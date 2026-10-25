# CHECKLIST ÉTICO Y DE INTELIGENCIA ARTIFICIAL RESPONSABLE
## Proyecto de Machine Learning para Olist E-Commerce Brasil

**Autor:** Oscar Orantes  
**Programa:** KODIGO Academy - AI Machine Learning Trainee  
**Módulo:** Entrega Final (Semana 12)  
**Fecha de Auditoría:** Octubre 2026

---

### RESUMEN EJECUTIVO DE EVALUACIÓN ÉTICA

El desarrollo de este sistema predictivo se rigió bajo los principios internacionales de **Inteligencia Artificial Confiable y Responsable (Responsible AI)**, garantizando que el modelo actúe como una herramienta de apoyo que promueva la satisfacción del cliente sin introducir sesgos discriminatorios, vulneraciones de privacidad ni incentivos perversos para los participantes del marketplace.

---

### 1. EVALUACIÓN DETALLADA POR PRINCIPIO

| Principio | Estado | Criterio de Verificación y Mitigación Aplicada |
| :--- | :---: | :--- |
| **Transparencia y Explicabilidad** | ✅ **Cumplido** | El modelo clasificador final (Random Forest / XGBoost) cuenta con explicabilidad de pesos y factores de riesgo basados en variables operativas interpretables (`dias_retraso`, `ratio_flete_precio`, `dias_despacho`). La Ficha Técnica (`ficha_modelo.md`) documenta públicamente sus capacidades, métricas y límites. |
| **Prevención de Fugas de Información (Zero Leakage)** | ✅ **Cumplido** | Se auditó rigurosamente la ausencia total de variables contaminantes. Las columnas de texto de reseñas, fechas de emisión de comentarios y longitudes de mensaje fueron excluidas del pipeline de entrenamiento. Solo se usan datos conocidos hasta la entrega física al cliente. |
| **Equidad Geográfica y No Discriminación** | ✅ **Cumplido** | Se auditó el desempeño por estado federativo (UF). Para evitar discriminar a clientes en regiones con infraestructura logística más remota (Norte/Nordeste como AM, PA, AC), la métrica central de retraso se calcula contra la fecha prometida de entrega y no contra el tiempo absoluto de viaje. |
| **Mitigación de Variables Proxy** | ✅ **Cumplido** | No se incluyen identificadores individuales de ingresos, etnia ni códigos postales a nivel de manzana (evitando *redlining* digital). La información geográfica se mantiene al nivel de macroestado (UF) únicamente con fines de normalización logística. |
| **Supervisión Humana (Human-in-the-Loop)** | ✅ **Cumplido** | El sistema no toma decisiones sancionatorias autónomas. Un puntaje de alto riesgo alerta al equipo de soporte humano para contacto proactivo y validación. Ningún vendedor es penalizado ni ningún comprador bloqueado automáticamente por este modelo. |
| **Gestión de Costos de Error y Calibración de Probabilidades** | ✅ **Cumplido** | Se calibró el umbral operativo al decil superior ($\tau = 0.2652$). La calibración de probabilidades asegura consistencia con el riesgo real. Un Falso Positivo implica enviar un mensaje de seguimiento o un cupón preventivo a un cliente satisfecho (impacto benigno/favorable). Un Falso Negativo omite la retención de un cliente insatisfecho. |
| **Privacidad y Protección de Datos (LGPD / GDPR)** | ✅ **Cumplido** | Todos los identificadores personales directos (nombres completos, CPF, direcciones de correo, teléfonos y números de tarjeta) fueron anonimizados con hashes o excluidos de los conjuntos de entrenamiento y APIs públicas. |

---

### 2. AUDITORÍA FORENSE DE VARIABLES Y RIESGOS

#### A. Auditoría de Variables de Entrada (17 Columnas Raw)
1. `order_id`, `customer_id`: Identificadores únicos anonimizados.
2. `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`: Marcas de tiempo del ciclo de vida físico del pedido. Permiten cuantificar demoras operacionales reales.
3. `num_items`, `num_vendedores`: Métricas de complejidad operativa.
4. `precio_total`, `flete_total`, `peso_total_g`, `volumen_total_cm3`: Atributos comerciales y físicos del paquete.
5. `tipo_pago_principal`, `total_pagos`: Dinámica financiera del pago (crédito, boleto, cuotas).
6. `customer_state`: Código de dos letras de la federación brasileña.

#### B. Variables Estrictamente Excluidas para Cumplimiento Ético y Legal
- ❌ `review_comment_message`: Excluido por riesgo de filtración de sesgo léxico retrospectivo y protección de privacidad.
- ❌ `review_comment_title`: Excluido para evitar fugas de información.
- ❌ `review_creation_date` / `review_answer_timestamp`: Excluidos porque ocurren cronológicamente después del evento a predecir.
- ❌ Información bancaria o números de cuenta: Excluidos en origen por diseño de seguridad.

---

### 3. PROTOCOLO DE INTERVENCIÓN ÉTICA EN PRODUCCIÓN

1. **Protocolo de Contacto Proactivo:**
   Cuando la API o el pipeline clasifica un pedido como `es_alto_riesgo = True`:
   - El mensaje enviado al cliente debe tener un tono empático y de servicio ("Queremos asegurarnos de que tu pedido haya llegado en perfectas condiciones").
   - Bajo ninguna circunstancia se debe mencionar al usuario que fue clasificado por un "algoritmo de riesgo".
2. **Salvaguarda de los Vendedores:**
   - Si un pedido tiene alto riesgo debido a demoras de la transportista externa (Correios), el sistema no debe imputar una mala calificación al puntaje de reputación del vendedor.
3. **Mecanismo de Exclusión y Desconexión de Emergencia (Kill Switch):**
   - Si se detecta un fallo en la API o una tasa anormal de falsas alarmas durante un evento extraordinario (huelgas, desastres naturales), el equipo de operaciones puede activar un switch para pausar los mensajes automáticos y reanudar el flujo manual.

---

### 4. CONCLUSIÓN DE LA AUDITORÍA

El sistema cumple con el 100% de los estándares de IA Ética y Responsable requeridos por KODIGO Academy y la industria de comercio electrónico global. No se identificaron riesgos críticos ni vulneraciones regulatorias.
