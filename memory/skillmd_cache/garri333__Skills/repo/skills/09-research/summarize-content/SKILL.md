---
name: summarize-content
version: 1.0.0
description: Resumir y sintetizar inteligentemente URLs, documentos, transcripciones y texto extenso. Usa cuando necesites extraer los puntos clave de un contenido largo o preparar un brief conciso.
tags: [summarization, content, nlp, extraction, brief, synthesis]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Summarize Content Skill

## Cuándo usar esta skill
- El usuario manda una URL y pide un resumen
- Se necesita extraer los puntos clave de un documento largo
- Preparar un executive brief de un report
- Condensar una transcripción de reunión
- Resumir un hilo de emails o Slack

## Tipos de resumen y cuándo usar cada uno

| Tipo | Cuándo | Longitud |
|------|--------|----------|
| Executive summary | Reports de empresa, investigaciones | 150-300 palabras |
| TL;DR | Posts, artículos técnicos | 2-5 frases |
| Bullet points | Reuniones, webinars, documentos técnicos | 5-15 bullets |
| Infographic summary | Contenido visual, datos | Estructura tabular |
| Thread/hilo | Posts de redes sociales, emails | 3-7 posts/bullets |

## Protocolo de resumen

### Paso 1: Entender el tipo de contenido
```
Antes de resumir, identificar:
1. Tipo de contenido: artículo, transcript, paper, email, doc legal, datos...
2. Audiencia del resumen: técnico, ejecutivo, general
3. Propósito: decisión, información, publicación, archivo...
4. Longitud objetivo del resumen
```

### Paso 2: Extraer los elementos clave
```
Para cualquier tipo de contenido, extraer:
- Qué: El hecho/conclusión/argumento central
- Por qué: El contexto o motivación
- Cómo: El método o proceso (si aplica)
- Quién: Protagonistas relevantes
- Cuándo/Dónde: Contexto temporal/espacial (si aplica)
- Datos clave: Números, estadísticas, fechas específicas
- Conclusión/CTA: Qué hay que hacer o qué implica
```

### Paso 3: Estructura según audiencia

#### Para ejecutivos / directores
```
[RESUMEN EJECUTIVO — X palabras]

**Puntos clave:**
- [Hallazgo 1 con dato concreto]
- [Hallazgo 2 con dato concreto]
- [Hallazgo 3 con dato concreto]

**Implicaciones:**
[1-2 frases sobre qué significa para el negocio]

**Acciones recomendadas:**
1. [Acción concreta]
2. [Acción concreta]
```

#### Para equipos técnicos
```
## TL;DR
[1-2 frases directas con la conclusión]

## Contexto
[Por qué importa esto]

## Detalles técnicos
- [Detalle 1]
- [Detalle 2]

## Próximos pasos
- [ ] [Acción técnica concreta]
```

#### Para publicación (redes sociales, blog)
```
[Hook - primera frase que engancha]

[Puntos principales - 3-5 bullets o párrafos cortos]

[Conclusión o insight]

[CTA si aplica]
```

## Resumir una URL

