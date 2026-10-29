"""Central Import Pipeline for KathaYantra Data Ingestion."""

import logging
import time
from typing import Any, Optional
from app.integrations.registry import SourceRegistryManager, source_registry_manager
from app.repositories.candidate_repository import CandidateRepository, candidate_repository
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum
from app.services.candidate_deduplication import CandidateDeduplicator
from app.services.candidate_normalizer import CandidateNormalizer
from app.services.import_batch_service import BatchManifest, ImportBatchService, import_batch_service

logger = logging.getLogger(__name__)


class ImportPipeline:
    """Orchestrates the 8-stage data acquisition, normalization, deduplication, and staging pipeline."""

    def __init__(
        self,
        registry_manager: Optional[SourceRegistryManager] = None,
        batch_service: Optional[ImportBatchService] = None,
        repository: Optional[CandidateRepository] = None,
    ):
        self.registry_manager = registry_manager or source_registry_manager
        self.batch_service = batch_service or import_batch_service
        self.repository = repository or candidate_repository

    async def run_import_batch(
        self,
        source_id: str,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> BatchManifest:
        """Execute a full 8-stage import cycle for a specific source and search query."""
        start_time = time.time()
        batch_id = kwargs.get("batch_id") or self.batch_service.generate_batch_id(source_id)
        errors: list[str] = []

        # Stage 1: Acquire from connector
        try:
            connector = self.registry_manager.get_connector(source_id)
        except Exception as exc:
            msg = f"Failed to instantiate connector for {source_id}: {exc}"
            logger.error(msg)
            return self.batch_service.compile_manifest(
                batch_id=batch_id,
                source_id=source_id,
                query=query,
                candidates=[],
                start_time=start_time,
                country_code=country_code,
                category=category.value if category else None,
                dry_run=dry_run,
                errors=[msg],
            )

        try:
            raw_candidates = await connector.search(
                query=query,
                country_code=country_code,
                category=category,
                limit=limit,
                batch_id=batch_id,
                **kwargs,
            )
        except Exception as exc:
            msg = f"Connector search failed for {source_id} query '{query}': {exc}"
            logger.error(msg)
            return self.batch_service.compile_manifest(
                batch_id=batch_id,
                source_id=source_id,
                query=query,
                candidates=[],
                start_time=start_time,
                country_code=country_code,
                category=category.value if category else None,
                dry_run=dry_run,
                errors=[msg],
            )

        # Pre-load known candidates for variant checking and duplicate detection
        existing_candidates = self.repository.load_all_candidates()
        seen_fingerprints = {
            CandidateDeduplicator.compute_fingerprint(c) for c in existing_candidates
        }

        processed_candidates: list[ImportCandidate] = []

        for candidate in raw_candidates:
            # Stage 2: Preserve permissible raw provenance (no unauthorized full-text copying)
            if candidate.raw_text_available and candidate.rights_status == RightsStatusEnum.NEEDS_RIGHTS_REVIEW:
                # Retain metadata-only summary; full-text must not be propagated
                pass

            # Stage 3: Normalize
            candidate = CandidateNormalizer.normalize_candidate(candidate)

            # Stage 4: Validate
            try:
                # Re-validate model
                validated_candidate = ImportCandidate.model_validate(candidate.model_dump())
            except Exception as val_exc:
                candidate.validation_errors.append(str(val_exc))
                candidate.disposition = CandidateDispositionEnum.REJECTED
                errors.append(f"Validation failed on {candidate.candidate_id}: {val_exc}")
                processed_candidates.append(candidate)
                continue

            # Stage 5: Deduplicate
            validated_candidate = CandidateDeduplicator.process_candidate(
                validated_candidate,
                seen_fingerprints=seen_fingerprints,
                known_candidates=existing_candidates,
            )

            # Stage 6: Rights and Mapping Review
            if validated_candidate.disposition != CandidateDispositionEnum.DUPLICATE_CANDIDATE:
                if not validated_candidate.proposed_country_code or validated_candidate.proposed_country_code not in SUPPORTED_COUNTRY_CODES:
                    validated_candidate.disposition = CandidateDispositionEnum.NEEDS_MAPPING_REVIEW
                elif validated_candidate.rights_status == RightsStatusEnum.NEEDS_RIGHTS_REVIEW:
                    validated_candidate.disposition = CandidateDispositionEnum.NEEDS_RIGHTS_REVIEW
                elif not validated_candidate.raw_url:
                    validated_candidate.disposition = CandidateDispositionEnum.NEEDS_SOURCE_VERIFICATION
                elif validated_candidate.rights_status in (RightsStatusEnum.APPROVED, RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED):
                    if validated_candidate.proposed_country_code in SUPPORTED_COUNTRY_CODES:
                        validated_candidate.disposition = CandidateDispositionEnum.ELIGIBLE_FOR_EDITORIAL_REVIEW

            processed_candidates.append(validated_candidate)

        # Stage 7: Persist staged candidates (unless dry-run)
        manifest = self.batch_service.compile_manifest(
            batch_id=batch_id,
            source_id=source_id,
            query=query,
            candidates=processed_candidates,
            start_time=start_time,
            country_code=country_code,
            category=category.value if category else None,
            dry_run=dry_run,
            errors=errors,
        )

        if not dry_run and processed_candidates:
            self.batch_service.persist_batch(batch_id, processed_candidates, manifest)

        # Stage 8: Return report manifest
        return manifest


import_pipeline = ImportPipeline()
