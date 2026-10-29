"""Source Registry Schemas for KathaYantra External Data Sources and APIs."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from app.schemas.story import RightsStatusEnum, validate_web_url


class SourceApiStatusEnum(str, Enum):
    """API or dataset integration status."""

    DOCUMENTED_API = "documented_api"
    PUBLIC_DATASET = "public_dataset"
    SEARCHABLE_CATALOGUE = "searchable_catalogue"
    REFERENCE_ONLY = "reference_only"
    REQUIRES_CREDENTIALS = "requires_credentials"
    REQUIRES_PERMISSION = "requires_permission"
    NOT_YET_VERIFIED = "not_yet_verified"


class SourceRegistryItem(BaseModel):
    """Schema for a registered data source or API."""

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

