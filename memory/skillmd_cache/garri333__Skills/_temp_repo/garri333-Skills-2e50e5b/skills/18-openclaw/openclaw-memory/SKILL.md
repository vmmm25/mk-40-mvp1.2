---
name: openclaw-memory
version: 1.0.0
description: Sistema de memoria triple para contexto persistente de agentes — LanceDB (búsqueda vectorial), Git-Notes (anotaciones versionadas), File-based (JSON/YAML estructurado). Gestiona almacenamiento, recuperación, búsqueda semántica, poda y persistencia entre sesiones.
tags: [openclaw, memory, lancedb, git-notes, vector-search, embeddings, persistence, context-management, semantic-retrieval]
author: garri333
license: MIT
source: VoltAgent/awesome-openclaw-skills
---

# OpenClaw Memory Skill

> Sistema de memoria triple para agentes autónomos con persistencia de contexto entre conversaciones. Permite almacenar, recuperar y buscar información semánticamente usando tres backends complementarios.

## Cuándo activar

- Cuando el agente necesita **recordar contexto** entre sesiones o conversaciones
- Cuando hay información recurrente (preferencias del usuario, decisiones de proyecto, hechos clave)
- Cuando se requiere **búsqueda semántica** sobre conocimiento acumulado
- Cuando el agente trabaja en proyectos de larga duración y necesita **persistencia de estado**
- Cuando la ventana de contexto se llena y hay que gestionar qué se retiene
- Cuando se necesitan **anotaciones versionadas** vinculadas a código o archivos

## Arquitectura: Triple Memory System

```
┌─────────────────────────────────────────────────────┐
│                   Memory Router                      │
│  Decide qué backend usar según tipo de dato          │
├──────────────┬──────────────────┬────────────────────┤
│   LanceDB    │    Git-Notes     │    File-Based      │
│  (Vectorial) │  (Versionada)    │  (Estructurada)    │
│              │                  │                    │
│ • Embeddings │ • git notes add  │ • JSON / YAML      │
│ • Similarity │ • Historial      │ • Key-value        │
│ • Semántica  │ • Por commit     │ • Categorías       │
└──────────────┴──────────────────┴────────────────────┘
```

## Instrucciones paso a paso

### 1. Configurar el backend de memoria

```yaml
# .openclaw/memory-config.yaml
memory:
  backends:
    lancedb:
      enabled: true
      path: ".openclaw/memory/vectors"
      embedding_model: "text-embedding-3-small"
      dimensions: 1536
      max_entries: 10000

    git_notes:
      enabled: true
      namespace: "openclaw-memory"
      auto_sync: true

    file_based:
      enabled: true
      path: ".openclaw/memory/store"
      format: "yaml"  # yaml | json
      max_file_size_kb: 512

  # Gestión de contexto
  context_window:
    max_tokens: 8000
    strategy: "relevance"  # relevance | recency | hybrid
    decay_rate: 0.05       # Factor de decaimiento por sesión

  categories:
    - facts          # Hechos sobre el proyecto/usuario
    - preferences    # Preferencias del usuario
    - project_state  # Estado actual del proyecto
    - decisions      # Decisiones tomadas y su razonamiento
    - learnings      # Lecciones aprendidas
```

### 2. Operaciones de memoria

```python
# Almacenar un recuerdo
def store_memory(content: str, category: str, metadata: dict = None):
    """
    Almacena información en los backends configurados.
    
    Args:
        content: Texto a recordar
        category: facts | preferences | project_state | decisions | learnings
        metadata: Metadatos adicionales (timestamp, source, confidence)
    """
    memory_entry = {
        "id": generate_uuid(),
        "content": content,
        "category": category,
        "timestamp": datetime.utcnow().isoformat(),
        "relevance_score": 1.0,
        "access_count": 0,
        "metadata": metadata or {}
    }
    
    # Backend 1: LanceDB — generar embedding y almacenar
    embedding = embed(content)
    lancedb_table.add([{
        **memory_entry,
        "vector": embedding
    }])
    
    # Backend 2: File-based — append a la categoría
    store_path = f".openclaw/memory/store/{category}.yaml"
    append_to_yaml(store_path, memory_entry)
    
    # Backend 3: Git-Notes — si hay commit activo
    if has_active_commit():
        git_notes_add(memory_entry)
    
    return memory_entry["id"]
```

```python
# Recuperar memorias relevantes
def retrieve_memories(query: str, top_k: int = 5, category: str = None):
    """
    Búsqueda semántica sobre memorias almacenadas.
    Combina resultados de todos los backends.
    """
    results = []
    
    # Búsqueda vectorial en LanceDB
    query_embedding = embed(query)
    lance_results = lancedb_table.search(query_embedding).limit(top_k * 2).to_list()
    
    # Filtrar por categoría si se especifica
    if category:
        lance_results = [r for r in lance_results if r["category"] == category]
    
    # Aplicar decay: memorias antiguas pierden relevancia
    for result in lance_results:
        age_days = (datetime.utcnow() - parse(result["timestamp"])).days
        decay_factor = math.exp(-DECAY_RATE * age_days)
        result["adjusted_score"] = result["_distance"] * decay_factor * result["relevance_score"]
    
    # Ordenar por score ajustado y devolver top_k
    results = sorted(lance_results, key=lambda x: x["adjusted_score"], reverse=True)[:top_k]
    
    return results
```

