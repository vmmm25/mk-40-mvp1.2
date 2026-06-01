"""MARK XL — Abstract provider interface for LLM backends.

Every provider (Gemini, Ollama, OpenRouter) implements this interface.
Supports both real-time audio (Gemini Live) and text-based chat for other providers.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

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
            response = await self.chat(history, tools)

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
