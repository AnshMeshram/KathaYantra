"""Story Narrative Schemas for KathaYantra Folklore and Urban Legends.

Defines the canonical Pydantic v2 data models for folklore and urban legend records,
verifying provenance, category integrity, rights states, and cultural attribution.
"""

from datetime import datetime, timezone
from enum import Enum
import re
from typing import Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator, model_validator
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.source import RightsStatusEnum, StorySource, validate_web_url


class CategoryEnum(str, Enum):
    """Primary content category."""

    FOLKLORE = "folklore"
    URBAN_LEGEND = "urban_legend"


class VerificationStatusEnum(str, Enum):
    """Curatorial verification state."""

    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"


class ContentOriginEnum(str, Enum):
    """Origin classification of narrative text content."""

    LICENSED_DATASET = "licensed_dataset"
    PUBLIC_DOMAIN_SOURCE = "public_domain_source"
    ORIGINAL_SUMMARY = "original_summary"
    METADATA_ONLY = "metadata_only"
    USER_CONTRIBUTED = "user_contributed"
    AI_GENERATED_FICTION = "ai_generated_fiction"


def generate_slug(title: str) -> str:
    """Generate a clean URL-safe slug from a narrative title."""
    clean = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "-", clean).strip("-")
    return slug or "untitled-story"


class StoryRecord(BaseModel):
    """Canonical KathaYantra story record model for folklore and urban legends."""

    id: str = Field(
        ...,
        min_length=3,
        description="Unique stable record identifier (e.g. IN-FOLK-001 or US-URBAN-001)",
    )
    schema_version: str = Field(default="2.0.0", description="Story schema contract version")
    record_version: str = Field(default="1.0.0", description="Semantic record version")
    title: str = Field(..., min_length=2, max_length=300, description="Canonical title of the narrative")
    slug: str = Field(default="", description="URL-safe slug identifier")
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 2-letter country code")
    category: CategoryEnum = Field(..., description="Primary category: folklore or urban_legend")
    subtype: Optional[str] = Field(
        default=None,
        description="Sub-genre classification (e.g. ghost_story, jataka_tale, cryptid, kaidan)",
    )
    summary: str = Field(..., min_length=10, max_length=5000, description="Original concise synopsis of the narrative")
    long_description: Optional[str] = Field(
        default=None,
        max_length=250000,
        description="Detailed story text or translation (omitted if metadata-only)",
    )
    alternate_names: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Variant titles, indigenous names, or regional designations",
    )
    language: str = Field(default="en", description="Language of this record text (ISO 639-1)")
    alternate_languages: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Other languages associated with traditional tellings",
    )
    motifs: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Thompson motif index codes or folk motif tags",
    )
    themes: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Keywords or thematic curatorial tags",
    )
    historical_period: Optional[str] = Field(
        default=None,
        description="Historical era, century, or earliest documented period",
    )
    region_or_community: Optional[str] = Field(
        default=None,
        description="Specific cultural, ethnic, indigenous, or regional community",
    )
    community_attributions: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Specific sovereign tribal nations, ethnic groups, or regional communities",
    )
    geographic_associations: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Geographic landmarks, cities, or sites associated with the narrative",
    )
    variant_notes: Optional[str] = Field(default=None, description="Notes on regional or cultural variants")
    related_record_ids: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Cross-references to related folklore or urban legend record IDs",
    )
    sources: list[StorySource] = Field(..., min_length=1, description="At least one documented source is required")
    source_type: str = Field(default="reference", description="Primary source classification")
    license: str = Field(default="Rights Managed / Educational Use", description="Copyright or license notice")
    rights_status: RightsStatusEnum = Field(
        default=RightsStatusEnum.NEEDS_RIGHTS_REVIEW,
        description="Rights assessment classification",
    )
    attribution_text: Optional[str] = Field(default=None, description="Mandatory attribution string if required")
    canonical_url: Optional[str] = Field(default=None, description="Canonical link for authoritative record")
    retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of data retrieval")
    verification_status: VerificationStatusEnum = Field(
        default=VerificationStatusEnum.NEEDS_REVIEW,
        description="Curatorial review state",
    )
    content_origin: ContentOriginEnum = Field(
        default=ContentOriginEnum.METADATA_ONLY,
        description="Origin classification of content",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Record creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Record last updated timestamp",
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[A-Z]{2}-(FOLK|URBAN)-[0-9]{3,}$", v):
            raise ValueError(
                f"Invalid record id format '{v}'. Expected format: [COUNTRY_CODE]-(FOLK|URBAN)-[INDEX] (e.g. IN-FOLK-001)"
            )
        return v

    @field_validator("country_code")
    @classmethod
    def validate_country(cls, v: str) -> str:
        upper = v.strip().upper()
        if upper not in SUPPORTED_COUNTRY_CODES:
            raise ValueError(f"Country code '{v}' is not one of the 15 supported countries.")
        return upper

    @field_validator("canonical_url")
    @classmethod
    def validate_canonical_url(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return validate_web_url(v)
        return v

    @model_validator(mode="after")
    def validate_record_integrity(self) -> "StoryRecord":
        # 1. Enforce ID prefix agreement with country_code
        expected_country_prefix = self.id[:2]
        if expected_country_prefix != self.country_code:
            raise ValueError(
                f"Record ID prefix '{expected_country_prefix}' does not match country_code '{self.country_code}'"
            )

        # 2. Enforce ID category tag agreement with category
        if self.category == CategoryEnum.FOLKLORE and "-FOLK-" not in self.id:
            raise ValueError(f"Folklore record ID '{self.id}' must contain '-FOLK-'")
        elif self.category == CategoryEnum.URBAN_LEGEND and "-URBAN-" not in self.id:
            raise ValueError(f"Urban legend record ID '{self.id}' must contain '-URBAN-'")

        # 3. AI-Generated Fiction REJECTION in StoryRecord
        if self.content_origin == ContentOriginEnum.AI_GENERATED_FICTION:
            raise ValueError(
                "AI-generated fiction cannot be saved as an authentic StoryRecord. "
                "Use GeneratedFictionRecord instead to maintain archival integrity."
            )

        # 4. Auto-generate slug if empty
        if not self.slug and self.title:
            self.slug = generate_slug(self.title)

        # 5. Check duplicate source URLs within record
        source_urls = [s.url.lower() for s in self.sources]
        if len(source_urls) != len(set(source_urls)):
            raise ValueError(f"StoryRecord '{self.id}' contains duplicate source URLs in its citations.")

        return self


class CountrySeedFile(BaseModel):
    """Schema for a country category seed JSON file (Phase 1 compatibility)."""

    schema_version: str = Field(default="2.0.0")
    dataset_id: str = Field(default="")
    country_code: str
    category: CategoryEnum
    records: list[StoryRecord] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    @field_validator("country_code")
    @classmethod
    def validate_country(cls, v: str) -> str:
        upper = v.strip().upper()
        if upper not in SUPPORTED_COUNTRY_CODES:
            raise ValueError(f"Country code '{v}' is not supported.")
        return upper

