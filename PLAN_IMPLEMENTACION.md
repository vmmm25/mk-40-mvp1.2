# PLAN DE IMPLEMENTACIÓN — MARK XL (J.A.R.V.I.S. MARK-40)

> **Fecha:** 2026-06-02
> **Versión:** 1.0
> **Objetivo:** Mejorar, optimizar y expandir las capacidades del asistente MARK XL

---

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Fase 0: Quick Wins & Bugfixes](#2-fase-0-quick-wins--bugfixes)
3. [Fase 1: Sistema RAG (Búsqueda Inteligente en Documentos)](#3-fase-1-sistema-rag)
4. [Fase 2: Email & Calendar Integration](#4-fase-2-email--calendar)
5. [Fase 3: Generación de Imágenes](#5-fase-3-generación-de-imágenes)
6. [Fase 4: Media & Música](#6-fase-4-media--música)
7. [Fase 5: Git & Desarrollo](#7-fase-5-git--desarrollo)
8. [Fase 6: Home Automation & MCP](#8-fase-6-home-automation--mcp)
9. [Fase 7: Seguridad & Estabilidad](#9-fase-7-seguridad--estabilidad)
10. [Arquitectura Técnica Propuesta](#10-arquitectura-técnica-propuesta)
11. [Dependencias & Requisitos](#11-dependencias--requisitos)

---

## 1. Resumen Ejecutivo

### Estado Actual
MARK XL es un asistente IA multimodal con interfaz Cyberpunk HUD, soporte para 4 proveedores LLM (Gemini, Ollama, OpenRouter, LM Studio), 22 herramientas funcionales, memoria persistente, y sistema de planner/ejecutor.

### Problemas Identificados
| ID | Problema | Severidad |
|---|---|---|
| P01 | Código duplicado en `ollama_provider.py` (`pull_model`, `check_server`) | ⚠️ Media |
| P02 | Sin tests unitarios ni de integración | 🔴 Alta |
| P03 | Logging con `print()` en vez de logging estructurado | ⚠️ Media |
| P04 | API keys en texto plano sin cifrado | 🔴 Alta |
| P05 | Modelos hardcodeados en Ollama provider | ⚠️ Media |
| P06 | Sin sandboxing en ejecución de código generado | 🔴 Alta |
| P07 | Sin caché de respuestas | 🟢 Baja |

### Habilidades Propuestas (Priorizadas)
| # | Habilidad | Esfuerzo | Impacto | Prioridad |
|---|---|---|---|---|
| H01 | RAG + Búsqueda en Documentos | 3 días | 🔥 Alto | Crítica |
| H02 | Email Integration | 2 días | 🔥 Alto | Alta |
| H03 | Calendar Integration | 1.5 días | 🔥 Alto | Alta |
| H04 | Generación de Imágenes | 2 días | ⭐ Alto | Alta |
| H05 | Spotify/Media Control | 1 día | 📌 Medio | Media |
| H06 | Git/GitHub Integration | 2 días | 📌 Medio | Media |
| H07 | Docker Management | 1.5 días | 📌 Medio | Media |
| H08 | System Monitoring | 1 día | 📌 Medio | Media |
| H09 | SQL Database Query | 1.5 días | 📌 Medio | Media |
| H10 | Home Automation (MCP) | 3 días | ⭐ Alto | Media |

---

## 2. Fase 0: Quick Wins & Bugfixes

**Duración estimada:** 1 día  
**Prioridad:** 🔴 Crítica (hacer primero)

### 2.1 Eliminar código duplicado

**Archivo:** `providers/ollama_provider.py`

**Problema:** Los métodos `pull_model()` y `check_server()` aparecen dos veces (líneas 267-290 y 322-345).

**Acción:**
```python
# Eliminar el primer bloque duplicado (líneas 267-290)
# Mantener el segundo bloque (líneas 322-345) que es idéntico
```

**Verificación:**
- [ ] `ollama_provider.py` compila sin errores
- [ ] `pull_model()` funciona correctamente
- [ ] `check_server()` funciona correctamente

### 2.2 Sistema de logging estructurado

**Archivos afectados:** `main.py`, `agent/*.py`, `actions/*.py`, `providers/*.py`, `memory/*.py`

**Acción:** Reemplazar `print()` con `logging` estándar de Python.

```python
# En cada módulo, agregar al inicio:
import logging
logger = logging.getLogger(__name__)

# Reemplazar:
print("[JARVIS] 🔧 Tool called")  
# Por:
logger.info("Tool called: %s", tool_name)
```

**Configuración centralizada** en `logging_config.py`:
```python
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/jarvis.log", encoding="utf-8"),
        ]
    )
```

**Verificación:**
- [ ] Logging configurado centralmente
- [ ] Todos los `print()` reemplazados
- [ ] Logs se escriben en archivo y consola
- [ ] Niveles: DEBUG, INFO, WARNING, ERROR según corresponda

### 2.3 Tests unitarios iniciales

**Nuevos archivos:**

```
tests/
├── __init__.py
├── conftest.py
├── test_providers/
│   ├── __init__.py
│   ├── test_ollama_provider.py
│   ├── test_gemini_provider.py
│   └── test_base.py
├── test_agent/
│   ├── __init__.py
│   ├── test_planner.py
│   ├── test_executor.py
│   └── test_task_queue.py
├── test_actions/
│   ├── __init__.py
│   ├── test_web_search.py
│   ├── test_file_controller.py
│   └── test_computer_control.py
└── test_memory/
    ├── __init__.py
    └── test_memory_manager.py
```

**Verificación:**
- [ ] `pytest` configurado en `requirements.txt`
- [ ] Tests básicos para `memory_manager.py`
- [ ] Tests básicos para `task_queue.py`
- [ ] Coverage report funcional

### 2.4 Caché de respuestas

**Nuevo archivo:** `core/cache.py`

```python
import time
import json
from pathlib import Path
from threading import Lock

class ResponseCache:
    def __init__(self, ttl_seconds=300, max_entries=100):
        self.cache = {}
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self.lock = Lock()
    
    def get(self, key: str) -> str | None:
        with self.lock:
            entry = self.cache.get(key)
            if entry and time.time() - entry["time"] < self.ttl:
                return entry["value"]
            return None
    
    def set(self, key: str, value: str):
        with self.lock:
            if len(self.cache) >= self.max_entries:
                # Eliminar entrada más antigua
                oldest = min(self.cache.keys(), key=lambda k: self.cache[k]["time"])
                del self.cache[oldest]
            self.cache[key] = {"value": value, "time": time.time()}
```

**Verificación:**
- [ ] `ResponseCache` implementado
- [ ] Integrado en `providers/base.py`
- [ ] TTL configurable desde config

---

## 3. Fase 1: Sistema RAG

**Duración estimada:** 3 días  
**Prioridad:** 🔥 Alta  
**Skill:** `RAG` — Búsqueda semántica local sobre documentos

### 3.1 Descripción
Permitir que el asistente busque información en documentos locales (PDFs, DOCX, TXT, CSV, HTML, código fuente) usando embeddings y búsqueda semántica.

### 3.2 Arquitectura

```
rag/
├── __init__.py
├── embeddings.py        # Generación de embeddings (Ollama/Gemini/local)
├── indexer.py           # Indexación de documentos
├── retriever.py         # Búsqueda semántica con ChromaDB
├── document_loader.py   # Carga de diferentes formatos
└── config.py            # Configuración de rutas a indexar
```

### 3.3 Dependencias Nuevas
```txt
chromadb>=0.5.0
sentence-transformers>=2.2.0
pypdf>=4.0.0
python-docx>=1.1.0
openpyxl>=3.1.0
markdown>=3.5.0
```

### 3.4 Implementación

#### 3.4.1 Document Loader (`rag/document_loader.py`)

Soportar formatos:
- `.pdf` → `pypdf`
- `.docx` → `python-docx`
- `.txt`, `.md` → lectura directa
- `.csv`, `.xlsx` → `pandas`
- `.py`, `.js`, `.ts`, etc. → código fuente

```python
from pathlib import Path
from typing import List

class DocumentLoader:
    SUPPORTED_EXTENSIONS = {
        ".pdf": "load_pdf",
        ".docx": "load_docx",
        ".txt": "load_text",
        ".md": "load_text",
        ".csv": "load_csv",
        ".xlsx": "load_excel",
    }
    
    def load(self, path: Path) -> List[dict]:
        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            return []
        method = getattr(self, self.SUPPORTED_EXTENSIONS[ext])
        return method(path)
```

#### 3.4.2 Embeddings (`rag/embeddings.py`)

```python
class EmbeddingProvider:
    """Genera embeddings usando Ollama o modelo local."""
    
    def __init__(self, model: str = "nomic-embed-text"):
        self.model = model
        self.ollama_url = "http://localhost:11434"
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        # Usar Ollama para generar embeddings
        async with aiohttp.ClientSession() as session:
            results = []
            for text in texts:
                async with session.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": self.model, "prompt": text}
                ) as resp:
                    data = await resp.json()
                    results.append(data["embedding"])
            return results
```

#### 3.4.3 Indexador (`rag/indexer.py`)

```python
class DocumentIndexer:
    """Indexa documentos en ChromaDB."""
    
    def __init__(self, persist_dir: str = "memory/vector_store"):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def index_document(self, path: Path, chunks: List[dict]):
        """Indexa chunks de un documento."""
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            ids.append(f"{path.stem}_{i}")
            documents.append(chunk["text"])
            metadatas.append({
                "source": str(path),
                "page": chunk.get("page", 0),
                "type": path.suffix,
            })
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
```

#### 3.4.4 Retriever (`rag/retriever.py`)

```python
class Retriever:
    def __init__(self, persist_dir: str = "memory/vector_store"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection("documents")
    
    def search(self, query: str, n_results: int = 5) -> List[dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        return [
            {
                "text": doc,
                "source": meta["source"],
                "score": dist,
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]
```

### 3.5 Tool Declaration

En `tools/declarations.py`, agregar:

```python
{
    "name": "search_documents",
    "description": (
        "Search your local documents using semantic search. "
        "Indexes PDFs, Word docs, text files, code, and more. "
        "Use this when the user asks about information in their files, "
        "documents, or projects."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "What to search for in natural language"
            },
            "n_results": {
                "type": "INTEGER",
                "description": "Number of results (default: 5)"
            },
        },
        "required": ["query"]
    }
}
```

### 3.6 Verificación
- [ ] Documentos PDF se indexan correctamente
- [ ] Documentos Word se indexan correctamente
- [ ] Archivos de código se indexan correctamente
- [ ] Búsqueda semántica devuelve resultados relevantes
- [ ] Tool `search_documents` funciona desde el asistente
- [ ] Índice persiste entre reinicios
- [ ] Re-indexación de documentos modificados

---

## 4. Fase 2: Email & Calendar

**Duración estimada:** 3 días  
**Prioridad:** 🔥 Alta  
**Skill:** `Communication` — Integración con servicios de email y calendario

### 4.1 Email Integration

#### 4.1.1 Arquitectura

```
services/
├── __init__.py
├── email/
│   ├── __init__.py
│   ├── gmail_client.py    # Cliente Gmail API
│   ├── outlook_client.py  # Cliente Outlook API
│   └── base.py            # Interfaz abstracta de email
├── calendar/
│   ├── __init__.py
│   ├── gcal_client.py     # Cliente Google Calendar
│   └── base.py            # Interfaz abstracta de calendario
```

#### 4.1.2 Dependencias
```txt
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.120.0
```

#### 4.1.3 Tools de Email

```python
# tools/declarations.py
{
    "name": "email_read",
    "description": "Read emails from your inbox. Can filter by sender, subject, date, or unread status.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "max_results": {"type": "INTEGER", "description": "Max emails to return (default: 10)"},
            "unread_only": {"type": "BOOLEAN", "description": "Only unread emails"},
            "query": {"type": "STRING", "description": "Search filter (e.g. 'from:john subject:meeting')"},
        },
        "required": []
    }
},
{
    "name": "email_send",
    "description": "Send an email to one or more recipients.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "to": {"type": "STRING", "description": "Recipient email address"},
            "subject": {"type": "STRING", "description": "Email subject"},
            "body": {"type": "STRING", "description": "Email body content"},
            "cc": {"type": "STRING", "description": "CC recipients (comma separated)"},
        },
        "required": ["to", "subject", "body"]
    }
}
```

#### 4.1.4 Verificación
- [ ] Autenticación OAuth2 funcional
- [ ] Lectura de inbox con filtros
- [ ] Envío de emails con adjuntos
- [ ] Búsqueda de emails por criterios
- [ ] Tool `email_read` funciona
- [ ] Tool `email_send` funciona

### 4.2 Calendar Integration

#### 4.2.1 Tools de Calendario

```python
{
    "name": "calendar_list_events",
    "description": "List upcoming events from your calendar.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "max_results": {"type": "INTEGER", "description": "Max events (default: 10)"},
            "days_ahead": {"type": "INTEGER", "description": "How many days ahead to look (default: 7)"},
        },
        "required": []
    }
},
{
    "name": "calendar_create_event",
    "description": "Create a new event in your calendar.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "summary": {"type": "STRING", "description": "Event title"},
            "description": {"type": "STRING", "description": "Event description"},
            "date": {"type": "STRING", "description": "Date YYYY-MM-DD"},
            "time": {"type": "STRING", "description": "Time HH:MM (24h format)"},
            "duration_minutes": {"type": "INTEGER", "description": "Duration in minutes (default: 60)"},
            "attendees": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Email addresses of attendees"},
        },
        "required": ["summary", "date"]
    }
}
```

#### 4.2.2 Verificación
- [ ] Listado de eventos próximos
- [ ] Creación de eventos con asistentes
- [ ] Modificación de eventos existentes
- [ ] Tool `calendar_list_events` funciona
- [ ] Tool `calendar_create_event` funciona

---

## 5. Fase 3: Generación de Imágenes

**Duración estimada:** 2 días  
**Prioridad:** ⭐ Alta  
**Skill:** `Image Generation` — Generación de imágenes desde el asistente

### 5.1 Arquitectura

```
services/
├── image_gen/
│   ├── __init__.py
│   ├── base.py              # Interfaz abstracta
│   ├── local_sd.py          # Stable Diffusion local (Automatic1111/ComfyUI)
│   ├── gemini_gen.py        # Gemini Image Generation
│   └── openai_gen.py        # DALL-E / OpenRouter image models
```

### 5.2 Modos de generación

1. **Local** → Stable Diffusion via API de Automatic1111 o ComfyUI
2. **Cloud** → Gemini 2.0 Flash Image Generation o DALL-E 3 via OpenRouter

### 5.3 Tool Declaration

```python
{
    "name": "generate_image",
    "description": "Generate an image from a text description using AI.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "prompt": {"type": "STRING", "description": "Detailed description of the image to generate"},
            "style": {"type": "STRING", "description": "Art style: realistic | anime | cyberpunk | oil_painting | watercolor | pixel_art"},
            "size": {"type": "STRING", "description": "Image size: 512x512 | 1024x1024 | 1024x768 (default: 1024x1024)"},
            "save": {"type": "BOOLEAN", "description": "Save to desktop (default: true)"},
            "count": {"type": "INTEGER", "description": "Number of images (default: 1, max: 4)"},
        },
        "required": ["prompt"]
    }
}
```

### 5.4 Implementación Local (Automatic1111)

```python
class StableDiffusionLocal:
    """Genera imágenes usando Stable Diffusion local."""
    
    def __init__(self, api_url: str = "http://127.0.0.1:7860"):
        self.api_url = api_url
    
    async def generate(self, prompt: str, **kwargs) -> bytes:
        payload = {
            "prompt": prompt,
            "negative_prompt": "nsfw, low quality, blurry",
            "steps": kwargs.get("steps", 30),
            "width": kwargs.get("width", 1024),
            "height": kwargs.get("height", 1024),
            "batch_size": kwargs.get("count", 1),
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json=payload
            ) as resp:
                data = await resp.json()
                return data["images"]  # Lista de base64
```

### 5.5 Verificación
- [ ] Generación local con SD funciona
- [ ] Generación cloud con Gemini/DALL-E funciona
- [ ] Tool `generate_image` desde el asistente
- [ ] Imágenes se guardan en el escritorio
- [ ] Múltiples estilos funcionan

---

## 6. Fase 4: Media & Música

**Duración estimada:** 1 día  
**Prioridad:** 📌 Media  
**Skill:** `Media Control` — Control de reproducción musical

### 6.1 Spotify Integration

#### 6.1.1 Dependencias
```txt
spotipy>=2.24.0
```

#### 6.1.2 Tools

```python
{
    "name": "play_music",
    "description": "Play music, podcasts, or control playback on Spotify.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "play | pause | next | previous | search | playlist | volume | info"},
            "query": {"type": "STRING", "description": "Song/artist/playlist name for search action"},
            "device": {"type": "STRING", "description": "Target device name"},
            "volume": {"type": "INTEGER", "description": "Volume level 0-100"},
        },
        "required": ["action"]
    }
}
```

### 6.2 Verificación
- [ ] Reproducir/pausar música
- [ ] Siguiente/anterior canción
- [ ] Búsqueda de canciones/artistas
- [ ] Control de volumen
- [ ] Tool `play_music` funciona

---

## 7. Fase 5: Git & Desarrollo

**Duración estimada:** 2 días  
**Prioridad:** 📌 Media  
**Skill:** `DevTools` — Integración con Git y herramientas de desarrollo

### 7.1 Git Integration

#### 7.1.1 Tools

```python
{
    "name": "git_operation",
    "description": "Perform Git operations: status, commit, push, pull, branch, log, diff, clone.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "status | commit | push | pull | branch | log | diff | clone | add | checkout | merge"},
            "path": {"type": "STRING", "description": "Repository path (default: current project)"},
            "message": {"type": "STRING", "description": "Commit message"},
            "branch": {"type": "STRING", "description": "Branch name"},
            "url": {"type": "STRING", "description": "Repository URL for clone"},
        },
        "required": ["action"]
    }
}
```

### 7.2 Docker Management

```python
{
    "name": "docker_control",
    "description": "Control Docker containers: list, start, stop, logs, compose.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "list | start | stop | restart | logs | ps | compose_up | compose_down | stats"},
            "container": {"type": "STRING", "description": "Container name or ID"},
            "compose_file": {"type": "STRING", "description": "Path to docker-compose.yml"},
        },
        "required": ["action"]
    }
}
```

### 7.3 Database Query

```python
{
    "name": "database_query",
    "description": "Execute SQL queries on configured databases.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "connection": {"type": "STRING", "description": "Connection name from config (e.g. 'local_postgres', 'project_db')"},
            "query": {"type": "STRING", "description": "SQL query to execute"},
        },
        "required": ["connection", "query"]
    }
}
```

### 7.4 Verificación
- [ ] Git status, commit, push funcionan
- [ ] Docker list, start, stop funcionan
- [ ] Database queries se ejecutan correctamente
- [ ] Resultados se muestran en la UI

---

## 8. Fase 6: Home Automation & MCP

**Duración estimada:** 3 días  
**Prioridad:** ⭐ Alta  
**Skill:** `MCP + IoT` — Integración con Home Assistant y protocolo MCP

### 8.1 Home Assistant Integration

```python
{
    "name": "smart_home",
    "description": "Control smart home devices via Home Assistant.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "list_devices | turn_on | turn_off | set_temperature | get_status | scene"},
            "device": {"type": "STRING", "description": "Device name or entity ID"},
            "value": {"type": "STRING", "description": "Value for set_temperature (e.g. '22')"},
            "scene": {"type": "STRING", "description": "Scene name for scene action"},
        },
        "required": ["action"]
    }
}
```

### 8.2 MCP Server Support

El protocolo MCP (Model Context Protocol) permite expandir las herramientas del asistente dinámicamente.

```python
# services/mcp/server.py
class MCPServerManager:
    """Gestiona conexiones a servidores MCP para herramientas dinámicas."""
    
    def __init__(self):
        self.servers = {}
    
    async def connect(self, name: str, command: str, args: List[str]):
        """Conecta a un servidor MCP."""
        process = await asyncio.create_subprocess_exec(
            command, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self.servers[name] = {
            "process": process,
            "tools": [],
        }
    
    async def list_tools(self) -> List[dict]:
        """Lista todas las herramientas de todos los servidores MCP."""
        tools = []
        for name, server in self.servers.items():
            # Comunicación vía JSON-RPC
            pass
        return tools
```

### 8.3 Verificación
- [ ] Home Assistant conectado y autenticado
- [ ] Listar dispositivos del hogar
- [ ] Controlar luces, termostato, switches
- [ ] Servidor MCP básico funcional
- [ ] Herramientas MCP disponibles en el asistente

---

## 9. Fase 7: Seguridad & Estabilidad

**Duración estimada:** 2 días  
**Prioridad:** 🔴 Alta  
**Skill:** `Security` — Mejoras de seguridad y robustez

### 9.1 Cifrado de API Keys

```python
# core/crypto.py
from cryptography.fernet import Fernet
import base64
import os

class KeyManager:
    def __init__(self):
        self.key_file = Path.home() / ".jarvis" / "master.key"
        self._ensure_master_key()
    
    def _ensure_master_key(self):
        if not self.key_file.exists():
            key = Fernet.generate_key()
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            self.key_file.write_text(base64.b64encode(key).decode())
        self.fernet = Fernet(base64.b64decode(self.key_file.read_text()))
    
    def encrypt(self, plaintext: str) -> str:
        return self.fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        return self.fernet.decrypt(ciphertext.encode()).decode()
```

### 9.2 Sandbox para código generado

```python
# core/sandbox.py
import sys
import subprocess
import tempfile
from pathlib import Path

class CodeSandbox:
    """Ejecuta código generado en un entorno restringido."""
    
    def __init__(self):
        self.allowed_modules = {
            "json", "math", "datetime", "re", "collections",
            "itertools", "functools", "typing", "pathlib",
        }
        self.blocked_keywords = [
            "import os", "import subprocess", "import sys",
            "__import__", "eval(", "exec(", "open(",
            "shutil", "socket", "requests",
        ]
    
    def validate_code(self, code: str) -> bool:
        """Valida que el código no use módulos peligrosos."""
        code_lower = code.lower()
        for keyword in self.blocked_keywords:
            if keyword in code_lower:
                return False
        return True
    
    def run(self, code: str, timeout: int = 30) -> str:
        if not self.validate_code(code):
            raise SecurityError("Código bloqueado por seguridad")
        
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(f"# RESTRICTED SANDBOX\n")
            f.write(code)
            tmp_path = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, "-I", tmp_path],  # -I = isolated mode
                capture_output=True, text=True,
                timeout=timeout,
            )
            return result.stdout if result.returncode == 0 else result.stderr
        finally:
            Path(tmp_path).unlink(missing_ok=True)
```

### 9.3 Rate Limiting

```python
# core/rate_limiter.py
import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    def __init__(self, calls_per_minute: int = 30):
        self.calls_per_minute = calls_per_minute
        self.calls = defaultdict(list)
        self.lock = Lock()
    
    def check(self, key: str = "default") -> bool:
        with self.lock:
            now = time.time()
            window = now - 60
            
            # Limpiar llamadas antiguas
            self.calls[key] = [t for t in self.calls[key] if t > window]
            
            if len(self.calls[key]) >= self.calls_per_minute:
                return False
            
            self.calls[key].append(now)
            return True
```

### 9.4 Verificación
- [ ] API keys cifradas en reposo
- [ ] Sandbox impide ejecución de código peligroso
- [ ] Rate limiting activo en providers
- [ ] Tests de seguridad pasan

---

## 10. Arquitectura Técnica Propuesta

### 10.1 Estructura de directorios final (post-implementación)

```
update-mk40/
├── main.py                 # Entry point (sin cambios)
├── setup.py                # Instalación de dependencias
├── requirements.txt        # Dependencias actualizadas
├── PLAN_IMPLEMENTACION.md  # Este documento
│
├── core/                   # Núcleo
│   ├── prompt.txt          # System prompt
│   ├── tts_piper.py        # TTS local (existente)
│   ├── cache.py            # 🆕 Caché de respuestas
│   ├── crypto.py           # 🆕 Cifrado de API keys
│   ├── sandbox.py          # 🆕 Sandbox para código
│   ├── rate_limiter.py     # 🆕 Rate limiting
│   └── logging_config.py   # 🆕 Configuración de logging
│
├── agent/                  # Sistema de agente
│   ├── planner.py          # Planificador (existente)
│   ├── executor.py         # Ejecutor (existente)
│   ├── error_handler.py    # Manejador de errores
│   ├── llm_helper.py       # Helper LLM (existente)
│   └── task_queue.py       # Cola de tareas (existente)
│
├── providers/              # Proveedores LLM
│   ├── __init__.py         # Registro de providers (existente)
│   ├── base.py             # Clase base (existente)
│   ├── gemini_provider.py  # Gemini (existente)
│   ├── ollama_provider.py  # Ollama (existente, con bugfix)
│   ├── openrouter_provider.py  # OpenRouter (existente)
│   └── lmstudio_provider.py    # LM Studio (existente)
│
├── actions/                # Herramientas/Acciones
│   ├── (22 archivos existentes)
│   └── ... 
│
├── tools/                  # Declaraciones y handlers de tools
│   ├── declarations.py     # Declaraciones actualizadas
│   └── handlers.py         # Handlers actualizados
│
├── rag/                    # 🆕 SISTEMA RAG
│   ├── __init__.py
│   ├── embeddings.py       # Generación de embeddings
│   ├── indexer.py          # Indexación de documentos
│   ├── retriever.py        # Búsqueda semántica
│   ├── document_loader.py  # Carga de formatos
│   └── config.py           # Configuración
│
├── services/               # 🆕 SERVICIOS EXTERNOS
│   ├── __init__.py
│   ├── email/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── gmail_client.py
│   │   └── outlook_client.py
│   ├── calendar/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── gcal_client.py
│   ├── image_gen/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local_sd.py
│   │   └── gemini_gen.py
│   ├── media/
│   │   ├── __init__.py
│   │   └── spotify_client.py
│   ├── git/
│   │   ├── __init__.py
│   │   └── git_client.py
│   ├── docker/
│   │   ├── __init__.py
│   │   └── docker_client.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db_client.py
│   └── mcp/
│       ├── __init__.py
│       └── server.py
│
├── memory/                 # Sistema de memoria
│   ├── __init__.py
│   ├── config_manager.py   # Gestor de configuración (existente)
│   ├── memory_manager.py   # Gestor de memoria (existente)
│   ├── long_term.json      # Memoria persistente (existente)
│   └── vector_store/       # 🆕 Base de datos vectorial (ChromaDB)
│
├── tests/                  # 🆕 TESTS
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_providers/
│   ├── test_agent/
│   ├── test_actions/
│   ├── test_memory/
│   ├── test_rag/
│   └── test_services/
│
├── ui/                     # Interfaz de usuario
│   ├── (archivos existentes)
│   └── ...
│
└── config/                 # Configuración
    ├── __init__.py
    ├── api_keys.json       # Config cifrada post-fase7
    └── api_keys.json.example   # Template de ejemplo
```

### 10.2 Flujo de datos extendido

```
Usuario (Voz/Texto)
    │
    ▼
┌─────────────────────┐
│       JarvisUI       │  PyQt6 Cyberpunk HUD
│  (Input/Output/Voz)  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    main.py Engine    │  ──►  Core: Cache, Logging, Rate Limiter
│  (Live / Chat mode)  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Tool Loop (tools/  │  ──►  22 tools existentes
│   handlers.py)       │        +
└─────────┬───────────┘         🆕 search_documents
          │                     🆕 email_*
          │                     🆕 calendar_*
          │                     🆕 generate_image
          │                     🆕 play_music
          │                     🆕 git_operation
          │                     🆕 docker_control
          │                     🆕 database_query
          │                     🆕 smart_home
          │
          ▼
┌─────────────────────┐
│   Agent System       │  Planner → Executor → Task Queue
│   (agent/)           │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   RAG System (rag/)  │  🆕 Document Indexing + Semantic Search
│   ChromaDB + Ollama  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Services (services/)│  🆕 Email, Calendar, Image Gen,
│                      │     Spotify, Git, Docker, DB, MCP
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  LLM Providers       │  Gemini / Ollama / OpenRouter / LM Studio
│  (providers/)        │
└─────────────────────┘
```

---

## 11. Dependencias & Requisitos

### 11.1 Dependencias a agregar en `requirements.txt`

```txt
# === FASE 1: RAG ===
chromadb>=0.5.0
sentence-transformers>=2.2.0
pypdf>=4.0.0
python-docx>=1.1.0
openpyxl>=3.1.0
markdown>=3.5.0

# === FASE 2: Email & Calendar ===
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.120.0

# === FASE 4: Media ===
spotipy>=2.24.0

# === FASE 7: Security ===
cryptography>=42.0.0

# === TESTS ===
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-mock>=3.12.0
pytest-cov>=5.0.0
```

### 11.2 Requisitos del sistema

- Python 3.11+
- Ollama (para embeddings RAG y LLMs locales)
- ChromaDB (almacenamiento vectorial)
- [Opcional] Automatic1111 / ComfyUI (generación de imágenes local)
- [Opcional] Home Assistant (Home Automation)

---

## 📊 Resumen de Tiempos

| Fase | Descripción | Días | Prioridad |
|---|---|---|---|
| **Fase 0** | Quick Wins & Bugfixes | 1 | 🔴 Crítica |
| **Fase 1** | Sistema RAG | 3 | 🔥 Alta |
| **Fase 2** | Email & Calendar | 3 | 🔥 Alta |
| **Fase 3** | Generación de Imágenes | 2 | ⭐ Alta |
| **Fase 4** | Media & Música | 1 | 📌 Media |
| **Fase 5** | Git & Desarrollo | 2 | 📌 Media |
| **Fase 6** | Home Automation & MCP | 3 | ⭐ Alta |
| **Fase 7** | Seguridad & Estabilidad | 2 | 🔴 Alta |
| **Total** | | **17 días** | |

---

## ✅ Checklist de Progreso

- [ ] **Fase 0:** Quick Wins & Bugfixes
  - [ ] 0.1: Código duplicado eliminado
  - [ ] 0.2: Logging estructurado implementado
  - [ ] 0.3: Tests unitarios iniciales
  - [ ] 0.4: Caché de respuestas
- [ ] **Fase 1:** Sistema RAG
  - [ ] 1.1: Document Loader
  - [ ] 1.2: Embeddings
  - [ ] 1.3: Indexador ChromaDB
  - [ ] 1.4: Retriever semántico
  - [ ] 1.5: Tool `search_documents`
- [ ] **Fase 2:** Email & Calendar
  - [ ] 2.1: Gmail client
  - [ ] 2.2: Tool `email_read`, `email_send`
  - [ ] 2.3: Google Calendar client
  - [ ] 2.4: Tool `calendar_*`
- [ ] **Fase 3:** Generación de Imágenes
  - [ ] 3.1: Integración SD local
  - [ ] 3.2: Integración cloud
  - [ ] 3.3: Tool `generate_image`
- [ ] **Fase 4:** Media & Música
  - [ ] 4.1: Spotify integration
  - [ ] 4.2: Tool `play_music`
- [ ] **Fase 5:** Git & Desarrollo
  - [ ] 5.1: Tool `git_operation`
  - [ ] 5.2: Tool `docker_control`
  - [ ] 5.3: Tool `database_query`
- [ ] **Fase 6:** Home Automation & MCP
  - [ ] 6.1: Home Assistant integration
  - [ ] 6.2: Tool `smart_home`
  - [ ] 6.3: MCP Server Manager
- [ ] **Fase 7:** Seguridad & Estabilidad
  - [ ] 7.1: Cifrado de API keys
  - [ ] 7.2: Sandbox para código
  - [ ] 7.3: Rate limiting

---

> **Nota:** Este plan es iterativo. Podemos ajustar prioridades según tus necesidades. ¿Por qué fase te gustaría empezar?
