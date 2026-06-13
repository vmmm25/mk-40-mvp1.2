"""Tests for providers/openrouter_provider.py — OpenRouter API provider.

Uses mocked aiohttp sessions to avoid requiring a real API key or network.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from providers.base import Message, ProviderConfig


# ── Helpers ────────────────────────────────────────────────────────────

def _make_session(mock_post_cm=None, mock_get_cm=None):
    """Create a mock aiohttp session injected directly into the provider."""
    s = MagicMock(spec=[])
    if mock_post_cm is None:
        mock_post_cm = _make_cm(200, {})
    if mock_get_cm is None:
        mock_get_cm = _make_cm(200, {})
    s.post = MagicMock(return_value=mock_post_cm)
    s.get = MagicMock(return_value=mock_get_cm)
    s.closed = False
    return s


def _make_cm(status: int, json_payload: dict, text_payload: str = ""):
    """Build an async-context-manager mock (the thing ``async with`` receives)."""
    cm = AsyncMock()
    resp = AsyncMock(spec=[])
    resp.status = status
    resp.json = AsyncMock(return_value=json_payload)
    resp.text = AsyncMock(return_value=text_payload)
    resp.content = AsyncMock(spec=[])
    cm.__aenter__.return_value = resp
    cm.__aexit__.return_value = None
    return cm


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def provider():
    """Return an OpenRouterProvider with default config."""
    from providers.openrouter_provider import OpenRouterProvider
    config = ProviderConfig(api_key="sk-or-v1-test123")
    return OpenRouterProvider(config)


@pytest.fixture
def provider_claude():
    """Return an OpenRouterProvider configured with a Claude model."""
    from providers.openrouter_provider import OpenRouterProvider
    config = ProviderConfig(
        api_key="sk-or-v1-test123",
        model="anthropic/claude-3.5-sonnet",
    )
    return OpenRouterProvider(config)


# ── Construction ──────────────────────────────────────────────────────

class TestConstruction:
    """Provider creation and defaults."""

    def test_name(self, provider):
        assert provider.name == "openrouter"

    def test_default_base_url(self, provider):
        assert provider.base_url == "https://openrouter.ai/api/v1"

    def test_default_model(self, provider):
        assert provider.model == "nvidia/nemotron-3-super-120b-a12b:free"

    def test_custom_model(self):
        from providers.openrouter_provider import OpenRouterProvider
        config = ProviderConfig(api_key="key", model="custom/model")
        p = OpenRouterProvider(config)
        assert p.model == "custom/model"

    def test_capabilities(self, provider):
        assert provider.supports_live_audio is False
        assert provider.supports_streaming is True
        assert provider.supports_tools is True
        assert provider.supports_vision is True

    def test_api_key_stored(self, provider):
        assert provider.api_key == "sk-or-v1-test123"

    def test_is_claude_false(self, provider):
        assert provider._is_claude() is False

    def test_is_claude_true(self, provider_claude):
        assert provider_claude._is_claude() is True


# ── Message Conversion ───────────────────────────────────────────────

class TestMessageConversion:
    """_message_to_openrouter and _openrouter_response_to_message."""

    def test_user_message(self, provider):
        msg = Message(role="user", content="Hello")
        result = provider._message_to_openrouter(msg)
        assert result["role"] == "user"
        assert result["content"] == "Hello"

    def test_system_message(self, provider):
        msg = Message(role="system", content="Be helpful")
        result = provider._message_to_openrouter(msg)
        assert result["role"] == "system"
        assert result["content"] == "Be helpful"

    def test_system_message_claude(self, provider_claude):
        """Claude models require the 'developer' role instead of 'system'."""
        msg = Message(role="system", content="Be helpful")
        result = provider_claude._message_to_openrouter(msg)
        assert result["role"] == "developer"
        assert result["content"] == "Be helpful"

    def test_tool_result_message(self, provider):
        msg = Message(role="tool", content='{"result": "ok"}', tool_call_id="call_123")
        result = provider._message_to_openrouter(msg)
        assert result["role"] == "tool"
        assert result["tool_call_id"] == "call_123"

    def test_assistant_with_tool_calls(self, provider):
        msg = Message(
            role="assistant",
            content="",
            tool_calls=[{"name": "get_weather", "args": {"city": "London"}, "id": "call_1"}],
        )
        result = provider._message_to_openrouter(msg)
        assert result["role"] == "assistant"
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["function"]["name"] == "get_weather"
        args = json.loads(result["tool_calls"][0]["function"]["arguments"])
        assert args["city"] == "London"

    def test_parse_response_with_content(self, provider):
        data = {
            "choices": [{"message": {"content": "Hello there!", "role": "assistant"}}],
        }
        msg = provider._openrouter_response_to_message(data)
        assert msg.role == "assistant"
        assert msg.content == "Hello there!"
        assert msg.tool_calls is None

    def test_parse_response_with_tool_calls(self, provider):
        data = {
            "choices": [{
                "message": {
                    "content": "",
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "get_weather", "arguments": '{"city": "Paris"}'},
                    }],
                }
            }],
        }
        msg = provider._openrouter_response_to_message(data)
        assert msg.role == "assistant"
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0]["name"] == "get_weather"

    def test_parse_response_empty_choices(self, provider):
        msg = provider._openrouter_response_to_message({"choices": []})
        assert msg.role == "assistant"
        assert "Error parsing response" in msg.content

    def test_parse_response_no_choices_key(self, provider):
        msg = provider._openrouter_response_to_message({})
        assert msg.role == "assistant"
        assert msg.content == ""
        assert msg.tool_calls is None


# ── Chat (mocked) ─────────────────────────────────────────────────────

class TestChat:
    """chat() with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_chat_simple_response(self, provider):
        mock_response = {
            "choices": [{"message": {"content": "Hello from OpenRouter!", "role": "assistant"}}],
        }
        cm = _make_cm(200, mock_response)
        provider._session = _make_session(mock_post_cm=cm)

        msgs = [Message(role="user", content="Hi")]
        result = await provider.chat(msgs)
        assert result.role == "assistant"
        assert "Hello" in result.content

    @pytest.mark.asyncio
    async def test_chat_with_tools(self, provider):
        mock_response = {
            "choices": [{
                "message": {
                    "content": "",
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "tc_1",
                        "type": "function",
                        "function": {"name": "get_weather", "arguments": '{"city": "Tokyo"}'},
                    }],
                }
            }],
        }
        cm = _make_cm(200, mock_response)
        provider._session = _make_session(mock_post_cm=cm)

        msgs = [Message(role="user", content="Weather?")]
        tools = [{"name": "get_weather", "description": "Get weather", "parameters": {"type": "OBJECT", "properties": {"city": {"type": "STRING"}}, "required": ["city"]}}]
        result = await provider.chat(msgs, tools=tools)
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_chat_connection_error(self, provider):
        import aiohttp
        from aiohttp import ClientConnectorError
        from aiohttp.client_reqrep import ConnectionKey

        try:
            conn = aiohttp.TCPConnector()
            conn_key = next(iter(conn._conns)) if conn._conns else None
        except Exception:
            conn_key = None
        if conn_key is None:
            conn_key = ConnectionKey(
                "openrouter.ai", 443, True, None, None, None, None
            )
        os_error = ConnectionRefusedError("Connection refused")
        connector_error = ClientConnectorError(
            conn_key,
            os_error,
        )

        failing_cm = AsyncMock()
        failing_cm.__aenter__.side_effect = connector_error

        s = MagicMock(spec=[])
        s.post = MagicMock(return_value=failing_cm)
        s.closed = True

        with patch.object(provider, "_get_session", wraps=provider._get_session) as spy:
            spy.return_value = s
            msgs = [Message(role="user", content="Hi")]
            result = await provider.chat(msgs)

        assert "No se puede conectar" in result.content

    @pytest.mark.asyncio
    async def test_chat_http_error(self, provider):
        cm = _make_cm(401, {}, text_payload="Unauthorized")
        provider._session = _make_session(mock_post_cm=cm)

        msgs = [Message(role="user", content="Hi")]
        result = await provider.chat(msgs)

        assert "OpenRouter error" in result.content
        assert "401" in result.content

    @pytest.mark.asyncio
    async def test_chat_sends_correct_payload(self, provider):
        captured = {}

        def capture_post(url, **kwargs):
            captured["url"] = url
            captured["json"] = kwargs.get("json", {})
            captured["headers"] = kwargs.get("headers", {})
            return _make_cm(200, {"choices": [{"message": {"content": "ok"}}]})

        s = MagicMock(spec=[])
        s.post = capture_post
        s.closed = False
        provider._session = s

        msgs = [Message(role="user", content="Hi")]
        await provider.chat(msgs)

        assert "chat/completions" in captured["url"]
        assert captured["json"]["model"] == "nvidia/nemotron-3-super-120b-a12b:free"
        assert captured["json"]["stream"] is False
        assert "Authorization" in captured["headers"]
        assert "Bearer" in captured["headers"]["Authorization"]


