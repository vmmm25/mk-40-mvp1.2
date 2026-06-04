# Guía de Mantenimiento — MARK XL (J.A.R.V.I.S.)

> **Versión:** 1.0  
> **Público:** Desarrolladores humanos e IA  
> **Propósito:** Mantener el proyecto saludable, seguro y funcional sin romper nada

---

## Índice

1. [Filosofía del Proyecto](#1-filosofía-del-proyecto)
2. [Reglas de Oro](#2-reglas-de-oro)
3. [Arquitectura y Dependencias](#3-arquitectura-y-dependencias)
4. [Flujo de Trabajo Seguro](#4-flujo-de-trabajo-seguro)
5. [DevOps y CI/CD](#5-devops-y-cicd)
6. [Ciberseguridad](#6-ciberseguridad)
7. [Machine Learning / Deep Learning](#7-machine-learning--deep-learning)
8. [Full Stack: Frontend](#8-full-stack-frontend)
9. [Full Stack: Backend](#9-full-stack-backend)
10. [Testing](#10-testing)
11. [Debugging: Cómo diagnosticar errores](#11-debugging)
12. [Checklist Pre-commit](#12-checklist-pre-commit)

---

## 1. Filosofía del Proyecto

### Principios Rectores

1. **Primero no dañar** — Cada cambio debe ser verificable y reversible.
2. **El usuario manda** — JARVIS existe para ayudar al usuario. No rompas su flujo.
3. **Consistencia > Creatividad** — Sigue los patrones existentes. No inventes nuevos patrones a menos que sea necesario.
4. **Pruebas primero** — Si no hay test para tu cambio, el cambio no existe.
5. **Logs, no prints** — Cada mensaje debe tener nivel, origen y contexto.

### Stack Tecnológico

| Capa | Tecnología | Versión mínima |
|------|-----------|----------------|
| Lenguaje | Python | 3.11 |
| UI | PyQt6 | 6.6.0 |
| LLMs | google-genai + REST | 0.2.2 |
| Vector Store | ChromaDB | 0.5.0 |
| Audio | sounddevice + numpy | 0.4.6 / 1.26.0 |
| Tests | pytest + pytest-asyncio | 8.0.0 / 0.23.0 |
| Seguridad | cryptography (Fernet) | 42.0.0 |
| STT | Whisper.cpp / Gemini API | — |
| TTS | Piper / Gemini TTS | — |

---

## 2. Reglas de Oro

### 🔴 NO HACER (violación = proyecto roto)

| # | Regla | Razón |
|---|-------|-------|
| 1 | **NO** usar `print()` para logging | Rompe el sistema de logs. Usar `logging.getLogger(__name__)` |
| 2 | **NO** guardar API keys en texto plano | Usar `crypto.KeyManager().encrypt()` |
| 3 | **NO** modificar `TOOL_DECLARATIONS` sin actualizar `TOOL_IMPLEMENTATIONS` | El asistente falla al llamar la tool |
| 4 | **NO** cambiar firmas de handlers sin actualizar `main.py:_execute_tool()` | Tool execution se rompe |
| 5 | **NO** eliminar imports de `__init__.py` sin verificar | Causa `ModuleNotFoundError` en cadena |
| 6 | **NO** ignorar tests existentes | `pytest tests/` debe pasar siempre |
| 7 | **NO** hardcodear rutas absolutas | Usar `Path(__file__).resolve().parent` |
| 8 | **NO** mezclar sync/async sin `iscoroutinefunction()` | Ver `base.py:execute_tool_call()` |
| 9 | **NO** modificar `config/api_keys.json` directamente en runtime | Usar `config_manager.save_config()` |
| 10 | **NO** asumir que el provider actual es Gemini | Usar `selected_provider` del config |

### 🟢 SÍ HACER (siempre)

| # | Regla | Ejemplo |
|---|-------|---------|
| 1 | Usar `logging` con `getLogger(__name__)` | `logger.info("Tool %s executed", name)` |
| 2 | Cifrar todo lo sensible | `_keyman.encrypt(api_key)` |
| 3 | Validar con tests | `pytest tests/test_mi_cambio.py -v` |
| 4 | Usar type hints | `def execute(args: dict, ui: JarvisUI) -> str:` |
| 5 | Documentar funciones públicas | Docstring con Args/Returns |
| 6 | Manejar errores con logging | `logger.exception("Fallo en X")` |
| 7 | Rutas relativas al proyecto | `BASE_DIR / "config" / "api_keys.json"` |
| 8 | Async para I/O | `await async_client.post(...)` |
| 9 | Verificar disponibilidad antes de usar | `if client.is_available():` |
| 10 | Cachear respuestas repetitivas | Usar `response_cache` en `base.py` |

---

## 3. Arquitectura y Dependencias

### Mapa de Dependencias Críticas

```
main.py
  ├── providers/__init__.py     → providers/base.py → core/cache.py, core/crypto.py
  ├── tools/declarations.py     → (solo datos, sin imports)
  ├── tools/registry.py         → tools/chat_tools/* (clases heredando de BaseTool)
  ├── tools/chat_tools/*        → actions/*, services/*, rag/*, agent/*
  ├── ui/__init__.py            → ui/main_window.py → ui/wave_canvas.py
  ├── memory/config_manager.py  → core/crypto.py
  └── memory/memory_manager.py  → (solo json)

CUIDADO: El registro de herramientas dinámico en registry.py carga automáticamente cada clase desde tools/chat_tools/.
CAMBIO en actions/* o services/* → requiere actualizar/verificar la clase correspondiente en tools/chat_tools/.
```

### Reglas de Importación

```python
# ✅ CORRECTO: imports explícitos y con ruta completa
from services.email.gmail_client import GmailClient
from memory.config_manager import load_config

# ❌ INCORRECTO: imports circulares o relativos profundos
from ..services.email.gmail_client import GmailClient  # NO
from services import *  # NO
```

### Patrón de Servicio (seguir siempre)

```python
# services/mi_servicio/mi_servicio_client.py
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MiServicioClient:
    """Descripción clara del servicio."""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self._authenticated = False
    
    def is_available(self) -> bool:
        """Verificar prerequisitos antes de usar."""
        return self._authenticated
    
    def execute(self, ...) -> dict:
        """Siempre devolver dict con estructura consistente."""
        try:
            # ... lógica
            return {"success": True, "data": ...}
        except Exception as e:
            logger.exception("MiServicio error")
            return {"success": False, "error": str(e)}
```

---

## 4. Flujo de Trabajo Seguro

### Para Humanos

```bash
# 1. Siempre empezar desde main actualizado
git checkout main
git pull origin main

# 2. Crear rama descriptiva
git checkout -b fix/descripcion-del-cambio
# O: git checkout -b feat/nueva-funcionalidad

# 3. Trabajar en cambios pequeños (1 archivo / 1 funcionalidad)

# 4. Testear antes de commit
python -m pytest tests/ -v --tb=short

# 5. Lint
flake8 . --max-line-length=120 --exclude=.venv,__pycache__

# 6. Commit con mensaje descriptivo
git commit -m "fix: corregir X en archivo Y"   # conventional commits

# 7. Push y PR
git push origin fix/descripcion-del-cambio
```

### Para IAs (Agentes Automáticos)

```
WORKFLOW_ORDER:
1. LEER: MAINTENANCE_GUIDE.md (este archivo)
2. LEER: PLAN_REFACTOR.md (si aplica)
3. RECOVER: ejecutar `node bin/eoc-script.js orchestrator-state recover --json`
4. ANALYZE: grep/glob para entender contexto
5. PLAN: verificar que el cambio no rompe dependencias
6. IMPLEMENT: cambios pequeños y verificables
7. TEST: python -m pytest tests/ -v --tb=short
8. COMMIT: solo si tests pasan
9. REPORT: resumir cambios, impacto, y riesgo residual

CRITICAL_FILES (no modificar sin permiso explícito):
- tools/declarations.py → rompe tool definitions de todos los providers
- tools/registry.py → rompe la carga automática y ejecución de tools
- tools/chat_tools/ → contiene las implementaciones individuales de tools
- main.py → rompe engine lifecycle
- ui/__init__.py → rompe import de toda la UI
- providers/__init__.py → rompe registro de providers
- memory/config_manager.py → rompe persistencia de config
```

---

## 5. DevOps y CI/CD

### Pipeline CI (GitHub Actions)

El pipeline ejecuta en cada push/PR:

```
1. lint:   flake8 + black --check
2. test:   pytest --cov=. (Windows + Linux, Python 3.11 + 3.12)
3. security: bandit + safety check
```

**Si el pipeline falla, NO hacer merge.** Investigar por qué.

### Docker

```bash
# Construir imagen
docker-compose build

# Ejecutar en desarrollo (código montado como volumen)
docker-compose up dev

# Ejecutar en producción
docker-compose up prod

# Ejecutar tests en contenedor
docker-compose run --rm dev python -m pytest tests/
```

### Pre-commit Hooks

```bash
# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

Los hooks atrapan automáticamente:
- Espacios al final de línea
- Archivos sin salto de línea final
- Errores de sintaxis Python
- `print()` statements
- Código mal formateado (black)

---

## 6. Ciberseguridad

### Política de Seguridad

```
CLASIFICACIÓN DE DATOS:
├── 🔴 CRÍTICOS → api_keys.json, master.key, tokens OAuth
├── 🟡 SENSIBLE → long_term.json (datos del usuario)
└── 🟢 PÚBLICO  → código fuente, tests, docs
```

### Reglas de Seguridad

| # | Regla | Implementación |
|---|-------|----------------|
| 1 | API keys siempre cifradas | `core/crypto.py` con Fernet AES |
| 2 | No commitear secrets | `.gitignore` bloquea `config/api_keys.json` |
| 3 | Sandbox para código generado | `core/sandbox.py` con modo `-I` aislado |
| 4 | Rate limiting en providers | `core/rate_limiter.py` (30 calls/min) |
| 5 | Validar input del usuario | Sanitizar antes de pasar a tools |
| 6 | No ejecutar comandos del LLM directamente | Siempre pasar por `sandbox.py` |
| 7 | OAuth2 tokens rotar periódicamente | Configurar refresh tokens |
| 8 | Logs sin datos sensibles | `logger.info("Email sent to %s", to)` OK. NO loguear bodies |

### Auditoría Rápida

```bash
# Buscar posibles fugas de secrets
bandit -r . -x .venv,__pycache__,tests

# Buscar API keys hardcodeadas
grep -rn "sk-or-\|AIzaSy\|ghp_" . --include="*.py" --include="*.json" --include="*.txt" --include="*.md" | grep -v .gitignore | grep -v __pycache__

# Buscar print() statements
grep -rn "^\s*print(" . --include="*.py" | grep -v __pycache__ | grep -v .venv
```

---

## 7. Machine Learning / Deep Learning

### Providers LLM

```
ARQUITECTURA DE PROVIDERS:
                    ┌──────────────┐
                    │ BaseProvider │  ← ABC en providers/base.py
                    └──────┬───────┘
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   GeminiProvider   OllamaProvider   OpenRouterProvider
   (Live Audio)     (Local)          (Cloud, 200+ models)
   
                    LMStudioProvider
                    (Local OpenAI-compat)

CADA PROVIDER DEBE:
├── Implementar chat()         → response Message
├── Implementar stream_chat()  → yield Message
├── Usar tool_chat_loop()      → heredado de BaseProvider
├── Manejar errores con logging
└── Reportar disponibilidad
```

### Buenas Prácticas ML/DL

```python
# 1. Siempre validar modelo antes de usar
if not provider.supports_tools:
    logger.warning("Provider %s does not support tools", provider.name)
    return "Lo siento, este proveedor no soporta herramientas."

# 2. Timeouts en todas las llamadas a LLM
try:
    response = await asyncio.wait_for(
        provider.chat(messages, tools),
        timeout=30.0  # segundos
    )
except asyncio.TimeoutError:
    logger.error("Provider %s timed out", provider.name)
    return "La solicitud tardó demasiado. Intenta de nuevo."

# 3. Fallback entre providers
backends = ["local", "gemini", "openai"]  # orden de prioridad
for backend in backends:
    try:
        result = await try_backend(backend, prompt)
        if result:
            return result
    except Exception as e:
        logger.warning("Backend %s failed: %s", backend, e)
        continue

# 4. Cachear respuestas repetitivas
cache_key = hashlib.md5(f"{model}:{prompt}".encode()).hexdigest()
cached = response_cache.get(cache_key)
if cached:
    return Message(**json.loads(cached))
```

### RAG (ChromaDB)

```python
# El RAG usa ChromaDB con embeddings de Ollama:
# 1. DocumentLoader → extrae texto de PDF/DOCX/TXT/CSV/código
# 2. EmbeddingService → genera embeddings vía Ollama API
# 3. DocumentIndexer → almacena en ChromaDB persistente
# 4. DocumentRetriever → búsqueda semántica

# Para re-indexar después de cambios:
from rag.indexer import DocumentIndexer
indexer = DocumentIndexer()
indexer.reindex_all()  # Reconstruye el índice completo
```

---

## 8. Full Stack: Frontend

### UI Architecture (PyQt6)

```
ESTRUCTURA UI OBJETIVO (post-refactor):
JarvisUI (main_window.py)
  ├── HUDWidget            → Estado, brain icon, animaciones
  ├── MetricsWidget        → CPU, RAM, GPU, red
  ├── LogPanel             → Chat log con scroll
  ├── AudioVisualizer      → WaveCanvas en tiempo real
  ├── FileDropHandler      → Drag & drop de archivos
  ├── ProviderSelector     → ComboBox de providers
  └── SettingsDialog       → ConfigToolbar transformado
       ├── APIKeysTab
       ├── AudioTab
       └── OllamaTab
```

### Reglas de UI

```python
# 1. Nunca bloquear el event loop de Qt
# ❌ INCORRECTO:
time.sleep(2)  # Congela la UI

# ✅ CORRECTO:
QTimer.singleShot(2000, lambda: hacer_algo())

# 2. Operaciones lentas en threads separados
# ❌ INCORRECTO:
result = llamada_lenta()  # Bloquea la UI

# ✅ CORRECTO:
threading.Thread(target=lambda: llamada_lenta(), daemon=True).start()

# 3. Actualizar UI desde el thread principal
# ❌ INCORRECTO (desde thread secundario):
label.setText("Hola")  # Crash

# ✅ CORRECTO:
label.setText.emit("Hola")  # Usar señales Qt
# O:
root.after(0, lambda: label.setText("Hola"))  # schedule en main thread

# 4. Estado visual siempre sincronizado con estado real
hud.set_state("LISTENING")  # → cambia color/animation/texto
assert hud.state == "LISTENING"

# 5. No hardcodear colores
# ❌ INCORRECTO:
label.setStyleSheet("color: #00ff88")

# ✅ CORRECTO:
from ui.theme import C
label.setStyleSheet(f"color: {C.TEXT_PRIMARY.name()}")
```

### Estilos y Tema

```python
# ui/theme.py define todos los colores del proyecto.
# NO agregar colores nuevos fuera de theme.py.

# Colores existentes:
C = {
    BG_DARK: "#0a0a1a",
    BG_MID: "#141428",
    TEXT_PRIMARY: "#00ff88",   # Verde neón
    TEXT_DIM: "#6666aa",       # Púrpura grisáceo
    ACCENT: "#ff00ff",         # Magenta
    WARNING: "#ffaa00",
    ERROR: "#ff0033",
}
```

---

## 9. Full Stack: Backend

### Servicios Externos

```python
# Todos los servicios siguen el mismo patrón:

class SomeService:
    """Template para cualquier servicio externo."""
    
    def __init__(self):
        self.config = load_config()
        self._client = None
        self._authenticated = False
    
    def is_available(self) -> bool:
        """¿Está configurado y funcional?"""
        return self._authenticated
    
    def is_configured(self) -> bool:
        """¿Tiene credenciales/config?"""
        return bool(self.config.get("some_key"))
    
    def _ensure_auth(self):
        """Autenticar si es necesario."""
        if not self._authenticated:
            self._authenticate()
    
    def execute(self, **kwargs) -> dict:
        """Punto de entrada principal.
        
        Returns:
            dict con "success": bool y datos o error.
        """
        try:
            self._ensure_auth()
            result = self._do_execute(**kwargs)
            return {"success": True, "data": result}
        except Exception as e:
            logger.exception("Service error")
            return {"success": False, "error": str(e)}
```

### Gestión de Configuración

```python
# memory/config_manager.py es el ÚNICO punto de entrada para config.
# NO leer api_keys.json directamente.

from memory.config_manager import load_config, save_config

# ✅ CORRECTO:
cfg = load_config()
api_key = cfg.get("gemini_api_key", "")

# ❌ INCORRECTO:
import json
api_key = json.loads(open("config/api_keys.json").read())["gemini_api_key"]
```

### Patrón de Tool / Herramienta (clase heredada de BaseTool)

Todas las herramientas se definen en clases independientes dentro de `tools/chat_tools/` y heredan de `BaseTool`.

```python
# tools/chat_tools/mi_herramienta_tool.py
import logging
from typing import Any
from tools.base import BaseTool
from services.mi_servicio.mi_servicio_client import MiServicioClient

logger = logging.getLogger(__name__)

class MiHerramientaTool(BaseTool):
    name = "mi_herramienta"
    description = "Descripción clara de lo que hace la herramienta."
    # Los parámetros deben coincidir exactamente con tools/declarations.py
    parameters = {
        "type": "OBJECT",
        "properties": {
            "param": {"type": "STRING", "description": "Parámetro requerido"}
        },
        "required": ["param"]
    }

    def execute(self, args: dict, ui: Any) -> str:
        """Siempre devolver string. Nunca lanzar excepción sin capturar."""
        try:
            # Validar args
            param = args.get("param")
            if not param:
                return "Parámetro 'param' requerido."

            # Ejecutar lógica a través de un servicio
            servicio = MiServicioClient()
            result = servicio.execute(param=param)

            # Devolver resultado formateado para el modelo
            if result.get("success"):
                return f"Operación exitosa: {result['data']}"
            return f"Error: {result.get('error', 'desconocido')}"

        except Exception as e:
            logger.exception("Error inesperado en MiHerramientaTool")
            return f"Error inesperado: {e}"
```

---

## 10. Testing

### Pirámide de Tests

```
         ╱╲
        ╱  ╲           E2E / Integración (5-10 tests)
       ╱    ╲          tool_chat_loop, provider switching
      ╱──────╲
     ╱        ╲        Unitarios de Servicios (20-30 tests)
    ╱          ╲       email, calendar, spotify, git, docker
   ╱────────────╲
  ╱              ╲     Unitarios de Core (100+ tests)
 ╱                ╲    providers, cache, crypto, sandbox, RAG
╱──────────────────╲
```

### Cómo Escribir Tests

```python
# tests/test_algo.py
import pytest
from unittest.mock import Mock, patch

# 1. Test básico
def test_something():
    result = my_function("input")
    assert result == "expected"

# 2. Test con mock (evitar llamadas reales a APIs)
def test_with_mock():
    with patch("services.mi_servicio.MiServicio._real_call") as mock_call:
        mock_call.return_value = {"success": True}
        client = MiServicio()
        result = client.execute()
        assert result["success"] is True

# 3. Test asíncrono
@pytest.mark.asyncio
async def test_async_thing():
    result = await my_async_function()
    assert "éxito" in result

# 4. Test con fixture
@pytest.fixture
def mock_ui():
    ui = Mock()
    ui.write_log = Mock()
    return ui

def test_handler_with_fixture(mock_ui):
    result = handle_algo({"param": "test"}, mock_ui)
    assert "éxito" in result
    mock_ui.write_log.assert_called_once()
```

### Comandos Útiles

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v --tb=short

# Tests específicos
python -m pytest tests/test_crypto.py -v

# Tests con nombre específico
python -m pytest tests/ -k "test_encrypt"

# Coverage
python -m pytest tests/ -v --cov=. --cov-report=html

# Tests rápidos (saltar lint)
python -m pytest tests/ -v --tb=short -q
```

---

## 11. Debugging

### Cómo Diagnosticar Errores

```
ERROR "ModuleNotFoundError: No module named 'services'"
    → Verificar services/__init__.py existe
    → Verificar imports en la tool correspondiente en tools/chat_tools/

ERROR "Tool 'X' failed: ..."
    → Verificar TOOL_DECLARATIONS tiene la tool
    → Verificar TOOL_IMPLEMENTATIONS tiene el handler
    → Revisar handler por excepciones

ERROR "Provider 'X' not found"
    → Verificar providers/__init__.py importa el provider
    → Verificar PROVIDER_REGISTRY tiene el nombre

ERROR "No module named 'rag'"
    → Verificar rag/__init__.py existe
    → Verificar requirements.txt tiene chromadb

ERROR en importaciones circulares
    → Verificar A importa B y B importa A
    → Solución: mover import dentro de función (lazy import)

ERROR "api_keys.json not found"
    → Ejecutar desde directorio raíz del proyecto
    → Verificar config/ existe
```

### Logging de Diagnóstico

```bash
# Activar DEBUG temporalmente
$env:LOG_LEVEL="DEBUG"
python main.py

# Ver logs en tiempo real
Get-Content logs/jarvis.log -Tail 50 -Wait

# Filtrar errores
Select-String -Path logs/jarvis.log -Pattern "ERROR|CRITICAL"

# Ver traces de herramientas
Select-String -Path logs/jarvis.log -Pattern "Tool called|Tool result"
```

### Puntos de Control para IA

```
CUANDO LLEGUES A ESTE PROYECTO POR PRIMERA VEZ:

1. LEE: MAINTENANCE_GUIDE.md (este archivo)
2. LEE: PLAN_IMPLEMENTACION.md (plan original)
3. LEE: PLAN_REFACTOR.md (plan de mejora)
4. LEE: CHECKPOINT.md (estado actual conocido)
5. CORRE: python -m pytest tests/ -v --tb=short (ver estado actual)
6. CORRE: python -c "from tools.declarations import TOOL_DECLARATIONS; print(len(TOOL_DECLARATIONS))" (ver 34 tools)
7. VERIFICA: git status (rama actual, cambios sin commit)
8. PREGUNTA: ¿Qué cambió desde el último checkpoint?
```

---

## 12. Checklist Pre-commit

### Para cada cambio, verificar:

```
[ ] 1. Tests pasan: pytest tests/ -v --tb=short
[ ] 2. Lint: flake8 . --max-line-length=120 --exclude=.venv,__pycache__
[ ] 3. 0 print() statements en archivos modificados
[ ] 4. No hay secrets expuestos (API keys, tokens)
[ ] 5. Type hints agregados a funciones nuevas/modificadas
[ ] 6. Docstring en funciones públicas
[ ] 7. logging.getLogger(__name__) importado si hay logs nuevos
[ ] 8. imports organizados: estándar → terceros → locales
[ ] 9. No hay cambios en archivos no relacionados al PR
[ ] 10. Rutas relativas al proyecto (no absolutas)
[ ] 11. try/except con logger.exception() en handlers
[ ] 12. No hay código comentado (si no sirve, eliminarlo)
[ ] 13. Mensaje de commit con formato conventional commit
[ ] 14. Rama con nombre descriptivo (fix/ feat/ refactor/ docs/)
[ ] 15. Si es refactor: no cambia comportamiento observable
```

### Formato de Commit

```
tipo(alcance): descripción en presente imperativo

Tipos permitidos:
- feat:     Nueva funcionalidad
- fix:      Corrección de bug
- refactor: Cambio que no agrega funcionalidad ni corrige bug
- docs:     Cambios en documentación
- test:     Agregar o modificar tests
- chore:    Tareas de mantenimiento (deps, CI, config)
- security: Mejoras de seguridad
- perf:     Mejoras de rendimiento

Ejemplos:
  feat(services): add Outlook email client
  fix(rag): handle empty documents in indexer
  refactor(main): extract audio utilities to engine/audio.py
  docs: add maintenance guide for AI agents
  test(crypto): add encryption roundtrip tests
  security: encrypt API keys at rest with Fernet
  chore(deps): update google-genai to 0.3.0
```

---

## Apéndice: Comandos Rápidos

```bash
# === DESARROLLO ===
python main.py                          # Iniciar JARVIS
python setup.py                         # Instalar dependencias
python -m pytest tests/ -v             # Tests
flake8 . --max-line-length=120          # Lint
black --line-length=120 .               # Formatear

# === GIT ===
git status                              # Estado
git log --oneline -10                   # Últimos 10 commits
git diff --stat                         # Archivos modificados

# === DEPURACIÓN ===
python -c "import ast; ast.parse(open('file.py').read())"  # Check sintaxis
python -c "from tools.declarations import TOOL_DECLARATIONS; print(len(TOOL_DECLARATIONS))"  # Ver tools

# === SEGURIDAD ===
bandit -r . -x .venv,__pycache__,tests
safety check -r requirements.txt

# === DOCKER ===
docker-compose build
docker-compose up
docker-compose run --rm dev python -m pytest tests/
```

---

> **Última actualización:** 2026-06-04  
> **Mantenido por:** El equipo de desarrollo de MARK XL  
> **Para reportar problemas:** Abrir issue en el repositorio
