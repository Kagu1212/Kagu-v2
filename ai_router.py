import asyncio
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