"""Retrieval Index Service for KathaYantra Using SQLite FTS5.

Builds and manages a deterministic, atomic, lexical search index derived strictly
from verified and publication-eligible KathaYantra story records.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sqlite3
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.core.config import BASE_DIR, settings
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.dataset import DatasetEnvelope
from app.schemas.source import RightsStatusEnum, StorySource
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
)
from app.services.publication_policy import PublicationPolicy

logger = logging.getLogger(__name__)

INDEX_VERSION = "1.0.0"


class IndexBuildStats(BaseModel):
    """Execution metrics and audit statistics from building the retrieval index."""

    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    index_version: str = INDEX_VERSION
    total_inspected: int = 0
    records_accepted: int = 0
    records_skipped: int = 0
    policy_rejected: int = 0
    synthetic_fiction_excluded: int = 0
    rights_ineligible_excluded: int = 0
    unverified_excluded: int = 0
    duplicate_ids: int = 0
    is_dry_run: bool = False
    index_file_path: str = ""
    exclusion_details: list[dict[str, Any]] = Field(default_factory=list)


class RetrievalIndexService:
    """Manages the creation, rebuilding, and integrity inspection of SQLite FTS5 indices."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.retrieval_index_file

    def get_connection(self) -> sqlite3.Connection:
        """Obtain a SQLite connection with row factory configured."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(str(self.db_path))
        con.row_factory = sqlite3.Row
        return con

    def _init_tables(self, con: sqlite3.Connection) -> None:
        """Create the metadata and FTS5 search virtual tables."""
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS index_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS stories_fts USING fts5(
                id UNINDEXED,
                country_code UNINDEXED,
                category UNINDEXED,
                title,
                alternate_names,
                summary,
                motifs,
                themes,
                cultural_community,
                region,
                sources_json UNINDEXED,
                attribution_text UNINDEXED,
                verification_status UNINDEXED,
                rights_status UNINDEXED,
                dataset_path UNINDEXED,
                tokenize = 'unicode61'
            )
            """
        )

    def rebuild_index(self, dry_run: bool = False) -> IndexBuildStats:
        """Scan all approved seed dataset files and build/rebuild the FTS5 search index."""
        stats = IndexBuildStats(
            is_dry_run=dry_run,
            index_file_path=str(self.db_path),
        )

        folklore_dir = settings.folklore_seed_dir
        urban_dir = settings.urban_legends_seed_dir

        seen_ids: set[str] = set()
        records_to_index: list[dict[str, Any]] = []

        # Iterate over all supported countries and both categories
        for country_code in sorted(SUPPORTED_COUNTRY_CODES.keys()):
            for category_dir, cat_enum in [
                (folklore_dir, CategoryEnum.FOLKLORE),
                (urban_dir, CategoryEnum.URBAN_LEGEND),
            ]:
                file_path = category_dir / f"{country_code}.json"
                if not file_path.exists():
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    envelope = DatasetEnvelope.model_validate(data)
                except Exception as e:
                    logger.error(f"Failed to read/validate envelope {file_path}: {e}")
                    stats.exclusion_details.append({
                        "file": str(file_path),
                        "reason": f"Corrupt envelope: {str(e)}",
                    })
                    continue

                for story in envelope.records:
                    stats.total_inspected += 1

                    # 1. Duplicate ID check
                    if story.id in seen_ids:
                        stats.duplicate_ids += 1
                        stats.records_skipped += 1
                        stats.exclusion_details.append({
                            "id": story.id,
                            "reason": f"Duplicate story ID '{story.id}' detected in {file_path.name}.",
                        })
                        continue
                    seen_ids.add(story.id)

                    # 2. Strict anti-fiction check (Generated fiction must never enter authentic index)
                    if story.content_origin == ContentOriginEnum.AI_GENERATED_FICTION:
                        stats.synthetic_fiction_excluded += 1
                        stats.records_skipped += 1
                        stats.exclusion_details.append({
                            "id": story.id,
                            "reason": "Synthetic AI fiction segregated from authentic index.",
                        })
                        continue

                    # 3. Verification status check
                    if story.verification_status != VerificationStatusEnum.VERIFIED:
                        stats.unverified_excluded += 1
                        stats.records_skipped += 1
                        stats.exclusion_details.append({
                            "id": story.id,
                            "reason": f"Verification status '{story.verification_status.value}' is not verified.",
                        })
                        continue

                    # 4. Rights status check
                    if story.rights_status not in (
                        RightsStatusEnum.APPROVED,
                        RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED,
                    ):
                        stats.rights_ineligible_excluded += 1
                        stats.records_skipped += 1
                        stats.exclusion_details.append({
                            "id": story.id,
                            "reason": f"Rights status '{story.rights_status.value}' ineligible for publication.",
                        })
                        continue

                    # 5. Full PublicationPolicy deterministic gate
                    eval_result = PublicationPolicy.evaluate_eligibility(story)
                    if not eval_result.is_eligible:
                        stats.policy_rejected += 1
                        stats.records_skipped += 1
                        stats.exclusion_details.append({
                            "id": story.id,
                            "reason": f"PublicationPolicy violations: {'; '.join(eval_result.violations)}",
                        })
                        continue

                    # Record accepted for indexing
                    sources_payload = [s.model_dump(mode="json") for s in story.sources]
                    cultural_comm = (
                        " ".join(story.community_attributions)
                        if story.community_attributions
                        else (story.region_or_community or "")
                    )
                    row = {
                        "id": story.id,
                        "country_code": story.country_code,
                        "category": story.category.value,
                        "title": story.title,
                        "alternate_names": " ".join(story.alternate_names),
                        "summary": story.summary,
                        "motifs": " ".join(story.motifs),
                        "themes": " ".join(story.themes),
                        "cultural_community": cultural_comm,
                        "region": story.region_or_community or "",
                        "sources_json": json.dumps(sources_payload, ensure_ascii=False),
                        "attribution_text": story.attribution_text or "",
                        "verification_status": story.verification_status.value,
                        "rights_status": story.rights_status.value,
                        "dataset_path": str(file_path.relative_to(BASE_DIR)),
                    }
                    records_to_index.append(row)
                    stats.records_accepted += 1

        if dry_run:
            return stats

        # Atomic commit inside SQLite transaction
        con = self.get_connection()
        try:
            with con:
                self._init_tables(con)
                # Clear previous indexed entries
                con.execute("DELETE FROM stories_fts")
                # Insert validated records
                insert_query = """
                INSERT INTO stories_fts (
                    id, country_code, category, title, alternate_names,
                    summary, motifs, themes, cultural_community, region,
                    sources_json, attribution_text, verification_status,
                    rights_status, dataset_path
                ) VALUES (
                    :id, :country_code, :category, :title, :alternate_names,
                    :summary, :motifs, :themes, :cultural_community, :region,
                    :sources_json, :attribution_text, :verification_status,
                    :rights_status, :dataset_path
                )
                """
                con.executemany(insert_query, records_to_index)

                # Update metadata
                con.execute(
                    "INSERT OR REPLACE INTO index_metadata (key, value) VALUES ('index_version', ?)",
                    (INDEX_VERSION,),
                )
                con.execute(
                    "INSERT OR REPLACE INTO index_metadata (key, value) VALUES ('last_rebuilt_at', ?)",
                    (stats.timestamp,),
                )
                con.execute(
                    "INSERT OR REPLACE INTO index_metadata (key, value) VALUES ('indexed_count', ?)",
                    (str(stats.records_accepted),),
                )
        finally:
            con.close()

        return stats

    def get_index_metadata(self) -> dict[str, Any]:
        """Fetch current index status and metrics from metadata table."""
        if not self.db_path.exists():
            return {
                "exists": False,
                "message": "Index database has not been initialized. Run build_retrieval_index.py first.",
            }

        con = self.get_connection()
        try:
            self._init_tables(con)
            rows = con.execute("SELECT key, value FROM index_metadata").fetchall()
            meta = {r["key"]: r["value"] for r in rows}
            count_row = con.execute("SELECT count(*) as cnt FROM stories_fts").fetchone()
            meta["actual_indexed_rows"] = count_row["cnt"] if count_row else 0
            meta["exists"] = True
            meta["db_path"] = str(self.db_path)
            return meta
        finally:
            con.close()


# Central singleton instance
retrieval_index_service = RetrievalIndexService()