# ── Stream Chat ───────────────────────────────────────────────────────

class TestStreamChat:
    """stream_chat() with mocked streaming responses."""

    @pytest.mark.asyncio
    async def test_stream_simple(self, provider):
        async def _content_iter():
            for c in [
                b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
                b'data: {"choices":[{"delta":{"content":" world"}}]}\n',
                b'data: {"choices":[{"delta":{"content":"!"}}]}\n',
                b"data: [DONE]\n",
            ]:
                yield c

        resp = AsyncMock(spec=[])
        resp.status = 200
        resp.content = _content_iter()

        cm = AsyncMock()
        cm.__aenter__.return_value = resp
        cm.__aexit__.return_value = None

        s = MagicMock(spec=[])
        s.post = MagicMock(return_value=cm)
        s.closed = False
        provider._session = s

        msgs = [Message(role="user", content="Say hi")]
        collected = []
        async for msg in provider.stream_chat(msgs):
            collected.append(msg.content)

        assert collected == ["Hello", " world", "!"]

    @pytest.mark.asyncio
    async def test_stream_connection_error(self, provider):
        import aiohttp
        from aiohttp import ClientConnectorError

        try:
            conn = aiohttp.TCPConnector()
            conn_key = next(iter(conn._conns)) if conn._conns else None
        except Exception:
            conn_key = None
        os_error = ConnectionRefusedError("Connection refused")
        connector_error = ClientConnectorError(
            conn_key or ("openrouter.ai", 443),
            os_error,
        )

        failing_cm = AsyncMock()
        failing_cm.__aenter__.side_effect = connector_error

        s = MagicMock(spec=[])
        s.post = MagicMock(return_value=failing_cm)
        s.closed = True

        with patch.object(provider, "_get_session", wraps=provider._get_session) as spy:
            spy.return_value = s
            msgs = [Message(role="user", content="Hi")]
            collected = []
            async for msg in provider.stream_chat(msgs):
                collected.append(msg.content)

        assert any("No se puede conectar" in c for c in collected)

    @pytest.mark.asyncio
    async def test_stream_http_error(self, provider):
        cm = _make_cm(429, {}, text_payload="Rate limited")
        provider._session = _make_session(mock_post_cm=cm)

        msgs = [Message(role="user", content="Hi")]
        collected = []
        async for msg in provider.stream_chat(msgs):
            collected.append(msg.content)

        assert any("OpenRouter error" in c for c in collected)


# ── get_models ────────────────────────────────────────────────────────

class TestGetModels:
    """get_models static list."""

    def test_contains_expected_models(self, provider):
        models = provider.get_models()
        ids = [m["id"] for m in models]
        assert "google/gemma-4-31b-it:free" in ids
        assert "meta-llama/llama-3.3-70b-instruct:free" in ids
        assert len(models) >= 20
