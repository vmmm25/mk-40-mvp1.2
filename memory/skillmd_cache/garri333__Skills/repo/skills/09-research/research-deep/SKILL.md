---
name: research-deep
version: 1.0.0
description: Investigación ultra-profunda sobre temas complejos usando múltiples fuentes y agentes. Usa cuando necesites el nivel más exhaustivo de investigación posible, combinando búsqueda, lectura de papers, síntesis y conclusiones accionables.
tags: [research, deep-research, gemini, perplexity, synthesis, multi-source, academic]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Research Deep Skill

## Cuándo usar esta skill vs `deep-research-agent`
- `deep-research-agent`: Una investigación estructurada con buenos resultados
- `research-deep`: Nivel máximo de exhaustividad — múltiples agentes, papers académicos, estado del arte

## El processo de investigación ultra-profunda

### Al recibir una petición de investigación profunda:
```
1. SCOPING (5 min):
   - ¿Es una pregunta factual? → Diferentes herramientas
   - ¿Es técnica? → GitHub, arXiv, docs oficiales
   - ¿Es de mercado? → CBInsights, Crunchbase, análisis sectoriales
   - ¿Es académica? → PubMed, arXiv, Semantic Scholar
   - ¿Es normativa? → EUR-Lex, CNMC, organismos reguladores

2. PLAN DE BÚSQUEDA (3+ queries distintas por sub-tema):
   - Query A: términos exactos
   - Query B: sinónimos/alternativas conceptuales
   - Query C: negación (buscar críticas/contra-argumentos)
   - Query D: en inglés si el tema tiene más literatura en ese idioma

3. SÍNTESIS:
   - Encontrar puntos de consenso entre fuentes
   - Identificar controversias activas
   - Pesar credibilidad de fuentes
   - Declarar incertidumbres explícitamente

4. VALIDACIÓN:
   - Cross-checking de datos críticos
   - Verificar que las fuentes primarias dicen lo que las secundarias afirman
   - Actualidad de la información (especialmente en tech/regulación)
```

## Herramientas por tipo de investigación

### Investigación técnica / software
```bash
# Buscar en GitHub con linguaged query
gh search repos "TERM" --language=python --stars=>100 --sort=updated

# Buscar issues/discussions para contexto real
gh search issues "TERM" --repo=REPO --label=enhancement

# Leer documentación oficial
curl https://rawgit.com/.../README.md | head -100

# Buscar en Hacker News
curl "https://hn.algolia.com/api/v1/search?query=TERM&tags=story&hitsPerPage=5" | jq '.hits[] | {title, url, points}'
```

### Investigación académica
```python
import requests

def search_arxiv(query: str, max_results: int = 10) -> list:
    """Buscar papers en arXiv"""
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    
    response = requests.get(url, params=params)
    
    # Parsear XML (simplificado)
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response.text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    
    papers = []
    for entry in root.findall("atom:entry", ns):
        papers.append({
            "title": entry.find("atom:title", ns).text.strip(),
            "summary": entry.find("atom:summary", ns).text.strip()[:500],
            "published": entry.find("atom:published", ns).text[:10],
            "authors": [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)],
            "url": entry.find("atom:id", ns).text,
        })
    
    return papers


def search_semantic_scholar(query: str, year_from: int = 2020) -> list:
    """Buscar en Semantic Scholar (papers con citations)"""
    response = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={
            "query": query,
            "limit": 10,
            "fields": "title,year,citationCount,abstract,authors,openAccessPdf",
            "publicationDateOrYear": f"{year_from}:"
        }
    )
    return response.json().get("data", [])
```

### Investigación de mercado y empresa
```python
def research_company(company_name: str) -> dict:
    """
    Investigar una empresa desde múltiples ángulos
    """
    queries = {
        "crunchbase": f"site:crunchbase.com {company_name}",
        "funding": f"{company_name} funding raise investor series",
        "tech_stack": f"{company_name} technology stack engineering blog",
        "reviews": f"{company_name} reviews glassdoor trustpilot",
        "news": f"{company_name} news announcement 2024",
        "competitors": f"{company_name} competitors alternatives comparison",
        "linkedin": f"site:linkedin.com/company {company_name}",
    }
    # Ejecutar cada query con Exa o Brave Search
    # (ver skills web-search-exa y web-search-brave)
    return queries


def market_research_queries(market: str) -> list:
    """Generar queries de investigación de mercado"""
    return [
        f"{market} market size 2024 billion",
        f"{market} market growth rate CAGR forecast",
        f"{market} top players competitors market share",
        f"{market} industry trends emerging technology",
        f"{market} challenges barriers problems",
        f"{market} regulatory environment compliance",
        f"disruption {market} startups innovation",
        f"{market} M&A activity acquisitions 2023 2024",
    ]
```

