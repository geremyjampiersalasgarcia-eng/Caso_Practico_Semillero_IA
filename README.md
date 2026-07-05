# Patito S.A.
## Departamento de Ventas
### Proyecto final del semillero

**Grupo:** Net Ingenieros

> **Sistema de Inteligencia Artificial Avanzado** con agentes especializados para potenciar la mesa de ayuda del equipo comercial.

Este proyecto consiste en un sistema de Inteligencia Artificial diseñado para asistir al Departamento de Ventas de la empresa ficticia Patito S.A. Utiliza una arquitectura Multi-Agente basada en LangGraph y procesamiento RAG (Retrieval-Augmented Generation) con ChromaDB y Google Gemini, permitiendo a los vendedores consultar información precisa sobre el catálogo de productos, precios, políticas comerciales y registrar oportunidades en el CRM mediante lenguaje natural o análisis de imágenes.

---

## Tabla de contenido

* [Stack Tecnológico](#stack-tecnológico)
* [Arquitectura](#arquitectura)
* [Agentes del Sistema](#agentes-del-sistema)
* [Estructura del Proyecto](#estructura-del-proyecto)
* [Cómo empezar](#-cómo-empezar)
* [Ingesta de Documentos](#-ingesta-de-documentos)
* [Ejecutar el Proyecto](#-ejecutar-el-proyecto)
* [Ejemplos de Uso](#-ejemplos-de-uso)
* [Decisiones Técnicas](#decisiones-técnicas)
* [Riesgos y Mejoras Futuras](#riesgos-y-mejoras-futuras)

---

## Stack Tecnológico

### Backend
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF4F00?style=for-the-badge&logo=chroma&logoColor=white)](https://www.trychroma.com/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

### Frontend
[![Next.js](https://img.shields.io/badge/Next.js_14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

### Justificación de Tecnologías Clave

| Componente | Elección | Por qué |
| :--- | :--- | :--- |
| **Lenguaje** | Python 3.11 | Estándar para IA/NLP. Ecosistema robusto con LangChain y Google AI. |
| **Framework web** | FastAPI + Uvicorn | Tipado estricto, docs automáticas (Swagger), alto rendimiento asíncrono. |
| **Agentes** | LangChain | Framework estándar para agentes, tools y chains. Requerido por el semillero. |
| **Orquestación** | LangGraph (StateGraph) | Flujo de agentes como grafo explícito con enrutamiento condicional. |
| **Vector store** | ChromaDB (local) | Persistente, rápido, sin servicios externos. Una colección por agente. |
| **LLM & Embeddings** | Google Gemini (via `langchain-google-genai`) | `ChatGoogleGenerativeAI` para agentes, `GoogleGenerativeAIEmbeddings` para vectores. |
| **Visión** | Gemini Vision | Capacidad multimodal nativa para análisis de imágenes de productos. |
| **Base de datos** | PostgreSQL + Docker | Historial de conversaciones y auditoría robusta. |
| **Frontend** | Next.js + Tailwind + Shadcn UI | Interfaz de chat moderna y responsive. |

---

## Arquitectura

### Diagrama de alto nivel

```text
Browser ──► Web UI (Next.js)  │  TypeScript + Tailwind + Shadcn
                │
                ▼
         HTTP (POST /api/v1/chat)
                │
                ▼
┌───────────────────────────────────────────────────────────────┐
│  FastAPI  (app.main)                                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  LangGraph StateGraph (orchestrator.py)                 │  │
│  │                                                         │  │
│  │  START                                                  │  │
│  │   └► classify (Gemini, temp=0)                          │  │
│  │       ├► catalogo_precios   → Agente Catálogo      ──┐  │  │
│  │       ├► politicas_comerc   → Agente Políticas     ──┤  │  │
│  │       ├► proceso_ventas     → Agente Proc. Ventas  ──┤  │  │
│  │       ├► multimodal         → Agente Imagen        ──┤  │  │
│  │       ├► accion_registro    → Agente Acción        ──┤  │  │
│  │       └► mixta              → 3 agentes RAG        ──┤  │  │
│  │                                                      │  │  │
│  │                                    consolidate ◄─────┘  │  │
│  │                                        │                │  │
│  │                                       END               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ChromaDB (3 colecciones: col_catalogo, col_politicas,        │
│            col_proceso_ventas)                                │
│  PostgreSQL (historial + auditoría)                           │
└───────────────────────────────────────────────────────────────┘
```

### Diagrama de flujo (Mermaid)

```mermaid
graph TD
    User([Usuario]) -->|HTTP POST + pregunta| API["FastAPI /api/v1/chat"]

    subgraph Orquestador LangGraph
        API --> Classify["Clasificador de Intención"]
        Classify --> Router{Router}

        Router -->|catalogo_precios| AgCat["Agente Catálogo y Precios"]
        Router -->|politicas_comerciales| AgPol["Agente Políticas Comerciales"]
        Router -->|proceso_ventas| AgProc["Agente Proceso de Venta y CRM"]
        Router -->|multimodal| AgImg["Agente Multimodal de Imagen"]
        Router -->|accion_registro| AgAcc["Agente de Acción - Registro"]
        Router -->|mixta| AgCat & AgPol & AgProc

        AgCat --> Consolidate["Consolidador"]
        AgPol --> Consolidate
        AgProc --> Consolidate
        AgImg --> Consolidate
        AgAcc --> Consolidate
    end

    subgraph Capa RAG
        AgCat --> VDB1[(col_catalogo)]
        AgPol --> VDB2[(col_politicas)]
        AgProc --> VDB3[(col_proceso_ventas)]
        AgImg --> VDB1
        VDB1 --> Doc1["01_Catalogo.txt"]
        VDB2 --> Doc2["02_Politicas.txt"]
        VDB3 --> Doc3["03_Proceso.txt"]
    end

    Consolidate --> API
    API -->|JSON Response| User
    API --> DB[(PostgreSQL)]
```

### Flujo de Inferencia Paso a Paso

1. El usuario realiza una pregunta (opcionalmente adjunta imagen).
2. El **orquestador** recibe la pregunta.
3. El **clasificador** (Gemini con temp=0) determina la intención:
   - `catalogo_precios`, `politicas_comerciales`, `proceso_ventas`, `multimodal`, `accion_registro` o `mixta`.
4. Si hay imagen adjunta → se redirige automáticamente al **agente multimodal**.
5. Si se detecta solicitud de registro → se redirige al **agente de acción**.
6. Se invoca uno o más **agentes especializados** (LangChain).
7. Cada agente consulta su **base de conocimiento embebida** (retriever sobre ChromaDB).
8. Cada agente genera una respuesta parcial con fuentes citadas.
9. El **consolidador** integra las respuestas en una sola coherente.
10. El sistema retorna: **respuesta final**, **agentes participantes**, **fuentes utilizadas** y **advertencias** (si aplica).

---

## Agentes del Sistema

### 1. Agente de Catálogo y Precios (`agente_catalogo`)
- **Función:** Productos, especificaciones, precios de lista, disponibilidad.
- **Base de conocimiento:** `01_Catalogo_Productos_Precios.txt` → `col_catalogo`
- **Ejemplo:** *"¿Cuál es el precio de lista y la disponibilidad del producto Patito Pro 2026?"*

### 2. Agente de Políticas Comerciales (`agente_politicas`)
- **Función:** Descuentos, niveles de autorización, crédito, garantías, devoluciones.
- **Base de conocimiento:** `02_Politicas_Comerciales_Descuentos_Credito.txt` → `col_politicas`
- **Ejemplo:** *"¿Qué descuento máximo puedo ofrecer a un cliente nuevo sin aprobación del gerente?"*

### 3. Agente de Proceso de Venta y CRM (`agente_proceso_ventas`)
- **Función:** Etapas del embudo, registro en CRM, requisitos para cerrar ventas.
- **Base de conocimiento:** `03_Proceso_Ventas_CRM.txt` → `col_proceso_ventas`
- **Ejemplo:** *"¿Qué información debo registrar en el CRM antes de marcar una oportunidad como ganada?"*

### 4. Agente Multimodal de Imagen (`agente_multimodal`)
- **Función:** Analiza imágenes de productos con Gemini Vision y cruza con el catálogo.
- **Base de conocimiento:** Cruza con `col_catalogo`
- **Ejemplo:** *"Adjunto la foto de un producto: ¿cuál es, cuál es su precio de lista y está disponible?"*

### 5. Agente de Acción — Registro (`agente_accion`)
- **Función:** Registra oportunidades/cotizaciones en `registro_oportunidades.txt`.
- **Validación:** Cliente, contacto, producto, cantidad, precio con descuento, condición de pago, monto total.
- **Control:** Si falta algún dato → lo solicita. Si descuento > 10% → advierte autorización. Pide confirmación antes de escribir.
- **Ejemplo:** *"Registra una oportunidad: cliente Comercial ABC, 10 unidades de Patito Pro 2026, 8% de descuento, pago de contado."*

---

## Estructura del Proyecto

```text
Caso_Practico_Semillero_IA/
├── backend/                              # Backend Python / FastAPI
│   ├── app/
│   │   ├── agents/                       # Agentes especializados
│   │   │   ├── base_agent.py             # Clase base (RAG + LLM)
│   │   │   ├── catalogo_agent.py         # Agente de Catálogo y Precios
│   │   │   ├── politicas_agent.py        # Agente de Políticas Comerciales
│   │   │   ├── proceso_ventas_agent.py   # Agente de Proceso de Venta y CRM
│   │   │   ├── multimodal_agent.py       # Agente Multimodal de Imagen
│   │   │   ├── accion_agent.py           # Agente de Acción (Registro)
│   │   │   ├── registry.py              # Patrón Registry
│   │   │   └── __init__.py              # Registro de todos los agentes
│   │   ├── core/                         # Motor de IA
│   │   │   ├── orchestrator.py           # LangGraph StateGraph (orquestador)
│   │   │   ├── classifier.py            # Clasificador de intención (Gemini)
│   │   │   └── llm.py                   # Cliente Gemini (LLM + Embeddings)
│   │   ├── prompts/                      # System prompts (Markdown)
│   │   │   ├── catalogo_prompt.md
│   │   │   ├── politicas_prompt.md
│   │   │   ├── proceso_ventas_prompt.md
│   │   │   ├── multimodal_prompt.md
│   │   │   ├── accion_prompt.md
│   │   │   ├── classifier_prompt.md
│   │   │   └── orchestrator_prompt.md
│   │   ├── rag/                          # Pipeline RAG
│   │   │   ├── loader.py                # Carga TXT/PDF
│   │   │   ├── splitter.py              # Chunking (RecursiveCharacterTextSplitter)
│   │   │   ├── embeddings.py            # GoogleGenerativeAIEmbeddings
│   │   │   ├── retriever.py             # Búsqueda semántica en ChromaDB
│   │   │   └── vectorstore.py           # Gestión de colecciones ChromaDB
│   │   ├── api/v1/                       # Endpoints REST
│   │   ├── services/                     # Lógica de negocio (ChatService)
│   │   ├── models/                       # ORM (Conversaciones, Auditoría)
│   │   ├── schemas/                      # DTOs Pydantic v2
│   │   └── utils/                        # Logging (structlog)
│   ├── data/
│   │   ├── raw/                          # Documentos base de conocimiento
│   │   │   ├── 01_Catalogo_Productos_Precios.txt
│   │   │   ├── 02_Politicas_Comerciales_Descuentos_Credito.txt
│   │   │   └── 03_Proceso_Ventas_CRM.txt
│   │   ├── chroma_db/                    # Persistencia ChromaDB
│   │   └── registro_oportunidades.txt    # Archivo de registro del agente de acción
│   ├── scripts/
│   │   └── ingest.py                    # Script de ingesta por colección
│   ├── tests/                            # Pruebas
│   ├── .env.example                      # Template de variables de entorno
│   └── requirements.txt                  # Dependencias Python
├── frontend/                             # Interfaz Next.js + TypeScript
│   ├── app/                              # Páginas principales y Layouts (App Router)
│   ├── components/                       # Componentes React (UI, ChatInput, etc.)
│   ├── hooks/                            # Custom hooks (e.g., useChat.ts)
│   ├── lib/                              # Lógica de API (conexión con FastAPI)
│   ├── types/                            # Definiciones de interfaces TypeScript
│   ├── tailwind.config.ts                # Configuración de estilos CSS
│   └── package.json                      # Dependencias de Node.js
├── 4_Ventas/                             # Documentos originales entregados
├── docs/                                 # Documentación técnica
├── docker-compose.yml                    # PostgreSQL con Docker
├── AGENTS.md                             # Definición de agentes
└── README.md                             # Este archivo
```

---

## 🚀 Cómo empezar

### 1. Clonar el repositorio

```bash
git clone https://github.com/geremyjampiersalasgarcia-eng/Caso_Practico_Semillero_IA.git
cd Caso_Practico_Semillero_IA
```

### 2. Configurar Variables de Entorno (IMPORTANTE)

**La GOOGLE_API_KEY es obligatoria** para que funcionen los agentes, embeddings y el clasificador.

```bash
cd backend
cp .env.example .env
# En Windows: copy .env.example .env
```

Abre el archivo `.env` y pega tu clave de Google Gemini:

```env
GOOGLE_API_KEY=tu_api_key_aqui
```

> 💡 **Obtén tu API Key gratuita en:** [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

El archivo `.env` está excluido en `.gitignore` — no hay riesgo de subir tu clave a GitHub.

### 3. Instalar dependencias de Python

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate       # Windows
# source venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
```

---

## 📥 Ingesta de Documentos

**Este paso es obligatorio antes de usar el sistema.** Genera los embeddings e índices vectoriales por agente.

```bash
cd backend
python scripts/ingest.py
```

**Flujo de ingesta:**

1. `loader.py` lee los 3 archivos TXT de `data/raw/`
2. `splitter.py` los divide en chunks de ~1000 caracteres con 200 de overlap (RecursiveCharacterTextSplitter)
3. `embeddings.py` genera vectores con `GoogleGenerativeAIEmbeddings` (modelo `models/gemini-embedding-2`)
4. `vectorstore.py` almacena cada documento en **su propia colección** ChromaDB:

| Documento | Colección ChromaDB |
|:---|:---|
| `01_Catalogo_Productos_Precios.txt` | `col_catalogo` |
| `02_Politicas_Comerciales_Descuentos_Credito.txt` | `col_politicas` |
| `03_Proceso_Ventas_CRM.txt` | `col_proceso_ventas` |

> **Nota:** Para re-indexar, simplemente ejecuta `python scripts/ingest.py` de nuevo. El script limpia las colecciones antes de re-indexar.

---

## 🐳 Ejecutar el Proyecto

### Paso 1: Levantar la Base de Datos (con Docker)

> [!NOTE]
> Asegúrate de tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo.

```bash
# Desde la raíz del proyecto
docker-compose up -d postgres
```

### Paso 2: Levantar el Backend

```bash
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Paso 3: Levantar el Frontend

```bash
cd frontend
npm install
npm run dev
```

### Servicios Activos

| Servicio | URL | Descripción |
| :--- | :--- | :--- |
| Backend API | http://localhost:8000/docs | Swagger UI interactivo |
| Frontend UI | http://localhost:3000 | Interfaz de chat |
| PostgreSQL | `localhost:5432` | Base de datos (vía Docker) |

---

## Endpoints de la API

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/chat` | Envía pregunta al orquestador. Acepta `question`, `image` (base64), `confirmation` (bool). |
| `GET` | `/api/v1/conversations` | Lista historial de conversaciones. |
| `GET` | `/api/v1/conversations/{id}` | Detalle de una conversación. |
| `DELETE` | `/api/v1/conversations/{id}` | Elimina una conversación. |
| `GET` | `/api/v1/health` | Estado del servicio. |
| `GET` | `/api/v1/documents` | Lista documentos indexados. |

### Ejemplo de request `POST /api/v1/chat`

```json
{
  "question": "¿Cuál es el precio del Patito Pro 2026?",
  "conversation_id": null,
  "image": null,
  "confirmation": null
}
```

### Ejemplo con imagen (agente multimodal):

```json
{
  "question": "¿Qué producto es este y cuánto cuesta?",
  "image": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

### Ejemplo con registro (agente de acción):

```json
{
  "question": "Registra una oportunidad: cliente Comercial ABC, 10 unidades Patito Pro 2026, 8% descuento, contado",
  "confirmation": true
}
```

---

## 💬 Ejemplos de Uso

### Consulta de Catálogo
**Pregunta:** *¿Cuál es el precio de lista y la disponibilidad del producto Patito Pro 2026?*

**Respuesta esperada:** El Patito Pro 2026 tiene un precio de lista de **USD 1,299**, está **EN STOCK** y cuenta con procesador de alto rendimiento, 16 GB RAM, 512 GB SSD. Incluye garantía estándar de 12 meses. (Fuente: Catálogo de Productos y Lista de Precios).

---

### Consulta de Políticas
**Pregunta:** *¿Qué descuento máximo puedo ofrecer a un cliente nuevo sin aprobación del gerente?*

**Respuesta esperada:** Hasta **10%** de descuento. El vendedor puede autorizarlo directamente sin aprobación adicional. (Fuente: Políticas Comerciales).

---

### Consulta de Proceso de Venta
**Pregunta:** *¿Qué información debo registrar en el CRM antes de marcar una oportunidad como ganada?*

**Respuesta esperada:** Orden de compra/contrato firmado, datos de facturación, productos/cantidades/precios finales, condición de pago, monto total, fecha de cierre y fecha de entrega comprometida. (Fuente: Manual del Proceso de Ventas y CRM).

---

### Consulta Mixta
**Pregunta:** *Un cliente nuevo quiere comprar 50 unidades del Patito Pro 2026 a crédito y pide un descuento especial. ¿Cuál es el precio, qué descuento y condiciones de crédito puedo ofrecer, y qué debo registrar en el CRM?*

**Agentes participantes:** Catálogo + Políticas + Proceso Ventas (mixta)

**Respuesta esperada:** Integra precio del Patito Pro 2026 (USD 1,299), que el descuento hasta 10% lo autoriza el vendedor (más requiere gerente), que clientes nuevos normalmente pagan de contado la primera compra (crédito requiere análisis), y los datos que deben registrarse en el CRM antes del cierre.

---

### Registro de Oportunidad
**Pregunta:** *Registra una oportunidad: cliente Comercial ABC, 10 unidades de Patito Pro 2026, 8% de descuento, pago de contado.*

**Agente:** Acción

**Respuesta esperada:** Presenta resumen con datos calculados (precio con descuento: USD 1,195.08, monto total: USD 11,950.80), pide confirmación, y al confirmar genera registro con ID único (OPP-20260705-A3F2B1) en `registro_oportunidades.txt`.

---

## Decisiones Técnicas

### Estrategia de Chunking
- **Tamaño:** 1000 caracteres con 200 de overlap
- **Splitter:** `RecursiveCharacterTextSplitter` con separadores `["\n\n", "\n", ".", " "]`
- **Justificación:** Los documentos son cortos (~1000-1500 bytes cada uno), por lo que chunks de 1000 chars capturan secciones completas. El overlap de 200 asegura contexto entre chunks.

### Modelo de Embeddings
- **Modelo:** `models/gemini-embedding-2` (Google)
- **Justificación:** Requerido por el semillero. Alta calidad para texto en español.

### Modelo LLM
- **Modelo:** Configurable vía `LLM_MODEL_NAME` en `.env` (default: `gemini-1.5-flash`)
- **Temperatura:** 0.1 para agentes (baja alucinación), 0.0 para clasificador (determinismo)
- **Justificación:** Flash es rápido y económico para prototipo. Soporta visión multimodal.

### Retrieval (top-k)
- **top-k:** 4 fragmentos por consulta
- **Justificación:** Con documentos pequeños, 4 chunks cubren la mayoría del contenido relevante sin exceder el contexto.

### Vector Store
- **ChromaDB local** con persistencia en `data/chroma_db/`
- **Una colección por agente:** Aislamiento de bases de conocimiento
- **Justificación:** Simple, sin servicios externos, ideal para prototipo.

### Patrón de Agentes
- **Registry Pattern:** Permite agregar nuevos agentes sin modificar el orquestador
- **BaseAgent (ABC):** Clase base con flujo RAG estándar (retrieve → prompt → LLM → result)
- **Agentes especializados** heredan y solo definen: nombre, descripción, colección, prompt



---

## Riesgos y Mejoras Futuras

### Riesgos identificados

| Riesgo | Impacto | Mitigación actual |
|:---|:---|:---|
| Alucinación del LLM | Respuestas inventadas | Prompt estricto + temp baja + validación "no encontré información" |
| API Key expuesta | Seguridad | `.env` + `.gitignore` + `.env.example` sin credenciales |
| Documentos pequeños | Chunks redundantes | Ajuste de chunk_size. Monitorear calidad de retrieval |
| Costos de API Gemini | Consumo de tokens | Modelo Flash (económico), cacheo futuro |
| Concurrencia | Escritura simultánea en registro_oportunidades.txt | File lock o migrar a BD en producción |
| Latencia en consultas mixtas | 3 agentes + LLM consolidador | Ejecución paralela en LangGraph |

### Mejoras futuras

1. **Memoria conversacional:** Mantener contexto de la conversación entre turnos
2. **Streaming:** Respuestas parciales en tiempo real (SSE)
3. **Autenticación:** JWT/OAuth para controlar acceso por rol
4. **Permisos por agente:** Control de qué usuarios pueden acceder a qué agentes
5. **Monitoreo de calidad:** Dashboard con métricas de tokens, latencia, feedback
6. **Evaluación RAG:** Métricas de relevancia (RAGAS, faithfulness, answer relevancy)
7. **Cacheo de embeddings:** Evitar re-calcular embeddings para preguntas repetidas
8. **File lock para registros:** Evitar corrupción en escritura concurrente
9. **Historial de precios:** Versionar el catálogo por fechas
10. **Tests automatizados:** Aumentar cobertura con preguntas de golden set

---

## Licencia

Proyecto académico — Semillero de Inteligencia Artificial.

---

<div align="center">
  <h3> Desarrollado por el equipo Net Ingenieros </h3>
  
  <p>
    <img src="https://img.icons8.com/fluency/48/user-male-circle.png" width="22" height="22" style="vertical-align: middle; margin-right: 5px;" /> <b>Frank Marcelo Villalta Díaz</b> <br>
    <img src="https://img.icons8.com/fluency/48/user-male-circle.png" width="22" height="22" style="vertical-align: middle; margin-right: 5px;" /> <b>Eddy Fernando Romo Quinde</b> <br>
    <img src="https://img.icons8.com/fluency/48/user-male-circle.png" width="22" height="22" style="vertical-align: middle; margin-right: 5px;" /> <b>Geremy Jampier Salas Garcia</b>
  </p>
  
  <br>
  <sub><i>Desarrollado con LangChain, LangGraph y Google Gemini</i></sub>
</div>