"""Source Reference and Registry Schemas for KathaYantra.

Defines both the individual story bibliographic reference (StorySource)
and the central external repository/API catalog item (SourceRegistryItem),
with referential integrity validation and rights tracking.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator, model_validator


class SourceApiStatusEnum(str, Enum):
    """API or dataset integration status in the registry."""

    DOCUMENTED_API = "documented_api"
    PUBLIC_DATASET = "public_dataset"
    SEARCHABLE_CATALOGUE = "searchable_catalogue"
    REFERENCE_ONLY = "reference_only"
    REQUIRES_CREDENTIALS = "requires_credentials"
    REQUIRES_PERMISSION = "requires_permission"
    NOT_YET_VERIFIED = "not_yet_verified"


class RightsStatusEnum(str, Enum):
    """Rights assessment status."""

    APPROVED = "approved"
    METADATA_ONLY = "metadata_only"
    PUBLIC_DOMAIN_VERIFIED = "public_domain_verified"
    PERMISSION_REQUIRED = "permission_required"
    NEEDS_RIGHTS_REVIEW = "needs_rights_review"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


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
    """Canonical bibliographic source citation embedded within a story record."""

    id: Optional[str] = Field(default=None, description="Stable source slug or registry link identifier")
    title: str = Field(default="", description="Title of the source publication, article, or narrative entry")
    publisher: str = Field(default="", description="Publisher, holding institution, or archive name")
    name: str = Field(default="", description="Human-readable citation label (Phase 1 compatibility)")
    url: str = Field(..., description="Canonical or web URL of the source")
    canonical_url: Optional[str] = Field(default=None, description="Authoritative canonical permanent URL")
    external_id: Optional[str] = Field(default=None, description="External catalog ID (e.g. ISBN, LoC call, OCLC)")
    source_type: str = Field(default="web", description="Type of source (book, academic, archive, web, api)")
    language: str = Field(default="en", description="Source document language (ISO 639-1)")
    published_at: Optional[str] = Field(default=None, description="Publication date or historical era string")
    updated_at: Optional[datetime] = Field(default=None, description="Source update timestamp")
    retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp when data was accessed")
    license_name: Optional[str] = Field(default=None, description="Documented license name (e.g. Public Domain, CC0)")
    license_url: Optional[str] = Field(default=None, description="License terms URL if available")
    rights_status: RightsStatusEnum = Field(
        default=RightsStatusEnum.NEEDS_RIGHTS_REVIEW,
        description="Rights assessment classification for this citation",
    )
    reuse_scope: str = Field(default="metadata_and_citation", description="Permitted scope of reuse")
    attribution_required: bool = Field(default=True, description="Whether explicit attribution text must be rendered")
    attribution_text: Optional[str] = Field(default=None, description="Mandatory attribution statement")
    full_text_reuse_allowed: bool = Field(default=False, description="Whether full narrative text redistribution is cleared")
    notes: Optional[str] = Field(default=None, description="Archival or editorial notes on source provenance")
    citation: Optional[str] = Field(default=None, description="Formal Chicago/MLA bibliographic citation string")
    access_date: Optional[str] = Field(default=None, description="ISO date when source was referenced (compatibility)")

    @field_validator("url")
    @classmethod
    def check_url(cls, v: str) -> str:
        return validate_web_url(v)

    @field_validator("canonical_url", "license_url")
    @classmethod
    def check_optional_url(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return validate_web_url(v)
        return v

    @model_validator(mode="after")
    def synchronize_labels(self) -> "StorySource":
        # Synchronize name, publisher, title for full backward compatibility
        if not self.name and self.publisher:
            self.name = self.publisher
        elif not self.name and self.title:
            self.name = self.title

        if not self.publisher and self.name:
            self.publisher = self.name

        if not self.title and self.name:
            self.title = self.name

        if not self.name and not self.title and not self.publisher:
            raise ValueError("StorySource must provide at least one of 'name', 'title', or 'publisher'.")

        return self


class SourceRegistryItem(BaseModel):
    """Schema for a registered external data source or API."""

    id: str = Field(..., min_length=2, description="Stable source slug identifier")
    name: str = Field(..., min_length=2, description="Human-readable source name")
    canonical_url: str = Field(..., description="Canonical source homepage or domain")
    docs_or_dataset_url: str = Field(..., description="Documentation, portal, or dataset URL")
    source_type: str = Field(..., description="Type of source (e.g. encyclopedic_api, open_dataset)")
    api_status: SourceApiStatusEnum = Field(..., description="API availability status")
    auth_required: bool = Field(default=False, description="Whether authentication or API key is required")
    rate_limit_info: str = Field(..., description="Rate limiting or access throttling policy")
    content_format: str = Field(..., description="Data formats provided (e.g. JSON, HTML, SPARQL)")
    supported_research_purpose: str = Field(..., description="Role of this source in KathaYantra")
    geographic_or_cultural_coverage: list[str] = Field(..., description="Covered countries or global scope")
    licensing_info: str = Field(..., description="Applicable copyright and license terms")
    rights_assessment_status: RightsStatusEnum = Field(..., description="Rights assessment classification")
    full_text_reuse_verified: bool = Field(default=False, description="Whether full text redistribution is permitted")
    retain_metadata_only: bool = Field(default=True, description="Whether KathaYantra should only store metadata and links")
    last_checked_date: str = Field(..., description="ISO date when source details were last verified")
    implementation_status: str = Field(default="registered_planned", description="Current implementation stage")
    known_limitations: str = Field(..., description="Known risks, limitations, or caveats")

    @field_validator("canonical_url", "docs_or_dataset_url")
    @classmethod
    def check_urls(cls, v: str) -> str:
        return validate_web_url(v)
