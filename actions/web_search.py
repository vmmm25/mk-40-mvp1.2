#web_search.py
"""Web search with multi-backend support: OpenRouter → Gemini → DuckDuckGo.

Uses OpenRouter for intelligent result analysis when available,
falls back to Gemini (with Google Search grounding), then to raw DDG.
"""

from memory.config_manager import load_config


def _get_api_key() -> str:
    cfg = load_config()
    key = cfg.get("gemini_api_key", "")
    if not key:
        raise ValueError("gemini_api_key not found in config")
    return key


def _openrouter_analyze(query: str, raw_results: list[dict]) -> str:
    """Use OpenRouter to analyze/search results with LLM intelligence."""
    from or_client import client

    formatted = _format_ddg(query, raw_results)
    prompt = (
        f"Search results for: {query}\n\n"
        f"{formatted}\n\n"
        f"Based on the above results, provide a clear and comprehensive answer "
        f"to the original query. Include relevant facts, data, and cite sources. "
        f"Respond in the same language as the query. "
        f"If the results don't contain enough information, say so clearly."
    )
    return client.chat(prompt)


def _openrouter_compare(items: list[str], aspect: str) -> str:
    """Use OpenRouter to perform a comparison analysis."""
    from or_client import client

    prompt = (
        f"Compare the following items in terms of {aspect}:\n"
        + "\n".join(f"- {item}" for item in items)
        + "\n\n"
        f"Provide a detailed comparison with specific facts, differences, "
        f"and recommendations. Respond in the same language as the query."
    )
    return client.chat(prompt)


def _gemini_search(query: str) -> str:
    from google import genai

    client   = genai.Client(api_key=_get_api_key())
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
        config={"tools": [{"google_search": {}}]},
    )

    text = ""
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            text += part.text

    text = text.strip()
    if not text:
        raise ValueError("Gemini returned an empty response.")
    return text


def _ddg_search(query: str, max_results: int = 6) -> list[dict]:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title":   r.get("title",  ""),
                "snippet": r.get("body",   ""),
                "url":     r.get("href",   ""),
            })
    return results


def _format_ddg(query: str, results: list[dict]) -> str:
    if not results:
        return f"No results found for: {query}"

    lines = [f"Search results for: {query}\n"]
    for i, r in enumerate(results, 1):
        if r.get("title"):   lines.append(f"{i}. {r['title']}")
        if r.get("snippet"): lines.append(f"   {r['snippet']}")
        if r.get("url"):     lines.append(f"   {r['url']}")
        lines.append("")
    return "\n".join(lines).strip()

def _compare(items: list[str], aspect: str) -> str:
    # 1. Try OpenRouter first
    try:
        print("[WebSearch] 📊 Trying OpenRouter compare...")
        result = _openrouter_compare(items, aspect)
        print("[WebSearch] ✅ OpenRouter compare OK.")
        return result
    except Exception as e:
        print(f"[WebSearch] ⚠️ OpenRouter compare failed ({e})")

    # 2. Fallback: Gemini with comparison query
    query = (
        f"Compare {', '.join(items)} in terms of {aspect}. "
        "Give specific facts and data."
    )
    try:
        return _gemini_search(query)
    except Exception as e:
        print(f"[WebSearch] ⚠️ Gemini compare failed: {e} — falling back to DDG")

    # 3. Fallback: raw DDG merge
    all_results: dict[str, list] = {}
    for item in items:
        try:
            all_results[item] = _ddg_search(f"{item} {aspect}", max_results=3)
        except Exception:
            all_results[item] = []

    lines = [f"Comparison — {aspect.upper()}", "─" * 40]
    for item in items:
        lines.append(f"\n▸ {item}")
        for r in all_results.get(item, [])[:2]:
            if r.get("snippet"):
                lines.append(f"  • {r['snippet']}")
    return "\n".join(lines)


def web_search(
    parameters:     dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    query  = params.get("query", "").strip()
    mode   = params.get("mode",  "search").lower().strip()
    items  = params.get("items", [])
    aspect = params.get("aspect", "general").strip() or "general"

    if not query and not items:
        return "Please provide a search query, sir."

    if items and mode != "compare":
        mode = "compare"

    if player:
        player.write_log(f"[Search] {query or ', '.join(items)}")

    print(f"[WebSearch] 🔍 Query: {query!r}  Mode: {mode}")

    try:
        if mode == "compare" and items:
            print(f"[WebSearch] 📊 Comparing: {items}")
            result = _compare(items, aspect)
            print("[WebSearch] ✅ Compare done.")
            return result

        # ── Search: OpenRouter → Gemini → DDG ────────────────────
        # 1. Try OpenRouter (DDG + OR LLM analysis)
        try:
            print("[WebSearch] 🌐 Trying OpenRouter...")
            raw = _ddg_search(query)
            if raw:
                result = _openrouter_analyze(query, raw)
                print("[WebSearch] ✅ OpenRouter OK.")
                return result
        except Exception as e:
            print(f"[WebSearch] ⚠️ OpenRouter failed ({e})")

        # 2. Fallback: Gemini with Google Search grounding
        try:
            print("[WebSearch] 🌐 Trying Gemini...")
            result = _gemini_search(query)
            print("[WebSearch] ✅ Gemini OK.")
            return result
        except Exception as e:
            print(f"[WebSearch] ⚠️ Gemini failed ({e}) — trying DDG...")

        # 3. Fallback: raw DDG results
        results = _ddg_search(query)
        result  = _format_ddg(query, results)
        print(f"[WebSearch] ✅ DDG: {len(results)} result(s).")
        return result

    except Exception as e:
        print(f"[WebSearch] ❌ All backends failed: {e}")
        return f"Search failed, sir: {e}"
