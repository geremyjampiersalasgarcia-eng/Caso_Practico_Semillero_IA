from app.agents.base_agent import BaseAgent
import os


class CatalogoAgent(BaseAgent):
    """
    Agente de Catálogo y Precios.
    Responsable de responder sobre productos, especificaciones,
    disponibilidad y lista de precios vigente de Patito S.A.
    """

    @property
    def name(self) -> str:
        return "agente_catalogo"

    @property
    def description(self) -> str:
        return (
            "Responde consultas sobre productos, especificaciones, "
            "disponibilidad y lista de precios vigente de Patito S.A."
        )

    @property
    def collection_name(self) -> str:
        return "col_catalogo"

    @property
    def system_prompt_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "..", "prompts", "catalogo_prompt.md"
        )
