import asyncio
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
        
        logger.info(f"\n{'='*70}")
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