import os
import time
from typing import TypedDict, List, Dict, Any, Optional, Annotated

from langgraph.graph import StateGraph, END
from app.core.classifier import classify_intent
from app.agents.registry import agent_registry
from app.agents.multimodal_agent import MultimodalAgent
from app.agents.accion_agent import AccionAgent
from app.schemas.agent import AgentResult
from app.utils.logger import logger
from app.core.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
import operator


# --------------------------------------------------------------------------- #
#  1. Estado del Grafo
# --------------------------------------------------------------------------- #

class GraphState(TypedDict):
    question: str
    category: str
    history: List[Dict[str, str]]        # Historial de mensajes previos
    image_data: Optional[str]            # Base64 de la imagen (si existe)
    confirmation: Optional[bool]         # Confirmación del usuario para acción
    agent_results: Annotated[List[AgentResult], operator.add]
    final_answer: str
    sources: List[Dict[str, Any]]
    agents_invoked: Annotated[List[str], operator.add]
    warnings: List[str]
    start_time: float
    tokens_input: Annotated[int, operator.add]
    tokens_output: Annotated[int, operator.add]


# --------------------------------------------------------------------------- #
#  2. Nodos del Grafo
# --------------------------------------------------------------------------- #

def node_classify(state: GraphState):
    """Nodo 1: Clasifica la intención de la pregunta."""
    logger.info("Orquestador: Iniciando clasificación")
    has_image = bool(state.get("image_data"))
    
    # Si viene el flag de confirmación explícito del frontend, 
    # o si el usuario escribe una variante de confirmación corta
    q_lower = state.get("question", "").strip().lower()
    is_confirmation_text = q_lower in ["sí", "si", "sí, registrar", "si, registrar", "confirmar", "confirmo", "sí, registrar."]
    
    if state.get("confirmation") or is_confirmation_text:
        return {
            "category": "accion_registro",
            "start_time": time.time(),
            "warnings": [],
        }

    # Validar si estamos a mitad de un flujo de registro mirando el historial
    history = state.get("history", [])
    if history:
        # Buscar el último mensaje del asistente (recorriendo de atrás hacia adelante)
        last_assistant_msg = None
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                last_assistant_msg = msg
                break
                
        if last_assistant_msg:
            last_content = last_assistant_msg.get("content", "").lower()
            if "registrar la oportunidad" in last_content or "para continuar" in last_content:
                logger.info("Orquestador: Detectado flujo de registro en curso desde el historial")
                return {
                    "category": "accion_registro",
                    "start_time": time.time(),
                    "warnings": [],
                }

    intent = classify_intent(state["question"], has_image=has_image)
    return {
        "category": intent.category,
        "start_time": time.time(),
        "warnings": [],
    }


def node_catalogo(state: GraphState):
    """Nodo: Ejecuta Agente de Catálogo y Precios."""
    try:
        agent = agent_registry.get_agent("agente_catalogo")
        result = agent.process_query(state["question"])
        return {
            "agent_results": [result],
            "agents_invoked": ["agente_catalogo"],
            "tokens_input": getattr(result, "tokens_input", 0),
            "tokens_output": getattr(result, "tokens_output", 0),
        }
    except Exception as e:
        logger.error("Error en agente catálogo", error=str(e))
        return {
            "agent_results": [],
            "agents_invoked": ["agente_catalogo (error)"],
        }


def node_politicas(state: GraphState):
    """Nodo: Ejecuta Agente de Políticas Comerciales."""
    try:
        agent = agent_registry.get_agent("agente_politicas")
        result = agent.process_query(state["question"])
        return {
            "agent_results": [result],
            "agents_invoked": ["agente_politicas"],
            "tokens_input": getattr(result, "tokens_input", 0),
            "tokens_output": getattr(result, "tokens_output", 0),
        }
    except Exception as e:
        logger.error("Error en agente políticas", error=str(e))
        return {
            "agent_results": [],
            "agents_invoked": ["agente_politicas (error)"],
        }


def node_proceso_ventas(state: GraphState):
    """Nodo: Ejecuta Agente de Proceso de Venta y CRM."""
    try:
        agent = agent_registry.get_agent("agente_proceso_ventas")
        result = agent.process_query(state["question"])
        return {
            "agent_results": [result],
            "agents_invoked": ["agente_proceso_ventas"],
            "tokens_input": getattr(result, "tokens_input", 0),
            "tokens_output": getattr(result, "tokens_output", 0),
        }
    except Exception as e:
        logger.error("Error en agente proceso ventas", error=str(e))
        return {
            "agent_results": [],
            "agents_invoked": ["agente_proceso_ventas (error)"],
        }


def node_multimodal(state: GraphState):
    """Nodo: Ejecuta Agente Multimodal de Imagen."""
    try:
        agent = agent_registry.get_agent("agente_multimodal")
        # Cast al tipo específico que acepta image_data
        assert isinstance(agent, MultimodalAgent)
        result = agent.process_query(
            state["question"],
            image_data=state.get("image_data"),
        )
        return {
            "agent_results": [result],
            "agents_invoked": ["agente_multimodal"],
            "tokens_input": getattr(result, "tokens_input", 0),
            "tokens_output": getattr(result, "tokens_output", 0),
        }
    except Exception as e:
        logger.error("Error en agente multimodal", error=str(e))
        return {
            "agent_results": [],
            "agents_invoked": ["agente_multimodal (error)"],
        }


