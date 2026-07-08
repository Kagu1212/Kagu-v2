# 🧠 KAGU - Persistent Intelligent Operating System

Un asistente de IA persistente para Windows que funciona 24/7 en segundo plano.

## 📊 Estado del Proyecto

### ✅ FASE 0: CEREBRO (Completado)

- [x] EventBus (comunicación entre módulos)
- [x] StateManager (gestión de estado global)
- [x] MemoryManager (memoria corto/largo plazo)
- [x] ContextManager (contexto conversacional)
- [x] Orchestrator (orquestador central)
- [x] IntentParser (parsear intenciones del usuario)
- [x] AIRouter (enrutamiento online/offline)

**Estado:** Funcional ✅

### ⏳ FASE 1: CORAZÓN (En desarrollo)

- [ ] Integración Claude API
- [ ] Integración OpenAI API
- [ ] Mejora Intent Parser
- [ ] Tests unitarios

### ⏳ FASE 2: SISTEMA NERVIOSO (Próximo)

- [ ] Voice (STT/TTS)
- [ ] Input Router
- [ ] Action Executor
- [ ] System Monitor

### ⏳ FASE 3: CUERPO (Próximo)

- [ ] PyQt6 Desktop App
- [ ] Chat Interface
- [ ] Avatar Flotante
- [ ] Settings Panel

## 🚀 Quick Start

### Requisitos

- Python 3.9+
- Windows 10+

### Instalación

```bash
git clone https://github.com/tuusuario/KAGU_v2.git
cd KAGU_v2

# Crear venv
python -m venv venv
source venv/Scripts/activate  # Windows

# Instalar dependencias
pip install -r requirements.txt