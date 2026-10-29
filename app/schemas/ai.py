"""Pydantic Schemas for KathaYantra AI Archivist, Retrieval, and Fiction Generation.

Defines strict input and response contracts for grounded Q&A, comparative analysis,
fiction generation, and Ollama diagnostics.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator

from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.generated_fiction import GeneratedFictionRecord
from app.schemas.story import CategoryEnum


class AIAnswerType(str, Enum):
    """Categorical classification of the AI response."""

    GROUNDED_ANSWER = "grounded_answer"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    OUT_OF_SCOPE = "out_of_scope"
    MODEL_UNAVAILABLE = "model_unavailable"
    ERROR = "error"


class AIOllamaHealthResponse(BaseModel):
    """Health and model availability diagnostic payload."""

    status: str = Field(..., description="'available', 'model_missing', 'unavailable', or 'misconfigured'")
    provider: str = Field(default="ollama", description="Local LLM runner provider")
    base_url: str = Field(..., description="Ollama endpoint URL")
    configured_model: str = Field(..., description="Target model tag specified in configuration")
    model_available: bool = Field(default=False, description="Whether configured model tag is available on host")
    installed_models: list[str] = Field(default_factory=list, description="All model tags found on host Ollama instance")
    message: str = Field(..., description="Explanatory operational status message")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AISourceCitation(BaseModel):
    """Bibliographic citation extracted from trusted retrieved story metadata."""

    story_id: str = Field(..., description="Canonical ID of the source story record")
    story_title: str = Field(..., description="Title of the source narrative")
    country_code: str = Field(..., description="Two-letter ISO country code")
    category: str = Field(..., description="'folklore' or 'urban_legend'")
    publisher: str = Field(default="", description="Publisher, archive, or scholarly holding body")
    url: str = Field(..., description="Authentic HTTP/HTTPS link to source material")
    citation: Optional[str] = Field(default=None, description="Formal academic/bibliographic citation string")
    attribution_text: Optional[str] = Field(default=None, description="Mandatory attribution statement")
    license_name: Optional[str] = Field(default=None, description="Documented reuse licence")


class AIQuestionRequest(BaseModel):
    """Incoming user inquiry for the grounded AI archivist."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The question regarding world folklore or urban legends",
    )
    country_code: Optional[str] = Field(
        default=None,
        description="Optional two-letter country code filter (e.g. IN, JP, IE)",
    )
    category: Optional[CategoryEnum] = Field(
        default=None,
        description="Optional filter by 'folklore' or 'urban_legend'",
    )
    max_records: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum supporting evidence records to retrieve",
    )

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        if v:
            code = v.upper()
            if code not in SUPPORTED_COUNTRY_CODES:
                raise ValueError(f"Country code '{v}' is not supported. Must be one of: {list(SUPPORTED_COUNTRY_CODES.keys())}")
            return code
        return v


class AIQuestionResponse(BaseModel):
    """Structured response from the grounded AI archivist."""

    question: str
    answer: str
    answer_type: AIAnswerType
    supporting_story_ids: list[str] = Field(default_factory=list)
    sources: list[AISourceCitation] = Field(default_factory=list)
    retrieval_status: str = Field(default="ok", description="'ok', 'no_matches', 'below_threshold', etc.")
    limitations: Optional[str] = None
    model_provider: str = "ollama"
    model_tag: str
    prompt_version: str = "archivist_v1"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AIComparisonRequest(BaseModel):
    """Request to compare two or more specific documented narratives."""

    story_ids: list[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="List of 2 to 5 canonical StoryRecord IDs to compare (e.g. ['JP-FOLK-001', 'KR-FOLK-001'])",
    )
    aspect_notes: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional specific comparison focus (e.g. 'Compare creature vulnerabilities')",
    )


class AIComparisonResponse(BaseModel):
    """Structured comparative analysis between documented stories."""

    summary: str
    compared_story_ids: list[str]
    similarities: list[str] = Field(default_factory=list)
    differences: list[str] = Field(default_factory=list)
    cultural_context: list[str] = Field(default_factory=list)
    uncertain_details: list[str] = Field(default_factory=list)
    sources: list[AISourceCitation] = Field(default_factory=list)
    model_provider: str = "ollama"
    model_tag: str
    prompt_version: str = "story_comparison_v1"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AIFictionRequest(BaseModel):
    """Request to generate an original creative fictional story inspired by approved records."""

    inspiration_story_ids: list[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="List of 1 to 5 canonical StoryRecord IDs providing motif inspiration",
    )
    setting: Optional[str] = Field(
        default="fog-draped coastal town",
        max_length=200,
        description="Atmospheric geographic/temporal setting",
    )
    atmosphere: Optional[str] = Field(
        default="quiet dread",
        max_length=100,
        description="Tone (e.g. 'gothic mystery', 'quiet dread', 'melancholic ghost story')",
    )
    narrative_style: Optional[str] = Field(
        default="found research document",
        max_length=100,
        description="Perspective/format (e.g. 'diary entry', 'oral storyteller', 'unmailed letter')",
    )
    creative_prompt: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional specific creative situation or conflict",
    )


class AIFictionResponse(BaseModel):
    """Response containing the isolated fictional narrative record."""

    fiction_record: GeneratedFictionRecord
    saved_path: Optional[str] = None
    model_tag: str
    prompt_version: str = "story_generation_v1"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

