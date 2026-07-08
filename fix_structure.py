# fix_structure.py
import os
from pathlib import Path

def crear_archivo(ruta, contenido):
    """Crea un archivo si no existe"""
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(ruta):
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"✓ CREADO: {ruta}")
    else:
        print(f"✓ EXISTE: {ruta}")

# ===== BRAIN =====
crear_archivo('brain/__init__.py', '')

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
    def __init__(self):
        self.lock = threading.RLock()
        self._mode = KAGUMode.SLEEPING
        self._connection_mode = ConnectionMode.ONLINE
        self._active_session_id = None
        self._last_activity = datetime.now()
        self._global_context = {"user_name": "Usuario"}
        self._state_callbacks = {}
        logger.info("✓ StateManager")
    
    def set_mode(self, new_mode: KAGUMode):
        with self.lock:
            if self._mode != new_mode:
                self._mode = new_mode
                self._last_activity = datetime.now()
    
    def get_mode(self) -> KAGUMode:
        with self.lock:
            return self._mode
    
    def set_connection_mode(self, mode: ConnectionMode):
        with self.lock:
            self._connection_mode = mode
    
    def get_connection_mode(self) -> ConnectionMode:
        with self.lock:
            return self._connection_mode
    
    def is_online(self) -> bool:
        with self.lock:
            return self._connection_mode != ConnectionMode.OFFLINE
    
    def start_session(self, session_id: str):
        with self.lock:
            self._active_session_id = session_id
    
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
''')

crear_archivo('brain/memory_manager.py', '''from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, db_manager=None, max_short_term: int = 50):
        self.db_manager = db_manager
        self.short_term_memory: List[Dict] = []
        self.max_short_term = max_short_term
        logger.info("✓ MemoryManager")
    
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
        self.short_term_memory.clear()
    
    def get_stats(self) -> Dict:
        return {
            "short_term_items": len(self.short_term_memory),
            "short_term_capacity": self.max_short_term,
        }
''')

crear_archivo('brain/context_manager.py', '''from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
import logging

logger = logging.getLogger(__name__)

class ContextManager:
    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.turns: deque = deque(maxlen=max_turns)
        self.current_intent = None
        self.current_entities = {}
        logger.info("✓ ContextManager")
    
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
''')

# ===== CORE =====
crear_archivo('core/__init__.py', '')

crear_archivo('core/event_bus.py', '''import logging
from typing import Callable, Dict, List
from threading import Lock
from collections import defaultdict

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = Lock()
        logger.info("✓ EventBus")
    
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
        
        for callback in subscribers:
            try:
                callback(event_data or {})
            except Exception as e:
                logger.error(f"Error: {e}")
''')

# ===== AI =====
crear_archivo('ai/__init__.py', '')

crear_archivo('ai/intent_parser.py', '''import logging
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
    def __init__(self):
        self.question_words = ["qué", "cuál", "cuáles", "cuándo", "dónde", "quién", "cuánto", "cómo", "por qué"]
        logger.info("✓ IntentParser")
    
    def parse(self, text: str) -> Dict:
        text_lower = text.lower().strip()
        
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

crear_archivo('ai/ai_router.py', '''import asyncio
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AIRouter:
    def __init__(self, state_manager, event_bus):
        self.state_manager = state_manager
        self.event_bus = event_bus
        logger.info("✓ AIRouter")
    
    async def get_response(self, user_input: str, conversation_history: List[Dict], intent: Dict, context: Dict) -> str:
        is_online = self.state_manager.is_online()
        mode = "ONLINE" if is_online else "OFFLINE"
        logger.info(f"IA: {mode}")
        await asyncio.sleep(0.1)
        return f"Respondiendo: {user_input}"
''')

# ===== DATABASE =====
crear_archivo('database/__init__.py', '')

crear_archivo('database/db_manager.py', '''import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        logger.info(f"✓ DatabaseManager: {db_path}")
    
    def add_conversation(self, session_id: str, role: str, content: str):
        pass
    
    def cleanup_old_data(self, days: int = 30):
        pass
''')

# ===== CONFIG =====
crear_archivo('config/__init__.py', '')

# ===== CORE ORCHESTRATOR =====
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
    def __init__(self):
        logger.info("🧠 ORCHESTRATOR INIT")
        
        self.event_bus = EventBus()
        self.state_manager = StateManager()
        self.memory_manager = MemoryManager()
        self.context_manager = ContextManager(max_turns=20)
        self.db_manager = DatabaseManager("data/kagu.db")
        self.memory_manager.db_manager = self.db_manager
        self.intent_parser = IntentParser()
        
        self.session_id = str(uuid.uuid4())
        self.state_manager.start_session(self.session_id)
        self.ai_router = None
        
        logger.info(f"✅ ORCHESTRATOR READY")
    
    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        logger.info(f"👤 {user_input}")
        
        self.state_manager.set_mode(KAGUMode.LISTENING)
        self.context_manager.add_turn("user", user_input)
        self.memory_manager.add_to_short_term(user_input, {"role": "user"})
        
        intent_result = self.intent_parser.parse(user_input)
        
        try:
            self.state_manager.set_mode(KAGUMode.THINKING)
            
            if intent_result['type'] in ['question', 'chat']:
                if self.ai_router:
                    response = await self.ai_router.get_response(
                        user_input,
                        self.context_manager.get_conversation_history(format="messages"),
                        intent_result,
                        self.state_manager.get_full_context()
                    )
                else:
                    response = "Sin IA"
            else:
                response = "OK"
            
            self.context_manager.add_turn("assistant", response)
            self.memory_manager.add_to_short_term(response, {"role": "assistant"})
            self.state_manager.set_mode(KAGUMode.SPEAKING)
            
            return {
                "status": "success",
                "response": response,
                "session_id": self.session_id,
                "intent": intent_result['type'],
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"ERROR: {e}")
            return {
                "status": "error",
                "message": str(e),
                "session_id": self.session_id,
            }
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "mode": self.state_manager.get_mode().value,
            "connection": self.state_manager.get_connection_mode().value,
            "is_online": self.state_manager.is_online(),
            "memory": self.memory_manager.get_stats(),
            "context_turns": len(self.context_manager)
        }
    
    def get_conversation_history(self) -> List[Dict]:
        return self.context_manager.get_conversation_history(format="dict")
    
    def shutdown(self):
        logger.info("SHUTDOWN")
        self.state_manager.end_session()
''')

print("\n" + "="*70)
print("✅ ESTRUCTURA COMPLETADA")
print("="*70)
print("\nAhora ejecuta: python main.py\n")
