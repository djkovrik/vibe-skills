"""Synthetic approvals and host events for isolated protocol unit tests, never production evidence."""
import json
from pathlib import Path
from vibe_protocol import sha256_bytes
from audit_evidence import source_sections


def decision_fixture(root, ids, kind="waiver", name="DEC-FIXTURE"):
    directory = root / "docs" / "decisions"; directory.mkdir(parents=True, exist_ok=True)
    source = directory / f"{name}-user.txt"; source.write_text("Test user explicitly approves this scoped decision.", encoding="utf-8")
    decision = {"schemaVersion":"2.0", "decisionId":name, "kind":kind, "status":"accepted", "obligationIds":ids,
        "rationale":"Synthetic fixture decision", "recordedAt":"2026-09-04T09:00:00Z", "supersedes":[],
        "userApproval":{"actor":"user", "path":source.relative_to(root).as_posix(), "messageId":"fixture-message-1",
        "quote":source.read_text(), "sha256":sha256_bytes(source.read_bytes())}}
    path = directory/f"{name}.json"; path.write_text(json.dumps(decision), encoding="utf-8")
    return path.relative_to(root).as_posix()


def launch_fixture(root, request_path, request, completed="2026-09-04T10:12:30Z"):
    events = request_path.with_name("events.jsonl"); events.write_text(json.dumps({"type":"thread.started", "thread_id":"test-thread"})+"\n", encoding="utf-8")
    prompt = request_path.with_name("prompt.txt"); prompt.write_text(f"Synthetic vibe-acceptance-auditor test invocation for {request_path}.", encoding="utf-8")
    launch = {"schemaVersion":"2.0", "producer":"vibe-fresh-process-runner", "contextId":request["requiredAuditorContextId"],
        "requestSha256":sha256_bytes(request_path.read_bytes()), "threadId":"test-thread", "argv":["codex", "exec", "--ephemeral", "--json", "-C", str(root)],
        "startedAt":request["createdAt"], "completedAt":completed, "exitCode":0, "executionStatus":"completed",
        "startWorkspaceFingerprint":request["workspaceFingerprint"], "workspaceFingerprint":request["workspaceFingerprint"],
        "eventsSha256":sha256_bytes(events.read_bytes()), "promptSha256":sha256_bytes(prompt.read_bytes())}
    request_path.with_name("launch.json").write_text(json.dumps(launch), encoding="utf-8")


def coverage_fixture(app_root, ids):
    return [{**section, "classification":"normative", "obligationIds":ids} for section in source_sections(app_root)]


def audit_receipt_fixture(root, check):
    """Synthetic runner receipt for structural tests only; real-run tests use run_check."""
    directory = root / ".vibe/receipts"; directory.mkdir(parents=True, exist_ok=True)
    log = directory / f"{check['checkId']}.log"; log.write_text("Synthetic command output", encoding="utf-8")
    receipt = {key:check[key] for key in ("argv", "startedAt", "completedAt", "exitCode", "executionStatus", "startWorkspaceFingerprint", "workspaceFingerprint")}
    grouped = {}
    for pair in check["coverage"]: grouped.setdefault(pair["obligationId"], []).append(pair["surface"])
    receipt.update(schemaVersion="2.0", receiptId=check["checkId"], kind="targeted", tasks=[],
        coveredObligations=[{"obligationId":key, "surfaces":value} for key,value in grouped.items()],
        log={"path":log.relative_to(root).as_posix(), "sha256":sha256_bytes(log.read_bytes())})
    path = directory / f"{check['checkId']}.json"; path.write_text(json.dumps(receipt), encoding="utf-8")
    check.update(receiptRef=path.relative_to(root).as_posix(), receiptSha256=sha256_bytes(path.read_bytes()))
