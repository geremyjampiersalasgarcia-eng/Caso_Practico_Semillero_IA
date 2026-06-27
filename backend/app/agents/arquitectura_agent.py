from app.agents.base_agent import BaseAgent
import os

class ArquitecturaAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "agente_2"  # Orquestador espera este nombre temporalmente

    @property
    def description(self) -> str:
        return "Responde consultas sobre arquitectura, diseño, tecnologías y despliegues."

    @property
    def collection_name(self) -> str:
        return "col_arquitectura"

    @property
    def system_prompt_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), "..", "prompts", "arquitectura_prompt.md")
