#!/usr/bin/env python3
"""Adopt an explicitly approved AppSpec revision without discarding delivery history."""
import argparse
import importlib.util
import sys
import uuid
from pathlib import Path
from vibe_protocol import ProtocolError, atomic_write_json, decision_valid, update_ledger_atomic, utc_now, fingerprint_equal


def reconcile(ledger, root, app_root, decision):
    if not decision_valid(root, decision, "AppSpec", "spec-change"):
        raise ProtocolError("AppSpec revision requires an accepted spec-change decision scoped to AppSpec")
    spec = importlib.util.spec_from_file_location("reconcile_init", Path(__file__).with_name("init-delivery-ledger.py"))
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    fresh = module.create_ledger(app_root, root)
    if fingerprint_equal(fresh["appSpec"]["fingerprint"], ledger["appSpec"]["fingerprint"]):
        raise ProtocolError("AppSpec has not changed")
    history = root / ".vibe" / "history" / f"spec-{uuid.uuid4()}.json"
    atomic_write_json(history, ledger, refuse_existing=True)
    old_ids = {i["id"] for i in [*ledger["acceptanceScenarios"], *ledger["qualityGates"]]}
    new_ids = {i["id"] for i in [*fresh["acceptanceScenarios"], *fresh["qualityGates"]]}
    # Prose may change the meaning of any AC. Conservatively reopen all current
    # obligations, preserving every old state and receipt in the immutable archive.
    ledger.setdefault("specHistory", []).append({"path":history.relative_to(root).as_posix(), "decisionReference":decision,
        "added":sorted(new_ids-old_ids), "removed":sorted(old_ids-new_ids), "reopened":sorted(old_ids & new_ids), "at":utc_now()})
    if ledger.get("closureAudit", {}).get("requestPath"): ledger.setdefault("auditHistory", []).append(ledger["closureAudit"])
    for key in ("appSpec", "canonicalInventory", "workspaceFingerprint", "acceptanceScenarios", "qualityGates", "execution", "finalReceiptRef", "closureAudit"):
        ledger[key] = fresh[key]
    ledger["execution"]["nextAction"] = "Reread the approved AppSpec revision and decision; select the first dependency-ready AC for revalidation."
    ledger["execution"]["requiredReads"] = [decision]
    ledger["updatedAt"] = utc_now()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--app-spec", type=Path, required=True)
    parser.add_argument("--decision-reference", required=True)
    parser.add_argument("--expected-ledger-digest", required=True)
    args = parser.parse_args(); root = args.project_root.resolve()
    app_root = args.app_spec.resolve() if args.app_spec.is_absolute() else (root / args.app_spec).resolve()
    try:
        result = update_ledger_atomic(root / ".vibe" / "delivery-ledger.json", args.expected_ledger_digest,
            lambda ledger: reconcile(ledger, root, app_root, args.decision_reference))
        print(f"ledger-digest: {result['ledgerDigest']}"); return 0
    except (ProtocolError, OSError, ValueError) as exc: print(f"ERROR: {exc}"); return 1


if __name__ == "__main__": raise SystemExit(main())
