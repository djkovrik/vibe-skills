#!/usr/bin/env python3
"""Read-only recovery brief for a Protocol 2.0 delivery."""

from __future__ import annotations

import argparse
import json
import sys
import importlib.util
from recovery_inputs import required_reads as recovery_required_reads, validate_reads
from pathlib import Path
from scoped_evidence import active_boundaries, assignment_errors, receipt_current, receipt_stable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(SCRIPT_DIR))

from vibe_protocol import (
    ProtocolError, canonical_inventory, compute_app_spec_fingerprint,
    compute_workspace_fingerprint, discover_scoped_instructions, fingerprint_equal,
    ledger_digest, paths_within_boundaries, read_json, validate_app_spec,
    workspace_drift_paths,
    audit_paths, parse_time, valid_time, pending_handoff_paths,
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
    execution = ledger.get("execution", {})
    errors.extend(validate_reads(root, ledger))
    items = [*ledger.get("acceptanceScenarios", []), *ledger.get("qualityGates", [])]
    active_id = execution.get("activeAcceptanceScenarioId") or execution.get("activeQualityGateId")
    active = next((item for item in items if item.get("id") == active_id), None)
    checkpoint = ledger.get("execution", {}).get("checkpoint", {}).get("workspaceFingerprint")
    drift_paths = workspace_drift_paths(checkpoint or {}, current_workspace)
    if fingerprint_equal(checkpoint, current_workspace):
        classification = "clean"
    elif isinstance(checkpoint, dict) and checkpoint.get("gitHead") != current_workspace.get("gitHead"):
        classification = "unexpected-drift"
    elif active_boundaries(ledger) and paths_within_boundaries(drift_paths, active_boundaries(ledger)):
        classification = "expected-drift"
    else:
        classification = "unexpected-drift"
    stale = not fingerprint_equal(ledger.get("appSpec", {}).get("fingerprint"), current_app)
    evidence_issues = []
    receipts = []
    for path in (root / ".vibe" / "receipts").glob("*.json"):
        try: receipts.append(read_json(path))
        except ProtocolError as exc: evidence_issues.append(str(exc))
    for item in items:
        if item.get("status") != "verified": continue
        for surface in item.get("requiredVerificationSurfaces", []):
            matching = [r for r in receipts if receipt_current(root, r, current_workspace)
                and valid_time(r.get("completedAt")) and any(c.get("obligationId") == item["id"] and surface in c.get("surfaces", []) for c in r.get("coveredObligations", []))]
            latest = max(matching, key=lambda r: (parse_time(r["completedAt"]), r.get("exitCode") != 0)) if matching else None
            if latest is None or latest.get("exitCode") != 0 or latest.get("executionStatus") != "completed" or not receipt_stable(latest):
                evidence_issues.append(f"{item['id']}/{surface}: current successful completed receipt missing")
    binding = ledger.get("closureAudit", {})
    if binding.get("requestPath"):
        try:
            request_path = resolve(root, binding["requestPath"])
            request = read_json(request_path)
            import hashlib
            if hashlib.sha256(request_path.read_bytes()).hexdigest() != binding.get("requestSha256"): evidence_issues.append("audit request hash mismatch")
            if not fingerprint_equal(request.get("workspaceFingerprint"), current_workspace) or not fingerprint_equal(request.get("appSpecFingerprint"), current_app): evidence_issues.append("audit request is stale")
            audit_path, launch_path = audit_paths(root, request_path)
            if audit_path.exists() and launch_path.exists():
                audit_module = load_module("resume_audit_validator", SCRIPT_DIR.parent.parent / "vibe-acceptance-auditor" / "scripts" / "validate-closure-audit.py")
                evidence_issues.extend(audit_module.validate(read_json(audit_path), app_root, root, request_path))
            elif execution.get("phase") != "auditing": evidence_issues.append("bound audit or launch receipt is missing")
        except (ProtocolError, OSError, ValueError) as exc: evidence_issues.append(str(exc))
    stale = stale or bool(evidence_issues)
    if classification == "clean" and stale:
        classification = "stale-evidence"
    handoff_dir = root / ".vibe" / "handoffs"
    unimported = set(pending_handoff_paths(root, ledger))
    pending = []
    if handoff_dir.is_dir():
        import hashlib
        for path in sorted(handoff_dir.glob("*.json")):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if path.relative_to(root).as_posix() in unimported:
                issues: list[str] = []
                try:
                    handoff = read_json(path)
                    if handoff.get("schemaVersion") != "2.0": issues.append("unsupported protocol")
                    validator = load_module("resume_handoff_validator", SCRIPT_DIR / "ingest-handoff.py")
                    issues.extend(validator.validate_handoff(handoff, root, current_workspace))
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
    for handoff in pending:
        if not handoff["valid"]:
            errors.append(f"pending hand-off conflict: {handoff['path']}: {', '.join(handoff['issues'])}")
            classification = "unexpected-drift"
    if classification == "unexpected-drift" or errors:
        next_action = "Do not edit; reconcile reported drift or invalid state explicitly."
    elif pending:
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
    item_blockers = [{"id": item["id"], "blockers": item.get("blockers", []), "blocker": item.get("blocker")} for item in items if item.get("blockers") or item.get("blocker")]
    recovery_by_assignment = {}
    for path in sorted((root / ".vibe" / "recovery").glob("*.json")):
        try:
            packet = read_json(path)
            packet["path"] = path.relative_to(root).as_posix()
            old = recovery_by_assignment.get(packet.get("assignmentId"))
            if old is None or packet.get("createdAt", "") > old.get("createdAt", ""):
                recovery_by_assignment[packet.get("assignmentId")] = packet
        except ProtocolError as exc: errors.append(str(exc))
    decisions = []
    for path in sorted((root / "docs" / "decisions").glob("DEC-*.json")):
        try:
            decision = read_json(path); decision["path"] = path.relative_to(root).as_posix(); decisions.append(decision)
        except ProtocolError as exc: errors.append(str(exc))
    if active and (active.get("blockers") or active.get("blocker")) and classification != "unexpected-drift":
        next_action = f"Resolve saved blockers for {active_id}; do not continue dependent implementation."
    completion_errors = []
    eligible = False
    if not errors and not stale and classification == "clean" and not pending and not item_blockers:
        try:
            aggregate = load_module("resume_delivery_validator", SCRIPT_DIR / "validate-delivery-ledger.py").validate_ledger(root, ledger_path)
            eligible = aggregate.implementation_complete
            completion_errors = aggregate.errors
        except Exception as exc: completion_errors = [str(exc)]
    required_reads = [*recovery_required_reads(root, ledger), str(ledger_path), *[i["path"] for i in instructions]]
    if active:
        required_reads += [str(app_root / "flows" / f"{active['flowId']}.md")] if active.get("flowId") else []
        required_reads += [str(app_root / "screens" / f"{screen}.md") for screen in active.get("screenIds", [])]
    required_reads += [d["path"] for d in decisions]
    return {
        "schemaVersion": "2.0", "projectRoot": str(root), "ledgerPath": str(ledger_path.resolve()),
        "activeAcceptanceScenarioId": execution.get("activeAcceptanceScenarioId"), "activeQualityGateId": execution.get("activeQualityGateId"), "phase": ledger.get("execution", {}).get("phase"),
        "driftClassification": classification, "driftPaths": drift_paths,
        "safeToContinue": not errors and classification != "unexpected-drift" and not (active and (active.get("blockers") or active.get("blocker"))),
        "completionEligible": eligible, "completionBlockers": completion_errors,
        "activePackage": ledger.get("workPackages", {}).get(execution.get("activePackageId")),
        "activeSlice": active, "unresolvedObligations": [i for i in items if i.get("status") not in {"verified", "waived"}],
        "pendingChecks": [{"id":i["id"], "checks":i["pendingChecks"]} for i in items if i.get("pendingChecks")],
        "itemBlockers": item_blockers, "evidenceIssues": evidence_issues,
        "recoveryPackets": [p for p in recovery_by_assignment.values() if p.get("status") != "returned"], "decisions": decisions, "requiredReads": sorted(set(required_reads)),
        "orphanAuditRequests": [p.relative_to(root).as_posix() for p in sorted((root / ".vibe" / "audits").glob("*/request.json")) if p.relative_to(root).as_posix() not in {binding.get("requestPath"), *[h.get("requestPath") for h in ledger.get("auditHistory", [])]}],
        "pendingHandoffs": pending, "dependencyBlockers": dependency_blockers,
        "blockers": [*errors, *item_blockers], "stateErrors": errors, "nextAction": next_action,
        "currentAppSpecFingerprint": current_app, "currentWorkspaceFingerprint": current_workspace,
        "ledgerDigest": ledger.get("ledgerDigest"),
    }


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module)
    return module

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--compact", action="store_true", help="Omit repeated snapshots; preserve actionable state")
    args = parser.parse_args()
    ledger_path = (args.ledger or args.project_root / ".vibe" / "delivery-ledger.json").resolve()
    try:
        brief = build_resume(args.project_root, ledger_path)
    except (ProtocolError, OSError, ValueError) as exc:
        print(json.dumps({"schemaVersion": "2.0", "blockers": [str(exc)], "completionEligible": False}, indent=2))
        return 1
    if args.compact:
        def compact(value):
            if isinstance(value, list): return [compact(v) for v in value]
            if not isinstance(value, dict): return value
            if value.get("algorithm") == "sha256" and "digest" in value: return {"digest": value["digest"]}
            return {k: compact(v) for k, v in value.items()}
        brief = compact(brief)
    print(json.dumps(brief, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not brief["blockers"] and brief["driftClassification"] != "unexpected-drift" else 1

if __name__ == "__main__":
    raise SystemExit(main())
