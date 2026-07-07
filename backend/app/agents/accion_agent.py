import os
import uuid
from datetime import datetime
from typing import Optional

from app.agents.base_agent import BaseAgent
from app.core.llm import get_llm
from app.rag.retriever import retrieve_context
from app.schemas.agent import AgentResult
from app.utils.logger import logger
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from app.db.session import get_db
from app.models.opportunity import Oportunidad


REGISTRO_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "registro_oportunidades.txt"
)


def _es_duplicado(cliente: str, producto: str) -> bool:
    """Verifica si ya existe un registro reciente con el mismo cliente y producto."""
    if not os.path.exists(REGISTRO_FILE):
        return False
    try:
        with open(REGISTRO_FILE, "r", encoding="utf-8") as f:
            contenido = f.read().lower()
            if cliente.lower() in contenido and producto.lower() in contenido:
                return True
        return False
    except Exception:
        return False


@tool
def registrar_oportunidad_crm(
    cliente: str,
    contacto: str,
    producto: str,
    cantidad: int,
    precio_con_descuento: float,
    porcentaje_descuento: float,
    condicion_pago: str,
    monto_total: float,
) -> str:
    """Registra de manera definitiva la oportunidad en el sistema CRM (archivo de texto).
    EJECUTA ESTA HERRAMIENTA ÚNICAMENTE DESPUÉS DE QUE EL USUARIO HAYA CONFIRMADO EL RESUMEN.
    """
    if _es_duplicado(cliente, producto):
        return "ERROR: Posible registro duplicado detectado para ese cliente y producto. No se realizó el registro."

    # Generar ID único
    now = datetime.now()
    opp_id = f"OPP-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    registro = f"""ID: {opp_id}
Fecha: {now.strftime('%Y-%m-%d %H:%M:%S')}
Cliente: {cliente}
Contacto: {contacto}
Producto: {producto}
Cantidad: {cantidad}
Precio unitario (con descuento): {precio_con_descuento}
Descuento aplicado: {porcentaje_descuento}%
Condición de pago: {condicion_pago}
Monto total: {monto_total}
Estado: Registrada"""

    try:
        # 1. Guardar en TXT
        os.makedirs(os.path.dirname(REGISTRO_FILE), exist_ok=True)
        with open(REGISTRO_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(registro)
            f.write(f"\n{'='*60}\n")
            
        # 2. Guardar en PostgreSQL
        db_generator = get_db()
        db = next(db_generator)
        try:
            nueva_oportunidad = Oportunidad(
                id=opp_id,
                fecha=now,
                cliente=cliente,
                contacto=contacto,
                producto=producto,
                cantidad=cantidad,
                precio_con_descuento=precio_con_descuento,
                porcentaje_descuento=porcentaje_descuento,
                condicion_pago=condicion_pago,
                monto_total=monto_total,
                estado="Registrada"
            )
            db.add(nueva_oportunidad)
            db.commit()
            logger.info("Oportunidad guardada en PostgreSQL", opp_id=opp_id)
        except Exception as db_err:
            db.rollback()
            logger.error("Error guardando oportunidad en BD", error=str(db_err))
        finally:
            try:
                next(db_generator) # Para gatillar el finally con db.close() del generador
            except StopIteration:
                pass
                
        logger.info("Herramienta de registro ejecutada exitosamente", opp_id=opp_id)
        return f"Registro guardado con éxito (TXT y Base de Datos). El identificador es: {opp_id}"
    except Exception as e:
        logger.error("Error escribiendo archivo de registro", error=str(e))
        return f"ERROR interno del sistema al intentar guardar el archivo: {str(e)}"


class AccionAgent(BaseAgent):
    """
    Agente de Acción (Registro de Oportunidades).
    Usa function calling (tools) de LangChain/Gemini para escribir en archivo.
    """

    @property
    def name(self) -> str:
        return "agente_accion"

    @property
    def description(self) -> str:
        return (
            "Registra oportunidades en el CRM simulado usando LangChain Tools (Function Calling)."
        )

    @property
    def collection_name(self) -> str:
        return "col_proceso_ventas"

    @property
    def system_prompt_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "..", "prompts", "accion_prompt.md"
        )

    def process_query(
        self, question: str, confirmation: Optional[bool] = None, history: Optional[list] = None
    ) -> AgentResult:
        logger.info("Agente de acción procesando solicitud", agent=self.name)

        # Configurar LLM con la herramienta de registro
        llm_with_tools = get_llm().bind_tools([registrar_oportunidad_crm])  # type: ignore
        system_prompt = self._load_prompt()

        # Recuperar reglas desde la base de conocimiento
        contexts = retrieve_context(
            "requisitos registrar oportunidad CRM datos obligatorios",
            self.collection_name,
        )

        context_text = ""
        sources = []
        for i, ctx in enumerate(contexts):
            snippet = ctx["content"]
            metadata = ctx["metadata"]
            doc_name = metadata.get("filename", f"doc_{i}")
            context_text += f"--- Fragmento {i+1} de {doc_name} ---\n{snippet}\n\n"
            sources.append(
                {
                    "document_name": doc_name,
                    "content_snippet": snippet[:200] + "...",
                    "relevance_score": metadata.get("score", 0.0),
                }
            )

        # Instrucciones de control rigurosas para el uso de la tool
        instructions = f"""{system_prompt}

