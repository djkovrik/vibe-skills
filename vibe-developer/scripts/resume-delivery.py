#!/usr/bin/env python3
"""Read-only recovery brief for a Protocol 2.0 delivery."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(SCRIPT_DIR))

from vibe_protocol import (
    ProtocolError, canonical_inventory, compute_app_spec_fingerprint,
    compute_workspace_fingerprint, discover_scoped_instructions, fingerprint_equal,
    ledger_digest, paths_within_boundaries, read_json, validate_app_spec,
    workspace_drift_paths,
)

def resolve(root: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()

def build_resume(project_root: Path, ledger_path: Path) -> dict:
    root = project_root.resolve()
    ledger = read_json(ledger_path)
    errors: list[str] = []
    if ledger.get("schemaVersion") != "2.0":
        errors.append(f"unsupported protocol: delivery ledger {ledger.get('schemaVersion')!r}")
    if ledger.get("ledgerDigest") != ledger_digest(ledger):
        errors.append("delivery ledger digest mismatch")
    app_root = resolve(root, ledger.get("appSpec", {}).get("root", ""))
    app, app_errors, _ = validate_app_spec(app_root)
    errors.extend(app_errors)
    current_app = compute_app_spec_fingerprint(app_root)
    current_workspace = compute_workspace_fingerprint(root)
    if app is not None and ledger.get("canonicalInventory") != canonical_inventory(app):
        errors.append("canonical inventory mismatch")
    active_id = ledger.get("execution", {}).get("activeAcceptanceScenarioId")
    active = next((item for item in ledger.get("acceptanceScenarios", []) if item.get("id") == active_id), None)
    checkpoint = ledger.get("execution", {}).get("checkpoint", {}).get("workspaceFingerprint")
    drift_paths = workspace_drift_paths(checkpoint or {}, current_workspace)
    if fingerprint_equal(checkpoint, current_workspace):
        classification = "clean"
    elif isinstance(checkpoint, dict) and checkpoint.get("gitHead") != current_workspace.get("gitHead"):
        classification = "unexpected-drift"
    elif active and active.get("status") == "in-progress" and paths_within_boundaries(drift_paths, active.get("fileBoundaries", [])):
        classification = "expected-drift"
    else:
        classification = "unexpected-drift"
    stale = not fingerprint_equal(ledger.get("appSpec", {}).get("fingerprint"), current_app)
    for collection in (ledger.get("acceptanceScenarios", []), ledger.get("qualityGates", [])):
        for item in collection:
            if item.get("status") == "verified":
                for ref in item.get("receiptRefs", []):
                    try:
                        receipt = read_json(resolve(root, ref))
                    except ProtocolError:
                        stale = True
                        continue
                    if not fingerprint_equal(receipt.get("workspaceFingerprint"), current_workspace):
                        stale = True
    if classification == "clean" and stale:
        classification = "stale-evidence"
    handoff_dir = root / ".vibe" / "handoffs"
    ingested = {item.get("sha256") for item in ledger.get("ingestedHandoffs", []) if isinstance(item, dict)}
    pending = []
    if handoff_dir.is_dir():
        import hashlib
        for path in sorted(handoff_dir.glob("*.json")):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest not in ingested:
                issues: list[str] = []
                try:
                    handoff = read_json(path)
                    if handoff.get("schemaVersion") != "2.0": issues.append("unsupported protocol")
                    if not fingerprint_equal(handoff.get("resultWorkspaceFingerprint"), current_workspace): issues.append("stale result fingerprint")
                    changed = handoff.get("changedFiles") if isinstance(handoff.get("changedFiles"), list) else []
                    allowed = handoff.get("allowedFiles") if isinstance(handoff.get("allowedFiles"), list) else []
                    if not paths_within_boundaries(changed, allowed): issues.append("changed files escape hand-off boundaries")
                    if active and any(item_id == active_id for item_id in handoff.get("acceptanceScenarioIds", [])):
                        if not fingerprint_equal(handoff.get("baseWorkspaceFingerprint"), active.get("baselineFingerprint")): issues.append("base fingerprint conflicts with active baseline")
                        if not paths_within_boundaries(changed, active.get("fileBoundaries", [])): issues.append("changed files escape ledger boundaries")
                    actual = workspace_drift_paths(handoff.get("baseWorkspaceFingerprint", {}), current_workspace)
                    if set(changed) != set(actual): issues.append("changedFiles do not match fingerprint drift")
                except (ProtocolError, TypeError, ValueError) as exc:
                    issues.append(str(exc))
                pending.append({"path": path.relative_to(root).as_posix(), "sha256": digest, "valid": not issues, "issues": issues})
    dependency_blockers = []
    statuses = {item.get("id"): item.get("status") for item in ledger.get("acceptanceScenarios", [])}
    for item in ledger.get("acceptanceScenarios", []):
        if item.get("status") == "not-started":
            unmet = [dep for dep in item.get("dependsOnAcceptanceScenarioIds", []) if statuses.get(dep) not in {"verified", "waived"}]
            if unmet:
                dependency_blockers.append({"id": item.get("id"), "unmet": unmet})
    instructions = discover_scoped_instructions(root)
    if instructions != ledger.get("execution", {}).get("scopedInstructions"):
        errors.append("scoped AGENTS.md inventory changed")
        if classification == "clean":
            classification = "unexpected-drift"
    next_action = ledger.get("execution", {}).get("nextAction")
    if pending:
        if pending[0]["valid"]:
            next_action = f"Inspect and ingest pending hand-off {pending[0]['path']}."
        else:
            errors.append(f"pending hand-off conflict: {pending[0]['path']}: {', '.join(pending[0]['issues'])}")
            classification = "unexpected-drift"
            next_action = f"Do not ingest {pending[0]['path']}; reconcile its conflicts explicitly."
    elif classification == "expected-drift":
        next_action = "Enter reconciliation, inspect the active slice diff, then checkpoint before continuing."
    elif classification == "unexpected-drift":
        next_action = "Do not edit; reconcile changes outside the active boundaries explicitly."
    elif classification == "stale-evidence":
        next_action = "Rerun affected checks, create a new audit request, and obtain a fresh audit."
    return {
        "schemaVersion": "2.0", "projectRoot": str(root), "ledgerPath": str(ledger_path.resolve()),
        "activeAcceptanceScenarioId": active_id, "phase": ledger.get("execution", {}).get("phase"),
        "driftClassification": classification, "driftPaths": drift_paths,
        "completionEligible": not errors and not stale and classification == "clean",
        "pendingHandoffs": pending, "dependencyBlockers": dependency_blockers,
        "blockers": errors, "nextAction": next_action,
        "currentAppSpecFingerprint": current_app, "currentWorkspaceFingerprint": current_workspace,
        "ledgerDigest": ledger.get("ledgerDigest"),
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()
    ledger_path = (args.ledger or args.project_root / ".vibe" / "delivery-ledger.json").resolve()
    try:
        brief = build_resume(args.project_root, ledger_path)
    except (ProtocolError, OSError, ValueError) as exc:
        print(json.dumps({"schemaVersion": "2.0", "blockers": [str(exc)], "completionEligible": False}, indent=2))
        return 1
    print(json.dumps(brief, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not brief["blockers"] and brief["driftClassification"] != "unexpected-drift" else 1

if __name__ == "__main__":
    raise SystemExit(main())
