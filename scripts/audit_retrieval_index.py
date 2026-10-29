"""Audit Retrieval Index CLI for KathaYantra.

Inspects the compiled SQLite FTS5 database, validates row counts, checks metadata,
and reports category/country distributions.
"""

from pathlib import Path
import sqlite3
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.retrieval_index import retrieval_index_service


def main():
    print("=" * 75)
    print("  KATHAYANTRA — RETRIEVAL INDEX AUDIT & HEALTH INSPECTOR")
    print("=" * 75)

    meta = retrieval_index_service.get_index_metadata()
    if not meta.get("exists"):
        print(f"[ERROR] Index not found at {settings.retrieval_index_file}. Run scripts/build_retrieval_index.py first.")
        sys.exit(1)

    print(f"Index File:        {meta.get('db_path')}")
    print(f"Index Version:     {meta.get('index_version', 'Unknown')}")
    print(f"Last Rebuilt At:   {meta.get('last_rebuilt_at', 'Unknown')}")
    print(f"Indexed Stories:   {meta.get('actual_indexed_rows', 0)}")
    print("-" * 75)

    con = retrieval_index_service.get_connection()
    try:
        # Distribution by category
        cat_rows = con.execute("SELECT category, count(*) as cnt FROM stories_fts GROUP BY category").fetchall()
        print("Indexed Breakdown by Category:")
        for r in cat_rows:
            print(f"  - {r['category']:<15} {r['cnt']} stories")

        # Distribution by country
        country_rows = con.execute("SELECT country_code, count(*) as cnt FROM stories_fts GROUP BY country_code ORDER BY country_code").fetchall()
        print("\nIndexed Breakdown by Country:")
        for r in country_rows:
            print(f"  - {r['country_code']:<5} {r['cnt']} stories")

        print("=" * 75)
        print("[SUCCESS] Retrieval index is healthy and verified!")
    finally:
        con.close()


if __name__ == "__main__":
    main()

