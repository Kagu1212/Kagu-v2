# brain/state_manager.py

import logging
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import threading

logger = logging.getLogger(__name__)

class KAGUMode(Enum):
    """Modos de funcionamiento"""
    SLEEPING = "sleeping"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    ERROR = "error"

class ConnectionMode(Enum):
    """Modo de conexión"""
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"

class StateManager:
    """Gestor centralizado del estado global de KAGU"""
    
    def __init__(self):
        self.lock = threading.RLock()
        
        # Estado actual
        self._mode = KAGUMode.SLEEPING
        self._connection_mode = ConnectionMode.ONLINE
        self._active_session_id = None
        self._last_activity = datetime.now()
        
        # Contexto global
        self._global_context = {
            "user_name": "Usuario",
            "time_of_day": "morning",
            "location": "home",
            "current_task": None,
            "device_state": {}
        }
        
        # Callbacks
        self._state_callbacks: Dict[str, List[Callable]] = {}
        
        logger.info("✓ StateManager inicializado")
    
    # ===== MODO =====
    def set_mode(self, new_mode: KAGUMode):
        """Cambia el modo de KAGU"""
        with self.lock:
            if self._mode != new_mode:
                old_mode = self._mode
                self._mode = new_mode
                self._last_activity = datetime.now()
                logger.info(f"🔄 Modo: {old_mode.value} → {new_mode.value}")
                
                # Ejecutar callbacks
                if "mode_changed" in self._state_callbacks:
                    for callback in self._state_callbacks["mode_changed"]:
                        try:
                            callback(old_mode, new_mode)
                        except Exception as e:
                            logger.error(f"Error en callback: {e}")
    
    def get_mode(self) -> KAGUMode:
        """Obtiene el modo actual"""
        with self.lock:
            return self._mode
    
    # ===== CONEXIÓN =====
    def set_connection_mode(self, mode: ConnectionMode):
        """Cambia el modo de conexión"""
        with self.lock:
            if self._connection_mode != mode:
                old_mode = self._connection_mode
                self._connection_mode = mode
                logger.info(f"🌐 Conexión: {old_mode.value} → {mode.value}")
                
                if "connection_changed" in self._state_callbacks:
                    for callback in self._state_callbacks["connection_changed"]:
                        try:
                            callback(old_mode, mode)
                        except Exception as e:
                            logger.error(f"Error en callback: {e}")
    
    def get_connection_mode(self) -> ConnectionMode:
        """Obtiene el modo de conexión"""
        with self.lock:
            return self._connection_mode
    
    def is_online(self) -> bool:
        """¿Está en línea?"""
        with self.lock:
            return self._connection_mode != ConnectionMode.OFFLINE
    
    # ===== SESIÓN =====
    def start_session(self, session_id: str):
        """Inicia una sesión"""
        with self.lock:
            self._active_session_id = session_id
            logger.info(f"🔓 Sesión iniciada: {session_id}")
    
    def end_session(self):
        """Termina la sesión actual"""
        with self.lock:
            if self._active_session_id:
                logger.info(f"🔒 Sesión terminada: {self._active_session_id}")
                self._active_session_id = None
    
    def get_session_id(self) -> Optional[str]:
        """Obtiene ID de sesión actual"""
        with self.lock:
            return self._active_session_id
    
    # ===== CONTEXTO GLOBAL =====
    def set_context(self, key: str, value: Any):
        """Establece una variable de contexto"""
        with self.lock:
            self._global_context[key] = value
            self._last_activity = datetime.now()
            logger.debug(f"📝 Contexto: {key} = {value}")
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Obtiene una variable de contexto"""
        with self.lock:
            return self._global_context.get(key, default)
    
    def get_full_context(self) -> Dict[str, Any]:
        """Obtiene todo el contexto"""
        with self.lock:
            return self._global_context.copy()
    
    # ===== CALLBACKS =====
    def on(self, event: str, callback: Callable):
        """Registra callback para evento"""
        with self.lock:
            if event not in self._state_callbacks:
                self._state_callbacks[event] = []
            self._state_callbacks[event].append(callback)
    
    # ===== SERIALIZACIÓN =====
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a diccionario"""
        with self.lock:
            return {
                "mode": self._mode.value,
                "connection_mode": self._connection_mode.value,
                "active_session_id": self._active_session_id,
                "last_activity": self._last_activity.isoformat(),
                "context": self._global_context
            }
    
    def __repr__(self) -> str:
        return f"StateManager(mode={self._mode.value}, connection={self._connection_mode.value})"