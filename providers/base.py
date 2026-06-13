"""MARK XL — Abstract provider interface for LLM backends.

Every provider (Gemini, Ollama, OpenRouter) implements this interface.
Supports both real-time audio (Gemini Live) and text-based chat for other providers.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

import aiohttp

log = logging.getLogger(__name__)

_CTRL_RE = re.compile(r"<ctrl\d+>", re.IGNORECASE)


def clean_transcript(text: str) -> str:
    """Remove control markers and non-printable chars from transcript text."""
    text = _CTRL_RE.sub("", text)
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)
    return text.strip()


@dataclass
class Message:
    role: str       # "user", "assistant", "system", "tool"
    content: str
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None
    name: str | None = None


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass
class ToolResult:
    id: str
    name: str
    result: str


@dataclass
class ProviderConfig:
    """Configuration for any provider."""
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    os_system: str = "windows"
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "os_system": self.os_system,
            **self.extra,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ProviderConfig":
        return cls(
            api_key=d.get("api_key", ""),
            base_url=d.get("base_url", ""),
            model=d.get("model", ""),
            system_prompt=d.get("system_prompt", ""),
            temperature=d.get("temperature", 0.7),
            max_tokens=d.get("max_tokens", 4096),
            os_system=d.get("os_system", "windows"),
            extra={k: v for k, v in d.items()
                   if k not in ("api_key", "base_url", "model",
                                "temperature", "max_tokens", "os_system",
                                "system_prompt")},
        )


# ---------------------------------------------------------------------------
# Shared retry helper — used by OpenRouter, LM Studio, and other HTTP providers
# ---------------------------------------------------------------------------


async def request_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    *,
    headers: dict | None = None,
    data: dict | None = None,
    timeout: aiohttp.ClientTimeout | None = None,
    max_attempts: int = 3,
) -> tuple[int, str]:
    """POST to *url* with exponential backoff retry.

    Retries on connection/timeout errors (ClientError, TimeoutError) and
    transient HTTP statuses (429, 5xx).  See:
    https://platform.openai.com/docs/guides/error-codes/api-errors

    Args:
        session:  aiohttp ClientSession
        url:      Full request URL
        headers:  Optional HTTP headers
        json:     Optional JSON-serialisable body
        timeout:  Custom timeout (defaults to 120 s total)
        max_attempts: Maximum retry count (default 3)

    Returns:
        Tuple of ``(status_code, body_text)``

    Raises:
        aiohttp.ClientError: if all attempts fail with client-side errors
    """
    if timeout is None:
        timeout = aiohttp.ClientTimeout(total=120)

    for attempt in range(1, max_attempts + 1):
        try:
            async with session.post(
                url, headers=headers, json=data, timeout=timeout
            ) as resp:
                # Retry on rate limits and common server errors
                if resp.status in {429, 500, 502, 503, 504}:
                    if attempt < max_attempts:
                        body = await resp.text(errors="replace")
                        log.warning(
                            "POST %s returned %d (attempt %d/%d): %.100s",
                            url, resp.status,
                            attempt, max_attempts, body,
                        )
                        await asyncio.sleep(_backoff(attempt))
                        continue
                # Read body — prefer JSON for 2xx, text for errors
                if 200 <= resp.status < 300:
                    data = await resp.json()
                    if isinstance(data, dict):
                        body = json.dumps(data)
                    else:
                        body = str(data)
                else:
                    body = await resp.text(errors="replace")
                return resp.status, body

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == max_attempts:
                raise
            log.warning(
                "POST %s failed (attempt %d/%d): %s",
                url, attempt, max_attempts, e,
            )
            await asyncio.sleep(_backoff(attempt))

    return 0, "Max retries exceeded"


def _backoff(attempt: int) -> float:
    """Exponential backoff with jitter: ``2^attempt + random(0, 1)``."""
    return (2 ** attempt) + random.random()


class BaseProvider(ABC):
    """Abstract base for all LLM providers."""

    name: str = "base"
    supports_live_audio: bool = False
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_vision: bool = False

    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> Message:
        """Send a chat message and get a response.
        If tools are provided, the response may contain tool_calls."""
        ...

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> AsyncGenerator[Message, None]:
        """Stream chat response tokens."""
        ...

    async def execute_tool_call(
        self,
        tool_call: ToolCall,
        tool_implementations: dict[str, Callable],
    ) -> ToolResult:
        """Execute a tool call from the LLM and return the result."""
        import asyncio
        handler = tool_implementations.get(tool_call.name)
        if handler is None:
            return ToolResult(
                id=tool_call.id,
                name=tool_call.name,
                result=f"Error: Unknown tool '{tool_call.name}'"
            )
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(tool_call.args)
            else:
                result = handler(tool_call.args)
            return ToolResult(
                id=tool_call.id,
                name=tool_call.name,
                result=str(result) if result is not None else "Done."
            )
        except Exception as e:
            return ToolResult(
                id=tool_call.id,
                name=tool_call.name,
                result=f"Error: {e}"
            )

    def get_models(self) -> list[dict]:
        """Return available models for this provider."""
        return []

    def format_tools_for_provider(self, tools: list[dict]) -> Any:
        """Convert our tool format to provider-specific format."""
        return tools

    def format_messages_for_provider(self, messages: list[Message]) -> Any:
        """Convert our messages to provider-specific format."""
        return messages

    def parse_response(self, response: Any) -> Message:
        """Parse provider-specific response to our Message format."""
        ...

    async def close(self):
        """Clean up resources like aiohttp sessions."""
        pass

    @staticmethod
    def convert_tools_openai(tools: list[dict]) -> list[dict]:
        """Convert tool declarations to OpenAI-compatible format.

        Shared by Ollama, OpenRouter, and any provider that uses the OpenAI
        function-calling format.
        """
        out = []
        for tool in tools:
            params = tool.get("parameters", {})
            props = params.get("properties", {})
            type_map = {
                "STRING": "string", "NUMBER": "number", "INTEGER": "integer",
                "BOOLEAN": "boolean", "OBJECT": "object", "ARRAY": "array",
            }
            mapped_props = {}
            for p_name, p_info in props.items():
                p_type = p_info.get("type", "STRING")
                mapped_props[p_name] = {
                    "type": type_map.get(p_type, "string"),
                    "description": p_info.get("description", ""),
                }
                if p_info.get("items"):
                    mapped_props[p_name]["items"] = p_info["items"]
            out.append({
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": mapped_props,
                        "required": params.get("required", []),
                    },
                },
            })
        return out

    async def tool_chat_loop(
        self,
        messages: list[Message],
        tools: list[dict],
        tool_implementations: dict[str, Callable],
        max_turns: int = 10,
    ) -> Message:
        """Multi-turn tool-calling chat with any provider.

        Sends messages, processes tool calls, returns final text response.
        Shared implementation for all providers.
        """
        history = list(messages)
        for _ in range(max_turns):
            import hashlib
            from core.cache import response_cache
            
            key_data = json.dumps([m.__dict__ for m in history] + (tools or []), sort_keys=True)
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            cached_resp = response_cache.get(cache_key)
            if cached_resp:
                response = Message(**json.loads(cached_resp))
            else:
                response = await self.chat(history, tools)
                response_cache.set(cache_key, json.dumps(response.__dict__))

            if not response.tool_calls:
                return response

            history.append(response)

            for tc_data in response.tool_calls:
                tool_call = ToolCall(
                    id=tc_data.get("id", tc_data.get("name", "")),
                    name=tc_data["name"],
                    args=tc_data.get("args", {}),
                )
                tool_result = await self.execute_tool_call(
                    tool_call, tool_implementations
                )
                history.append(Message(
                    role="tool",
                    content=tool_result.result,
                    tool_call_id=tool_result.id,
                    name=tool_result.name,
                ))

        return Message(
            role="assistant",
            content="Maximum tool call turns reached."
        )


# AsyncGenerator type alias for compatibility
from typing import AsyncGenerator
