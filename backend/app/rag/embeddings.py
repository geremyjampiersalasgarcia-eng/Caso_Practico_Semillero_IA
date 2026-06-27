from app.core.llm import get_embeddings

# Wrapper para mantener la estructura RAG separada,
# aunque la inicialización del modelo viva en core/llm.py

def get_rag_embeddings():
    """Retorna el modelo de embeddings para operaciones RAG."""
    return get_embeddings()
