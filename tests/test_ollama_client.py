"""Tests for KathaYantra Local Ollama Client and Diagnostics."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from app.schemas.ai import AIOllamaHealthResponse
from app.services.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaResponseError,
    OllamaTimeoutError,
)


@pytest.mark.asyncio
async def test_ollama_client_model_tag_matching():
    """Verify flexible matching between configured tags and installed library tags."""
    client = OllamaClient(default_model="gemma2")

    assert client._model_tag_matches("gemma2", ["gemma2:latest", "llama3:latest"]) is True
    assert client._model_tag_matches("gemma2", ["gemma2:9b", "mistral:latest"]) is True
    assert client._model_tag_matches("gemma2:9b", ["gemma2:9b"]) is True
    assert client._model_tag_matches("gemma2:latest", ["gemma2:latest"]) is True
    assert client._model_tag_matches("phi3", ["gemma2:latest", "llama3:latest"]) is False


@pytest.mark.asyncio
async def test_ollama_client_health_available():
    """Verify health returns 'available' when Ollama responds and model is present."""
    client = OllamaClient(base_url="http://test-ollama:11434", default_model="gemma2")

    mock_resp = httpx.Response(
        status_code=200,
        json={"models": [{"name": "gemma2:latest"}]},
        request=httpx.Request("GET", "http://test-ollama:11434/api/tags"),
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        health = await client.check_health()

        assert isinstance(health, AIOllamaHealthResponse)
        assert health.status == "available"
        assert health.model_available is True
        assert "gemma2:latest" in health.installed_models


@pytest.mark.asyncio
async def test_ollama_client_health_model_missing():
    """Verify health returns 'model_missing' when Ollama is running but target tag is absent."""
    client = OllamaClient(base_url="http://test-ollama:11434", default_model="gemma2")

    mock_resp = httpx.Response(
        status_code=200,
        json={"models": [{"name": "llama3:latest"}, {"name": "mistral:7b"}]},
        request=httpx.Request("GET", "http://test-ollama:11434/api/tags"),
    )

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        health = await client.check_health()

        assert health.status == "model_missing"
        assert health.model_available is False
        assert "ollama pull gemma2" in health.message


@pytest.mark.asyncio
async def test_ollama_client_health_unavailable():
    """Verify health returns 'unavailable' when connection is refused without crashing."""
    client = OllamaClient(base_url="http://nonexistent-host:11434", default_model="gemma2")

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectError("Connection refused")
        health = await client.check_health()

        assert health.status == "unavailable"
        assert health.model_available is False
        assert "unreachable" in health.message.lower()


@pytest.mark.asyncio
async def test_ollama_client_chat_success():
    """Verify chat completion sends correct payload and parses response."""
    client = OllamaClient(base_url="http://test-ollama:11434", default_model="gemma2", max_retries=1)

    mock_resp = httpx.Response(
        status_code=200,
        json={"message": {"role": "assistant", "content": "The Banshee is an Irish ancestral spirit."}},
        request=httpx.Request("POST", "http://test-ollama:11434/api/chat"),
    )

    with patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        result = await client.chat([{"role": "user", "content": "Tell me about the Banshee"}])

        assert result == "The Banshee is an Irish ancestral spirit."
        payload = mock_post.call_args[1]["json"]
        assert payload["model"] == "gemma2"
        assert payload["stream"] is False


@pytest.mark.asyncio
async def test_ollama_client_chat_timeout():
    """Verify chat raises OllamaTimeoutError when request times out."""
    client = OllamaClient(base_url="http://test-ollama:11434", default_model="gemma2", max_retries=0)

    with patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ReadTimeout("Read timed out")
        with pytest.raises(OllamaTimeoutError):
            await client.chat([{"role": "user", "content": "Test timeout"}])


@pytest.mark.asyncio
async def test_ollama_client_chat_model_not_found_404():
    """Verify 404 response raises OllamaModelNotFoundError."""
    client = OllamaClient(base_url="http://test-ollama:11434", default_model="gemma2", max_retries=0)

    mock_resp = httpx.Response(
        status_code=404,
        text="model 'gemma2' not found",
        request=httpx.Request("POST", "http://test-ollama:11434/api/chat"),
    )

    with patch.object(httpx.AsyncClient, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with pytest.raises(OllamaModelNotFoundError):
            await client.chat([{"role": "user", "content": "Test 404"}])

