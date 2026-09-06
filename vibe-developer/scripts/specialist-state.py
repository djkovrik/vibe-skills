#!/usr/bin/env python3
"""Immutable recovery packets for interrupted specialist and standalone assignments."""
import argparse
import json
import re
import uuid
from pathlib import Path
from vibe_protocol import (ProtocolError, atomic_write_json, compute_workspace_fingerprint,
    discover_scoped_instructions, read_json, utc_now, workspace_drift_paths, paths_within_boundaries, sha256_bytes)


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
            if not args.owner or not args.obligation_id or not args.file_boundary or not args.next_action or not args.required_read:
                raise ProtocolError("checkpoint requires owner, obligations, boundaries, next action and durable request/required reads")
            packet = {"schemaVersion":"2.0", "assignmentId":args.assignment_id, "owner":args.owner,
                "obligationIds":args.obligation_id, "fileBoundaries":args.file_boundary, "pendingChecks":args.pending_check,
                "blockers":args.blocker, "requiredReads":args.required_read, "nextAction":args.next_action,
                "workspaceFingerprint":workspace, "scopedInstructions":discover_scoped_instructions(root),
                "status":args.status, "createdAt":utc_now()}
            packet["requiredReadHashes"] = [{"path":value, "sha256":sha256_bytes((root/value).read_bytes())} for value in args.required_read]
            path = directory / f"{args.assignment_id}--{uuid.uuid4()}.json"
            atomic_write_json(path, packet, refuse_existing=True)
            print(path.relative_to(root).as_posix()); return 0
        if not packets: raise ProtocolError("no recovery packet; inspect durable assignment before editing")
        packet = max(packets, key=lambda p:p["createdAt"])
        drift = workspace_drift_paths(packet["workspaceFingerprint"], workspace)
        safe = packet["workspaceFingerprint"].get("gitHead") == workspace.get("gitHead") and paths_within_boundaries(drift, packet["fileBoundaries"])
        safe = safe and packet["scopedInstructions"] == discover_scoped_instructions(root) and not packet["blockers"]
        safe = safe and bool(packet.get("requiredReadHashes")) and all(sha256_bytes((root/source["path"]).read_bytes())==source["sha256"] for source in packet.get("requiredReadHashes", []))
        print(json.dumps({"packet":packet, "safeToContinue":safe, "driftPaths":drift,
            "decisions":[read_json(p) for p in sorted((root/"docs"/"decisions").glob("DEC-*.json"))],
            "nextAction":packet["nextAction"] if safe and not drift else "Reconcile saved constraints, blockers and changed files before editing."}, indent=2))
        return 0 if safe else 1
    except (ProtocolError, OSError, ValueError) as exc: print(f"ERROR: {exc}"); return 1


if __name__ == "__main__": raise SystemExit(main())
