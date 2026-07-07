from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SourceInfo(BaseModel):
    """Información sobre un documento fuente utilizado en la respuesta"""
    document_name: str
    content_snippet: str
    relevance_score: float = 0.0


class ChatRequest(BaseModel):
    """Payload de entrada para el endpoint de chat"""
    question: str = Field(..., description="Pregunta del usuario en lenguaje natural")
    conversation_id: Optional[str] = Field(None, description="ID de la conversación actual, si existe")
    image: Optional[str] = Field(None, description="Imagen en base64 para el agente multimodal")
    confirmation: Optional[bool] = Field(None, description="Confirmación para ejecutar una acción (registro)")


class ChatResponse(BaseModel):
    """Payload de salida estandarizado"""
    class MetaInfo(BaseModel):
        agents_used: List[str]
        latency_ms: float
        conversation_id: str

    answer: str
    meta: MetaInfo
    sources: List[SourceInfo] = []
    warnings: List[str] = Field(default=[], description="Advertencias si no se encontró información suficiente")


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    image_data: Optional[str] = None
    sources: List[dict] = []
    agents_used: List[str] = []
    created_at: datetime


class ConversationListResponse(BaseModel):
    id: str
    title: Optional[str]
    updated_at: datetime


class ConversationDetailResponse(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]
