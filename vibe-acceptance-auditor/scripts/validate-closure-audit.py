#!/usr/bin/env python3
"""Validate a closure audit 2.0 against its request and canonical AppSpec inventory."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

DEVELOPER_SCRIPTS = Path(__file__).resolve().parents[2] / "vibe-developer" / "scripts"
if str(DEVELOPER_SCRIPTS) not in sys.path: sys.path.insert(0, str(DEVELOPER_SCRIPTS))
from vibe_protocol import canonical_inventory, compute_app_spec_fingerprint, compute_workspace_fingerprint, fingerprint_equal, read_json, validate_app_spec, valid_time, parse_time, decision_valid, audit_paths, ProtocolError
from audit_evidence import validate_launch, validate_source_coverage, validate_check_receipt
from vibe_protocol import verification_surface_map

def timestamp(value: Any) -> bool:
    return valid_time(value)

def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def expected_surface_map(app: dict) -> dict[str, list[str]]:
    return verification_surface_map(app)

def validate(data: dict[str, Any], app_root: Path, repository: Path, request_path: Path) -> list[str]:
    errors: list[str] = []
    try: audit_paths(repository, request_path)
    except ProtocolError as exc: errors.append(str(exc))
    app, app_errors, _ = validate_app_spec(app_root)
    errors.extend(f"AppSpec: {error}" for error in app_errors)
    if app is None: return errors
    current_app = compute_app_spec_fingerprint(app_root)
    current_workspace = compute_workspace_fingerprint(repository)
    request = read_json(request_path)
    request_hash = hashlib.sha256(request_path.read_bytes()).hexdigest()
    if data.get("schemaVersion") != "2.0": errors.append("unsupported protocol: closure audit must be 2.0")
    if request.get("schemaVersion") != "2.0": errors.append("unsupported protocol: audit request must be 2.0")
    for field in ("auditId", "auditRequest", "auditorContext", "startedAt", "completedAt", "verdict", "appSpecFingerprint", "workspaceFingerprint", "shadowInventory", "obligations", "checks", "findings", "completion"):
        if field not in data: errors.append(f"missing required field: {field}")
    binding = data.get("auditRequest", {})
    if binding.get("requestId") != request.get("requestId"): errors.append("auditRequest.requestId does not match immutable request")
    if binding.get("sha256") != request_hash: errors.append("auditRequest.sha256 does not match request bytes")
    if binding.get("path") != request_path.resolve().relative_to(repository.resolve()).as_posix(): errors.append("auditRequest.path must match this attempt")
    if request.get("requestId") != request_path.parent.name: errors.append("request ID must match attempt directory")
    context = data.get("auditorContext", {})
    if context.get("contextId") != request.get("requiredAuditorContextId"): errors.append("auditorContext.contextId does not match request")
    if context.get("invocationKind") != request.get("invocationKind"): errors.append("auditorContext.invocationKind does not match request")
    if context.get("implementationContextAvailable") is not False or request.get("implementationContextAvailable") is not False:
        errors.append("implementationContextAvailable must be false")
    if not timestamp(data.get("startedAt")) or not timestamp(data.get("completedAt")): errors.append("audit start/completion timestamps must be RFC3339")
    if timestamp(data.get("startedAt")) and timestamp(data.get("completedAt")) and parse_time(data["startedAt"]) > parse_time(data["completedAt"]): errors.append("audit completedAt precedes startedAt")
    if not timestamp(request.get("createdAt")): errors.append("request creation timestamp is invalid")
    elif timestamp(data.get("startedAt")) and parse_time(data["startedAt"]) < parse_time(request["createdAt"]): errors.append("audit started before its request")
    for label, actual, expected in (("AppSpec", data.get("appSpecFingerprint"), current_app), ("workspace", data.get("workspaceFingerprint"), current_workspace)):
        if not fingerprint_equal(actual, expected): errors.append(f"stale {label} fingerprint")
    if not fingerprint_equal(request.get("appSpecFingerprint"), current_app): errors.append("stale audit request AppSpec fingerprint")
    if not fingerprint_equal(request.get("workspaceFingerprint"), current_workspace): errors.append("stale audit request workspace fingerprint")
    inventory = canonical_inventory(app)
    if data.get("shadowInventory") != inventory: errors.append("shadowInventory does not match independently derived canonical inventory")
    surfaces = expected_surface_map(app)
    expected_ids = set(surfaces)
    errors.extend(validate_source_coverage(data, app_root, expected_ids))
    errors.extend(validate_launch(repository, request_path, request, data))
    obligations = data.get("obligations") if isinstance(data.get("obligations"), list) else []
    by_id: dict[str, dict] = {}
    for index, item in enumerate(obligations):
        if not isinstance(item, dict) or not nonempty(item.get("id")): errors.append(f"obligations[{index}].id is required"); continue
        if item["id"] in by_id: errors.append(f"duplicate obligation: {item['id']}")
        by_id[item["id"]] = item
    if set(by_id) != expected_ids: errors.append(f"obligation inventory mismatch; missing={sorted(expected_ids-set(by_id))}, extra={sorted(set(by_id)-expected_ids)}")
    from validation_context import ValidationContext
    metadata_path = repository / '.vibe/delivery-ledger.json'
    metadata = read_json(metadata_path) if metadata_path.exists() else {'appSpec':{'root':str(app_root)}}
    validation = ValidationContext(repository, metadata)
    successful_pairs: set[tuple[str, str]] = set()
    checks = data.get("checks") if isinstance(data.get("checks"), list) else []
    for index, check in enumerate(checks):
        prefix = f"checks[{index}]"
        if not isinstance(check, dict): errors.append(f"{prefix} must be an object"); continue
        receipt_errors = validate_check_receipt(check, repository)
        errors.extend(f"{prefix}: {error}" for error in receipt_errors)
        if not nonempty(check.get("checkId")) or not isinstance(check.get("argv"), list) or not check.get("argv"): errors.append(f"{prefix} requires checkId and argv")
        if not timestamp(check.get("startedAt")) or not timestamp(check.get("completedAt")): errors.append(f"{prefix} requires timestamps")
        elif timestamp(data.get("startedAt")) and timestamp(data.get("completedAt")):
            if not parse_time(check["startedAt"]) <= parse_time(check["completedAt"]) <= parse_time(data["completedAt"]): errors.append(f"{prefix} has invalid execution time")
        actual_receipt = validation.receipts.get(check.get('receiptRef'))
        if not actual_receipt or not validation.current(actual_receipt): errors.append(f'{prefix} has stale workspace fingerprint')
        if not fingerprint_equal(check.get('startWorkspaceFingerprint'), check.get('workspaceFingerprint')): errors.append(f'{prefix} missing start fingerprint or workspace changed during check')
        if check.get("executionStatus") != "completed": errors.append(f"{prefix} was interrupted or did not complete")
        coverage = check.get("coverage") if isinstance(check.get("coverage"), list) else []
        if check.get("exitCode") == 0 and not receipt_errors:
            for pair in coverage:
                if isinstance(pair, dict) and pair.get("obligationId") in expected_ids and pair.get("surface") in surfaces[pair["obligationId"]]:
                    if (pair['obligationId'], pair['surface']) not in validation.coverage(actual_receipt): continue
                    latest = validation.latest.get((pair['obligationId'], pair['surface']))
                    if latest and latest[0][1]: errors.append(f'{prefix}: later current check failed')
                    else: successful_pairs.add((pair["obligationId"], pair["surface"]))
        elif not isinstance(check.get("exitCode"), int): errors.append(f"{prefix}.exitCode must be an integer")
    unavailable = {(r["obligationId"], r["surface"]) for r in request.get("unavailablePairs", [])}
    blocking = []
    gate_categories = {g["id"]: g["category"] for g in app["qualityGates"]}
    for row in request.get("unavailablePairs", []):
        oid, surface = row.get("obligationId"), row.get("surface")
        if surface not in surfaces.get(oid, []) or (surface not in {"ios-link-test", "ios-build"} and gate_categories.get(oid) not in {"platform", "external", "release"}):
            errors.append("invalid external verification limitation")
    for obligation_id, required_surfaces in surfaces.items():
        item = by_id.get(obligation_id)
        if not item: continue
        result = item.get("result")
        if result not in {"verified", "locally-verified", "waived", "blocked-external", "gap"}: errors.append(f"obligation {obligation_id} has invalid result"); continue
        if result == "blocked-external" and gate_categories.get(obligation_id) not in {"platform", "external", "release"}: errors.append(f"obligation {obligation_id} cannot be blocked-external")
        if result == "waived" and not decision_valid(repository, item.get("decisionReference"), obligation_id): errors.append(f"obligation {obligation_id} waiver lacks an accepted scoped durable decision with user approval")
        if item.get("verificationSurfaces") != required_surfaces: errors.append(f"obligation {obligation_id} verificationSurfaces mismatch")
        evidence = item.get("evidence") if isinstance(item.get("evidence"), list) else []
        if result == 'locally-verified' and not any((obligation_id, s) in unavailable for s in required_surfaces):
            errors.append(f'obligation {obligation_id}: local result lacks request-bound host limitation')
        if result in {'verified', 'locally-verified'}:
            for surface in required_surfaces:
                if result == 'locally-verified' and (obligation_id, surface) in unavailable: continue
                matching = [e for e in evidence if isinstance(e, dict) and e.get("surface") == surface and nonempty(e.get("path"))]
                if not matching: errors.append(f"obligation {obligation_id} surface {surface} has no evidence")
                for entry in matching:
                    path = Path(entry["path"])
                    target = repository / path
                    if path.is_absolute() or ".." in path.parts or not target.is_file(): errors.append(f"obligation {obligation_id} evidence path is invalid: {entry['path']}")
                    elif entry.get("anchor"):
                        from evidence_registry import check_anchor
                        try: check_anchor(repository, entry)
                        except (ProtocolError, OSError, ValueError) as exc: errors.append(str(exc))
                    elif entry.get("symbol") or entry.get("testName"):
                        needle = entry.get("symbol") or entry.get("testName")
                        try:
                            if needle not in target.read_text(encoding="utf-8-sig"): errors.append(f"obligation {obligation_id} evidence symbol/testName not found: {needle}")
                        except (OSError, UnicodeError): errors.append(f"obligation {obligation_id} evidence cannot be inspected: {entry['path']}")
                if (obligation_id, surface) not in successful_pairs: errors.append(f"obligation {obligation_id} surface {surface} has no successful audit-time check")
        if result in {"gap"} or (result == "blocked-external" and gate_categories.get(obligation_id) == "repository"):
            blocking.append(obligation_id)
    verdict = data.get("verdict")
    if verdict == "PASS" and data.get("findings"): errors.append("PASS requires all findings to be resolved in a new audit")
    if verdict not in {"PASS", "GAPS", "BLOCKED"}: errors.append("verdict must be PASS, GAPS, or BLOCKED")
    if verdict == "PASS" and (blocking or any(isinstance(c, dict) and c.get("exitCode") != 0 for c in checks)): errors.append("PASS conflicts with gaps or failed audit checks")
    if verdict == "GAPS" and not any(i.get("result") == "gap" for i in obligations if isinstance(i, dict)): errors.append("GAPS requires a gap obligation")
    completion = data.get("completion", {})
    implementation = all(by_id.get(i, {}).get("result") in {"verified", "waived"} for i in expected_ids if gate_categories.get(i, "repository") == "repository")
    release = implementation and all(by_id.get(i, {}).get("result") in {"verified", "waived"} for i in expected_ids)
    local = not blocking and all(by_id.get(i, {}).get('result') in {'verified', 'waived', 'locally-verified'} or
        (by_id.get(i, {}).get('result') == 'blocked-external' and gate_categories.get(i) in {'platform', 'external', 'release'}) for i in expected_ids)
    if completion != {"locallyVerified": local, "implementationComplete": implementation, "releaseReady": release}: errors.append("completion does not match audited obligations")
    if verdict == "PASS" and not local: errors.append("PASS requires locallyVerified")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    parser.add_argument("--app-spec-root", type=Path, required=True)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--audit-request", type=Path)
    args = parser.parse_args()
    try:
        data = read_json(args.audit)
        request = (args.audit_request or args.audit.with_name("request.json")).resolve()
        errors = validate(data, args.app_spec_root.resolve(), args.repository.resolve(), request)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2
    for error in errors: print(f"ERROR: {error}", file=sys.stderr)
    if errors: return 1
    print(f"OK: {args.audit} ({data['verdict']})")
    return 0

if __name__ == "__main__": raise SystemExit(main())
