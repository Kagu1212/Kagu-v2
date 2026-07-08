import json
from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración central de KAGU"""
    
    # Rutas
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"
    CONFIG_DIR = PROJECT_ROOT / "config"
    LOGS_DIR = DATA_DIR / "logs"
    CACHE_DIR = DATA_DIR / "cache"
    DB_PATH = DATA_DIR / "kagu.db"
    VECTOR_DB_PATH = DATA_DIR / "vector_db"
    
    # Crear directorios
    for dir_path in [DATA_DIR, LOGS_DIR, CACHE_DIR, VECTOR_DB_PATH]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # APIs
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Modelos
    PRIMARY_MODEL = "claude-3-5-sonnet-20241022"
    FALLBACK_MODEL = "ollama:mistral"
    
    # Memoria
    MAX_CONVERSATION_HISTORY = 50
    MAX_SHORT_TERM_MEMORY = 20
    
    # Sistema
    DEBUG = True
    LOG_LEVEL = "INFO"
    
    # App
    APP_NAME = "KAGU"
    APP_VERSION = "0.1.0"
    
    @staticmethod
    def load_json(filename: str) -> Dict[str, Any]:
        """Carga un JSON de configuración"""
        path = Config.CONFIG_DIR / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save_json(filename: str, data: Dict[str, Any]):
        """Guarda un JSON de configuración"""
        path = Config.CONFIG_DIR / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def __repr__(self):
        return f"Config(version={self.APP_VERSION}, debug={self.DEBUG})"