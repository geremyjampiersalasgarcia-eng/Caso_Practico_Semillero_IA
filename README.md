# Caso Práctico Semillero IA

---

## Tabla de contenido

* [Stack Tecnológico](#stack-tecnológico)
* [Arquitectura](#arquitectura)
* [Estructura del Proyecto](#estructura-del-proyecto)
* [Cómo empezar (Configuración Inicial)](#cómo-empezar-configuración-inicial)
* [Endpoints de la API](#endpoints-de-la-api)
* [Decisiones Técnicas](#decisiones-técnicas)

---

## Stack Tecnológico

### Backend (Mesa de Ayuda IA & RAG)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF4F00?style=for-the-badge&logo=chroma&logoColor=white)](https://www.trychroma.com/)
[![Gemini](https://img.shields.io/badge/Gemini_1.5-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy_2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)

### Frontend (Interfaz de Chat Premium)
[![Next.js](https://img.shields.io/badge/Next.js_14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Shadcn UI](https://img.shields.io/badge/Shadcn_UI-000000?style=for-the-badge&logo=shadcnui&logoColor=white)](https://ui.shadcn.com/)

### Justificación de Tecnologías Clave

| Componente | Elección | Por qué |
| :--- | :--- | :--- |
| **Lenguaje** | Python 3.11 | Estándar empresarial para IA / RAG. Ecosistema robusto de NLP. |
| **Web framework** | FastAPI + uvicorn | Tipado estricto, documentación automática (Swagger), alto rendimiento asíncrono. |
| **Orquestación** | LangGraph 0.4 | Permite modelar el flujo de agentes como un grafo explícito (State Graph), ideal para enrutamiento condicional y flujos cíclicos. |
| **Vector store** | ChromaDB (local) | Persistente, rápido de configurar y no requiere servicios externos para el prototipo. |
| **Base de Datos** | PostgreSQL + SQLAlchemy | Almacenamiento robusto y estructurado para historial de conversaciones y auditoría. |
| **LLM & Embeddings** | Google Gemini 1.5 Flash / embeddings-004 | Alta velocidad de inferencia, excelente ventana de contexto, ideal para agentes. |
| **Frontend UI** | Next.js + Tailwind + Shadcn UI | Desarrollo ágil con componentes pre-estilizados de alta calidad y SSR/CSR híbrido. |

---

## Arquitectura

El sistema sigue una arquitectura de microservicios separando el frontend del backend, con un flujo interno orquestado por LangGraph.

```mermaid
graph TD
    User([Usuario]) -->|Pregunta (HTTP POST)| API["FastAPI / Chat Endpoint"]
    
    subgraph Orquestador LangGraph
        API --> Classify["Clasificador de Intención"]
        Classify -->|Condicional| Router{Router}
        
        Router -->|Tema A| AgentA["Agente A"]
        Router -->|Tema B| AgentB["Agente B"]
        Router -->|Múltiple| AgentC["Agente C"]
        
        AgentA --> Consolidate["Consolidador de Respuesta"]
        AgentB --> Consolidate
        AgentC --> Consolidate
    end
    
    subgraph Capa RAG
        AgentA <-->|Retriever| VectorDB[(ChromaDB)]
        AgentB <-->|Retriever| VectorDB
        AgentC <-->|Retriever| VectorDB
        VectorDB -.-> Docs["Documentos Locales"]
    end
    
    Consolidate -->|Respuesta + Fuentes| API
    API -->|JSON Response| User
    
    API -.-> DB[(PostgreSQL)]
    DB -.->|Auditoría / Historial| DB
```

### Flujo de Inferencia Paso a Paso

A continuación se presenta el flujo detallado de inferencia y procesamiento secuencial de una consulta dentro del sistema de mesa de ayuda técnica:

![Proceso de Inferencia: Mesa de Ayuda IA](docs/images/pipeline_infographic.png)

---

## Estructura del Proyecto

```text
Caso_Practico_Semillero_IA/
├── backend/                        # Núcleo de servicios, RAG y agentes IA (Python/FastAPI)
│   ├── alembic/                    # Gestión de migraciones de base de datos
│   ├── app/                        # Aplicación principal
│   │   ├── agents/                 # Agentes especializados y clase base
│   │   ├── api/v1/endpoints/       # Rutas REST: Chat, Documents, Health
│   │   ├── core/                   # Orquestador LangGraph, cliente LLM y excepciones
│   │   ├── db/                     # Sesión de base de datos relacional
│   │   ├── models/                 # Modelos ORM (Conversaciones, Mensajes, Auditoría)
│   │   ├── prompts/                # System prompts para cada agente y clasificador
│   │   ├── rag/                    # Pipeline RAG: Loader, Splitter, Embeddings, Retriever, Vectorstore
│   │   ├── repositories/           # Capa de acceso a datos para PostgreSQL
│   │   ├── schemas/                # DTOs de Pydantic v2 (ChatRequest, AgentResult)
│   │   ├── services/               # Lógica de negocio (ChatService)
│   │   └── utils/                  # Logging estructurado (structlog) y métricas
│   ├── data/                       # Almacenamiento de documentos crudos y persistencia ChromaDB
│   ├── scripts/                    # Scripts de indexación de documentos y pruebas
│   └── tests/                      # Pruebas unitarias, de integración y end-to-end
├── frontend/                       # Interfaz de chat (Next.js 14 + TypeScript)
│   ├── app/                        # App Router y estilos globales
│   ├── components/chat/            # Componentes del chat (ChatWindow, MessageBubble, InputBox)
│   ├── hooks/                      # Hooks para gestión de estado del chat
│   ├── lib/                        # Clientes de API y utilidades
│   ├── tests/                      # Pruebas de interfaz
│   └── types/                      # Interfaces TypeScript reflejando los schemas del backend
├── docs/                           # Documentación técnica, ADRs, riesgos y guías
├── docker-compose.yml              # Orquestación de infraestructura local
├── *.md                            # Documentos de control (AGENTS.md, STATUS.md, WORKFLOW.md, etc.)
└── README.md                       # Documentación maestra del sistema
```

---

## 🚀 Cómo empezar (Configuración Inicial)

### 1. Clonar el repositorio
```bash
git clone https://github.com/geremyjampiersalasgarcia-eng/Caso_Practico_Semillero_IA.git
cd Caso_Practico_Semillero_IA
```

### 2. Configurar Variables de Entorno (IMPORTANTE)

El proyecto utiliza variables de entorno para manejar credenciales de forma segura. NUNCA debes subir tus API keys al repositorio.

**Para el Backend:**
1. Navega a la carpeta del backend:
   ```bash
   cd backend
   ```
2. Copia el archivo de ejemplo para crear tu propio archivo `.env` local:
   ```bash
   cp .env.example .env
   ```
   *(En Windows puedes usar `copy .env.example .env`)*
3. Abre el nuevo archivo `.env` en tu editor de código y agrega tu clave de Gemini (y cualquier otra credencial que necesites en el futuro):
   ```env
   GOOGLE_API_KEY=tu_api_key_aqui
   ```

**Para el Frontend:**
1. Navega a la carpeta del frontend:
   ```bash
   cd ../frontend
   ```
2. Crea tu archivo `.env.local`:
   ```bash
   cp .env.example .env.local
   ```

El archivo `.env` ya está excluido en el `.gitignore`, así que no hay riesgo de subirlo accidentalmente.

---

## Endpoints de la API

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/chat` | Envía un mensaje al orquestador de agentes y devuelve la respuesta consolidada con fuentes. |
| `GET` | `/api/v1/health` | Verifica el estado del servicio y conexión a BD/ChromaDB. |
| `GET` | `/api/v1/documents` | Lista los documentos indexados en el sistema RAG. |

---

## Decisiones Técnicas

* **Arquitectura Clean/Hexagonal**: Se han separado las capas de presentación (`api`), negocio (`services`/`core`/`agents`), y acceso a datos (`rag`/`repositories`).
* **Patrón de Registro de Agentes (Registry)**: Permite inyectar nuevos agentes especializados sin modificar el código base del orquestador.
* **Trazabilidad Pura**: Cada respuesta incluye un bloque de `sources` que detalla qué agente intervino, qué documento consultó y qué sección exacta extrajo, mitigando alucinaciones.