```python
# Actualizar una memoria existente
def update_memory(memory_id: str, new_content: str = None, boost: float = None):
    """
    Actualiza contenido o relevancia de una memoria.
    """
    entry = get_memory_by_id(memory_id)
    
    if new_content:
        entry["content"] = new_content
        entry["vector"] = embed(new_content)
        entry["metadata"]["last_updated"] = datetime.utcnow().isoformat()
    
    if boost:
        entry["relevance_score"] = min(entry["relevance_score"] + boost, 2.0)
    
    entry["access_count"] += 1
    
    # Sincronizar en todos los backends
    sync_all_backends(entry)
```

```python
# Podar memorias irrelevantes
def prune_memories(threshold: float = 0.1, max_age_days: int = 90):
    """
    Elimina memorias con baja relevancia o muy antiguas.
    Preserva 'decisions' y 'facts' con acceso reciente.
    """
    all_memories = load_all_memories()
    
    to_remove = []
    for mem in all_memories:
        age = (datetime.utcnow() - parse(mem["timestamp"])).days
        adjusted_relevance = mem["relevance_score"] * math.exp(-DECAY_RATE * age)
        
        # Nunca podar decisiones accedidas recientemente
        if mem["category"] == "decisions" and mem["access_count"] > 3:
            continue
        
        if adjusted_relevance < threshold or age > max_age_days:
            to_remove.append(mem["id"])
    
    remove_from_all_backends(to_remove)
    return len(to_remove)
```

### 3. Gestión de ventana de contexto

```python
def build_context_window(query: str, max_tokens: int = 8000):
    """
    Construye la ventana de contexto óptima para una query.
    Prioriza memorias por relevancia y recencia.
    """
    # Paso 1: Recuperar candidatos
    candidates = retrieve_memories(query, top_k=20)
    
    # Paso 2: Comprimir y seleccionar
    context_parts = []
    token_count = 0
    
    for mem in candidates:
        mem_tokens = count_tokens(mem["content"])
        if token_count + mem_tokens > max_tokens:
            # Intentar comprimir
            compressed = summarize(mem["content"], max_tokens=mem_tokens // 2)
            mem_tokens = count_tokens(compressed)
            if token_count + mem_tokens > max_tokens:
                break
            context_parts.append(compressed)
        else:
            context_parts.append(mem["content"])
        token_count += mem_tokens
    
    return "\n---\n".join(context_parts)
```

### 4. Persistencia entre sesiones

```yaml
# .openclaw/memory/session-state.yaml
session:
  id: "sess_20260207_abc123"
  started: "2026-02-07T10:30:00Z"
  last_active: "2026-02-07T14:22:00Z"
  
  active_memories:
    - id: "mem_001"
      category: "project_state"
      content: "Trabajando en migración de DB PostgreSQL a SQLite"
      relevance: 0.95
    
    - id: "mem_002"
      category: "preferences"
      content: "Usuario prefiere TypeScript sobre JavaScript"
      relevance: 0.88
    
    - id: "mem_003"
      category: "decisions"
      content: "Se decidió usar FastAPI en lugar de Flask por async support"
      relevance: 0.92

  continuation_context: |
    Resumen de la última sesión: Se completó la migración del esquema
    de base de datos. Pendiente: migración de datos y tests de integración.
```

## Mejores prácticas

1. **Categorizar siempre**: Asigna categoría a cada memoria para facilitar búsqueda y poda
2. **No almacenar duplicados**: Antes de guardar, busca memorias similares (cosine similarity > 0.92) y actualiza en su lugar
3. **Hacer poda regular**: Ejecuta `prune_memories()` al inicio de cada sesión para mantener relevancia alta
4. **Comprimir memorias antiguas**: Resumir memorias con más de 30 días en versiones más cortas
5. **Separar hechos de opiniones**: Los `facts` deben ser verificables; las interpretaciones van en `learnings`
6. **Versionado con Git-Notes**: Vincula decisiones importantes a commits específicos para trazabilidad
7. **Limitar embeddings costosos**: Cachea embeddings y reutiliza cuando el contenido no cambie
8. **Backup periódico**: Exporta el store de memoria regularmente en formato portable

## Ejemplos

### Ejemplo 1: Recordar preferencias del usuario

```
Usuario: "Siempre quiero que uses Prettier con tabs de 4 espacios"

→ store_memory(
    content="El usuario prefiere Prettier con indentación de 4 espacios (tabs)",
    category="preferences",
    metadata={"source": "user_instruction", "confidence": 1.0}
  )
```

### Ejemplo 2: Persistir estado de proyecto

```
Agente detecta: El proyecto usa monorepo con pnpm workspaces

→ store_memory(
    content="Proyecto configurado como monorepo con pnpm workspaces. Packages: api/, web/, shared/",
    category="project_state",
    metadata={"source": "file_analysis", "files": ["pnpm-workspace.yaml", "package.json"]}
  )
```

### Ejemplo 3: Búsqueda semántica en nueva sesión

```
Nueva sesión. Usuario pregunta: "¿Qué formato de indentación uso?"

→ results = retrieve_memories("formato indentación código estilo", category="preferences")
→ Resultado: "El usuario prefiere Prettier con indentación de 4 espacios (tabs)"
→ Agente aplica automáticamente la preferencia
```

### Ejemplo 4: Gestión de ventana de contexto

```
Sesión larga, ventana de contexto al 80%.

→ build_context_window("migración base de datos", max_tokens=4000)
→ Selecciona las 5 memorias más relevantes sobre la migración
→ Comprime las menos relevantes
→ Inyecta contexto optimizado en el prompt
```

### Ejemplo 5: Poda automática

```
Inicio de sesión → prune_memories(threshold=0.15, max_age_days=60)

Resultado:
  - 12 memorias eliminadas (bajo relevance_score)
  - 3 memorias comprimidas (antiguas pero accedidas)
  - 45 memorias activas preservadas
```
