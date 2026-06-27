import structlog
import logging
import sys
from app.config import settings

def setup_logger():
    """Configura structlog para toda la aplicación"""
    
    # Nivel de log desde config
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configuración base de logging estándar
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Configuración de structlog
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() # JSON para ingesta estructurada
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()

# Instancia global del logger
logger = setup_logger()
