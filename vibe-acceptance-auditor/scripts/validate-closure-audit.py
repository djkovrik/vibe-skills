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
from vibe_protocol import canonical_inventory, compute_app_spec_fingerprint, compute_workspace_fingerprint, fingerprint_equal, read_json, validate_app_spec

def timestamp(value: Any) -> bool:
    if not isinstance(value, str): return False
    try: datetime.fromisoformat(value.replace("Z", "+00:00")); return True
    except ValueError: return False

def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def durable_reference(root: Path, value: Any) -> bool:
    if not nonempty(value): return False
    path_text, _, anchor = value.partition("#")
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts: return False
    target = root / path
    if not target.is_file(): return False
    if anchor:
        try: return anchor.casefold() in target.read_text(encoding="utf-8-sig").casefold()
        except (OSError, UnicodeError): return False
    return True

def expected_surface_map(app: dict) -> dict[str, list[str]]:
    result = {item["id"]: item["verificationSurfaces"] for item in app["acceptanceScenarios"]}
    result.update({item["id"]: item["verificationSurfaces"] for item in app["qualityGates"]})
    by_ac = {item["id"]: item for item in app["acceptanceScenarios"]}
    for entity in app.get("managedEntities", []):
        for operation, decision in entity["operations"].items():
            if decision.get("status") == "required":
                surfaces = sorted({surface for ac in decision["acceptanceScenarioIds"] for surface in by_ac[ac]["verificationSurfaces"]})
                result[f"{entity['entity']}:{operation}"] = surfaces
    return result

