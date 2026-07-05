import time
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse, SourceInfo
from app.core.orchestrator import orchestrator_app
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.audit_repository import AuditRepository
from app.utils.logger import logger

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.conv_repo = ConversationRepository(db)
        self.audit_repo = AuditRepository(db)

    def process_chat(self, request: ChatRequest) -> ChatResponse:
        start_total = time.time()
        
        # 1. Recuperar o crear conversación
        conv = self.conv_repo.get_or_create_conversation(request.conversation_id)
        
        # Guardar mensaje del usuario
        self.conv_repo.add_message(
            conversation_id=conv.id,
            role="user",
            content=request.question
        )

        # 2. Invocar Orquestador LangGraph
        initial_state = {
            "question": request.question,
            "image_data": request.image,
            "confirmation": request.confirmation,
            "agent_results": [],
            "agents_invoked": [],
            "sources": [],
            "warnings": [],
        }
        
        logger.info("Invocando orquestador", conversation_id=conv.id)
        result_state = orchestrator_app.invoke(initial_state)
        
        # 3. Extraer resultados
        final_answer = result_state.get("final_answer", "Error procesando la solicitud.")
        category = result_state.get("category", "unknown")
        agents_invoked = result_state.get("agents_invoked", [])
        raw_sources = result_state.get("sources", [])
        warnings = result_state.get("warnings", [])
        
        # Formatear fuentes (pueden venir como dict o como objetos Pydantic)
        formatted_sources = []
        for s in raw_sources:
            if isinstance(s, dict):
                formatted_sources.append(SourceInfo(
                    document_name=s.get("document_name", "Desconocido"),
                    content_snippet=s.get("content_snippet", ""),
                    relevance_score=s.get("relevance_score", 0.0)
                ))
            elif isinstance(s, SourceInfo):
                formatted_sources.append(s)
            else:
                # Si es otro objeto Pydantic con los mismos campos
                formatted_sources.append(SourceInfo(
                    document_name=getattr(s, "document_name", "Desconocido"),
                    content_snippet=getattr(s, "content_snippet", ""),
                    relevance_score=getattr(s, "relevance_score", 0.0)
                ))
        
        latency = (time.time() - start_total) * 1000

        # 4. Guardar respuesta del asistente
        self.conv_repo.add_message(
            conversation_id=conv.id,
            role="assistant",
            content=final_answer,
            sources=[s.model_dump() for s in formatted_sources],
            agents=agents_invoked
        )

        # 5. Crear log de auditoría
        self.audit_repo.create_log(
            intent_category=category,
            agents_invoked=agents_invoked,
            sources_retrieved=[s.model_dump() for s in formatted_sources],
            latency_ms=latency,
            conversation_id=conv.id
        )

        # 6. Retornar
        return ChatResponse(
            answer=final_answer,
            meta=ChatResponse.MetaInfo(
                agents_used=agents_invoked,
                latency_ms=latency,
                conversation_id=conv.id
            ),
            sources=formatted_sources,
            warnings=warnings,
        )
