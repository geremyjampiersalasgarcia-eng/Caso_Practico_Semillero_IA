from app.agents.registry import agent_registry
from app.agents.catalogo_agent import CatalogoAgent
from app.agents.politicas_agent import PoliticasAgent
from app.agents.proceso_ventas_agent import ProcesoVentasAgent
from app.agents.multimodal_agent import MultimodalAgent
from app.agents.accion_agent import AccionAgent


def register_all_agents():
    """Registra todos los agentes especializados del Departamento de Ventas."""
    # Agentes RAG obligatorios
    agent_registry.register(CatalogoAgent())
    agent_registry.register(PoliticasAgent())
    agent_registry.register(ProcesoVentasAgent())

    # Agentes adicionales
    agent_registry.register(MultimodalAgent())
    agent_registry.register(AccionAgent())
