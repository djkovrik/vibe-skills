"""Evidence shared by the fresh-process launcher and the independent validator."""
import json
import re
from pathlib import Path
from vibe_protocol import ProtocolError, read_json, sha256_bytes, audit_paths, parse_time, fingerprint_equal


def source_sections(app_root):
    paths = [app_root / name for name in ("product.md", "domain.md", "data.md", "design.md", "quality.md")]
    paths += sorted((app_root / "flows").glob("FLOW-*.md")) + sorted((app_root / "screens").glob("SCREEN-*.md"))
    sections = []
    for path in paths:
        used = {}; in_code = False
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.lstrip().startswith(("```", "~~~")): in_code = not in_code
            if in_code: continue
            match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
            if not match: continue
            slug = re.sub(r"[^\w\s-]", "", match[1].lower()).strip().replace(" ", "-")
            count = used.get(slug, 0); used[slug] = count + 1
            sections.append({"path":path.relative_to(app_root).as_posix(), "anchor":slug + (f"-{count}" if count else "")})
        if not used: sections.append({"path":path.relative_to(app_root).as_posix(), "anchor":"document"})
    return sections


def validate_source_coverage(data, app_root, known_ids):
    expected = {(i["path"],i["anchor"]) for i in source_sections(app_root)}
    actual = set(); errors = []
    for entry in data.get("sourceCoverage", []):
        pair = (entry.get("path"),entry.get("anchor"))
        if pair in actual: errors.append(f"duplicate source coverage: {pair}")
        actual.add(pair)
        ids = entry.get("obligationIds", [])
        if not isinstance(ids, list) or any(i not in known_ids for i in ids): errors.append(f"unknown source obligation: {pair}")
        if entry.get("classification") == "normative":
            if not ids: errors.append(f"normative source has no obligation: {pair}")
        elif entry.get("classification") == "context":
            if not str(entry.get("rationale", "")).strip(): errors.append(f"context source requires rationale: {pair}")
        else: errors.append(f"invalid source classification: {pair}")
    if actual != expected: errors.append(f"source coverage mismatch; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    return errors


def validate_launch(root, request_path, request, audit):
    """Require runner output tied to an actual fresh CLI thread event, not an auditor flag."""
    errors = []
    try:
        _, launch_path = audit_paths(root, request_path)
        launch = read_json(launch_path)
        if launch.get("schemaVersion") != "2.0" or launch.get("producer") != "vibe-fresh-process-runner": errors.append("invalid launch receipt producer")
        if launch.get("requestSha256") != sha256_bytes(request_path.read_bytes()): errors.append("launch request hash mismatch")
        if launch.get("contextId") != request.get("requiredAuditorContextId"): errors.append("launch context ID mismatch")
        argv = launch.get("argv", [])
        if len(argv) < 2 or argv[1] != "exec" or "--ephemeral" not in argv or "--json" not in argv or any(a in argv for a in ("resume", "fork")): errors.append("launch was not a fresh ephemeral exec")
        if "-C" not in argv or argv.index("-C")+1 >= len(argv) or Path(argv[argv.index("-C")+1]).resolve()!=root.resolve(): errors.append("launch repository mismatch")
        if launch.get("exitCode") != 0 or launch.get("executionStatus") != "completed": errors.append("auditor process failed or was interrupted")
        for field in ("startWorkspaceFingerprint", "workspaceFingerprint"):
            if not fingerprint_equal(launch.get(field), request.get("workspaceFingerprint")): errors.append(f"launch {field} mismatch")
        events = launch_path.with_name("events.jsonl")
        if sha256_bytes(events.read_bytes()) != launch.get("eventsSha256"): errors.append("launch events hash mismatch")
        event_data = [json.loads(line) for line in events.read_text(encoding="utf-8").splitlines() if line.strip()]
        thread_ids = [e.get("thread_id") for e in event_data if e.get("type") == "thread.started"]
        if len(thread_ids) != 1 or not thread_ids[0] or thread_ids[0] != launch.get("threadId"): errors.append("missing or mismatched host thread.started event")
        prompt = launch_path.with_name("prompt.txt")
        if sha256_bytes(prompt.read_bytes()) != launch.get("promptSha256"): errors.append("launch prompt hash mismatch")
        prompt_text = prompt.read_text(encoding="utf-8")
        if str(request_path) not in prompt_text or "vibe-acceptance-auditor" not in prompt_text: errors.append("launch prompt does not identify this independent audit request")
        if not parse_time(launch["startedAt"]) <= parse_time(audit["startedAt"]) <= parse_time(audit["completedAt"]) <= parse_time(launch["completedAt"]): errors.append("audit timestamps are outside launched process")
    except (ProtocolError, OSError, ValueError, KeyError, TypeError) as exc: errors.append(f"launch evidence invalid: {exc}")
    return errors
