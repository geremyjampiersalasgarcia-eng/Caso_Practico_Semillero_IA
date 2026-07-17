import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.exceptions import AppError, app_error_handler
from app.config import settings
from app.utils.logger import logger
from app.models.base import Base
from app.db.session import engine
from contextlib import asynccontextmanager
from app.agents import register_all_agents

# --- Importaciones opcionales de Observabilidad (tolerante a fallos) ---
_OBSERVABILITY_AVAILABLE = False
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from openinference.instrumentation.langchain import LangChainInstrumentor
    _OBSERVABILITY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Modulos de observabilidad no disponibles (OpenTelemetry/Phoenix): {e}. "
                   "El servidor arrancara sin trazas.")


# 5. Eventos de inicio/apagado
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación. Creando tablas en base de datos si no existen...")
    Base.metadata.create_all(bind=engine)  # type: ignore

    # --- Observabilidad: conectar a Phoenix externo (Docker) si está disponible ---
    if _OBSERVABILITY_AVAILABLE:
        try:
            import os
            os.environ["PHOENIX_PROJECT_NAME"] = "Patito_SA_Ventas"
            
            logger.info("Configurando OpenTelemetry para enviar trazas a Phoenix...")
            endpoint = "http://localhost:6006/v1/traces"
            project_name = "Patito_SA_Ventas"
            
            # Darle un nombre al proyecto en Phoenix
            resource = Resource(attributes={
                "project.name": project_name,
                "openinference.project.name": project_name,
                "service.name": project_name,
            })
            
            exporter = OTLPSpanExporter(
                endpoint=endpoint,
                headers={"project-name": project_name},
            )
            
            tracer_provider = TracerProvider(resource=resource)
            tracer_provider.add_span_processor(
                BatchSpanProcessor(exporter)
            )
            trace.set_tracer_provider(tracer_provider)

            try:
                LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
                logger.info("LangChainInstrumentor activado. Trazas -> Phoenix (localhost:6006)")
            except Exception as e:
                logger.warning(f"Instrumentacion ya activa o no disponible: {e}")
        except Exception as e:
            logger.warning(f"No se pudo conectar a Phoenix (¿docker-compose up -d phoenix?): {e}. "
                           "El servidor funcionara sin observabilidad.")
    else:
        logger.info("Observabilidad desactivada (dependencias no instaladas).")

    logger.info("Registrando agentes del sistema...")
    register_all_agents()
    logger.info("Aplicación iniciada correctamente")

    yield

    logger.info("Apagando aplicación...")

# 1. Configurar FastAPI
app = FastAPI(
    title="Semillero IA - Mesa de Ayuda API",
    version="1.0.0",
    description="API RAG con Orquestador LangGraph para agentes especializados.",
    lifespan=lifespan
)

# 2. Configurar CORS (Permitir frontend Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Frontend default URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Registrar Manejador de Errores Global
app.add_exception_handler(AppError, app_error_handler)  # type: ignore

# 4. Incluir Rutas
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    logger.info("Iniciando servidor Uvicorn...", host=settings.API_HOST, port=settings.API_PORT)
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )
