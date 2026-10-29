"""API Envelope and Response Schemas for KathaYantra REST API."""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.country import CountryRecord
from app.schemas.story import StoryRecord, StorySource

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Metadata describing the pagination window of a collection."""

    total: int = Field(ge=0, description="Total number of items matching filter criteria")
    limit: int = Field(ge=1, le=100, description="Page size limit requested")
    offset: int = Field(ge=0, description="Page offset starting index")
    has_next: bool = Field(description="Whether a subsequent page exists")
    has_prev: bool = Field(description="Whether a prior page exists")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard collection response wrapper."""

    data: list[T] = Field(description="List of records for the requested page")
    pagination: PaginationMeta = Field(description="Pagination cursor metadata")
    meta: dict[str, Any] = Field(default_factory=dict, description="Query execution and filter context")


class SingleResponse(BaseModel, Generic[T]):
    """Standard single-record response envelope."""

    data: T = Field(description="Requested entity payload")


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    error_code: str = Field(description="Machine-readable error classification code")
    message: str = Field(description="Human-readable error description")
    detail: Optional[Any] = Field(default=None, description="Optional diagnostic details or validation errors")


class CountryStatsResponse(BaseModel):
    """Detailed published metrics and target quota evaluation for a country."""

    country_code: str = Field(description="ISO 3166-1 alpha-2 country code")
    country_name: str = Field(description="Standard country name")
    folklore_count: int = Field(ge=0, description="Actual published folklore records")
    urban_legend_count: int = Field(ge=0, description="Actual published urban legend records")
    total_count: int = Field(ge=0, description="Total published records")
    folklore_target: int = Field(default=10, description="Folklore target quota")
    urban_legend_target: int = Field(default=10, description="Urban legend target quota")
    total_target: int = Field(default=20, description="Total country quota target")
    folklore_gap: int = Field(ge=0, description="Remaining folklore deficit")
    urban_legend_gap: int = Field(ge=0, description="Remaining urban legend deficit")
    total_gap: int = Field(ge=0, description="Total remaining deficit")
    is_quotas_met: bool = Field(description="Whether both category quotas are fully met")
    source_count: int = Field(ge=0, description="Number of distinct bibliographic citations across country records")
    cultural_context: str = Field(description="Cultural background overview")


class RelatedStoryItem(BaseModel):
    """Curated or motif-based relationship link between stories."""

    story_id: str = Field(description="Target story identifier")
    title: str = Field(description="Target story canonical title")
    category: str = Field(description="Story category ('folklore' or 'urban_legend')")
    country_code: str = Field(description="Origin country code")
    summary: str = Field(description="Story synopsis")
    relationship_basis: str = Field(description="Documented rationale for the relationship link")
    shared_motifs: list[str] = Field(default_factory=list, description="Shared Thompson motif or keyword codes")
    shared_themes: list[str] = Field(default_factory=list, description="Shared thematic tags")


class SearchSuggestion(BaseModel):
    """Bounded autocomplete or search suggestion item."""

    text: str = Field(description="Suggested search term, title, or motif")
    suggestion_type: str = Field(description="'title', 'motif', 'alternate_name', or 'region'")
    category: Optional[str] = Field(default=None, description="Associated category if specific to one")
    country_code: Optional[str] = Field(default=None, description="Associated country if specific to one")


class DatasetQualityResponse(BaseModel):
    """Comprehensive dataset health, audit, and candidate disposition report."""

    status: str = Field(default="healthy", description="Overall archive health status")
    published_records: int = Field(description="Count of active published StoryRecords")
    seed_files_valid: int = Field(description="Count of valid JSON seed files")
    total_seed_files: int = Field(default=30, description="Expected seed files count (15x2)")
    staged_candidates_count: int = Field(description="Count of staged unpromoted candidates")
    retrieval_index_count: int = Field(description="Count of records compiled in FTS5 index")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit reconciliation metrics")


class SourceReadinessResponse(BaseModel):
    """Detailed audit metrics confirming dataset readiness for AI retrieval."""

    total_records_audited: int = Field(description="Total records inspected")
    accepted_for_ai: int = Field(description="Records meeting AI retrieval readiness")
    flagged_records_count: int = Field(description="Records with unresolved issues")
    acceptance_rate_percent: float = Field(description="Percentage of records cleared for retrieval")
    status: str = Field(description="'pass' or 'needs_remediation'")
    issues_by_category: dict[str, int] = Field(default_factory=dict, description="Categorized issue tallies")
