"""Fiction Generation Service for KathaYantra with Architectural Isolation.

Generates original creative fiction inspired by authentic folklore and urban legend records,
enforcing strict segregation, explicit disclaimer tagging, and isolated storage.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import re
from typing import Optional

from app.core.config import settings
from app.schemas.ai import AIFictionRequest, AIFictionResponse
from app.schemas.generated_fiction import GeneratedFictionRecord
from app.schemas.story import VerificationStatusEnum
from app.services.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaError,
    ollama_client,
)
from app.services.retrieval import RetrievalResultItem, RetrievalService, retrieval_service

logger = logging.getLogger(__name__)

PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "story_generation_system_v1.txt"


class FictionGenerationService:
    """Orchestrates creative narrative generation with strict segregation from authentic records."""

    def __init__(
        self,
        retriever: Optional[RetrievalService] = None,
        llm_client: Optional[OllamaClient] = None,
        output_dir: Optional[Path] = None,
        prompt_path: Optional[Path] = None,
    ):
        self.retriever = retriever or retrieval_service
        self.llm_client = llm_client or ollama_client
        self.output_dir = output_dir or settings.generated_fiction_dir
        self.prompt_path = prompt_path or PROMPT_FILE
        self._prompt_cache: Optional[str] = None

    def _get_system_prompt(self) -> str:
        """Load and cache the creative fiction system prompt."""
        if self._prompt_cache is None:
            if self.prompt_path.exists():
                self._prompt_cache = self.prompt_path.read_text(encoding="utf-8").strip()
            else:
                self._prompt_cache = (
                    "You are the KathaYantra Creative Storyteller. Craft original fictional narratives "
                    "inspired by traditional folklore motifs without copying text verbatim or claiming historical authenticity."
                )
        return self._prompt_cache

    def _get_next_fiction_id(self) -> str:
        """Generate the next sequential AI-FIC identifier (format: AI-FIC-001, AI-FIC-002, etc.)."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        existing_files = list(self.output_dir.glob("AI-FIC-*.json"))
        highest_idx = 0

        for f in existing_files:
            match = re.search(r"AI-FIC-(\d+)", f.stem)
            if match:
                idx = int(match.group(1))
                if idx > highest_idx:
                    highest_idx = idx

        next_idx = highest_idx + 1
        return f"AI-FIC-{next_idx:03d}"

    async def generate_fiction(self, request: AIFictionRequest) -> AIFictionResponse:
        """Generate an original fictional narrative inspired by specified authentic stories."""
        if not settings.AI_ENABLE_STORY_GENERATION:
            raise ValueError("Story generation is currently disabled in application settings.")

        story_ids = [sid.strip().upper() for sid in request.inspiration_story_ids]
        records = self.retriever.get_multiple_by_ids(story_ids)

        if not records:
            raise ValueError(
                f"None of the requested inspiration story IDs ({', '.join(story_ids)}) "
                "were found in the verified KathaYantra archive."
            )

        # Assemble inspiration context
        context_parts = ["[INSPIRATION RECORDS]"]
        for idx, rec in enumerate(records, start=1):
            context_parts.append(
                f"\n--- INSPIRATION RECORD {idx}: {rec.id} ({rec.title}) ---\n"
                f"Country of Origin: {rec.country_code} ({rec.cultural_community or 'Traditional'})\n"
                f"Category: {rec.category.value}\n"
                f"Summary Synopsis: {rec.summary}\n"
                f"Traditional Motifs: {', '.join(rec.motifs)}\n"
            )
        context_parts.append("\n[END OF INSPIRATION RECORDS]\n")
        context_str = "\n".join(context_parts)

        setting_str = request.setting or "fog-draped coastal town"
        atmosphere_str = request.atmosphere or "quiet dread"
        style_str = request.narrative_style or "found research document"
        creative_notes = f"\nCreative Direction: {request.creative_prompt}" if request.creative_prompt else ""

        user_content = (
            f"{context_str}\n"
            f"Requested Setting: {setting_str}\n"
            f"Atmosphere / Tone: {atmosphere_str}\n"
            f"Narrative Format: {style_str}{creative_notes}\n\n"
            f"Please write an original fictional short story that honors the atmosphere and motifs "
            f"of these inspiration records. Author fresh prose and memorable characters."
        )

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_content},
        ]

        try:
            story_body = await self.llm_client.chat(
                messages=messages,
                temperature=settings.AI_FICTION_TEMPERATURE,
                max_tokens=settings.AI_MAX_OUTPUT_TOKENS,
            )
        except OllamaConnectionError as e:
            raise OllamaConnectionError(
                f"Cannot generate fictional story: local Ollama server is offline at {self.llm_client.base_url}."
            ) from e

        # Extract or synthesize title
        title = f"Echoes of {records[0].title}: A Fictional Tale"
        first_line = story_body.splitlines()[0].strip() if story_body else ""
        if first_line.startswith("#"):
            title = first_line.lstrip("#").strip()
            # Strip title from body
            story_body = "\n".join(story_body.splitlines()[1:]).strip()

        fiction_id = self._get_next_fiction_id()
        inspiration_source_ids = [
            s.url for rec in records for s in rec.sources if s.url
        ]

        # Construct strictly segregated GeneratedFictionRecord
        fiction_record = GeneratedFictionRecord(
            id=fiction_id,
            title=title,
            story_text=story_body,
            inspiration_story_ids=[r.story_id for r in records],
            inspiration_source_ids=inspiration_source_ids,
            model_provider="ollama",
            model_tag=self.llm_client.default_model,
            prompt_template_version="1.0.0",
            verification_status=VerificationStatusEnum.NEEDS_REVIEW,
        )

        # Persist ONLY to data/processed/generated_fiction/
        out_file = self.output_dir / f"{fiction_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(fiction_record.model_dump_json(indent=2))

        logger.info(f"Persisted generated fiction {fiction_id} to {out_file}")

        return AIFictionResponse(
            fiction_record=fiction_record,
            saved_path=str(out_file),
            model_tag=self.llm_client.default_model,
            prompt_version="story_generation_v1",
            generated_at=datetime.now(timezone.utc).isoformat(),
        )


# Central singleton instance
fiction_service = FictionGenerationService()