def validate(data: dict[str, Any], app_root: Path, repository: Path, request_path: Path) -> list[str]:
    errors: list[str] = []
    if request_path.resolve() != (repository / ".vibe" / "audit-request.json").resolve(): errors.append("audit request must be .vibe/audit-request.json")
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
    if binding.get("path") != ".vibe/audit-request.json": errors.append("auditRequest.path must be .vibe/audit-request.json")
    context = data.get("auditorContext", {})
    if context.get("contextId") != request.get("requiredAuditorContextId"): errors.append("auditorContext.contextId does not match request")
    if context.get("invocationKind") != request.get("invocationKind"): errors.append("auditorContext.invocationKind does not match request")
    if context.get("implementationContextAvailable") is not False or request.get("implementationContextAvailable") is not False:
        errors.append("implementationContextAvailable must be false")
    if not timestamp(data.get("startedAt")) or not timestamp(data.get("completedAt")): errors.append("audit start/completion timestamps must be RFC3339")
    if timestamp(data.get("startedAt")) and timestamp(data.get("completedAt")) and data["startedAt"] > data["completedAt"]: errors.append("audit completedAt precedes startedAt")
    if timestamp(data.get("startedAt")) and timestamp(request.get("createdAt")) and data["startedAt"] < request["createdAt"]: errors.append("audit started before its request")
    for label, actual, expected in (("AppSpec", data.get("appSpecFingerprint"), current_app), ("workspace", data.get("workspaceFingerprint"), current_workspace)):
        if not fingerprint_equal(actual, expected): errors.append(f"stale {label} fingerprint")
    if not fingerprint_equal(request.get("appSpecFingerprint"), current_app): errors.append("stale audit request AppSpec fingerprint")
    if not fingerprint_equal(request.get("workspaceFingerprint"), current_workspace): errors.append("stale audit request workspace fingerprint")
    inventory = canonical_inventory(app)
    if data.get("shadowInventory") != inventory: errors.append("shadowInventory does not match independently derived canonical inventory")
    surfaces = expected_surface_map(app)
    expected_ids = set(surfaces)
    obligations = data.get("obligations") if isinstance(data.get("obligations"), list) else []
    by_id: dict[str, dict] = {}
    for index, item in enumerate(obligations):
        if not isinstance(item, dict) or not nonempty(item.get("id")): errors.append(f"obligations[{index}].id is required"); continue
        if item["id"] in by_id: errors.append(f"duplicate obligation: {item['id']}")
        by_id[item["id"]] = item
    if set(by_id) != expected_ids: errors.append(f"obligation inventory mismatch; missing={sorted(expected_ids-set(by_id))}, extra={sorted(set(by_id)-expected_ids)}")
    successful_pairs: set[tuple[str, str]] = set()
    checks = data.get("checks") if isinstance(data.get("checks"), list) else []
    for index, check in enumerate(checks):
        prefix = f"checks[{index}]"
        if not isinstance(check, dict): errors.append(f"{prefix} must be an object"); continue
        if not nonempty(check.get("checkId")) or not isinstance(check.get("argv"), list) or not check.get("argv"): errors.append(f"{prefix} requires checkId and argv")
        if not timestamp(check.get("startedAt")) or not timestamp(check.get("completedAt")): errors.append(f"{prefix} requires timestamps")
        if not fingerprint_equal(check.get("workspaceFingerprint"), current_workspace): errors.append(f"{prefix} has stale workspace fingerprint")
        coverage = check.get("coverage") if isinstance(check.get("coverage"), list) else []
        if check.get("exitCode") == 0:
            for pair in coverage:
                if isinstance(pair, dict) and pair.get("obligationId") in expected_ids and pair.get("surface") in surfaces[pair["obligationId"]]:
                    successful_pairs.add((pair["obligationId"], pair["surface"]))
        elif not isinstance(check.get("exitCode"), int): errors.append(f"{prefix}.exitCode must be an integer")
    blocking = []
    gate_categories = {g["id"]: g["category"] for g in app["qualityGates"]}
    for obligation_id, required_surfaces in surfaces.items():
        item = by_id.get(obligation_id)
        if not item: continue
        result = item.get("result")
        if result not in {"verified", "waived", "blocked-external", "gap"}: errors.append(f"obligation {obligation_id} has invalid result"); continue
        if result == "blocked-external" and gate_categories.get(obligation_id) not in {"platform", "external", "release"}: errors.append(f"obligation {obligation_id} cannot be blocked-external")
        if result == "waived" and not durable_reference(repository, item.get("decisionReference")): errors.append(f"obligation {obligation_id} waiver lacks an existing durable decision")
        if item.get("verificationSurfaces") != required_surfaces: errors.append(f"obligation {obligation_id} verificationSurfaces mismatch")
        evidence = item.get("evidence") if isinstance(item.get("evidence"), list) else []
        if result == "verified":
            for surface in required_surfaces:
                matching = [e for e in evidence if isinstance(e, dict) and e.get("surface") == surface and nonempty(e.get("path"))]
                if not matching: errors.append(f"obligation {obligation_id} surface {surface} has no evidence")
                for entry in matching:
                    path = Path(entry["path"])
                    target = repository / path
                    if path.is_absolute() or ".." in path.parts or not target.is_file(): errors.append(f"obligation {obligation_id} evidence path is invalid: {entry['path']}")
                    elif entry.get("symbol") or entry.get("testName"):
                        needle = entry.get("symbol") or entry.get("testName")
                        try:
                            if needle not in target.read_text(encoding="utf-8-sig"): errors.append(f"obligation {obligation_id} evidence symbol/testName not found: {needle}")
                        except (OSError, UnicodeError): errors.append(f"obligation {obligation_id} evidence cannot be inspected: {entry['path']}")
                if (obligation_id, surface) not in successful_pairs: errors.append(f"obligation {obligation_id} surface {surface} has no successful audit-time check")
        if result in {"gap"} or (result == "blocked-external" and gate_categories.get(obligation_id) == "repository"):
            blocking.append(obligation_id)
    verdict = data.get("verdict")
    if verdict not in {"PASS", "GAPS", "BLOCKED"}: errors.append("verdict must be PASS, GAPS, or BLOCKED")
    if verdict == "PASS" and (blocking or any(isinstance(c, dict) and c.get("exitCode") != 0 for c in checks)): errors.append("PASS conflicts with gaps or failed audit checks")
    if verdict == "GAPS" and not any(i.get("result") == "gap" for i in obligations if isinstance(i, dict)): errors.append("GAPS requires a gap obligation")
    completion = data.get("completion", {})
    implementation = all(by_id.get(i, {}).get("result") in {"verified", "waived"} for i in expected_ids if gate_categories.get(i, "repository") == "repository")
    release = implementation and all(by_id.get(i, {}).get("result") in {"verified", "waived"} for i in expected_ids)
    if completion != {"implementationComplete": implementation, "releaseReady": release}: errors.append("completion does not match audited obligations")
    if verdict == "PASS" and not implementation: errors.append("PASS requires implementationComplete")
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
        request = (args.audit_request or args.repository / ".vibe" / "audit-request.json").resolve()
        errors = validate(data, args.app_spec_root.resolve(), args.repository.resolve(), request)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2
    for error in errors: print(f"ERROR: {error}", file=sys.stderr)
    if errors: return 1
    print(f"OK: {args.audit} ({data['verdict']})")
    return 0

if __name__ == "__main__": raise SystemExit(main())
