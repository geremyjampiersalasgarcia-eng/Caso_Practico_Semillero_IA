from fastapi import APIRouter
from app.api.v1.endpoints import chat, health, documents, conversations, metrics

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
