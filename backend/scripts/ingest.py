"""
Script de ingesta de documentos para la Mesa de Ayuda de Ventas — Patito S.A.

Cada documento se indexa en su propia colección ChromaDB:
  - 01_Catalogo_Productos_Precios.txt       → col_catalogo
  - 02_Politicas_Comerciales_Descuentos.txt  → col_politicas
  - 03_Proceso_Ventas_CRM.txt               → col_proceso_ventas

Uso:
  cd backend
  python scripts/ingest.py
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para que funcionen los imports de app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.rag.loader import load_documents
from app.rag.splitter import split_documents
from app.rag.vectorstore import index_documents, get_vectorstore
from app.utils.logger import logger


# Mapeo: patrón del nombre de archivo → colección de ChromaDB
DOCUMENT_COLLECTION_MAP = {
    "01_Catalogo": "col_catalogo",
    "02_Politicas": "col_politicas",
    "03_Proceso": "col_proceso_ventas",
}


def clear_collection(collection_name: str):
    """Limpia una colección existente antes de re-indexar."""
    try:
        vs = get_vectorstore(collection_name)
        # Obtener todos los IDs existentes y eliminarlos
        existing = vs.get()
        if existing and existing.get("ids"):
            vs.delete(ids=existing["ids"])
            logger.info(
                "Colección limpiada",
                collection=collection_name,
                docs_removed=len(existing["ids"]),
            )
    except Exception as e:
        logger.warning(
            "No se pudo limpiar la colección (puede no existir aún)",
            collection=collection_name,
            error=str(e),
        )


def get_collection_for_file(filename: str) -> str:
    """Determina la colección ChromaDB según el nombre del archivo."""
    for pattern, collection in DOCUMENT_COLLECTION_MAP.items():
        if pattern in filename:
            return collection
    # Fallback: si no matchea, indexar en todas las colecciones
    logger.warning(
        "Archivo no mapeado a colección específica, se ignorará",
        filename=filename,
    )
    return ""


def main():
    logger.info("=" * 60)
    logger.info("INGESTA DE DOCUMENTOS — Mesa de Ayuda Ventas Patito S.A.")
    logger.info("=" * 60)

    data_dir = os.path.join("data", "raw")
    logger.info(f"Cargando documentos desde: {data_dir}")

    # 1. Cargar TODOS los documentos
    all_documents = load_documents(data_dir)

    if not all_documents:
        logger.warning("No se encontraron documentos para procesar.")
        return

    logger.info(f"Total de documentos cargados: {len(all_documents)}")

    # 2. Limpiar colecciones existentes
    logger.info("Limpiando colecciones existentes...")
    for collection in DOCUMENT_COLLECTION_MAP.values():
        clear_collection(collection)

    # 3. Agrupar documentos por colección
    docs_by_collection = {}
    for doc in all_documents:
        filename = doc.metadata.get("filename", "")
        collection = get_collection_for_file(filename)
        if not collection:
            continue
        if collection not in docs_by_collection:
            docs_by_collection[collection] = []
        docs_by_collection[collection].append(doc)

    # 4. Chunking e indexación por colección
    for collection, docs in docs_by_collection.items():
        logger.info(f"\n--- Procesando colección: {collection} ---")
        logger.info(f"Documentos: {[d.metadata.get('filename') for d in docs]}")

        # Hacer chunking
        chunks = split_documents(docs)
        logger.info(f"Chunks generados: {len(chunks)}")

        # Indexar
        index_documents(chunks, collection_name=collection)
        logger.info(f"✅ Colección '{collection}' indexada con {len(chunks)} chunks")

    logger.info("\n" + "=" * 60)
    logger.info("¡INGESTA FINALIZADA EXITOSAMENTE!")
    logger.info("=" * 60)

    # Resumen
    logger.info("\nResumen de colecciones:")
    for collection in DOCUMENT_COLLECTION_MAP.values():
        try:
            vs = get_vectorstore(collection)
            count = vs._collection.count()
            logger.info(f"  • {collection}: {count} documentos indexados")
        except Exception:
            logger.info(f"  • {collection}: (no disponible)")


if __name__ == "__main__":
    main()
