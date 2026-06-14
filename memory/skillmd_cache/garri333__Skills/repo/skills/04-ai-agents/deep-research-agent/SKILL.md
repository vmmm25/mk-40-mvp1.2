---
name: deep-research-agent
version: 1.0.0
description: Agente de investigación profunda para tareas complejas de múltiples pasos. Usa cuando necesites respuestas exhaustivas sobre un tema, comparativas detalladas, o síntesis de fuentes múltiples.
tags: [research, agents, deep-research, gemini, perplexity, analysis, synthesis]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Deep Research Agent Skill

## Cuándo usar esta skill
- El usuario pide una investigación exhaustiva sobre un tema
- Se necesitan comparativas detalladas (tecnologías, productos, servicios)
- Se pide sintetizar información de múltiples fuentes
- El usuario quiere entender un tema complejo en profundidad
- Se necesita un estado del arte o review de literatura

## Protocolo de investigación profunda

### Fase 1: Descomposición del tema
```
Antes de buscar, descompón la pregunta en:
1. Pregunta principal
2. Sub-preguntas derivadas (3-7)
3. Términos de búsqueda alternativos
4. Perspectivas relevantes (técnica, comercial, histórica, etc.)
5. Tipo de fuentes necesarias (primarias, secundarias, datos, opiniones)
```

### Fase 2: Estrategia de búsqueda
```
Por cada sub-pregunta:
1. Formular variaciones de búsqueda
2. Identificar sitios/dominios especializados
3. Buscar tanto la tesis como la antítesis
4. Buscar datos actualizados vs perspectiva histórica
```

### Fase 3: Síntesis
```
1. Agrupar hallazgos por sub-tema
2. Identificar consensos y controversias
3. Pesar credibilidad de fuentes
4. Identificar gaps de información
5. Formular conclusiones con nivel de confianza
```

## Agentes de sub-investigación

### Usando Gemini CLI
```bash
gemini -p "Investiga en profundidad: [TEMA]. 
Estructura tu respuesta con:
1. Resumen ejecutivo (3 párrafos)
2. Contexto histórico y evolución
3. Estado actual (datos concretos, ejemplos)
4. Actores principales y sus posiciones
5. Tendencias emergentes
6. Controversias o debates activos
7. Conclusiones con nivel de confianza
8. Fuentes recomendadas para profundizar

Sé específico, con números y fechas cuando sea posible."
```

### Usando Perplexity API
```python
import requests

def deep_research(topic: str) -> dict:
    """
    Usa Perplexity para investigación con fuentes verificadas
    """
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"},
        json={
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un investigador experto. Usa fuentes actualizadas y cita URLs."
                },
                {
                    "role": "user", 
                    "content": f"Investiga exhaustivamente: {topic}\n\nIncluye datos concretos, fechas y fuentes."
                }
            ],
            "return_citations": True,
            "return_related_questions": True
        }
    )
    return response.json()
```

### Usando Exa AI (búsqueda semántica avanzada)
```python
from exa_py import Exa

exa = Exa(api_key=EXA_API_KEY)

def research_with_exa(query: str, num_results: int = 10):
    # Búsqueda con contenido completo
    results = exa.search_and_contents(
        query,
        type="neural",           # Búsqueda semántica
        use_autoprompt=True,     # Optimiza la query automáticamente
        num_results=num_results,
        text=True,               # Obtiene contenido completo
        highlights=True,         # Obtiene fragmentos relevantes
        start_published_date="2023-01-01"  # Solo contenido reciente
    )
    
    return [{
        "title": r.title,
        "url": r.url,
        "score": r.score,
        "text": r.text[:2000],  # Primeros 2000 chars
        "highlights": r.highlights
    } for r in results.results]
```

## Template para investigación estructurada

