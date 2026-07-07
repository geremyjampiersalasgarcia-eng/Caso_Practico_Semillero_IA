from __future__ import annotations
import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey("conversations.id", ondelete="CASCADE"))
    
    role: Mapped[str] = mapped_column(String) # "user" o "assistant"
    content: Mapped[str] = mapped_column(Text)
    image_data: Mapped[str] = mapped_column(Text, nullable=True)
    
    # JSON genérico compatible con PostgreSQL y SQLite
    sources: Mapped[dict] = mapped_column(JSON, nullable=True, default=list) 
    agents_used: Mapped[dict] = mapped_column(JSON, nullable=True, default=list)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
