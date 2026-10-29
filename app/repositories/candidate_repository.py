"""Repository for Persisting and Querying Staged Import Candidates in data/processed/candidates/."""

import json
from pathlib import Path
from typing import Any, Optional
from app.core.config import settings
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.story import CategoryEnum


class CandidateRepository:
    """Manages file-based storage and query operations for staged import candidates."""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or settings.candidates_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _batch_file_path(self, batch_id: str) -> Path:
        sanitized = batch_id.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{sanitized}.jsonl"

    def _manifest_file_path(self, batch_id: str) -> Path:
        sanitized = batch_id.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{sanitized}.meta.json"

    def save_batch(
        self,
        batch_id: str,
        candidates: list[ImportCandidate],
        batch_metadata: Optional[dict[str, Any]] = None,
    ) -> Path:
        """Atomically persist a list of ImportCandidates and batch manifest."""
        batch_path = self._batch_file_path(batch_id)
        temp_path = self.storage_dir / f".tmp_{batch_path.name}"

        with open(temp_path, "w", encoding="utf-8") as f:
            for cand in candidates:
                line = json.dumps(cand.model_dump(mode="json"), ensure_ascii=False)
                f.write(line + "\n")

        temp_path.replace(batch_path)

        # Write manifest metadata
        if batch_metadata:
            meta_path = self._manifest_file_path(batch_id)
            meta_temp = self.storage_dir / f".tmp_{meta_path.name}"
            with open(meta_temp, "w", encoding="utf-8") as f:
                json.dump(batch_metadata, f, indent=2, ensure_ascii=False)
            meta_temp.replace(meta_path)

        return batch_path

    def load_batch(self, batch_id: str) -> list[ImportCandidate]:
        """Load all ImportCandidates belonging to a specific import batch."""
        batch_path = self._batch_file_path(batch_id)
        if not batch_path.exists():
            return []

        candidates: list[ImportCandidate] = []
        with open(batch_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    try:
                        data = json.loads(stripped)
                        candidates.append(ImportCandidate.model_validate(data))
                    except Exception:
                        continue
        return candidates

    def get_batch_metadata(self, batch_id: str) -> Optional[dict[str, Any]]:
        """Retrieve batch summary metadata."""
        meta_path = self._manifest_file_path(batch_id)
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_all_batches(self) -> list[dict[str, Any]]:
        """List all staged import batch manifests in storage directory."""
        batches: list[dict[str, Any]] = []
        for meta_file in sorted(self.storage_dir.glob("*.meta.json")):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    batches.append(json.load(f))
            except Exception:
                continue
        return batches

    def load_all_candidates(self) -> list[ImportCandidate]:
        """Load all staged candidates across all batch files."""
        candidates: list[ImportCandidate] = []
        for batch_file in self.storage_dir.glob("*.jsonl"):
            with open(batch_file, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        try:
                            data = json.loads(stripped)
                            candidates.append(ImportCandidate.model_validate(data))
                        except Exception:
                            continue
        return candidates

    def query(
        self,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        disposition: Optional[CandidateDispositionEnum] = None,
        source_id: Optional[str] = None,
    ) -> list[ImportCandidate]:
        """Query staged candidates with optional filters."""
        all_cands = self.load_all_candidates()
        results: list[ImportCandidate] = []

        for cand in all_cands:
            if country_code and cand.proposed_country_code != country_code.upper():
                continue
            if category and cand.proposed_category != category:
                continue
            if disposition and cand.disposition != disposition:
                continue
            if source_id and cand.source_registry_id != source_id:
                continue
            results.append(cand)

        return results


candidate_repository = CandidateRepository()
