import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Cargar .env explícitamente si existe
load_dotenv()

class Settings(BaseSettings):
    """
    Configuración global de la aplicación.
    Los valores se leen automáticamente del entorno o del archivo .env
    """
    
    # API Keys
    GOOGLE_API_KEY: str = Field(default="")
    
    # LLM y Embeddings
    LLM_MODEL_NAME: str = Field(default="gemini-1.5-flash")
    EMBEDDING_MODEL_NAME: str = Field(default="models/gemini-embedding-2")
    LLM_TEMPERATURE: float = Field(default=0.1)
    
    # Base de Datos
    DATABASE_URL: str = Field(default="postgresql://mesa_ayuda_user:mesa_ayuda_pass_2024@localhost:5433/mesa_ayuda_db")
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = Field(default="data/chroma_db")
    
    # RAG
    CHUNK_SIZE: int = Field(default=1000)
    CHUNK_OVERLAP: int = Field(default=200)
    RETRIEVAL_TOP_K: int = Field(default=4)
    
    # API y Servidor
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    
    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

# Instancia global
settings = Settings()
