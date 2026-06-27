from fastapi import Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    """Excepción base para todos los errores de la aplicación"""
    def __init__(self, message: str, status_code: int = 400, error_code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class AgentNotFoundError(AppError):
    def __init__(self, agent_name: str):
        super().__init__(
            message=f"El agente '{agent_name}' no está registrado en el sistema.",
            status_code=404,
            error_code="AGENT_NOT_FOUND"
        )

class RAGRetrievalError(AppError):
    def __init__(self, details: str):
        super().__init__(
            message=f"Error al recuperar documentos de ChromaDB: {details}",
            status_code=500,
            error_code="RAG_RETRIEVAL_ERROR"
        )

class InsufficientContextError(AppError):
    def __init__(self):
        super().__init__(
            message="No se encontró información suficiente en la base documental para responder la consulta.",
            status_code=200, # 200 porque no es un fallo técnico, es un fallo semántico/negocio
            error_code="INSUFFICIENT_CONTEXT"
        )

class LLMConnectionError(AppError):
    def __init__(self, details: str):
        super().__init__(
            message=f"Error de conexión con el proveedor LLM (Gemini): {details}",
            status_code=502, # Bad Gateway
            error_code="LLM_CONNECTION_ERROR"
        )

# Handler global para FastAPI
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )
