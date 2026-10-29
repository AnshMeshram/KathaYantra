"""Tests for Canonical StoryRecord Schema Extensions (Phase 2)."""

from pydantic import ValidationError
import pytest
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.source import RightsStatusEnum, StorySource
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
    generate_slug,
)


def sample_story_source(url="https://www.gutenberg.org/ebooks/7128"):
    return StorySource(
        title="Indian Fairy Tales",
        publisher="David Nutt",
        url=url,
        license_name="Public Domain in the USA",
        rights_status=RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED,
    )


def test_valid_phase2_story_record():
    """Verify that a story record with all Phase 2 canonical fields validates cleanly."""
    story = StoryRecord(
        id="IN-FOLK-001",
        title="The Demon with the Matted Hair",
        country_code="IN",
        category=CategoryEnum.FOLKLORE,
        subtype="jataka_tale",
        summary="Prince Brahmadatta overcomes the demon Sticky-Hair through fearlessness and moral resolve.",
        long_description="In the realm of Magadha, the Bodhisatta was born as Prince Brahmadatta...",
        alternate_names=["Pancasavudha Jataka", "Jataka 55"],
        language="en",
        alternate_languages=["pi", "sa"],
        motifs=["G510.4", "D1654.4.1"],
        themes=["courage", "demon", "buddhist_moral"],
        historical_period="Classical Ancient India (circa 4th century BCE)",
        region_or_community="Varanasi / Magadha",
        community_attributions=["Buddhist Jataka Tradition", "Ancient Gangetic Plain"],
        geographic_associations=["Varanasi", "Rajgir"],
        variant_notes="Parallels exist in Southeast Asian Buddhist mural cycles.",
        related_record_ids=[],
        sources=[sample_story_source()],
        source_type="public_domain_anthology",
        license="Public Domain in the United States",
        rights_status=RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED,
        verification_status=VerificationStatusEnum.VERIFIED,
        content_origin=ContentOriginEnum.PUBLIC_DOMAIN_SOURCE,
    )

    assert story.schema_version == "2.0.0"
    assert story.record_version == "1.0.0"
    assert story.slug == "the-demon-with-the-matted-hair"
    assert story.country_code == "IN"
    assert story.category == CategoryEnum.FOLKLORE


def test_country_and_category_prefix_mismatch():
    """Verify that StoryRecord rejects ID prefix mismatches with country_code and category."""
    # Country mismatch
    with pytest.raises(ValidationError) as exc:
        StoryRecord(
            id="US-FOLK-001",  # US prefix
            title="Valid Title Here",
            country_code="IN",  # IN country
            category=CategoryEnum.FOLKLORE,
            summary="A valid summary of adequate length for testing purposes.",
            sources=[sample_story_source()],
        )
    assert "does not match country_code" in str(exc.value)

    # Category mismatch: -FOLK- id with urban_legend category
    with pytest.raises(ValidationError) as exc:
        StoryRecord(
            id="IN-FOLK-001",
            title="Valid Title Here",
            country_code="IN",
            category=CategoryEnum.URBAN_LEGEND,  # Mismatched category
            summary="A valid summary of adequate length for testing purposes.",
            sources=[sample_story_source()],
        )
    assert "must contain '-URBAN-'" in str(exc.value)

    # Category mismatch: -URBAN- id with folklore category
    with pytest.raises(ValidationError) as exc:
        StoryRecord(
            id="IN-URBAN-001",
            title="Valid Title Here",
            country_code="IN",
            category=CategoryEnum.FOLKLORE,  # Mismatched category
            summary="A valid summary of adequate length for testing purposes.",
            sources=[sample_story_source()],
        )
    assert "must contain '-FOLK-'" in str(exc.value)


def test_rejection_of_ai_generated_fiction_in_story_record():
    """Verify that StoryRecord strictly rejects content_origin == ai_generated_fiction."""
    with pytest.raises(ValidationError) as exc:
        StoryRecord(
            id="IN-FOLK-002",
            title="A Machine Tale",
            country_code="IN",
            category=CategoryEnum.FOLKLORE,
            summary="A generated tale about a mechanical monster in a village.",
            sources=[sample_story_source()],
            content_origin=ContentOriginEnum.AI_GENERATED_FICTION,
        )
    assert "AI-generated fiction cannot be saved as an authentic StoryRecord" in str(exc.value)


def test_slug_generation_and_unicode_handling():
    """Verify that titles with Unicode characters, accents, and punctuation generate clean slugs."""
    assert generate_slug("The Yōkai of Mount Hiei") == "the-yōkai-of-mount-hiei"
    assert generate_slug("La Llorona (The Weeping Woman)") == "la-llorona-the-weeping-woman"
    assert generate_slug("Saci-Pererê's Whistle") == "saci-pererês-whistle"


def test_duplicate_source_urls_in_citations_rejected():
    """Verify that a StoryRecord containing duplicate source URLs fails validation."""
    with pytest.raises(ValidationError) as exc:
        StoryRecord(
            id="IN-FOLK-003",
            title="Duplicate Source Story",
            country_code="IN",
            category=CategoryEnum.FOLKLORE,
            summary="A valid summary for testing duplicate source validation.",
            sources=[
                sample_story_source(url="https://example.com/source1"),
                sample_story_source(url="https://example.com/source1"),  # Duplicate
            ],
        )
    assert "contains duplicate source URLs" in str(exc.value)
