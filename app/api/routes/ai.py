"""AI Archivist and Generation API Endpoints for KathaYantra.

Provides endpoints for grounded question answering, evidence-based comparative analysis,
creative fiction generation with strict segregation, and Ollama model diagnostics.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status

from app.schemas.ai import (
    AIComparisonRequest,
    AIComparisonResponse,
    AIFictionRequest,
    AIFictionResponse,
    AIOllamaHealthResponse,
    AIQuestionRequest,
    AIQuestionResponse,
)
from app.services.fiction_service import fiction_service
from app.services.ollama_client import ollama_client
from app.services.question_answering import question_answering_service
from app.services.story_comparison import story_comparison_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["Local AI Archivist"])


@router.get(
    "/health",
    response_model=AIOllamaHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check Local Ollama Model Availability",
)
@router.get(
    "/health/ollama",
    response_model=AIOllamaHealthResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_ollama_health() -> AIOllamaHealthResponse:
    """Inspect the local Ollama instance and report whether the configured Gemma 2 model is ready."""
    return await ollama_client.check_health()


@router.post(
    "/ask",
    response_model=AIQuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the Grounded Local AI Archivist",
)
async def ask_archivist(request: AIQuestionRequest) -> AIQuestionResponse:
    """Retrieve verified folklore records and answer an inquiry grounded strictly in archival evidence.

    If no sufficiently relevant records are found, returns an INSUFFICIENT_EVIDENCE response
    rather than hallucinating an answer.
    """
    try:
        return await question_answering_service.answer_question(request)
    except Exception as e:
        logger.error(f"Error in /ai/ask: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Archival inquiry failed: {str(e)}",
        )


@router.post(
    "/compare",
    response_model=AIComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Documented Stories Using Archival Evidence",
)
async def compare_stories(request: AIComparisonRequest) -> AIComparisonResponse:
    """Compare 2 to 5 verified story records, analyzing shared motifs, distinct cultural roots,

    and regional differences without claiming unsupported historical lineage.
    """
    try:
        return await story_comparison_service.compare_stories(request)
    except Exception as e:
        logger.error(f"Error in /ai/compare: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Story comparison failed: {str(e)}",
        )


@router.post(
    "/generate-story",
    response_model=AIFictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Isolated Creative Fiction Inspired by Folklore",
)
async def generate_fiction_story(request: AIFictionRequest) -> AIFictionResponse:
    """Generate an original fictional narrative inspired by authentic folklore motifs.

    The resulting story is segregated to `GeneratedFictionRecord`, tagged with a mandatory
    disclaimer, and stored exclusively in `data/processed/generated_fiction/`.
    It can NEVER enter canonical folklore datasets.
    """
    try:
        return await fiction_service.generate_fiction(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error in /ai/generate-story: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fiction generation failed: {str(e)}",
        )

