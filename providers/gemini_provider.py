"""MARK XL — Gemini Provider.

Supports two modes:
1. LIVE MODE — Real-time audio with the Gemini Live API (for voice conversations)
2. CHAT MODE — Text-based chat with Gemini models (for typed conversations)

"""

from __future__ import annotations

import asyncio
import json
import re
import threading
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable

from google import genai
from google.genai import types

from .base import BaseProvider, Message, ProviderConfig, ToolCall, ToolResult
from . import register_provider


# Gemini models
GEMINI_LIVE_MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"
GEMINI_CHAT_MODEL = "models/gemini-2.5-flash"


class GeminiProvider(BaseProvider):
    name = "gemini"
    supports_live_audio = True
    supports_streaming = True
    supports_tools = True
    supports_vision = True

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = genai.Client(
            api_key=config.api_key,
            http_options={"api_version": "v1beta"} if config.api_key else {},
        )
        # Use hardcoded Gemini model — config.model is provider-specific
        # (e.g. "llama3.2" for Ollama) and won't work with Gemini
        self._live_model = GEMINI_LIVE_MODEL
        self._chat_model = GEMINI_CHAT_MODEL

    # ── Live Audio Session (unique to Gemini) ──────────────────────────

    @asynccontextmanager
    async def create_live_session(self, config_overrides: dict | None = None):
        """Create a Live API session for real-time audio.
        Yields the session inside an async context manager.

        Usage:
            async with provider.create_live_session({...}) as session:
                ... use session ...
        """
        from datetime import datetime

        now = datetime.now()
        time_str = now.strftime("%A, %B %d, %Y — %I:%M %p")
        parts = [
            f"[CURRENT DATE & TIME]\nRight now it is: {time_str}\n\n"
        ]

        # Add memory if available
        mem_str = config_overrides.get("memory_str", "") if config_overrides else ""
        if mem_str:
            parts.append(mem_str)

        # Add system prompt
        sys_prompt = config_overrides.get("system_prompt", "")
        if sys_prompt:
            parts.append(sys_prompt)

        system_instruction = "\n".join(parts)

        tools_defs = config_overrides.get("tools", [])

        live_config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            output_audio_transcription={},
            input_audio_transcription={},
            system_instruction=system_instruction,
            tools=[{"function_declarations": tools_defs}] if tools_defs else None,
            session_resumption=types.SessionResumptionConfig(),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Charon"
                    )
                )
            ),
        )

        # Use async with to properly enter the live connect context manager
        async with self._client.aio.live.connect(
            model=self._live_model,
            config=live_config,
        ) as session:
            yield session

    # ── Chat (text only, no audio) ─────────────────────────────────────

    def _gemini_tools_from_declarations(self, tools: list[dict] | None):
        """Convert our tool declarations to Gemini function_declarations format."""
        if not tools:
            return None
        return [{"function_declarations": tools}]

    def _message_to_gemini_content(self, msg: Message) -> dict:
        """Convert our Message to Gemini content format."""
        role_map = {"user": "user", "assistant": "model", "tool": "function"}
        d = {"role": role_map.get(msg.role, "user"), "parts": [{"text": msg.content}]}
        if msg.tool_calls:
            d["parts"] = []
            d["parts"].append({"text": msg.content} if msg.content else None)
            for tc in msg.tool_calls:
                d["parts"].append({
                    "function_call": {
                        "name": tc.get("name", ""),
                        "args": tc.get("args", {}),
                    }
                })
            d["parts"] = [p for p in d["parts"] if p]
        if msg.tool_call_id and msg.name:
            d["parts"] = d.get("parts", [{"text": msg.content or ""}])
            d["parts"].append({
                "function_response": {
                    "name": msg.name,
                    "response": {"result": msg.content},
                }
            })
        return d

    def _gemini_response_to_message(self, response) -> Message:
        """Parse Gemini response to our Message format."""
        text = response.text if hasattr(response, 'text') else ""
        # Check for function calls
        tool_calls = []
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            tool_calls.append({
                                "name": part.function_call.name,
                                "args": dict(part.function_call.args) if part.function_call.args else {},
                                "id": part.function_call.name,
                            })
        return Message(
            role="assistant",
            content=text or "",
            tool_calls=tool_calls if tool_calls else None,
        )

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> Message:
        """Send a text chat to Gemini and get response."""
        try:
            contents = [self._message_to_gemini_content(m) for m in messages]

            # Filter system messages out of contents
            chat_contents = [c for c in contents if c["role"] != "user" or True]

            # Find system prompt from messages
            sys_prompt = ""
            for m in messages:
                if m.role == "system":
                    sys_prompt += m.content + "\n"

            model = self._client.aio.models
            genai_tools = self._gemini_tools_from_declarations(tools)

            # Separate system instruction
            generate_config = {}
            if genai_tools:
                generate_config["tools"] = genai_tools

            response = await model.generate_content(
                model=self._chat_model,
                contents=chat_contents,
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt.strip() if sys_prompt else None,
                    **generate_config,
                ),
            )
            return self._gemini_response_to_message(response)

        except Exception as e:
            return Message(
                role="assistant",
                content=f"Error: {str(e)}"
            )

    async def stream_chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> AsyncGenerator[Message, None]:
        """Stream Gemini response tokens."""
        try:
            contents = [self._message_to_gemini_content(m) for m in messages]
            chat_contents = [c for c in contents if c["role"] != "user" or True]

            sys_prompt = ""
            for m in messages:
                if m.role == "system":
                    sys_prompt += m.content + "\n"

            genai_tools = self._gemini_tools_from_declarations(tools)

            generate_config = {}
            if genai_tools:
                generate_config["tools"] = genai_tools

            async for chunk in self._client.aio.models.generate_content_stream(
                model=self._chat_model,
                contents=chat_contents,
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt.strip() if sys_prompt else None,
                    **generate_config,
                ),
            ):
                if chunk.text:
                    yield Message(role="assistant", content=chunk.text)

        except Exception as e:
            yield Message(role="assistant", content=f"Error: {str(e)}")

    def get_models(self) -> list[dict]:
        return [
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
            {"id": "gemini-2.0-flash-lite", "name": "Gemini 2.0 Flash Lite"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
        ]


register_provider("gemini", GeminiProvider)
