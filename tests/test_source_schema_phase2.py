"""Tests for Canonical Source Schemas and Referential Integrity (Phase 2)."""

from pydantic import ValidationError
import pytest
from app.schemas.source import (
    RightsStatusEnum,
    SourceApiStatusEnum,
    SourceRegistryItem,
    StorySource,
    validate_web_url,
)


def test_valid_canonical_story_source():
    """Verify that a full Phase 2 StorySource model validates cleanly."""
    src = StorySource(
        id="loc_afc_001",
        title="American Folklife Center Collections",
        publisher="Library of Congress",
        url="https://www.loc.gov/folklife/",
        canonical_url="https://www.loc.gov/folklife/",
        external_id="AFC-1938-001",
        source_type="national_library_archive",
        language="en",
        published_at="1938",
        license_name="Public Domain (US Government Work)",
        rights_status=RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED,
        reuse_scope="metadata_and_full_text",
        attribution_required=True,
        attribution_text="Library of Congress, American Folklife Center",
        full_text_reuse_allowed=True,
        notes="Digitized field recording and transcript.",
    )

    assert src.title == "American Folklife Center Collections"
    assert src.publisher == "Library of Congress"
    assert src.rights_status == RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED
    assert src.full_text_reuse_allowed is True


def test_story_source_backward_compatibility():
    """Verify Phase 1 compatibility where only 'name' and 'url' were supplied."""
    src = StorySource(
        name="Ancient Irish Tales",
        url="https://example.com/irish-tales",
    )
    # Synchronized fields
    assert src.name == "Ancient Irish Tales"
    assert src.title == "Ancient Irish Tales"
    assert src.publisher == "Ancient Irish Tales"
    assert src.rights_status == RightsStatusEnum.NEEDS_RIGHTS_REVIEW


def test_story_source_missing_all_identifying_labels_rejected():
    """Verify failure when no name, title, or publisher is provided."""
    with pytest.raises(ValidationError):
        StorySource(url="https://example.com/no-title")


def test_story_source_optional_license_url():
    """Verify that a source without a known license URL validates cleanly."""
    src = StorySource(
        title="Oral Family Tradition",
        publisher="Private Informant",
        url="https://example.com/field-interview",
        license_name="Informant Oral Consent",
        license_url=None,  # No license URL
    )
    assert src.license_url is None

