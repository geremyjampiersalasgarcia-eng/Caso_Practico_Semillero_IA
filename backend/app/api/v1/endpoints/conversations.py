from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ConversationListResponse, ConversationDetailResponse
from app.utils.logger import logger

router = APIRouter()

@router.get("/", response_model=List[ConversationListResponse])
def get_conversations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene la lista de conversaciones recientes."""
    repo = ConversationRepository(db)
    conversations = repo.get_all_conversations(skip=skip, limit=limit)
    return conversations

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Obtiene el detalle de una conversación con sus mensajes."""
    repo = ConversationRepository(db)
    conv = repo.get_conversation_with_messages(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Ordenar mensajes por ID
    messages_sorted = sorted(conv.messages, key=lambda m: m.id)
    conv.messages = messages_sorted
    return conv

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Elimina una conversación."""
    repo = ConversationRepository(db)
    success = repo.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}
