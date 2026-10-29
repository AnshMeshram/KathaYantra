"""Build and Rebuild Retrieval Index CLI for KathaYantra.

Compiles a deterministic SQLite FTS5 search index from all verified, published
story records across the 15 supported countries.
"""

import argparse
from pathlib import Path
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.retrieval_index import retrieval_index_service


def main():
    parser = argparse.ArgumentParser(
        description="Build or rebuild the KathaYantra SQLite FTS5 retrieval index."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate index compilation and report statistics without writing to disk.",
    )
    args = parser.parse_args()

    mode = "DRY-RUN (SIMULATION)" if args.dry_run else "LIVE REBUILD & PERSIST"
    print("=" * 75)
    print(f"  KATHAYANTRA — RETRIEVAL INDEX COMPILER ({mode})")
    print("=" * 75)

    stats = retrieval_index_service.rebuild_index(dry_run=args.dry_run)

    print(f"Total Records Inspected:          {stats.total_inspected}")
    print(f"Eligible Records Accepted:        {stats.records_accepted}")
    print(f"Records Skipped / Excluded:       {stats.records_skipped}")
    print(f"  - Publication Policy Rejected:  {stats.policy_rejected}")
    print(f"  - Synthetic AI Fiction Blocked: {stats.synthetic_fiction_excluded}")
    print(f"  - Unverified Records Blocked:   {stats.unverified_excluded}")
    print(f"  - Ineligible Rights Blocked:    {stats.rights_ineligible_excluded}")
    print(f"  - Duplicate Story IDs Blocked:  {stats.duplicate_ids}")
    print("-" * 75)
    print(f"Index Target Path:                {stats.index_file_path}")
    print(f"Index Version:                    {stats.index_version}")
    print(f"Timestamp:                        {stats.timestamp}")
    print("=" * 75)

    if stats.records_accepted == 0:
        print("[ERROR] No eligible records were accepted for indexing.")
        sys.exit(1)

    print(f"[SUCCESS] Successfully indexed {stats.records_accepted} records!")


if __name__ == "__main__":
    main()

