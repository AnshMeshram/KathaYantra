"""Grounded Question Answering Service for the KathaYantra AI Archivist.

Orchestrates lexical retrieval, context assembly, prompt construction, Ollama inference,
and trusted bibliographic citation attachment.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.schemas.ai import (
    AIAnswerType,
    AIQuestionRequest,
    AIQuestionResponse,
    AISourceCitation,
)
from app.schemas.story import CategoryEnum
from app.services.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
    ollama_client,
)
from app.services.retrieval import RetrievalResultItem, RetrievalService, retrieval_service

logger = logging.getLogger(__name__)

PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "archivist_system_v1.txt"


class QuestionAnsweringService:
    """Answers user inquiries regarding folklore and urban legends grounded strictly in retrieved records."""

    def __init__(
        self,
        retriever: Optional[RetrievalService] = None,
        llm_client: Optional[OllamaClient] = None,
        system_prompt_path: Optional[Path] = None,
    ):
        self.retriever = retriever or retrieval_service
        self.llm_client = llm_client or ollama_client
        self.system_prompt_path = system_prompt_path or PROMPT_FILE
        self._system_prompt_cache: Optional[str] = None

    def _get_system_prompt(self) -> str:
        """Load and cache the versioned archivist system prompt."""
        if self._system_prompt_cache is None:
            if self.system_prompt_path.exists():
                self._system_prompt_cache = self.system_prompt_path.read_text(encoding="utf-8").strip()
            else:
                self._system_prompt_cache = (
                    "You are the KathaYantra Local AI Archivist. Answer questions strictly based "
                    "on the supplied retrieved records. Never invent citations or facts."
                )
        return self._system_prompt_cache

    def _build_context(self, records: list[RetrievalResultItem]) -> tuple[str, int]:
        """Format retrieved story records into delimited internal context for the model."""
        context_parts = ["[RETRIEVED ARCHIVE RECORDS]"]
        total_chars = 0

        for idx, rec in enumerate(records, start=1):
            source_labels = [s.publisher or s.title or s.url for s in rec.sources]
            sources_str = "; ".join(source_labels) if source_labels else "Unspecified verified source"

            block = (
                f"\n--- RECORD {idx} ---\n"
                f"Story ID: {rec.story_id}\n"
                f"Title: {rec.title}\n"
                f"Country: {rec.country_code}\n"
                f"Category: {rec.category.value}\n"
                f"Cultural/Regional Attribution: {rec.cultural_community or rec.region or 'General'}\n"
                f"Summary: {rec.summary}\n"
                f"Sources: {sources_str}\n"
                f"Attribution Statement: {rec.attribution_text or 'None'}\n"
            )

            if total_chars + len(block) > settings.AI_MAX_CONTEXT_CHARS:
                # Truncate further records if context exceeds safety boundaries
                break

            context_parts.append(block)
            total_chars += len(block)

        context_parts.append("\n[END OF RETRIEVED ARCHIVE RECORDS]\n")
        return "\n".join(context_parts), total_chars

    def _extract_source_citations(self, records: list[RetrievalResultItem]) -> list[AISourceCitation]:
        """Construct trusted bibliographic citations directly from retrieved record metadata."""
        citations: list[AISourceCitation] = []
        seen_urls: set[str] = set()

        for rec in records:
            for s in rec.sources:
                if s.url in seen_urls:
                    continue
                seen_urls.add(s.url)
                citations.append(
                    AISourceCitation(
                        story_id=rec.story_id,
                        story_title=rec.title,
                        country_code=rec.country_code,
                        category=rec.category.value,
                        publisher=s.publisher or s.name or "Holding Archive",
                        url=s.url,
                        citation=s.citation,
                        attribution_text=s.attribution_text or rec.attribution_text,
                        license_name=s.license_name,
                    )
                )
        return citations

    async def answer_question(self, request: AIQuestionRequest) -> AIQuestionResponse:
        """Process a user query, retrieve eligible evidence, invoke local model, and return grounded answer."""
        start_time = datetime.now(timezone.utc)
        query = request.question.strip()

        # Input length safety check
        if len(query) > settings.AI_MAX_INPUT_CHARS:
            query = query[: settings.AI_MAX_INPUT_CHARS]

        # 1. Retrieve candidates from local lexical index
        records = self.retriever.search(
            query=query,
            country_code=request.country_code,
            category=request.category,
            limit=request.max_records,
            min_score=settings.AI_RETRIEVAL_MIN_SCORE,
        )

        citations = self._extract_source_citations(records)
        supporting_ids = [r.story_id for r in records]

        # 2. Check if retrieval found sufficient evidence
        if not records:
            return AIQuestionResponse(
                question=request.question,
                answer=(
                    "The local archive does not contain sufficient documented records to answer this question. "
                    "Please refine your inquiry using specific folklore figures, creatures, or country names "
                    "(e.g., Baital Pachisi, Mothman, Saci-Pererê, Banshee)."
                ),
                answer_type=AIAnswerType.INSUFFICIENT_EVIDENCE,
                supporting_story_ids=[],
                sources=[],
                retrieval_status="no_matches_found",
                limitations="Query yielded zero matching records meeting the relevance threshold.",
                model_tag=self.llm_client.default_model,
                prompt_version="archivist_v1",
                generated_at=datetime.now(timezone.utc).isoformat(),
            )

        # 3. Assemble prompt context
        system_prompt = self._get_system_prompt()
        context_str, char_count = self._build_context(records)

        user_content = (
            f"{context_str}\n"
            f"User Question: {query}\n\n"
            f"Please provide an informative, culturally accurate, and evidence-grounded response "
            f"based strictly on the records provided above."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # 4. Invoke local Ollama instance
        try:
            raw_answer = await self.llm_client.chat(
                messages=messages,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_OUTPUT_TOKENS,
            )

            return AIQuestionResponse(
                question=request.question,
                answer=raw_answer,
                answer_type=AIAnswerType.GROUNDED_ANSWER,
                supporting_story_ids=supporting_ids,
                sources=citations,
                retrieval_status="grounded_in_evidence",
                limitations=None,
                model_tag=self.llm_client.default_model,
                prompt_version="archivist_v1",
                generated_at=datetime.now(timezone.utc).isoformat(),
            )

        except OllamaConnectionError as e:
            logger.warning(f"Ollama connection unavailable: {e}")
            fallback_answer = (
                f"The local Ollama server is currently offline or unreachable at {self.llm_client.base_url}. "
                f"However, the following {len(records)} relevant story records were successfully retrieved "
                f"from KathaYantra's verified local index: "
                + ", ".join([f"{r.title} ({r.story_id})" for r in records])
                + "."
            )
            return AIQuestionResponse(
                question=request.question,
                answer=fallback_answer,
                answer_type=AIAnswerType.MODEL_UNAVAILABLE,
                supporting_story_ids=supporting_ids,
                sources=citations,
                retrieval_status="retrieval_successful_inference_offline",
                limitations="Local Ollama daemon is offline; returned deterministic search results.",
                model_tag=self.llm_client.default_model,
                prompt_version="archivist_v1",
                generated_at=datetime.now(timezone.utc).isoformat(),
            )

        except (OllamaModelNotFoundError, OllamaTimeoutError, OllamaError) as e:
            logger.error(f"Ollama inference error: {e}")
            return AIQuestionResponse(
                question=request.question,
                answer=f"An error occurred while generating the archival response: {str(e)}",
                answer_type=AIAnswerType.ERROR,
                supporting_story_ids=supporting_ids,
                sources=citations,
                retrieval_status="inference_error",
                limitations=str(e),
                model_tag=self.llm_client.default_model,
                prompt_version="archivist_v1",
                generated_at=datetime.now(timezone.utc).isoformat(),
            )


# Central singleton instance
question_answering_service = QuestionAnsweringService()

