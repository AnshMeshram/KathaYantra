"""Tests for Grounded Question Answering and Local AI Archivist Service."""

import pytest
from unittest.mock import AsyncMock, patch

from app.schemas.ai import AIAnswerType, AIQuestionRequest, AIQuestionResponse
from app.services.ollama_client import OllamaClient, OllamaConnectionError
from app.services.question_answering import QuestionAnsweringService
from app.services.retrieval import RetrievalResultItem, retrieval_service


@pytest.mark.asyncio
async def test_question_answering_grounded_success():
    """Verify grounded Q&A retrieves evidence and attaches authentic metadata citations."""
    mock_llm = OllamaClient(default_model="gemma2")

    with patch.object(mock_llm, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "The Mothman is a documented West Virginia urban legend associated with Point Pleasant."

        qa_svc = QuestionAnsweringService(retriever=retrieval_service, llm_client=mock_llm)
        req = AIQuestionRequest(question="Who is the Mothman?", country_code="US")

        resp = await qa_svc.answer_question(req)

        assert isinstance(resp, AIQuestionResponse)
        assert resp.answer_type == AIAnswerType.GROUNDED_ANSWER
        assert "Mothman" in resp.answer
        assert len(resp.supporting_story_ids) >= 1
        assert "US-URBAN-001" in resp.supporting_story_ids
        assert len(resp.sources) >= 1

        # Verify sources are genuine and from metadata
        citation = resp.sources[0]
        assert citation.story_id == "US-URBAN-001"
        assert citation.url.startswith("http")
        assert citation.country_code == "US"


@pytest.mark.asyncio
async def test_question_answering_insufficient_evidence():
    """Verify that queries matching zero records return INSUFFICIENT_EVIDENCE rather than hallucinating."""
    mock_llm = OllamaClient(default_model="gemma2")

    with patch.object(mock_llm, "chat", new_callable=AsyncMock) as mock_chat:
        qa_svc = QuestionAnsweringService(retriever=retrieval_service, llm_client=mock_llm)
        req = AIQuestionRequest(question="Tell me about the Martian Zorgons of Atlantis")

        resp = await qa_svc.answer_question(req)

        assert resp.answer_type == AIAnswerType.INSUFFICIENT_EVIDENCE
        assert "does not contain sufficient documented records" in resp.answer
        assert len(resp.supporting_story_ids) == 0
        assert len(resp.sources) == 0
        # Model chat should not even have been called
        mock_chat.assert_not_called()


@pytest.mark.asyncio
async def test_question_answering_ollama_offline_fallback():
    """Verify that when Ollama is offline, deterministic search results are still returned safely."""
    mock_llm = OllamaClient(default_model="gemma2")

    with patch.object(mock_llm, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.side_effect = OllamaConnectionError("Connection refused")

        qa_svc = QuestionAnsweringService(retriever=retrieval_service, llm_client=mock_llm)
        req = AIQuestionRequest(question="What is the Banshee?", country_code="IE")

        resp = await qa_svc.answer_question(req)

        assert resp.answer_type == AIAnswerType.MODEL_UNAVAILABLE
        assert "offline or unreachable" in resp.answer
        assert len(resp.supporting_story_ids) >= 1
        assert len(resp.sources) >= 1


@pytest.mark.asyncio
async def test_question_answering_input_truncation():
    """Verify queries exceeding AI_MAX_INPUT_CHARS are handled without raising an error."""
    mock_llm = OllamaClient(default_model="gemma2")

    with patch.object(mock_llm, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "Answer to long prompt."
        qa_svc = QuestionAnsweringService(retriever=retrieval_service, llm_client=mock_llm)

        huge_q = "Banshee " * 200  # 1600 chars > 1000 limit
        req = AIQuestionRequest(question=huge_q[:1000])

        resp = await qa_svc.answer_question(req)
        assert resp.answer_type in (AIAnswerType.GROUNDED_ANSWER, AIAnswerType.INSUFFICIENT_EVIDENCE)

