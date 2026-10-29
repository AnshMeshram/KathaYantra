"""Batch Execution and Manifest Tracking Service for KathaYantra Ingestion."""

from datetime import datetime, timezone
import time
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.repositories.candidate_repository import CandidateRepository, candidate_repository
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate


class BatchManifest(BaseModel):
    """Detailed metadata tracking a single data acquisition run."""

    batch_id: str
    source_id: str
    query: str
    country_code: Optional[str] = None
    category: Optional[str] = None
    start_time: str
    finish_time: str
    duration_seconds: float
    retrieved_count: int = 0
    normalized_count: int = 0
    accepted_count: int = 0
    rejected_count: int = 0
    duplicate_count: int = 0
    rights_pending_count: int = 0
    mapping_review_count: int = 0
    source_verification_count: int = 0
    error_count: int = 0
    output_file: Optional[str] = None
    dry_run: bool = False
    errors: list[str] = Field(default_factory=list)


class ImportBatchService:
    """Orchestrates batch creation, execution tracking, and manifest writing."""

    def __init__(self, repository: Optional[CandidateRepository] = None):
        self.repository = repository or candidate_repository

    @staticmethod
    def generate_batch_id(source_id: str) -> str:
        """Create a timestamped, traceable batch identifier."""
        clean_source = source_id.replace("_", "-")
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"batch-{clean_source}-{ts}"

    def compile_manifest(
        self,
        batch_id: str,
        source_id: str,
        query: str,
        candidates: list[ImportCandidate],
        start_time: float,
        country_code: Optional[str] = None,
        category: Optional[str] = None,
        dry_run: bool = False,
        errors: Optional[list[str]] = None,
    ) -> BatchManifest:
        """Calculate exact disposition breakdown from candidate list."""
        finish_time = time.time()
        start_dt = datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat()
        finish_dt = datetime.fromtimestamp(finish_time, tz=timezone.utc).isoformat()

        dup_count = sum(1 for c in candidates if c.disposition == CandidateDispositionEnum.DUPLICATE_CANDIDATE)
        rights_count = sum(1 for c in candidates if c.disposition == CandidateDispositionEnum.NEEDS_RIGHTS_REVIEW)
        mapping_count = sum(1 for c in candidates if c.disposition == CandidateDispositionEnum.NEEDS_MAPPING_REVIEW)
        source_count = sum(1 for c in candidates if c.disposition == CandidateDispositionEnum.NEEDS_SOURCE_VERIFICATION)
        rejected_count = sum(1 for c in candidates if c.disposition == CandidateDispositionEnum.REJECTED)

        # Accepted count are candidates staged for editorial review or new
        accepted_count = sum(
            1
            for c in candidates
            if c.disposition
            in (
                CandidateDispositionEnum.NEW_CANDIDATE,
                CandidateDispositionEnum.ELIGIBLE_FOR_EDITORIAL_REVIEW,
                CandidateDispositionEnum.APPROVED_FOR_PUBLICATION,
            )
        )

        output_filename = f"{batch_id}.jsonl" if not dry_run else None

        return BatchManifest(
            batch_id=batch_id,
            source_id=source_id,
            query=query,
            country_code=country_code,
            category=category,
            start_time=start_dt,
            finish_time=finish_dt,
            duration_seconds=round(finish_time - start_time, 3),
            retrieved_count=len(candidates),
            normalized_count=len(candidates),
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            duplicate_count=dup_count,
            rights_pending_count=rights_count,
            mapping_review_count=mapping_count,
            source_verification_count=source_count,
            error_count=len(errors or []),
            output_file=output_filename,
            dry_run=dry_run,
            errors=errors or [],
        )

    def persist_batch(
        self,
        batch_id: str,
        candidates: list[ImportCandidate],
        manifest: BatchManifest,
    ) -> Optional[str]:
        """Save candidates and manifest metadata using the repository."""
        if manifest.dry_run:
            return None
        path = self.repository.save_batch(batch_id, candidates, manifest.model_dump())
        return str(path)


import_batch_service = ImportBatchService()
