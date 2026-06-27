import os
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from app.utils.logger import logger

def load_documents(directory_path: str) -> List[Document]:
    """
    Lee archivos (TXT, PDF) desde un directorio y retorna una lista de Documents.
    Agrega metadatos útiles (ej. filename) a cada documento.
    """
    documents = []
    path = Path(directory_path)
    
    if not path.exists():
        logger.warning("El directorio de documentos no existe", path=str(path))
        return documents
        
    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue
            
        try:
            if file_path.suffix.lower() == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
                docs = loader.load()
            elif file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()
            else:
                logger.debug("Formato no soportado, ignorando", file=file_path.name)
                continue
                
            # Agregar nombre de archivo como metadato si no lo tiene
            for doc in docs:
                if "source" not in doc.metadata:
                    doc.metadata["source"] = file_path.name
                # Guardar filename limpio para visualización
                doc.metadata["filename"] = file_path.name
                
            documents.extend(docs)
            logger.info("Archivo cargado", file=file_path.name, chunks=len(docs))
            
        except Exception as e:
            logger.error("Error al cargar archivo", file=file_path.name, error=str(e))
            
    return documents
