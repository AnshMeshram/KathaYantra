"""Story Narrative Schemas for KathaYantra Folklore and Urban Legends.

Defines the Pydantic v2 data models for folklore and urban legend records,
verifying provenance, category integrity, rights states, and cultural attribution.
"""

from datetime import datetime, timezone
from enum import Enum
import re
from typing import Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator
from app.schemas.country import SUPPORTED_COUNTRY_CODES


class CategoryEnum(str, Enum):
    """Primary content category."""

    FOLKLORE = "folklore"
    URBAN_LEGEND = "urban_legend"


class VerificationStatusEnum(str, Enum):
    """Curatorial verification state."""

    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"


class RightsStatusEnum(str, Enum):
    """Rights assessment status."""

    APPROVED = "approved"
    METADATA_ONLY = "metadata_only"
    PUBLIC_DOMAIN_VERIFIED = "public_domain_verified"
    PERMISSION_REQUIRED = "permission_required"
    NEEDS_RIGHTS_REVIEW = "needs_rights_review"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


class ContentOriginEnum(str, Enum):
    """Origin of narrative text content."""

    LICENSED_DATASET = "licensed_dataset"
    PUBLIC_DOMAIN_SOURCE = "public_domain_source"
    ORIGINAL_SUMMARY = "original_summary"
    METADATA_ONLY = "metadata_only"
    USER_CONTRIBUTED = "user_contributed"
    AI_GENERATED_FICTION = "ai_generated_fiction"


def validate_web_url(url_str: str) -> str:
    """Validate that a URL string has valid HTTP or HTTPS scheme and network location."""
    if not url_str or not isinstance(url_str, str):
        raise ValueError("URL must be a non-empty string.")
    parsed = urlparse(url_str.strip())
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme '{parsed.scheme}'; expected 'http' or 'https'.")
    if not parsed.netloc:
        raise ValueError("URL is missing a valid host / network location.")
    return url_str.strip()


class StorySource(BaseModel):
    """Documented reference or citation for a story record."""

    name: str = Field(..., min_length=2, description="Name of source publication, archive, or institution")
    url: str = Field(..., description="Canonical or web URL of the source")
    source_type: str = Field(default="web", description="Type of source (e.g. academic, archive, website, book)")
    citation: Optional[str] = Field(default=None, description="Formal bibliographic citation")
    access_date: Optional[str] = Field(default=None, description="ISO date when source was referenced")

    @field_validator("url")
    @classmethod
    def check_url(cls, v: str) -> str:
        return validate_web_url(v)


class StoryRecord(BaseModel):
    """Full KathaYantra story record model."""

    id: str = Field(
        ...,
        min_length=3,
        description="Unique stable record identifier (e.g. IN-FOLK-001 or US-URBAN-001)",
    )
    title: str = Field(..., min_length=2, description="Standardized title of the narrative")
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 2-letter country code")
    region_or_community: Optional[str] = Field(
        default=None,
        description="Specific cultural, ethnic, indigenous, or regional group",
    )
    category: CategoryEnum = Field(..., description="Primary category: folklore or urban_legend")
    subtype: Optional[str] = Field(
        default=None,
        description="Sub-genre (e.g. ghost_story, fairy_tale, warning_legend, cryptid)",
    )
    summary: str = Field(..., min_length=10, description="Concise synopsis of the narrative")
    long_description: Optional[str] = Field(default=None, description="Detailed story text or transcription")
    alternate_names: list[str] = Field(default_factory=list, description="Variant titles or regional names")
    language: str = Field(default="en", description="Language of this record text")
    motifs: list[str] = Field(default_factory=list, description="Thompson motif index codes or thematic motifs")
    themes: list[str] = Field(default_factory=list, description="Keywords or thematic tags")
    historical_period: Optional[str] = Field(default=None, description="Historical origin or first documented era")
    variant_notes: Optional[str] = Field(default=None, description="Notes on regional or cultural variants")
    sources: list[StorySource] = Field(..., min_length=1, description="At least one documented source is required")
    source_type: str = Field(default="reference", description="Primary source classification")
    license: str = Field(default="Rights Managed / Educational Use", description="Copyright or license notice")
    rights_status: RightsStatusEnum = Field(
        default=RightsStatusEnum.NEEDS_RIGHTS_REVIEW,
        description="Rights assessment state",
    )
    attribution_text: Optional[str] = Field(default=None, description="Mandatory attribution string if required")
    canonical_url: Optional[str] = Field(default=None, description="Canonical link for authoritative record")
    retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of data retrieval")
    verification_status: VerificationStatusEnum = Field(
        default=VerificationStatusEnum.NEEDS_REVIEW,
        description="Verification state",
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
    record_version: str = Field(default="1.0.0", description="Semantic record version")

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


class CountrySeedFile(BaseModel):
    """Schema for a country category seed JSON file (e.g. data/seed/folklore/IN.json)."""

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

