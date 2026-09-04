#!/usr/bin/env python3
"""Initialize a non-overwriting Vibe delivery ledger 2.0."""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(SCRIPT_DIR))

from vibe_protocol import (
    LEDGER_VERSION, ProtocolError, atomic_write_json, canonical_inventory,
    compute_app_spec_fingerprint, compute_workspace_fingerprint,
    discover_scoped_instructions, utc_now, validate_app_spec, with_ledger_digest,
)

def portable(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return os.fspath(path.resolve())

def readiness_scope(gate: dict) -> str:
    return "implementation" if gate.get("category") == "repository" else "release"

def create_ledger(app_spec_root: Path, project_root: Path) -> dict:
    app_spec_root, project_root = app_spec_root.resolve(), project_root.resolve()
    data, errors, _ = validate_app_spec(app_spec_root)
    if errors or data is None:
        raise ProtocolError("invalid AppSpec 2.0: " + "; ".join(errors))
    now = utc_now()
    workspace = compute_workspace_fingerprint(project_root)
    inventory = canonical_inventory(data)
    requirements = {item["id"]: item for item in data["requirements"] if item.get("status") == "approved"}
    ledger = {
        "schemaVersion": LEDGER_VERSION,
        "ledgerId": f"LEDGER-{uuid.uuid4()}",
        "createdAt": now,
        "updatedAt": now,
        "appSpec": {"root": portable(app_spec_root, project_root), "fingerprint": compute_app_spec_fingerprint(app_spec_root)},
        "canonicalInventory": inventory,
        "workspaceFingerprint": workspace,
        "execution": {
            "phase": "planning",
            "activeAcceptanceScenarioId": None,
            "scopedInstructions": discover_scoped_instructions(project_root),
            "checkpoint": {"checkpointId": f"CP-{uuid.uuid4()}", "createdAt": now, "workspaceFingerprint": workspace},
            "nextAction": "Select the first dependency-ready acceptance scenario and checkpoint before editing.",
        },
        "acceptanceScenarios": [],
        "qualityGates": [],
        "ingestedHandoffs": [],
        "finalReceiptRef": None,
        "closureAudit": {"requestPath": None, "auditPath": None},
    }
    for scenario in data["acceptanceScenarios"]:
        requirement = requirements[scenario["requirementId"]]
        ledger["acceptanceScenarios"].append({
            "id": scenario["id"], "requirementId": scenario["requirementId"],
            "priority": requirement["priority"], "flowId": scenario["flowId"],
            "screenIds": scenario["screenIds"],
            "dependsOnAcceptanceScenarioIds": scenario["dependsOnAcceptanceScenarioIds"],
            "requiredVerificationSurfaces": scenario["verificationSurfaces"],
            "status": "not-started", "productionEvidence": [], "testEvidence": [],
            "receiptRefs": [], "handoffRefs": [],
        })
    for gate in data["qualityGates"]:
        applicability = "applicable" if gate["requirement"] == "required" else "needs-review"
        ledger["qualityGates"].append({
            "id": gate["id"], "category": gate["category"], "platform": gate["platform"],
            "requirement": gate["requirement"], "condition": gate.get("condition"),
            "verificationMethod": gate["verificationMethod"], "contractSource": gate["contractSource"],
            "requiredVerificationSurfaces": gate["verificationSurfaces"],
            "readinessScope": readiness_scope(gate), "applicability": applicability,
            "status": "not-started", "productionEvidence": [], "testEvidence": [], "receiptRefs": [],
        })
    return with_ledger_digest(ledger)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app_spec", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()
    target = (args.ledger or args.project_root / ".vibe" / "delivery-ledger.json").resolve()
    try:
        ledger = create_ledger(args.app_spec, args.project_root)
        atomic_write_json(target, ledger, refuse_existing=True)
    except (ProtocolError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Initialized delivery ledger 2.0: {target}")
    print(f"ledger-digest: {ledger['ledgerDigest']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
