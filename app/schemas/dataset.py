"""Country Dataset Envelope Schema for KathaYantra Seed Repositories.

Standardizes the shape of all 30 country-level seed JSON files across folklore and urban legends,
enforcing country/category alignment, unique record IDs, and dynamic count calculation.
"""

from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.story import CategoryEnum, StoryRecord


class DatasetMetadata(BaseModel):
    """Metadata envelope header for country seed files."""

    description: str = Field(default="", description="Human-readable description of this country dataset partition")
    dataset_version: str = Field(default="2.0.0", description="Dataset semantic version")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last modification timestamp")
    provenance_notes: Optional[str] = Field(default=None, description="Curatorial and provenance notes")
    target_count: int = Field(default=10, ge=0, description="Intended quota milestone for this partition")
    actual_record_count: int = Field(default=0, ge=0, description="Dynamically calculated count of valid records")
    total_records: int = Field(default=0, ge=0, description="Total record count (Phase 1 compatibility)")
    status: str = Field(default="pending_curation", description="Partition curation status")
    validation_status: str = Field(default="valid", description="Data validation status")
    last_updated: Optional[str] = Field(default=None, description="ISO timestamp string (compatibility)")
    import_batch_references: list[str] = Field(
        default_factory=list,
        description="References to import batches contributing to this dataset",
    )


class DatasetEnvelope(BaseModel):
    """Canonical dataset envelope for all country seed files (e.g. data/seed/folklore/IN.json)."""

    schema_version: str = Field(default="2.0.0", description="Dataset envelope contract version")
    dataset_id: str = Field(default="", description="Unique dataset partition slug (e.g. IN-folklore)")
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 2-letter country code")
    category: CategoryEnum = Field(..., description="Primary category: folklore or urban_legend")
    records: list[StoryRecord] = Field(default_factory=list, description="Validated story records in this partition")
    metadata: DatasetMetadata = Field(default_factory=DatasetMetadata, description="Dataset envelope metadata")

    @field_validator("country_code")
    @classmethod
    def validate_country(cls, v: str) -> str:
        upper = v.strip().upper()
        if upper not in SUPPORTED_COUNTRY_CODES:
            raise ValueError(f"Country code '{v}' is not supported in KathaYantra: {list(SUPPORTED_COUNTRY_CODES.keys())}")
        return upper

    @model_validator(mode="after")
    def validate_envelope_alignment(self) -> "DatasetEnvelope":
        expected_dataset_id = f"{self.country_code}-{self.category.value}"
        if not self.dataset_id:
            self.dataset_id = expected_dataset_id
        elif self.dataset_id != expected_dataset_id:
            raise ValueError(
                f"dataset_id '{self.dataset_id}' does not match expected '{expected_dataset_id}'"
            )

        # Enforce that every record inside this file matches the file's country and category
        record_ids: set[str] = set()
        for idx, rec in enumerate(self.records, start=1):
            if rec.country_code != self.country_code:
                raise ValueError(
                    f"Record at index {idx} has country_code '{rec.country_code}' which does not match envelope '{self.country_code}'"
                )
            if rec.category != self.category:
                raise ValueError(
                    f"Record at index {idx} has category '{rec.category.value}' which does not match envelope '{self.category.value}'"
                )
            if rec.id in record_ids:
                raise ValueError(f"Duplicate record ID '{rec.id}' detected within dataset envelope '{self.dataset_id}'")
            record_ids.add(rec.id)

        # Synchronize dynamic actual counts
        actual_count = len(self.records)
        self.metadata.actual_record_count = actual_count
        self.metadata.total_records = actual_count

        return self


# Backward-compatible alias for Phase 1 code
class CountrySeedFile(DatasetEnvelope):
    """Backward-compatible seed file model for Phase 1 consumers."""

    pass

