from fastapi import APIRouter
from app.schemas.health import HealthResponse, ComponentStatus
from app.db.session import engine
from app.rag.vectorstore import get_vectorstore
from app.core.llm import get_llm

router = APIRouter()

@router.get("/", response_model=HealthResponse)
def health_check():
    """
    Verifica el estado del servicio y sus dependencias (Postgres, ChromaDB, Gemini).
    """
    components = {}
    overall_status = "healthy"
    
    # Check BD
    try:
        with engine.connect() as conn:
            pass
        components["database"] = ComponentStatus(status="ok")
    except Exception as e:
        components["database"] = ComponentStatus(status="error", details=str(e))
        overall_status = "degraded"
        
    # Check LLM (Fast check)
    try:
        llm = get_llm()
        if not llm:
            raise ValueError("No LLM instance")
        components["llm"] = ComponentStatus(status="ok")
    except Exception as e:
        components["llm"] = ComponentStatus(status="error", details=str(e))
        overall_status = "degraded"
        
    return HealthResponse(
        status=overall_status,
        components=components
    )
