# main.py

import asyncio
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/kagu.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from core.orchestrator import Orchestrator
from ai.ai_router import AIRouter

async def main():
    """Función principal"""
    
    logger.info("="*80)
    logger.info("🧠 KAGU AI - CEREBRO EN FUNCIONAMIENTO - FASE 0")
    logger.info("="*80)
    
    # 1. Crear orchestrator
    try:
        orchestrator = Orchestrator()
    except Exception as e:
        logger.error(f"✗ Error inicializando orchestrator: {e}")
        return
    
    # 2. Inicializar AI Router
    try:
        ai_router = AIRouter(orchestrator.state_manager, orchestrator.event_bus)
        orchestrator.ai_router = ai_router
        logger.info("✓ AI Router listo")
    except Exception as e:
        logger.error(f"✗ Error inicializando AI Router: {e}")
        return
    
    # Demo interactivo
    print("\n" + "="*80)
    print("🤖 KAGU CEREBRO - MODO INTERACTIVO")
    print("="*80)
    print("\nComandos disponibles:")
    print("  - 'salir': Terminar")
    print("  - 'status': Ver estado del sistema")
    print("  - 'memory': Ver memoria")
    print("  - 'history': Ver historial de conversación")
    print("  - 'clear': Limpiar contexto")
    print("  - O escribe cualquier mensaje para chatear")
    print("="*80 + "\n")
    
    while True:
        try:
            user_input = input("👤 TÚ: ").strip()
            
            if not user_input:
                continue
            
            # ===== COMANDOS ESPECIALES =====
            if user_input.lower() == "salir":
                logger.info("Saliendo...")
                break
            
            elif user_input.lower() == "status":
                import json
                status = orchestrator.get_status()
                print(f"\n📊 ESTADO DEL SISTEMA:")
                print(json.dumps(status, indent=2, ensure_ascii=False))
                print()
                continue
            
            elif user_input.lower() == "memory":
                import json
                memory_stats = orchestrator.memory_manager.get_stats()
                short_term = orchestrator.memory_manager.get_short_term_memory(limit=5)
                
                print(f"\n💾 MEMORIA:")
                print(f"  {json.dumps(memory_stats, indent=2, ensure_ascii=False)}")
                print(f"\n  Últimos recuerdos:")
                for item in short_term:
                    role = item.get('metadata', {}).get('role', 'unknown')
                    content = item['content'][:60]
                    print(f"    [{role}] {content}...")
                print()
                continue
            
            elif user_input.lower() == "history":
                history = orchestrator.get_conversation_history()
                print("\n📜 HISTORIAL DE CONVERSACIÓN:")
                for turn in history:
                    role = turn['role'].upper()
                    content = turn['content'][:80]
                    print(f"  {role}: {content}...")
                print()
                continue
            
            elif user_input.lower() == "clear":
                orchestrator.context_manager.clear()
                orchestrator.memory_manager.clear_short_term()
                print("\n🗑️ Contexto limpiado\n")
                continue
            
            elif user_input.lower() == "debug":
                print(f"\n🔧 DEBUG INFO:")
                print(f"  Session: {orchestrator.session_id}")
                print(f"  Mode: {orchestrator.state_manager.get_mode().value}")
                print(f"  Connection: {orchestrator.state_manager.get_connection_mode().value}")
                print(f"  Context turns: {len(orchestrator.context_manager)}")
                print()
                continue
            
            # ===== PROCESAR INPUT NORMAL =====
            response = await orchestrator.process_user_input(user_input)
            
            if response['status'] == 'success':
                print(f"\n🤖 KAGU: {response['response']}\n")
            else:
                print(f"\n⚠️ ERROR: {response['message']}\n")
        
        except KeyboardInterrupt:
            logger.info("\nInterrupción por usuario")
            break
        
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"✗ Error: {e}\n")
    
    # Shutdown
    orchestrator.shutdown()
    logger.info("✓ KAGU finalizado")
    print("\n¡Hasta luego! 👋\n")

if __name__ == "__main__":
    asyncio.run(main())