from app.agents.base_agent import BaseAgent
import os

class SoporteAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "agente_1"  # Orquestador espera este nombre temporalmente

    @property
    def description(self) -> str:
        return "Responde consultas sobre niveles de soporte, accesos y operaciones generales."

    @property
    def collection_name(self) -> str:
        return "col_soporte"

    @property
    def system_prompt_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), "..", "prompts", "soporte_prompt.md")
