import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para que funcionen los imports de app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.rag.loader import load_documents
from app.rag.splitter import split_documents
from app.rag.vectorstore import index_documents
from app.utils.logger import logger

def main():
    logger.info("Iniciando proceso de ingesta de RAG...")
    
    # 1. Cargar documentos
    data_dir = os.path.join("data", "raw")
    logger.info(f"Cargando documentos desde {data_dir}")
    documents = load_documents(data_dir)
    
    if not documents:
        logger.warning("No se encontraron documentos para procesar.")
        return
        
    # 2. Hacer Chunking
    logger.info("Dividiendo documentos en chunks...")
    chunks = split_documents(documents)
    
    # 3. Indexar en ChromaDB
    logger.info("Generando embeddings e indexando en ChromaDB...")
    # Por ahora indexamos todo en una colección genérica para agentes mixtos o soporte
    index_documents(chunks, collection_name="col_soporte")
    index_documents(chunks, collection_name="col_arquitectura")
    
    logger.info("¡Proceso de ingesta finalizado con éxito!")

if __name__ == "__main__":
    main()
