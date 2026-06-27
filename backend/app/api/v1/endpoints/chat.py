from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.db.session import get_db
from app.utils.logger import logger

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def process_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Recibe una pregunta del usuario, invoca al orquestador y devuelve la respuesta final
    con las fuentes utilizadas.
    """
    logger.info("Recibida petición de chat", question=request.question, conv_id=request.conversation_id)
    service = ChatService(db)
    response = service.process_chat(request)
    return response
