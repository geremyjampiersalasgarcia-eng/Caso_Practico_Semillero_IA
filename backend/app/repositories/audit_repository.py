from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from typing import List, Dict, Optional

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_log(self, 
                   intent_category: str,
                   agents_invoked: List[str],
                   sources_retrieved: List[Dict],
                   latency_ms: float,
                   tokens_used: int = 0,
                   conversation_id: Optional[str] = None) -> AuditLog:
                       
        log = AuditLog(
            intent_category=intent_category,
            agents_invoked=agents_invoked,
            sources_retrieved=sources_retrieved,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            conversation_id=conversation_id
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
