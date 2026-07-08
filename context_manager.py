# brain/context_manager.py

from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque
import logging

logger = logging.getLogger(__name__)

class ConversationTurn:
    """Representa un turno en la conversación"""
    
    def __init__(self, role: str, content: str, metadata: Dict = None):
        self.role = role
        self.content = content
        self.timestamp = datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

class ContextManager:
    """Gestor de contexto conversacional (ventana deslizante)"""
    
    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.turns: deque = deque(maxlen=max_turns)
        self.current_intent = None
        self.current_entities = {}
        self.conversation_topic = None
        
        logger.info(f"✓ ContextManager inicializado (max_turns={max_turns})")
    
    def add_turn(self, role: str, content: str, metadata: Dict = None):
        """Añade un turno a la conversación"""
        turn = ConversationTurn(role, content, metadata)
        self.turns.append(turn)
        logger.debug(f"💬 Turno añadido: {role} - {content[:50]}...")
    
    def get_conversation_history(self, format: str = "dict") -> List:
        """Obtiene el historial de conversación"""
        if format == "dict":
            return [turn.to_dict() for turn in self.turns]
        elif format == "messages":
            return [
                {"role": turn.role, "content": turn.content}
                for turn in self.turns
            ]
        return list(self.turns)
    
    def get_last_user_message(self) -> Optional[str]:
        """Obtiene el último mensaje del usuario"""
        for turn in reversed(self.turns):
            if turn.role == "user":
                return turn.content
        return None
    
    def get_conversation_summary(self) -> str:
        """Resumen de la conversación actual"""
        if not self.turns:
            return "Sin historial"
        
        summary = f"📖 CONTEXTO DE CONVERSACIÓN\n"
        summary += f"  Turnos: {len(self.turns)}/{self.max_turns}\n"
        summary += f"  Tema: {self.conversation_topic or 'General'}\n"
        summary += f"  Intención: {self.current_intent or 'Desconocida'}\n"
        
        if self.current_entities:
            summary += f"  Entidades: {', '.join(self.current_entities.keys())}\n"
        
        return summary
    
    def set_intent(self, intent: str):
        """Establece la intención actual"""
        self.current_intent = intent
        logger.debug(f"🎯 Intención: {intent}")
    
    def get_intent(self) -> Optional[str]:
        """Obtiene la intención actual"""
        return self.current_intent
    
    def set_entities(self, entities: Dict):
        """Establece las entidades extraídas"""
        self.current_entities = entities
        logger.debug(f"🏷️ Entidades: {entities}")
    
    def get_entities(self) -> Dict:
        """Obtiene las entidades"""
        return self.current_entities.copy()
    
    def clear(self):
        """Limpia el contexto"""
        self.turns.clear()
        self.current_intent = None
        self.current_entities = {}
        self.conversation_topic = None
        logger.info("🗑️ Contexto limpiado")
    
    def __len__(self) -> int:
        return len(self.turns)
    
    def __repr__(self) -> str:
        return f"ContextManager(turns={len(self.turns)}, intent={self.current_intent})"