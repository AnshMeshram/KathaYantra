"""Quarantined Raw Folktales CSV Importer for KathaYantra."""

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Optional
from app.core.config import settings
from app.integrations.base import BaseConnector, PayloadValidationError
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class CSVFolktalesImporter(BaseConnector):
    """Imports candidate metadata from the quarantined folk_tales_deduplicated.csv without publishing unlicensed full text."""

    EXPECTED_COLUMNS = {"source", "nation", "title", "text"}

    def __init__(
        self,
        source_id: str = "fairytalez_raw_corpus",
        registry_item: Optional[SourceRegistryItem] = None,
        csv_path: Optional[Path] = None,
        mapping_file: Optional[Path] = None,
    ):
        super().__init__(source_id, registry_item)
        self.csv_path = csv_path or (settings.RAW_DIR / "folk_tales_deduplicated.csv")
        self.mapping_file = mapping_file or (settings.MANIFESTS_DIR / "nation_mapping_review.json")
        self._nation_map: dict[str, dict[str, Any]] = {}
        self._load_nation_mapping()

    def _load_nation_mapping(self) -> None:
        """Load cultural nation mappings from review manifest."""
        if self.mapping_file.exists():
            try:
                with open(self.mapping_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        nation = item.get("original_nation", "").strip().lower()
                        self._nation_map[nation] = item
            except Exception:
                self._nation_map = {}

    async def check_health(self) -> dict[str, Any]:
        """Verify that the raw CSV is present and readable."""
        if not self.csv_path.exists():
            return {
                "source_id": self.source_id,
                "status": "unavailable",
                "message": f"Raw CSV file not found at {self.csv_path}",
            }
        try:
            with open(self.csv_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header and set(header) == self.EXPECTED_COLUMNS:
                    return {
                        "source_id": self.source_id,
                        "status": "ok",
                        "message": "Raw CSV file is present, readable, and headers match expected schema",
                    }
                return {
                    "source_id": self.source_id,
                    "status": "degraded",
                    "message": f"CSV headers do not match expected columns: {header}",
                }
        except Exception as exc:
            return {
                "source_id": self.source_id,
                "status": "unavailable",
                "message": f"Error reading CSV: {exc}",
            }

    async def search(
        self,
        query: str = "",
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 50,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Read CSV rows matching query/country and normalize into ImportCandidates."""
        if not self.csv_path.exists():
            return []

        candidates: list[ImportCandidate] = []
        batch_id = kwargs.get("batch_id", "batch-csv-default")
        q_lower = query.lower() if query else ""

        seen_fingerprints: set[str] = set()
        row_idx = 0

        with open(self.csv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_idx += 1
                title = (row.get("title") or "").strip()
                nation = (row.get("nation") or "").strip().lower()
                url = (row.get("source") or "").strip()
                text = (row.get("text") or "").strip()

                # Filter by query if provided
                if q_lower and q_lower not in title.lower() and q_lower not in nation:
                    continue

                # Nation mapping lookup
                mapping = self._nation_map.get(nation, {})
                mapped_country = mapping.get("proposed_country_code")

                # Filter by country if requested
                if country_code and mapped_country != country_code.upper():
                    continue

                # Fingerprint check
                fingerprint = hashlib.sha256(f"{url}|{title.lower()}".encode("utf-8")).hexdigest()
                is_duplicate = fingerprint in seen_fingerprints
                seen_fingerprints.add(fingerprint)

                row_dict = {
                    "row_index": row_idx,
                    "title": title,
                    "nation": nation,
                    "source": url,
                    "text_length": len(text),
                    "fingerprint": fingerprint,
                    "is_duplicate": is_duplicate,
                    "mapping": mapping,
                }

                try:
                    candidate = self.normalize_record(
                        row_dict,
                        batch_id=batch_id,
                        proposed_country_code=mapped_country,
                        proposed_category=CategoryEnum.FOLKLORE,
                    )
                    candidates.append(candidate)
                except Exception:
                    continue

                if len(candidates) >= limit:
                    break

        return candidates

    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Find row by candidate ID or row index."""
        try:
            target_idx = int(external_id.replace("CAND-CSV-", ""))
        except ValueError:
            return None

        if not self.csv_path.exists():
            return None

        row_idx = 0
        with open(self.csv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_idx += 1
                if row_idx == target_idx:
                    nation = (row.get("nation") or "").strip().lower()
                    mapping = self._nation_map.get(nation, {})
                    fingerprint = hashlib.sha256(f"{row.get('source')}|{row.get('title')}".encode("utf-8")).hexdigest()
                    row_dict = {
                        "row_index": row_idx,
                        "title": row.get("title", ""),
                        "nation": nation,
                        "source": row.get("source", ""),
                        "text_length": len(row.get("text", "")),
                        "fingerprint": fingerprint,
                        "is_duplicate": False,
                        "mapping": mapping,
                    }
                    return self.normalize_record(row_dict, batch_id="batch-csv-single")
        return None

    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert a raw CSV row into an ImportCandidate with strict rights and mapping flags."""
        row_idx = raw_item.get("row_index", 0)
        title = raw_item.get("title") or f"Untitled Row {row_idx}"
        raw_nation = raw_item.get("nation") or ""
        source_url = raw_item.get("source") or ""
        mapping = raw_item.get("mapping") or {}
        is_duplicate = raw_item.get("is_duplicate", False)

        candidate_id = f"CAND-CSV-{row_idx:05d}"

        # Disposition state machine
        if is_duplicate:
            disposition = CandidateDispositionEnum.DUPLICATE_CANDIDATE
        elif not raw_nation or not mapping.get("proposed_country_code") or mapping.get("human_review_required"):
            disposition = CandidateDispositionEnum.NEEDS_MAPPING_REVIEW
        else:
            # Country maps cleanly to 1 of 15 countries, but rights are unresolved (fairytalez retellings)
            disposition = CandidateDispositionEnum.NEEDS_RIGHTS_REVIEW

        review_notes = (
            f"Candidate from raw CSV row {row_idx}. Original nation: '{raw_nation}'. "
            f"Mapping reason: {mapping.get('reason', 'Unreviewed nation')}. "
            "Underlying text from fairytalez.com is copyrighted retelling; full text must remain quarantined. "
            "Only bibliographic metadata and original summaries permitted."
        )

        return ImportCandidate(
            candidate_id=candidate_id,
            import_batch_id=batch_id,
            source_registry_id=self.source_id,
            external_id=f"row-{row_idx}",
            raw_title=title,
            raw_nation=raw_nation,
            raw_language="en",
            raw_url=source_url,
            raw_metadata={
                "row_index": row_idx,
                "text_length": raw_item.get("text_length", 0),
                "fingerprint": raw_item.get("fingerprint"),
                "mapping_status": mapping.get("mapping_status"),
                "raw_domain": "fairytalez.com" if "fairytalez" in source_url else "unknown",
            },
            raw_text_available=True,  # Text exists in raw CSV, but withheld from published datasets
            rights_status=RightsStatusEnum.NEEDS_RIGHTS_REVIEW,
            proposed_country_code=proposed_country_code,
            proposed_category=CategoryEnum.FOLKLORE,
            proposed_summary=f"Folktale titled '{title}' associated with {raw_nation or 'unknown nation'} in candidate CSV.",
            disposition=disposition,
            review_notes=review_notes,
        )
