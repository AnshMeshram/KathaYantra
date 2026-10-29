"""Tests for KathaYantra CSV Dataset Audit Script."""

import csv
import json
from pathlib import Path
import pytest
from scripts.audit_folktales_csv import audit_csv


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a minimal valid CSV fixture for auditing."""
    csv_file = tmp_path / "sample_folktales.csv"
    fieldnames = ["source", "nation", "title", "text"]
    rows = [
        {
            "source": "https://example.com/tale1",
            "nation": "indian",
            "title": "The Golden Fish",
            "text": "Once upon a time there was a golden fish that granted wishes to a humble fisherman in ancient times.",
        },
        {
            "source": "https://example.com/tale2",
            "nation": "",  # Missing nation
            "title": "The Nameless Tale",
            "text": "A wandering traveller entered a deserted village at dusk.",
        },
        {
            "source": "https://example.com/tale3",
            "nation": "japanese",
            "title": "The Golden Fish",  # Duplicate title
            "text": "In a mountain lake lived an ancient carp revered as a spirit.",
        },
        {
            "source": "https://example.com/tale4",
            "nation": "german",
            "title": "Wise Folks",
            "text": "Once upon a time there was a golden fish that granted wishes to a humble fisherman in ancient times.",  # Exact duplicate text of row 1
        },
    ]

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return csv_file


def test_missing_or_malformed_csv_handling(tmp_path: Path):
    """Test 11: Missing file or malformed columns raise expected exceptions."""
    # Non-existent file
    non_existent = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError):
        audit_csv(non_existent)

    # Malformed columns
    bad_csv = tmp_path / "bad_columns.csv"
    with open(bad_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "country", "story_body"])  # Wrong columns
        writer.writerow(["https://example.com", "IN", "Story text"])

    with pytest.raises(ValueError) as exc:
        audit_csv(bad_csv)
    assert "Column mismatch" in str(exc.value)


def test_missing_csv_values_detection(sample_csv: Path, tmp_path: Path):
    """Test 12: Audit accurately detects missing fields in rows."""
    json_out = tmp_path / "audit.json"
    md_out = tmp_path / "audit.md"

    report = audit_csv(sample_csv, json_output_path=json_out, md_output_path=md_out)

    assert report["total_rows"] == 4
    # Missing nation detection
    missing_nation_count = report["missing_values"]["nation_missing_count"]
    assert missing_nation_count == 1
    missing_records = report["missing_values"]["missing_nation_records"]
    assert missing_records[0]["row_index"] == 2
    assert missing_records[0]["title"] == "The Nameless Tale"

    # Duplicate title detection
    assert report["duplicate_titles_count"] == 1
    assert "the golden fish" in report["duplicate_titles_sample"][0]["title"].lower()

    # Exact duplicate text detection
    assert report["exact_duplicates_count"] == 1
    exact_match = report["exact_duplicates"][0]
    assert set(exact_match["row_indices"]) == {1, 4}


def test_deterministic_csv_auditing(sample_csv: Path, tmp_path: Path):
    """Test 13: Running audit multiple times produces deterministic, identical outputs."""
    out1_json = tmp_path / "run1.json"
    out1_md = tmp_path / "run1.md"
    out2_json = tmp_path / "run2.json"
    out2_md = tmp_path / "run2.md"

    rep1 = audit_csv(sample_csv, json_output_path=out1_json, md_output_path=out1_md)
    rep2 = audit_csv(sample_csv, json_output_path=out2_json, md_output_path=out2_md)

    assert rep1 == rep2
    assert out1_json.read_text(encoding="utf-8") == out2_json.read_text(encoding="utf-8")
    assert out1_md.read_text(encoding="utf-8") == out2_md.read_text(encoding="utf-8")

