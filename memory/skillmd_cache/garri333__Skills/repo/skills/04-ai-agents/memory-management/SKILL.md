---
name: memory-management
version: 1.0.0
description: Configurar memoria persistente y context management para agentes IA. Usa cuando quieras que el agente recuerde información entre sesiones o gestione conocimiento acumulativo del proyecto.
tags: [ai, memory, agents, context, persistence, knowledge]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Memory Management para Agentes IA

## Tipos de memoria en agentes IA

### 1. Memoria de sesión (en contexto)
- Solo dura mientras dure la conversación
- El agente la tiene naturalmente
- Limitada por la ventana de contexto

### 2. Memoria persistente (entre sesiones)
- Sobrevive entre conversaciones
- Necesita configuración explícita
- Implementada a través de archivos o vector DBs

### 3. Memoria semántica (base de conocimiento)
- Conocimiento general del dominio
- Implementada con skills (como este repositorio)
- No cambia por conversaciones individuales

## Implementación: MEMORY.md

La forma más simple de memoria persistente: un archivo `MEMORY.md` en el proyecto.

### Estructura del MEMORY.md
```markdown
# Memoria del Proyecto

## Decisiones de arquitectura
- [FECHA] Decidimos usar PostgreSQL sobre MongoDB por [RAZÓN]
- [FECHA] El sistema de auth usa JWT con refresh tokens

## Contexto del negocio
- El cliente principal es [NOMBRE], contacto: [EMAIL]
- El deadline del MVP es [FECHA]
- El stack técnico es: [STACK]

## Convenciones de código
- Nombrar componentes en PascalCase
- Usar kebab-case para rutas de URLs
- Tests en /tests/unit y /tests/integration

## Problemas conocidos y soluciones
- Si X falla, hacer Y (encontrado el [FECHA])
- La dependencia Z tiene un bug en versión X.Y.Z, usar X.Y.W

## Glosario del proyecto
- "Deal" = oportunidad de venta en el CRM
- "Lead" = contacto no calificado
```

### Instrucciones para el agente
En tu `.cursorrules`, `CLAUDE.md`, o system prompt:
```
Antes de cada sesión de trabajo:
1. Lee MEMORY.md para contexto acumulado del proyecto
2. Al final de conversaciones largas, actualiza MEMORY.md con nuevas decisiones
3. Formato al añadir: [FECHA] + decisión o aprendizaje
```

## Implementación: Logs diarios

Para proyectos activos, llevar un log diario:

```
memory/
├── MEMORY.md           ← Conocimiento permanente
├── 2026-02-18.md       ← Log del día
├── 2026-02-17.md
└── index.md            ← Índice de días con resúmenes
```

### Formato del log diario
```markdown
# 2026-02-18

## Trabajo completado
- Implementé el sistema de auth con JWT
- Encontré y resolví bug en el endpoint /api/users

## Decisiones tomadas
- Usaremos Redis para sesiones (más escalable que JWT stateless)

## Pendiente para mañana
- [ ] Implementar refresh token rotation
- [ ] Tests de integración para auth

## Contexto para el agente
[Información específica que el agente necesita saber hoy]
```

## Implementación: Vector search (avanzado)

Para proyectos grandes, usar búsqueda semántica sobre la memoria:

### Con LanceDB (local, gratuito)
```python
import lancedb
import openai

db = lancedb.connect("./memory_db")

# Guardar memoria
def save_memory(text: str, metadata: dict):
    embedding = get_embedding(text)
    table.add([{
        "text": text,
        "vector": embedding,
        **metadata
    }])

# Buscar memoria relevante
def search_memory(query: str, n=5) -> list:
    query_vec = get_embedding(query)
    results = table.search(query_vec).limit(n).to_list()
    return [r["text"] for r in results]
```

### Con Chroma (local, gratuito)
```python
import chromadb
client = chromadb.Client()
collection = client.create_collection("project_memory")

# Añadir memoria
collection.add(
    documents=["El proyecto usa PostgreSQL como base de datos principal"],
    ids=["mem-001"]
)

# Buscar
results = collection.query(
    query_texts=["qué base de datos usamos"],
    n_results=3
)
```

## Patrones de uso efectivo

### Patrón 1: Briefing al inicio
```
Al comenzar cada sesión:
"Lee el archivo MEMORY.md y dame un briefing de:
1. Estado actual del proyecto
2. Últimas 3 decisiones importantes
3. Qué está pendiente"
```

### Patrón 2: Capture de aprendizajes
```
Al final de cada sesión compleja:
"Actualiza MEMORY.md con:
1. Las decisiones técnicas que tomamos hoy
2. Los problemas que encontramos y sus soluciones
3. Cualquier convención que establecimos"
```

### Patrón 3: Memoria de errores
Llevar un archivo `ERRORS.md` para no repetir los mismos errores:
```markdown
# Problemas y Soluciones

## Error: [NOMBRE DEL PROBLEMA]
- **Síntoma**: La llamada a /api/users retorna 403 intermitentemente
- **Causa raíz**: El middleware de auth no maneja tokens con espacios en el header
- **Solución**: `token = token.strip()` antes de validar
- **Fecha**: 2026-02-15
```

## Cuándo NO usar cada tipo de memoria

| Tipo | No usar cuando |
|------|----------------|
| MEMORY.md | El proyecto es de una sola sesión |
| Logs diarios | El contexto no cambia día a día |
| Vector search | El equipo tiene < 5 personas y < 100 documentos |

## Referencias
- [Memory Setup (Clawdbot)](https://clawdbotskills.org/)
- [LanceDB Docs](https://lancedb.github.io/lancedb/)
- [Chroma Docs](https://docs.trychroma.com/)
