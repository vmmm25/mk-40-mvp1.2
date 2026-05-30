"""Tests for providers/lmstudio_provider.py — LM Studio OpenAI-compatible provider.

These tests use mocked aiohttp sessions to avoid requiring a real LM Studio server.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from providers.base import Message, ProviderConfig


# ── Helpers ────────────────────────────────────────────────────────────

def _make_session(mock_post_cm=None, mock_get_cm=None):
    """Create a mock aiohttp session injected directly into the provider.

    Each ``_cm`` arg is a pre-built AsyncMock that will be returned when
    ``session.post()`` / ``session.get()`` is called.
    Setting ``provider._session`` directly avoids the complexities of
    patching the ``async def _get_session`` coroutine.
    """
    s = MagicMock(spec=[])
    # If no explicit CM is provided, build a default one that returns 200 + empty JSON
    if mock_post_cm is None:
        mock_post_cm = _make_cm(200, {})
    if mock_get_cm is None:
        mock_get_cm = _make_cm(200, {})

    # Make post() / get() return the CM directly (not a coroutine)
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
    # For streaming: content is an async iterable
    resp.content = AsyncMock(spec=[])
    cm.__aenter__.return_value = resp
    cm.__aexit__.return_value = None
    return cm


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def provider():
    """Return an LMStudioProvider with default config."""
    from providers.lmstudio_provider import LMStudioProvider
    config = ProviderConfig(
        base_url="http://localhost:1234/v1",
        temperature=0.7,
        max_tokens=4096,
    )
    return LMStudioProvider(config)


@pytest.fixture
def provider_with_model():
    """Return an LMStudioProvider with a specific model set."""
    from providers.lmstudio_provider import LMStudioProvider
    config = ProviderConfig(
        base_url="http://localhost:1234/v1",
        model="llama-3.2-3b-instruct",
        temperature=0.5,
        max_tokens=2048,
    )
    return LMStudioProvider(config)


# ── Construction ──────────────────────────────────────────────────────

class TestConstruction:
    """Provider creation and defaults."""

    def test_name(self, provider):
        assert provider.name == "lmstudio"

    def test_default_base_url(self):
        from providers.lmstudio_provider import LMStudioProvider
        config = ProviderConfig()
        p = LMStudioProvider(config)
        assert p.base_url == "http://localhost:1234/v1"

    def test_custom_base_url(self):
        from providers.lmstudio_provider import LMStudioProvider
        config = ProviderConfig(base_url="http://192.168.1.100:8080/v1")
        p = LMStudioProvider(config)
        assert p.base_url == "http://192.168.1.100:8080/v1"

    def test_capabilities(self, provider):
        assert provider.supports_live_audio is False
        assert provider.supports_streaming is True
        assert provider.supports_tools is True
        assert provider.supports_vision is True


# ── Message Conversion ───────────────────────────────────────────────

class TestMessageConversion:
    """_message_to_lmstudio and _lmstudio_response_to_message."""

    def test_simple_user_message(self, provider):
        msg = Message(role="user", content="Hello")
        result = provider._message_to_lmstudio(msg)
        assert result["role"] == "user"
        assert result["content"] == "Hello"

    def test_system_message(self, provider):
        msg = Message(role="system", content="Be helpful")
        result = provider._message_to_lmstudio(msg)
        assert result["role"] == "system"
        assert result["content"] == "Be helpful"

    def test_tool_result_message(self, provider):
        msg = Message(role="tool", content='{"result": "ok"}', tool_call_id="call_123")
        result = provider._message_to_lmstudio(msg)
        assert result["role"] == "tool"
        assert result["tool_call_id"] == "call_123"

    def test_assistant_with_tool_calls(self, provider):
        msg = Message(
            role="assistant",
            content="",
            tool_calls=[{"name": "get_weather", "args": {"city": "London"}, "id": "call_1"}],
        )
        result = provider._message_to_lmstudio(msg)
        assert result["role"] == "assistant"
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["function"]["name"] == "get_weather"
        args = json.loads(result["tool_calls"][0]["function"]["arguments"])
        assert args["city"] == "London"

    def test_parse_response_with_content(self, provider):
        data = {
            "choices": [{"message": {"content": "Hello there!", "role": "assistant"}}],
        }
        msg = provider._lmstudio_response_to_message(data)
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
        msg = provider._lmstudio_response_to_message(data)
        assert msg.role == "assistant"
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0]["name"] == "get_weather"
        assert msg.tool_calls[0]["args"]["city"] == "Paris"

    def test_parse_response_empty_dict_returns_empty_content(self, provider):
        msg = provider._lmstudio_response_to_message({})
        assert msg.role == "assistant"
        assert msg.content == ""
        assert msg.tool_calls is None

    def test_parse_response_no_choices(self, provider):
        msg = provider._lmstudio_response_to_message({"choices": []})
        assert msg.role == "assistant"
        # Empty choices list triggers IndexError in the parser,
        # which returns a descriptive error message
        assert "Error parsing LM Studio response" in msg.content


# ── Chat (mocked) ─────────────────────────────────────────────────────

class TestChat:
    """chat() with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_chat_simple_response(self, provider):
        mock_response = {
            "choices": [{"message": {"content": "Hello! How can I help?", "role": "assistant"}}],
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

        msgs = [Message(role="user", content="Weather in Tokyo?")]
        tools = [{"name": "get_weather", "description": "Get weather", "parameters": {"type": "OBJECT", "properties": {"city": {"type": "STRING"}}, "required": ["city"]}}]
        result = await provider.chat(msgs, tools=tools)

        assert result.role == "assistant"
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_chat_connection_error(self, provider):
        """When LM Studio is not running, should return a friendly error message."""
        provider._session = None  # force _get_session to create new session

        # Simulate ClientConnectorError by making the POST fail at CM __aenter__
        failing_cm = AsyncMock()
        failing_cm.__aenter__.side_effect = Exception("Connection refused")
        failing_s = MagicMock(spec=[])
        failing_s.post = MagicMock(return_value=failing_cm)
        failing_s.closed = True

        with patch.object(provider, "_get_session", wraps=provider._get_session) as spy:
            # Make the first call return our failing session
            spy.return_value = failing_s
            msgs = [Message(role="user", content="Hi")]
            result = await provider.chat(msgs)

        assert "Error con LM Studio" in result.content

    @pytest.mark.asyncio
    async def test_chat_http_error(self, provider):
        """Non-200 status should return formatted error message."""
        cm = _make_cm(500, {}, text_payload="Internal Server Error")
        provider._session = _make_session(mock_post_cm=cm)

        msgs = [Message(role="user", content="Hi")]
        result = await provider.chat(msgs)

        assert "LM Studio error" in result.content
        assert "500" in result.content

    @pytest.mark.asyncio
    async def test_chat_sends_correct_payload(self, provider):
        """Verify the exact payload sent to LM Studio's API."""
        captured = {}

        def capture_post(url, **kwargs):
            captured["url"] = url
            captured["json"] = kwargs.get("json", {})
            captured["headers"] = kwargs.get("headers", {})
            return _make_cm(200, {"choices": [{"message": {"content": "ok", "role": "assistant"}}]})

        s = MagicMock(spec=[])
        s.post = capture_post
        s.closed = False
        provider._session = s

        msgs = [Message(role="user", content="Hi")]
        await provider.chat(msgs)

        assert "chat/completions" in captured["url"]
        assert captured["json"]["messages"][0]["role"] == "user"
        assert captured["json"]["messages"][0]["content"] == "Hi"
        assert captured["json"]["stream"] is False
        assert "model" not in captured["json"]  # no model set = not sent


# ── Chat with model ──────────────────────────────────────────────────

class TestChatWithModel:
    """When a specific model is configured."""

    @pytest.mark.asyncio
    async def test_sends_model_in_payload(self, provider_with_model):
        captured = {}

        def capture_post(url, **kwargs):
            captured["json"] = kwargs.get("json", {})
            return _make_cm(200, {"choices": [{"message": {"content": "ok", "role": "assistant"}}]})

        s = MagicMock(spec=[])
        s.post = capture_post
        s.closed = False
        provider_with_model._session = s

        msgs = [Message(role="user", content="Hi")]
        await provider_with_model.chat(msgs)

        assert captured["json"]["model"] == "llama-3.2-3b-instruct"
        assert captured["json"]["temperature"] == 0.5
        assert captured["json"]["max_tokens"] == 2048


# ── Stream Chat ───────────────────────────────────────────────────────

class TestStreamChat:
    """stream_chat() with mocked streaming responses."""

    @pytest.mark.asyncio
    async def test_stream_simple(self, provider):
        lines = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b'data: {"choices":[{"delta":{"content":" world"}}]}\n',
            b'data: {"choices":[{"delta":{"content":"!"}}]}\n',
            b"data: [DONE]\n",
        ]
        self._line_index = 0

        async def _readline():
            if self._line_index < len(lines):
                line = lines[self._line_index]
                self._line_index += 1
                return line
            return b""

        # Build a response object where .content.readline() is callable
        resp = AsyncMock()
        resp.status = 200
        resp.content.readline = _readline

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
        """When LM Studio is not reachable, stream_chat should yield error message."""
        import aiohttp

        # Build a proper ClientConnectorError
        try:
            conn = aiohttp.TCPConnector()
            conn_key = next(iter(conn._conns)) if conn._conns else None
        except Exception:
            conn_key = None
        os_error = ConnectionRefusedError("Connection refused")
        connector_error = aiohttp.ClientConnectorError(
            conn_key or ("localhost", 1234),
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


# ── List Models ───────────────────────────────────────────────────────

class TestListModels:
    """list_models() with mocked and fallback behavior."""

    @pytest.mark.asyncio
    async def test_list_models_success(self, provider):
        mock_response_data = {
            "data": [
                {"id": "llama-3.2-3b-instruct", "object": "model"},
                {"id": "mistral-7b", "object": "model"},
            ]
        }

        cm = _make_cm(200, mock_response_data)
        provider._session = _make_session(mock_get_cm=cm)

        models = await provider.list_models()

        assert len(models) == 2
        assert models[0]["id"] == "llama-3.2-3b-instruct"
        assert models[1]["id"] == "mistral-7b"

    @pytest.mark.asyncio
    async def test_list_models_fallback(self, provider):
        """When the server is not reachable, return static fallback list."""
        failing_cm = AsyncMock()
        failing_cm.__aenter__.side_effect = Exception("Connection refused")

        s = MagicMock(spec=[])
        s.get = MagicMock(return_value=failing_cm)
        s.closed = True

        with patch.object(provider, "_get_session", wraps=provider._get_session) as spy:
            spy.return_value = s
            models = await provider.list_models()

        assert len(models) == 1
        assert models[0]["id"] == "local-model"


# ── Tool Format Conversion ────────────────────────────────────────────

class TestToolConversion:
    """convert_tools_openai — shared static method."""

    def test_converts_mark_xl_tool_format(self, provider):
        tools = [
            {
                "name": "get_weather",
                "description": "Get weather for a city",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "city": {"type": "STRING", "description": "City name"},
                    },
                    "required": ["city"],
                },
            }
        ]
        result = provider.convert_tools_openai(tools)
        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "get_weather"
        assert result[0]["function"]["parameters"]["properties"]["city"]["type"] == "string"
        assert result[0]["function"]["parameters"]["required"] == ["city"]


