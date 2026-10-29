"""Tests for KathaYantra Story Comparison Service."""

import pytest
from unittest.mock import AsyncMock, patch

from app.schemas.ai import AIComparisonRequest, AIComparisonResponse
from app.services.ollama_client import OllamaClient, OllamaConnectionError
from app.services.retrieval import retrieval_service
from app.services.story_comparison import StoryComparisonService


@pytest.mark.asyncio
async def test_story_comparison_success():
    """Verify comparison returns structured breakdown with authentic citations."""
    mock_llm = OllamaClient(default_model="gemma2")

    mock_comparison_text = (
        "Summary: Both narratives feature spectral women heralding tragedy.\n"
        "Similarities:\n"
        "- Both figures are auditory spirits warning of mortal calamity.\n"
        "- Both are anchored in water or nocturnal environments.\n"
        "Differences:\n"
        "- La Llorona is tied to maternal grief in Mexico, while the Banshee is tied to Gaelic ancestry.\n"
        "- The Banshee foretells death, whereas La Llorona actively abducts or frightens wanderers.\n"
        "Cultural Context:\n"
        "- Mexican syncretic colonial lore vs. pre-Christian Celtic oral traditions.\n"
        "Uncertain Details:\n"
        "- The earliest written record of La Llorona varies by regional chronicler."
    )

    with patch.object(mock_llm, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_comparison_text

        cmp_svc = StoryComparisonService(retriever=retrieval_service, llm_client=mock_llm)
        req = AIComparisonRequest(story_ids=["IE-FOLK-006", "MX-URBAN-001"])

        resp = await cmp_svc.compare_stories(req)

        assert isinstance(resp, AIComparisonResponse)
        assert len(resp.compared_story_ids) == 2
        assert "IE-FOLK-006" in resp.compared_story_ids
        assert "MX-URBAN-001" in resp.compared_story_ids
        assert len(resp.similarities) >= 1
        assert len(resp.differences) >= 1
        assert len(resp.sources) >= 2


@pytest.mark.asyncio
async def test_story_comparison_missing_id():
    """Verify comparison notes unrecognized IDs in uncertain_details."""
    mock_llm = OllamaClient(default_model="gemma2")

    with patch.object(mock_llm, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "Summary: Partial comparison.\nDifferences:\n- Distinct lore."

        cmp_svc = StoryComparisonService(retriever=retrieval_service, llm_client=mock_llm)
        req = AIComparisonRequest(story_ids=["US-URBAN-001", "NONEXISTENT-999"])

        resp = await cmp_svc.compare_stories(req)

        assert "US-URBAN-001" in resp.compared_story_ids
        assert any("NONEXISTENT-999" in u for u in resp.uncertain_details)


@pytest.mark.asyncio
async def test_story_comparison_offline_fallback():
    """Verify offline Ollama returns deterministic summary without throwing."""
    mock_llm = OllamaClient(default_model="gemma2")

    with patch.object(mock_llm, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.side_effect = OllamaConnectionError("Offline")

        cmp_svc = StoryComparisonService(retriever=retrieval_service, llm_client=mock_llm)
        req = AIComparisonRequest(story_ids=["IN-FOLK-001", "JP-FOLK-001"])

        resp = await cmp_svc.compare_stories(req)

        assert "Deterministic comparison" in resp.summary
        assert len(resp.compared_story_ids) == 2
        assert len(resp.sources) >= 2

