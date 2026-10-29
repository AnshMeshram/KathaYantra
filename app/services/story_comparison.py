"""Story Comparison Service for KathaYantra Folklore and Urban Legends.

Conducts evidence-grounded comparative analysis between two or more documented
stories, analyzing shared motifs, distinct cultural roots, and divergence points.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path
import re
from typing import Optional

from app.core.config import settings
from app.schemas.ai import (
    AIComparisonRequest,
    AIComparisonResponse,
    AISourceCitation,
)
from app.services.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaError,
    ollama_client,
)
from app.services.retrieval import RetrievalResultItem, RetrievalService, retrieval_service

logger = logging.getLogger(__name__)

PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "story_comparison_system_v1.txt"


class StoryComparisonService:
    """Compares multiple documented stories using verified record evidence."""

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
        """Load and cache the comparative system prompt."""
        if self._system_prompt_cache is None:
            if self.system_prompt_path.exists():
                self._system_prompt_cache = self.system_prompt_path.read_text(encoding="utf-8").strip()
            else:
                self._system_prompt_cache = (
                    "You are the KathaYantra Comparative Folklore Analyst. Compare the provided "
                    "stories strictly based on the records provided. Highlight similarities, differences, "
                    "and cultural context without asserting unproven historical connections."
                )
        return self._system_prompt_cache

    def _extract_citations(self, records: list[RetrievalResultItem]) -> list[AISourceCitation]:
        """Glean authentic source citations from compared records."""
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

    def _parse_comparison_sections(self, raw_text: str) -> tuple[str, list[str], list[str], list[str], list[str]]:
        """Parse structured comparative output into modular sections."""
        summary = ""
        similarities: list[str] = []
        differences: list[str] = []
        cultural_context: list[str] = []
        uncertain_details: list[str] = []

        current_section = "summary"
        lines = raw_text.splitlines()

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Only evaluate section header switches on non-bullet lines
            is_bullet = bool(re.match(r"^[-*•\d.]+\s+", line_stripped))
            lower_line = line_stripped.lower()

            if not is_bullet:
                if "similarit" in lower_line or "shared motif" in lower_line:
                    current_section = "similarities"
                    continue
                elif "differen" in lower_line or "divergence" in lower_line:
                    current_section = "differences"
                    continue
                elif "cultural" in lower_line or "context" in lower_line:
                    current_section = "cultural_context"
                    continue
                elif "uncertain" in lower_line or "gap" in lower_line or "limitation" in lower_line:
                    current_section = "uncertain_details"
                    continue

            cleaned_point = re.sub(r"^[-*•#\d.]+\s*", "", line_stripped)

            if current_section == "summary":
                summary = f"{summary} {line_stripped}".strip()
            elif current_section == "similarities":
                if cleaned_point:
                    similarities.append(cleaned_point)
            elif current_section == "differences":
                if cleaned_point:
                    differences.append(cleaned_point)
            elif current_section == "cultural_context":
                if cleaned_point:
                    cultural_context.append(cleaned_point)
            elif current_section == "uncertain_details":
                if cleaned_point:
                    uncertain_details.append(cleaned_point)

        if not summary:
            summary = raw_text[:300].strip() + "..."

        return summary, similarities, differences, cultural_context, uncertain_details

    async def compare_stories(self, request: AIComparisonRequest) -> AIComparisonResponse:
        """Retrieve target story records and perform grounded comparative analysis."""
        story_ids = [sid.strip().upper() for sid in request.story_ids]
        records = self.retriever.get_multiple_by_ids(story_ids)
        found_ids = {r.story_id for r in records}
        missing_ids = [sid for sid in story_ids if sid not in found_ids]

        citations = self._extract_citations(records)

        if not records:
            return AIComparisonResponse(
                summary=f"None of the requested story IDs ({', '.join(story_ids)}) exist in the approved archive.",
                compared_story_ids=[],
                similarities=[],
                differences=[],
                cultural_context=[],
                uncertain_details=[f"Unrecognized IDs: {', '.join(missing_ids)}"],
                sources=[],
                model_tag=self.llm_client.default_model,
                prompt_version="story_comparison_v1",
                generated_at=datetime.now(timezone.utc).isoformat(),
            )

        # Build context
        context_parts = ["[STORIES UNDER COMPARISON]"]
        for idx, rec in enumerate(records, start=1):
            context_parts.append(
                f"\n--- STORY {idx}: {rec.id} ({rec.title}) ---\n"
                f"Country: {rec.country_code} | Category: {rec.category.value}\n"
                f"Cultural/Regional Attribution: {rec.cultural_community or rec.region or 'General'}\n"
                f"Summary: {rec.summary}\n"
                f"Motifs & Themes: {', '.join(rec.motifs)}\n"
            )
        context_parts.append("\n[END OF STORIES UNDER COMPARISON]\n")
        context_str = "\n".join(context_parts)

        aspect_note = f"\nSpecific Comparison Focus: {request.aspect_notes}" if request.aspect_notes else ""
        missing_note = (
            f"\nNote: Story IDs {', '.join(missing_ids)} could not be located in the verified index."
            if missing_ids
            else ""
        )

        user_content = (
            f"{context_str}{aspect_note}{missing_note}\n\n"
            f"Please compare these narratives, highlighting documented similarities, "
            f"cultural differences, and regional contexts without claiming unsupported historical derivation."
        )

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_content},
        ]

        try:
            raw_output = await self.llm_client.chat(
                messages=messages,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_OUTPUT_TOKENS,
            )

            summary, sims, diffs, context_pts, uncert = self._parse_comparison_sections(raw_output)
            if missing_ids:
                uncert.append(f"Story IDs not found in verified dataset: {', '.join(missing_ids)}")

            return AIComparisonResponse(
                summary=summary,
                compared_story_ids=[r.story_id for r in records],
                similarities=sims,
                differences=diffs,
                cultural_context=context_pts,
                uncertain_details=uncert,
                sources=citations,
                model_tag=self.llm_client.default_model,
                prompt_version="story_comparison_v1",
                generated_at=datetime.now(timezone.utc).isoformat(),
            )

        except OllamaConnectionError:
            # Deterministic offline comparison fallback
            logger.warning("Ollama offline during story comparison. Returning deterministic fallback.")
            deterministic_sims = [
                f"Both stories share the general category of {records[0].category.value} storytelling."
            ]
            deterministic_diffs = [
                f"{r.title} belongs to {r.country_code} ({r.cultural_community or 'regional lore'})."
                for r in records
            ]
            return AIComparisonResponse(
                summary=(
                    f"Deterministic comparison between {len(records)} records: "
                    + ", ".join([f"{r.title} ({r.country_code})" for r in records])
                    + ". Local Ollama server is offline."
                ),
                compared_story_ids=[r.story_id for r in records],
                similarities=deterministic_sims,
                differences=deterministic_diffs,
                cultural_context=[f"Origins: {', '.join([r.country_code for r in records])}"],
                uncertain_details=["Ollama inference offline; qualitative thematic comparison unavailable."],
                sources=citations,
                model_tag=self.llm_client.default_model,
                prompt_version="story_comparison_v1",
                generated_at=datetime.now(timezone.utc).isoformat(),
            )


# Central singleton instance
story_comparison_service = StoryComparisonService()
