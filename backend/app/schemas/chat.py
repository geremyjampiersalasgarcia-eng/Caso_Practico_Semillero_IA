from pydantic import BaseModel, Field
from typing import List, Optional

class SourceInfo(BaseModel):
    """Información sobre un documento fuente utilizado en la respuesta"""
    document_name: str
    content_snippet: str
    relevance_score: float = 0.0

class ChatRequest(BaseModel):
    """Payload de entrada para el endpoint de chat"""
    question: str = Field(..., description="Pregunta del usuario en lenguaje natural")
    conversation_id: Optional[str] = Field(None, description="ID de la conversación actual, si existe")
    
class ChatResponse(BaseModel):
    """Payload de salida estandarizado (ver DESIGN.md)"""
    class MetaInfo(BaseModel):
        agents_used: List[str]
        latency_ms: float
        conversation_id: str
        
    answer: str
    meta: MetaInfo
    sources: List[SourceInfo] = []
