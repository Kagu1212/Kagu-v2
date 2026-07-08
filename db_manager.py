# database/db_manager.py

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from threading import Lock
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de base de datos SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = Lock()
        self._init_db()
        logger.info(f"✓ DatabaseManager listo: {db_path}")
    
    def _init_db(self):
        """Inicializa la BD con esquema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de sesiones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT DEFAULT 'default'
                )
            """)
            
            # Tabla de conversaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            
            # Tabla de preferencias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    key TEXT,
                    value TEXT,
                    UNIQUE(user_id, key)
                )
            """)
            
            # Tabla de eventos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    source TEXT,
                    severity TEXT DEFAULT 'info',
                    description TEXT,
                    data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_conversation(self, session_id: str, role: str, content: str):
        """Añade un mensaje de conversación"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations (session_id, role, content)
                    VALUES (?, ?, ?)
                """, (session_id, role, content))
                conn.commit()
                logger.debug(f"💬 Conversación guardada: {role}")
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Obtiene historial de conversación"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content, timestamp
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def set_preference(self, user_id: str, key: str, value: str):
        """Guarda una preferencia"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO preferences (user_id, key, value)
                    VALUES (?, ?, ?)
                """, (user_id, key, value))
                conn.commit()
                logger.debug(f"⚙️ Preferencia guardada: {key}={value}")
    
    def get_preference(self, user_id: str, key: str, default: str = None) -> Optional[str]:
        """Obtiene una preferencia"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value FROM preferences
                WHERE user_id = ? AND key = ?
            """, (user_id, key))
            result = cursor.fetchone()
            return result[0] if result else default
    
    def log_event(self, event_type: str, source: str, description: str, 
                  severity: str = "info", data: Dict = None):
        """Registra un evento"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO events (event_type, source, severity, description, data)
                    VALUES (?, ?, ?, ?, ?)
                """, (event_type, source, severity, description, json.dumps(data or {})))
                conn.commit()
                logger.debug(f"📊 Evento registrado: {event_type}")
    
    def cleanup_old_data(self, days: int = 30):
        """Limpia datos antiguos"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    DELETE FROM conversations
                    WHERE timestamp < datetime('now', '-{days} days')
                """)
                conn.commit()
                logger.info(f"🗑️ Datos antiguos limpiados ({days} días)")
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas de la BD"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conversations_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM events")
            events_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM preferences")
            preferences_count = cursor.fetchone()[0]
            
            return {
                "conversations": conversations_count,
                "events": events_count,
                "preferences": preferences_count,
                "timestamp": datetime.now().isoformat()
            }