### CONTEXTO DE LA BASE DE CONOCIMIENTO (Reglas del CRM):
{context_text}

### INSTRUCCIONES DE CONTROL (¡MUY IMPORTANTE!):
1. Revisa si el usuario proporcionó TODOS los datos obligatorios para registrar la oportunidad.
2. Si falta algún dato, PREGÚNTALE al usuario cuáles faltan. NO LLAMES A LA HERRAMIENTA.
3. Si los datos están completos pero el usuario NO HA CONFIRMADO explícitamente, muéstrale un resumen de los datos y PÍDELE CONFIRMACIÓN. NO LLAMES A LA HERRAMIENTA.
4. Si el descuento supera el 10%, indícale que requiere autorización del gerente.
5. SÓLO si tienes todos los datos completos Y TIENES LA CONFIRMACIÓN del usuario, DEBES llamar a la herramienta `registrar_oportunidad_crm` pasando todos los argumentos.

Confirmación actual del usuario: {"SÍ, CONFIRMADO" if confirmation else "NO HA CONFIRMADO"}
"""

        messages = [SystemMessage(content=instructions)]
        if history:
            from langchain_core.messages import AIMessage
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        else:
            messages.append(HumanMessage(content=question))
            
        # Si la pregunta actual no es la última en el historial (a veces el historial ya la incluye)
        if not history or history[-1]["content"] != question:
            messages.append(HumanMessage(content=question))

        try:
            # Invocar al LLM, permitiendo function calling
            response = llm_with_tools.invoke(messages)

            # Verificar si el LLM decidió llamar a la herramienta
            if response.tool_calls:
                logger.info("El LLM decidió ejecutar la herramienta", tool_calls=response.tool_calls)
                tool_call = response.tool_calls[0]
                
                # Ejecutar la herramienta localmente
                tool_output = registrar_oportunidad_crm.invoke(tool_call["args"])  # type: ignore
                
                return AgentResult(
                    agent_name=self.name,
                    answer=f"✅ **Proceso de registro finalizado.**\n\nResultado del CRM: *{tool_output}*",
                    sources=sources,
                )
            else:
                # El LLM solo respondió con texto (pidiendo datos o confirmación)
                answer_text = str(response.content)
                if confirmation is not True and not "falta" in answer_text.lower():
                    answer_text += (
                        "\n\n---\n"
                        "⚠️ **Para continuar**, confirma respondiendo 'Sí, registrar' "
                        "o usa el botón de confirmación si está disponible."
                    )
                return AgentResult(
                    agent_name=self.name,
                    answer=answer_text,
                    sources=sources,
                )

        except Exception as e:
            logger.error("Error en agente de acción (Function Calling)", error=str(e))
            return AgentResult(
                agent_name=self.name,
                answer=f"❌ Ocurrió un error al procesar el registro: {str(e)}",
                sources=sources,
            )
