#!/usr/bin/env python3
"""CLI Tool alias for Wikimedia / Wikipedia REST API discovery."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.discover_wikimedia import main

if __name__ == "__main__":
    sys.exit(main())
