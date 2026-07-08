# tests/test_orchestrator.py

import pytest
import asyncio
from core.orchestrator import Orchestrator
from brain.state_manager import KAGUMode

@pytest.fixture
def orchestrator():
    return Orchestrator()

@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    """Test: Orchestrator se inicializa correctamente"""
    assert orchestrator.session_id is not None
    assert orchestrator.state_manager.get_mode() == KAGUMode.SLEEPING
    assert len(orchestrator.context_manager) == 0

@pytest.mark.asyncio
async def test_process_input(orchestrator):
    """Test: Procesa entrada del usuario"""
    response = await orchestrator.process_user_input("hola")
    
    assert response['status'] == 'success'
    assert 'response' in response
    assert 'session_id' in response
    assert len(orchestrator.context_manager) == 2  # user + assistant

@pytest.mark.asyncio
async def test_conversation_history(orchestrator):
    """Test: Mantiene historial de conversación"""
    await orchestrator.process_user_input("hola")
    await orchestrator.process_user_input("¿cómo estás?")
    
    history = orchestrator.get_conversation_history()
    assert len(history) == 4  # 2 user + 2 assistant

def test_memory_manager(orchestrator):
    """Test: Memory Manager funciona"""
    orchestrator.memory_manager.add_to_short_term("test content")
    
    assert len(orchestrator.memory_manager.short_term_memory) == 1
    
    short_term = orchestrator.memory_manager.get_short_term_memory()
    assert short_term[0]['content'] == "test content"

def test_event_bus(orchestrator):
    """Test: Event Bus funciona"""
    received_events = []
    
    def callback(data):
        received_events.append(data)
    
    orchestrator.event_bus.subscribe("test_event", callback)
    orchestrator.event_bus.publish("test_event", {"data": "test"})
    
    assert len(received_events) == 1
    assert received_events[0]['data'] == 'test'