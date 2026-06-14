---
name: web-search-exa
version: 1.0.0
description: Búsqueda web semántica y de código con Exa AI. Usa cuando necesites encontrar contenido por significado (no solo palabras clave), buscar repos de GitHub similares, o hacer investigación con contenido completo de páginas.
tags: [search, exa, semantic-search, research, web, code, api]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Web Search Exa Skill

## Cuándo usar esta skill
- Búsqueda semántica (por concepto, no solo palabras exactas)
- Encontrar artículos similares a uno dado (similares por contenido)
- Buscar repositorios de código con funcionalidad específica
- Investigación con extracción automática del contenido completo
- Búsqueda con filtros por fecha, dominio, tipo de contenido

## Setup

```bash
pip install exa-py
# O
npm install exa-js

# API Key en: https://exa.ai/
export EXA_API_KEY="tu-api-key"
```

## Uso con Python

```python
from exa_py import Exa
import os

exa = Exa(api_key=os.environ.get("EXA_API_KEY"))
```

## Tipos de búsqueda

### 1. Búsqueda semántica (neural)
Para buscar por concepto o significado, no solo palabras exactas.

```python
# Búsqueda neural — entiende intención y contexto
results = exa.search(
    "frameworks para autenticación en aplicaciones modernas",
    type="neural",
    num_results=10,
    use_autoprompt=True  # Exa optimiza la query automáticamente
)

for r in results.results:
    print(f"{r.title} — {r.url} (score: {r.score:.3f})")
```

### 2. Búsqueda por palabras clave (keyword)
Para búsquedas exactas o términos técnicos específicos.

```python
results = exa.search(
    "React Server Components tutorial 2024",
    type="keyword",  
    num_results=10
)
```

### 3. Búsqueda con contenido completo
Obtiene el texto completo de las páginas, no solo el snippet.

```python
results = exa.search_and_contents(
    "mejores prácticas para APIs REST en 2024",
    type="neural",
    use_autoprompt=True,
    num_results=5,
    text=True,              # Texto completo
    text_contents_options={
        "max_characters": 3000,   # Limitar para context window
        "include_html_tags": False
    },
    highlights=True,        # Fragmentos más relevantes
    highlights_contents_options={
        "num_sentences": 3,       # 3 frases por highlight
        "highlights_per_url": 2   # 2 highlights por resultado
    }
)

for r in results.results:
    print(f"\n=== {r.title} ===")
    print(f"URL: {r.url}")
    if r.highlights:
        for h in r.highlights:
            print(f"📌 {h}")
    if r.text:
        print(f"Texto: {r.text[:500]}...")
```

### 4. Find Similar (buscar contenido similar a una URL)
```python
# Encuentra artículos similares a una URL específica
similar = exa.find_similar(
    "https://react.dev/blog/2023/03/22/react-labs-march-2023",
    num_results=5,
    exclude_source_domain=True  # No incluir el mismo dominio
)

for r in similar.results:
    print(f"{r.title} — {r.url}")
```

### 5. Búsqueda de código en GitHub
```python
# Buscar repositorios o código específico
code_results = exa.search(
    "Python library for parsing PDF with table extraction",
    type="neural",
    include_domains=["github.com"],
    num_results=10,
    use_autoprompt=True
)

# Buscar ejemplos de implementación específica
implementation_results = exa.search_and_contents(
    "implementation of rate limiting middleware Express.js",
    type="neural",
    include_domains=["github.com", "gist.github.com"],
    num_results=5,
    highlights=True
)
```

## Filtros avanzados

```python
# Filtrar por dominio (incluir)
results = exa.search(
    "machine learning deployment best practices",
    include_domains=["huggingface.co", "pytorch.org", "tensorflow.org"],
    num_results=10
)

# Filtrar por dominio (excluir)
results = exa.search(
    "Python packaging tutorial",
    exclude_domains=["medium.com", "dev.to"],  # Evitar blogs de baja calidad
    num_results=10
)

# Filtrar por fecha
from datetime import datetime, timedelta

results = exa.search(
    "AI agents framework comparison",
    start_published_date=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
    end_published_date=datetime.now().strftime("%Y-%m-%d"),
    num_results=10
)

# Filtrar por categoría
results = exa.search(
    "startup fundraising strategies",
    category="tweet",  # tweet, paper, article, github, personal site
    num_results=10
)
```

## Patrón: Research assistant

```python
def research_topic(query: str, depth: str = "standard") -> dict:
    """
    Investigar un tema con Exa
    depth: "quick" | "standard" | "deep"
    """
    
    configs = {
        "quick": {"num_results": 3, "text": False, "highlights": True},
        "standard": {"num_results": 7, "text": True, "highlights": True},
        "deep": {"num_results": 15, "text": True, "highlights": True},
    }
    
    config = configs.get(depth, configs["standard"])
    
    results = exa.search_and_contents(
        query,
        type="neural",
        use_autoprompt=True,
        highlights=config["highlights"],
        text=config["text"],
        text_contents_options={"max_characters": 2000} if config["text"] else None,
        num_results=config["num_results"]
    )
    
    research = {
        "query": query,
        "total_results": len(results.results),
        "sources": []
    }
    
    for r in results.results:
        source = {
            "title": r.title,
            "url": r.url,
            "published": r.published_date,
            "relevance_score": r.score,
        }
        if r.highlights:
            source["highlights"] = r.highlights
        if r.text:
            source["content"] = r.text[:2000]
        
        research["sources"].append(source)
    
    return research


# Uso:
result = research_topic("GDPR compliance for AI systems 2024", depth="deep")

# Formatear para LLM
context = "\n\n".join([
    f"## {s['title']}\n{s['url']}\n\n{chr(10).join(s.get('highlights', []))}"
    for s in result["sources"]
])
```

## Comparativa con otras herramientas de búsqueda

| Feature | Exa | Brave Search | Perplexity | Google |
|---------|-----|--------------|------------|--------|
| Búsqueda semántica | ✅ Excelente | ⚠️ Básica | ✅ Buena | ⚠️ Básica |
| Contenido completo | ✅ Sí | ❌ No (nativo) | ⚠️ Parcial | ❌ No |
| Find Similar | ✅ Sí | ❌ No | ❌ No | ❌ No |
| Búsqueda de código | ✅ Muy buena | ⚠️ Básica | ⚠️ Básica | ✅ Buena |
| Filtros por dominio | ✅ Sí | ✅ Sí | ❌ No | ✅ Sí |
| Filtros por fecha | ✅ Sí | ✅ Sí | ✅ Sí | ✅ Sí |
| Precio | Pago (free tier) | Freemium | Freemium | Free (limitado) |
| Mejora con AI | ✅ autoprompt | ❌ No | ✅ Sí | ❌ No |

**Cuándo usar Exa vs alternativas:**
- **Exa**: Investigación semántica, find similar, contenido completo de artículos
- **Brave**: Búsqueda general rápida, privacidad, noticias recientes
- **Perplexity**: Preguntas directas con respuesta sintetizada + fuentes
- **Google**: Cobertura máxima, búsquedas muy específicas o locales

## Referencias
- [Exa API Documentation](https://docs.exa.ai/)
- [Exa Python SDK](https://github.com/exa-labs/exa-py)
- [Exa console](https://exa.ai/) — para obtener API key
