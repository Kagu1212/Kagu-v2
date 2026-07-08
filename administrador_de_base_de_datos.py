import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de base de datos"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        logger.info(f"✓ DatabaseManager: {db_path}")
    
    def add_conversation(self, session_id: str, role: str, content: str):
        pass
    
    def cleanup_old_data(self, days: int = 30):
        logger.info(f"Limpiando datos > {days} días")