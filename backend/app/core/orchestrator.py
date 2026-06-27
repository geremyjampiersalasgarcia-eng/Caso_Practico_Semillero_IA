import time
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from app.core.classifier import classify_intent
from app.agents.registry import agent_registry
from app.schemas.agent import AgentResult
from app.utils.logger import logger
from app.core.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
import operator

# 1. Definir el Estado del Grafo
class GraphState(TypedDict):
    question: str
    category: str
    agent_results: Annotated[List[AgentResult], operator.add]
    final_answer: str
    sources: List[Dict[str, Any]]
    agents_invoked: Annotated[List[str], operator.add]
    start_time: float

# 2. Nodos del Grafo

def node_classify(state: GraphState):
    """Nodo 1: Clasifica la intención de la pregunta"""
    logger.info("Orquestador: Iniciando clasificación")
    intent = classify_intent(state["question"])
    return {"category": intent.category, "start_time": time.time()}

def node_agent_1(state: GraphState):
    """Nodo 2a: Ejecuta Agente 1 (Placeholder)"""
    try:
        agent = agent_registry.get_agent("agente_1")
        result = agent.process_query(state["question"])
        return {"agent_results": [result], "agents_invoked": ["agente_1"]}
    except Exception as e:
        logger.error("Error en agente 1", error=str(e))
        return {"agent_results": [], "agents_invoked": ["agente_1 (failed)"]}

def node_agent_2(state: GraphState):
    """Nodo 2b: Ejecuta Agente 2 (Placeholder)"""
    try:
        agent = agent_registry.get_agent("agente_2")
        result = agent.process_query(state["question"])
        return {"agent_results": [result], "agents_invoked": ["agente_2"]}
    except Exception as e:
        logger.error("Error en agente 2", error=str(e))
        return {"agent_results": [], "agents_invoked": ["agente_2 (failed)"]}

def node_consolidate(state: GraphState):
    """Nodo 3: Consolida resultados si hubo más de un agente, o pasa directo"""
    results = state.get("agent_results", [])
    
    if not results:
        return {"final_answer": "Hubo un error procesando la consulta con los agentes.", "sources": []}
        
    all_sources = []
    for r in results:
        all_sources.extend(r.sources)
        
    if len(results) == 1:
        # Solo un agente respondió, su respuesta es la final
        return {"final_answer": results[0].answer, "sources": all_sources}
        
    # Múltiples agentes: Consolidar con LLM
    logger.info("Orquestador: Consolidando respuestas múltiples")
    llm = get_llm()
    
    context = "\n\n".join([f"[{r.agent_name}]: {r.answer}" for r in results])
    
    prompt = f"""
    Consolida las siguientes respuestas de diferentes agentes expertos en una respuesta única,
    coherente y bien estructurada para el usuario.
    
    Respuestas de los agentes:
    {context}
    
    Pregunta original del usuario: {state['question']}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"final_answer": response.content, "sources": all_sources}
    except Exception as e:
        logger.error("Error consolidando", error=str(e))
        return {"final_answer": "Error al consolidar las respuestas parciales.", "sources": all_sources}

# 3. Lógica de Enrutamiento (Conditional Edges)
def route_agents(state: GraphState):
    cat = state["category"]
    if cat == "agente_1":
        return ["agent_1"]
    elif cat == "agente_2":
        return ["agent_2"]
    else:
        # Mixta: Invocar a ambos en paralelo
        return ["agent_1", "agent_2"]

# 4. Construir el Grafo
workflow = StateGraph(GraphState)

workflow.add_node("classify", node_classify)
workflow.add_node("agent_1", node_agent_1)
workflow.add_node("agent_2", node_agent_2)
workflow.add_node("consolidate", node_consolidate)

workflow.set_entry_point("classify")

workflow.add_conditional_edges(
    "classify",
    route_agents,
    {
        "agent_1": "agent_1",
        "agent_2": "agent_2",
    }
)

# Ambos agentes convergen en consolidar
workflow.add_edge("agent_1", "consolidate")
workflow.add_edge("agent_2", "consolidate")
workflow.add_edge("consolidate", END)

orchestrator_app = workflow.compile()
