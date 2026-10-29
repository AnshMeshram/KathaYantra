"""Summary Builder and Narrative Curation Service for KathaYantra.

Ensures all published narrative summaries are original, culturally accurate,
structurally complete, and free from synthetic hallucinations or verbatim copyright infringement.
"""

import re
from typing import Optional
from pydantic import BaseModel, Field


class StructuredSummary(BaseModel):
    """Structured breakdown of an authentic folklore or urban legend narrative."""

    title: str
    key_figures: list[str] = Field(default_factory=list, description="Protagonists, spirits, creatures, or historical figures")
    setting: Optional[str] = Field(default=None, description="Geographic, temporal, or cultural setting")
    narrative_arc: Optional[str] = Field(default=None, description="Core conflict, journey, encounter, or transformation")
    motif_notes: list[str] = Field(default_factory=list, description="Traditional motifs or symbolic elements")
    summary_text: str = Field(..., description="The unified original narrative summary text")
    word_count: int = Field(default=0, description="Word count of summary_text")
    character_count: int = Field(default=0, description="Character count of summary_text")
    is_valid: bool = Field(default=False, description="Whether summary meets all curatorial criteria")
    issues: list[str] = Field(default_factory=list, description="Validation issues or stylistic warnings")


class SummaryBuilder:
    """Validator and generator for original, ethically curated folklore summaries."""

    MIN_WORDS: int = 20
    RECOMMENDED_MIN_WORDS: int = 50
    RECOMMENDED_MAX_WORDS: int = 250
    MAX_WORDS: int = 600

    VERBATIM_COPY_PATTERNS = [
        r"^(once upon a time[,\s]+there lived\b)",
        r"(all rights reserved|copyright \d{4})",
        r"(reprinted with permission|transcribed verbatim)",
        r"(chapter \d+:|page \d+ of \d+)",
    ]

    BOILERPLATE_HALLUCINATION_PATTERNS = [
        r"\bas an ai\b",
        r"\bas a language model\b",
        r"\bi am unable to\b",
        r"\blorem ipsum\b",
        r"\btodo:\b",
        r"\binsert summary\b",
    ]

    def build_summary(
        self,
        title: str,
        summary_text: str,
        key_figures: Optional[list[str]] = None,
        setting: Optional[str] = None,
        narrative_arc: Optional[str] = None,
        motif_notes: Optional[list[str]] = None,
    ) -> StructuredSummary:
        """Construct and validate a StructuredSummary object."""
        clean_text = " ".join(summary_text.strip().split())
        words = clean_text.split() if clean_text else []
        word_count = len(words)
        char_count = len(clean_text)

        issues: list[str] = []

        # Length validation
        if word_count < self.MIN_WORDS:
            issues.append(f"Summary is too short ({word_count} words). Minimum required is {self.MIN_WORDS} words.")
        elif word_count > self.MAX_WORDS:
            issues.append(f"Summary exceeds maximum word count ({word_count} words > {self.MAX_WORDS}).")

        # Copying / verbatim markers
        for pat in self.VERBATIM_COPY_PATTERNS:
            if re.search(pat, clean_text, re.IGNORECASE):
                issues.append(f"Possible raw/copyrighted text detected matching pattern: {pat}")

        # AI boilerplate / hallucination markers
        for pat in self.BOILERPLATE_HALLUCINATION_PATTERNS:
            if re.search(pat, clean_text, re.IGNORECASE):
                issues.append(f"Synthetic placeholder or AI artifact detected matching: {pat}")

        is_valid = len(issues) == 0

        return StructuredSummary(
            title=title,
            key_figures=key_figures or [],
            setting=setting,
            narrative_arc=narrative_arc,
            motif_notes=motif_notes or [],
            summary_text=clean_text,
            word_count=word_count,
            character_count=char_count,
            is_valid=is_valid,
            issues=issues,
        )

    def validate_summary_text(self, text: str) -> tuple[bool, list[str]]:
        """Quick check of a summary text string."""
        summary = self.build_summary(title="Untitled", summary_text=text)
        return summary.is_valid, summary.issues

    def compose_original_summary(
        self,
        title: str,
        setting: str,
        key_figures: list[str],
        narrative_arc: str,
        cultural_significance: Optional[str] = None,
    ) -> str:
        """Compose a structured, original prose synopsis suitable for KathaYantra."""
        parts = []
        figures_str = ", ".join(key_figures) if key_figures else "unnamed figures"
        parts.append(f"Originating in {setting}, the narrative of {title} centres on {figures_str}.")
        parts.append(narrative_arc)
        if cultural_significance:
            parts.append(cultural_significance)
        return " ".join(parts)


summary_builder = SummaryBuilder()
