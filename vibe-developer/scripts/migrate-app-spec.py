#!/usr/bin/env python3
"""Protocol 2.0 intentionally provides no AppSpec 1.x migrator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path); parser.add_argument("destination", type=Path); parser.parse_args()
    print("ERROR: unsupported protocol: AppSpec 1.x migration and backward compatibility are not available; create and approve a new AppSpec 2.0 without modifying either path", file=sys.stderr)
    return 1

if __name__ == "__main__": raise SystemExit(main())
