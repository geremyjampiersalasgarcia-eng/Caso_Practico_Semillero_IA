import os
from typing import List, Dict
from pydantic import BaseModel
from app.core.llm import get_llm
from app.utils.logger import logger
from langchain_core.messages import SystemMessage, HumanMessage


VALID_CATEGORIES = [
    "catalogo_precios",
    "politicas_comerciales",
    "proceso_ventas",
    "accion_registro",
    "multimodal",
    "mixta",
]


class IntentClassification(BaseModel):
    category: str
    confidence: float
    reasoning: str


def _load_classifier_prompt() -> str:
    """Carga el prompt del clasificador desde archivo."""
    prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "prompts", "classifier_prompt.md"
    )
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("Archivo de prompt del clasificador no encontrado, usando prompt inline")
        return ""


def classify_intent(
    question: str, has_image: bool = False
) -> IntentClassification:
    """
    Clasifica la pregunta del usuario en una de las categorías del dominio de Ventas.
    Usa temperatura 0 para mayor determinismo.

    Categorías:
    - catalogo_precios: productos, precios, disponibilidad
    - politicas_comerciales: descuentos, crédito, garantías, devoluciones
    - proceso_ventas: embudo, CRM, requisitos de cierre
    - accion_registro: solicitudes de registrar oportunidades
    - multimodal: consultas con imagen
    - mixta: consultas que abarcan más de un dominio
    """
    # Detección directa si hay imagen
    if has_image:
        logger.info(
            "Clasificación directa: multimodal (imagen detectada)",
            query=question,
        )
        return IntentClassification(
            category="multimodal",
            confidence=1.0,
            reasoning="La consulta incluye una imagen adjunta",
        )

    llm = get_llm(temperature=0.0)

    # Cargar prompt desde archivo, con fallback inline
    classifier_prompt = _load_classifier_prompt()
    if not classifier_prompt.strip():
        classifier_prompt = f"""Eres un clasificador experto del Departamento de Ventas de Patito S.A.
Clasifica la intención de la siguiente pregunta.
Solo puedes responder con una de estas categorías:
- catalogo_precios
- politicas_comerciales
- proceso_ventas
- accion_registro
- multimodal
- mixta
Responde ÚNICAMENTE con el nombre de la categoría."""

    messages = [
        SystemMessage(content=classifier_prompt),
        HumanMessage(content=question),
    ]

    try:
        response = llm.invoke(messages)
        # response.content puede ser str, list (bloques multimodal), o None
        raw_content = response.content
        if isinstance(raw_content, list):
            raw_content = " ".join(
                block.get("text", str(block))
                if isinstance(block, dict)
                else str(block)
                for block in raw_content
            )
        cat: str = (raw_content or "").strip().lower()

        # Validar contra categorías conocidas
        if cat not in VALID_CATEGORIES:
            # Intentar match parcial
            for valid_cat in VALID_CATEGORIES:
                if valid_cat in cat:
                    cat = valid_cat
                    break
            else:
                cat = "mixta"

        logger.info(
            "Clasificación de intención exitosa",
            query=question,
            category=cat,
        )

        return IntentClassification(
            category=cat,
            confidence=1.0,
            reasoning="Clasificación por prompt directo",
        )
    except Exception as e:
        logger.error("Error en clasificación, fallback a mixta", error=str(e))
        return IntentClassification(
            category="mixta", confidence=0.0, reasoning=str(e)
        )
