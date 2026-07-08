# tests/test_phase_0.py

import pytest
import asyncio
from core.orchestrator import Orchestrator
from ai.intent_parser import IntentParser
from ai.ai_router import AIRouter
from brain.state_manager import KAGUMode, ConnectionMode

@pytest.fixture
def orchestrator():
    """Fixture para crear orchestrator"""
    orch = Orchestrator()
    orch.ai_router = AIRouter(orch.state_manager, orch.event_bus)
    return orch

@pytest.fixture
def intent_parser():
    """Fixture para parser"""
    return IntentParser()

class TestIntentParser:
    """Tests para IntentParser"""
    
    def test_question_detection(self, intent_parser):
        """Test: Detecta preguntas"""
        result = intent_parser.parse("¿Cuál es la capital de Francia?")
        assert result['type'] == 'question'
        assert result['action'] == 'answer_question'
        assert result['confidence'] > 0.9
    
    def test_command_detection(self, intent_parser):
        """Test: Detecta comandos"""
        result = intent_parser.parse("Abre VS Code")
        assert result['type'] == 'command'
        assert result['action'] == 'launch_app'
        assert result['parameters']['app_name'] == 'code'
    
    def test_chat_detection(self, intent_parser):
        """Test: Detecta chat"""
        result = intent_parser.parse("Hola, ¿cómo estás?")
        assert result['type'] in ['chat', 'question']
    
    def test_search_command(self, intent_parser):
        """Test: Detecta búsquedas"""
        result = intent_parser.parse("Busca Python tutorial")
        assert result['type'] == 'command'
        assert result['action'] == 'search'

class TestOrchestrator:
    """Tests para Orchestrator"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test: Orchestrator se inicializa"""
        assert orchestrator.session_id is not None
        assert orchestrator.state_manager.get_mode() == KAGUMode.SLEEPING
        assert len(orchestrator.context_manager) == 0
    
    @pytest.mark.asyncio
    async def test_process_simple_input(self, orchestrator):
        """Test: Procesa input simple"""
        response = await orchestrator.process_user_input("¿Hola?")
        
        assert response['status'] == 'success'
        assert 'response' in response
        assert len(orchestrator.context_manager) == 2  # user + assistant
    
    @pytest.mark.asyncio
    async def test_conversation_history(self, orchestrator):
        """Test: Mantiene historial"""
        await orchestrator.process_user_input("Hola")
        await orchestrator.process_user_input("¿Cómo estás?")
        
        history = orchestrator.get_conversation_history()
        assert len(history) == 4  # 2 user + 2 assistant
    
    @pytest.mark.asyncio
    async def test_memory_persistence(self, orchestrator):
        """Test: Memoria funciona"""
        await orchestrator.process_user_input("Test")
        
        stats = orchestrator.memory_manager.get_stats()
        assert stats['short_term_items'] >= 2

class TestStateManager:
    """Tests para StateManager"""
    
    def test_mode_changes(self):
        from brain.state_manager import StateManager
        
        state = StateManager()
        
        assert state.get_mode() == KAGUMode.SLEEPING
        
        state.set_mode(KAGUMode.THINKING)
        assert state.get_mode() == KAGUMode.THINKING
    
    def test_context_management(self):
        from brain.state_manager import StateManager
        
        state = StateManager()
        
        state.set_context("user_name", "Juan")
        assert state.get_context("user_name") == "Juan"
    
    def test_connection_modes(self):
        from brain.state_manager import StateManager
        
        state = StateManager()
        
        assert state.is_online()
        
        state.set_connection_mode(ConnectionMode.OFFLINE)
        assert not state.is_online()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])