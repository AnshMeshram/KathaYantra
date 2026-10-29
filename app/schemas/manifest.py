"""Dataset Manifest Schemas for KathaYantra Tracking, Auditing, and Verification.

Provides comprehensive reconciliation between intended quotas (300 target stories)
and true actual counts across 15 countries and both content categories.
"""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class TargetBreakdown(BaseModel):
    """Target quotas breakdown across categories."""

    per_country_folklore: int = 10
    per_country_urban_legends: int = 10
    total_countries: int = 15


class ActualCounts(BaseModel):
    """Calculated actual counts across categories."""

    total_records: int = 0
    folklore_records: int = 0
    urban_legend_records: int = 0


class DatasetManifest(BaseModel):
    """Canonical manifest tracking dataset coverage, actual vs target counts, and rights status."""

    schema_version: str = Field(default="2.0.0", description="Dataset manifest schema contract version")
    dataset_version: str = Field(default="0.2.0", description="Semantic version of the dataset collection")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of manifest generation",
    )
    last_validation_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of last validation run (Phase 1 compatibility)",
    )
    target_country_count: int = Field(default=15, description="Number of target countries (15)")
    actual_country_count: int = Field(default=15, description="Number of configured country datasets")
    country_list: list[str] = Field(..., description="List of 15 target country codes")
    required_record_count: int = Field(default=300, description="Target total verified record count")
    total_target_records: int = Field(default=300, description="Target total verified record count (Phase 2)")
    target_breakdown: TargetBreakdown = Field(default_factory=TargetBreakdown)
    target_records_per_category: dict[str, int] = Field(
        default_factory=lambda: {"folklore": 10, "urban_legends": 10},
        description="Quotas per category",
    )
    current_actual_counts: ActualCounts = Field(default_factory=ActualCounts)
    actual_record_count: int = Field(default=0, ge=0, description="Sum of actual published records")
    folklore_counts_by_country: dict[str, int] = Field(..., description="Count of folklore records per country")
    urban_legend_counts_by_country: dict[str, int] = Field(..., description="Count of urban legend records per country")
    published_and_verified_records: int = Field(default=0, description="Count of records passing publication policy")
    unverified_records: int = Field(default=0, description="Count of unverified records")
    unverified_candidates: int = Field(default=0, description="Count of unverified candidates in review pipeline")
    rejected_records: int = Field(default=0, description="Count of records rejected during curation")
    rights_pending_records: int = Field(default=0, description="Count of records awaiting rights review")
    metadata_only_records: int = Field(default=0, description="Count of metadata-only records")
    records_by_content_origin: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of records by ContentOriginEnum",
    )
    records_by_source: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of records by contributing source",
    )
    records_by_language: dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of records by primary language code",
    )
    source_coverage: list[str] = Field(default_factory=list, description="List of actively contributing sources")
    duplicate_findings_count: int = Field(default=0, description="Count of suspected duplicates requiring review")
    schema_invalid_count: int = Field(default=0, description="Count of schema-invalid records found during scan")
    source_link_validation_findings: list[str] = Field(
        default_factory=list,
        description="Issues detected with source references or URLs",
    )
    coverage_gaps: list[str] = Field(
        default_factory=list,
        description="List of country/category pairs with 0 verified records",
    )
    dataset_validation_status: str = Field(
        default="valid_empty_staging",
        description="Status flag of dataset integrity",
    )
    dataset_limitations: list[str] = Field(
        default_factory=list,
        description="Known dataset boundaries, rights warnings, and disclaimers",
    )
