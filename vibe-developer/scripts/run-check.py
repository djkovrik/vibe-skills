#!/usr/bin/env python3
"""Record a real non-Gradle check with pre/post fingerprints and immutable output."""
import argparse
import subprocess
import uuid
import sys
from pathlib import Path
from vibe_protocol import ProtocolError, atomic_write_json, read_json, compute_workspace_fingerprint, fingerprint_equal, utc_now, sha256_bytes, execute_process


def run_check(root, argv, coverage, kind="targeted", timeout=1800):
    if any("gradle" in Path(arg).name.lower() for arg in argv[:1]): raise ProtocolError("use the orchestrator Gradle runner")
    directory = root / ".vibe" / "receipts"; directory.mkdir(parents=True, exist_ok=True)
    receipt_id = f"RECEIPT-{uuid.uuid4()}"
    before = compute_workspace_fingerprint(root); started = utc_now(); status = "completed"
    code, stdout, stderr, status = execute_process(argv, cwd=root, timeout=timeout)
    output = stdout + stderr
    after = compute_workspace_fingerprint(root)
    if status == "completed" and not fingerprint_equal(before, after): status = "workspace-changed"
    log = directory / f"{receipt_id}.log"; log.write_bytes(output)
    receipt = {"schemaVersion":"2.0", "receiptId":receipt_id, "kind":kind, "argv":argv, "tasks":argv[1:],
        "coveredObligations":coverage, "startedAt":started, "completedAt":utc_now(), "exitCode":code,
        "executionStatus":status, "startWorkspaceFingerprint":before, "workspaceFingerprint":after,
        "log":{"path":log.relative_to(root).as_posix(), "sha256":sha256_bytes(output)}}
    path = directory / f"{receipt_id}.json"; atomic_write_json(path, receipt, refuse_existing=True)
    return path, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("project_root", type=Path)
    parser.add_argument("--coverage", type=Path, required=True, help="JSON object with coveredObligations")
    parser.add_argument("--kind", choices=("targeted", "final"), default="targeted")
    parser.add_argument("--timeout", type=float, default=1800)
    if "--" not in sys.argv: parser.error("separate the check command with --")
    separator = sys.argv.index("--")
    args = parser.parse_args(sys.argv[1:separator])
    try:
        command = sys.argv[separator+1:]
        if not command: raise ProtocolError("command required after --")
        path, receipt = run_check(args.project_root.resolve(), command, read_json(args.coverage)["coveredObligations"], args.kind, args.timeout)
        print(path); return 0 if receipt["exitCode"] == 0 and receipt["executionStatus"] == "completed" else 1
    except (ProtocolError, OSError, ValueError, KeyError) as exc: print(f"ERROR: {exc}"); return 1


if __name__ == "__main__": raise SystemExit(main())
