from typing import List, Dict, Any, Optional
from app.rag.vectorstore import get_vectorstore
from app.config import settings
from app.core.exceptions import RAGRetrievalError
from app.utils.logger import logger

def retrieve_context(query: str, collection_name: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Busca los fragmentos más relevantes para una query en una colección específica.
    Retorna una lista de diccionarios con el contenido y metadatos.
    """
    if top_k is None:
        top_k = settings.RETRIEVAL_TOP_K
        
    try:
        vectorstore = get_vectorstore(collection_name)
        # Búsqueda de similitud básica, se puede mejorar con MMR o HNSW parameters si se necesita
        docs = vectorstore.similarity_search(query, k=top_k)
        
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
            
        logger.debug("Contexto recuperado", query=query, collection=collection_name, count=len(results))
        return results
        
    except Exception as e:
        logger.error("Error recuperando contexto", query=query, collection=collection_name, error=str(e))
        raise RAGRetrievalError(str(e))
