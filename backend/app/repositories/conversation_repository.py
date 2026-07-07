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

    def add_message(self, conversation_id: str, role: str, content: str, sources: Optional[list] = None, agents: Optional[list] = None, image_data: Optional[str] = None) -> Message:
        # Check if conversation needs a title (first user message)
        conv = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv and role == "user" and not conv.title:
            # Generate simple title
            title = content[:25]
            if len(content) > 25:
                title += "..."
            conv.title = title
            
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources or [],
            agents_used=agents or [],
            image_data=image_data
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_all_conversations(self, skip: int = 0, limit: int = 100) -> List[Conversation]:
        return self.db.query(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    def get_conversation_with_messages(self, conversation_id: str) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def delete_conversation(self, conversation_id: str) -> bool:
        conv = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv:
            self.db.delete(conv)
            self.db.commit()
            return True
        return False
