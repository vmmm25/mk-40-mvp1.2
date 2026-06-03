"""MARK XL — Ollama Provider.

Connects to local Ollama instance for running models locally.
Uses the Ollama REST API (default: http://localhost:11434).
Supports streaming chat and tool calling via JSON mode.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from typing import Any, AsyncGenerator

import aiohttp

from .base import BaseProvider, Message, ProviderConfig
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

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    # ------------------------------------------------------------------
    # Message format conversion
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Shared helpers — DRY refactor target
    # ------------------------------------------------------------------

    def _build_payload(
        self,
        messages: list[Message],
        stream: bool = False,
    ) -> dict:
        """Build the Ollama /api/chat request payload."""
        ollama_messages = [self._message_to_ollama(m) for m in messages]

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": stream,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            },
        }

        # Add optional sampling parameters
        for key in ("top_p", "repeat_penalty", "frequency_penalty", "presence_penalty"):
            value = getattr(self.config, key, None)
            if value is not None:
                payload["options"][key] = value

        return payload

    def _get_timeout(self) -> aiohttp.ClientTimeout:
        """Return a ClientTimeout based on config (default 120 s)."""
        return aiohttp.ClientTimeout(
            total=getattr(self.config, "timeout_seconds", 120)
        )

    def _get_max_attempts(self) -> int:
        return getattr(self.config, "max_retries", 3) or 3

    def _error_message(self, status: int, text: str) -> Message:
        return Message(
            role="assistant",
            content=f"Ollama error ({status}): {text[:200]}",
        )

    def _connection_error_message(self) -> Message:
        return Message(
            role="assistant",
            content=f"⚠️ No se puede conectar a Ollama en {self.base_url}. "
                    f"¿Está Ollama corriendo? Inicia Ollama e intenta de nuevo.",
        )

    # ------------------------------------------------------------------
    # Non-streaming chat
    # ------------------------------------------------------------------

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> Message:
        """Send a chat to Ollama and get response."""
        try:
            session = await self._get_session()
            payload = self._build_payload(messages, stream=False)

            response = await self._request_with_retry(session, payload)
            if isinstance(response, Message):
                return response  # already an error message
            return self._ollama_response_to_message(response)

        except aiohttp.ClientConnectorError:
            return self._connection_error_message()
        except Exception as e:
            return Message(
                role="assistant",
                content=f"Error con Ollama: {str(e)}",
            )

    # ------------------------------------------------------------------
    # Streaming chat
    # ------------------------------------------------------------------

    async def stream_chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> AsyncGenerator[Message, None]:
        """Stream Ollama response tokens."""
        try:
            session = await self._get_session()
            payload = self._build_payload(messages, stream=True)

            async for chunk_msg in self._stream_with_retry(session, payload):
                yield chunk_msg

        except aiohttp.ClientConnectorError:
            yield self._connection_error_message()
        except Exception as e:
            yield Message(
                role="assistant",
                content=f"Error con Ollama: {str(e)}",
            )

    # ------------------------------------------------------------------
    # Retry logic for non-streaming requests
    # ------------------------------------------------------------------

    async def _request_with_retry(
        self,
        session: aiohttp.ClientSession,
        payload: dict,
    ) -> dict | Message:
        """POST to /api/chat, retrying on transient errors.

        Returns the parsed JSON dict on success, or a ``Message`` on failure.
        """
        max_attempts = self._get_max_attempts()
        timeout = self._get_timeout()
        url = f"{self.base_url}/api/chat"

        for attempt in range(1, max_attempts + 1):
            try:
                async with session.post(
                    url, json=payload, timeout=timeout,
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        return self._error_message(resp.status, error_text)
                    return await resp.json()

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_attempts:
                    raise
                backoff = (2**attempt) + random.random()
                log.warning(
                    "Chat request failed (attempt %d/%d): %s. "
                    "Retrying in %.2fs...",
                    attempt, max_attempts, e, backoff,
                )
                await asyncio.sleep(backoff)

        # Should not be reached
        return self._error_message(0, "Max retries exceeded")

    # ------------------------------------------------------------------
    # Retry logic for streaming requests
    # ------------------------------------------------------------------

    async def _stream_with_retry(
        self,
        session: aiohttp.ClientSession,
        payload: dict,
    ) -> AsyncGenerator[Message, None]:
        """Stream from /api/chat, retrying on transient errors."""
        max_attempts = self._get_max_attempts()
        timeout = self._get_timeout()
        url = f"{self.base_url}/api/chat"

        for attempt in range(1, max_attempts + 1):
            try:
                async with session.post(
                    url, json=payload, timeout=timeout,
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        yield self._error_message(resp.status, error_text)
                        return

                    full_content = ""
                    async for line_bytes in resp.content:
                        if not line_bytes:
                            continue
                        try:
                            line = line_bytes.decode("utf-8").strip()
                            if not line:
                                continue
                            chunk = json.loads(line)
                            if "message" in chunk:
                                content = chunk["message"].get("content", "")
                                if content:
                                    full_content += content
                                    yield Message(role="assistant", content=content)

                            if chunk.get("done"):
                                return
                        except json.JSONDecodeError:
                            continue
                    return  # success, exit retry loop

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_attempts:
                    yield Message(
                        role="assistant",
                        content=f"⚠️ No se puede conectar a Ollama en {self.base_url}.",
                    )
                    return
                backoff = (2**attempt) + random.random()
                log.warning(
                    "Stream request failed (attempt %d/%d): %s. "
                    "Retrying in %.2fs...",
                    attempt, max_attempts, e, backoff,
                )
                await asyncio.sleep(backoff)

    # ------------------------------------------------------------------
    # Model listing
    # ------------------------------------------------------------------

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
            log.warning("Could not fetch models from Ollama, using fallback list")
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
        except Exception as e:
            log.error("Failed to pull model %s: %s", model_name, e)
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


register_provider("ollama", OllamaProvider)
