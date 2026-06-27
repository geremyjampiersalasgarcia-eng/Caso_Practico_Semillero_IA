from typing import List, Dict
from pydantic import BaseModel
from app.core.llm import get_llm
from app.utils.logger import logger
from langchain_core.messages import SystemMessage, HumanMessage

class IntentClassification(BaseModel):
    category: str
    confidence: float
    reasoning: str

def classify_intent(question: str) -> IntentClassification:
    """
    Clasifica la pregunta del usuario en una de las categorías de dominio.
    Usa temperatura 0 para mayor determinismo.
    """
    llm = get_llm(temperature=0.0)
    
    # Este prompt es genérico y se adaptará cuando tengamos el tema,
    # pero el mecanismo de Pydantic/Structured Output de LangChain funcionará igual.
    # Por ahora usamos un approach básico: pedimos que devuelva la categoría en texto.
    
    prompt = """Eres un clasificador experto. Clasifica la intención de la siguiente pregunta del usuario.
    Solo puedes responder con una de estas categorías:
    - agente_1: para consultas sobre soporte técnico, niveles de soporte, tiempos de respuesta, accesos, operaciones generales
    - agente_2: para consultas sobre arquitectura de software, despliegues, contenedores, bases de datos, CI/CD
    - mixta: cuando la pregunta cubre ambos dominios o no queda claro
    
    Responde ÚNICAMENTE con el nombre de la categoría, sin explicación adicional."""
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=question)
    ]
    
    try:
        response = llm.invoke(messages)
        # response.content puede ser str, list (bloques multimodal), o None
        raw_content = response.content
        if isinstance(raw_content, list):
            # Extraer texto de bloques: [{"type": "text", "text": "..."}]
            raw_content = " ".join(
                block.get("text", str(block)) if isinstance(block, dict) else str(block)
                for block in raw_content
            )
        cat: str = (raw_content or "").strip().lower()
        
        # Validar fallback
        if cat not in ["agente_1", "agente_2", "mixta"]:
            cat = "mixta"
            
        logger.info("Clasificación de intención exitosa", query=question, category=cat)
        
        return IntentClassification(
            category=cat,
            confidence=1.0, # Simplificación por ahora sin structured output
            reasoning="Clasificación por prompt directo"
        )
    except Exception as e:
        logger.error("Error en clasificación, fallback a mixta", error=str(e))
        return IntentClassification(category="mixta", confidence=0.0, reasoning=str(e))
