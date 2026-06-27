import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.exceptions import AppError, app_error_handler
from app.config import settings
from app.utils.logger import logger
from app.models.base import Base
from app.db.session import engine

# 1. Configurar FastAPI
app = FastAPI(
    title="Semillero IA - Mesa de Ayuda API",
    version="1.0.0",
    description="API RAG con Orquestador LangGraph para agentes especializados."
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
app.add_exception_handler(AppError, app_error_handler)

# 4. Incluir Rutas
app.include_router(api_router, prefix="/api/v1")

# 5. Eventos de inicio/apagado
@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando aplicación. Creando tablas en base de datos si no existen...")
    # Crear tablas usando SQLAlchemy (Alembic se usaría en producción)
    Base.metadata.create_all(bind=engine)
    logger.info("Aplicación iniciada correctamente")

if __name__ == "__main__":
    logger.info("Iniciando servidor Uvicorn...", host=settings.API_HOST, port=settings.API_PORT)
    uvicorn.run(
        "app.main:app", 
        host=settings.API_HOST, 
        port=settings.API_PORT, 
        reload=settings.API_DEBUG
    )
