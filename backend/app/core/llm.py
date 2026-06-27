from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from app.config import settings
from app.core.exceptions import LLMConnectionError
from app.utils.logger import logger

def get_llm(temperature: Optional[float] = None) -> ChatGoogleGenerativeAI:
    """
    Inicializa y retorna el cliente LLM (Gemini).
    Permite sobreescribir la temperatura para casos específicos (ej. clasificador con temp=0).
    """
    if not settings.GOOGLE_API_KEY:
        raise LLMConnectionError("GOOGLE_API_KEY no configurada.")
        
    temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=temp,
        )
        return llm
    except Exception as e:
        logger.error("Error inicializando LLM", error=str(e))
        raise LLMConnectionError(str(e))

def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Inicializa y retorna el modelo de embeddings.
    """
    if not settings.GOOGLE_API_KEY:
        raise LLMConnectionError("GOOGLE_API_KEY no configurada para embeddings.")
        
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY
        )
        return embeddings
    except Exception as e:
        logger.error("Error inicializando embeddings", error=str(e))
        raise LLMConnectionError(str(e))
