"""Tests for KathaYantra Pydantic Schemas and Data Validation."""

from datetime import datetime, timezone
from pydantic import ValidationError
import pytest
from app.schemas.country import CountryRecord, SUPPORTED_COUNTRY_CODES
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    CountrySeedFile,
    RightsStatusEnum,
    StoryRecord,
    StorySource,
    VerificationStatusEnum,
    validate_web_url,
)


def create_sample_story(
    story_id="IN-FOLK-001",
    country_code="IN",
    category=CategoryEnum.FOLKLORE,
    rights_status=RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED,
    sources=None,
) -> StoryRecord:
    """Helper creating a valid StoryRecord fixture."""
    if sources is None:
        sources = [
            StorySource(
                name="Indian Fairy Tales (Joseph Jacobs)",
                url="https://www.gutenberg.org/ebooks/7128",
                source_type="public_domain_book",
                access_date="2026-10-29",
            )
        ]
    return StoryRecord(
        id=story_id,
        title="The Demon with the Matted Hair",
        country_code=country_code,
        region_or_community="Varanasi / Buddhist Jataka Tradition",
        category=category,
        subtype="jataka_tale",
        summary="Prince Brahmadatta faces a giant demon whose fur traps weapons; the prince overcomes him through fearlessness.",
        sources=sources,
        source_type="anthology",
        license="Public Domain in the United States",
        rights_status=rights_status,
        verification_status=VerificationStatusEnum.VERIFIED,
        content_origin=ContentOriginEnum.PUBLIC_DOMAIN_SOURCE,
        canonical_url="https://www.gutenberg.org/ebooks/7128",
    )


def test_country_code_validation():
    """Test 4: Country code validation across the 15 supported countries."""
    # All 15 supported countries pass
    for code, name in SUPPORTED_COUNTRY_CODES.items():
        rec = CountryRecord(
            code=code,
            name=name,
            region="Test Region",
        )
        assert rec.code == code

    # Invalid country codes fail
    with pytest.raises(ValidationError) as exc:
        CountryRecord(
            code="ZZ",
            name="Unknown Country",
            region="Fantasy",
        )
    assert "not one of the 15 supported countries" in str(exc.value)

    with pytest.raises(ValidationError):
        CountryRecord(code="USA", name="United States", region="North America")


def test_invalid_story_categories():
    """Test 5: Story category must be either folklore or urban_legend."""
    # Valid categories
    folk_story = create_sample_story(category=CategoryEnum.FOLKLORE)
    assert folk_story.category == CategoryEnum.FOLKLORE

    urban_story = create_sample_story(
        story_id="IN-URBAN-001",
        category=CategoryEnum.URBAN_LEGEND,
    )
    assert urban_story.category == CategoryEnum.URBAN_LEGEND

    # Invalid categories fail
    with pytest.raises(ValidationError):
        create_sample_story(category="fairy_tale")

    with pytest.raises(ValidationError):
        create_sample_story(category="conspiracy_theory")


def test_missing_source_urls():
    """Test 6: Missing source URLs or empty sources list causes validation failure."""
    # Empty sources list fails
    with pytest.raises(ValidationError) as exc:
        create_sample_story(sources=[])
    assert "sources" in str(exc.value)

    # Source without URL fails
    with pytest.raises(ValidationError):
        StorySource(name="Oral Citation", url="")


def test_invalid_source_url_formats():
    """Test 7: Invalid source URL formats fail validation."""
    # Invalid schemes (e.g. ftp, file, javascript)
    with pytest.raises(ValueError):
        validate_web_url("ftp://example.com/story")

    with pytest.raises(ValueError):
        validate_web_url("javascript:alert(1)")

    # Missing netloc / invalid format
    with pytest.raises(ValueError):
        validate_web_url("https://")

    with pytest.raises(ValueError):
        validate_web_url("not_a_valid_url")

    # In StorySource model
    with pytest.raises(ValidationError):
        StorySource(name="Invalid Source", url="invalid-url-string")


def test_duplicate_record_ids():
    """Test 8: Detecting duplicate record IDs in a seed file."""
    story1 = create_sample_story(story_id="IN-FOLK-001")
    story2 = create_sample_story(story_id="IN-FOLK-001")  # Duplicate ID

    seed_file = CountrySeedFile(
        country_code="IN",
        category=CategoryEnum.FOLKLORE,
        records=[story1, story2],
    )

    ids = [r.id for r in seed_file.records]
    has_duplicates = len(ids) != len(set(ids))
    assert has_duplicates is True


def test_missing_or_invalid_rights_status():
    """Test 9: Missing or invalid rights status validation."""
    # Default rights status is needs_rights_review
    story = StoryRecord(
        id="US-FOLK-001",
        title="Rip Van Winkle",
        country_code="US",
        category=CategoryEnum.FOLKLORE,
        summary="A villager falls asleep in the Catskill Mountains and awakes twenty years later.",
        sources=[StorySource(name="The Sketch Book", url="https://www.gutenberg.org/ebooks/2048")],
    )
    assert story.rights_status == RightsStatusEnum.NEEDS_RIGHTS_REVIEW

    # Invalid rights status string fails
    with pytest.raises(ValidationError):
        StoryRecord(
            id="US-FOLK-002",
            title="The Legend of Sleepy Hollow",
            country_code="US",
            category=CategoryEnum.FOLKLORE,
            summary="Ichabod Crane encounters the Headless Horseman in Sleepy Hollow.",
            sources=[StorySource(name="The Sketch Book", url="https://www.gutenberg.org/ebooks/2048")],
            rights_status="totally_free_to_use",
        )

