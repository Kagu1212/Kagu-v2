import logging
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