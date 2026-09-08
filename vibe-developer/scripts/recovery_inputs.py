"""Required durable inputs for delivery checkpoints and read-only recovery."""
from pathlib import Path
from vibe_protocol import ProtocolError, repository_path, sha256_bytes


def needs_request(ledger):
    return ledger.get("execution", {}).get("phase") != "planning" or any(
        item.get("status") != "not-started"
        for item in [*ledger.get("acceptanceScenarios", []), *ledger.get("qualityGates", [])])


def required_reads(root, ledger):
    execution = ledger.get("execution", {})
    app_root = Path(ledger["appSpec"]["root"])
    if not app_root.is_absolute(): app_root = root / app_root
    paths = [app_root / name for name in ("app-spec.json", "product.md", "domain.md", "data.md", "design.md", "quality.md")]
    paths += [root / value for value in execution.get("requiredReads", [])]
    if execution.get("durableRequest", {}).get("path"):
        paths.append(repository_path(root, execution["durableRequest"]["path"]))
    package_ids = {i for pid in execution.get('activePackageIds', []) for i in ledger.get('workPackages', {}).get(pid, {}).get('acceptanceScenarioIds', [])}
    for item in ledger.get("acceptanceScenarios", []):
        if item["id"] in package_ids:
            if item.get("flowId"): paths.append(app_root / "flows" / f"{item['flowId']}.md")
            paths += [app_root / "screens" / f"{screen}.md" for screen in item.get("screenIds", [])]
    active_id = execution.get("activeAcceptanceScenarioId")
    active = next((item for item in ledger.get("acceptanceScenarios", []) if item.get("id") == active_id), {})
    if active.get("flowId"): paths.append(app_root / "flows" / f"{active['flowId']}.md")
    paths += [app_root / "screens" / f"{screen}.md" for screen in active.get("screenIds", [])]
    return sorted({str(path.resolve()) for path in paths})


def capture_request(root, path):
    target = repository_path(root, path)
    content = target.read_bytes()
    if not content.strip(): raise ProtocolError("durable request must be a non-empty saved request")
    return {"path":target.relative_to(root).as_posix(), "sha256":sha256_bytes(content)}


def validate_request(root, ledger):
    request = ledger.get("execution", {}).get("durableRequest")
    if not request:
        return ["durable request missing; checkpoint with --request-file before implementation"] if needs_request(ledger) else []
    try:
        if capture_request(root, request["path"]) != request:
            return ["durable request changed; inspect it and explicitly checkpoint --request-file"]
    except (ProtocolError, OSError, ValueError, KeyError, TypeError) as exc:
        return [f"durable request invalid: {exc}"]
    return []


def capture_reads(root, ledger):
    return [{"path":path, "sha256":sha256_bytes(Path(path).read_bytes())} for path in required_reads(root, ledger)]


def validate_reads(root, ledger):
    errors = validate_request(root, ledger)
    try:
        saved = ledger.get("execution", {}).get("requiredReadHashes")
        if saved is None and not needs_request(ledger): return errors
        saved_by_path = {item["path"]: item["sha256"] for item in (saved or [])}
        if any(saved_by_path.get(item["path"]) != item["sha256"] for item in capture_reads(root, ledger)):
            errors.append("required recovery reads missing or changed; inspect and checkpoint their current hashes")
    except (ProtocolError, OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"required recovery read invalid: {exc}")
    return errors