```markdown
# Investigación: [TEMA]
Fecha: [HOY]
Objetivo: [QUÉ NECESITA DECIDIR/SABER EL USUARIO]
Audiencia: [A QUIÉN VA DIRIGIDA]

---

## 1. Resumen ejecutivo
[3 párrafos con los hallazgos más importantes]

**Conclusión principal:** [Una oración con la conclusión clave]
**Nivel de confianza:** [Alto / Medio / Bajo] — [Razón]

---

## 2. Contexto y antecedentes
[Por qué este tema es relevante ahora, historia breve]

---

## 3. Análisis detallado

### 3.1 [Sub-tema 1]
**Hallazgos clave:**
- [Hallazgo con dato concreto y fuente]
- [Hallazgo con dato concreto y fuente]

**Implicaciones:**
[Qué significa esto para el usuario]

### 3.2 [Sub-tema 2]
...

---

## 4. Comparativa / Análisis de opciones

| Criterio | Opción A | Opción B | Opción C |
|----------|----------|----------|----------|
| [K1]     | [V]      | [V]      | [V]      |
| [K2]     | [V]      | [V]      | [V]      |

---

## 5. Perspectivas divergentes
**A favor de [X]:**
- [Argumento 1]

**En contra / Alternativa:**
- [Contra-argumento 1]

---

## 6. Tendencias y outlook
[Qué se espera que cambie en los próximos 6-24 meses]

---

## 7. Recomendaciones
1. [Acción recomendada 1 - con justificación]
2. [Acción recomendada 2]

---

## 8. Fuentes consultadas
- [Fuente 1 - URL - Fecha]
- [Fuente 2 - URL - Fecha]

## 9. Para profundizar
- [Recurso de alta calidad 1]
- [Recurso de alta calidad 2]
```

## Patrones de búsqueda efectivos

### Búsquedas por intención
```
Factual:      "[tema] statistics 2024 site:statista.com OR site:ourworldindata.org"
Comparativa:  "[A] vs [B] comparison pros cons 2024"
Técnica:      "[tema] how it works explained site:github.com OR site:arxiv.org"
Crítica:      "[producto/empresa] problems issues criticism"
Reciente:     "[tema] after:2024-01-01 news"
Experta:      "[tema] expert opinion researcher academic"
```

### Fuentes por tipo de información
```
Datos estadísticos:  Statista, Our World in Data, World Bank, Eurostat
Investigación:       arXiv, PubMed, Google Scholar, ResearchGate
Tecnología:          GitHub, Hacker News, Stack Overflow, dev.to
Noticias:            Reuters, Bloomberg, TechCrunch, Wired
Legal/Regulatorio:   EUR-Lex, BOE, GDPR.eu, CNIL
Empresarial:         Crunchbase, LinkedIn, Yahoo Finance, SEC EDGAR
```

## Anti-patrones de investigación

**Evitar:**
- ❌ Conformarse con la primera página de resultados
- ❌ Citar como fuente solo Wikipedia
- ❌ Mezclar datos de años diferentes sin notar las diferencias
- ❌ Presentar la perspectiva mayoritaria sin mencionar alternativas
- ❌ No verificar si la información sigue siendo vigente
- ❌ Hacer afirmaciones definitivas sobre áreas con genuina incertidumbre

**Siempre:**
- ✅ Buscar la fuente original (no la noticia que cita la noticia que cita el estudio)
- ✅ Contrastar desde mínimo 3 fuentes diferentes
- ✅ Declarar explícitamente el nivel de certeza de cada afirmación
- ✅ Distinguir hechos confirmados de interpretaciones

## Entregables según el caso

| Caso de uso | Formato de entrega |
|-------------|-------------------|
| Decisión técnica | Tabla comparativa + pros/cons + recomendación |
| Brief ejecutivo | 1 página: resumen + conclusiones + acciones |
| Investigación de mercado | Análisis competitivo + datos de tamaño + trends |
| Due diligence | Checklist de riesgos + verificación de claims |
| Content research | Outline estructurado + datos clave + ángulo único |
| Technical deep dive | Explicación técnica + ejemplos de código + refs |
