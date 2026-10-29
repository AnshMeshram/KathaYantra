"""Dataset Manifest, Coverage, and Data Quality Endpoints for KathaYantra."""

import sqlite3
from typing import Any
from fastapi import APIRouter, status
from app.core.config import settings
from app.repositories.candidate_repository import candidate_repository
from app.repositories.story_repository import story_repository
from app.schemas.api import DatasetQualityResponse, SingleResponse, SourceReadinessResponse
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.dataset import DatasetEnvelope
from app.schemas.manifest import DatasetManifest
from app.schemas.story import CategoryEnum
from app.services.coverage_planner import ArchiveCoverageReport, coverage_planner
from app.services.manifest_service import manifest_service
from app.services.publication_policy import PublicationPolicy

router = APIRouter(prefix="/dataset", tags=["Dataset Governance"])


@router.get(
    "/manifest",
    response_model=SingleResponse[DatasetManifest],
    status_code=status.HTTP_200_OK,
    summary="Get Canonical Dataset Manifest",
)
async def get_dataset_manifest() -> SingleResponse[DatasetManifest]:
    """Retrieve real-time computed dataset manifest with published totals, targets, and gaps."""
    manifest = manifest_service.compute_manifest()
    return SingleResponse(data=manifest)


@router.get(
    "/coverage",
    response_model=SingleResponse[ArchiveCoverageReport],
    status_code=status.HTTP_200_OK,
    summary="Get 15-Country Archive Coverage Report",
)
async def get_archive_coverage() -> SingleResponse[ArchiveCoverageReport]:
    """Retrieve detailed country-by-country and category-by-category quota coverage report."""
    report = coverage_planner.compile_coverage_report()
    return SingleResponse(data=report)


@router.get(
    "/quality",
    response_model=SingleResponse[DatasetQualityResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Data Quality and Seed File Integrity Report",
)
async def get_dataset_quality() -> SingleResponse[DatasetQualityResponse]:
    """Audit health of published records, valid seed files, staged candidates, and SQLite FTS5 index."""
    # Count valid seed files
    valid_seed_files = 0
    total_seed_files = 30
    folklore_dir = settings.folklore_seed_dir
    urban_dir = settings.urban_legends_seed_dir

    for c in SUPPORTED_COUNTRY_CODES.keys():
        for c_dir in [folklore_dir, urban_dir]:
            p = c_dir / f"{c}.json"
            if p.exists():
                try:
                    import json
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    DatasetEnvelope.model_validate(data)
                    valid_seed_files += 1
                except Exception:
                    pass

    # Published stories count from repository
    published_count = len(story_repository.list_stories(limit=1000)[0])

    # Count staged candidates
    try:
        candidates = candidate_repository.load_all_candidates()
        staged_count = len(candidates)
    except Exception:
        staged_count = 0

    # Count entries in SQLite FTS5 index
    retrieval_index_count = 0
    index_file = settings.retrieval_index_file
    if index_file.exists():
        try:
            conn = sqlite3.connect(str(index_file))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stories_fts")
            row = cursor.fetchone()
            if row:
                retrieval_index_count = row[0]
            conn.close()
        except Exception:
            pass

    return SingleResponse(
        data=DatasetQualityResponse(
            status="healthy" if valid_seed_files == total_seed_files and published_count == 300 else "degraded",
            published_records=published_count,
            seed_files_valid=valid_seed_files,
            total_seed_files=total_seed_files,
            staged_candidates_count=staged_count,
            retrieval_index_count=retrieval_index_count,
            audit_summary={
                "target_records": 300,
                "deficit": max(0, 300 - published_count),
                "is_complete": published_count >= 300,
            },
        )
    )


@router.get(
    "/quality/source-readiness",
    response_model=SingleResponse[SourceReadinessResponse],
    status_code=status.HTTP_200_OK,
    summary="Get AI Source-Readiness Audit Report",
)
async def get_source_readiness() -> SingleResponse[SourceReadinessResponse]:
    """Audit all 300 published records for AI retrieval readiness, genuine sources, and rights clearances."""
    from collections import Counter
    import json

    folklore_dir = settings.folklore_seed_dir
    urban_dir = settings.urban_legends_seed_dir

    total_records = 0
    accepted_for_ai = 0
    flagged_records = []
    issues_by_category = Counter()

    for country_code in sorted(SUPPORTED_COUNTRY_CODES.keys()):
        for cat_dir, cat_enum in [(folklore_dir, CategoryEnum.FOLKLORE), (urban_dir, CategoryEnum.URBAN_LEGEND)]:
            seed_file = cat_dir / f"{country_code}.json"
            if not seed_file.exists():
                flagged_records.append({"record_id": f"{country_code}-{cat_enum.value}", "issue": "Missing file"})
                continue

            try:
                with open(seed_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                envelope = DatasetEnvelope.model_validate(data)

                for story in envelope.records:
                    total_records += 1
                    eval_result = PublicationPolicy.evaluate_eligibility(story)
                    if not eval_result.is_eligible:
                        issues_by_category["publication_policy_failure"] += 1
                        flagged_records.append({"record_id": story.id, "issues": eval_result.violations})
                        continue

                    # Summary check
                    if len(story.summary.strip()) < 50:
                        issues_by_category["summary_too_short"] += 1
                        flagged_records.append({"record_id": story.id, "issues": ["Summary under 50 chars"]})
                        continue

                    # Source check
                    if not story.sources or not any(s.url and str(s.url).startswith(("http://", "https://")) for s in story.sources):
                        issues_by_category["invalid_sources"] += 1
                        flagged_records.append({"record_id": story.id, "issues": ["No valid HTTP sources"]})
                        continue

                    accepted_for_ai += 1
            except Exception as e:
                issues_by_category["file_parse_error"] += 1

    rate = (accepted_for_ai / total_records * 100.0) if total_records > 0 else 0.0

    return SingleResponse(
        data=SourceReadinessResponse(
            total_records_audited=total_records,
            accepted_for_ai=accepted_for_ai,
            flagged_records_count=len(flagged_records),
            acceptance_rate_percent=round(rate, 2),
            status="pass" if len(flagged_records) == 0 else "needs_remediation",
            issues_by_category=dict(issues_by_category),
        )
    )