def node_accion(state: GraphState):
    """Nodo: Ejecuta Agente de Acción (Registro)."""
    try:
        agent = agent_registry.get_agent("agente_accion")
        # Cast al tipo específico que acepta confirmation
        assert isinstance(agent, AccionAgent)
        result = agent.process_query(
            state["question"],
            confirmation=state.get("confirmation"),
            history=state.get("history")
        )
        return {
            "agent_results": [result],
            "agents_invoked": ["agente_accion"],
            "tokens_input": getattr(result, "tokens_input", 0),
            "tokens_output": getattr(result, "tokens_output", 0),
        }
    except Exception as e:
        logger.error("Error en agente acción", error=str(e))
        return {
            "agent_results": [],
            "agents_invoked": ["agente_accion (error)"],
        }


def node_consolidate(state: GraphState):
    """Nodo final: Consolida resultados de uno o más agentes."""
    results = state.get("agent_results", [])
    warnings = state.get("warnings", [])

    if not results:
        return {
            "final_answer": "Hubo un error procesando la consulta con los agentes.",
            "sources": [],
            "warnings": warnings + ["Ningún agente pudo procesar la consulta."],
        }

    # Recopilar todas las fuentes
    all_sources = []
    for r in results:
        all_sources.extend(r.sources)

    # Si solo un agente respondió, su respuesta es la final
    if len(results) == 1:
        return {
            "final_answer": results[0].answer,
            "sources": all_sources,
            "warnings": warnings,
        }

    # Múltiples agentes: Consolidar con LLM
    logger.info("Orquestador: Consolidando respuestas de múltiples agentes")
    llm = get_llm()

    # Cargar prompt del orquestador
    prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "prompts", "orchestrator_prompt.md"
    )
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            orchestrator_prompt = f.read()
    except FileNotFoundError:
        orchestrator_prompt = "Consolida las respuestas de los agentes de forma coherente."

    context = "\n\n".join(
        [f"### [{r.agent_name}]:\n{r.answer}" for r in results]
    )

    prompt = f"""{orchestrator_prompt}

---

### Respuestas de los agentes participantes:
{context}

### Pregunta original del usuario:
{state['question']}

Genera una respuesta consolidada, única y bien estructurada."""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        
        tokens_input = 0
        tokens_output = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            tokens_input = response.usage_metadata.get("input_tokens", 0)
            tokens_output = response.usage_metadata.get("output_tokens", 0)
            
        return {
            "final_answer": response.content,
            "sources": all_sources,
            "warnings": warnings,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output
        }
    except Exception as e:
        logger.error("Error consolidando", error=str(e))
        # Fallback: concatenar las respuestas
        fallback = "\n\n---\n\n".join(
            [f"**{r.agent_name}:** {r.answer}" for r in results]
        )
        return {
            "final_answer": fallback,
            "sources": all_sources,
            "warnings": warnings + ["Error al consolidar; se muestran las respuestas individuales."],
            "tokens_input": 0,
            "tokens_output": 0
        }


# --------------------------------------------------------------------------- #
#  3. Lógica de Enrutamiento (Conditional Edges)
# --------------------------------------------------------------------------- #

def route_agents(state: GraphState):
    """
    Decide qué agente(s) invocar según la categoría clasificada.
    Retorna una lista de nombres de nodo.
    """
    cat = state["category"]

    if cat == "catalogo_precios":
        return ["catalogo"]
    elif cat == "politicas_comerciales":
        return ["politicas"]
    elif cat == "proceso_ventas":
        return ["proceso_ventas"]
    elif cat == "multimodal":
        return ["multimodal"]
    elif cat == "accion_registro":
        return ["accion"]
    else:
        # mixta: invocar los 3 agentes RAG principales en paralelo
        return ["catalogo", "politicas", "proceso_ventas"]


# --------------------------------------------------------------------------- #
#  4. Construir el Grafo
# --------------------------------------------------------------------------- #

workflow = StateGraph(GraphState)

# Agregar nodos
workflow.add_node("classify", node_classify)
workflow.add_node("catalogo", node_catalogo)
workflow.add_node("politicas", node_politicas)
workflow.add_node("proceso_ventas", node_proceso_ventas)
workflow.add_node("multimodal", node_multimodal)
workflow.add_node("accion", node_accion)
workflow.add_node("consolidate", node_consolidate)

# Punto de entrada
workflow.set_entry_point("classify")

# Enrutamiento condicional desde clasificación
workflow.add_conditional_edges(
    "classify",
    route_agents,
    {
        "catalogo": "catalogo",
        "politicas": "politicas",
        "proceso_ventas": "proceso_ventas",
        "multimodal": "multimodal",
        "accion": "accion",
    },
)

# Todos los agentes convergen en el nodo de consolidación
workflow.add_edge("catalogo", "consolidate")
workflow.add_edge("politicas", "consolidate")
workflow.add_edge("proceso_ventas", "consolidate")
workflow.add_edge("multimodal", "consolidate")
workflow.add_edge("accion", "consolidate")
workflow.add_edge("consolidate", END)

# Compilar el grafo
orchestrator_app = workflow.compile()
