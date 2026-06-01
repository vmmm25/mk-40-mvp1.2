"""MARK XL — OpenRouter Provider.

Connects to OpenRouter API for cloud-hosted models.
Supports hundreds of models via a single API.
Provides streaming chat and tool calling.
"""

from __future__ import annotations

import json
import aiohttp
from typing import Any, AsyncGenerator, Callable

from .base import BaseProvider, Message, ProviderConfig, ToolCall, ToolResult
from . import register_provider


OPENROUTER_BASE = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


class OpenRouterProvider(BaseProvider):
    name = "openrouter"
    supports_live_audio = False
    supports_streaming = True
    supports_tools = True
    supports_vision = True

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or OPENROUTER_BASE
        self.model = config.model or DEFAULT_OPENROUTER_MODEL
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _message_to_openrouter(self, msg: Message) -> dict:
        """Convert our Message to OpenAI-compatible format."""
        role_map = {
            "user": "user",
            "assistant": "assistant",
            "system": "developer" if self._is_claude() else "system",
            "tool": "tool",
        }
        d = {"role": role_map.get(msg.role, "user")}

        # Handle tool results
        if msg.role == "tool":
            d["tool_call_id"] = msg.tool_call_id or ""
            d["content"] = msg.content
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

    def _openrouter_response_to_message(self, data: dict) -> Message:
        """Parse OpenRouter API response to our Message format."""
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
                content=f"Error parsing response: {str(e)}"
            )

    def _is_claude(self) -> bool:
        """Check if current model is Claude (uses 'developer' role)."""
        return "claude" in self.model.lower()

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> Message:
        """Send a chat to OpenRouter and get response."""
        try:
            session = await self._get_session()

            or_messages = [self._message_to_openrouter(m) for m in messages]

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:11434",
                "X-Title": "MARK XL - AI Assistant",
            }

            payload = {
                "model": self.model,
                "messages": or_messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": False,
            }

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
                        content=f"OpenRouter error ({resp.status}): {error_text[:200]}"
                    )
                data = await resp.json()
                return self._openrouter_response_to_message(data)

        except aiohttp.ClientConnectorError:
            return Message(
                role="assistant",
                content="⚠️ No se puede conectar a OpenRouter. Verifica tu conexión a internet."
            )
        except Exception as e:
            return Message(
                role="assistant",
                content=f"Error con OpenRouter: {str(e)}"
            )

    async def stream_chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> AsyncGenerator[Message, None]:
        """Stream OpenRouter response tokens."""
        try:
            session = await self._get_session()

            or_messages = [self._message_to_openrouter(m) for m in messages]

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:11434",
                "X-Title": "MARK XL - AI Assistant",
            }

            payload = {
                "model": self.model,
                "messages": or_messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": True,
            }

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
                        content=f"OpenRouter error ({resp.status}): {error_text[:200]}"
                    )
                    return

                async for line in resp.content:
                    if line:
                        text = line.decode("utf-8").strip()
                        if text.startswith("data: "):
                            data_str = text[6:]
                            if data_str == "[DONE]":
                                break
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
                content="⚠️ No se puede conectar a OpenRouter."
            )
        except Exception as e:
            yield Message(
                role="assistant",
                content=f"Error con OpenRouter: {str(e)}"
            )

    def get_models(self) -> list[dict]:
        """Return all currently available free models from OpenRouter.
        Live list fetched from API on 2026-05-28.
        """
        return [
            # NVIDIA models
            {"id": "nvidia/nemotron-3-nano-30b-a3b:free",             "name": "Nvidia Nemotron 3 Nano 30B (free)"},
            {"id": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free","name": "Nvidia Nemotron 3 Nano Omni (free)"},
            {"id": "nvidia/nemotron-3-super-120b-a12b:free",          "name": "Nvidia Nemotron 3 Super 120B (free)"},
            {"id": "nvidia/nemotron-nano-12b-v2-vl:free",             "name": "Nvidia Nemotron Nano 12B VL (free)"},
            {"id": "nvidia/nemotron-nano-9b-v2:free",                 "name": "Nvidia Nemotron Nano 9B (free)"},
            # Google
            {"id": "google/gemma-4-31b-it:free",                     "name": "Gemma 4 31B IT (free)"},
            {"id": "google/gemma-4-26b-a4b-it:free",                 "name": "Gemma 4 26B A4B IT (free)"},
            # DeepSeek
            {"id": "deepseek/deepseek-v4-flash:free",                 "name": "DeepSeek V4 Flash (free)"},
            # Meta Llama
            {"id": "meta-llama/llama-3.3-70b-instruct:free",          "name": "Llama 3.3 70B (free)"},
            {"id": "meta-llama/llama-3.2-3b-instruct:free",           "name": "Llama 3.2 3B (free)"},
            # OpenAI OSS
            {"id": "openai/gpt-oss-120b:free",                       "name": "GPT-OSS 120B (free)"},
            {"id": "openai/gpt-oss-20b:free",                        "name": "GPT-OSS 20B (free)"},
            # Qwen
            {"id": "qwen/qwen3-coder:free",                          "name": "Qwen 3 Coder (free)"},
            {"id": "qwen/qwen3-next-80b-a3b-instruct:free",          "name": "Qwen 3 Next 80B (free)"},
            # Others
            {"id": "liquid/lfm-2.5-1.2b-instruct:free",              "name": "Liquid LFM 2.5 1.2B (free)"},
            {"id": "liquid/lfm-2.5-1.2b-thinking:free",              "name": "Liquid LFM 2.5 1.2B Think (free)"},
            {"id": "minimax/minimax-m2.5:free",                      "name": "MiniMax M2.5 (free)"},
            {"id": "moonshotai/kimi-k2.6:free",                      "name": "Moonshot Kimi K2.6 (free)"},
            {"id": "nousresearch/hermes-3-llama-3.1-405b:free",      "name": "Nous Hermes 3 405B (free)"},
            {"id": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free", "name": "Dolphin Mistral 24B (free)"},
            {"id": "poolside/laguna-m.1:free",                       "name": "Poolside Laguna M.1 (free)"},
            {"id": "poolside/laguna-xs.2:free",                      "name": "Poolside Laguna XS.2 (free)"},
            {"id": "z-ai/glm-4.5-air:free",                          "name": "GLM 4.5 Air (free)"},
        ]

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


register_provider("openrouter", OpenRouterProvider)
