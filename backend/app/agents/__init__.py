from app.agents.registry import agent_registry
from app.agents.soporte_agent import SoporteAgent
from app.agents.arquitectura_agent import ArquitecturaAgent

def register_all_agents():
    """Registra todos los agentes disponibles en el sistema."""
    agent_registry.register(SoporteAgent())
    agent_registry.register(ArquitecturaAgent())
