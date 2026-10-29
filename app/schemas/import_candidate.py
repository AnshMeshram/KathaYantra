"""Import Candidate Schema for KathaYantra Ingestion Pipelines.

Maintains strict architectural separation between raw, incomplete incoming
source data (e.g. raw CSV rows, raw API harvests) and curated, published StoryRecord objects.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.source import RightsStatusEnum, validate_web_url
from app.schemas.story import CategoryEnum, VerificationStatusEnum


class CandidateDispositionEnum(str, Enum):
    """Review and lifecycle disposition of an import candidate."""

    NEW_CANDIDATE = "new_candidate"
    NEEDS_MAPPING_REVIEW = "needs_mapping_review"
    NEEDS_SOURCE_VERIFICATION = "needs_source_verification"
    NEEDS_RIGHTS_REVIEW = "needs_rights_review"
    ELIGIBLE_FOR_EDITORIAL_REVIEW = "eligible_for_editorial_review"
    APPROVED_FOR_PUBLICATION = "approved_for_publication"
    REJECTED = "rejected"
    DUPLICATE_CANDIDATE = "duplicate_candidate"


class ImportCandidate(BaseModel):
    """Staging model for unreviewed or partially processed raw narrative records."""

    candidate_id: str = Field(..., min_length=3, description="Unique candidate identifier (e.g. CAND-FT-0001)")
    import_batch_id: str = Field(..., min_length=2, description="Batch identifier for this import run")
    source_registry_id: Optional[str] = Field(default=None, description="Slug of registered source in source_registry.json")
    external_id: Optional[str] = Field(default=None, description="Upstream accession or item identifier")
    raw_title: str = Field(..., min_length=1, description="Raw title as provided by upstream source")
    raw_nation: Optional[str] = Field(default=None, description="Raw nation / cultural tag from upstream data")
    raw_language: Optional[str] = Field(default=None, description="Raw language code or label")
    raw_url: Optional[str] = Field(default=None, description="Raw upstream web URL")
    raw_metadata: dict[str, Any] = Field(default_factory=dict, description="Raw unparsed metadata payload")
    raw_text_available: bool = Field(default=False, description="Whether raw story text payload is accessible in raw storage")
    rights_status: RightsStatusEnum = Field(
        default=RightsStatusEnum.NEEDS_RIGHTS_REVIEW,
        description="Assessed rights state of this candidate",
    )
    verification_status: VerificationStatusEnum = Field(
        default=VerificationStatusEnum.NEEDS_REVIEW,
        description="Verification stage",
    )
    proposed_country_code: Optional[str] = Field(default=None, description="Proposed ISO country code pending review")
    proposed_category: Optional[CategoryEnum] = Field(default=None, description="Proposed primary category")
    proposed_summary: Optional[str] = Field(default=None, description="Draft or extracted summary")
    validation_errors: list[str] = Field(default_factory=list, description="Validation issues detected during staging")
    review_notes: Optional[str] = Field(default=None, description="Human curator notes or provenance warnings")
    imported_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of candidate import",
    )
    reviewed_at: Optional[datetime] = Field(default=None, description="Timestamp of human review action")
    reviewed_by: Optional[str] = Field(default=None, description="Curator identifier who conducted review")
    disposition: CandidateDispositionEnum = Field(
        default=CandidateDispositionEnum.NEW_CANDIDATE,
        description="Current candidate review disposition",
    )
    schema_version: str = Field(default="2.0.0", description="Import candidate schema contract version")

    @field_validator("raw_url")
    @classmethod
    def check_raw_url(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return validate_web_url(v)
        return v

