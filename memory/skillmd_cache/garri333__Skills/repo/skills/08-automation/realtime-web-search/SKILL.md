---
name: realtime-web-search
version: 1.0.0
description: Search the live web for real-time information using Tavily, Serper, Brave Search, and Google Custom Search APIs. Ideal for news, current events, prices, documentation updates, and any information not in training data.
tags: [web-search, real-time, tavily, serper, brave, google, news, live-data, rag]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Realtime Web Search Skill

## When to Use This Skill

Use when you need:
- Current news, events, prices, scores
- Latest software versions, documentation updates
- Information after your knowledge cutoff
- Live stock prices, crypto rates, exchange rates
- Recent research papers, announcements
- Real-time product availability, reviews

## Provider Comparison

| Provider | Free Tier | Quality | Speed | Best For |
|----------|-----------|---------|-------|---------|
| Tavily | 1000 req/mo | ⭐⭐⭐⭐⭐ | Fast | AI-optimized, RAG |
| Serper | 2500 req/mo | ⭐⭐⭐⭐ | Fast | Google results |
| Brave Search | 2000 req/mo | ⭐⭐⭐⭐ | Fast | Privacy-first |
| Google CSE | 100 req/day | ⭐⭐⭐⭐⭐ | Moderate | Full Google |
| DuckDuckGo | Unlimited* | ⭐⭐⭐ | Fast | No key needed |

## Setup

```bash
pip install tavily-python requests python-dotenv
```

`.env`:
```
TAVILY_API_KEY=tvly-...
SERPER_API_KEY=...
BRAVE_API_KEY=BSA...
GOOGLE_CSE_KEY=...
GOOGLE_CSE_ID=...
```

## Tavily — Best for AI/RAG (Recommended)

```python
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_tavily(
    query: str,
    search_depth: str = "basic",    # "basic" (faster) | "advanced" (deeper)
    max_results: int = 5,
    include_answer: bool = True,     # AI-generated summary
    include_images: bool = False,
    days: int = None,                # Limit to results from last N days
    topic: str = "general"           # "general" | "news"
) -> dict:
    """Search the web using Tavily (AI-optimized)."""
    kwargs = {
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results,
        "include_answer": include_answer,
        "include_images": include_images,
        "topic": topic,
    }
    if days:
        kwargs["days"] = days
    
    return tavily.search(**kwargs)

def search_news(query: str, days: int = 3, max_results: int = 5) -> dict:
    """Search for recent news on a topic."""
    return search_tavily(query, topic="news", days=days, max_results=max_results)

def get_answer(question: str) -> str:
    """Get a direct AI-synthesized answer from the web."""
    result = search_tavily(question, search_depth="advanced", include_answer=True)
    return result.get("answer", "No answer found")

def extract_content(url: str) -> dict:
    """Extract clean content from a specific URL."""
    return tavily.extract(urls=[url])

# Usage:
results = search_tavily("Python 3.13 new features")
print(results["answer"])  # AI summary
for r in results["results"]:
    print(f"- {r['title']}: {r['url']}")
    print(f"  {r['content'][:200]}...")
```

## Serper — Real Google Results

```python
import requests

def search_serper(
    query: str,
    num_results: int = 10,
    search_type: str = "search",  # "search" | "news" | "images" | "places"
    country: str = "us",
    lang: str = "en",
    time_range: str = None,        # "h" (hour) | "d" (day) | "w" (week) | "m" (month) | "y" (year)
) -> dict:
    """Search using Serper (Google results via API)."""
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": num_results,
        "gl": country,
        "hl": lang,
    }
    if time_range:
        payload["tbs"] = f"qdr:{time_range}"
    
    endpoint = f"https://google.serper.dev/{search_type}"
    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def get_top_results_serper(query: str, n: int = 5) -> list[dict]:
    """Get top N organic search results."""
    data = search_serper(query, num_results=n)
    return [
        {
            "title": r.get("title"),
            "url": r.get("link"),
            "snippet": r.get("snippet"),
            "position": r.get("position"),
        }
        for r in data.get("organic", [])
    ]

def get_featured_snippet(query: str) -> str:
    """Get the featured snippet (answer box) for a query."""
    data = search_serper(query)
    answer_box = data.get("answerBox", {})
    return answer_box.get("answer") or answer_box.get("snippet") or "No featured snippet"

def news_serper(query: str, time_range: str = "d") -> list[dict]:
    """Get recent news articles."""
    data = search_serper(query, search_type="news", time_range=time_range)
    return [
        {
            "title": n.get("title"),
            "url": n.get("link"),
            "source": n.get("source"),
            "date": n.get("date"),
            "snippet": n.get("snippet"),
        }
        for n in data.get("news", [])
    ]
```

## Brave Search

