---
name: prompt-log
version: 1.0.0
description: Extraer, estructurar y archivar transcripciones de conversaciones con IA. Usa cuando quieras guardar prompts efectivos, crear una base de datos de conversaciones, o extraer patrones de prompts exitosos.
tags: [prompts, logging, archive, conversation, knowledge-management, prompting]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Prompt Log Skill

## Cuándo usar esta skill
- Guardar prompts que funcionaron especialmente bien
- Archivar una conversación completa para referencia futura
- Extraer patrones de prompts exitosos para reutilizarlos
- Crear un "prompt journal" personal o de equipo
- Hacer `git commit` de conversaciones importantes

## Estructura del log

```
prompts-log/
├── README.md                    — Índice de todos los logs
├── by-date/
│   ├── 2024-01/
│   │   └── 2024-01-15-refactor-auth.md
│   └── 2024-02/
└── by-category/
    ├── code-generation/
    ├── content-writing/
    ├── data-analysis/
    └── debugging/
```

## Formato de un prompt log

```markdown
---
date: 2024-01-15
category: code-generation
model: claude-3-5-sonnet
task: Refactorizar sistema de autenticación
rating: 5/5
tags: [auth, refactor, typescript, security]
---

# Prompt Log — Refactor Auth System

## Contexto
[Por qué lo necesitaba, qué problema resolvía]

## Prompt final (el que mejor funcionó)
```
[El prompt exacto que usaste, incluyendo system prompt si lo hay]
```

## Iteraciones previas
### Intento 1 (no funcionó porque...)
```
[Primer intento]
```
**Problema:** [Qué salió mal]

### Intento 2 (parcialmente)
```
[Segundo intento]
```
**Mejora:** [Qué mejoró]

## Resultado obtenido
[Summary de qué obtuvo el prompt, o pegar la respuesta relevante]

## Lecciones aprendidas
- [Qué funcionó y por qué]
- [Qué cambié entre iteraciones]
- [Truco o pattern que descubrí]

## Reutilizable como template
```
[Versión genérica del prompt, con [VARIABLES] en los campos que cambian]
```
```

## Script de captura rápida

```python
#!/usr/bin/env python3
"""
Guardar un prompt efectivo en el log con un comando simple
Uso: python prompt-log.py add
"""
import json
import sys
from datetime import date
from pathlib import Path

LOGS_DIR = Path.home() / "prompt-logs"

def add_prompt_log():
    """Interactivo para registrar un prompt"""
    print("=== Guardar Prompt Log ===\n")
    
    log = {
        "date": str(date.today()),
        "category": input("Categoría (code/content/debug/analysis/other): ").strip(),
        "task": input("Tarea/objetivo: ").strip(),
        "model": input("Modelo usado (claude/gpt-4/gemini/...): ").strip(),
        "rating": input("Rating 1-5: ").strip(),
    }
    
    print("\nPega el prompt (termina con '---END---' en una nueva línea):")
    lines = []
    while True:
        line = input()
        if line == '---END---':
            break
        lines.append(line)
    log["prompt"] = '\n'.join(lines)
    
    print("\nLecciones aprendidas (una por línea, vacío para terminar):")
    lessons = []
    while True:
        lesson = input("- ").strip()
        if not lesson:
            break
        lessons.append(lesson)
    log["lessons"] = lessons
    
    # Guardar
    date_dir = LOGS_DIR / "by-date" / log["date"][:7]
    date_dir.mkdir(parents=True, exist_ok=True)
    
    task_slug = log["task"].lower().replace(' ', '-')[:30]
    filename = f"{log['date']}-{task_slug}.md"
    filepath = date_dir / filename
    
    content = f"""---
date: {log['date']}
category: {log['category']}
model: {log['model']}
task: {log['task']}
rating: {log['rating']}/5
---

# Prompt Log — {log['task']}

## Prompt
```
{log['prompt']}
```

## Lecciones aprendidas
{chr(10).join(f'- {l}' for l in log['lessons'])}
"""
    
    filepath.write_text(content, encoding='utf-8')
    print(f"\n✅ Guardado en: {filepath}")
    
    # También guardar en JSON para búsqueda
    json_file = LOGS_DIR / "index.json"
    index = json.loads(json_file.read_text()) if json_file.exists() else []
    index.append({**log, "file": str(filepath)})
    json_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))


def search_logs(query: str):
    """Buscar en el índice de logs"""
    json_file = LOGS_DIR / "index.json"
    if not json_file.exists():
        print("No hay logs guardados")
        return
    
    index = json.loads(json_file.read_text())
    query_lower = query.lower()
    
    results = [
        log for log in index
        if query_lower in log.get('task', '').lower()
        or query_lower in log.get('category', '').lower()
        or query_lower in log.get('prompt', '').lower()
        or query_lower in ' '.join(log.get('lessons', [])).lower()
    ]
    
    if not results:
        print(f"No se encontraron logs para: {query}")
        return
    
    print(f"Encontrados {len(results)} logs:\n")
    for log in results:
        print(f"📝 {log['date']} | {log['task']}")
        print(f"   📁 {log['file']}")
        print(f"   ⭐ {log['rating']}/5 | 🤖 {log['model']}")
        print()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "add"
    
    if cmd == "add":
        add_prompt_log()
    elif cmd == "search" and len(sys.argv) > 2:
        search_logs(sys.argv[2])
    else:
        print("Uso: python prompt-log.py [add|search <query>]")
```

## Integración con agentes (auto-logging)

```python
import functools
import json
from datetime import datetime
from pathlib import Path

CHAT_LOG_DIR = Path("./chat-logs")
CHAT_LOG_DIR.mkdir(exist_ok=True)

def log_conversation(func):
    """Decorator para auto-guardar conversaciones con el LLM"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        messages_before = len(kwargs.get('messages', []))
        
        result = func(*args, **kwargs)
        
        # Guardar log
        log_entry = {
            "timestamp": start.isoformat(),
            "duration_ms": int((datetime.now() - start).total_seconds() * 1000),
            "messages": kwargs.get('messages', []),
            "response": result if isinstance(result, str) else str(result),
        }
        
        log_file = CHAT_LOG_DIR / f"{start.strftime('%Y-%m-%d')}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        return result
    return wrapper

# Uso:
@log_conversation
def ask_llm(messages: list, **kwargs):
    # Tu llamada al LLM aquí
    pass
```

## Tips para un buen prompt journal

```
✅ Registrar el prompt EXACTO que funcionó (con copia-pega, no parafrasear)
✅ Documentar el contexto del sistema si lo hay (system prompt)
✅ Anotar qué NO funcionó y por qué — tan valioso como lo que funcionó
✅ Hacer rating inmediatamente (en caliente, antes de olvidar por qué fue bueno)
✅ Extraer el template reutilizable separando lo específico de lo genérico
✅ Tagear bien para encontrar más tarde
✅ Revisar el log mensualmente para identificar patrones propios
```
