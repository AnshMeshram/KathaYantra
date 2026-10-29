"""Tests for Canonical Country Registry Schema (Phase 2)."""

from pydantic import ValidationError
import pytest
from app.schemas.country import (
    CountryCodeEnum,
    CountryRecord,
    CountryRecordTargets,
    SUPPORTED_COUNTRY_CODES,
)


def test_all_15_supported_countries_valid():
    """Verify that all 15 supported country codes pass canonical validation."""
    assert len(SUPPORTED_COUNTRY_CODES) == 15
    for code, name in SUPPORTED_COUNTRY_CODES.items():
        rec = CountryRecord(
            code=code,
            name=name,
            region="Test Region",
            primary_languages=["en"],
            regions_or_communities=["Region A"],
            cultural_context="Rich folklore traditions.",
        )
        assert rec.code == code
        assert rec.iso_alpha2 == code
        assert rec.display_name == name
        assert rec.enabled is True
        assert rec.record_targets.folklore == 10
        assert rec.record_targets.urban_legends == 10
        assert rec.record_targets.total == 20


def test_country_code_case_normalization_and_rejection():
    """Verify lowercase country codes are normalized and unsupported codes fail."""
    # Lowercase gets normalized to uppercase
    rec = CountryRecord(code="in", name="India")
    assert rec.code == "IN"
    assert rec.iso_alpha2 == "IN"

    # Unsupported country code fails
    with pytest.raises(ValidationError) as exc:
        CountryRecord(code="FR", name="France")
    assert "not one of the 15 supported countries" in str(exc.value)


def test_iso_alpha2_mismatch_validation():
    """Verify that iso_alpha2 must equal country code."""
    with pytest.raises(ValidationError) as exc:
        CountryRecord(code="JP", iso_alpha2="US", name="Japan")
    assert "must match country code" in str(exc.value)


def test_negative_target_quotas_rejected():
    """Verify that negative target quota values fail validation."""
    with pytest.raises(ValidationError):
        CountryRecordTargets(folklore=-1, urban_legends=10)

    with pytest.raises(ValidationError):
        CountryRecordTargets(folklore=10, urban_legends=-5)


def test_seed_countries_json_validity():
    """Verify that all 15 entries in data/seed/countries.json validate against CountryRecord."""
    import json
    from pathlib import Path

    countries_file = Path("data/seed/countries.json")
    assert countries_file.exists()

    with open(countries_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 15
    codes_seen = set()
    for item in data:
        record = CountryRecord.model_validate(item)
        assert record.code not in codes_seen, f"Duplicate country code {record.code}"
        codes_seen.add(record.code)
        assert record.schema_version == "2.0.0"
        assert record.record_targets.total == 20
        assert len(record.primary_languages) > 0
        assert len(record.regions_or_communities) > 0

    assert codes_seen == set(SUPPORTED_COUNTRY_CODES.keys())
