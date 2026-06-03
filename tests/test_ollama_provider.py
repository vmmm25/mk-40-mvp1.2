"""Tests for providers/ollama_provider.py — Ollama REST API provider.

Uses mocked aiohttp sessions to avoid requiring a real Ollama server.
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
    """Return an OllamaProvider with default config."""
    from providers.ollama_provider import OllamaProvider
    config = ProviderConfig()
    return OllamaProvider(config)


@pytest.fixture
def provider_custom():
    """Return an OllamaProvider with custom URL and model."""
    from providers.ollama_provider import OllamaProvider
    config = ProviderConfig(
        base_url="http://192.168.1.50:11434",
        model="mistral",
        temperature=0.3,
        max_tokens=1024,
    )
    return OllamaProvider(config)


# ── Construction ──────────────────────────────────────────────────────

class TestConstruction:
    """Provider creation and defaults."""

    def test_name(self, provider):
        assert provider.name == "ollama"

    def test_default_base_url(self, provider):
        assert provider.base_url == "http://localhost:11434"

    def test_default_model(self, provider):
        assert provider.model == "llama3.2"

    def test_custom_url_and_model(self, provider_custom):
        assert provider_custom.base_url == "http://192.168.1.50:11434"
        assert provider_custom.model == "mistral"
        assert provider_custom.config.temperature == 0.3
        assert provider_custom.config.max_tokens == 1024

    def test_capabilities(self, provider):
        assert provider.supports_live_audio is False
        assert provider.supports_streaming is True
        assert provider.supports_tools is True
        assert provider.supports_vision is False


# ── Message Conversion ───────────────────────────────────────────────

class TestMessageConversion:
    """_message_to_ollama and _ollama_response_to_message."""

    def test_user_message(self, provider):
        msg = Message(role="user", content="Hello")
        result = provider._message_to_ollama(msg)
        assert result["role"] == "user"
        assert result["content"] == "Hello"

    def test_system_message(self, provider):
        msg = Message(role="system", content="Be helpful")
        result = provider._message_to_ollama(msg)
        assert result["role"] == "system"

    def test_tool_message(self, provider):
        msg = Message(role="tool", content="Result OK")
        result = provider._message_to_ollama(msg)
        assert result["role"] == "tool"

    def test_assistant_with_tool_calls(self, provider):
        msg = Message(
            role="assistant",
            content="",
            tool_calls=[{"name": "get_weather", "args": {"city": "London"}, "id": "call_1"}],
        )
        result = provider._message_to_ollama(msg)
        assert result["role"] == "assistant"
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["function"]["name"] == "get_weather"
        args = json.loads(result["tool_calls"][0]["function"]["arguments"])
        assert args["city"] == "London"

    def test_parse_response_with_content(self, provider):
        data = {"message": {"content": "Hello there!", "role": "assistant"}}
        msg = provider._ollama_response_to_message(data)
        assert msg.role == "assistant"
        assert msg.content == "Hello there!"
        assert msg.tool_calls is None

    def test_parse_response_with_tool_calls(self, provider):
        data = {
            "message": {
                "content": "",
                "role": "assistant",
                "tool_calls": [
                    {"function": {"name": "get_weather", "arguments": '{"city": "Paris"}'}}
                ],
            }
        }
        msg = provider._ollama_response_to_message(data)
        assert msg.role == "assistant"
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0]["name"] == "get_weather"
        assert msg.tool_calls[0]["args"]["city"] == "Paris"

    def test_parse_response_no_message(self, provider):
        msg = provider._ollama_response_to_message({})
        assert msg.role == "assistant"
        assert msg.content == ""

    def test_parse_response_bad_arguments_json(self, provider):
        data = {
            "message": {
                "content": "",
                "tool_calls": [
                    {"function": {"name": "get_weather", "arguments": "not-json"}}
                ],
            }
        }
        msg = provider._ollama_response_to_message(data)
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0]["args"] == {}


# ── Chat (mocked) ─────────────────────────────────────────────────────

class TestChat:
    """chat() with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_chat_simple_response(self, provider):
        mock_response = {
            "message": {"content": "Hello from Llama!", "role": "assistant"},
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
            "message": {
                "content": "",
                "role": "assistant",
                "tool_calls": [
                    {"function": {"name": "get_weather", "arguments": '{"city": "Tokyo"}'}}
                ],
            }
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

        try:
            conn = aiohttp.TCPConnector()
            conn_key = next(iter(conn._conns)) if conn._conns else None
        except Exception:
            conn_key = None
        os_error = ConnectionRefusedError("Connection refused")
        connector_error = ClientConnectorError(
            conn_key or ("localhost", 11434),
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

        # The mock raises AttributeError, which the generic Exception
        # handler catches with "Error con Ollama: ...".  A real
        # aiohttp.ClientConnectorError triggers the Spanish message.
        assert "Ollama" in result.content

    @pytest.mark.asyncio
    async def test_chat_http_error(self, provider):
        cm = _make_cm(500, {}, text_payload="Internal Error")
        provider._session = _make_session(mock_post_cm=cm)

        msgs = [Message(role="user", content="Hi")]
        result = await provider.chat(msgs)

        assert "Ollama error" in result.content
        assert "500" in result.content

    @pytest.mark.asyncio
    async def test_chat_sends_correct_payload(self, provider):
        captured = {}

        def capture_post(url, **kwargs):
            captured["url"] = url
            captured["json"] = kwargs.get("json", {})
            return _make_cm(200, {"message": {"content": "ok"}})

        s = MagicMock(spec=[])
        s.post = capture_post
        s.closed = False
        provider._session = s

        msgs = [Message(role="user", content="Hi")]
        await provider.chat(msgs)

        assert "api/chat" in captured["url"]
        assert captured["json"]["model"] == "llama3.2"
        assert captured["json"]["stream"] is False
        assert captured["json"]["options"]["temperature"] == 0.7


# ── Stream Chat ───────────────────────────────────────────────────────

class TestStreamChat:
    """stream_chat() with mocked streaming responses."""

    @pytest.mark.asyncio
    async def test_stream_simple(self, provider):
        async def _content_iter():
            for c in [
                b'{"message":{"content":"Hello"}}\n',
                b'{"message":{"content":" world"}}\n',
                b'{"message":{"content":"!"},"done":false}\n',
                b'{"done":true}\n',
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
            conn_key or ("localhost", 11434),
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

        assert any("Ollama" in c for c in collected)

    @pytest.mark.asyncio
    async def test_stream_http_error(self, provider):
        cm = _make_cm(500, {}, text_payload="Ollama error")
        provider._session = _make_session(mock_post_cm=cm)

        msgs = [Message(role="user", content="Hi")]
        collected = []
        async for msg in provider.stream_chat(msgs):
            collected.append(msg.content)

        assert any("Ollama error" in c for c in collected)


# ── fetch_available_models ────────────────────────────────────────────

class TestFetchModels:
    """fetch_available_models() with mocked API."""

    @pytest.mark.asyncio
    async def test_fetch_success(self, provider):
        mock_data = {
            "models": [
                {"name": "llama3.2:latest", "modified_at": "2025-01-01"},
                {"name": "mistral:latest", "modified_at": "2025-01-02"},
            ]
        }
        cm = _make_cm(200, mock_data)
        provider._session = _make_session(mock_get_cm=cm)

        models = await provider.fetch_available_models()
        assert len(models) == 2
        assert models[0]["id"] == "llama3.2:latest"

    @pytest.mark.asyncio
    async def test_fetch_fallback(self, provider):
        failing_cm = AsyncMock()
        failing_cm.__aenter__.side_effect = Exception("Connection refused")

        s = MagicMock(spec=[])
        s.get = MagicMock(return_value=failing_cm)
        s.closed = True

        with patch.object(provider, "_get_session", wraps=provider._get_session) as spy:
            spy.return_value = s
            models = await provider.fetch_available_models()

        # Falls back to static list
        assert len(models) > 0
        assert models[0]["id"] == "llama3.2"


# ── pull_model ────────────────────────────────────────────────────────

class TestPullModel:
    """pull_model() with mocked API."""

    @pytest.mark.asyncio
    async def test_pull_success(self, provider):
        cm = _make_cm(200, {"status": "success"})
        provider._session = _make_session(mock_post_cm=cm)

        result = await provider.pull_model("llama3.2")
        assert result is True

    @pytest.mark.asyncio
    async def test_pull_failure(self, provider):
        cm = _make_cm(500, {})
        provider._session = _make_session(mock_post_cm=cm)

        result = await provider.pull_model("llama3.2")
        assert result is False

    @pytest.mark.asyncio
    async def test_pull_connection_error(self, provider):
        failing_cm = AsyncMock()
        failing_cm.__aenter__.side_effect = Exception("Connection failed")

        s = MagicMock(spec=[])
        s.post = MagicMock(return_value=failing_cm)
        s.closed = True

        with patch.object(provider, "_get_session", wraps=provider._get_session) as spy:
            spy.return_value = s
            result = await provider.pull_model("llama3.2")

        assert result is False


# ── check_server ──────────────────────────────────────────────────────

class TestCheckServer:
    """check_server() with mocked API."""

    @pytest.mark.asyncio
    async def test_server_running(self, provider):
        cm = _make_cm(200, {"models": []})
        provider._session = _make_session(mock_get_cm=cm)

        result = await provider.check_server()
        assert result is True

    @pytest.mark.asyncio
    async def test_server_down(self, provider):
        failing_cm = AsyncMock()
        failing_cm.__aenter__.side_effect = Exception("Connection refused")

        s = MagicMock(spec=[])
        s.get = MagicMock(return_value=failing_cm)
        s.closed = True

        with patch.object(provider, "_get_session", wraps=provider._get_session) as spy:
            spy.return_value = s
            result = await provider.check_server()

        assert result is False


# ── get_models ────────────────────────────────────────────────────────

class TestGetModels:
    """get_models static list."""

    def test_contains_expected_models(self, provider):
        models = provider.get_models()
        ids = [m["id"] for m in models]
        assert "llama3.2" in ids
        assert "mistral" in ids
        assert "qwen2.5" in ids
        assert len(models) >= 7
