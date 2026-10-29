#!/usr/bin/env python3
"""CLI Tool to generate import batch and candidate coverage reports."""

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.import_reporting import import_reporting_service


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Display staged candidate coverage, disposition breakdown, and shortfall against 300 target."
    )
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON format")
    args = parser.parse_args()

    if args.json:
        report = import_reporting_service.generate_coverage_report()
        print(json.dumps(report, indent=2))
    else:
        print(import_reporting_service.format_text_report())

    return 0


if __name__ == "__main__":
    sys.exit(main())
