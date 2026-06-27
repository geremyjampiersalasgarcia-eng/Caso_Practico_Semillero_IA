from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.utils.logger import logger

# pool_pre_ping asegura que la conexión no esté rota antes de usarla
engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True,
    # Habilitar echo=True en debug para ver las consultas SQL generadas
    echo=False 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Generador de dependencia para inyectar la sesión de BD en FastAPI.
    Asegura que la conexión se cierre correctamente después de usarla.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Error en la sesión de base de datos", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()
