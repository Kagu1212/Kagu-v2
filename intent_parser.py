import re
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