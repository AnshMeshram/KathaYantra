#!/usr/bin/env python3
"""CLI Tool to validate all staged import candidates in data/processed/candidates/."""

import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.import_candidate import ImportCandidate


def main() -> int:
    candidates_dir = settings.candidates_dir
    print("=" * 70)
    print("  KATHAYANTRA — STAGED CANDIDATE INTEGRITY & SCHEMA VALIDATOR")
    print("=" * 70)

    if not candidates_dir.exists():
        print(f"Candidates directory not found at {candidates_dir}. Nothing to validate.")
        return 0

    jsonl_files = list(candidates_dir.glob("*.jsonl"))
    if not jsonl_files:
        print(f"No .jsonl candidate batch files found in {candidates_dir}.")
        print("Candidate archive is clean (0 records staged).")
        print("=" * 70)
        return 0

    total_records = 0
    total_errors = 0
    file_count = 0

    for fpath in jsonl_files:
        file_count += 1
        line_idx = 0
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line_idx += 1
                stripped = line.strip()
                if not stripped:
                    continue
                total_records += 1
                try:
                    raw_data = json.loads(stripped)
                    candidate = ImportCandidate.model_validate(raw_data)

                    # Domain rule: Country code must be in supported list if provided
                    if candidate.proposed_country_code and candidate.proposed_country_code not in SUPPORTED_COUNTRY_CODES:
                        print(f"  [ERROR] {fpath.name}:{line_idx} - Invalid country code '{candidate.proposed_country_code}'")
                        total_errors += 1

                except Exception as exc:
                    print(f"  [ERROR] {fpath.name}:{line_idx} - Schema validation failed: {exc}")
                    total_errors += 1

    print("-" * 70)
    print(f"Batch Files Inspected:  {file_count}")
    print(f"Candidates Inspected:   {total_records}")
    print(f"Total Errors Found:     {total_errors}")

    if total_errors > 0:
        print(f"FAILED: Found {total_errors} candidate validation error(s).")
        print("=" * 70)
        return 1

    print("PASSED: All staged import candidates strictly conform to schema contract.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
