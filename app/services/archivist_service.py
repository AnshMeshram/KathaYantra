"""Archivist Service Facade for KathaYantra.

Exposes the central AI archivist functionality, linking question answering,
source citations, and evidence grounding.
"""

from app.schemas.ai import (
    AIAnswerType,
    AIQuestionRequest,
    AIQuestionResponse,
    AISourceCitation,
)
from app.services.question_answering import QuestionAnsweringService, question_answering_service

# Re-export singleton and class for modular use
ArchivistService = QuestionAnsweringService
archivist_service = question_answering_service

__all__ = [
    "ArchivistService",
    "archivist_service",
    "AIAnswerType",
    "AIQuestionRequest",
    "AIQuestionResponse",
    "AISourceCitation",
]

