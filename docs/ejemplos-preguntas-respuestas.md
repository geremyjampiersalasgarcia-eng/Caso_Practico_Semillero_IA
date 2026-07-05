# Ejemplos de Preguntas y Respuestas — Mesa de Ayuda Ventas Patito S.A.

## 1. Consulta de Catálogo (agente_catalogo)

**Pregunta:** ¿Cuál es el precio de lista y la disponibilidad del producto Patito Pro 2026?

**Respuesta esperada:**
Según el **Catálogo de Productos y Lista de Precios** de Patito S.A.:
- **Producto:** Patito Pro 2026
- **Precio de lista:** USD 1,299
- **Disponibilidad:** EN STOCK
- **Características:** Equipo insignia, procesador de alto rendimiento, 16 GB RAM, 512 GB SSD
- Incluye garantía estándar de 12 meses
- Precios antes de impuestos y antes de descuentos comerciales

**Agente:** agente_catalogo  
**Fuente:** 01_Catalogo_Productos_Precios.txt

---

## 2. Consulta de Políticas (agente_politicas)

**Pregunta:** ¿Qué descuento máximo puedo ofrecer a un cliente nuevo sin aprobación del gerente?

**Respuesta esperada:**
Según las **Políticas Comerciales** de Patito S.A.:
- Un vendedor puede autorizar directamente hasta **10% de descuento** sin necesidad de aprobación adicional
- Descuentos mayores al 10% requieren aprobación del gerente comercial
- Ejemplo específico en la política: "A un cliente nuevo, el vendedor puede ofrecer hasta 10% sin pedir aprobación"

**Agente:** agente_politicas  
**Fuente:** 02_Politicas_Comerciales_Descuentos_Credito.txt

---

## 3. Consulta de Proceso de Venta (agente_proceso_ventas)

**Pregunta:** ¿Qué información debo registrar en el CRM antes de marcar una oportunidad como ganada?

**Respuesta esperada:**
Según el **Manual del Proceso de Ventas y CRM**:
- Orden de compra o contrato firmado por el cliente
- Datos de facturación completos del cliente
- Productos, cantidades y precios finales (con descuento aplicado y su autorización)
- Condición de pago (contado o crédito) y plazo acordado
- Monto total de la venta y fecha de cierre
- Fecha de entrega comprometida

**Agente:** agente_proceso_ventas  
**Fuente:** 03_Proceso_Ventas_CRM.txt

---

## 4. Consulta Mixta (3 agentes en paralelo)

**Pregunta:** Un cliente nuevo quiere comprar 50 unidades del Patito Pro 2026 a crédito y pide un descuento especial. ¿Cuál es el precio, qué descuento y condiciones de crédito puedo ofrecer, y qué debo registrar en el CRM?

**Respuesta esperada (consolidada):**

**Precio (Catálogo):**
- Patito Pro 2026: USD 1,299 por unidad. EN STOCK.

**Descuento y Crédito (Políticas):**
- Hasta 10% lo autoriza el vendedor. Más del 10% requiere gerente comercial.
- Clientes nuevos: primera compra suele ser de contado. El crédito se evalúa tras la primera operación.
- Si se aprueba crédito: plazos de 30, 60 o 90 días.

**Registro CRM (Proceso):**
- Registrar la oportunidad con todos los datos: cliente, productos, cantidades, precios, condición de pago, monto total.
- Para cerrar como "ganada": orden de compra firmada, datos de facturación, fecha de entrega.

**Agentes:** agente_catalogo, agente_politicas, agente_proceso_ventas  
**Fuentes:** Los 3 documentos TXT

---

## 5. Registro de Oportunidad (agente_accion)

**Pregunta:** Registra una oportunidad: cliente Comercial ABC, 10 unidades de Patito Pro 2026, 8% de descuento, pago de contado.

**Respuesta esperada:**
El agente analiza los datos, calcula:
- Precio con descuento: USD 1,299 × (1 - 0.08) = USD 1,195.08
- Monto total: 10 × USD 1,195.08 = USD 11,950.80
- Descuento 8% ≤ 10%: no requiere autorización adicional
- Contacto: Comercial ABC (si no se especifica otro)

Presenta resumen y pide confirmación. Al confirmar, genera registro con ID único en `registro_oportunidades.txt`.

**Agente:** agente_accion

---

## 6. Consulta fuera de alcance

**Pregunta:** ¿Cuál es la política de vacaciones de Patito S.A.?

**Respuesta esperada:**
"No encontré información suficiente en la base documental proporcionada."

(La base de conocimiento solo cubre: catálogo/precios, políticas comerciales y proceso de ventas/CRM)
