from app.agents.base_agent import BaseAgent
import os


class PoliticasAgent(BaseAgent):
    """
    Agente de Políticas Comerciales.
    Responsable de responder sobre descuentos autorizados,
    condiciones de crédito, garantías y devoluciones.
    """

    @property
    def name(self) -> str:
        return "agente_politicas"

    @property
    def description(self) -> str:
        return (
            "Responde consultas sobre descuentos autorizados, condiciones "
            "de crédito, garantías y devoluciones de Patito S.A."
        )

    @property
    def collection_name(self) -> str:
        return "col_politicas"

    @property
    def system_prompt_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "..", "prompts", "politicas_prompt.md"
        )
