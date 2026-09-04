#!/usr/bin/env python3
"""Strictly validate a Vibe AppSpec 2.0 directory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(SCRIPT_DIR))

from vibe_protocol import APP_SPEC_VERSION, canonical_inventory, validate_app_spec

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app_spec", type=Path)
    parser.add_argument("--require-current", action="store_true", help="Compatibility flag; Protocol 2.0 validation is always strict")
    parser.add_argument("--inventory", action="store_true")
    args = parser.parse_args()
    data, errors, warnings = validate_app_spec(args.app_spec)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if not errors and data is not None:
        if args.inventory:
            print(json.dumps(canonical_inventory(data), ensure_ascii=False, indent=2, sort_keys=True))
        print(f"RESULT: VALID AppSpec {APP_SPEC_VERSION}")
        return 0
    print("RESULT: INVALID")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
