from typing import Dict, List
from app.agents.base_agent import BaseAgent
from app.core.exceptions import AgentNotFoundError
from app.schemas.agent import AgentInfo
from app.utils.logger import logger

class AgentRegistry:
    """
    Patrón Registry para los agentes.
    Permite registrar nuevos agentes sin modificar el código del orquestador.
    """
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """Registra una instancia de un agente"""
        if agent.name in self._agents:
            logger.warning("Sobrescribiendo agente existente", agent=agent.name)
        self._agents[agent.name] = agent
        logger.info("Agente registrado exitosamente", agent=agent.name)

    def get_agent(self, name: str) -> BaseAgent:
        """Recupera un agente por su nombre"""
        agent = self._agents.get(name)
        if not agent:
            raise AgentNotFoundError(name)
        return agent

    def list_agents(self) -> List[AgentInfo]:
        """Lista todos los agentes disponibles y sus descripciones"""
        return [
            AgentInfo(name=agent.name, description=agent.description)
            for agent in self._agents.values()
        ]

# Instancia global del registro
agent_registry = AgentRegistry()
