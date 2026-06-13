"""MARK XL — Provider-agnostic LLM helper for the agent system.

Provides a synchronous `ask_llm(prompt, system_instruction)` function
that works with any configured provider (Gemini, Ollama, OpenRouter).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from memory.config_manager import load_config, get_model
from providers import create_provider, ProviderConfig, Message

# Cached Gemini client for fallback — avoids re-importing google SDK on every failure
_gemini_client = None


def _get_gemini_client():
    """Lazy-init and cache the Gemini SDK client."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    cfg = load_config()
    gemini_key = cfg.get("gemini_api_key", "")
    if not gemini_key:
        return None
    from google import genai
    _gemini_client = genai.Client(api_key=gemini_key)
    return _gemini_client


def _get_provider():
    """Create a provider instance based on saved config."""
    cfg = load_config()
    selected = cfg.get("selected_provider", "gemini")

    if selected == "openrouter":
        api_key = cfg.get("openrouter_api_key", "")
        base_url = ""
    elif selected == "ollama":
        api_key = ""  # Ollama does not require authentication
        base_url = cfg.get("ollama_url", "http://localhost:11434")
    elif selected == "lmstudio":
        api_key = ""  # LM Studio is local, no API key needed
        base_url = cfg.get("lmstudio_url", "http://localhost:1234/v1")
    else:  # Gemini
        api_key = cfg.get("gemini_api_key", "")
        base_url = ""

    pconfig = ProviderConfig(
        api_key=api_key,
        base_url=base_url,
        model=get_model(selected),
        temperature=0.3,  # Lower temp for planning/analysis
        max_tokens=2048,
    )

    return create_provider(selected, pconfig)


async def ask_llm(prompt: str, system_instruction: str = "") -> str:
    """Async helper: send a prompt to the configured LLM and get text back.

    Args:
        prompt: The user/query message.
        system_instruction: Optional system instruction.

    Returns:
        Response text string.
    """
    try:
        provider = _get_provider()
        messages = []
        if system_instruction:
            messages.append(Message(role="system", content=system_instruction))
        messages.append(Message(role="user", content=prompt))

        response = await provider.chat(messages)
        return response.content

    except Exception as e:
        print(f"[LLM] ❌ Primary provider error: {e}")
        # Fallback: try direct Gemini if configured (cached client)
        try:
            client = _get_gemini_client()
            if client is not None:
                print("[LLM] ⚠️ Falling back to direct Gemini call...")
                from google.genai import types
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction if system_instruction else None,
                    ),
                )
                text = response.text if hasattr(response, 'text') else ""
                if text:
                    print("[LLM] ✅ Fallback succeeded via direct Gemini")
                    return text
        except Exception as fallback_err:
            print(f"[LLM] ❌ Fallback also failed: {fallback_err}")

        return f"Error: Could not reach AI provider — {str(e)}"


def ask_llm_sync(prompt: str, system_instruction: str = "") -> str:
    """Synchronous wrapper for ask_llm for use in non-async contexts."""
    try:
        return asyncio.run(ask_llm(prompt, system_instruction))
    except RuntimeError:
        # Already in an event loop — create a new loop in a thread
        import threading
        result_container = []
        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                r = loop.run_until_complete(ask_llm(prompt, system_instruction))
                result_container.append(r)
            finally:
                loop.close()
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join()
        return result_container[0] if result_container else f"Error: Could not reach AI provider"

