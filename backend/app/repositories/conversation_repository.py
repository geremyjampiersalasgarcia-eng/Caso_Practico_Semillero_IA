from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.conversation import Conversation
from app.models.message import Message

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_conversation(self, conversation_id: Optional[str] = None) -> Conversation:
        if conversation_id:
            conv = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conv:
                return conv
                
        # Crear nueva
        new_conv = Conversation()
        self.db.add(new_conv)
        self.db.commit()
        self.db.refresh(new_conv)
        return new_conv

    def add_message(self, conversation_id: str, role: str, content: str, sources: Optional[list] = None, agents: Optional[list] = None) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources or [],
            agents_used=agents or []
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg
