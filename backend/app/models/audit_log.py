import uuid
from sqlalchemy import String, Integer, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class AuditLog(Base):
    """
    Registro de auditoría inmutable para cada consulta procesada por el orquestador.
    Cumple con el requisito de Trazabilidad y Capacidad de Explicación.
    """
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # IMPORTANTE: Según SECURITY.md, NO registrar la pregunta real si contiene PII, 
    # pero para el caso práctico registraremos un hash o la pregunta anonimizada si es posible.
    # Por ahora, guardamos un resumen o la intención detectada.
    intent_category: Mapped[str] = mapped_column(String, nullable=True)
    
    agents_invoked: Mapped[dict] = mapped_column(JSON, default=list)
    sources_retrieved: Mapped[dict] = mapped_column(JSON, default=list)
    
    latency_ms: Mapped[float] = mapped_column(Float, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Opcional: ID de la conversación a la que pertenece
    conversation_id: Mapped[str] = mapped_column(String, nullable=True)

    # Observabilidad y Costos
    trace_id: Mapped[str] = mapped_column(String, nullable=True)
    tokens_input: Mapped[int] = mapped_column(Integer, nullable=True)
    tokens_output: Mapped[int] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=True)
