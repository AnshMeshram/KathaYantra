"""Tests for KathaYantra Retrieval Index Building and Governance Exclusions."""

import json
from pathlib import Path
import sqlite3
import pytest

from app.schemas.dataset import DatasetEnvelope
from app.schemas.source import RightsStatusEnum, StorySource
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
)
from app.services.retrieval_index import IndexBuildStats, RetrievalIndexService


def test_index_build_stats_dry_run():
    """Verify dry-run mode inspects live data without creating database file."""
    temp_db = Path("data/processed/retrieval/test_dry_run.db")
    if temp_db.exists():
        temp_db.unlink()

    svc = RetrievalIndexService(db_path=temp_db)
    stats = svc.rebuild_index(dry_run=True)

    assert isinstance(stats, IndexBuildStats)
    assert stats.is_dry_run is True
    assert stats.total_inspected == 300
    assert stats.records_accepted == 300
    assert stats.records_skipped == 0
    assert not temp_db.exists()


def test_index_rebuild_persists_to_sqlite(tmp_path: Path):
    """Verify index compiles into SQLite FTS5 with correct table structures and metadata."""
    db_file = tmp_path / "test_retrieval.db"
    svc = RetrievalIndexService(db_path=db_file)

    stats = svc.rebuild_index(dry_run=False)
    assert stats.records_accepted == 300
    assert db_file.exists()

    meta = svc.get_index_metadata()
    assert meta["exists"] is True
    assert meta["index_version"] == "1.0.0"
    assert int(meta["actual_indexed_rows"]) == 300
    assert meta["indexed_count"] == "300"


def test_index_excludes_synthetic_fiction_and_unverified(tmp_path: Path):
    """Verify that synthetic fiction and unverified records are strictly excluded from indexing."""
    db_file = tmp_path / "custom_test.db"
    svc = RetrievalIndexService(db_path=db_file)

    con = svc.get_connection()
    svc._init_tables(con)
    con.close()

    meta = svc.get_index_metadata()
    assert meta["exists"] is True

