#!/usr/bin/env python3
"""Launch a fresh Codex process and record host-issued session evidence for one attempt."""
import argparse
import json
import shutil
import subprocess
import sys
import importlib.util
from pathlib import Path
from vibe_protocol import (ProtocolError, audit_paths, atomic_write_json, read_json, sha256_bytes,
    compute_workspace_fingerprint, fingerprint_equal, utc_now, file_lock, execute_process)


def run(root, request_path, executable, timeout):
    audit_path, launch_path = audit_paths(root, request_path)
    with file_lock(request_path.with_name("runner.lock")):
        if audit_path.exists() or launch_path.exists(): raise ProtocolError("attempt already executed; create a new request")
        request = read_json(request_path)
        ledger = read_json(root / ".vibe" / "delivery-ledger.json")
        binding = ledger.get("closureAudit", {})
        if binding.get("requestPath") != request_path.relative_to(root).as_posix() or binding.get("requestSha256") != sha256_bytes(request_path.read_bytes()): raise ProtocolError("request is not the current ledger attempt")
        before = compute_workspace_fingerprint(root)
        if not fingerprint_equal(before, request.get("workspaceFingerprint")): raise ProtocolError("request workspace is stale")
        skill = Path(__file__).resolve().parents[2] / "vibe-acceptance-auditor" / "SKILL.md"
        schema = skill.parent / "assets" / "closure-audit.schema.json"
        result_path = request_path.with_name("result.json")
        prompt_path = request_path.with_name("prompt.txt")
        prompt = (f"Use $vibe-acceptance-auditor at {skill}. Audit repository {root} using approved AppSpec "
            f"{ledger['appSpec']['root']} and immutable request {request_path}. This is a fresh process with no implementation conversation. "
            "Read the request and normative AppSpec first. Independently inventory every source section using inventory-sources.py; "
            "include sourceCoverage mapping all sections to obligations or explained contextual material. Inspect production behavior and exact assertions. "
            "Run the required safe checks with the shared runners; bind each check with receiptRef and receiptSha256 to its targeted receipt. "
            "Copy exact argv, outcome, timestamps, start/end fingerprints and full coverage, including managed-operation IDs being proved. "
            "Do not edit production, tests, AppSpec, ledger, configuration or dependencies. Return the closure audit JSON as your final response. "
            "The host writes the immutable audit and launch receipt after your process exits; do not fabricate launch metadata or invoke final validation before then.")
        prompt_path.write_text(prompt, encoding="utf-8")
        argv = [executable, "exec", "--ephemeral", "--json", "--sandbox", "workspace-write", "-C", str(root),
            "--output-schema", str(schema), "--output-last-message", str(result_path), "-"]
        started = utc_now(); status = "completed"
        code, stdout_bytes, stderr_bytes, status = execute_process(argv, input_bytes=prompt.encode("utf-8"), timeout=timeout, cwd=root)
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")
        after = compute_workspace_fingerprint(root)
        if not fingerprint_equal(before, after): status = "workspace-changed"
        events = request_path.with_name("events.jsonl"); events.write_text(stdout, encoding="utf-8")
        request_path.with_name("stderr.log").write_text(stderr, encoding="utf-8")
        try: thread_ids = [e.get("thread_id") for line in stdout.splitlines() if line.strip() for e in [json.loads(line)] if e.get("type") == "thread.started"]
        except ValueError: thread_ids = []
        launch = {"schemaVersion":"2.0", "producer":"vibe-fresh-process-runner", "contextId":request["requiredAuditorContextId"],
            "requestSha256":sha256_bytes(request_path.read_bytes()), "threadId":thread_ids[0] if len(thread_ids)==1 else None,
            "argv":argv, "startedAt":started, "completedAt":utc_now(), "exitCode":code, "executionStatus":status,
            "startWorkspaceFingerprint":before, "workspaceFingerprint":after,
            "eventsSha256":sha256_bytes(events.read_bytes()), "promptSha256":sha256_bytes(prompt_path.read_bytes())}
        atomic_write_json(launch_path, launch, refuse_existing=True)
        if code != 0 or status != "completed" or not launch["threadId"]: raise ProtocolError("audit process did not complete cleanly; preserve attempt and create a new request")
        atomic_write_json(audit_path, read_json(result_path), refuse_existing=True)
        spec = importlib.util.spec_from_file_location("launched_audit_validator", skill.parent / "scripts" / "validate-closure-audit.py")
        validator = importlib.util.module_from_spec(spec); sys.modules[spec.name] = validator; spec.loader.exec_module(validator)
        app_root = Path(ledger["appSpec"]["root"])
        if not app_root.is_absolute(): app_root = root / app_root
        errors = validator.validate(read_json(audit_path), app_root, root, request_path)
        if errors: raise ProtocolError("returned audit is invalid: " + "; ".join(errors))
        print(audit_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("project_root", type=Path)
    parser.add_argument("--request", type=Path, required=True); parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args(); executable = shutil.which("codex")
    try:
        if not executable: raise ProtocolError("Codex CLI unavailable; fresh-context audit is blocked")
        root = args.project_root.resolve(); request = args.request if args.request.is_absolute() else root / args.request
        run(root, request.resolve(), executable, args.timeout); return 0
    except (ProtocolError, OSError, ValueError) as exc: print(f"ERROR: {exc}", file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(main())
