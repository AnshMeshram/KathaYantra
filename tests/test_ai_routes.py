"""Tests for KathaYantra AI API Endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.services.ollama_client import ollama_client


@pytest.mark.asyncio
async def test_get_ollama_health_endpoint():
    """Verify GET /api/v1/health/ollama returns 200 with diagnostic payload."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/health/ollama")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "provider" in data
        assert data["provider"] == "ollama"
        assert "configured_model" in data
        assert "message" in data


@pytest.mark.asyncio
async def test_post_ai_ask_endpoint():
    """Verify POST /api/v1/ai/ask executes grounded retrieval and returns 200."""
    with patch.object(ollama_client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "The Banshee is an Irish ancestral spirit whose wailing warns of approaching demise."

        payload = {
            "question": "What is the cultural role of the Banshee in Ireland?",
            "country_code": "IE",
            "category": "folklore",
            "max_records": 3,
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/v1/ai/ask", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data["answer_type"] == "grounded_answer"
            assert "Banshee" in data["answer"]
            assert len(data["supporting_story_ids"]) >= 1
            assert len(data["sources"]) >= 1


@pytest.mark.asyncio
async def test_post_ai_ask_validation_error():
    """Verify input validation catches short questions and invalid country codes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Question too short
        resp = await ac.post("/api/v1/ai/ask", json={"question": "hi"})
        assert resp.status_code == 422

        # Invalid country code
        resp = await ac.post("/api/v1/ai/ask", json={"question": "Valid folklore query", "country_code": "ZZ"})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_post_ai_compare_endpoint():
    """Verify POST /api/v1/ai/compare compares documented stories and returns 200."""
    with patch.object(ollama_client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = (
            "Summary: Comparative analysis between banshee and weeping woman.\n"
            "Similarities:\n"
            "- Nocturnal auditory spectral encounters.\n"
            "Differences:\n"
            "- Distinct regional roots in Ireland and Mexico."
        )

        payload = {
            "story_ids": ["IE-FOLK-006", "MX-URBAN-001"],
            "aspect_notes": "Compare vocal manifestations",
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/v1/ai/compare", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert len(data["compared_story_ids"]) == 2
            assert len(data["similarities"]) >= 1
            assert len(data["differences"]) >= 1
            assert len(data["sources"]) >= 2


@pytest.mark.asyncio
async def test_post_ai_generate_story_endpoint():
    """Verify POST /api/v1/ai/generate-story generates fiction and returns 201."""
    with patch.object(ollama_client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = (
            "# Shadows Over Point Pleasant\n"
            "The fog clung to the rusting girders of the abandoned bridge as the red eyes glowed."
        )

        payload = {
            "inspiration_story_ids": ["US-URBAN-001"],
            "setting": "Point Pleasant wetlands",
            "atmosphere": "quiet dread",
            "narrative_style": "found audio transcript",
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/v1/ai/generate-story", json=payload)
            assert resp.status_code == 201
            data = resp.json()
            rec = data["fiction_record"]
            assert rec["id"].startswith("AI-FIC-")
            assert rec["content_type"] == "ai_generated_fiction"
            assert "AI-generated work of creative fiction" in rec["fiction_disclaimer"]
            assert "US-URBAN-001" in rec["inspiration_story_ids"]
