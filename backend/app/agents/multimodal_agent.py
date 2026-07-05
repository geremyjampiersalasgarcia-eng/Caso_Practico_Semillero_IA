import base64
import os
from typing import Any, List, Optional

from app.agents.base_agent import BaseAgent
from app.core.llm import get_llm
from app.rag.retriever import retrieve_context
from app.schemas.agent import AgentResult
from app.utils.logger import logger
from langchain_core.messages import HumanMessage, SystemMessage


class MultimodalAgent(BaseAgent):
    """
    Agente Multimodal de Imagen.
    Analiza imágenes de productos usando la capacidad de visión de Google Gemini,
    identifica el producto y lo relaciona con el catálogo de Patito S.A.
    """

    @property
    def name(self) -> str:
        return "agente_multimodal"

    @property
    def description(self) -> str:
        return (
            "Analiza imágenes de productos usando visión de Gemini, "
            "identifica el producto y consulta precio y disponibilidad en el catálogo."
        )

    @property
    def collection_name(self) -> str:
        return "col_catalogo"  # Cruza con el catálogo para obtener precios

    @property
    def system_prompt_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "..", "prompts", "multimodal_prompt.md"
        )

    def process_query(
        self, question: str, image_data: Optional[str] = None
    ) -> AgentResult:
        """
        Flujo del agente multimodal:
        1. Recibe la imagen (base64) y la pregunta
        2. Usa Gemini Vision para analizar la imagen
        3. Busca en el catálogo (RAG) para complementar
        4. Retorna respuesta con producto, precio y disponibilidad
        """
        logger.info("Agente multimodal procesando consulta", agent=self.name)

        if not image_data:
            return AgentResult(
                agent_name=self.name,
                answer="No se proporcionó una imagen para analizar. "
                "Por favor, adjunta una imagen del producto.",
                sources=[],
            )

        # 1. Analizar la imagen con Gemini Vision
        llm = get_llm()
        vision_prompt = self._load_prompt()

        # Construir mensaje multimodal con imagen
        message_content: List[Any] = []

        # Agregar la imagen como contenido multimodal
        # Soportamos base64 directamente
        if image_data.startswith("data:"):
            # Ya tiene el prefijo data:image/...;base64,
            image_url = image_data
        else:
            # Solo es base64 crudo, agregar prefijo
            image_url = f"data:image/jpeg;base64,{image_data}"

        message_content.append(
            {"type": "image_url", "image_url": {"url": image_url}}
        )
        message_content.append(
            {
                "type": "text",
                "text": (
                    f"Analiza esta imagen y responde la siguiente pregunta: "
                    f"{question}"
                ),
            }
        )

        try:
            # Paso 1: Análisis de imagen con Gemini Vision
            vision_response = llm.invoke(
                [
                    SystemMessage(content=vision_prompt),
                    HumanMessage(content=message_content),
                ]
            )
            image_analysis = str(vision_response.content)
            logger.info("Análisis de imagen completado", agent=self.name)

        except Exception as e:
            logger.error("Error analizando imagen", error=str(e))
            return AgentResult(
                agent_name=self.name,
                answer=f"Error al analizar la imagen: {str(e)}",
                sources=[],
            )

        # Paso 2: Buscar en el catálogo (RAG) para complementar
        contexts = retrieve_context(
            f"producto {image_analysis}", self.collection_name
        )

        context_text = ""
        sources = []
        for i, ctx in enumerate(contexts):
            snippet = ctx["content"]
            metadata = ctx["metadata"]
            doc_name = metadata.get("filename", f"doc_{i}")
            context_text += (
                f"--- Fragmento {i+1} de {doc_name} ---\n{snippet}\n\n"
            )
            sources.append(
                {
                    "document_name": doc_name,
                    "content_snippet": snippet[:200] + "...",
                    "relevance_score": metadata.get("score", 0.0),
                }
            )

        # Paso 3: Consolidar análisis de imagen + datos del catálogo
        consolidation_prompt = f"""Con base en el análisis de la imagen y los datos del catálogo,
proporciona una respuesta completa al usuario.

### ANÁLISIS DE LA IMAGEN:
{image_analysis}

### DATOS DEL CATÁLOGO:
{context_text}

### PREGUNTA DEL USUARIO:
{question}

Responde indicando: producto identificado, precio de lista, disponibilidad y cualquier
información relevante del catálogo. Si no puedes identificar el producto con certeza,
indícalo claramente."""

        try:
            final_response = llm.invoke(
                [HumanMessage(content=consolidation_prompt)]
            )
            return AgentResult(
                agent_name=self.name,
                answer=str(final_response.content),
                sources=sources,
            )
        except Exception as e:
            logger.error("Error consolidando respuesta multimodal", error=str(e))
            return AgentResult(
                agent_name=self.name,
                answer=f"Análisis de imagen: {image_analysis}\n\n"
                "(No se pudo cruzar con el catálogo debido a un error.)",
                sources=sources,
            )
