"""Tests for KathaYantra Phase 4: World Folklore Data Acquisition, Source Verification,
Curatorial Workflows, and Dataset Quota Coverage.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import pytest

from app.curation.helpers import create_curated_record
from app.curation.registry import (
    ALL_CURATED_RECORDS,
    get_all_curated_records,
    get_curated_record_by_id,
    get_curated_records_for_country,
)
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.import_candidate import (
    CandidateDispositionEnum,
    ImportCandidate,
)
from app.schemas.source import RightsStatusEnum, StorySource
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
)
from app.services.coverage_planner import (
    ArchiveCoverageReport,
    CountryCoverageSummary,
    CoveragePlanner,
    coverage_planner,
)
from app.services.curation_service import CurationService
from app.services.publication_policy import PublicationEligibilityResult, PublicationPolicy
from app.services.source_verification import SourceInspectionItem, SourceVerificationResult, SourceVerificationService
from app.services.summary_builder import StructuredSummary, SummaryBuilder


# ==============================================================================
# 1. Source Verification Service Tests
# ==============================================================================


def test_source_verification_valid_story():
    """Verify that a properly sourced and attributed story passes source verification."""
    service = SourceVerificationService()
    record = ALL_CURATED_RECORDS[0]  # First verified record (BR-FOLK-001)

    result = service.verify_story_record(record)
    assert isinstance(result, SourceVerificationResult)
    assert result.is_verified is True
    assert result.narrative_valid is True
    assert result.cultural_attribution_valid is True
    assert result.rights_cleared is True
    assert result.sources_verified is True
    assert len(result.source_inspections) >= 1
    assert result.source_inspections[0].url_valid is True
    assert result.source_inspections[0].attribution_satisfied is True


def test_source_verification_invalid_url():
    """Verify that non-HTTP/HTTPS URLs or missing URLs are caught by verification."""
    service = SourceVerificationService()
    # Construct StorySource bypassing pydantic validator to test verification logic
    bad_source = StorySource.model_construct(
        id="src_bad",
        title="Bogus Archive",
        name="Bogus Archive",
        publisher="Bogus Org",
        url="ftp://invalid.example.com",
        rights_status=RightsStatusEnum.APPROVED,
        attribution_required=True,
        attribution_text="Source: Bogus",
    )
    bad_story = StoryRecord(
        id="IN-FOLK-999",
        country_code="IN",
        category=CategoryEnum.FOLKLORE,
        title="Invalid Source Tale",
        summary="A traditional tale documented with an invalid source URL that should fail verification checks.",
        sources=[bad_source],
        verification_status=VerificationStatusEnum.NEEDS_REVIEW,
        rights_status=RightsStatusEnum.APPROVED,
        region_or_community="Assam",
        attribution_text="Source: Bogus",
    )

    result = service.verify_story_record(bad_story)
    assert result.is_verified is False
    assert result.sources_verified is False
    assert any("URL" in finding for finding in result.findings)


def test_source_verification_missing_cultural_attribution():
    """Verify that missing cultural community or region flags an issue."""
    service = SourceVerificationService()
    source = StorySource(
        name="Valid Source",
        url="https://example.org/test",
        rights_status=RightsStatusEnum.APPROVED,
        attribution_text="Source: Valid",
    )
    story = StoryRecord(
        id="IN-FOLK-998",
        country_code="IN",
        category=CategoryEnum.FOLKLORE,
        title="Cultureless Tale",
        summary="A tale with a valid source and approval status but completely omitted cultural community or region.",
        sources=[source],
        verification_status=VerificationStatusEnum.VERIFIED,
        rights_status=RightsStatusEnum.APPROVED,
        region_or_community=None,
        community_attributions=[],
        attribution_text="Source: Valid",
    )

    result = service.verify_story_record(story)
    assert result.is_verified is False
    assert result.cultural_attribution_valid is False
    assert any("cultural attribution" in finding.lower() for finding in result.findings)


def test_narrative_validity_anti_hallucination():
    """Verify narrative validity check detects AI boilerplate and rejection triggers."""
    service = SourceVerificationService()

    valid, findings = service.check_narrative_validity(
        "In traditional folklore, ancestral guardian spirits are believed to protect the mountain passes from malevolent winter storms."
    )
    assert valid is True
    assert len(findings) == 0

    invalid, ai_findings = service.check_narrative_validity(
        "As an AI, I am pleased to tell you a folklore story about a ghost in the ancient forest."
    )
    assert invalid is False
    assert any("as an ai" in f.lower() for f in ai_findings)


# ==============================================================================
# 2. Summary Builder & Verification Tests
# ==============================================================================


def test_summary_builder_validation():
    """Verify SummaryBuilder rejects summaries that are too short, have AI boilerplate, or lack substance."""
    builder = SummaryBuilder()

    # Too short
    short_val = builder.build_summary(title="Ghost", summary_text="Short tale of ghosts.")
    assert short_val.is_valid is False
    assert any("short" in issue.lower() for issue in short_val.issues)

    # AI boilerplate
    ai_val = builder.build_summary(
        title="Spirit",
        summary_text="As an AI, I cannot provide folklore, but here is a story about a spirit that wanders the village at night.",
    )
    assert ai_val.is_valid is False
    assert any("synthetic" in issue.lower() or "ai" in issue.lower() for issue in ai_val.issues)

    # Valid summary
    valid_text = (
        "In the remote hills of Assam, villagers speak of the Burhi Aai, an ancient ancestral guardian "
        "who warns travelers when sudden monsoons approach and guides lost wanderers toward safe shelters. "
        "Documented in regional oral folklore compilations during the late colonial period."
    )
    valid_val = builder.build_summary(title="Burhi Aai", summary_text=valid_text)
    assert valid_val.is_valid is True
    assert valid_val.word_count >= 20


def test_summary_builder_composition():
    """Verify compose_original_summary formatting retains narrative core and cultural context."""
    builder = SummaryBuilder()
    summary = builder.compose_original_summary(
        title="The Flying Dutchman",
        setting="the Cape of Good Hope",
        key_figures=["Captain Hendrick van der Decken", "his doomed crew"],
        narrative_arc="A spectral ship sails against a violent gale, forever barred from port after its captain swore a defiant oath.",
        cultural_significance="A cornerstone of 17th-century European maritime lore passed down through generations of sailors.",
    )
    assert "Originating in the Cape of Good Hope" in summary
    assert "Flying Dutchman" in summary
    assert "spectral ship" in summary
    assert "maritime lore" in summary


# ==============================================================================
# 3. Curation Service Tests
# ==============================================================================


def test_curation_service_candidate_review_and_promotion(tmp_path: Path):
    """Verify that CurationService can inspect candidates, review them, and promote to StoryRecord."""
    batches_dir = tmp_path / "batches"
    batches_dir.mkdir()
    repo = CandidateRepository(storage_dir=batches_dir)

    candidate = ImportCandidate(
        candidate_id="CAND-TEST-001",
        import_batch_id="test_batch_01",
        source_registry_id="national_folklore",
        raw_title="The Banshee of Munster",
        raw_nation="Ireland",
        raw_url="https://archive.example.org/tales/001",
        raw_text_available=True,
        rights_status=RightsStatusEnum.APPROVED,
        verification_status=VerificationStatusEnum.NEEDS_REVIEW,
        proposed_country_code="IE",
        proposed_category=CategoryEnum.FOLKLORE,
        disposition=CandidateDispositionEnum.NEW_CANDIDATE,
    )
    repo.save_batch(
        batch_id="test_batch_01",
        candidates=[candidate],
        batch_metadata={"source": "test"},
    )

    service = CurationService(repository=repo)
    queue = service.get_review_queue()
    assert len(queue) == 1
    assert queue[0].candidate_id == "CAND-TEST-001"

    # Review and approve
    test_summary = (
        "A traditional Bean Sidhe narrative describing the herald of death in Gaelic family lore "
        "across ancient Munster households, warning inhabitants of approaching loss with mournful laments."
    )
    reviewed = service.review_candidate(
        candidate_id="CAND-TEST-001",
        curator="curator_test",
        approved=True,
        notes="Authentic Irish oral tradition with verified public domain provenance.",
        rights_status=RightsStatusEnum.APPROVED,
        proposed_summary=test_summary,
    )
    assert reviewed is not None
    assert reviewed.disposition == CandidateDispositionEnum.APPROVED_FOR_PUBLICATION
    assert reviewed.verification_status == VerificationStatusEnum.VERIFIED

    # Promote to story
    source = StorySource(
        name="National Folklore Archive",
        url="https://archive.example.org/tales/001",
        rights_status=RightsStatusEnum.APPROVED,
        attribution_text="Source: National Folklore Archive",
    )
    story = service.promote_candidate_to_story(
        candidate=reviewed,
        story_id="IE-FOLK-001",
        summary=test_summary,
        sources=[source],
        region_or_community="Munster",
        attribution_text="Source: National Folklore Archive",
    )
    assert story.id == "IE-FOLK-001"
    assert story.country_code == "IE"
    assert story.category == CategoryEnum.FOLKLORE
    assert story.rights_status == RightsStatusEnum.APPROVED
    assert story.verification_status == VerificationStatusEnum.VERIFIED
    assert len(story.sources) == 1
    assert story.sources[0].url == "https://archive.example.org/tales/001"


# ==============================================================================
# 4. Coverage Planner Tests
# ==============================================================================


def test_coverage_planner_live_dataset():
    """Verify CoveragePlanner accurately analyzes the 300-story populated seed dataset."""
    report = coverage_planner.compile_coverage_report()
    assert isinstance(report, ArchiveCoverageReport)
    assert report.required_total_records == 300
    assert report.actual_total_records == 300
    assert report.total_deficit == 0
    assert report.completion_percentage == 100.0
    assert report.partitions_met == 30
    assert report.total_partitions == 30
    assert report.countries_fully_met == 15
    assert len(report.countries) == 15


def test_coverage_planner_markdown_generation():
    """Verify CoveragePlanner produces valid Markdown and JSON serializations."""
    md = coverage_planner.generate_markdown_report()
    assert "# KathaYantra" in md
    assert "World Folklore & Urban Legend Dataset Coverage Report" in md
    assert "300 / 300" in md
    assert "100.0%" in md

    report = coverage_planner.compile_coverage_report()
    data = report.model_dump(mode="json")
    assert data["completion_percentage"] == 100.0
    assert data["total_deficit"] == 0


# ==============================================================================
# 5. Full Archive Integrity & Publication Policy Tests (All 300 Records)
# ==============================================================================


def test_all_300_curated_records_count_and_distribution():
    """Verify that exactly 300 curated records exist across the 15 countries and 2 categories."""
    records = get_all_curated_records()
    assert len(records) == 300

    # Ensure all 15 supported countries are present
    country_counts = {}
    for country in SUPPORTED_COUNTRY_CODES:
        country_records = get_curated_records_for_country(country)
        assert len(country_records) == 20
        folklore = [r for r in country_records if r.category == CategoryEnum.FOLKLORE]
        urban = [r for r in country_records if r.category == CategoryEnum.URBAN_LEGEND]
        assert len(folklore) == 10
        assert len(urban) == 10
        country_counts[country] = len(country_records)

    assert len(country_counts) == 15


def test_all_300_records_pass_publication_policy():
    """Verify that every single one of the 300 curated records passes PublicationPolicy."""
    records = get_all_curated_records()
    failures = []

    for r in records:
        eval_result = PublicationPolicy.evaluate_eligibility(r)
        if not eval_result.is_eligible:
            failures.append((r.id, eval_result.violations))

    assert len(failures) == 0, f"Stories failed PublicationPolicy: {failures}"


def test_all_300_records_have_authentic_http_sources():
    """Verify that all 300 records have genuine HTTP/HTTPS sources and non-empty attributions."""
    records = get_all_curated_records()

    for r in records:
        assert len(r.sources) >= 1, f"Story {r.id} missing sources."
        for s in r.sources:
            assert s.url.startswith("http://") or s.url.startswith("https://"), (
                f"Story {r.id} source has invalid URL: {s.url}"
            )
            assert len(s.publisher.strip()) > 0, f"Story {r.id} source missing publisher/author."
            assert len(s.attribution_text.strip()) > 0, f"Story {r.id} source missing attribution."
        assert len(r.attribution_text.strip()) > 0, f"Story {r.id} missing record attribution."
        assert len(r.summary.strip()) >= 50, f"Story {r.id} summary is too short."


def test_get_curated_record_by_id():
    """Verify lookup helper retrieves existing stories and returns None for missing ones."""
    story = get_curated_record_by_id("IN-FOLK-001")
    assert story is not None
    assert story.id == "IN-FOLK-001"
    assert story.country_code == "IN"
    assert story.category == CategoryEnum.FOLKLORE

    missing = get_curated_record_by_id("NONEXISTENT-999")
    assert missing is None
