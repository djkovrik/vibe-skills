#!/usr/bin/env python3
"""Create an immutable closure audit request and bind it into the ledger."""

from __future__ import annotations

import argparse
import hashlib
import sys
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(SCRIPT_DIR))

from vibe_protocol import ProtocolError, atomic_write_json, canonical_inventory, compute_app_spec_fingerprint, compute_workspace_fingerprint, fingerprint_equal, ledger_digest, read_json, update_ledger_atomic, utc_now, validate_app_spec, audit_paths

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--expected-ledger-digest", required=True)
    parser.add_argument("--auditor-context-id", required=True)
    parser.add_argument("--request-id", help="Reuse this ID to recover an interrupted request creation")
    parser.add_argument("--invocation-kind", default="fresh-context", choices=("fresh-context", "isolated-agent"))
    args = parser.parse_args()
    root = args.project_root.resolve()
    ledger_path = (args.ledger or root / ".vibe" / "delivery-ledger.json").resolve()
    request_id = args.request_id or f"AUDIT-REQUEST-{uuid.uuid4()}"
    import re
    if not re.fullmatch(r"AUDIT-REQUEST-[A-Za-z0-9-]+", request_id):
        parser.error("invalid request ID")
    request_path = root / ".vibe" / "audits" / request_id / "request.json"
    try:
        # Artifact creation and binding share the ledger lock. An orphan from a
        # terminated writer can be rebound with its unchanged ID/digest.
        def mutate(ledger: dict) -> None:
            nonlocal request_hash
            request_hash = prepare_request(root, ledger, request_path, request_id, args)
        request_hash = ""
        updated = update_ledger_atomic(ledger_path, args.expected_ledger_digest, mutate)
    except (ProtocolError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"created: {request_path}")
    print(f"request-sha256: {request_hash}")
    print(f"ledger-digest: {updated['ledgerDigest']}")
    return 0


def prepare_request(root, ledger, request_path, request_id, args):
    app_root_value = ledger.get("appSpec", {}).get("root")
    app_root = Path(app_root_value) if Path(app_root_value).is_absolute() else root / app_root_value
    app, app_errors, _ = validate_app_spec(app_root)
    if app_errors or app is None: raise ProtocolError("invalid AppSpec 2.0: " + "; ".join(app_errors))
    if ledger.get("canonicalInventory") != canonical_inventory(app): raise ProtocolError("canonical inventory mismatch")
    current_workspace = compute_workspace_fingerprint(root)
    current_app = compute_app_spec_fingerprint(app_root)
    if not fingerprint_equal(ledger.get("appSpec", {}).get("fingerprint"), current_app): raise ProtocolError("AppSpec fingerprint is stale; reconcile-spec first")
    if not fingerprint_equal(ledger.get("execution", {}).get("checkpoint", {}).get("workspaceFingerprint"), current_workspace): raise ProtocolError("checkpoint is stale; checkpoint immediately before requesting audit")
    if any(item.get("status") not in {"verified", "waived"} for item in ledger.get("acceptanceScenarios", [])): raise ProtocolError("all acceptance scenarios must be verified or waived before audit")
    for gate in ledger.get("qualityGates", []):
        if gate.get("category") == "repository" and not (gate.get("applicability") == "not-applicable" or (gate.get("applicability") == "applicable" and gate.get("status") in {"verified", "waived"})):
            raise ProtocolError(f"repository gate is not closed: {gate.get('id')}")
    ingested = {item.get("sha256") for item in ledger.get("ingestedHandoffs", []) if isinstance(item, dict)}
    if any(hashlib.sha256(path.read_bytes()).hexdigest() not in ingested for path in (root / ".vibe" / "handoffs").glob("*.json")):
        raise ProtocolError("pending specialist hand-offs must be inspected and ingested before audit")
    # Validate all local evidence without depending on the audit we are creating.
    import importlib.util
    spec = importlib.util.spec_from_file_location("preaudit_validator", SCRIPT_DIR / "validate-delivery-ledger.py")
    validator = importlib.util.module_from_spec(spec); sys.modules[spec.name] = validator; spec.loader.exec_module(validator)
    check = validator.validate_ledger(root, (args.ledger or root / ".vibe" / "delivery-ledger.json").resolve(), closure=False)
    if check.errors: raise ProtocolError("pre-audit validation failed: " + "; ".join(check.errors))
    request = {
        "schemaVersion": "2.0", "requestId": request_id,
        "createdAt": utc_now(), "ledgerDigest": ledger["ledgerDigest"],
        "appSpecFingerprint": current_app, "workspaceFingerprint": current_workspace,
        "requiredAuditorContextId": args.auditor_context_id,
        "invocationKind": args.invocation_kind, "implementationContextAvailable": False,
    }
    if request_path.exists():
        existing = read_json(request_path)
        if {k:v for k,v in existing.items() if k != "createdAt"} != {k:v for k,v in request.items() if k != "createdAt"}:
            raise ProtocolError("orphan request does not match current state; use a new request ID")
        request = existing
    else:
        atomic_write_json(request_path, request, refuse_existing=True)
    request_hash = hashlib.sha256(request_path.read_bytes()).hexdigest()
    if ledger.get("closureAudit", {}).get("requestPath"):
        ledger.setdefault("auditHistory", []).append(ledger["closureAudit"])
    audit_path, _ = audit_paths(root, request_path)
    ledger["closureAudit"] = {"requestPath": request_path.relative_to(root).as_posix(), "requestSha256": request_hash, "auditPath": audit_path.relative_to(root).as_posix()}
    ledger["finalReceiptRef"] = None
    ledger["execution"].update(phase="auditing", activeAcceptanceScenarioId=None, activeQualityGateId=None,
        nextAction=f"Run run-acceptance-audit.py for {request_path.relative_to(root).as_posix()}.")
    ledger["workspaceFingerprint"] = current_workspace
    ledger["updatedAt"] = utc_now()
    return request_hash

if __name__ == "__main__":
    raise SystemExit(main())
