#!/usr/bin/env python3
"""Immutable recovery packets for interrupted specialist and standalone assignments."""
import argparse
import json
import re
import uuid
from pathlib import Path
from vibe_protocol import (ProtocolError, atomic_write_json, compute_workspace_fingerprint,
    discover_scoped_instructions, read_json, utc_now, workspace_drift_paths, paths_within_boundaries, sha256_bytes, file_lock)


def checkpoint(root, directory, args):
    with file_lock(directory / f"{args.assignment_id}.lock"):
        packets = [read_json(p) for p in directory.glob(f"{args.assignment_id}--*.json")]
        previous = max(packets, key=lambda p:p["createdAt"]) if packets else {}
        if previous.get("status") == "returned":
            raise ProtocolError("assignment already returned; use a new assignment ID for new work")
        required_reads = sorted(set(previous.get("requiredReads", [])) | set(args.required_read))
        if not args.owner or not args.obligation_id or not args.file_boundary or not args.next_action or not required_reads:
            raise ProtocolError("checkpoint requires owner, obligations, boundaries, next action and durable request/required reads")
        if (args.resolve_pending_check or args.resolve_blocker) and not (args.resolution_reason or "").strip():
            raise ProtocolError("resolving pending checks or blockers requires --resolution-reason")
        remaining = {}
        for field, added, resolved in (("pendingChecks", args.pending_check, args.resolve_pending_check),
                                       ("blockers", args.blocker, args.resolve_blocker)):
            old = previous.get(field, [])
            if any(value not in old for value in resolved): raise ProtocolError(f"cannot resolve unknown {field}")
            if set(added) & set(resolved): raise ProtocolError(f"cannot add and resolve the same {field}")
            remaining[field] = sorted((set(old) | set(added)) - set(resolved))
        packet = {"schemaVersion":"2.0", "assignmentId":args.assignment_id, "owner":args.owner,
            "obligationIds":args.obligation_id, "fileBoundaries":args.file_boundary, **remaining,
            "requiredReads": required_reads,
            "nextAction":args.next_action, "workspaceFingerprint":compute_workspace_fingerprint(root),
            "scopedInstructions":discover_scoped_instructions(root), "status":args.status, "createdAt":utc_now(),
            "previousPacketDigest":sha256_bytes(json.dumps(previous, sort_keys=True).encode()) if previous else None,
            "resolutions":{"pendingChecks":args.resolve_pending_check, "blockers":args.resolve_blocker, "reason":args.resolution_reason}}
        packet["requiredReadHashes"] = [{"path":value, "sha256":sha256_bytes((root/value).read_bytes())} for value in packet["requiredReads"]]
        path = directory / f"{args.assignment_id}--{uuid.uuid4()}.json"
        atomic_write_json(path, packet, refuse_existing=True)
        return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("checkpoint", "resume"))
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--assignment-id", required=True)
    parser.add_argument("--owner")
    parser.add_argument("--obligation-id", action="append", default=[])
    parser.add_argument("--file-boundary", action="append", default=[])
    parser.add_argument("--pending-check", action="append", default=[])
    parser.add_argument("--blocker", action="append", default=[])
    parser.add_argument("--resolve-pending-check", action="append", default=[], help="Exact saved check to resolve")
    parser.add_argument("--resolve-blocker", action="append", default=[], help="Exact saved blocker to resolve")
    parser.add_argument("--resolution-reason", help="Completed verification or decision that resolves the named items")
    parser.add_argument("--required-read", action="append", default=[])
    parser.add_argument("--next-action")
    parser.add_argument("--status", choices=("active", "returned"), default="active")
    args = parser.parse_args(); root = args.project_root.resolve()
    try:
        if not re.fullmatch(r"[A-Za-z0-9-]+", args.assignment_id): raise ProtocolError("invalid assignment ID")
        directory = root / ".vibe" / "recovery"
        packets = [read_json(p) for p in directory.glob(f"{args.assignment_id}--*.json")]
        workspace = compute_workspace_fingerprint(root)
        if args.mode == "checkpoint":
            path = checkpoint(root, directory, args)
            print(path.relative_to(root).as_posix()); return 0
        if not packets: raise ProtocolError("no recovery packet; inspect durable assignment before editing")
        packet = max(packets, key=lambda p:p["createdAt"])
        drift = workspace_drift_paths(packet["workspaceFingerprint"], workspace)
        if packet.get("status") == "returned":
            print(json.dumps({"packet":packet, "safeToContinue":False, "assignmentReturned":True,
                "driftPaths":drift, "nextAction":"Assignment already returned; use a new assignment ID for new work."}, indent=2))
            return 0
        safe = packet["workspaceFingerprint"].get("gitHead") == workspace.get("gitHead") and paths_within_boundaries(drift, packet["fileBoundaries"])
        safe = safe and packet["scopedInstructions"] == discover_scoped_instructions(root) and not packet["blockers"]
        safe = safe and bool(packet.get("requiredReadHashes")) and all(sha256_bytes((root/source["path"]).read_bytes())==source["sha256"] for source in packet.get("requiredReadHashes", []))
        print(json.dumps({"packet":packet, "safeToContinue":safe, "driftPaths":drift,
            "decisions":[read_json(p) for p in sorted((root/"docs"/"decisions").glob("DEC-*.json"))],
            "nextAction":packet["nextAction"] if safe and not drift else "Reconcile saved constraints, blockers and changed files before editing."}, indent=2))
        return 0 if safe else 1
    except (ProtocolError, OSError, ValueError) as exc: print(f"ERROR: {exc}"); return 1


if __name__ == "__main__": raise SystemExit(main())
