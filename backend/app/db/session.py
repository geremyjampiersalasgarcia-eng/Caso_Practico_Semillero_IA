from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.utils.logger import logger

_engine = None
_SessionLocal = None

def _get_engine():
    global _engine
    if _engine is not None:
        return _engine
    
    # Intentar PostgreSQL primero
    try:
        _engine = create_engine(
            settings.DATABASE_URL, 
            pool_pre_ping=True,
            echo=False
        )
        # Probar la conexión
        with _engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        logger.info("Conexión a PostgreSQL exitosa", url=settings.DATABASE_URL.split("@")[-1])
        return _engine
    except Exception as e:
        logger.warning(f"No se pudo conectar a PostgreSQL: {e}. Usando SQLite como fallback.")
        _engine = create_engine("sqlite:///data/mesa_ayuda_fallback.db", echo=False)
        return _engine

def _get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _SessionLocal

# Propiedad para acceso compatible con código existente (ej: Base.metadata.create_all(bind=engine))
engine = property(lambda self: _get_engine())

# Hack: hacer que 'engine' funcione como variable de módulo
class _EngineProxy:
    """Proxy que delega al engine real cuando se accede."""
    def __getattr__(self, name):
        return getattr(_get_engine(), name)
    def __repr__(self):
        return repr(_get_engine())

engine = _EngineProxy()

def get_db():
    """
    Generador de dependencia para inyectar la sesión de BD en FastAPI.
    Asegura que la conexión se cierre correctamente después de usarla.
    """
    SessionLocal = _get_session_local()
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Error en la sesión de base de datos", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()

