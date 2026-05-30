# MARK XL — Session Checkpoint

> Actualizado: 2026-05-23  
> Checkpoint anterior reemplazado con cambios completos

---

## Goal
Review, fix critical issues, and enhance the MARK XL (Mark 40) AI assistant project with:
- UI configuration toolbar with brain icons
- Ollama management panel (pull models, server up/down)
- API key management (Gemini + OpenRouter) desde la UI
- Audio settings (mic, speaker, volume)

## Constraints & Preferences
- "pon los accesos de los modelos en un apartado de configuracion que estara en la parte superior"
- Brain icons: Gemini = celeste outline + white interior, Ollama = white, OpenRouter = dynamic color based on model company
- "el primer boton(pull) sera un ollama pull modelo se hara un escript a comandos en la terminal para automatizar"
- "antes del boton habra una fila desplegable en donde estaran los modelos de ollama"
- "el segundo boton sera up server(ollama serve) y justo abajo estara down server"
- "deja un acceso directo en el escritorio"
- "en la pestaña de ajustes se vean una lista ordenada y clara de los comandos necesarios en una parte"
- "el dropdown se actualiza con ollama list, para que le pogas un boton de recarga"
- "ahora quiero quie le hagas lo mismo a ala api de gimini y a la api de openrouters" (UI para API keys)
- "quiero que le des en la parte de ajustes un apartado a la configuracion de microfono y de altavoz ademas de un apartado para el volumen"
- "quier que la ventana de configuracion tenga subventanas, como las ventanas de google"

---

## Progress

### ✅ Done

#### Core Fixes
- **Security**: Removed hardcoded Gemini API key from `config/api_keys.json`, created `.gitignore`
- **Tool map**: Wired `_get_tool_map()` with real action implementations (`main.py:934-957`)
- **Face fallback**: Added fallback chain for missing `face.png` (`main.py:1025`)
- **Version fix**: `setup.py:10` — "MARK XXV" → "MARK XL"
- **Dependencies**: `requirements.txt` — added `aiohttp`, removed duplicate `Pillow`
- **Async fix**: Made `ask_llm()` async, created `ask_llm_sync()` via thread+new event loop (`agent/llm_helper.py`)
- **Sync/async dispatch**: `providers/base.py:123` — `execute_tool_call()` uses `iscoroutinefunction()`
- **OpenRouter header**: Fixed `HTTP-Referer` (`providers/openrouter_provider.py`)
- **Deduplication**: Removed duplicate `analyze_error()` in `agent/executor.py`
- **Sync callers updated**: `agent/error_handler.py`, `agent/planner.py` use `ask_llm_sync`

#### UI — Toolbar & Brain Icons
- **BrainIcon widget**: Custom QPainter brain with per-provider color (Gemini=celeste, Ollama=white, OpenRouter=dynamic company color)
- **ConfigToolbar**: 48px top bar with brain icons + status + gear toggle

#### UI — Settings Panel (QTabWidget con 3 tabs estilo Google)
- **🔑 API KEYS tab**:
  - Gemini API Key input (password mode)
  - OpenRouter API Key input (password mode)
  - "💾 SAVE KEYS" button → escribe a `config/api_keys.json`
- **🔊 AUDIO tab**:
  - Microphone dropdown (poblado desde `sounddevice.query_devices()`)
  - Speaker dropdown
  - Volume slider (0-100%) persistido en config
  - Guardado automático al cambiar dispositivo
- **🤖 OLLAMA tab** (split horizontal):
  - **Left**: 7 comandos de referencia de Ollama
  - **Right**: 
    - Model dropdown con live `ollama list` + ↻ reload button
    - PULL MODEL → abre terminal con `ollama pull <modelo>`
    - UP SERVER → abre terminal con `ollama serve`
    - DOWN SERVER → taskkill/pkill ollama
    - Server status indicator (RUNNING/STOPPED)

#### Audio Integration
- `main.py`: `sd.InputStream` ahora usa `audio_input_device` del config
- `main.py`: `sd.RawOutputStream` ahora usa `audio_output_device` del config
- `main.py`: Volume scaling aplicado (multiplica samples int16 por gain factor)
- `config_manager.py`: defaults para `audio_input_device`, `audio_output_device`, `audio_volume`

#### Desktop
- **Desktop shortcut**: Created `C:\Users\lolpl\Desktop\MARK XL.lnk`

#### Verification
- **Syntax validation**: `ui.py`, `main.py`, `memory/config_manager.py` pasan `ast.parse()`

### 🔄 In Progress
- *(none)*

### ❌ Blocked
- *(none)*

---

## Key Decisions
- `ask_llm()` made async; `ask_llm_sync()` uses `threading.Thread` + `asyncio.new_event_loop()`
- `_wrap(fn)` pattern wraps sync action functions for async-compatible dispatch
- Ollama commands open new terminal windows via `subprocess.Popen` for visible feedback
- Brain icon drawn with QPainter (overlapping ellipses + brainstem + wrinkle arcs)
- Model dropdown populated via `ollama list` at runtime with hardcoded fallback
- Settings panel uses **QTabWidget** con 3 tabs para organización tipo Google
- API keys saved to same `config/api_keys.json` via `save_config()`
- Volume scaling hecho vía `array('h', ...)` para multiplicar samples int16 sin numpy
- Audio devices guardados por ID numérico de sounddevice; se re-seleccionan al abrir settings

---

## Relevant Files
| File | Lines | Description |
|---|---|---|
| `ui.py` | ~2500 | BrainIcon, ConfigToolbar (3 tabs), MainWindow |
| `main.py` | ~1086 | Audio device config + volume scaling |
| `memory/config_manager.py` | ~155 | Defaults for audio keys |
| `agent/llm_helper.py` | — | `ask_llm()` async + `ask_llm_sync()` |
| `agent/executor.py` | — | Uses `ask_llm_sync` |
| `agent/error_handler.py` | — | Uses `ask_llm_sync` |
| `agent/planner.py` | — | Uses `ask_llm_sync` |
| `providers/base.py` | — | `execute_tool_call()` sync/async dispatch |
| `providers/openrouter_provider.py` | — | Fixed HTTP-Referer |
| `config/api_keys.json` | — | Provider config, secrets stored |
| `.gitignore` | — | Git exclusion rules |
| `setup.py` | — | Version reference fixed |
| `requirements.txt` | — | Dependencies updated |


