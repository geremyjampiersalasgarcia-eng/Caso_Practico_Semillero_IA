from fastapi import HTTPException, status
import re
from typing import Optional

# Patrones maliciosos (Capa 1)
PATRONES_PROHIBIDOS = [
    r"ignora[\s\w]*instrucciones",
    r"cambia[\s\w]*rol",
    r"olvida[\s\w]*anterior",
    r"eres[\s\w]*ahora",
    r"bypass",
]

def validar_input(question: Optional[str] = None) -> str:
    """
    FastAPI Dependency para validar el input (Capa 1 - Firewall).
    Se inyecta en el endpoint de chat.
    """
    if not question:
        return ""
        
    if len(question) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Input rechazado: Pregunta demasiado larga"
        )
        
    q_lower = question.lower()
    for patron in PATRONES_PROHIBIDOS:
        if re.search(patron, q_lower):
            # En un entorno real se podría guardar en log de auditoría como ataque
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Input rechazado: Patrón sospechoso detectado"
            )
            
    return question
