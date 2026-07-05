from app.agents.base_agent import BaseAgent
import os


class ProcesoVentasAgent(BaseAgent):
    """
    Agente de Proceso de Venta y CRM.
    Responsable de responder sobre etapas del embudo,
    registro en el CRM y requisitos para cerrar una venta.
    """

    @property
    def name(self) -> str:
        return "agente_proceso_ventas"

    @property
    def description(self) -> str:
        return (
            "Responde consultas sobre etapas del embudo de ventas, "
            "registro en el CRM y requisitos para cerrar una venta."
        )

    @property
    def collection_name(self) -> str:
        return "col_proceso_ventas"

    @property
    def system_prompt_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "..", "prompts", "proceso_ventas_prompt.md"
        )
