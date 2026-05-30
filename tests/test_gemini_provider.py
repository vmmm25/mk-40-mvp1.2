"""Tests for providers/gemini_provider.py — Google Gemini SDK provider.

Uses mocked genai.Client to avoid requiring real API keys or network.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from providers.base import Message, ProviderConfig


# ── Helper: build mock Gemini response objects ─────────────────────────

def _make_text_response(text: str):
    """Create a mock Gemini response with text content."""
    resp = MagicMock()
    resp.text = text
    resp.candidates = []
    return resp


def _make_tool_call_response(name: str, args: dict):
    """Create a mock Gemini response with a function call."""
    fc = MagicMock()
    fc.name = name
    fc.args = args

    part = MagicMock()
    part.function_call = fc
    part.text = None

    content = MagicMock()
    content.parts = [part]
    content.text = ""

    candidate = MagicMock()
    candidate.content = content

    resp = MagicMock()
    resp.text = ""
    resp.candidates = [candidate]
    return resp


def _make_mock_client(text_response=None, tool_response=None):
    """Build a mock genai.Client with configured async model methods."""
    mock_model = MagicMock()

    if text_response:
        mock_model.generate_content = AsyncMock(return_value=text_response)

    if tool_response:
        mock_model.generate_content = AsyncMock(return_value=tool_response)

    mock_client = MagicMock()
    mock_client.aio.models = mock_model
    mock_client.aio.live.connect = AsyncMock()

    return mock_client


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def provider():
    """Return a GeminiProvider with a mocked client."""
    from providers.gemini_provider import GeminiProvider

    with patch("providers.gemini_provider.genai.Client") as mk_cls:
        mk_cls.return_value = _make_mock_client()
        config = ProviderConfig(api_key="test-key-123")
        p = GeminiProvider(config)
        # Store the mock class so tests can access it
        p._mock_client_class = mk_cls
        yield p


@pytest.fixture
def provider_no_key():
    """Return a GeminiProvider without an API key."""
    from providers.gemini_provider import GeminiProvider

    with patch("providers.gemini_provider.genai.Client") as mk_cls:
        mk_cls.return_value = _make_mock_client()
        config = ProviderConfig()
        p = GeminiProvider(config)
        p._mock_client_class = mk_cls
        yield p


# ── Construction ──────────────────────────────────────────────────────

class TestConstruction:
    """Provider creation and defaults."""

    def test_name(self, provider):
        assert provider.name == "gemini"

    def test_capabilities(self, provider):
        assert provider.supports_live_audio is True
        assert provider.supports_streaming is True
        assert provider.supports_tools is True
        assert provider.supports_vision is True

    def test_api_key_stored(self, provider):
        assert provider.config.api_key == "test-key-123"

    def test_no_api_key_still_creates(self, provider_no_key):
        assert provider_no_key.config.api_key == ""

    def test_allows_key_via_client(self, provider):
        # Ensure the mock was called with the API key
        provider._mock_client_class.assert_called_once()
        _, kwargs = provider._mock_client_class.call_args
        assert kwargs["api_key"] == "test-key-123"


# ── Message Conversion ───────────────────────────────────────────────

class TestMessageConversion:
    """_message_to_gemini_content and _gemini_response_to_message."""

    def test_user_message(self, provider):
        msg = Message(role="user", content="Hello")
        result = provider._message_to_gemini_content(msg)
        assert result["role"] == "user"
        assert result["parts"][0]["text"] == "Hello"

    def test_assistant_message(self, provider):
        msg = Message(role="assistant", content="Hi there")
        result = provider._message_to_gemini_content(msg)
        assert result["role"] == "model"
        assert result["parts"][0]["text"] == "Hi there"

    def test_system_message(self, provider):
        msg = Message(role="system", content="Be helpful")
        result = provider._message_to_gemini_content(msg)
        assert result["role"] == "user"  # Gemini maps system→user, sent separately
        assert result["parts"][0]["text"] == "Be helpful"

    def test_tool_result_message(self, provider):
        msg = Message(role="tool", content='{"result": "ok"}', tool_call_id="call_123", name="get_weather")
        result = provider._message_to_gemini_content(msg)
        assert result["role"] == "function"
        # Should have a function_response part
        has_fr = any(
            "function_response" in p
            for p in result.get("parts", [])
        )
        assert has_fr

    def test_assistant_with_tool_calls(self, provider):
        msg = Message(
            role="assistant",
            content="",
            tool_calls=[{"name": "get_weather", "args": {"city": "London"}, "id": "call_1"}],
        )
        result = provider._message_to_gemini_content(msg)
        assert result["role"] == "model"
        # Should have a function_call part
        has_fc = any(
            "function_call" in p
            for p in result.get("parts", [])
        )
        assert has_fc

    def test_parse_text_response(self, provider):
        resp = _make_text_response("Hello there!")
        msg = provider._gemini_response_to_message(resp)
        assert msg.role == "assistant"
        assert msg.content == "Hello there!"
        assert msg.tool_calls is None

    def test_parse_tool_call_response(self, provider):
        resp = _make_tool_call_response("get_weather", {"city": "Paris"})
        msg = provider._gemini_response_to_message(resp)
        assert msg.role == "assistant"
        assert msg.content == ""
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0]["name"] == "get_weather"
        assert msg.tool_calls[0]["args"]["city"] == "Paris"

    def test_parse_empty_response(self, provider):
        resp = MagicMock()
        resp.text = None  # no text attr — hasattr returns False
        # Remove text to simulate missing attribute
        del resp.text
        resp.candidates = []
        msg = provider._gemini_response_to_message(resp)
        assert msg.role == "assistant"
        assert msg.content == ""
        assert msg.tool_calls is None


# ── Chat (mocked SDK) ────────────────────────────────────────────────

class TestChat:
    """chat() with mocked Gemini SDK responses."""

    @pytest.mark.asyncio
    async def test_chat_simple_response(self):
        from providers.gemini_provider import GeminiProvider

        text_resp = _make_text_response("Hello! How can I help?")
        mock_client = _make_mock_client(text_response=text_resp)

        with patch("providers.gemini_provider.genai.Client", return_value=mock_client):
            config = ProviderConfig(api_key="test-key")
            p = GeminiProvider(config)

        msgs = [Message(role="user", content="Hi")]
        result = await p.chat(msgs)
        assert result.role == "assistant"
        assert "Hello" in result.content

    @pytest.mark.asyncio
    async def test_chat_with_tools(self):
        from providers.gemini_provider import GeminiProvider

        tool_resp = _make_tool_call_response("get_weather", {"city": "Tokyo"})
        mock_client = _make_mock_client(tool_response=tool_resp)

        with patch("providers.gemini_provider.genai.Client", return_value=mock_client):
            config = ProviderConfig(api_key="test-key")
            p = GeminiProvider(config)

        msgs = [Message(role="user", content="Weather in Tokyo?")]
        tools = [{"name": "get_weather", "description": "Get weather", "parameters": {"type": "OBJECT", "properties": {"city": {"type": "STRING"}}, "required": ["city"]}}]
        result = await p.chat(msgs, tools=tools)
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_chat_error_returns_friendly_message(self):
        from providers.gemini_provider import GeminiProvider

        mock_model = MagicMock()
        mock_model.generate_content = AsyncMock(side_effect=Exception("API quota exceeded"))

        mock_client = MagicMock()
        mock_client.aio.models = mock_model
        mock_client.aio.live.connect = AsyncMock()

        with patch("providers.gemini_provider.genai.Client", return_value=mock_client):
            config = ProviderConfig(api_key="test-key")
            p = GeminiProvider(config)

        msgs = [Message(role="user", content="Hi")]
        result = await p.chat(msgs)
        assert "Error" in result.content
        assert "API quota exceeded" in result.content


# ── Stream Chat ───────────────────────────────────────────────────────

class TestStreamChat:
    """stream_chat() with mocked Gemini SDK."""

    @pytest.mark.asyncio
    async def test_stream_simple(self):
        from providers.gemini_provider import GeminiProvider

        async def _stream():
            yield MagicMock(text="Hello")
            yield MagicMock(text=" world")
            yield MagicMock(text="!")

        mock_model = MagicMock()
        mock_model.generate_content_stream = MagicMock(return_value=_stream())

        mock_client = MagicMock()
        mock_client.aio.models = mock_model
        mock_client.aio.live.connect = AsyncMock()

        with patch("providers.gemini_provider.genai.Client", return_value=mock_client):
            config = ProviderConfig(api_key="test-key")
            p = GeminiProvider(config)

        msgs = [Message(role="user", content="Say hi")]
        collected = []
        async for msg in p.stream_chat(msgs):
            collected.append(msg.content)

        assert collected == ["Hello", " world", "!"]

    @pytest.mark.asyncio
    async def test_stream_error(self):
        from providers.gemini_provider import GeminiProvider

        mock_model = MagicMock()
        mock_model.generate_content_stream.side_effect = Exception("Stream failed")

        # Need to make it work as an async generator — side_effect won't work directly
        # Instead, set up the mock so iterating raises
        async def _broken():
            raise Exception("Stream failed")
            # no yield — this is unreachable but makes it an async generator
            if False:
                yield None

        mock_model.generate_content_stream = _broken()

        mock_client = MagicMock()
        mock_client.aio.models = mock_model
        mock_client.aio.live.connect = AsyncMock()

        with patch("providers.gemini_provider.genai.Client", return_value=mock_client):
            config = ProviderConfig(api_key="test-key")
            p = GeminiProvider(config)

        msgs = [Message(role="user", content="Hi")]
        collected = []
        async for msg in p.stream_chat(msgs):
            collected.append(msg.content)

        assert any("Error" in c for c in collected)


# ── Live Audio Session ───────────────────────────────────────────────

class TestLiveSession:
    """create_live_session context manager."""

    @pytest.mark.asyncio
    async def test_create_live_session(self):
        from providers.gemini_provider import GeminiProvider

        mock_session = AsyncMock()
        mock_connect = AsyncMock()
        mock_connect.__aenter__ = AsyncMock(return_value=mock_session)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        mock_client = MagicMock()
        mock_client.aio.live.connect = MagicMock(return_value=mock_connect)
        mock_client.aio.models = MagicMock()

        with patch("providers.gemini_provider.genai.Client", return_value=mock_client):
            config = ProviderConfig(api_key="test-key")
            p = GeminiProvider(config)

        async with p.create_live_session({}) as session:
            assert session is mock_session


# ── get_models ────────────────────────────────────────────────────────

class TestGetModels:
    """get_models static list."""

    def test_contains_expected_models(self, provider):
        models = provider.get_models()
        ids = [m["id"] for m in models]
        assert "gemini-2.5-flash" in ids
        assert "gemini-2.5-pro" in ids
        assert len(models) >= 4
