from pydantic import BaseModel
from typing import List
from app.schemas.chat import SourceInfo

class AgentResult(BaseModel):
    """Resultado devuelto por un agente individual tras procesar una consulta"""
    agent_name: str
    answer: str
    sources: List[SourceInfo] = []
    tokens_input: int = 0
    tokens_output: int = 0

class AgentInfo(BaseModel):
    """Información de registro estático de un agente"""
    name: str
    description: str
