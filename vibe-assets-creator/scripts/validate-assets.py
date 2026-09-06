#!/usr/bin/env python3
"""Validate the frozen asset requirements or their delivered project resources."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "vibe-developer" / "scripts"))
from asset_contract import validate_delivery, validate_requirements

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-spec-root", type=Path, required=True)
    parser.add_argument("--repository", type=Path)
    args = parser.parse_args()
    try:
        app = json.loads((args.app_spec_root / "app-spec.json").read_text(encoding="utf-8-sig"))
        errors, warnings = validate_delivery(app, args.repository) if args.repository else validate_requirements(app)
        if "assetRequirements" not in app: errors.append("assetRequirements missing; reconcile the legacy AppSpec before asset delivery")
    except (OSError, ValueError, TypeError) as exc: errors, warnings = [str(exc)], []
    print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings}, indent=2))
    return 1 if errors else 0

if __name__ == "__main__": raise SystemExit(main())
