"""Tests for Fiction Generation Service and Architectural Segregation."""

from pathlib import Path
import pytest
from unittest.mock import AsyncMock, patch

from app.schemas.ai import AIFictionRequest, AIFictionResponse
from app.schemas.generated_fiction import GeneratedFictionRecord
from app.schemas.story import ContentOriginEnum, StoryRecord, VerificationStatusEnum
from app.services.fiction_service import FictionGenerationService
from app.services.ollama_client import OllamaClient
from app.services.publication_policy import PublicationPolicy
from app.services.retrieval import retrieval_service


@pytest.mark.asyncio
async def test_fiction_generation_creates_valid_record(tmp_path: Path):
    """Verify fiction generation creates a valid GeneratedFictionRecord with mandatory disclaimer."""
    mock_llm = OllamaClient(default_model="gemma2")

    fiction_text = (
        "# The Midnight Station\n"
        "The train ground to a halt on the abandoned Sinseol platform. "
        "Through the condensation on the carriage window, Inspector Park saw shadowy figures "
        "gliding across the cold platform tiles, leaving no footprints behind in the dust."
    )

    with patch.object(mock_llm, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = fiction_text

        fiction_svc = FictionGenerationService(
            retriever=retrieval_service,
            llm_client=mock_llm,
            output_dir=tmp_path / "fiction_output",
        )

        req = AIFictionRequest(
            inspiration_story_ids=["KR-URBAN-007"],
            setting="subterranean metro tunnel",
            atmosphere="claustrophobic dread",
            narrative_style="investigative report",
        )

        resp = await fiction_svc.generate_fiction(req)

        assert isinstance(resp, AIFictionResponse)
        rec = resp.fiction_record
        assert isinstance(rec, GeneratedFictionRecord)
        assert rec.id.startswith("AI-FIC-")
        assert rec.content_type == "ai_generated_fiction"
        assert len(rec.story_text) >= 20
        assert len(rec.fiction_disclaimer) >= 20
        assert "AI-generated work of creative fiction" in rec.fiction_disclaimer
        assert "KR-URBAN-007" in rec.inspiration_story_ids
        assert Path(resp.saved_path).exists()


@pytest.mark.asyncio
async def test_fiction_record_fails_publication_policy():
    """Verify that synthetic fiction is strictly blocked from the authentic folklore archive."""
    # Attempt to evaluate a fictional record as a StoryRecord under PublicationPolicy
    fake_story = StoryRecord.model_construct(
        id="AI-FIC-001",
        country_code="US",
        category="folklore",
        title="Fabricated AI Legend",
        summary="A synthetic story created by an AI model simulating traditional folklore.",
        sources=[],
        verification_status=VerificationStatusEnum.VERIFIED,
        content_origin=ContentOriginEnum.AI_GENERATED_FICTION,
    )

    eval_result = PublicationPolicy.evaluate_eligibility(fake_story)
    assert eval_result.is_eligible is False
    assert any("AI-generated synthetic fiction" in v for v in eval_result.violations)


@pytest.mark.asyncio
async def test_fiction_generation_invalid_inspiration_id(tmp_path: Path):
    """Verify requesting fiction with non-existent story IDs raises a clean ValueError."""
    mock_llm = OllamaClient(default_model="gemma2")

    fiction_svc = FictionGenerationService(
        retriever=retrieval_service,
        llm_client=mock_llm,
        output_dir=tmp_path / "fiction_output",
    )

    req = AIFictionRequest(inspiration_story_ids=["NONEXISTENT-999"])

    with pytest.raises(ValueError) as excinfo:
        await fiction_svc.generate_fiction(req)

    assert "were found in the verified KathaYantra archive" in str(excinfo.value)

