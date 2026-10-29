"""Tests for Publication Eligibility Policy Service (Phase 2)."""

import pytest
from app.schemas.source import RightsStatusEnum, StorySource
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
)
from app.services.publication_policy import publication_policy


def create_candidate_record(
    verification=VerificationStatusEnum.VERIFIED,
    rights=RightsStatusEnum.APPROVED,
    long_desc="A detailed narrative text.",
    summary="A complete and rich summary describing the narrative in detail.",
    attribution=None,
    source_attribution_required=False,
) -> StoryRecord:
    src = StorySource(
        title="Verified Folk Anthology",
        publisher="National Folklore Society",
        url="https://example.com/source",
        license_name="Open Culture",
        rights_status=rights,
        attribution_required=source_attribution_required,
        attribution_text=attribution,
    )
    return StoryRecord(
        id="IN-FOLK-001",
        title="The Serpent's Jewel",
        country_code="IN",
        category=CategoryEnum.FOLKLORE,
        summary=summary,
        long_description=long_desc,
        sources=[src],
        verification_status=verification,
        rights_status=rights,
        content_origin=ContentOriginEnum.PUBLIC_DOMAIN_SOURCE,
        attribution_text=attribution,
    )


def test_fully_cleared_story_is_eligible():
    """Verify that a verified story with approved rights passes publication policy."""
    rec = create_candidate_record(
        verification=VerificationStatusEnum.VERIFIED,
        rights=RightsStatusEnum.APPROVED,
    )
    result = publication_policy.evaluate_eligibility(rec)
    assert result.is_eligible is True
    assert result.publication_tier == "full_text"
    assert len(result.violations) == 0


def test_metadata_only_without_full_text_is_eligible():
    """Verify that a metadata_only record with no long_description is eligible under metadata tier."""
    rec = create_candidate_record(
        verification=VerificationStatusEnum.VERIFIED,
        rights=RightsStatusEnum.METADATA_ONLY,
        long_desc=None,  # No full text
    )
    result = publication_policy.evaluate_eligibility(rec)
    assert result.is_eligible is True
    assert result.publication_tier == "metadata_only"


def test_metadata_only_with_full_text_is_blocked():
    """Verify that a metadata_only record containing full-text is blocked from publication."""
    rec = create_candidate_record(
        verification=VerificationStatusEnum.VERIFIED,
        rights=RightsStatusEnum.METADATA_ONLY,
        long_desc="This is restricted copyrighted text that should not be published.",
    )
    result = publication_policy.evaluate_eligibility(rec)
    assert result.is_eligible is False
    assert any("metadata_only" in v and "long_description" in v for v in result.violations)


def test_unverified_record_is_blocked():
    """Verify that an unverified record (needs_review or rejected) is blocked."""
    rec_review = create_candidate_record(verification=VerificationStatusEnum.NEEDS_REVIEW)
    res_review = publication_policy.evaluate_eligibility(rec_review)
    assert res_review.is_eligible is False
    assert any("needs_review" in v for v in res_review.violations)

    rec_reject = create_candidate_record(verification=VerificationStatusEnum.REJECTED)
    res_reject = publication_policy.evaluate_eligibility(rec_reject)
    assert res_reject.is_eligible is False
    assert any("rejected" in v for v in res_reject.violations)


def test_restricted_rights_cannot_be_bypassed_by_verification():
    """Verify that changing verification status to verified does NOT bypass rights restrictions."""
    for restricted_rights in (
        RightsStatusEnum.NEEDS_RIGHTS_REVIEW,
        RightsStatusEnum.PERMISSION_REQUIRED,
        RightsStatusEnum.RESTRICTED,
        RightsStatusEnum.UNKNOWN,
    ):
        rec = create_candidate_record(
            verification=VerificationStatusEnum.VERIFIED,
            rights=restricted_rights,
        )
        res = publication_policy.evaluate_eligibility(rec)
        assert res.is_eligible is False
        assert any("prohibits public dissemination" in v for v in res.violations)


def test_missing_mandatory_attribution_is_blocked():
    """Verify that a source requiring attribution blocks publication if attribution is missing."""
    rec = create_candidate_record(
        verification=VerificationStatusEnum.VERIFIED,
        rights=RightsStatusEnum.APPROVED,
        source_attribution_required=True,
        attribution=None,  # Missing mandatory attribution!
    )
    res = publication_policy.evaluate_eligibility(rec)
    assert res.is_eligible is False
    assert any("requires explicit attribution" in v for v in res.violations)

