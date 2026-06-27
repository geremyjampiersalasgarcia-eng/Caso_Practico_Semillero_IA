from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
from app.rag.loader import load_documents
from app.rag.splitter import split_documents
from app.rag.vectorstore import index_documents
from app.utils.logger import logger
import os

router = APIRouter()

class IngestRequest(BaseModel):
    directory_path: str = "data/raw"
    collection_name: str

class IngestResponse(BaseModel):
    status: str
    message: str

def process_ingestion(directory_path: str, collection_name: str):
    try:
        docs = load_documents(directory_path)
        if not docs:
            logger.warning("No se encontraron documentos para ingestar", dir=directory_path)
            return
            
        chunks = split_documents(docs)
        index_documents(chunks, collection_name)
        logger.info("Ingesta completada en background", collection=collection_name, num_chunks=len(chunks))
    except Exception as e:
        logger.error("Error durante ingesta en background", error=str(e))

@router.post("/ingest", response_model=IngestResponse)
def ingest_documents(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Endpoint para disparar la ingesta de documentos en ChromaDB.
    Se ejecuta en background.
    """
    if not os.path.exists(request.directory_path):
        raise HTTPException(status_code=400, detail="El directorio no existe")
        
    background_tasks.add_task(process_ingestion, request.directory_path, request.collection_name)
    
    return IngestResponse(
        status="accepted",
        message=f"La ingesta para la colección '{request.collection_name}' ha comenzado en background."
    )
