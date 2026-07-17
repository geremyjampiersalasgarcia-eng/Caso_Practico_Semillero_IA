import time
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse, SourceInfo
from app.core.orchestrator import orchestrator_app
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.audit_repository import AuditRepository
from app.utils.logger import logger
from app.core.security import validar_input
from app.core.exceptions import AppError

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.conv_repo = ConversationRepository(db)
        self.audit_repo = AuditRepository(db)

    def process_chat(self, request: ChatRequest) -> ChatResponse:
        start_total = time.time()
        
        # 0. Capa 1: Firewall (Validación de Input)
        if not validar_input(request.question):
            raise AppError(
                status_code=400,
                message="ALERTA CAPA 1: Input rechazado por sospecha de inyección o abuso."
            )
        
        # 1. Recuperar o crear conversación
        conv = self.conv_repo.get_or_create_conversation(request.conversation_id)
        
        # Guardar mensaje del usuario
        self.conv_repo.add_message(
            conversation_id=conv.id,
            role="user",
            content=request.question,
            image_data=request.image
        )

        # Recuperar historial
        history = [{"role": m.role, "content": m.content} for m in sorted(conv.messages, key=lambda x: x.created_at) if m.role in ["user", "assistant"]]

        # 2. Invocar Orquestador LangGraph
        initial_state = {
            "question": request.question,
            "history": history,
            "image_data": request.image,
            "confirmation": request.confirmation,
            "agent_results": [],
            "agents_invoked": [],
            "sources": [],
            "warnings": [],
            "tokens_input": 0,
            "tokens_output": 0,
        }
        
        logger.info("Invocando orquestador", conversation_id=conv.id)
        result_state = orchestrator_app.invoke(initial_state)
        
        # ═══ CAPA 4: OUTPUT VALIDATION ═══
        final_answer = result_state.get("final_answer", "Error procesando la solicitud.")
        final_answer = self._validate_output(final_answer)
        
        # 3. Extraer resultados
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

        # Obtener trace_id
        from opentelemetry import trace
        current_span = trace.get_current_span()
        trace_id = None
        if current_span and current_span.get_span_context().is_valid:
            trace_id = format(current_span.get_span_context().trace_id, "032x")

        # Sumar tokens (se espera que el state los devuelva, Fase 2 requiere extraerlos)
        tokens_input = result_state.get("tokens_input", 0)
        tokens_output = result_state.get("tokens_output", 0)
        tokens_total = tokens_input + tokens_output
        
        # Tarifa Gemini 1.5 Flash (ejemplo): $0.075/1M input, $0.30/1M output
        cost_usd = (tokens_input / 1_000_000 * 0.075) + (tokens_output / 1_000_000 * 0.30)

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
            conversation_id=conv.id,
            tokens_used=tokens_total,
            trace_id=trace_id,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_usd=cost_usd
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

    def _validate_output(self, answer: str) -> str:
        """
        Capa 4: Output Validation.
        Sanitiza la respuesta antes de enviarla al usuario.
        """
        import re
        
        # 1. Detectar si la respuesta contiene partes del system prompt filtrado
        prompt_leak_patterns = [
            r"system prompt",
            r"instrucciones internas",
            r"NO NEGOCIABLES",
            r"NUNCA cambies de rol",
        ]
        for pattern in prompt_leak_patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                logger.warning("OUTPUT VALIDATION: Posible filtración de system prompt detectada")
                answer = "Lo siento, no puedo procesar esa solicitud. ¿En qué más puedo ayudarte sobre productos de Patito S.A.?"
                return answer
        
        # 2. Detectar precios que podrían ser alucinaciones (precios muy altos o muy bajos)
        price_matches = re.findall(r'\$\s?([\d,]+(?:\.\d{2})?)', answer)
        for price_str in price_matches:
            try:
                price = float(price_str.replace(',', ''))
                if price > 100000 or price < 1:
                    logger.warning(f"OUTPUT VALIDATION: Precio sospechoso detectado: ${price_str}")
                    answer += "\n\n> ⚠️ **Nota:** Verifica los precios mencionados directamente con el catálogo oficial antes de cotizar."
                    break
            except ValueError:
                pass
        
        return answer
