"""Tests for Country Dataset Envelope Schema and Partition Integrity (Phase 2)."""

from pydantic import ValidationError
import pytest
from app.schemas.dataset import DatasetEnvelope, DatasetMetadata
from app.schemas.source import RightsStatusEnum, StorySource
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
)


def create_test_story(
    story_id="IN-FOLK-001",
    country_code="IN",
    category=CategoryEnum.FOLKLORE,
) -> StoryRecord:
    return StoryRecord(
        id=story_id,
        title="Sample Tale",
        country_code=country_code,
        category=category,
        summary="A sample verified folklore story summary of sufficient length.",
        sources=[
            StorySource(
                title="Historical Anthology",
                publisher="National Archive",
                url="https://example.com/source",
                license_name="Public Domain",
                rights_status=RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED,
            )
        ],
        verification_status=VerificationStatusEnum.VERIFIED,
        rights_status=RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED,
        content_origin=ContentOriginEnum.PUBLIC_DOMAIN_SOURCE,
    )


def test_valid_empty_dataset_envelope():
    """Verify that a canonical empty dataset envelope validates cleanly."""
    envelope = DatasetEnvelope(
        schema_version="2.0.0",
        dataset_id="IN-folklore",
        country_code="IN",
        category=CategoryEnum.FOLKLORE,
        records=[],
        metadata=DatasetMetadata(target_count=10),
    )

    assert envelope.schema_version == "2.0.0"
    assert envelope.dataset_id == "IN-folklore"
    assert envelope.metadata.actual_record_count == 0
    assert envelope.metadata.total_records == 0


def test_country_mismatch_between_envelope_and_record_rejected():
    """Verify that a dataset envelope rejects records from a different country."""
    # US record inside IN envelope
    us_record = create_test_story(
        story_id="US-FOLK-001",
        country_code="US",
        category=CategoryEnum.FOLKLORE,
    )

    with pytest.raises(ValidationError) as exc:
        DatasetEnvelope(
            schema_version="2.0.0",
            dataset_id="IN-folklore",
            country_code="IN",
            category=CategoryEnum.FOLKLORE,
            records=[us_record],
        )
    assert "does not match envelope 'IN'" in str(exc.value)


def test_category_mismatch_between_envelope_and_record_rejected():
    """Verify that a dataset envelope rejects records from a different category."""
    # Urban legend record inside folklore envelope
    urban_record = create_test_story(
        story_id="IN-URBAN-001",
        country_code="IN",
        category=CategoryEnum.URBAN_LEGEND,
    )

    with pytest.raises(ValidationError) as exc:
        DatasetEnvelope(
            schema_version="2.0.0",
            dataset_id="IN-folklore",
            country_code="IN",
            category=CategoryEnum.FOLKLORE,
            records=[urban_record],
        )
    assert "does not match envelope 'folklore'" in str(exc.value)


def test_duplicate_record_ids_inside_envelope_rejected():
    """Verify that duplicate record IDs within the same envelope file are rejected."""
    rec1 = create_test_story(story_id="IN-FOLK-001")
    rec2 = create_test_story(story_id="IN-FOLK-001")  # Duplicate ID

    with pytest.raises(ValidationError) as exc:
        DatasetEnvelope(
            schema_version="2.0.0",
            dataset_id="IN-folklore",
            country_code="IN",
            category=CategoryEnum.FOLKLORE,
            records=[rec1, rec2],
        )
    assert "Duplicate record ID 'IN-FOLK-001'" in str(exc.value)


def test_actual_record_count_dynamically_calculated():
    """Verify that actual_record_count in metadata synchronizes with len(records)."""
    rec1 = create_test_story(story_id="IN-FOLK-001")
    rec2 = create_test_story(story_id="IN-FOLK-002")

    envelope = DatasetEnvelope(
        schema_version="2.0.0",
        country_code="IN",
        category=CategoryEnum.FOLKLORE,
        records=[rec1, rec2],
    )

    assert envelope.metadata.actual_record_count == 2
    assert envelope.metadata.total_records == 2