## Pipeline completo de deep research

```python
from dataclasses import dataclass, field
from typing import Callable
import json

@dataclass
class ResearchPlan:
    topic: str
    objective: str             # Qué debe poder decidir/hacer el usuario con esto
    depth: str = "deep"        # "quick", "standard", "deep", "exhaustive"
    sub_topics: list = field(default_factory=list)
    sources_required: list = field(default_factory=list)
    output_format: str = "report"  # "report", "brief", "comparison", "summary"


def create_research_plan(topic: str, objective: str) -> ResearchPlan:
    """
    Crear un plan de investigación estructurado
    (En la práctica, esto lo generaría el LLM dado el topic)
    """
    plan = ResearchPlan(
        topic=topic,
        objective=objective,
        sub_topics=[
            f"Definición y conceptos clave de {topic}",
            f"Estado actual y tendencias de {topic}",
            f"Actores principales en {topic}",
            f"Debates y controversias sobre {topic}",
            f"Perspectiva práctica: cómo aplica a {objective}",
        ],
        sources_required=["web", "docs", "academic"],
    )
    
    return plan


def execute_research(plan: ResearchPlan, search_fn: Callable) -> dict:
    """
    Ejecutar el plan de investigación
    search_fn: función que toma una query string y retorna resultados
    """
    results = {
        "topic": plan.topic,
        "objective": plan.objective,
        "findings": {}
    }
    
    for sub_topic in plan.sub_topics:
        # 3 queries por sub-tema
        queries = [
            sub_topic,
            f"{sub_topic} expert perspective analysis",
            f"{sub_topic} problems challenges criticism",
        ]
        
        sub_results = []
        for query in queries:
            found = search_fn(query)
            sub_results.extend(found)
        
        results["findings"][sub_topic] = sub_results
    
    return results
```

## Formato de entregable para deep research

```markdown
# Deep Research: [TEMA]

**Encargo:** [Qué necesitaba el usuario]
**Fecha:** [Fecha]  
**Profundidad:** Exhaustiva — [N fuentes consultadas]
**Nivel de confianza general:** [Alto/Medio/Bajo]

---

## 🎯 Conclusiones ejecutivas (para quien no leerá el resto)

**Bottom line:** [1-3 frases con LO MÁS IMPORTANTE]

**Acciones recomendadas:**
1. [Acción concreta — razón]
2. [Acción concreta — razón]

**Incertidumbres clave:** 
- [Lo que NO pudo confirmarse con certeza]

---

## 📊 Hallazgos por dimensión

### 1. [Dimensión 1]
**Consenso:** [Lo que la mayoría de fuentes coincide]
**Controversia:** [Donde hay debate]
**Datos clave:**
- [Dato concreto con fuente y fecha]

### 2. [Dimensión 2]
...

---

## 🔍 Fuentes consultadas (por relevancia)

### Tier 1 — Alta credibilidad
- [Fuente 1 — URL — Fecha — Por qué es fiable]

### Tier 2 — Buena referencia
- [Fuente 2 — URL]

### Fuentes contradictorias
- [Fuente que dice algo distinto — URL — Por qué diverge]

---

## ❓ Preguntas sin respuesta clara
1. [Pregunta que las fuentes no resolvieron]
2. [Controversy activa sin resolución]

---

## 🔗 Para profundizar más
- [Recurso 1 — Descripción]
- [Recurso 2 — Descripción]
```

## Anti-patrones de investigación profunda

```
❌ Confirmar sesgos: Solo buscar fuentes que apoyen la hipótesis inicial
❌ Wikipedia como fuente primaria (solo para orientación, nunca para citar)
❌ Artículos de blog sin credenciales como "estudios"
❌ Datos sin fecha (especialmente en tech/mercados que cambian rápido)
❌ Generalizar desde un solo caso o estudio
❌ No distinguir entre correlación y causalidad
❌ Ignorar el contexto geográfico/temporal de los datos

✅ Buscar activamente evidencia contraria a tu conclusión inicial
✅ Identificar quién financia cada estudio o análisis
✅ Triangular: misma afirmación desde 3+ fuentes independientes
✅ Declarar explícitamente el nivel de certeza de cada claim
✅ La fecha de los datos importa siempre — mencionarla
```

## Referencias
- [arXiv](https://arxiv.org/) — Papers gratuitos en ciencias y tech
- [Semantic Scholar](https://www.semanticscholar.org/) — Papers con métricas de impacto
- [Google Scholar](https://scholar.google.com/) — Búsqueda académica amplia
- [Our World in Data](https://ourworldindata.org/) — Datos globales visualizados
- [SSRN](https://ssrn.com/) — Papers de economía, finanzas, derecho