```python
def search_brave(
    query: str,
    count: int = 10,
    country: str = "us",
    search_lang: str = "en",
    freshness: str = None,   # "pd" (day) | "pw" (week) | "pm" (month) | "py" (year)
    result_filter: str = "web"  # "web" | "news"
) -> dict:
    """Search using Brave Search API."""
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.getenv("BRAVE_API_KEY")
    }
    params = {
        "q": query,
        "count": count,
        "country": country,
        "search_lang": search_lang,
        "result_filter": result_filter,
    }
    if freshness:
        params["freshness"] = freshness
    
    response = requests.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    
    results = []
    for r in data.get("web", {}).get("results", []):
        results.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "description": r.get("description"),
            "age": r.get("age"),
        })
    return results
```

## DuckDuckGo — No API Key Required

```python
def search_duckduckgo(query: str, max_results: int = 10) -> list[dict]:
    """Search DuckDuckGo without an API key using the instant answers API."""
    # Instant answer (best for factual questions)
    response = requests.get(
        "https://api.duckduckgo.com/",
        params={
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
    )
    data = response.json()
    
    results = []
    
    # Abstract (main answer)
    if data.get("Abstract"):
        results.append({
            "type": "abstract",
            "title": data.get("Heading"),
            "url": data.get("AbstractURL"),
            "snippet": data.get("Abstract")
        })
    
    # Related topics
    for topic in data.get("RelatedTopics", [])[:max_results]:
        if isinstance(topic, dict) and topic.get("Text"):
            results.append({
                "type": "related",
                "title": topic.get("Text", "")[:100],
                "url": topic.get("FirstURL", ""),
                "snippet": topic.get("Text", "")
            })
    
    return results
```

## Unified Search Interface

```python
def search(
    query: str,
    provider: str = "tavily",  # "tavily" | "serper" | "brave" | "ddg"
    max_results: int = 5,
    **kwargs
) -> list[dict]:
    """Unified search interface across all providers."""
    if provider == "tavily":
        result = search_tavily(query, max_results=max_results, **kwargs)
        return result.get("results", [])
    
    elif provider == "serper":
        return get_top_results_serper(query, n=max_results)
    
    elif provider == "brave":
        return search_brave(query, count=max_results, **kwargs)
    
    elif provider == "ddg":
        return search_duckduckgo(query, max_results=max_results)
    
    raise ValueError(f"Unknown provider: {provider}")

def search_with_fallback(query: str, max_results: int = 5) -> list[dict]:
    """Try providers in order until one succeeds."""
    providers = ["tavily", "serper", "brave", "ddg"]
    for provider in providers:
        try:
            results = search(query, provider=provider, max_results=max_results)
            if results:
                return results
        except Exception:
            continue
    return []
```

## RAG (Retrieval-Augmented Generation) Pattern

```python
def search_and_summarize(question: str, max_sources: int = 3) -> dict:
    """
    Full RAG pipeline: search → extract content → return enriched context.
    Ready to inject into an LLM prompt.
    """
    # 1. Search
    results = search_tavily(question, search_depth="advanced", max_results=max_sources)
    
    # 2. Extract AI summary if available
    ai_answer = results.get("answer", "")
    
    # 3. Gather source snippets
    sources = []
    for r in results.get("results", []):
        sources.append({
            "title": r["title"],
            "url": r["url"],
            "content": r["content"][:500]
        })
    
    # 4. Build context for LLM
    context = f"Question: {question}\n\n"
    if ai_answer:
        context += f"Web Summary: {ai_answer}\n\n"
    context += "Sources:\n"
    for i, s in enumerate(sources, 1):
        context += f"[{i}] {s['title']} ({s['url']})\n{s['content']}\n\n"
    
    return {
        "question": question,
        "answer": ai_answer,
        "sources": sources,
        "context_for_llm": context,
    }

# Usage with Claude/OpenAI:
def answer_with_web_context(question: str, llm_client) -> str:
    """Use web search to augment LLM response."""
    web_data = search_and_summarize(question)
    
    prompt = f"""Based on the following real-time web information, answer the question.

{web_data['context_for_llm']}

Please provide a comprehensive, accurate answer based on these sources."""
    
    # Inject into your LLM call
    return llm_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ).content[0].text
```

## Common Use Cases

```python
# Get latest news on a topic
news = news_serper("AI regulation Europe 2025", time_range="w")
for article in news[:3]:
    print(f"{article['date']}: {article['title']} — {article['url']}")

# Check current cryptocurrency price
result = get_answer("What is the current price of Bitcoin in USD?")
print(result)

# Find latest version of a library
result = get_answer("What is the latest stable version of Python?")
print(result)

# Research competitor news
results = search("OpenAI GPT-5 release date", provider="tavily", days=7)
for r in results:
    print(f"- {r['title']}: {r['content'][:150]}")

# Get weather information
result = get_answer("What is the weather in Madrid today?")
print(result)
```

## References
- [Tavily](https://tavily.com/) — AI-optimized search, best for RAG
- [Serper](https://serper.dev/) — Google Search API, cheap
- [Brave Search API](https://api.search.brave.com/app/documentation/web-search/get-started) — Privacy-first
- [Google Custom Search](https://developers.google.com/custom-search/v1/overview) — Official Google
- [DuckDuckGo API](https://duckduckgo.com/duckduckgo-help-pages/settings/params/) — Free, no key
