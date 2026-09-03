#!/usr/bin/env python3
"""Initialize the tracked Vibe delivery ledger without overwriting prior state."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


LEDGER_VERSION = "1.0"


def _load_fingerprint_module() -> Any:
    path = Path(__file__).with_name("compute-workspace-fingerprint.py")
    spec = importlib.util.spec_from_file_location("vibe_workspace_fingerprint", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load fingerprint implementation: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _portable_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return os.fspath(path.resolve())


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object in {path}")
    return value


def _readiness_scope(gate: dict[str, Any]) -> str:
    explicit = str(gate.get("readinessScope", "")).casefold()
    if explicit in {"implementation", "release"}:
        return explicit
    category = str(gate.get("category", "")).casefold().replace("_", "-")
    platform = str(gate.get("platform", "")).casefold().replace("_", "-")
    release_categories = {
        "external",
        "platform",
        "platform-build",
        "publication",
        "release",
        "release-automation",
        "store",
    }
    release_platforms = {"android", "ios", "external", "google-play", "app-store"}
    return "release" if category in release_categories or platform in release_platforms else "implementation"


def _requirement_index(app_spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in app_spec.get("requirements", []):
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def _scenario_is_required(
    scenario: dict[str, Any], requirements: dict[str, dict[str, Any]]
) -> bool:
    if isinstance(scenario.get("required"), bool):
        return bool(scenario["required"])
    requirement = requirements.get(str(scenario.get("requirementId", "")), {})
    return str(requirement.get("priority", "")).casefold() != "optional"


def create_ledger(app_spec_root: Path, project_root: Path) -> dict[str, Any]:
    fingerprint = _load_fingerprint_module()
    app_spec_path = app_spec_root / "app-spec.json"
    app_spec = _read_json(app_spec_path)
    if app_spec.get("schemaVersion") != "1.4":
        raise RuntimeError(
            "delivery ledger initialization requires an approved AppSpec 1.4; "
            f"found {app_spec.get('schemaVersion')!r}"
        )

    requirements = _requirement_index(app_spec)
    acceptance_entries: list[dict[str, Any]] = []
    for scenario in app_spec.get("acceptanceScenarios", []):
        if not isinstance(scenario, dict) or not isinstance(scenario.get("id"), str):
            raise RuntimeError("every acceptance scenario must be an object with a string id")
        acceptance_entries.append(
            {
                "id": scenario["id"],
                "requirementId": scenario.get("requirementId"),
                "flowId": scenario.get("flowId"),
                "screenIds": scenario.get("screenIds", []),
                "required": _scenario_is_required(scenario, requirements),
                "requiredTestSurfaces": scenario.get("verificationSurfaces", []),
                "status": "not-started",
                "productionEvidence": [],
                "testEvidence": [],
                "verificationReceipts": [],
                "blocker": None,
                "waiver": None,
            }
        )

    gate_entries: list[dict[str, Any]] = []
    for gate in app_spec.get("qualityGates", []):
        if not isinstance(gate, dict) or not isinstance(gate.get("id"), str):
            raise RuntimeError("every quality gate must be an object with a string id")
        requirement = gate.get("requirement")
        gate_entries.append(
            {
                "id": gate["id"],
                "category": gate.get("category"),
                "platform": gate.get("platform"),
                "requirement": requirement,
                "condition": gate.get("condition") if requirement == "conditional" else None,
                "verificationMethod": gate.get("verificationMethod"),
                "contractSource": gate.get("contractSource"),
                "readinessScope": _readiness_scope(gate),
                "applicability": "needs-review" if requirement == "conditional" else "applicable",
                "applicabilityReason": None,
                "status": "not-started",
                "productionEvidence": [],
                "testEvidence": [],
                "verificationReceipts": [],
                "blocker": None,
                "waiver": None,
            }
        )

    acceptance_entries.sort(key=lambda item: item["id"])
    gate_entries.sort(key=lambda item: item["id"])
    return {
        "schemaVersion": LEDGER_VERSION,
        "createdAt": _utc_now(),
        "appSpec": {
            "root": _portable_path(app_spec_root, project_root),
            "fingerprint": fingerprint.compute_app_spec_fingerprint(app_spec_root),
        },
        "workspaceFingerprint": fingerprint.compute_workspace_fingerprint(project_root),
        "acceptanceScenarios": acceptance_entries,
        "qualityGates": gate_entries,
        "closureAudit": {"path": ".vibe/closure-audit.json"},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app_spec", type=Path, help="Approved AppSpec 1.4 directory")
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Target Git project root"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Ledger path (default: <project-root>/.vibe/delivery-ledger.json)",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = args.project_root.resolve()
    app_spec_root = args.app_spec.resolve()
    output = (args.output or project_root / ".vibe" / "delivery-ledger.json").resolve()
    if output.exists():
        print(f"ERROR: refusing to overwrite existing ledger: {output}", file=sys.stderr)
        return 2
    try:
        ledger = create_ledger(app_spec_root, project_root)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Initialized delivery ledger: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
