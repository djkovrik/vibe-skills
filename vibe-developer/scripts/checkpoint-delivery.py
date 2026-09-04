#!/usr/bin/env python3
"""Atomically checkpoint Protocol 2.0 delivery state using optimistic locking."""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(SCRIPT_DIR))

from vibe_protocol import ProtocolError, compute_workspace_fingerprint, discover_scoped_instructions, update_ledger_atomic, utc_now

PHASES = ("planning", "implementing", "reconciling", "auditing", "final-verification", "complete", "blocked")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--expected-ledger-digest", required=True)
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--active-ac")
    parser.add_argument("--owner")
    parser.add_argument("--file-boundary", action="append", default=[])
    parser.add_argument("--pending-check", action="append", default=[])
    parser.add_argument("--set-item-status", action="append", default=[], metavar="ID=STATUS")
    parser.add_argument("--add-receipt", action="append", default=[], metavar="ID=.vibe/receipts/name.json")
    parser.add_argument("--set-gate-applicability", action="append", default=[], metavar="QG-ID=applicable|not-applicable:reason")
    parser.add_argument("--decision-reference", action="append", default=[], metavar="ID=path#anchor")
    parser.add_argument("--blocker", action="append", default=[], metavar="ID=reason")
    parser.add_argument("--final-receipt-ref")
    parser.add_argument("--audit-path")
    parser.add_argument("--next-action", required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    ledger_path = (args.ledger or root / ".vibe" / "delivery-ledger.json").resolve()
    try:
        workspace = compute_workspace_fingerprint(root)
        now = utc_now()
        def mutate(ledger: dict) -> None:
            if ledger.get("schemaVersion") != "2.0":
                raise ProtocolError("unsupported protocol: delivery ledger must be 2.0")
            active = None
            if args.active_ac:
                active = next((item for item in ledger.get("acceptanceScenarios", []) if item.get("id") == args.active_ac), None)
                if active is None:
                    raise ProtocolError(f"unknown acceptance scenario: {args.active_ac}")
                unmet = [dep for dep in active.get("dependsOnAcceptanceScenarioIds", []) if next((i for i in ledger["acceptanceScenarios"] if i.get("id") == dep), {}).get("status") not in {"verified", "waived"}]
                if unmet and active.get("status") == "not-started":
                    raise ProtocolError(f"acceptance scenario dependencies are not closed: {', '.join(unmet)}")
                if active.get("status") == "not-started":
                    if not args.owner or not args.file_boundary:
                        raise ProtocolError("starting an AC requires --owner and at least one --file-boundary")
                    active.update({
                        "status": "in-progress", "owner": args.owner,
                        "fileBoundaries": args.file_boundary,
                        "baselineFingerprint": workspace, "checkpointFingerprint": workspace,
                        "changedFiles": [], "pendingChecks": args.pending_check,
                        "handoffRefs": active.get("handoffRefs", []), "blockers": [],
                        "startedAt": now, "updatedAt": now,
                    })
                elif active.get("status") == "in-progress":
                    if args.file_boundary and args.file_boundary != active.get("fileBoundaries"):
                        active["fileBoundaries"] = args.file_boundary
                    if args.owner:
                        active["owner"] = args.owner
                    if args.pending_check:
                        active["pendingChecks"] = args.pending_check
                    active["checkpointFingerprint"] = workspace
                    active["changedFiles"] = [item["path"] for item in workspace.get("workingFiles", [])]
                    active["updatedAt"] = now
            items = {item.get("id"): item for item in [*ledger.get("acceptanceScenarios", []), *ledger.get("qualityGates", [])]}
            for assignment in args.set_item_status:
                item_id, separator, status = assignment.partition("=")
                if not separator or item_id not in items:
                    raise ProtocolError(f"invalid --set-item-status: {assignment}")
                if status not in {"not-started", "in-progress", "implemented-unverified", "verified", "blocked-external", "waived"}:
                    raise ProtocolError(f"invalid item status: {status}")
                items[item_id]["status"] = status
                items[item_id]["updatedAt"] = now
            for assignment in args.add_receipt:
                item_id, separator, receipt_ref = assignment.partition("=")
                if not separator or item_id not in items or not receipt_ref.startswith(".vibe/receipts/"):
                    raise ProtocolError(f"invalid --add-receipt: {assignment}")
                items[item_id]["receiptRefs"] = sorted(set(items[item_id].get("receiptRefs", []) + [receipt_ref]))
            gates = {item.get("id"): item for item in ledger.get("qualityGates", [])}
            for assignment in args.set_gate_applicability:
                item_id, separator, decision = assignment.partition("=")
                value, reason_separator, reason = decision.partition(":")
                if not separator or item_id not in gates or value not in {"applicable", "not-applicable"}:
                    raise ProtocolError(f"invalid --set-gate-applicability: {assignment}")
                if value == "not-applicable" and (not reason_separator or not reason.strip()):
                    raise ProtocolError("not-applicable requires a reason after ':'")
                gates[item_id]["applicability"] = value
                if value == "not-applicable": gates[item_id]["applicabilityReason"] = reason
            for assignment in args.decision_reference:
                item_id, separator, reference = assignment.partition("=")
                if not separator or item_id not in items or not reference.strip(): raise ProtocolError(f"invalid --decision-reference: {assignment}")
                items[item_id]["decisionReference"] = reference
            for assignment in args.blocker:
                item_id, separator, reason = assignment.partition("=")
                if not separator or item_id not in items or not reason.strip(): raise ProtocolError(f"invalid --blocker: {assignment}")
                items[item_id]["blocker"] = {"reason": reason, "recordedAt": now}
            if args.final_receipt_ref:
                if not args.final_receipt_ref.startswith(".vibe/receipts/"):
                    raise ProtocolError("--final-receipt-ref must be under .vibe/receipts")
                ledger["finalReceiptRef"] = args.final_receipt_ref
            if args.audit_path:
                if args.audit_path != ".vibe/closure-audit.json":
                    raise ProtocolError("--audit-path must be .vibe/closure-audit.json")
                ledger.setdefault("closureAudit", {})["auditPath"] = args.audit_path
            execution = ledger.setdefault("execution", {})
            execution.update({
                "phase": args.phase, "activeAcceptanceScenarioId": args.active_ac,
                "scopedInstructions": discover_scoped_instructions(root),
                "checkpoint": {"checkpointId": f"CP-{uuid.uuid4()}", "createdAt": now, "workspaceFingerprint": workspace},
                "nextAction": args.next_action,
            })
            ledger["workspaceFingerprint"] = workspace
            ledger["updatedAt"] = now
        ledger = update_ledger_atomic(ledger_path, args.expected_ledger_digest, mutate)
    except (ProtocolError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"checkpoint: {ledger['execution']['checkpoint']['checkpointId']}")
    print(f"ledger-digest: {ledger['ledgerDigest']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
