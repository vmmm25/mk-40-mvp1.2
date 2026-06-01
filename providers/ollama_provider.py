"""MARK XL — Ollama Provider.

Connects to local Ollama instance for running models locally.
Uses the Ollama REST API (default: http://localhost:11434).
Supports streaming chat and tool calling via JSON mode.
"""

from __future__ import annotations

import asyncio
import json
import random
import logging
from typing import Any, AsyncGenerator, Callable

import aiohttp

from .base import BaseProvider, Message, ProviderConfig, ToolCall, ToolResult
from . import register_provider

log = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2"


class OllamaProvider(BaseProvider):
    name = "ollama"
    supports_live_audio = False
    supports_streaming = True
    supports_tools = True
    supports_vision = False

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or DEFAULT_OLLAMA_URL
        self.model = config.model or DEFAULT_OLLAMA_MODEL
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _message_to_ollama(self, msg: Message) -> dict:
        """Convert our Message to Ollama chat format."""
        role_map = {
            "user": "user",
            "assistant": "assistant",
            "system": "system",
            "tool": "tool",
        }
        d = {"role": role_map.get(msg.role, "user"), "content": msg.content}

        # Handle tool results
        if msg.role == "tool":
            d["name"] = msg.name or ""
            return d

        # Handle tool calls in assistant messages
        if msg.tool_calls:
            d["content"] = msg.content or ""
            d["tool_calls"] = [
                {
                    "function": {
                        "name": tc.get("name", ""),
                        "arguments": json.dumps(tc.get("args", {})),
                    }
                }
                for tc in msg.tool_calls
            ]

        return d

    def _ollama_response_to_message(self, data: dict) -> Message:
        """Parse Ollama response to our Message format."""
        message = data.get("message", {})
        content = message.get("content", "")
        tool_calls_raw = message.get("tool_calls", [])

        tool_calls = None
        if tool_calls_raw:
            tool_calls = []
            for tc in tool_calls_raw:
                func = tc.get("function", {})
                args = func.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}
                elif not isinstance(args, dict):
                    args = {}
                tool_calls.append({
                    "name": func.get("name", ""),
                    "args": args,
                    "id": func.get("name", ""),
                })

        return Message(
            role="assistant",
            content=content or "",
            tool_calls=tool_calls,
        )

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> Message:
        """Send a chat to Ollama and get response."""
        try:
            session = await self._get_session()
            ollama_messages = [self._message_to_ollama(m) for m in messages]

            payload = {
                "model": self.model,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                },
            }

            # Add optional sampling parameters if they exist in the config
            optional_keys = ["top_p", "repeat_penalty"]
            for key in optional_keys:
                value = getattr(self.config, key, None)
                if value is not None:
                    payload["options"][key] = value

            # Configurable timeout (default 120 s)
            timeout_seconds = getattr(self.config, "timeout_seconds", 120)
            client_timeout = aiohttp.ClientTimeout(total=timeout_seconds)

            # Retry loop with exponential back‑off
            max_attempts = getattr(self.config, "max_retries", 3) or 3
            for attempt in range(1, max_attempts + 1):
                try:
                    async with session.post(
                        f"{self.base_url}/api/chat",
                        json=payload,
                        timeout=client_timeout,
                    ) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            return Message(
                                role="assistant",
                                content=f"Ollama error ({resp.status}): {error_text[:200]}",
                            )
                        data = await resp.json()
                        return self._ollama_response_to_message(data)

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt == max_attempts:
                        raise
                    backoff = (2 ** attempt) + random.random()
                    log.warning(
                        f"Chat request failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {backoff:.2f}s..."
                    )
                    await asyncio.sleep(backoff)

        except aiohttp.ClientConnectorError:
            return Message(
                role="assistant",
                content=f"⚠️ No se puede conectar a Ollama en {self.base_url}. "
                        f"¿Está Ollama corriendo? Inicia Ollama e intenta de nuevo."
            )
        except Exception as e:
            return Message(
                role="assistant",
                content=f"Error con Ollama: {str(e)}"
            )

    async def stream_chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> AsyncGenerator[Message, None]:
        """Stream Ollama response tokens."""
        try:
            session = await self._get_session()
            ollama_messages = [self._message_to_ollama(m) for m in messages]

            payload = {
                "model": self.model,
                "messages": ollama_messages,
                "stream": True,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                },
            }

            # Add optional sampling parameters if they exist in the config
            optional_keys = ["top_p", "repeat_penalty"]
            for key in optional_keys:
                value = getattr(self.config, key, None)
                if value is not None:
                    payload["options"][key] = value

            timeout_seconds = getattr(self.config, "timeout_seconds", 120)
            client_timeout = aiohttp.ClientTimeout(total=timeout_seconds)

            max_attempts = getattr(self.config, "max_retries", 3) or 3
            for attempt in range(1, max_attempts + 1):
                try:
                    async with session.post(
                        f"{self.base_url}/api/chat",
                        json=payload,
                        timeout=client_timeout,
                    ) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            yield Message(
                                role="assistant",
                                content=f"Ollama error ({resp.status}): {error_text[:200]}"
                            )
                            return

                        full_content = ""
                        async for line in resp.content:
                            if line:
                                try:
                                    chunk = json.loads(line)
                                    if "message" in chunk:
                                        content = chunk["message"].get("content", "")
                                        if content:
                                            full_content += content
                                            yield Message(role="assistant", content=content)

                                    if chunk.get("done"):
                                        # Token usage could be forwarded to UI via the Message
                                        # For now we just break the stream.
                                        break
                                except json.JSONDecodeError:
                                    continue
                        break

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt == max_attempts:
                        yield Message(
                            role="assistant",
                            content=f"⚠️ No se puede conectar a Ollama en {self.base_url}."
                        )
                        return
                    backoff = (2 ** attempt) + random.random()
                    log.warning(
                        f"Stream request failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {backoff:.2f}s..."
                    )
                    await asyncio.sleep(backoff)

        except aiohttp.ClientConnectorError:
            yield Message(
                role="assistant",
                content=f"⚠️ No se puede conectar a Ollama en {self.base_url}."
            )
        except Exception as e:
            yield Message(
                role="assistant",
                content=f"Error con Ollama: {str(e)}"
            )

    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama."""
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=aiohttp.ClientTimeout(total=300),
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def check_server(self) -> bool:
        """Check if Ollama server is running."""
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    def get_models(self) -> list[dict]:
        """Get available models from local Ollama instance."""
        return [
            {"id": "llama3.2", "name": "Llama 3.2 (8B)"},
            {"id": "llama3.1", "name": "Llama 3.1 (70B)"},
            {"id": "mistral", "name": "Mistral (7B)"},
            {"id": "mixtral", "name": "Mixtral (8x7B)"},
            {"id": "qwen2.5", "name": "Qwen 2.5"},
            {"id": "phi4", "name": "Phi-4"},
            {"id": "deepseek-r1", "name": "DeepSeek R1"},
            {"id": "codellama", "name": "CodeLlama"},
            {"id": "gemma2", "name": "Gemma 2"},
        ]

    async def fetch_available_models(self) -> list[dict]:
        """Fetch actual models from Ollama API."""
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = data.get("models", [])
                    return [{"id": m["name"], "name": m["name"]} for m in models]
        except Exception:
            pass
        return self.get_models()

    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama."""
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=aiohttp.ClientTimeout(total=300),
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def check_server(self) -> bool:
        """Check if Ollama server is running."""
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


register_provider("ollama", OllamaProvider)
