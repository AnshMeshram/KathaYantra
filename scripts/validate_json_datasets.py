"""KathaYantra - Seed JSON Dataset Quality Validation Script.

Validates all 30 country seed files across folklore and urban legends,
enforcing dataset envelope contracts, ID formats, referential integrity,
rights classifications, and gap analysis.
"""

from pathlib import Path
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.data_validation import data_quality_validator


def run_validation(verbose: bool = False) -> int:
    """Run data quality validation and print structured findings."""
    print("=" * 70)
    print("  KATHAYANTRA — DATA QUALITY & ARCHIVAL GOVERNANCE VALIDATOR")
    print("=" * 70)

    report = data_quality_validator.validate_all()

    print(f"Files Inspected:   {report.total_files_inspected}")
    print(f"Records Inspected: {report.total_records_inspected}")
    print(f"Total Errors:      {report.error_count}")
    print(f"Total Warnings:    {report.warning_count}")
    print(f"Dataset Valid:     {'YES (All checks passed)' if report.is_valid else 'NO (Errors detected)'}")
    print("-" * 70)

    if report.issues:
        print("Findings / Diagnostic Details:")
        for issue in report.issues:
            prefix = "[ERROR]  " if issue.severity == "error" else "[WARN]   "
            loc = f" ({issue.file_path})" if issue.file_path else ""
            rec = f" [ID: {issue.record_id}]" if issue.record_id else ""
            print(f" {prefix}{issue.error_code}{loc}{rec}: {issue.message}")
        print("-" * 70)

    if report.counts_by_country:
        print("Actual Published Counts by Country (Folklore / Urban Legends):")
        for country, counts in sorted(report.counts_by_country.items()):
            print(f"  {country}: {counts.get('folklore', 0)} folklore, {counts.get('urban_legends', 0)} urban legends (Target: 10 + 10 = 20)")
        print("=" * 70)

    return 0 if report.is_valid else 1


if __name__ == "__main__":
    is_verbose = "--verbose" in sys.argv or "-v" in sys.argv
    exit_code = run_validation(verbose=is_verbose)
    sys.exit(exit_code)
