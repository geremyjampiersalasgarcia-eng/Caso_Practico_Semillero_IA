import os
from langchain_chroma import Chroma
from app.config import settings
from app.rag.embeddings import get_rag_embeddings
from app.utils.logger import logger

def get_vectorstore(collection_name: str) -> Chroma:
    """
    Inicializa o recupera un Chroma vector store local para la colección dada.
    """
    embeddings = get_rag_embeddings()
    
    # Crear directorio si no existe
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    
    try:
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR
        )
        return vectorstore
    except Exception as e:
        logger.error("Error inicializando ChromaDB", collection=collection_name, error=str(e))
        raise

def index_documents(documents, collection_name: str):
    """
    Agrega o actualiza documentos en una colección específica.
    """
    vectorstore = get_vectorstore(collection_name)
    vectorstore.add_documents(documents)
    logger.info("Documentos indexados exitosamente", collection=collection_name, doc_count=len(documents))
