"""Country and Regional Attribution Schemas for KathaYantra."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator

SUPPORTED_COUNTRY_CODES = {
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


class CountryRecord(BaseModel):
    """Metadata for a target country."""

    code: str = Field(..., min_length=2, max_length=2, description="ISO 2-letter country code")
    name: str = Field(..., description="Full country name")
    region: str = Field(..., description="Geographic cultural region")
    target_folklore_count: int = Field(default=10, ge=0)
    target_urban_legends_count: int = Field(default=10, ge=0)
    total_target: int = Field(default=20, ge=0)
    status: str = Field(default="active_target")
    cultural_context_notes: str = Field(default="")

    @field_validator("code")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        upper = v.upper()
        if upper not in SUPPORTED_COUNTRY_CODES:
            raise ValueError(
                f"Country code '{v}' is not one of the 15 supported countries: {list(SUPPORTED_COUNTRY_CODES.keys())}"
            )
        return upper

