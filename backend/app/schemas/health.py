from pydantic import BaseModel
from typing import Dict

class ComponentStatus(BaseModel):
    status: str # "ok", "error"
    details: str = ""

class HealthResponse(BaseModel):
    """Respuesta para el endpoint de health check"""
    status: str # "healthy", "degraded", "unhealthy"
    version: str = "1.0.0"
    components: Dict[str, ComponentStatus]
