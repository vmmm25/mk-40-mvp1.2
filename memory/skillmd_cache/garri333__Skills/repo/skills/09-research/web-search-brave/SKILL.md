---
name: web-search-brave
version: 1.0.0
description: Búsqueda web vía Brave Search API para encontrar documentación, hechos, o cualquier contenido web. Usa cuando necesites información actualizada de internet sin abrir un navegador.
tags: [search, web, research, brave, api, information]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Brave Search Skill

## Cuándo usar esta skill

- Buscar documentación de una librería o API
- Verificar hechos o estadísticas recientes
- Encontrar ejemplos de código en la web
- Research de competidores o mercado
- Buscar artículos, noticias, o papers

## Setup

Requiere API key de Brave Search:
- Obtener en: https://api.search.brave.com/
- Plan gratuito: 2.000 búsquedas/mes
- Variable de entorno: `BRAVE_API_KEY`

## Uso básico

```python
import requests
import os

def brave_search(query: str, count: int = 5) -> list[dict]:
    """Busca en la web usando Brave Search API."""
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.environ["BRAVE_API_KEY"]
    }
    
    params = {
        "q": query,
        "count": count,
        "country": "es",  # "es" para España, "us" para EEUU
        "lang": "es",     # Idioma de los resultados
        "safesearch": "moderate"
    }
    
    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    
    data = response.json()
    results = []
    
    for item in data.get("web", {}).get("results", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "description": item.get("description"),
            "published": item.get("page_age")
        })
    
    return results

# Uso:
results = brave_search("Python asyncio best practices 2026")
for r in results:
    print(f"📄 {r['title']}")
    print(f"   {r['url']}")
    print(f"   {r['description']}\n")
```

## Búsqueda con extracción de contenido

```python
import requests
from bs4 import BeautifulSoup

def search_and_extract(query: str, num_results: int = 3) -> list[dict]:
    """Busca y extrae el contenido textual de los primeros resultados."""
    search_results = brave_search(query, count=num_results)
    
    extracted = []
    for result in search_results:
        try:
            page = requests.get(result["url"], timeout=5, 
                               headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(page.content, 'html.parser')
            
            # Eliminar scripts y estilos
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            # Limpiar líneas vacías múltiples
            text = '\n'.join(line for line in text.split('\n') if line.strip())
            
            extracted.append({
                **result,
                "content": text[:3000]  # Primeros 3000 chars
            })
        except Exception as e:
            extracted.append({**result, "content": f"Error: {e}"})
    
    return extracted
```

## Tipos de búsqueda

```python
# Búsqueda de noticias recientes
params = {
    "q": query,
    "news_count": 5,  # Incluir resultados de noticias
    "freshness": "pd"  # pd = past day, pw = past week, pm = past month
}

# Búsqueda de imágenes
response = requests.get(
    "https://api.search.brave.com/res/v1/images/search",
    headers=headers,
    params={"q": query, "count": 5}
)

# Búsqueda de noticias (endpoint dedicado)
response = requests.get(
    "https://api.search.brave.com/res/v1/news/search",
    headers=headers,
    params={"q": query, "count": 5}
)
```

## Queries efectivas

```
# Específico > genérico
✅ "python fastapi jwt authentication example 2026"
❌ "python auth"

# Site-specific
"site:github.com fastapi starter template"
"site:stackoverflow.com asyncio gather exception handling"

# Búsqueda de documentación
"python requests library documentation timeout"
"nextjs 15 server components data fetching"

# Búsqueda de código
"github.com python web scraper playwright 2026"
```

## Limitaciones

- Rate limit: 1 request/segundo en plan gratuito
- No indexa sitios detrás de login
- Resultados pueden variar por región
- Para contenido muy reciente (<24h), puede no aparecer aún

## Alternativas

| Herramienta | Cuando usar |
|-------------|-------------|
| Brave Search | Búsqueda general, sin cookies requeridas |
| Exa AI | Búsqueda semántica, mejores resultados para código y papers |
| Perplexity | Cuando necesitas respuesta sintetizada con fuentes |
| Google Custom Search | Integración con ecosistema Google |

## Referencias
- [Brave Search API Docs](https://api.search.brave.com/app/documentation)
- [Brave Search (Clawdbot)](https://clawdbotskills.org/)
