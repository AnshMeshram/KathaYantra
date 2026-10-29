"""Dataset Manifest Schemas for KathaYantra Tracking and Verification."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class TargetBreakdown(BaseModel):
    per_country_folklore: int = 10
    per_country_urban_legends: int = 10
    total_countries: int = 15


class ActualCounts(BaseModel):
    total_records: int = 0
    folklore_records: int = 0
    urban_legend_records: int = 0


class DatasetManifest(BaseModel):
    """Manifest tracking dataset coverage, actual vs target counts, and rights status."""

    dataset_version: str = Field(default="0.1.0", description="Semantic version of the dataset")
    country_list: list[str] = Field(..., description="List of 15 target country codes")
    required_record_count: int = Field(default=300, description="Target total verified record count")
    target_breakdown: TargetBreakdown = Field(default_factory=TargetBreakdown)
    current_actual_counts: ActualCounts = Field(default_factory=ActualCounts)
    folklore_counts_by_country: dict[str, int] = Field(..., description="Count of folklore records per country")
    urban_legend_counts_by_country: dict[str, int] = Field(..., description="Count of urban legend records per country")
    unverified_records: int = Field(default=0, description="Count of unverified records")
    rights_pending_records: int = Field(default=0, description="Count of records awaiting rights review")
    source_coverage: list[str] = Field(default_factory=list, description="List of actively contributing sources")
    last_validation_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of last validation run",
    )
    dataset_limitations: list[str] = Field(
        default_factory=list,
        description="Known dataset boundaries and disclaimers",
    )

