"""
Configuración centralizada del sistema RAG
Maneja secrets y variables de entorno de forma segura
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    # Cargar .env desde el directorio raíz del proyecto
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Cargado archivo .env desde: {env_path}")
    else:
        logger.warning(f"Archivo .env no encontrado en: {env_path}")
        # Intentar cargar desde el directorio actual
        load_dotenv()
except ImportError:
    logger.warning("python-dotenv no está instalado. Usando variables de entorno del sistema.")


class Settings:
    """Configuración centralizada del sistema"""
    
    # API Keys (Secrets)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")
    
    # Configuración de la API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Configuración de la interfaz
    UI_HOST: str = os.getenv("UI_HOST", "0.0.0.0")
    UI_PORT: int = int(os.getenv("UI_PORT", "7860"))
    
    # Base de datos
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploaded_documents")
    
    # Modelos
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    # Modelo Local
    USE_LOCAL_LLM: bool = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    LOCAL_MODEL_PATH: str = os.getenv("LOCAL_MODEL_PATH", "./models/codellama-7b-programming")
    BASE_MODEL_PATH: Optional[str] = os.getenv("BASE_MODEL_PATH")
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    @classmethod
    def validate(cls) -> Tuple[bool, List[str]]:
        """
        Valida que las configuraciones críticas estén presentes
        
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # Validar API Key de OpenAI si no se usa modelo local
        if not cls.USE_LOCAL_LLM:
            if not cls.OPENAI_API_KEY:
                errors.append("OPENAI_API_KEY no está configurada. Es requerida para usar OpenAI.")
            elif cls.OPENAI_API_KEY == "tu_api_key_aqui" or cls.OPENAI_API_KEY.startswith("tu_"):
                errors.append("OPENAI_API_KEY parece ser un placeholder. Configura tu API key real.")
            elif len(cls.OPENAI_API_KEY) < 20:
                errors.append("OPENAI_API_KEY parece inválida (muy corta).")
        
        # Validar directorios
        if not Path(cls.CHROMA_DB_PATH).parent.exists():
            errors.append(f"Directorio padre para CHROMA_DB_PATH no existe: {cls.CHROMA_DB_PATH}")
        
        # Validar puertos
        if cls.API_PORT < 1 or cls.API_PORT > 65535:
            errors.append(f"API_PORT inválido: {cls.API_PORT}")
        if cls.UI_PORT < 1 or cls.UI_PORT > 65535:
            errors.append(f"UI_PORT inválido: {cls.UI_PORT}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_openai_key(cls) -> Optional[str]:
        """Obtiene la API key de OpenAI de forma segura"""
        return cls.OPENAI_API_KEY
    
    @classmethod
    def is_openai_configured(cls) -> bool:
        """Verifica si OpenAI está configurado correctamente"""
        if cls.USE_LOCAL_LLM:
            return True  # No necesita OpenAI
        return cls.OPENAI_API_KEY is not None and \
               cls.OPENAI_API_KEY != "tu_api_key_aqui" and \
               not cls.OPENAI_API_KEY.startswith("tu_") and \
               len(cls.OPENAI_API_KEY) > 20
    
    @classmethod
    def print_config(cls, show_secrets: bool = False):
        """Imprime la configuración actual (sin secrets por defecto)"""
        print("\n=== Configuración del Sistema RAG ===")
        print(f"\nAPI:")
        print(f"  Host: {cls.API_HOST}")
        print(f"  Puerto: {cls.API_PORT}")
        print(f"\nInterfaz Web:")
        print(f"  Host: {cls.UI_HOST}")
        print(f"  Puerto: {cls.UI_PORT}")
        print(f"\nBase de Datos:")
        print(f"  ChromaDB: {cls.CHROMA_DB_PATH}")
        print(f"  Uploads: {cls.UPLOAD_DIR}")
        print(f"\nModelos:")
        print(f"  Embedding: {cls.EMBEDDING_MODEL}")
        print(f"  LLM: {cls.LLM_MODEL}")
        print(f"  Local LLM: {'Sí' if cls.USE_LOCAL_LLM else 'No'}")
        print(f"\nRAG:")
        print(f"  Chunk Size: {cls.CHUNK_SIZE}")
        print(f"  Chunk Overlap: {cls.CHUNK_OVERLAP}")
        print(f"  Top K: {cls.TOP_K_RESULTS}")
        
        if show_secrets:
            print(f"\nSecrets:")
            print(f"  OpenAI API Key: {'***' + cls.OPENAI_API_KEY[-4:] if cls.OPENAI_API_KEY else 'No configurada'}")
            if cls.HF_TOKEN:
                print(f"  HF Token: {'***' + cls.HF_TOKEN[-4:]}")
        else:
            print(f"\nSecrets: {'Configurados' if cls.is_openai_configured() else 'No configurados'}")
        
        # Validar
        is_valid, errors = cls.validate()
        print(f"\nValidacion: {'[OK]' if is_valid else '[ERROR]'}")
        if errors:
            print("Errores:")
            for error in errors:
                print(f"  - {error}")


# Instancia global de configuración
settings = Settings()

