# PLAN DE REFACTORIZACIÓN — MARK XL (J.A.R.V.I.S. MARK-40)

> **Versión:** 2.0  
> **Fecha:** 2026-06-04  
> **Objetivo:** Transformar MARK XL en un proyecto mantenible, seguro y escalable

---

## 📋 Tabla de Contenidos

1. [Arquitectura Objetivo](#1-arquitectura-objetivo)
2. [Fase 0: Quick Wins — Seguridad y Logging](#2-fase-0-quick-wins)
3. [Fase 1: Refactor de main.py](#3-fase-1-refactor-main)
4. [Fase 2: Refactor de UI](#4-fase-2-refactor-ui)
5. [Fase 3: Desacoplar Actions](#5-fase-3-refactor-actions)
6. [Fase 4: Desacoplar Tools → Tool Registry](#6-fase-4-desacoplar-tools)
7. [Fase 5: Tests de Integración y UI](#7-fase-5-tests)
8. [Fase 6: Infraestructura DevOps](#8-fase-6-devops)
9. [Fase 7: UX/UI Avanzado](#9-fase-7-ux)
10. [Checklist de Progreso](#10-checklist)

---

## 1. Arquitectura Objetivo

### Estado Actual (Monolito)
```
main.py (1197 lines)
├── JarvisLive (Gemini Live Audio)
├── JarvisChat (text + voice)
├── Audio utilities
├── STT (Whisper/Gemini)
├── TTS (Piper/Gemini)
├── Tool execution
└── Provider factory

ui/main_window.py (1717 lines)
├── System metrics
├── HUD rendering
├── Chat log
├── File drop
├── Audio visualization
├── Settings management
└── Provider switching
```

### Estado Deseado (Modular)
```
engine/                     # ← refactor de main.py
├── __init__.py
├── base.py                 # JarvisEngine ABC
├── live.py                 # JarvisLive
├── chat.py                 # JarvisChat
├── audio.py                # Audio utilities
└── factory.py              # Provider factory

ui/                         # ← refactor de main_window.py
├── __init__.py
├── main_window.py          # Solo orquestación (~300 lines)
├── hud.py                  # HUD rendering
├── metrics.py              # System metrics
├── log_panel.py            # Chat log
├── file_drop.py            # Drag & drop
├── audio_viz.py            # Wave visualization
└── dialogs/
    ├── settings.py         # Settings dialog
    └── about.py            # About dialog

tools/                      # ← refactor de handlers.py
├── __init__.py             # ToolRegistry class
├── declarations.py         # 34 tool definitions
├── base.py                 # BaseTool ABC
├── registry.py             # Tool registry + dispatcher
├── git_tool.py
├── docker_tool.py
├── spotify_tool.py
├── calendar_tool.py
├── image_gen_tool.py
├── smart_home_tool.py
├── database_tool.py
└── ... (one file per domain)

services/                   # ← ya bien, expandir
├── __init__.py
├── steam/                  # Extraer de game_updater.py
├── epic/                   # Extraer de game_updater.py
└── ...
```

---

## 2. Fase 0: Quick Wins

**Duración:** 1 día  
**Prioridad:** 🔴 Crítica

### 0.1 Activar Cifrado de API Keys

**Archivos:** `core/crypto.py`, `memory/config_manager.py`

**Qué hacer:** Integrar `KeyManager` en el guardado/carga de config para que las keys viajen cifradas.

```python
# memory/config_manager.py
from core.crypto import KeyManager

_keyman = KeyManager()

def save_config(data: dict) -> None:
    # Cifrar keys sensibles antes de guardar
    for key_field in ("gemini_api_key", "openrouter_api_key"):
        if key_field in data and data[key_field]:
            if not data[key_field].startswith("gAAAAA"):  # ya cifrado?
                data[key_field] = _keyman.encrypt(data[key_field])
    # ... resto del save normal

def load_config() -> dict:
    data = _raw_load()
    for key_field in ("gemini_api_key", "openrouter_api_key"):
        if key_field in data and data[key_field]:
            try:
                data[key_field] = _keyman.decrypt(data[key_field])
            except Exception:
                pass  # ya está en texto plano
    return data
```

**Verificación:**
- [ ] `api_keys.json` almacena keys cifradas (empiezan con `gAAAAA`)
- [ ] Login flow sigue funcionando
- [ ] Si se corrompe la master key, mostrar error claro al usuario

### 0.2 print() → logging estructurado

**Archivos afectados:** Los 32 archivos identificados con `print()`  
**Script de migración:** Usar el archivo `scripts/migrate_print_to_logging.py`

```python
# Ejemplo de reemplazo en main.py:
# ANTES:
print(f"[JARVIS] 🔧 {name}  {args}")
# DESPUÉS:
logger.info("Tool called: %s args=%s", name, args)
```

**Reglas de mapeo:**
| `print()` original | Reemplazar con |
|---|---|
| `print("[JARVIS] 🔧 ...")` | `logger.info(...)` |
| `print("[JARVIS] ⚠️ ...")` | `logger.warning(...)` |
| `print("[JARVIS] ❌ ...")` | `logger.error(...)` |
| `print("[JARVIS] 🔴 ...")` | `logger.critical(...)` |
| `print("[JARVIS] 🐛 ...")` | `logger.debug(...)` |
| `traceback.print_exc()` | `logger.exception(...)` |

**Verificación:**
- [ ] 0 `print()` en archivos de producción
- [ ] Logs se escriben en `logs/jarvis.log` con rotación
- [ ] Logs tienen formato: `2026-06-04 14:30:00 [main] INFO: Tool called: ...`
- [ ] Navegación por niveles (DEBUG < INFO < WARNING < ERROR)

### 0.3 CI/CD Básico

**Nuevo archivo:** `.github/workflows/test.yml`

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-asyncio pytest-mock pytest-cov
      - run: python -m pytest tests/ -v --tb=short --cov=.
      - run: python -m flake8 . --count --max-line-length=120 --statistics
```

### 0.4 Pre-commit Hooks

**Nuevo archivo:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-ast
      - id: debug-statements  # atrapa print() y pdb
  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
        args: [--line-length=120]
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=120]
```

---

## 3. Fase 1: Refactor de main.py

**Duración:** 1 día  
**Prioridad:** 🔴 Alta

### 3.1 Crear estructura engine/

```
engine/
├── __init__.py          # exporta create_engine()
├── base.py              # JarvisEngine (ABC)
├── live.py              # JarvisLive (Gemini Live Audio)
├── chat.py              # JarvisChat (text + voice wrapper)
├── audio.py             # Audio: STT, TTS, play_wav, pcm_to_wav
└── factory.py           # create_engine(), build_provider_config()
```

### 3.2 engine/base.py

```python
"""Abstract engine interface."""
from abc import ABC, abstractmethod
from ui import JarvisUI

class JarvisEngine(ABC):
    def __init__(self, ui: JarvisUI, provider):
        self.ui = ui
        self.provider = provider
    
    @abstractmethod
    async def run(self):
        """Main engine loop."""
        ...
    
    @abstractmethod
    async def stop(self):
        """Graceful shutdown."""
        ...
```

### 3.3 engine/audio.py (extraer de main.py)

Mover a este archivo:
- `_save_pcm_to_wav()`
- `_play_wav_file()`
- `_pcm_to_wav_bytes()`
- `_clean_whisper_transcript()`
- `_clean_text_for_tts()`
- `_transcribe_audio()`
- `_synthesize_speech_in_memory()`
- `_synthesize_with_piper_fallback()`
- `find_fallback_device()`

### 3.4 engine/factory.py

```python
"""Provider factory — crea el engine y provider adecuados."""
from providers import create_provider, ProviderConfig

def build_provider_config() -> ProviderConfig:
    """Build ProviderConfig from saved config."""
    ...

def create_engine(ui) -> JarvisEngine:
    """Create appropriate engine based on provider."""
    ...
```

**Verificación Fase 1:**
- [ ] `main.py` < 200 líneas (solo entry point + lifecycle)
- [ ] `engine/audio.py` funcional
- [ ] `engine/live.py` funcional (Gemini Live)
- [ ] `engine/chat.py` funcional (text + voice wrapper)
- [ ] Hot-swap de providers sigue funcionando

---

## 4. Fase 2: Refactor de UI

**Duración:** 2 días  
**Prioridad:** 🔴 Alta

### 4.1 Dividir main_window.py (target: 1,717 → ~300 líneas)

```
ui/
├── __init__.py           # exporta JarvisUI
├── main_window.py        # ~300 lines: solo orquestación de subcomponentes
├── hud.py                # HUD rendering (brain, status, animations)
├── metrics.py            # System metrics display (CPU, RAM, GPU, net)
├── log_panel.py          # Chat log widget
├── file_drop.py          # Drag & drop handler
├── audio_viz.py          # WaveCanvas wrapper
├── dialogs/
│   ├── __init__.py
│   ├── settings.py       # ConfigToolbar transformado en QDialog
│   └── about.py          # About dialog
└── theme.py              # Colores, estilos, temas (ya existe)
```

### 4.2 Patrón de Composición

```python
# ui/main_window.py (después del refactor)
class JarvisUI:
    """Orchestrates all UI subcomponents."""
    
    def __init__(self, face_path=None):
        self.root = QMainWindow()
        self.hud = HUDWidget(self.root)
        self.metrics = MetricsWidget(self.root)
        self.log = LogPanel(self.root)
        self.file_drop = FileDropHandler(self)
        self.audio_viz = AudioVisualizer(self.root)
        self.settings = SettingsDialog(self.root)
        # ... conectar señales entre componentes
```

### 4.3 Sistema de Eventos (señales Qt)

```python
# Cada componente emite señales en lugar de llamar métodos directamente
class HUDWidget(QWidget):
    state_changed = pyqtSignal(str)
    
class MetricsWidget(QWidget):
    def __init__(self):
        self._metrics_thread = MetricsUpdater()
        self._metrics_thread.metrics_updated.connect(self._on_metrics)
    
    def _on_metrics(self, cpu, mem, gpu):
        # Solo actualizar display, no lógica
        self.cpu_label.setText(f"CPU: {cpu:.1f}%")
```

**Verificación Fase 2:**
- [ ] `main_window.py` < 400 líneas
- [ ] Cada subcomponente en su propio archivo
- [ ] Señales Qt conectadas correctamente
- [ ] Drag & drop funciona
- [ ] Visualizador de audio funciona
- [ ] Settings dialog funcional

---

## 5. Fase 3: Desacoplar Actions

**Duración:** 2 días  
**Prioridad:** ⚠️ Media

### 5.1 game_updater.py (916 → ~150 líneas)

**Problema:** Mezcla lógica de Steam, Epic Games, y scheduler en un solo archivo.

**Solución:**
```
actions/game_updater.py          # ~150 lines: solo routing
services/steam/
├── __init__.py
├── steam_client.py              # SteamCMD interface
├── steam_parser.py              # Parse Steam output
└── steam_scheduler.py           # Save/Load schedules
services/epic/
├── __init__.py
├── epic_client.py               # Epic Games Launcher interface
└── epic_parser.py               # Parse Epic output
```

### 5.2 computer_settings.py (62 funciones → por dominio)

```python
# ANTES: 62 funciones sueltas
def set_volume(...)
def set_brightness(...)
def toggle_wifi(...)
def close_app(...)
... 58 más ...

# DESPUÉS: Separado por dominio
services/system/
├── __init__.py
├── audio_control.py             # volume, mute, devices
├── display_control.py           # brightness, dark mode, resolution
├── network_control.py           # wifi, bluetooth
├── power_control.py             # shutdown, restart, sleep
├── window_control.py            # close, minimize, focus
└── keyboard_control.py          # hotkeys, typing
```

### 5.3 file_processor.py (760 → por tipo de archivo)

```
services/file_processing/
├── __init__.py
├── registry.py                  # File type → handler mapping
├── image_handler.py             # describe, ocr, resize, compress, convert
├── pdf_handler.py               # summarize, extract_text, to_word
├── docx_handler.py              # fix, reformat, translate
├── csv_handler.py               # analyze, stats, filter, sort
├── code_handler.py              # explain, review, fix, run
├── audio_handler.py             # transcribe, trim, convert
├── video_handler.py             # trim, extract_audio, compress
└── archive_handler.py           # list, extract
```

**Verificación Fase 3:**
- [ ] `game_updater.py` < 200 líneas
- [ ] `computer_settings.py` delegado a `services/system/`
- [ ] `file_processor.py` delegado a `services/file_processing/`
- [ ] Tests unitarios para cada nuevo servicio

---

## 6. Fase 4: Desacoplar Tools → Tool Registry

**Duración:** 2 días  
**Prioridad:** ⚠️ Media

### 6.1 Tool Registry Pattern

```python
# tools/base.py
from abc import ABC, abstractmethod
from typing import Any

class BaseTool(ABC):
    """Abstract tool — cada tool en su propio archivo."""
    
    name: str = ""
    description: str = ""
    parameters: dict = {}
    
    @abstractmethod
    def execute(self, args: dict, ui: Any) -> str:
        """Execute the tool and return result string."""
        ...

# tools/registry.py
class ToolRegistry:
    """Central registry for all tools."""
    
    def __init__(self):
        self._declarations: list[dict] = []
        self._implementations: dict[str, BaseTool] = {}
    
    def register(self, tool: type[BaseTool]):
        instance = tool()
        self._declarations.append({
            "name": instance.name,
            "description": instance.description,
            "parameters": instance.parameters,
        })
        self._implementations[instance.name] = instance
    
    def get_declarations(self) -> list[dict]:
        return self._declarations
    
    def execute(self, name: str, args: dict, ui: Any) -> str:
        tool = self._implementations.get(name)
        if not tool:
            return f"Unknown tool: {name}"
        return tool.execute(args, ui)
```

### 6.2 Estructura final de tools/

```
tools/
├── __init__.py                   # exporta ToolRegistry + register_all()
├── declarations.py               # Tool definitions (se mantiene como fuente de verdad para providers)
├── base.py                       # BaseTool ABC
├── registry.py                   # ToolRegistry class
├── chat_tools/
│   ├── __init__.py
│   ├── save_memory_tool.py
│   └── process_openrouter_tool.py
├── system_tools/
│   ├── __init__.py
│   ├── terminal_control_tool.py
│   ├── shutdown_tool.py
│   └── computer_settings_tool.py
├── file_tools/
│   ├── __init__.py
│   ├── file_controller_tool.py
│   ├── file_processor_tool.py
│   └── desktop_control_tool.py
├── web_tools/
│   ├── __init__.py
│   ├── web_search_tool.py
│   ├── browser_control_tool.py
│   ├── youtube_tool.py
│   └── flight_finder_tool.py
├── media_tools/
│   ├── __init__.py
│   ├── play_music_tool.py
│   ├── generate_image_tool.py
│   └── screen_process_tool.py
├── dev_tools/
│   ├── __init__.py
│   ├── code_helper_tool.py
│   ├── dev_agent_tool.py
│   ├── git_operation_tool.py
│   ├── docker_control_tool.py
│   └── database_query_tool.py
├── communication_tools/
│   ├── __init__.py
│   ├── email_read_tool.py
│   ├── email_send_tool.py
│   ├── send_message_tool.py
│   └── reminder_tool.py
├── knowledge_tools/
│   ├── __init__.py
│   ├── search_documents_tool.py
│   └── index_document_tool.py
├── automation_tools/
│   ├── __init__.py
│   ├── smart_home_tool.py
│   ├── agent_task_tool.py
│   └── game_updater_tool.py
└── calendar_tools/
    ├── __init__.py
    ├── calendar_list_events_tool.py
    └── calendar_create_event_tool.py
```

### 6.3 Migración progresiva

```python
# tools/__init__.py — registro automático
from tools.registry import ToolRegistry

registry = ToolRegistry()

def register_all():
    """Discover and register all tool classes."""
    import pkgutil
    import inspect
    import tools
    from tools.base import BaseTool
    
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=tools.__path__, prefix="tools.",
        onerror=lambda x: None
    ):
        try:
            module = __import__(modname, fromlist=[""])
            for name, obj in inspect.getmembers(module):
                if (isinstance(obj, type) and issubclass(obj, BaseTool) 
                    and obj is not BaseTool):
                    registry.register(obj)
        except Exception as e:
            logger.debug("Could not load tool module %s: %s", modname, e)

register_all()

# Acceso global (compatible con código existente)
TOOL_DECLARATIONS = registry.get_declarations()
TOOL_IMPLEMENTATIONS = registry.get_implementations()
```

**Verificación Fase 4:**
- [ ] Cada tool en su propio archivo
- [ ] Registry descubre tools automáticamente
- [ ] `handlers.py` elimina 615 líneas
- [ ] 34 tools siguen funcionando
- [ ] Compatibilidad hacia atrás: `TOOL_DECLARATIONS` y `TOOL_IMPLEMENTATIONS` exportados

---

## 7. Fase 5: Tests de Integración y UI

**Duración:** 3 días  
**Prioridad:** ⚠️ Media

### 7.1 Tests Faltantes por Prioridad

| Prioridad | Suite | Estado actual | Objetivo |
|-----------|-------|---------------|----------|
| 🔴 Alta | `tests/test_actions/` | Vacío | 20 tests |
| 🔴 Alta | `tests/test_services/` | Vacío | 15 tests |
| 🔴 Alta | `tests/test_ui/` | No existe | 10 tests (pytest-qt) |
| ⚠️ Media | `tests/test_integration/` | No existe | 5 tests (tool_chat_loop) |
| 🟢 Baja | `tests/test_security/` | No existe | 5 tests (crypto, sandbox) |

### 7.2 Tests de Integración

```python
# tests/test_integration/test_tool_chat_loop.py
@pytest.mark.asyncio
async def test_tool_chat_loop_with_mock_tools():
    """Verify the multi-turn tool loop processes tools correctly."""
    provider = MockProvider()
    messages = [Message(role="user", content="Search the web for AI news")]
    tools = [MOCK_SEARCH_TOOL]
    tool_impls = {"web_search": lambda a, u: "AI news results..."}
    
    response = await provider.tool_chat_loop(
        messages=messages, tools=tools,
        tool_implementations=tool_impls,
    )
    
    assert response.role == "assistant"
    assert response.content
    assert not response.tool_calls  # Should resolve after tool call
```

### 7.3 Tests de UI (pytest-qt)

```python
# tests/test_ui/test_hud.py
def test_hud_state_transitions(qtbot):
    """Test HUD visual states change correctly."""
    widget = HUDWidget()
    qtbot.addWidget(widget)
    
    widget.set_state("LISTENING")
    assert widget.state_label.text() == "LISTENING"
    assert widget.state_color == QColor("#00ff88")
    
    widget.set_state("THINKING")
    assert widget.state_label.text() == "THINKING"
    assert widget.state_color == QColor("#ffaa00")
```

### 7.4 Coverage Targets

```bash
# Ejecutar con:
pytest tests/ -v --cov=. --cov-report=html --cov-fail-under=50
```

| Módulo | Mínimo | Meta |
|--------|--------|------|
| `core/` | 80% | 90% |
| `providers/` | 60% | 75% |
| `rag/` | 60% | 75% |
| `services/` | 40% | 60% |
| `actions/` | 30% | 50% |
| `tools/` | 50% | 70% |
| `engine/` | 50% | 70% |
| `ui/` | 20% | 40% |

---

## 8. Fase 6: Infraestructura DevOps

**Duración:** 1 día  
**Prioridad:** 🟢 Media/Baja

### 8.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Development stage ---
FROM base AS dev
COPY . .
CMD ["python", "main.py"]

# --- Production stage ---
FROM base AS prod
COPY . .
RUN useradd -m jarvis
USER jarvis
CMD ["python", "main.py"]
```

### 8.2 docker-compose.yml

```yaml
version: "3.8"
services:
  jarvis:
    build:
      context: .
      target: dev
    volumes:
      - .:/app
      - ./config:/app/config
      - ./logs:/app/logs
      - ./memory:/app/memory
    environment:
      - PYTHONUNBUFFERED=1
      - DISPLAY=${DISPLAY}
      - PULSE_SERVER=unix:/run/user/1000/pulse/native
    devices:
      - "/dev/snd:/dev/snd"
    group_add:
      - audio
    stdin_open: true
    tty: true
```

### 8.3 GitHub Actions Workflows

```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install flake8 black
      - run: flake8 . --max-line-length=120 --exclude=.venv,__pycache__
      - run: black --check --line-length=120 .

  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-asyncio pytest-mock pytest-cov pytest-qt
      - run: python -m pytest tests/ -v --tb=short --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v4

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install bandit safety
      - run: bandit -r . -x .venv,__pycache__,tests
      - run: safety check -r requirements.txt
```

### 8.4 Makefile

```makefile
.PHONY: install test lint clean security docker

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt  # black, flake8, bandit, safety, pre-commit

test:
	python -m pytest tests/ -v --tb=short --cov=. --cov-report=html

lint:
	flake8 . --max-line-length=120 --exclude=.venv,__pycache__
	black --check --line-length=120 .

format:
	black --line-length=120 .

security:
	bandit -r . -x .venv,__pycache__,tests
	safety check -r requirements.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

docker:
	docker-compose build

docker-run:
	docker-compose up

pre-commit:
	pre-commit run --all-files
```

---

## 9. Fase 7: UX/UI Avanzado

**Duración:** 3 días  
**Prioridad:** 🟢 Media/Baja

### 9.1 OAuth2 Wizards en UI

```python
# ui/dialogs/oauth_wizard.py
class OAuthWizard(QWizard):
    """Wizard step-by-step for OAuth2 services."""
    
    def __init__(self, service_name: str, parent=None):
        super().__init__(parent)
        self.service_name = service_name  # "gmail", "calendar", "spotify"
        self.addPage(IntroPage(service_name))
        self.addPage(AuthPage(service_name))
        self.addPage(SuccessPage(service_name))
```

### 9.2 Sistema de Temas

```python
# ui/theme.py — ya existe, expandir
class Theme:
    CYBERPUNK = {
        "bg_primary": QColor("#0a0a1a"),
        "bg_secondary": QColor("#141428"),
        "text_primary": QColor("#00ff88"),
        "text_secondary": QColor("#6666aa"),
        "accent": QColor("#ff00ff"),
        "warning": QColor("#ffaa00"),
        "error": QColor("#ff0033"),
    }
    
    DARK = {
        "bg_primary": QColor("#1e1e1e"),
        "bg_secondary": QColor("#2d2d2d"),
        "text_primary": QColor("#ffffff"),
        ...
    }
    
    LIGHT = {
        "bg_primary": QColor("#ffffff"),
        ...
    }
```

### 9.3 i18n / Internacionalización

```python
# ui/i18n.py
import json
from pathlib import Path

class I18n:
    _translations: dict = {}
    _current_lang: str = "es"
    
    @classmethod
    def load(cls, lang: str = "es"):
        path = Path(__file__).parent / "locales" / f"{lang}.json"
        if path.exists():
            cls._translations = json.loads(path.read_text(encoding="utf-8"))
        cls._current_lang = lang
    
    @classmethod
    def t(cls, key: str, **kwargs) -> str:
        text = cls._translations.get(key, key)
        return text.format(**kwargs)
```

---

## 10. Checklist

### ✅ Fase 0: Quick Wins
- [ ] 0.1: Crypto activado en config_manager.py
- [ ] 0.2: print() reemplazado por logging (0 prints en prod)
- [ ] 0.3: GitHub Actions CI configurado
- [ ] 0.4: Pre-commit hooks instalados

### 🔄 Fase 1: Refactor main.py
- [ ] 1.1: `engine/` creado con 5 módulos
- [ ] 1.2: `main.py` reducido a < 200 líneas
- [ ] 1.3: Modo Live (Gemini) funcionando
- [ ] 1.4: Modo Chat funcionando
- [ ] 1.5: Hot-swap de providers funcionando

### 🔄 Fase 2: Refactor UI
- [ ] 2.1: `main_window.py` < 400 líneas
- [ ] 2.2: Subcomponentes separados (hud, metrics, log, file_drop)
- [ ] 2.3: Señales Qt conectadas correctamente
- [ ] 2.4: Settings como QDialog separado

### 🔄 Fase 3: Desacoplar Actions
- [ ] 3.1: `game_updater.py` delegado a services/steam/ + services/epic/
- [ ] 3.2: `computer_settings.py` delegado a services/system/
- [ ] 3.3: `file_processor.py` delegado a services/file_processing/

### 🔄 Fase 4: Tool Registry
- [ ] 4.1: `BaseTool` ABC implementado
- [ ] 4.2: `ToolRegistry` implementado
- [ ] 4.3: Cada tool en su propio archivo
- [ ] 4.4: `handlers.py` eliminado (reemplazado por registry)

### 🔄 Fase 5: Tests
- [ ] 5.1: Tests de actions (20+)
- [ ] 5.2: Tests de services (15+)
- [ ] 5.3: Tests de UI con pytest-qt (10+)
- [ ] 5.4: Tests de integración (5+)
- [ ] 5.5: Coverage mínimo 50%

### 🔄 Fase 6: DevOps
- [ ] 6.1: Dockerfile multistage
- [ ] 6.2: docker-compose.yml
- [ ] 6.3: GitHub Actions con lint + test + security
- [ ] 6.4: Makefile
- [ ] 6.5: requirements-dev.txt

### 🔄 Fase 7: UX Avanzado
- [ ] 7.1: OAuth2 wizards en UI
- [ ] 7.2: Sistema de temas (cyberpunk/dark/light)
- [ ] 7.3: i18n (es/en)
- [ ] 7.4: Notificaciones del sistema
