from abc import ABC, abstractmethod
from app.schemas.agent import AgentResult
from app.rag.retriever import retrieve_context
from app.core.llm import get_llm
from app.utils.logger import logger
from langchain_core.messages import SystemMessage, HumanMessage

class BaseAgent(ABC):
    """
    Clase base para todos los agentes especializados.
    Define el flujo estándar RAG + LLM.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del agente (ej. agente_arquitectura)"""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción de lo que hace el agente"""
        pass
        
    @property
    @abstractmethod
    def collection_name(self) -> str:
        """Nombre de la colección ChromaDB de este agente"""
        pass
        
    @property
    @abstractmethod
    def system_prompt_path(self) -> str:
        """Ruta al archivo Markdown con el prompt del agente"""
        pass

    def _load_prompt(self) -> str:
        try:
            with open(self.system_prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(
                "Archivo de prompt no encontrado",
                agent=self.name,
                path=self.system_prompt_path,
            )
            return "Eres un asistente especializado del departamento de ventas de Patito S.A. Responde únicamente con base en el contexto proporcionado."

    def process_query(self, question: str) -> AgentResult:
        """
        Flujo principal del agente:
        1. Busca en su colección ChromaDB
        2. Inyecta el contexto en su prompt
        3. Invoca al LLM
        4. Retorna el resultado con las fuentes
        """
        logger.info("Agente procesando consulta", agent=self.name)
        
        # 1. RAG Retrieval (con manejo de errores si ChromaDB está caído)
        contexts = []
        try:
            contexts = retrieve_context(question, self.collection_name)
        except Exception as e:
            logger.error(
                "Error al recuperar contexto de ChromaDB",
                agent=self.name,
                error=str(e),
            )
            return AgentResult(
                agent_name=self.name,
                answer=(
                    "⚠️ No se pudo conectar a la base de conocimiento (ChromaDB). "
                    "Verifica que el servicio esté activo y que se haya ejecutado "
                    "`python scripts/ingest.py` correctamente."
                ),
                sources=[],
            )
        
        # Extraer texto de los fragmentos y armar las fuentes
        context_text = ""
        sources = []
        for i, ctx in enumerate(contexts):
            snippet = ctx["content"]
            metadata = ctx["metadata"]
            doc_name = metadata.get("filename", f"doc_{i}")
            
            context_text += f"--- Fragmento {i+1} de {doc_name} ---\n{snippet}\n\n"
            
            sources.append({
                "document_name": doc_name,
                "content_snippet": (snippet[:200] + "...") if len(snippet) > 200 else snippet,
                "relevance_score": metadata.get("score", 0.0)
            })

        # 2. Preparar el Prompt
        base_prompt = self._load_prompt()
        system_content = f"{base_prompt}\n\n### CONTEXTO RECUPERADO:\n{context_text}"
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=question)
        ]
        
        # 3. Invocar LLM (con manejo de errores si Gemini falla)
        try:
            llm = get_llm()
            response = llm.invoke(messages)
        except Exception as e:
            logger.error(
                "Error al invocar el LLM (Gemini)",
                agent=self.name,
                error=str(e),
            )
            error_msg = str(e)
            if "429" in error_msg or "rate" in error_msg.lower():
                answer = (
                    "⚠️ Se alcanzó el límite de peticiones de la API de Gemini (Rate Limit). "
                    "Espera unos segundos e intenta de nuevo."
                )
            else:
                answer = (
                    "⚠️ Ocurrió un error al comunicarse con el modelo de IA. "
                    "Intenta de nuevo en unos segundos."
                )
            return AgentResult(
                agent_name=self.name,
                answer=answer,
                sources=sources,
            )
        
        # 4. Retornar
        return AgentResult(
            agent_name=self.name,
            answer=str(response.content),
            sources=sources
        )

