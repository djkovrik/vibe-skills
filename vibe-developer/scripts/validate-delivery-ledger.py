#!/usr/bin/env python3
"""Final aggregate validator for Vibe Protocol 2.0 delivery state."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(SCRIPT_DIR))

from vibe_protocol import (
    ProtocolError, canonical_inventory, compute_app_spec_fingerprint,
    compute_workspace_fingerprint, discover_scoped_instructions, fingerprint_equal,
    ledger_digest, read_json, validate_app_spec,
    decision_valid, valid_time, parse_time, audit_paths, pending_handoff_paths, verification_surface_map,
)

from recovery_inputs import validate_reads
from scoped_evidence import receipt_current, receipt_stable, receipt_format_errors

STATUSES = {"not-started", "in-progress", "implemented-unverified", "verified", "blocked-external", "waived"}
PHASES = {"planning", "implementing", "reconciling", "auditing", "final-verification", "complete", "blocked"}

@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    implementation_complete: bool = False
    release_ready: bool = False
    @property
    def valid(self) -> bool: return not self.errors
    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": self.errors, "warnings": self.warnings,
                "implementationComplete": self.implementation_complete, "releaseReady": self.release_ready}

def timestamp(value: Any) -> bool:
    return valid_time(value)

def resolve(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value: raise ProtocolError(f"{label}: expected path")
    path = Path(value)
    target = path.resolve() if path.is_absolute() else (root / path).resolve()
    if not path.is_absolute():
        try: target.relative_to(root)
        except ValueError as exc: raise ProtocolError(f"{label}: path escapes repository") from exc
    return target

def evidence_ok(root: Path, evidence: Any, label: str, result: ValidationResult) -> list[dict]:
    if not isinstance(evidence, list): result.errors.append(f"{label}: expected array"); return []
    valid = []
    for index, item in enumerate(evidence):
        prefix = f"{label}[{index}]"
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("surface"), str):
            result.errors.append(f"{prefix}: requires path and surface"); continue
        try: target = resolve(root, item["path"], prefix)
        except ProtocolError as exc: result.errors.append(str(exc)); continue
        if not target.is_file(): result.errors.append(f"{prefix}: file does not exist"); continue
        symbol = item.get("symbol") or item.get("testName")
        if symbol:
            try:
                if symbol not in target.read_text(encoding="utf-8-sig"): result.errors.append(f"{prefix}: symbol/testName not found: {symbol}")
            except (OSError, UnicodeError): result.errors.append(f"{prefix}: cannot inspect text")
        valid.append(item)
    return valid

def load_receipts(root: Path, refs: set[str], current: dict, result: ValidationResult, *, scoped=False) -> dict[str, dict]:
    loaded: dict[str, dict] = {}
    for ref in sorted(refs):
        if not isinstance(ref, str) or not ref.startswith(".vibe/receipts/") or not ref.endswith(".json"):
            result.errors.append(f"receipt ref must point to .vibe/receipts/*.json: {ref!r}"); continue
        try:
            path = resolve(root, ref, "receipt")
            receipt = read_json(path)
        except ProtocolError as exc: result.errors.append(str(exc)); continue
        label = f"receipt[{ref}]"
        format_errors = receipt_format_errors(receipt)
        if format_errors:
            result.errors.extend(f"{label}: {error}" for error in format_errors)
            continue
        if not (receipt_current(root, receipt, current) if scoped else fingerprint_equal(receipt.get("workspaceFingerprint"), current)):
            result.warnings.append(f"{label}: stale workspace fingerprint; retained only as history")
            continue
        if receipt.get("schemaVersion") != "2.0": result.errors.append(f"{label}: unsupported protocol")
        for field in ("receiptId", "kind", "argv", "tasks", "coveredObligations", "startedAt", "completedAt", "workspaceFingerprint", "exitCode", "log"):
            if field not in receipt: result.errors.append(f"{label}.{field}: required")
        if receipt.get("kind") not in {"targeted", "integration", "final"}: result.errors.append(f"{label}.kind: expected targeted, integration or final")
        if receipt.get("inputScopeId") and receipt.get("kind") != "targeted": result.errors.append(f"{label}: integration/final receipt cannot use scoped inputs")
        if not isinstance(receipt.get("argv"), list) or not receipt.get("argv") or any(not isinstance(v, str) for v in receipt.get("argv", [])): result.errors.append(f"{label}.argv: expected non-empty string array")
        if not isinstance(receipt.get("tasks"), list): result.errors.append(f"{label}.tasks: expected array")
        if not timestamp(receipt.get("startedAt")) or not timestamp(receipt.get("completedAt")): result.errors.append(f"{label}: invalid timestamps")
        elif parse_time(receipt["startedAt"]) > parse_time(receipt["completedAt"]): result.errors.append(f"{label}: completedAt precedes startedAt")
        if not isinstance(receipt.get("exitCode"), int): result.errors.append(f"{label}.exitCode: expected integer")
        if not fingerprint_equal(receipt.get("workspaceFingerprint"), current): result.warnings.append(f"{label}: stale workspace fingerprint")
        log = receipt.get("log")
        if isinstance(log, dict) and isinstance(log.get("path"), str) and isinstance(log.get("sha256"), str):
            try:
                log_path = resolve(root, log["path"], f"{label}.log")
                if not log_path.is_file() or hashlib.sha256(log_path.read_bytes()).hexdigest() != log["sha256"]: result.errors.append(f"{label}.log: missing or hash mismatch")
            except ProtocolError as exc: result.errors.append(str(exc))
        else: result.errors.append(f"{label}.log: requires repository-relative path and sha256")
        coverage = receipt.get("coveredObligations")
        if not isinstance(coverage, list): result.errors.append(f"{label}.coveredObligations: expected array")
        loaded[ref] = receipt
    return loaded

def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise ProtocolError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module); return module

def validate_ledger(project_root: Path, ledger_path: Path, *, closure: bool = True) -> ValidationResult:
    result = ValidationResult(); root = project_root.resolve()
    try: ledger = read_json(ledger_path)
    except ProtocolError as exc: result.errors.append(str(exc)); return result
    if ledger.get("schemaVersion") != "2.0": result.errors.append(f"unsupported protocol: delivery ledger {ledger.get('schemaVersion')!r}")
    if ledger.get("ledgerDigest") != ledger_digest(ledger): result.errors.append("ledgerDigest does not match canonical ledger content")
    app_ref = ledger.get("appSpec") if isinstance(ledger.get("appSpec"), dict) else {}
    try:
        app_root = resolve(root, app_ref.get("root"), "appSpec.root")
        app, app_errors, app_warnings = validate_app_spec(app_root)
        result.errors.extend(f"AppSpec: {v}" for v in app_errors); result.warnings.extend(f"AppSpec: {v}" for v in app_warnings)
        current_app = compute_app_spec_fingerprint(app_root); current_workspace = compute_workspace_fingerprint(root)
    except (ProtocolError, OSError, ValueError) as exc: result.errors.append(str(exc)); return result
    if app is None: return result
    from asset_contract import validate_delivery
    asset_errors, _ = validate_delivery(app, root)
    result.errors.extend(f"Assets: {error}" for error in asset_errors)
    if not fingerprint_equal(app_ref.get("fingerprint"), current_app): result.errors.append("app-spec.fingerprint.stale")
    if not fingerprint_equal(ledger.get("workspaceFingerprint"), current_workspace): result.errors.append("workspace.fingerprint.stale")
    inventory = canonical_inventory(app)
    if ledger.get("canonicalInventory") != inventory: result.errors.append("canonical inventory mismatch")
    if closure:
        for package_id, package in ledger.get("workPackages", {}).items():
            if package.get("status") != "integrated" or not package.get("integrationEvidence") or not package.get("integrationReceiptRef"):
                result.errors.append(f"{package_id}: production flow integration is incomplete")
    pending = pending_handoff_paths(root, ledger)
    if pending: result.errors.append("pending specialist hand-offs must be inspected and ingested: " + ", ".join(pending))
    execution = ledger.get("execution") if isinstance(ledger.get("execution"), dict) else {}
    result.errors.extend(validate_reads(root, ledger))
    if execution.get("phase") not in PHASES: result.errors.append("execution.phase is invalid")
    if not isinstance(execution.get("nextAction"), str) or not execution.get("nextAction").strip(): result.errors.append("execution.nextAction is required")
    if execution.get("scopedInstructions") != discover_scoped_instructions(root): result.errors.append("execution.scopedInstructions is stale")
    checkpoint = execution.get("checkpoint")
    if not isinstance(checkpoint, dict) or not timestamp(checkpoint.get("createdAt")) or not isinstance(checkpoint.get("workspaceFingerprint"), dict): result.errors.append("execution.checkpoint is invalid")

    spec_acs = {item["id"]: item for item in app["acceptanceScenarios"]}
    reqs = {item["id"]: item for item in app["requirements"] if item.get("status") == "approved"}
    spec_gates = {item["id"]: item for item in app["qualityGates"]}
    ledger_acs = {item.get("id"): item for item in ledger.get("acceptanceScenarios", []) if isinstance(item, dict)}
    ledger_gates = {item.get("id"): item for item in ledger.get("qualityGates", []) if isinstance(item, dict)}
    if set(ledger_acs) != set(spec_acs): result.errors.append("acceptanceScenarios inventory mismatch")
    if set(ledger_gates) != set(spec_gates): result.errors.append("qualityGates inventory mismatch")
    for index, handoff in enumerate(ledger.get("ingestedHandoffs", [])):
        label = f"ingestedHandoffs[{index}]"
        if not isinstance(handoff, dict) or not isinstance(handoff.get("path"), str) or not isinstance(handoff.get("sha256"), str):
            result.errors.append(f"{label}: requires path and sha256"); continue
        try:
            handoff_path = resolve(root, handoff["path"], label)
            if not handoff["path"].startswith(".vibe/handoffs/") or not handoff_path.is_file() or hashlib.sha256(handoff_path.read_bytes()).hexdigest() != handoff["sha256"]:
                result.errors.append(f"{label}: immutable hand-off is missing or hash-mismatched")
            elif read_json(handoff_path).get("schemaVersion") != "2.0" or read_json(handoff_path).get("evidenceMode") != "assignment": result.errors.append(f"{label}: unsupported hand-off protocol/format")
        except ProtocolError as exc: result.errors.append(str(exc))
    refs: set[str] = set()
    for item in [*ledger_acs.values(), *ledger_gates.values()]:
        item_refs = item.get("receiptRefs")
        if isinstance(item_refs, list) and all(isinstance(ref, str) for ref in item_refs): refs.update(item_refs)
        else: result.errors.append(f"{item.get('id')}.receiptRefs must be an array of file paths; inline receipts are forbidden")
    if closure and ledger.get("finalReceiptRef") is not None: refs.add(ledger["finalReceiptRef"])
    # A failed run cannot disappear by omitting its ref from the ledger.
    refs.update(path.relative_to(root).as_posix() for path in (root / ".vibe" / "receipts").glob("*.json"))
    receipts = load_receipts(root, refs, current_workspace, result, scoped=not closure)
    receipt_ids = [receipt.get("receiptId") for receipt in receipts.values() if isinstance(receipt.get("receiptId"), str)]
    if len(receipt_ids) != len(set(receipt_ids)): result.errors.append("receiptId values must be unique")
    declared_surfaces = verification_surface_map(app)
    for ref, receipt in receipts.items():
        for index, coverage in enumerate(receipt.get("coveredObligations", []) if isinstance(receipt.get("coveredObligations"), list) else []):
            if not isinstance(coverage, dict) or coverage.get("obligationId") not in declared_surfaces:
                result.errors.append(f"receipt[{ref}].coveredObligations[{index}]: unknown obligation"); continue
            surfaces_value = coverage.get("surfaces")
            if not isinstance(surfaces_value, list) or any(surface not in declared_surfaces[coverage["obligationId"]] for surface in surfaces_value):
                result.errors.append(f"receipt[{ref}].coveredObligations[{index}]: incompatible surface")
    latest: dict[tuple[str, str], tuple[datetime, int]] = {}
    for receipt in receipts.values():
        if not (receipt_current(root, receipt, current_workspace) if not closure else fingerprint_equal(receipt.get("workspaceFingerprint"), current_workspace)): continue
        if not timestamp(receipt.get("completedAt")): continue
        completed = parse_time(receipt["completedAt"])
        outcome = receipt.get("exitCode") if receipt.get("executionStatus") == "completed" and (receipt_stable(receipt) if not closure else fingerprint_equal(receipt.get("startWorkspaceFingerprint"), receipt.get("workspaceFingerprint"))) else 1
        for coverage in receipt.get("coveredObligations", []) if isinstance(receipt.get("coveredObligations"), list) else []:
            if not isinstance(coverage, dict): continue
            obligation_id = coverage.get("obligationId")
            for surface in coverage.get("surfaces", []) if isinstance(coverage.get("surfaces"), list) else []:
                key = (obligation_id, surface)
                if key not in latest or completed > latest[key][0]: latest[key] = (completed, outcome)
                elif completed == latest[key][0] and outcome != 0: latest[key] = (completed, outcome)

    def validate_item(item_id: str, item: dict, required_surfaces: list[str], *, gate: dict | None = None) -> None:
        status = item.get("status")
        if status not in STATUSES: result.errors.append(f"{item_id}.status is invalid"); return
        if gate is None and status == "blocked-external": result.errors.append(f"{item_id}: acceptance scenarios cannot be blocked-external")
        if gate is not None and status == "blocked-external" and gate.get("category") not in {"platform", "external", "release"}: result.errors.append(f"{item_id}: blocked-external is limited to platform/external/release gates")
        if status == "blocked-external" and not isinstance(item.get("blocker"), dict): result.errors.append(f"{item_id}: blocked-external requires blocker metadata")
        if status == "in-progress":
            for field_name in ("owner", "fileBoundaries", "baselineFingerprint", "checkpointFingerprint", "changedFiles", "pendingChecks", "handoffRefs", "blockers", "startedAt", "updatedAt"):
                if field_name not in item: result.errors.append(f"{item_id}.{field_name} is required while in-progress")
            if not item.get("fileBoundaries"): result.errors.append(f"{item_id}.fileBoundaries must be non-empty while in-progress")
        if status == "waived" and not decision_valid(root, item.get("decisionReference") or item.get("waiver", {}).get("decisionReference"), item_id): result.errors.append(f"{item_id}: waiver lacks an accepted scoped durable decision with user approval")
        if status in {"verified", "waived"} and (item.get("blockers") or item.get("blocker") or item.get("pendingChecks")): result.errors.append(f"{item_id}: closed item retains blockers or pending checks")
        production = evidence_ok(root, item.get("productionEvidence"), f"{item_id}.productionEvidence", result)
        tests = evidence_ok(root, item.get("testEvidence"), f"{item_id}.testEvidence", result)
        if item.get("requiredVerificationSurfaces") != required_surfaces: result.errors.append(f"{item_id}.requiredVerificationSurfaces does not match AppSpec")
        if status == "verified":
            if not production: result.errors.append(f"{item_id}: verified without production evidence")
            if not tests: result.errors.append(f"{item_id}: verified without test evidence")
            test_surfaces = {entry.get("surface") for entry in tests}
            for surface in required_surfaces:
                if surface not in test_surfaces: result.errors.append(f"{item_id}: missing test evidence for surface {surface}")
                if latest.get((item_id, surface), ("", 1))[1] != 0: result.errors.append(f"{item_id}: latest current receipt for surface {surface} is absent or failed")

    for ac_id, spec_item in spec_acs.items():
        item = ledger_acs.get(ac_id)
        if not item: continue
        expected = {"requirementId": spec_item["requirementId"], "priority": reqs[spec_item["requirementId"]]["priority"], "flowId": spec_item["flowId"], "screenIds": spec_item["screenIds"], "dependsOnAcceptanceScenarioIds": spec_item["dependsOnAcceptanceScenarioIds"]}
        for key, value in expected.items():
            if item.get(key) != value: result.errors.append(f"{ac_id}.{key} does not match AppSpec")
        validate_item(ac_id, item, spec_item["verificationSurfaces"])
    for gate_id, spec_item in spec_gates.items():
        item = ledger_gates.get(gate_id)
        if not item: continue
        for key in ("category", "platform", "requirement", "verificationMethod", "contractSource"):
            if item.get(key) != spec_item.get(key): result.errors.append(f"{gate_id}.{key} does not match AppSpec")
        if spec_item["requirement"] == "required" and item.get("applicability") != "applicable": result.errors.append(f"{gate_id}: required gate must be applicable")
        if item.get("applicability") == "not-applicable" and not str(item.get("applicabilityReason", "")).strip(): result.errors.append(f"{gate_id}.applicabilityReason is required")
        validate_item(gate_id, item, spec_item["verificationSurfaces"], gate=spec_item)

    applicable_ids = {aid for aid, item in ledger_acs.items() if item.get("status") == "verified"} | {gid for gid, item in ledger_gates.items() if item.get("applicability") == "applicable" and item.get("status") == "verified"}
    applicable_pairs = {(item_id, surface) for item_id in applicable_ids for surface in (spec_acs.get(item_id) or spec_gates[item_id])["verificationSurfaces"]}
    final_ref = ledger.get("finalReceiptRef")
    final_receipt = receipts.get(final_ref) if isinstance(final_ref, str) else None
    final_ok = False
    if closure and final_receipt:
        covered = {(c.get("obligationId"), s) for c in final_receipt.get("coveredObligations", []) if isinstance(c, dict) for s in c.get("surfaces", []) if isinstance(s, str)}
        final_ok = final_receipt.get("kind") == "final" and final_receipt.get("exitCode") == 0 and final_receipt.get("executionStatus") == "completed" and fingerprint_equal(final_receipt.get("startWorkspaceFingerprint"), current_workspace) and fingerprint_equal(final_receipt.get("workspaceFingerprint"), current_workspace) and applicable_pairs <= covered
        if not final_ok: result.errors.append("final receipt failed, is stale, or does not cover every applicable obligation/surface")
    current_finals = [receipt for receipt in receipts.values() if receipt.get("kind") == "final" and fingerprint_equal(receipt.get("workspaceFingerprint"), current_workspace)]
    all_ac_closed = all(item.get("status") in {"verified", "waived"} for item in ledger_acs.values())
    implementation_gates = [item for item in ledger_gates.values() if item.get("readinessScope") == "implementation"]
    implementation_closed = all_ac_closed and all(item.get("applicability") == "not-applicable" or (item.get("applicability") == "applicable" and item.get("status") in {"verified", "waived"}) for item in implementation_gates)
    all_gates_closed = all(item.get("applicability") == "not-applicable" or item.get("status") in {"verified", "waived"} for item in ledger_gates.values())
    if closure and implementation_closed and not final_ok: result.errors.append("completion requires one successful current final receipt")

    audit_ok = False
    audit_ref = ledger.get("closureAudit", {}).get("auditPath") if isinstance(ledger.get("closureAudit"), dict) else None
    if closure and implementation_closed:
        if not audit_ref: result.errors.append("completion requires a closure audit")
        else:
            try:
                audit_path = resolve(root, audit_ref, "closureAudit.auditPath")
                auditor_script = Path(__file__).resolve().parents[2] / "vibe-acceptance-auditor" / "scripts" / "validate-closure-audit.py"
                auditor = _load_module(auditor_script, "vibe_protocol_audit_validator")
                audit_data = read_json(audit_path)
                request_path = resolve(root, ledger["closureAudit"].get("requestPath"), "closureAudit.requestPath")
                if audit_path != audit_paths(root, request_path)[0]: result.errors.append("audit path does not match current attempt")
                if hashlib.sha256(request_path.read_bytes()).hexdigest() != ledger["closureAudit"].get("requestSha256"):
                    result.errors.append("closureAudit.requestSha256 does not match immutable request")
                audit_errors = auditor.validate(audit_data, app_root, root, request_path)
                result.errors.extend(f"closureAudit: {error}" for error in audit_errors)
                audit_ok = not audit_errors and audit_data.get("verdict") == "PASS"
                if final_receipt and timestamp(final_receipt.get("startedAt")) and timestamp(audit_data.get("completedAt")):
                    if parse_time(final_receipt["startedAt"]) < parse_time(audit_data["completedAt"]): result.errors.append("final receipt must start after audit completion")
            except (ProtocolError, OSError, ValueError, KeyError) as exc: result.errors.append(f"closureAudit: {exc}")

    final_phase = execution.get("phase") in {"final-verification", "complete"} or implementation_closed
    if closure and final_phase:
        try:
            delivery_renderer = _load_module(Path(__file__).with_name("render-delivery-report.py"), "vibe_delivery_renderer")
            expected_delivery = delivery_renderer.render_report(ledger)
            delivery_path = root / "docs" / "requirement-traceability.generated.md"
            if not delivery_path.is_file() or delivery_path.read_text(encoding="utf-8-sig") != expected_delivery: result.errors.append("generated delivery report is missing or stale")
            if audit_ref:
                audit_renderer = _load_module(Path(__file__).resolve().parents[2] / "vibe-acceptance-auditor" / "scripts" / "render-closure-audit.py", "vibe_audit_renderer")
                audit_data = read_json(resolve(root, audit_ref, "closureAudit.auditPath"))
                expected_audit = audit_renderer.render(audit_data)
                audit_report = root / "docs" / "closure-audit.generated.md"
                if not audit_report.is_file() or audit_report.read_text(encoding="utf-8-sig") != expected_audit: result.errors.append("generated closure report is missing or stale")
        except (ProtocolError, OSError, ValueError, KeyError, TypeError) as exc: result.errors.append(f"generated report validation failed: {exc}")

    result.implementation_complete = closure and implementation_closed and final_ok and audit_ok and fingerprint_equal(app_ref.get("fingerprint"), current_app) and fingerprint_equal(ledger.get("workspaceFingerprint"), current_workspace) and not result.errors
    result.release_ready = result.implementation_complete and all_gates_closed and all(item.get("status") != "blocked-external" for item in ledger_gates.values())
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require", choices=("implementation-complete", "release-ready"))
    args = parser.parse_args(); root = args.project_root.resolve(); ledger = (args.ledger or root / ".vibe" / "delivery-ledger.json").resolve()
    try: result = validate_ledger(root, ledger)
    except Exception as exc: result = ValidationResult(errors=[f"aggregate validator failure: {exc}"])
    if args.json: print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for warning in result.warnings: print(f"WARNING: {warning}")
        for error in result.errors: print(f"ERROR: {error}")
        print(f"implementation-complete: {'YES' if result.implementation_complete else 'NO'}")
        print(f"release-ready: {'YES' if result.release_ready else 'NO'}")
    required = result.implementation_complete if args.require == "implementation-complete" else result.release_ready if args.require == "release-ready" else True
    return 0 if result.valid and required else 1

if __name__ == "__main__": raise SystemExit(main())
