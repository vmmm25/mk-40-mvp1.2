---
name: reddit
version: 1.0.0
description: Explorar y buscar Reddit en modo lectura usando endpoints JSON públicos sin autenticación. Usa cuando necesites monitorizar subreddits, buscar opiniones de comunidades o hacer research sobre tendencias.
tags: [reddit, social-media, research, community, scraping, monitoring, trends]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Reddit Read-Only Skill

## Acceso sin autenticación (endpoints JSON públicos)

```python
import requests
import time

# Reddit permite acceder a JSON añadiendo .json a cualquier URL
# No requiere API key para lectura básica

HEADERS = {"User-Agent": "MyAgent/1.0 (by u/yourusername)"}

def get_subreddit_posts(
    subreddit: str,
    sort: str = "hot",       # hot, new, top, rising
    limit: int = 25,
    time_filter: str = "day" # hour, day, week, month, year, all (solo para "top")
) -> list:
    """Obtener posts de un subreddit"""
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    params = {"limit": limit, "t": time_filter}
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    
    posts = []
    for post in response.json()["data"]["children"]:
        d = post["data"]
        posts.append({
            "title": d["title"],
            "author": d["author"],
            "score": d["score"],
            "upvote_ratio": d["upvote_ratio"],
            "num_comments": d["num_comments"],
            "url": d["url"],
            "permalink": f"https://reddit.com{d['permalink']}",
            "selftext": d.get("selftext", "")[:500],
            "created_utc": d["created_utc"],
            "flair": d.get("link_flair_text", ""),
        })
    
    return posts
```

## Búsqueda en Reddit

```python
def search_reddit(
    query: str,
    subreddit: str = None,    # None = buscar en todo Reddit
    sort: str = "relevance",  # relevance, hot, new, top, comments
    time_filter: str = "year",
    limit: int = 25,
) -> list:
    """Buscar posts por palabras clave"""
    if subreddit:
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {"q": query, "restrict_sr": "1", "sort": sort, "t": time_filter, "limit": limit}
    else:
        url = "https://www.reddit.com/search.json"
        params = {"q": query, "sort": sort, "t": time_filter, "limit": limit}
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    return [
        {
            "title": p["data"]["title"],
            "subreddit": p["data"]["subreddit"],
            "score": p["data"]["score"],
            "comments": p["data"]["num_comments"],
            "permalink": f"https://reddit.com{p['data']['permalink']}",
            "text": p["data"].get("selftext", "")[:300],
        }
        for p in response.json()["data"]["children"]
    ]
```

## Obtener comentarios de un post

```python
def get_post_comments(permalink: str, limit: int = 20) -> list:
    """Obtener comentarios top de un post"""
    # Convertir permalink relativo → URL JSON
    if not permalink.startswith("http"):
        permalink = f"https://reddit.com{permalink}"
    if not permalink.endswith(".json"):
        permalink += ".json"
    
    response = requests.get(permalink, headers=HEADERS, params={"limit": limit})
    data = response.json()
    
    if len(data) < 2:
        return []
    
    comments = []
    for comment in data[1]["data"]["children"]:
        if comment["kind"] == "t1":  # Solo comentarios reales (no "more")
            d = comment["data"]
            comments.append({
                "author": d["author"],
                "body": d["body"][:500],
                "score": d["score"],
                "depth": d["depth"],
            })
    
    return comments
```

## Monitorizar subreddits para research

```python
def monitor_subreddits(
    subreddits: list[str],
    keyword: str,
    min_score: int = 10
) -> list:
    """Encontrar posts relevantes en múltiples subreddits"""
    relevant = []
    
    for subreddit in subreddits:
        posts = search_reddit(query=keyword, subreddit=subreddit)
        for post in posts:
            if post["score"] >= min_score:
                relevant.append({**post, "subreddit": subreddit})
        
        time.sleep(1)  # Rate limit
    
    return sorted(relevant, key=lambda x: x["score"], reverse=True)


# Ejemplo: monitorizar opiniones sobre ciberseguridad
cyber_posts = monitor_subreddits(
    subreddits=["cybersecurity", "netsec", "sysadmin", "devops"],
    keyword="ISO 27001 implementation",
    min_score=50
)


def subreddit_sentiment_sample(subreddit: str, limit: int = 50) -> dict:
    """Análisis básico de sentimientos del top de un subreddit"""
    posts = get_subreddit_posts(subreddit, sort="top", limit=limit, time_filter="week")
    
    total_score = sum(p["score"] for p in posts)
    avg_comments = sum(p["num_comments"] for p in posts) / len(posts) if posts else 0
    
    # Palabras más frecuentes en títulos
    from collections import Counter
    import re
    words = " ".join(p["title"] for p in posts).lower()
    words = re.sub(r'[^\w\s]', '', words).split()
    stopwords = {"the", "a", "an", "is", "in", "to", "and", "or", "of", "it", "i", "this", "that"}
    word_freq = Counter(w for w in words if w not in stopwords and len(w) > 3)
    
    return {
        "subreddit": subreddit,
        "posts_analyzed": len(posts),
        "avg_score": round(total_score / len(posts), 1) if posts else 0,
        "avg_comments": round(avg_comments, 1),
        "top_words": dict(word_freq.most_common(10)),
        "top_posts": posts[:5],
    }
```

## Buscar con la API oficial (PRAW)

```python
# pip install praw
# Más potente pero requiere credenciales (gratis)
import praw
import os

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="MyAgent/1.0"
)

# PRAW con autenticación — más capacidades
sub = reddit.subreddit("cybersecurity")

# Top posts de la semana
for post in sub.top(time_filter="week", limit=10):
    print(f"{post.score:5d} | {post.title[:80]}")

# Buscar sobre un tema
for post in reddit.subreddit("all").search("GDPR compliance", sort="top", time_filter="year"):
    print(f"r/{post.subreddit} | {post.score} pts | {post.title}")
```

## Referencias
- [Reddit JSON API](https://www.reddit.com/dev/api/) — Documentación oficial
- [PRAW](https://praw.readthedocs.io/) — Python Reddit API Wrapper (con auth)
- [Pushshift.io](https://pushshift.io/) — Historial de Reddit (posts archivados)
