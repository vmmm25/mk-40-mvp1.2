"""MARK XL — LM Studio Provider.

Connects to LM Studio's local OpenAI-compatible server.
Default endpoint: http://localhost:1234/v1
No API key required — runs fully local.
Supports any model loaded in LM Studio.
"""

from __future__ import annotations

import json
import aiohttp
from typing import Any, AsyncGenerator

from .base import BaseProvider, Message, ProviderConfig, ToolCall, ToolResult
from . import register_provider


LMSTUDIO_BASE = "http://localhost:1234/v1"
DEFAULT_LMSTUDIO_MODEL = ""


class LMStudioProvider(BaseProvider):
    name = "lmstudio"
    supports_live_audio = False
    supports_streaming = True
    supports_tools = True
    supports_vision = True  # LM Studio supports vision if model does

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.api_key  # may be empty — optional for LM Studio
        self.base_url = config.base_url or LMSTUDIO_BASE
        self.model = config.model or DEFAULT_LMSTUDIO_MODEL
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _message_to_lmstudio(self, msg: Message) -> dict:
        """Convert our Message to OpenAI-compatible format."""
        d = {"role": msg.role}

        # Handle tool results
        if msg.role == "tool":
            d["tool_call_id"] = msg.tool_call_id or ""
            d["content"] = msg.content
            if msg.name:
                d["name"] = msg.name
            return d

        # Handle assistant messages with tool calls
        if msg.tool_calls:
            d["content"] = msg.content or ""
            d["tool_calls"] = [
                {
                    "id": tc.get("id", tc.get("name", "")),
                    "type": "function",
                    "function": {
                        "name": tc.get("name", ""),
                        "arguments": json.dumps(tc.get("args", {})),
                    },
                }
                for tc in msg.tool_calls
            ]
        else:
            d["content"] = msg.content

        return d

    def _lmstudio_response_to_message(self, data: dict) -> Message:
        """Parse LM Studio API response to our Message format."""
        try:
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "") or ""
            tool_calls_raw = message.get("tool_calls", [])

            tool_calls = None
            if tool_calls_raw:
                tool_calls = []
                for tc in tool_calls_raw:
                    func = tc.get("function", {})
                    try:
                        args = json.loads(func.get("arguments", "{}"))
                    except (json.JSONDecodeError, TypeError):
                        args = {}
                    tool_calls.append({
                        "name": func.get("name", ""),
                        "args": args,
                        "id": tc.get("id", func.get("name", "")),
                    })

            return Message(
                role="assistant",
                content=content,
                tool_calls=tool_calls,
            )
        except Exception as e:
            return Message(
                role="assistant",
                content=f"Error parsing LM Studio response: {str(e)}"
            )

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> Message:
        """Send a chat to LM Studio and get response."""
        try:
            session = await self._get_session()

            ls_messages = [self._message_to_lmstudio(m) for m in messages]

            headers = {
                "Content-Type": "application/json",
            }
            # Optional API key if LM Studio server is configured with one
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            payload = {
                "messages": ls_messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": False,
            }

            # Only include model if one is specified (LM Studio can use whatever is loaded)
            if self.model:
                payload["model"] = self.model

            # Convert tools if provided
            if tools:
                payload["tools"] = self.convert_tools_openai(tools)

            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return Message(
                        role="assistant",
                        content=f"LM Studio error ({resp.status}): {error_text[:200]}"
                    )
                data = await resp.json()
                return self._lmstudio_response_to_message(data)

        except aiohttp.ClientConnectorError:
            return Message(
                role="assistant",
                content="⚠️ No se puede conectar a LM Studio. ¿Está el servidor corriendo en localhost:1234?"
            )
        except Exception as e:
            return Message(
                role="assistant",
                content=f"Error con LM Studio: {str(e)}"
            )

    async def stream_chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> AsyncGenerator[Message, None]:
        """Stream LM Studio response tokens."""
        try:
            session = await self._get_session()

            ls_messages = [self._message_to_lmstudio(m) for m in messages]

            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            payload = {
                "messages": ls_messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": True,
            }

            if self.model:
                payload["model"] = self.model

            if tools:
                payload["tools"] = self.convert_tools_openai(tools)

            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    yield Message(
                        role="assistant",
                        content=f"LM Studio error ({resp.status}): {error_text[:200]}"
                    )
                    return

                # Read SSE lines properly (handles multi-line chunks)
                while True:
                    line = await resp.content.readline()
                    if not line:
                        break
                    text = line.decode("utf-8", errors="replace").strip()
                    if not text:
                        continue
                    if not text.startswith("data: "):
                        continue
                    data_str = text[6:]
                    if data_str == "[DONE]":
                        return
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield Message(role="assistant", content=content)
                    except json.JSONDecodeError:
                        continue

        except aiohttp.ClientConnectorError:
            yield Message(
                role="assistant",
                content="⚠️ No se puede conectar a LM Studio."
            )
        except Exception as e:
            yield Message(
                role="assistant",
                content=f"Error con LM Studio: {str(e)}"
            )

    async def list_models(self) -> list[dict]:
        """Fetch currently loaded models from LM Studio's /v1/models endpoint."""
        try:
            session = await self._get_session()
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with session.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = data.get("data", [])
                    return [
                        {"id": m["id"], "name": m.get("id", "Unknown")}
                        for m in models
                    ]
                return [{"id": "local-model", "name": "Local Model (LM Studio)"}]
        except Exception:
            return [{"id": "local-model", "name": "Local Model (LM Studio)"}]

    def get_models(self) -> list[dict]:
        """Return available models (static fallback if server not reachable)."""
        return [
            {"id": "local-model", "name": "Local Model (default)"},
        ]


register_provider("lmstudio", LMStudioProvider)

