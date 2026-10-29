"""Country and Regional Attribution Schemas for KathaYantra.

Defines the canonical country registry model, ISO 3166-1 alpha-2 validation,
cultural community attributions, and folklore/urban legend quota targets.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

SUPPORTED_COUNTRY_CODES: dict[str, str] = {
    "IN": "India",
    "US": "United States",
    "JP": "Japan",
    "MX": "Mexico",
    "IE": "Ireland",
    "GB": "United Kingdom",
    "BR": "Brazil",
    "GR": "Greece",
    "CN": "China",
    "NG": "Nigeria",
    "KR": "South Korea",
    "PH": "Philippines",
    "ID": "Indonesia",
    "EG": "Egypt",
    "DE": "Germany",
}


class CountryCodeEnum(str, Enum):
    """Allowed ISO 3166-1 alpha-2 country codes for KathaYantra."""

    IN = "IN"
    US = "US"
    JP = "JP"
    MX = "MX"
    IE = "IE"
    GB = "GB"
    BR = "BR"
    GR = "GR"
    CN = "CN"
    NG = "NG"
    KR = "KR"
    PH = "PH"
    ID = "ID"
    EG = "EG"
    DE = "DE"


class CountryRecordTargets(BaseModel):
    """Target quotas for verified story curation per country."""

    folklore: int = Field(default=10, ge=0, description="Minimum target folklore records")
    urban_legends: int = Field(default=10, ge=0, description="Minimum target urban legend records")

    @property
    def total(self) -> int:
        return self.folklore + self.urban_legends


class CountryRecord(BaseModel):
    """Canonical country registry model for KathaYantra."""

    code: str = Field(..., min_length=2, max_length=2, description="Canonical ISO 2-letter country code")
    name: str = Field(..., min_length=2, description="Standard English country name")
    display_name: str = Field(default="", description="Localized or formal display title")
    iso_alpha2: str = Field(default="", min_length=2, max_length=2, description="ISO 3166-1 alpha-2 code")
    region: str = Field(default="", description="Geographic cultural region (e.g. South Asia, East Asia)")
    primary_languages: list[str] = Field(
        default_factory=list,
        description="ISO 639-1 language codes representing predominant storytelling traditions",
    )
    regions_or_communities: list[str] = Field(
        default_factory=list,
        description="Key regional, ethnic, or cultural community designations",
    )
    cultural_context: str = Field(default="", description="High-level narrative and folkloric tradition overview")
    cultural_context_notes: str = Field(default="", description="Additional archival curation notes (compatibility)")
    enabled: bool = Field(default=True, description="Whether country is active for collection ingestion")
    status: str = Field(default="active_target", description="Curation status lifecycle")
    record_targets: CountryRecordTargets = Field(
        default_factory=CountryRecordTargets,
        description="Target story quotas for this country",
    )
    target_folklore_count: int = Field(default=10, ge=0, description="Target folklore count (compatibility)")
    target_urban_legends_count: int = Field(default=10, ge=0, description="Target urban legends count (compatibility)")
    total_target: int = Field(default=20, ge=0, description="Total target stories (compatibility)")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Record registration timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Record last updated timestamp",
    )
    schema_version: str = Field(default="2.0.0", description="Country schema contract version")

    @field_validator("code")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        upper = v.strip().upper()
        if upper not in SUPPORTED_COUNTRY_CODES:
            raise ValueError(
                f"Country code '{v}' is not one of the 15 supported countries: {list(SUPPORTED_COUNTRY_CODES.keys())}"
            )
        return upper

    @model_validator(mode="after")
    def synchronize_iso_and_defaults(self) -> "CountryRecord":
        # Ensure display_name defaults to name
        if not self.display_name:
            self.display_name = self.name

        # Ensure iso_alpha2 matches code
        if not self.iso_alpha2:
            self.iso_alpha2 = self.code
        elif self.iso_alpha2.upper() != self.code:
            raise ValueError(
                f"iso_alpha2 '{self.iso_alpha2}' must match country code '{self.code}'"
            )

        # Synchronize backward-compatible cultural context fields
        if not self.cultural_context and self.cultural_context_notes:
            self.cultural_context = self.cultural_context_notes
        elif not self.cultural_context_notes and self.cultural_context:
            self.cultural_context_notes = self.cultural_context

        # Synchronize target counts
        self.target_folklore_count = self.record_targets.folklore
        self.target_urban_legends_count = self.record_targets.urban_legends
        self.total_target = self.record_targets.total

        return self
