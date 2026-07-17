import sys
import os
import json
import re

# Asegurar que el backend está en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import _get_session_local
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.evaluation import Evaluation
from app.evaluation.rubrica import EvaluacionRica
from app.core.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def extract_json(text: str) -> str:
    """Extrae el primer bloque JSON de un texto."""
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return match.group(1)
    
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        return text[start:end+1]
    
    return text

def main():
    print("Iniciando Juez LLM Batch Evaluator...")
    SessionLocal = _get_session_local()
    db = SessionLocal()
    
    try:
        # Obtener las últimas conversaciones con al menos 1 mensaje de usuario y 1 de asistente
        conversations = db.query(Conversation).order_by(Conversation.created_at.desc()).limit(10).all()
        
        if not conversations:
            print("No hay conversaciones para evaluar.")
            return

        llm = get_llm()
        
        system_prompt = f"""
Eres un juez experto evaluando respuestas de un asistente de ventas de software (Patito S.A.).
Debes calificar la respuesta usando la siguiente estructura JSON obligatoria.
El output DEBE ser un JSON válido, sin texto adicional, que coincida con esta estructura:

{EvaluacionRica.model_json_schema()}
"""
        
        evaluaciones_insertadas = 0

        for conv in conversations:
            # Obtener el par pregunta / respuesta más reciente de esta conversación
            messages = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).all()
            if len(messages) < 2:
                continue
            
            # Tomar la última interacción
            pregunta = ""
            respuesta = ""
            
            for msg in reversed(messages):
                if msg.role == "assistant" and not respuesta:
                    respuesta = msg.content
                elif msg.role == "user" and not pregunta and respuesta:
                    pregunta = msg.content
                    break
                    
            if not pregunta or not respuesta:
                continue
                
            # Preguntar al Juez
            human_prompt = f"PREGUNTA DEL USUARIO:\n{pregunta}\n\nRESPUESTA DEL SISTEMA:\n{respuesta}"
            
            try:
                print(f"Evaluando conversación {conv.id}...")
                resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)])
                
                json_str = extract_json(str(resp.content))
                eval_data = json.loads(json_str)
                
                # Guardar cada métrica en la tabla Evaluation
                for dimension, metrica in eval_data.items():
                    eval_record = Evaluation(
                        conversation_id=conv.id,
                        dimension=dimension,
                        score=float(metrica.get("score", 0)),
                        justificacion=metrica.get("justificacion", "")
                    )
                    db.add(eval_record)
                    evaluaciones_insertadas += 1
                
                db.commit()
                print(f"[OK] Evaluada exitosamente.")
                
            except Exception as e:
                db.rollback()
                print(f"[ERROR] Error evaluando conversación {conv.id}: {str(e)}")

        print(f"\nEvaluación Batch completada. {evaluaciones_insertadas} dimensiones evaluadas insertadas.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
