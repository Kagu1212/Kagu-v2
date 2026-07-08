# setup.py
"""
Script de setup para crear la estructura completa de KAGU
Ejecutar: python setup.py
"""

import os
from pathlib import Path

def crear_archivo(ruta, contenido):
    """Crea un archivo con contenido"""
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"✓ {ruta}")

def main():
    print("🚀 Creando estructura de KAGU...\n")
    
    # Crear __init__.py en todas las carpetas
    carpetas = [
        'core',
        'ai',
        'brain',
        'database',
        'interface',
        'config',
        'utils',
        'tests',
        'data',
        'data/logs',
        'data/cache',
        'data/vector_db',
    ]
    
    for carpeta in carpetas:
        Path(carpeta).mkdir(parents=True, exist_ok=True)
        init_file = f'{carpeta}/__init__.py'
        if not os.path.exists(init_file):
            crear_archivo(init_file, '')
    
    print("\n📁 Carpetas creadas\n")
    
    # ===== CREAR ARCHIVOS PYTHON =====
    
    # 1. brain/state_manager.py
    crear_archivo('brain/state_manager.py', '''import logging
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional
import threading

logger = logging.getLogger(__name__)

class KAGUMode(Enum):
    SLEEPING = "sleeping"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    ERROR = "error"

class ConnectionMode(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"

class StateManager:
    """Gestor de estado global"""
    
    def __init__(self):
        self.lock = threading.RLock()
        self._mode = KAGUMode.SLEEPING
        self._connection_mode = ConnectionMode.ONLINE
        self._active_session_id = None
        self._last_activity = datetime.now()
        self._global_context = {
            "user_name": "Usuario",
            "time_of_day": "morning",
            "location": "home",
        }
        self._state_callbacks = {}
        logger.info("✓ StateManager inicializado")
    
    def set_mode(self, new_mode: KAGUMode):
        with self.lock:
            if self._mode != new_mode:
                old_mode = self._mode
                self._mode = new_mode
                self._last_activity = datetime.now()
                logger.info(f"Modo: {old_mode.value} → {new_mode.value}")
    
    def get_mode(self) -> KAGUMode:
        with self.lock:
            return self._mode
    
    def set_connection_mode(self, mode: ConnectionMode):
        with self.lock:
            if self._connection_mode != mode:
                old_mode = self._connection_mode
                self._connection_mode = mode
                logger.info(f"Conexión: {old_mode.value} → {mode.value}")
    
    def get_connection_mode(self) -> ConnectionMode:
        with self.lock:
            return self._connection_mode
    
    def is_online(self) -> bool:
        with self.lock:
            return self._connection_mode != ConnectionMode.OFFLINE
    
    def start_session(self, session_id: str):
        with self.lock:
            self._active_session_id = session_id
            logger.info(f"Sesión: {session_id[:12]}...")
    
    def end_session(self):
        with self.lock:
            self._active_session_id = None
    
    def get_session_id(self) -> Optional[str]:
        with self.lock:
            return self._active_session_id
    
    def set_context(self, key: str, value: Any):
        with self.lock:
            self._global_context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        with self.lock:
            return self._global_context.get(key, default)
    
    def get_full_context(self) -> Dict[str, Any]:
        with self.lock:
            return self._global_context.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "mode": self._mode.value,
                "connection": self._connection_mode.value,
                "session": self._active_session_id,
                "context": self._global_context
            }
''')
    
    # 2. brain/memory_manager.py
    crear_archivo('brain/memory_manager.py', '''from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """Gestor de memoria (corto y largo plazo)"""
    
    def __init__(self, db_manager=None, max_short_term: int = 50):
        self.db_manager = db_manager
        self.short_term_memory: List[Dict] = []
        self.max_short_term = max_short_term
        logger.info(f"✓ MemoryManager inicializado")
    
    def add_to_short_term(self, content: str, metadata: Dict = None):
        memory_item = {
            "id": len(self.short_term_memory),
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.short_term_memory.append(memory_item)
        if len(self.short_term_memory) > self.max_short_term:
            self.short_term_memory.pop(0)
        return memory_item["id"]
    
    def get_short_term_memory(self, limit: int = 10) -> List[Dict]:
        return self.short_term_memory[-limit:]
    
    def clear_short_term(self):
        count = len(self.short_term_memory)
        self.short_term_memory.clear()
        logger.info(f"🗑️  Memoria limpiada ({count} items)")
    
    def get_stats(self) -> Dict:
        return {
            "short_term_items": len(self.short_term_memory),
            "short_term_capacity": self.max_short_term,
            "usage_percentage": round((len(self.short_term_memory) / self.max_short_term) * 100, 2),
        }
    
    def __repr__(self) -> str:
        return f"MemoryManager({len(self.short_term_memory)}/{self.max_short_term})"
''')
    
    # 3. brain/context_manager.py
    crear_archivo('brain/context_manager.py', '''from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
import logging

logger = logging.getLogger(__name__)

class ContextManager:
    """Gestor de contexto conversacional"""
    
    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.turns: deque = deque(maxlen=max_turns)
        self.current_intent = None
        self.current_entities = {}
        logger.info(f"✓ ContextManager inicializado")
    
    def add_turn(self, role: str, content: str, metadata: Dict = None):
        self.turns.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
    
    def get_conversation_history(self, format: str = "dict") -> List:
        if format == "messages":
            return [{"role": t["role"], "content": t["content"]} for t in self.turns]
        return list(self.turns)
    
    def set_intent(self, intent: str):
        self.current_intent = intent
    
    def get_intent(self) -> Optional[str]:
        return self.current_intent
    
    def clear(self):
        self.turns.clear()
        self.current_intent = None
    
    def __len__(self) -> int:
        return len(self.turns)
    
    def __repr__(self) -> str:
        return f"ContextManager(turns={len(self.turns)}/{self.max_turns})"
''')
    
    # 4. core/event_bus.py
    crear_archivo('core/event_bus.py', '''import logging
from typing import Callable, Dict, List
from threading import Lock
from collections import defaultdict

logger = logging.getLogger(__name__)

class EventBus:
    """Bus central de eventos"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = Lock()
        logger.info("✓ EventBus inicializado")
    
    def subscribe(self, event_name: str, callback: Callable):
        with self._lock:
            self._subscribers[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable):
        with self._lock:
            if event_name in self._subscribers:
                try:
                    self._subscribers[event_name].remove(callback)
                except ValueError:
                    pass
    
    def publish(self, event_name: str, event_data: Dict = None):
        with self._lock:
            if event_name in self._subscribers:
                subscribers = self._subscribers[event_name].copy()
            else:
                subscribers = []
        
        logger.debug(f"📢 {event_name}")
        for callback in subscribers:
            try:
                callback(event_data or {})
            except Exception as e:
                logger.error(f"Error en callback: {e}")
''')
    
    # 5. ai/intent_parser.py
    crear_archivo('ai/intent_parser.py', '''import re
import logging
from typing import Dict
from enum import Enum

logger = logging.getLogger(__name__)

class IntentType(Enum):
    QUESTION = "question"
    CHAT = "chat"
    COMMAND = "command"
    SEARCH = "search"
    UNKNOWN = "unknown"

class IntentParser:
    """Parser de intenciones"""
    
    def __init__(self):
        self.question_words = [
            "qué", "cuál", "cuáles", "cuándo", "dónde", 
            "quién", "cuánto", "cómo", "por qué"
        ]
        logger.info("✓ IntentParser inicializado")
    
    def parse(self, text: str) -> Dict:
        text_lower = text.lower().strip()
        
        # Detectar tipo
        if text_lower.endswith("?") or any(q in text_lower for q in self.question_words):
            intent_type = IntentType.QUESTION
            action = "answer_question"
            confidence = 0.95
        else:
            intent_type = IntentType.CHAT
            action = "chat"
            confidence = 0.7
        
        return {
            "type": intent_type.value,
            "action": action,
            "parameters": {},
            "entities": [],
            "confidence": confidence,
            "original_text": text
        }
''')
    
    # 6. ai/ai_router.py
    crear_archivo('ai/ai_router.py', '''import asyncio
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AIRouter:
    """Enrutador de IA (online/offline)"""
    
    def __init__(self, state_manager, event_bus):
        self.state_manager = state_manager
        self.event_bus = event_bus
        logger.info("✓ AIRouter inicializado")
    
    async def get_response(self, user_input: str, conversation_history: List[Dict],
                          intent: Dict, context: Dict) -> str:
        is_online = self.state_manager.is_online()
        mode = "ONLINE" if is_online else "OFFLINE"
        logger.info(f"🤖 IA {mode}")
        
        # Simulación
        await asyncio.sleep(0.1)
        return f"Respondiendo a: '{user_input}'"
''')
    
    # 7. database/db_manager.py
    crear_archivo('database/db_manager.py', '''import logging

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
''')
    
    # 8. core/orchestrator.py
    crear_archivo('core/orchestrator.py', '''import asyncio
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from core.event_bus import EventBus
from brain.state_manager import StateManager, KAGUMode, ConnectionMode
from brain.memory_manager import MemoryManager
from brain.context_manager import ContextManager
from ai.intent_parser import IntentParser
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class Orchestrator:
    """🧠 CEREBRO DE KAGU - Orquestador central"""
    
    def __init__(self):
        logger.info("="*70)
        logger.info("🧠 INICIALIZANDO ORCHESTRATOR")
        logger.info("="*70)
        
        # Componentes
        self.event_bus = EventBus()
        self.state_manager = StateManager()
        self.memory_manager = MemoryManager()
        self.context_manager = ContextManager(max_turns=20)
        self.db_manager = DatabaseManager("data/kagu.db")
        self.memory_manager.db_manager = self.db_manager
        self.intent_parser = IntentParser()
        
        # Sesión
        self.session_id = str(uuid.uuid4())
        self.state_manager.start_session(self.session_id)
        self.ai_router = None
        
        logger.info(f"✅ ORCHESTRATOR LISTO")
        logger.info(f"   Session: {self.session_id[:12]}...")
        logger.info(f"   Modo: {self.state_manager.get_mode().value}")
        logger.info(f"="*70)
    
    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Procesa input del usuario"""
        
        logger.info(f"\\n{'='*70}")
        logger.info(f"👤 USER: {user_input}")
        logger.info(f"{'='*70}")
        
        # 1. Escuchar
        self.state_manager.set_mode(KAGUMode.LISTENING)
        self.context_manager.add_turn("user", user_input)
        self.memory_manager.add_to_short_term(user_input, {"role": "user"})
        
        # 2. Parsear
        intent_result = self.intent_parser.parse(user_input)
        logger.info(f"📊 Intent: {intent_result['type']} | Confidence: {intent_result['confidence']:.0%}")
        
        try:
            # 3. Pensar
            self.state_manager.set_mode(KAGUMode.THINKING)
            
            # 4. Obtener respuesta
            if intent_result['type'] in ['question', 'chat']:
                if self.ai_router:
                    response = await self.ai_router.get_response(
                        user_input,
                        self.context_manager.get_conversation_history(format="messages"),
                        intent_result,
                        self.state_manager.get_full_context()
                    )
                else:
                    response = "AI Router no disponible"
            else:
                response = "Comando procesado"
            
            # 5. Guardar
            self.context_manager.add_turn("assistant", response)
            self.memory_manager.add_to_short_term(response, {"role": "assistant"})
            
            # 6. Hablar
            self.state_manager.set_mode(KAGUMode.SPEAKING)
            
            result = {
                "status": "success",
                "response": response,
                "session_id": self.session_id,
                "intent": intent_result['type'],
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"🤖 KAGU: {response[:80]}...")
            return result
        
        except Exception as e:
            logger.error(f"❌ ERROR: {e}", exc_info=True)
            self.state_manager.set_mode(KAGUMode.ERROR)
            return {
                "status": "error",
                "message": str(e),
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Estado del sistema"""
        return {
            "session_id": self.session_id,
            "mode": self.state_manager.get_mode().value,
            "connection": self.state_manager.get_connection_mode().value,
            "is_online": self.state_manager.is_online(),
            "memory": self.memory_manager.get_stats(),
            "context_turns": len(self.context_manager)
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """Historial de conversación"""
        return self.context_manager.get_conversation_history(format="dict")
    
    def shutdown(self):
        """Apagar KAGU"""
        logger.info("🔴 Apagando KAGU...")
        self.state_manager.end_session()
        logger.info("✓ KAGU finalizado")
''')
    
    print("\n✅ TODOS LOS ARCHIVOS CREADOS\n")
    print("Ahora ejecuta: python main.py\n")

if __name__ == '__main__':
    main()