```python
import httpx
from bs4 import BeautifulSoup
import re

def fetch_article(url: str) -> str:
    """Extrae el texto principal de una URL"""
    response = httpx.get(url, headers={'User-Agent': 'Mozilla/5.0'}, follow_redirects=True)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Eliminar elementos no relevantes
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'ad']):
        tag.decompose()
    
    # Intentar encontrar el artículo principal
    article = (
        soup.find('article') or
        soup.find(class_=re.compile(r'article|post|content|main')) or
        soup.find('main') or
        soup.body
    )
    
    if article:
        text = article.get_text(separator='\n', strip=True)
        # Limpiar líneas vacías múltiples
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text[:15000]  # Limitar para context window
    
    return soup.get_text(separator='\n', strip=True)[:15000]


def summarize_url(url: str, style: str = "bullets", audience: str = "general") -> str:
    """
    Resumir el contenido de una URL
    
    Args:
        url: URL a resumir
        style: "bullets" | "executive" | "tldr" | "thread"
        audience: "general" | "technical" | "executive"
    """
    content = fetch_article(url)
    
    prompts = {
        "tldr": f"Resume este artículo en máximo 3 frases. Ve directo al punto, sin contexto innecesario:\n\n{content}",
        
        "bullets": f"""Resume los puntos clave de este artículo como bullet points:
- Usa máximo 10 bullets
- Cada bullet: 1 idea concreta y específica
- Incluye datos/números cuando existan
- El último bullet debe ser la conclusión o implicación

Artículo:\n{content}""",
        
        "executive": f"""Escribe un executive summary (200 palabras máximo) de este contenido:
Formato:
**Resumen:** [2-3 frases]
**Puntos clave:** [3-5 bullets con datos]
**Conclusión:** [1 frase de implicación práctica]

Contenido:\n{content}""",
        
        "thread": f"""Convert este artículo en un hilo de Twitter/LinkedIn de 5-7 posts:
- Post 1: Hook que haga querer leer más
- Posts 2-6: Un punto clave cada uno, con dato concreto
- Post final: Conclusión + "¿Qué opinas?"
Usa números (1/7, 2/7...) al inicio de cada post.

Artículo:\n{content}"""
    }
    
    # Aquí llamarías a tu LLM preferido con el prompt
    prompt = prompts.get(style, prompts["bullets"])
    
    return prompt  # Devuelve el prompt para usar con tu LLM


# Uso
url = "https://example.com/article"
prompt = summarize_url(url, style="executive")
# response = llm.generate(prompt)
```

## Resumir documentos largos (chunking)

```python
def hierarchical_summary(text: str, max_chunk_size: int = 4000) -> str:
    """
    Para documentos muy largos: resumir por secciones, luego el resumen de resúmenes
    """
    # Dividir en chunks con overlap
    chunks = []
    words = text.split()
    chunk_words = max_chunk_size // 5  # ~5 chars por palabra
    overlap = chunk_words // 10
    
    for i in range(0, len(words), chunk_words - overlap):
        chunk = ' '.join(words[i:i + chunk_words])
        chunks.append(chunk)
    
    # Resumen de cada chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        prompt = f"[Sección {i+1}/{len(chunks)}] Resume los puntos clave de esta sección en 3-5 bullets:\n\n{chunk}"
        # summary = llm.generate(prompt)
        # chunk_summaries.append(summary)
    
    # Resumen final
    combined = "\n\n".join(chunk_summaries)
    final_prompt = f"A partir de estos resúmenes de secciones, crea un resumen ejecutivo coherente del documento completo:\n\n{combined}"
    
    return final_prompt


def summarize_meeting_transcript(transcript: str) -> str:
    """Resumir una transcripción de reunión"""
    prompt = f"""Resume esta transcripción de reunión con el siguiente formato:

## Resumen de reunión

**Fecha:** [si se menciona]
**Participantes:** [lista de personas que hablan]
**Duración:** [si se menciona]

### Puntos tratados
- [Tema 1]: [Qué se discutió, qué se decidió]
- [Tema 2]: [Qué se discutió, qué se decidió]

### Decisiones tomadas
- [ ] [Decisión 1]
- [ ] [Decisión 2]

### Action items
- [ ] [Tarea] — Responsable: [nombre] — Fecha límite: [fecha si se menciona]

### Próximos pasos
[Resumen de lo que pasa después de esta reunión]

---
Transcripción:
{transcript}"""
    
    return prompt
```

## Fórmulas de resumen por tipo

### Artículo técnico / paper
```
[Problema que resuelve] + [Método usado] + [Resultado principal] + [Implicación práctica]
```

### Post de blog / opinion piece
```
[Tesis central] + [Argumento principal] + [Ejemplo o dato clave] + [Conclusión o call to action]
```

### Email o conversación
```
[Contexto] + [Lo que pide / propone] + [Puntos de acción requeridos]
```

### Report o informe
```
[Objetivo del report] + [Hallazgos principales (con datos)] + [Conclusión y recomendaciones]
```

### Video / podcast / webinar
```
[Tema] + [Speaker y credenciales] + [3-5 insights clave] + [Recurso o referencia más útil]
```

## Referencias
- [readability (npm)](https://github.com/mozilla/readability) — Extrae contenido limpio de páginas web
- [newspaper3k (Python)](https://newspaper.readthedocs.io/) — Extrae artículos de noticias
- [trafilatura (Python)](https://trafilatura.readthedocs.io/) — Extracción de texto web
