#!/usr/bin/env python3
"""Shared, dependency-free primitives for Vibe Protocol 2.0 tools."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


PROTOCOL_VERSION = "2.0"
APP_SPEC_VERSION = "2.0"
LEDGER_VERSION = "2.0"
DELIVERY_ARTIFACT_PATTERNS = (
    ".vibe/delivery-ledger.json",
    ".vibe/audit-request.json",
    ".vibe/closure-audit.json",
    ".vibe/receipts",
    ".vibe/handoffs",
    "docs/requirement-traceability.generated.md",
    "docs/closure-audit.generated.md",
)


class ProtocolError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def ledger_digest(value: dict[str, Any]) -> str:
    copy = dict(value)
    copy.pop("ledgerDigest", None)
    return canonical_digest(copy)


def with_ledger_digest(value: dict[str, Any]) -> dict[str, Any]:
    value["ledgerDigest"] = ledger_digest(value)
    return value


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProtocolError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProtocolError(f"expected a JSON object: {path}")
    return value


def atomic_write_json(path: Path, value: dict[str, Any], *, refuse_existing: bool = False) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if refuse_existing and path.exists():
        raise ProtocolError(f"refusing to overwrite immutable artifact: {path}")
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        if refuse_existing and path.exists():
            raise ProtocolError(f"refusing to overwrite immutable artifact: {path}")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def update_ledger_atomic(path: Path, expected_digest: str, mutate: Any) -> dict[str, Any]:
    ledger = read_json(path)
    actual = ledger_digest(ledger)
    stored = ledger.get("ledgerDigest")
    if stored != actual:
        raise ProtocolError("delivery ledger digest is invalid; reconcile manual or concurrent edits")
    if expected_digest != actual:
        raise ProtocolError(f"ledger digest conflict: expected {expected_digest}, current {actual}")
    mutate(ledger)
    with_ledger_digest(ledger)
    atomic_write_json(path, ledger)
    return ledger


def _run_git(root: Path, arguments: list[str], *, allow_failure: bool = False) -> bytes:
    process = subprocess.run(
        ["git", "-C", os.fspath(root), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0 and not allow_failure:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise ProtocolError(detail or f"git {' '.join(arguments)} failed")
    return process.stdout if process.returncode == 0 else b""


def _is_delivery_artifact(path: str) -> bool:
    normalized = PurePosixPath(path.replace("\\", "/")).as_posix()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return any(normalized == pattern or normalized.startswith(pattern.rstrip("/") + "/") for pattern in DELIVERY_ARTIFACT_PATTERNS)


def _file_state(root: Path, relative: str) -> dict[str, Any]:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ProtocolError(f"Git returned path outside project: {relative}") from exc
    return {
        "path": PurePosixPath(relative).as_posix(),
        "sha256": sha256_bytes(candidate.read_bytes()) if candidate.is_file() else None,
    }


def compute_workspace_fingerprint(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ProtocolError(f"project root does not exist: {root}")
    if _run_git(root, ["rev-parse", "--is-inside-work-tree"]).strip() != b"true":
        raise ProtocolError(f"not a Git worktree: {root}")
    raw_head = _run_git(root, ["rev-parse", "--verify", "HEAD"], allow_failure=True)
    head = raw_head.decode("ascii", errors="strict").strip() or None
    pathspecs = ["."] + [f":(exclude){p}/**" if p in {".vibe/receipts", ".vibe/handoffs"} else f":(exclude){p}" for p in DELIVERY_ARTIFACT_PATTERNS]
    diff_args = ["diff", "--relative", "--binary", "--no-ext-diff"] + (["HEAD"] if head else ["--cached"])
    binary_diff = _run_git(root, [*diff_args, "--", *pathspecs])
    tracked_names = _run_git(root, ["diff", "--name-only", "-z"] + (["HEAD"] if head else ["--cached"]) + ["--", *pathspecs])
    untracked_names = _run_git(root, ["ls-files", "--others", "--exclude-standard", "-z", "--", "."])
    names = {
        part.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        for raw in (tracked_names, untracked_names)
        for part in raw.split(b"\0") if part
    }
    working_files = [_file_state(root, name) for name in sorted(names, key=str.casefold) if not _is_delivery_artifact(name)]
    payload: dict[str, Any] = {
        "algorithm": "sha256",
        "gitHead": head,
        "binaryDiffSha256": sha256_bytes(binary_diff),
        "workingFiles": working_files,
    }
    payload["digest"] = canonical_digest(payload)
    return payload


def compute_app_spec_fingerprint(app_spec_root: str | Path) -> dict[str, Any]:
    root = Path(app_spec_root).resolve()
    if not root.is_dir():
        raise ProtocolError(f"AppSpec root does not exist: {root}")
    files = [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_bytes(path.read_bytes())}
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold())
        if path.is_file()
    ]
    if not files:
        raise ProtocolError(f"AppSpec contains no regular files: {root}")
    payload: dict[str, Any] = {"algorithm": "sha256", "files": files}
    payload["digest"] = canonical_digest(payload)
    return payload


def fingerprint_equal(left: Any, right: Any) -> bool:
    return isinstance(left, dict) and isinstance(right, dict) and left.get("digest") == right.get("digest") and left == right


def discover_scoped_instructions(project_root: str | Path) -> list[dict[str, str]]:
    root = Path(project_root).resolve()
    candidates: set[Path] = set()
    cursor = root
    while True:
        candidate = cursor / "AGENTS.md"
        if candidate.is_file():
            candidates.add(candidate.resolve())
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    for candidate in root.rglob("AGENTS.md"):
        if ".git" not in candidate.parts and candidate.is_file():
            candidates.add(candidate.resolve())
    result = []
    for path in sorted(candidates, key=lambda p: (len(p.parts), str(p).casefold())):
        try:
            portable = path.relative_to(root).as_posix()
            scope = path.parent.relative_to(root).as_posix() or "."
        except ValueError:
            portable = os.fspath(path)
            scope = os.fspath(path.parent)
        result.append({"path": portable, "scope": scope, "sha256": sha256_bytes(path.read_bytes())})
    return result


def canonical_inventory(app_spec: dict[str, Any]) -> dict[str, list[str]]:
    approved = [r for r in app_spec.get("requirements", []) if isinstance(r, dict) and r.get("status") == "approved"]
    excluded = [r for r in app_spec.get("requirements", []) if isinstance(r, dict) and r.get("status") == "excluded"]
    operations: list[str] = []
    for entity in app_spec.get("managedEntities", []):
        if not isinstance(entity, dict) or not isinstance(entity.get("operations"), dict):
            continue
        for operation, decision in entity["operations"].items():
            if isinstance(decision, dict) and decision.get("status") == "required":
                operations.append(f"{entity.get('entity')}:{operation}")
    return {
        "requirementIds": sorted(str(item.get("id")) for item in approved),
        "excludedRequirementIds": sorted(str(item.get("id")) for item in excluded),
        "acceptanceScenarioIds": sorted(str(item.get("id")) for item in app_spec.get("acceptanceScenarios", []) if isinstance(item, dict)),
        "managedOperationIds": sorted(operations),
        "qualityGateIds": sorted(str(item.get("id")) for item in app_spec.get("qualityGates", []) if isinstance(item, dict)),
    }


def validate_app_spec_data(root: Path, data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    version = data.get("schemaVersion")
    if version != APP_SPEC_VERSION:
        errors.append(f"unsupported protocol: AppSpec {version!r}; expected {APP_SPEC_VERSION}")
        return errors, warnings
    required_files = ("app-spec.json", "product.md", "design.md", "domain.md", "data.md", "quality.md")
    for name in required_files:
        if not (root / name).is_file():
            errors.append(f"Missing required file: {name}")
    for name in ("flows", "screens"):
        if not (root / name).is_dir():
            errors.append(f"Missing required directory: {name}")
    for field in ("app", "requirements", "acceptanceScenarios", "managedEntities", "qualityGates", "flows", "screens", "capabilities", "constraints", "localization", "architecture", "uiQuality", "openQuestions"):
        if field not in data: errors.append(f"{field} is required")
    app_value = data.get("app")
    if not isinstance(app_value, dict):
        errors.append("app must be an object"); app_value = {}
    for field in ("name", "summary"):
        if not isinstance(app_value.get(field), str) or not app_value[field].strip(): errors.append(f"app.{field} is required")
    targets_value, locales_value = app_value.get("targets"), app_value.get("locales")
    if not isinstance(targets_value, list) or not targets_value or any(not isinstance(v, str) or not v for v in targets_value) or len(targets_value) != len(set(targets_value)): errors.append("app.targets must be a non-empty unique string array")
    if not isinstance(locales_value, list) or not locales_value or any(not isinstance(v, str) or not v for v in locales_value) or len(locales_value) != len(set(locales_value)): errors.append("app.locales must be a non-empty unique string array")
    elif locales_value[0] != "en" or "ru" not in locales_value: errors.append("app.locales must use en as base and include initial ru locale")

    requirements = data.get("requirements")
    scenarios = data.get("acceptanceScenarios")
    gates = data.get("qualityGates")
    if not isinstance(requirements, list) or not requirements:
        errors.append("requirements must be a non-empty array")
        requirements = []
    if not isinstance(scenarios, list):
        errors.append("acceptanceScenarios must be an array")
        scenarios = []
    if not isinstance(gates, list) or not gates:
        errors.append("qualityGates must be a non-empty array")
        gates = []

    def unique_ids(items: list[Any], label: str, pattern: str) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{label}[{index}] must be an object")
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or re.fullmatch(pattern, item_id) is None:
                errors.append(f"{label}[{index}].id has invalid format")
            elif item_id in result:
                errors.append(f"Duplicate {label} ID: {item_id}")
            else:
                result[item_id] = item
        return result

    reqs = unique_ids(requirements, "requirements", r"REQ-[0-9]{3,}")
    acs = unique_ids(scenarios, "acceptanceScenarios", r"AC-[0-9]{3,}")
    gate_map = unique_ids(gates, "qualityGates", r"QG-[0-9]{3,}")
    if not isinstance(data.get("flows"), list): errors.append("flows must be an array")
    if not isinstance(data.get("screens"), list): errors.append("screens must be an array")
    flows = data.get("flows") if isinstance(data.get("flows"), list) else []
    screens = data.get("screens") if isinstance(data.get("screens"), list) else []
    if any(not isinstance(v, str) or re.fullmatch(r"FLOW-[0-9]{3,}", v) is None for v in flows): errors.append("flows contains an invalid ID")
    if any(not isinstance(v, str) or re.fullmatch(r"SCREEN-[0-9]{3,}", v) is None for v in screens): errors.append("screens contains an invalid ID")
    if all(isinstance(v, str) for v in flows) and len(flows) != len(set(flows)):
        errors.append("flows contains duplicate IDs")
    if all(isinstance(v, str) for v in screens) and len(screens) != len(set(screens)):
        errors.append("screens contains duplicate IDs")

    claimed: list[str] = []
    for req_id, requirement in reqs.items():
        if not isinstance(requirement.get("title"), str) or not requirement["title"].strip(): errors.append(f"requirements.{req_id}.title is required")
        status = requirement.get("status")
        ids = requirement.get("acceptanceScenarioIds")
        if status == "approved":
            if requirement.get("priority") not in {"must", "should", "could"}:
                errors.append(f"requirements.{req_id}.priority must be must, should, or could")
            if not isinstance(ids, list) or not ids or any(not isinstance(v, str) for v in ids) or len(ids) != len(set(ids)):
                errors.append(f"requirements.{req_id}.acceptanceScenarioIds must contain at least one AC")
            else:
                claimed.extend(str(v) for v in ids)
            if "reason" in requirement:
                warnings.append(f"requirements.{req_id}.reason is ignored for approved requirements")
        elif status == "excluded":
            if not isinstance(requirement.get("reason"), str) or not requirement["reason"].strip():
                errors.append(f"requirements.{req_id}.reason is required for excluded requirements")
            if "acceptanceScenarioIds" in requirement:
                errors.append(f"requirements.{req_id}: excluded requirement must not have acceptanceScenarioIds")
            if requirement.get("priority") == "wont":
                errors.append(f"requirements.{req_id}: priority 'wont' is removed in Protocol 2.0")
            elif "priority" in requirement and requirement.get("priority") not in {"must", "should", "could"}: errors.append(f"requirements.{req_id}.priority is invalid")
        else:
            errors.append(f"requirements.{req_id}.status must be approved or excluded")

    if len(claimed) != len(set(claimed)):
        errors.append("acceptance scenario IDs may belong to only one approved requirement")
    if set(claimed) != set(acs):
        errors.append("approved requirements acceptanceScenarioIds and acceptanceScenarios IDs must be equal")

    dependencies: dict[str, list[str]] = {}
    for ac_id, scenario in acs.items():
        for field in ("title", "requirementId", "flowId", "screenIds", "kind", "subject", "operation", "verificationSurfaces", "dependsOnAcceptanceScenarioIds"):
            if field not in scenario:
                errors.append(f"acceptanceScenarios.{ac_id}.{field} is required")
        if "required" in scenario:
            errors.append(f"acceptanceScenarios.{ac_id}.required is removed in Protocol 2.0")
        if not isinstance(scenario.get("title"), str) or not scenario["title"].strip(): errors.append(f"acceptanceScenarios.{ac_id}.title is required")
        if scenario.get("kind") not in {"action", "state", "failure"}: errors.append(f"acceptanceScenarios.{ac_id}.kind is invalid")
        if not isinstance(scenario.get("subject"), str) or not scenario["subject"].strip(): errors.append(f"acceptanceScenarios.{ac_id}.subject is required")
        if not isinstance(scenario.get("operation"), str) or not scenario["operation"].strip(): errors.append(f"acceptanceScenarios.{ac_id}.operation is required")
        req_id = scenario.get("requirementId")
        if not isinstance(req_id, str) or req_id not in reqs or reqs.get(req_id, {}).get("status") != "approved":
            errors.append(f"acceptanceScenarios.{ac_id}.requirementId must reference an approved requirement")
        if scenario.get("flowId") not in flows:
            errors.append(f"acceptanceScenarios.{ac_id}.flowId must reference a declared flow")
        screen_ids = scenario.get("screenIds")
        if not isinstance(screen_ids, list) or not screen_ids or any(not isinstance(v, str) for v in screen_ids) or len(screen_ids) != len(set(screen_ids)) or any(s not in screens for s in screen_ids):
            errors.append(f"acceptanceScenarios.{ac_id}.screenIds must reference declared screens")
        surfaces = scenario.get("verificationSurfaces")
        if not isinstance(surfaces, list) or not surfaces or any(not isinstance(v, str) or not v for v in surfaces) or len(surfaces) != len(set(surfaces)):
            errors.append(f"acceptanceScenarios.{ac_id}.verificationSurfaces must be a non-empty unique array")
        deps = scenario.get("dependsOnAcceptanceScenarioIds")
        if not isinstance(deps, list) or any(not isinstance(v, str) for v in deps) or len(deps) != len(set(deps)):
            errors.append(f"acceptanceScenarios.{ac_id}.dependsOnAcceptanceScenarioIds must be a unique array")
            deps = []
        for dep in deps:
            if dep not in acs:
                errors.append(f"acceptanceScenarios.{ac_id} dependency {dep!r} does not exist")
            if dep == ac_id:
                errors.append(f"acceptanceScenarios.{ac_id} cannot depend on itself")
        dependencies[ac_id] = [str(v) for v in deps]

        flow_path = root / "flows" / f"{scenario.get('flowId')}.md"
        if flow_path.is_file():
            text = flow_path.read_text(encoding="utf-8-sig")
            marker = f"## {ac_id}"
            start = text.find(marker)
            next_heading = text.find("\n## ", start + len(marker)) if start >= 0 else -1
            section = text[start: next_heading if next_heading >= 0 else None] if start >= 0 else ""
            positions = [section.lower().find(word) for word in ("given", "when", "then")]
            if start < 0 or any(v < 0 for v in positions) or positions != sorted(positions):
                errors.append(f"{ac_id} section must contain its own ordered Given/When/Then")
            linked_screens = scenario.get("screenIds") if isinstance(scenario.get("screenIds"), list) else []
            for linked in [scenario.get("requirementId"), *linked_screens]:
                if isinstance(linked, str) and linked not in text: errors.append(f"{ac_id} flow file must link {linked}")

    colors: dict[str, int] = {}
    stack: list[str] = []
    def visit(node: str) -> None:
        colors[node] = 1
        stack.append(node)
        for dep in dependencies.get(node, []):
            if dep not in dependencies:
                continue
            if colors.get(dep) == 1:
                cycle = stack[stack.index(dep):] + [dep]
                errors.append("acceptance scenario dependency cycle: " + " -> ".join(cycle))
            elif colors.get(dep, 0) == 0:
                visit(dep)
        stack.pop()
        colors[node] = 2
    for ac_id in dependencies:
        if colors.get(ac_id, 0) == 0:
            visit(ac_id)

    entities = data.get("managedEntities")
    if not isinstance(entities, list):
        errors.append("managedEntities must be an array")
        entities = []
    for index, entity in enumerate(entities):
        if not isinstance(entity, dict) or not isinstance(entity.get("entity"), str) or not isinstance(entity.get("operations"), dict):
            errors.append(f"managedEntities[{index}] requires entity and operations")
            continue
        operations = entity["operations"]
        for operation in ("create", "read", "update", "delete"):
            if operation not in operations:
                errors.append(f"managedEntities[{index}].operations.{operation} must explicitly decide required or not-applicable")
        for operation, decision in operations.items():
            label = f"managedEntities[{index}].operations.{operation}"
            if not isinstance(decision, dict) or decision.get("status") not in {"required", "not-applicable"}:
                errors.append(f"{label}.status must be required or not-applicable")
                continue
            if decision["status"] == "required":
                ids = decision.get("acceptanceScenarioIds")
                if not isinstance(ids, list) or not ids or any(not isinstance(v, str) for v in ids) or len(ids) != len(set(ids)):
                    errors.append(f"{label} requires acceptanceScenarioIds")
                elif any(ac not in acs or acs[ac].get("subject") != entity["entity"] or acs[ac].get("operation") != operation for ac in ids):
                    errors.append(f"{label} must reference matching acceptance scenarios")
            elif not isinstance(decision.get("reason"), str) or not decision["reason"].strip():
                errors.append(f"{label}.reason is required for not-applicable")

    targets = data.get("app", {}).get("targets", []) if isinstance(data.get("app"), dict) else []
    valid_gates: list[dict[str, Any]] = []
    for gate_id, gate in gate_map.items():
        for field in ("title", "category", "platform", "requirement", "verificationMethod", "contractSource", "verificationSurfaces"):
            if field not in gate:
                errors.append(f"qualityGates.{gate_id}.{field} is required")
        if not isinstance(gate.get("title"), str) or not gate["title"].strip(): errors.append(f"qualityGates.{gate_id}.title is required")
        if gate.get("category") not in {"repository", "platform", "external", "release"}:
            errors.append(f"qualityGates.{gate_id}.category is invalid")
        if gate.get("requirement") not in {"required", "conditional"}:
            errors.append(f"qualityGates.{gate_id}.requirement must be required or conditional")
        if gate.get("requirement") == "conditional" and not str(gate.get("condition", "")).strip():
            errors.append(f"qualityGates.{gate_id}.condition is required for a conditional quality gate")
        surfaces = gate.get("verificationSurfaces")
        if not isinstance(surfaces, list) or not surfaces or any(not isinstance(v, str) or not v.strip() for v in surfaces) or len(surfaces) != len(set(surfaces)):
            errors.append(f"qualityGates.{gate_id}.verificationSurfaces must be non-empty")
        source = gate.get("contractSource")
        if isinstance(source, str):
            path_text, _, anchor = source.partition("#")
            source_path = Path(path_text)
            if source_path.is_absolute() or ".." in source_path.parts or not (root / source_path).is_file():
                errors.append(f"qualityGates.{gate_id}.contractSource does not resolve")
            elif anchor:
                text = (root / source_path).read_text(encoding="utf-8-sig")
                slugs = []
                for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", text):
                    slug = re.sub(r"[^a-z0-9 -]", "", heading.casefold()).strip().replace(" ", "-")
                    slugs.append(re.sub(r"-+", "-", slug))
                if anchor.casefold() not in slugs: errors.append(f"qualityGates.{gate_id}.contractSource anchor does not exist")
        valid_gates.append(gate)
    if not any(g.get("category") == "repository" and g.get("requirement") == "required" for g in valid_gates):
        errors.append("qualityGates must contain at least one required repository gate")
    if not any(g.get("category") == "release" and g.get("requirement") == "required" for g in valid_gates):
        errors.append("qualityGates must contain at least one required release gate")
    for target in targets:
        if not any(g.get("category") == "platform" and g.get("platform") == target and g.get("requirement") == "required" for g in valid_gates):
            errors.append(f"qualityGates must contain a required platform gate for target {target}")

    for flow in flows:
        if not (root / "flows" / f"{flow}.md").is_file():
            errors.append(f"Missing flow file: flows/{flow}.md")
    for screen in screens:
        screen_path = root / "screens" / f"{screen}.md"
        if not screen_path.is_file():
            errors.append(f"Missing screen file: screens/{screen}.md")
        else:
            text = screen_path.read_text(encoding="utf-8-sig")
            for heading in ("Actions and iconography", "Text layout expectations", "Preview and golden matrix"):
                if not re.search(rf"(?im)^#+\s+{re.escape(heading)}\s*$", text): errors.append(f"screens/{screen}.md missing heading: {heading}")
    if not isinstance(data.get("openQuestions"), list): errors.append("openQuestions must be an array")
    for question in data.get("openQuestions", []) if isinstance(data.get("openQuestions"), list) else []:
        if isinstance(question, dict) and question.get("blocking") is True and question.get("status") == "open":
            errors.append(f"blocking open question remains unresolved: {question.get('id', '<unknown>')}")
    localization = data.get("localization")
    expected_localization = {"defaultLocale":"en", "localeSelection":"system-only", "resourceSystem":"compose-multiplatform-resources", "resourceFileFormat":"strings.xml", "keyStrategy":"shared-key-across-locales", "localDataTextStorage":"resource-keys-only", "nativeFallback":"platform-localized-resources", "hardcodedUserFacingStrings":False}
    if not isinstance(localization, dict): errors.append("localization must be an object")
    else:
        for field, expected in expected_localization.items():
            if localization.get(field) != expected: errors.append(f"localization.{field} must be {expected!r}")
    architecture = data.get("architecture")
    expected_architecture = {"resultType":"kotlin-result", "componentModel":"immutable-value", "stateOwner":"mvikotlin-store", "stateMapping":"store-state-to-component-model", "storeDataAccess":"manager-result-unwrap", "managerResultCapture":"runCatching", "previewComponent":"separate-preview-implementation", "componentModuleStrategy":"screen-or-flow-boundary"}
    if not isinstance(architecture, dict): errors.append("architecture must be an object")
    else:
        for field, expected in expected_architecture.items():
            if architecture.get(field) != expected: errors.append(f"architecture.{field} must be {expected!r}")
        if architecture.get("screenshotTestHost") not in {"compose-ui-module", "dedicated-android-host-module"}: errors.append("architecture.screenshotTestHost is invalid")
        if not isinstance(architecture.get("screenshotTestHostRationale"), str) or len(architecture["screenshotTestHostRationale"].strip()) < 20: errors.append("architecture.screenshotTestHostRationale is too short")
    ui = data.get("uiQuality")
    if not isinstance(ui, dict): errors.append("uiQuality must be an object")
    else:
        themes = ui.get("previewThemes", []); scales = ui.get("fontScales", [])
        if not isinstance(themes, list) or any(not isinstance(v, str) for v in themes) or not {"light", "dark"} <= set(themes): errors.append("uiQuality.previewThemes must include light and dark")
        if not isinstance(scales, list) or 1.0 not in scales or not any(isinstance(v, (int, float)) and v > 1.0 for v in scales): errors.append("uiQuality.fontScales must include 1.0 and a stress scale")
        golden, review, icons = ui.get("goldenTesting"), ui.get("designReview"), ui.get("iconography")
        if not isinstance(golden, dict) or golden.get("required") is not True or golden.get("engine") != "paparazzi" or golden.get("previewDiscovery") != "ComposablePreviewScanner": errors.append("uiQuality.goldenTesting contract is invalid")
        standards = review.get("standards", []) if isinstance(review, dict) else []
        if not isinstance(review, dict) or review.get("required") is not True or review.get("provider") != "lazyweb" or review.get("trigger") != "after-goldens" or not isinstance(standards, list) or "material3" not in standards: errors.append("uiQuality.designReview contract is invalid")
        if not isinstance(icons, dict) or icons.get("inventoryStatus") not in {"approved", "not-required"} or icons.get("customAssetsStatus") not in {"provided", "not-required"}: errors.append("uiQuality.iconography inventory is unresolved")
    capabilities = data.get("capabilities")
    if not isinstance(capabilities, dict): errors.append("capabilities must be an object")
    else:
        for field in ("network", "database", "settings", "sync", "authentication", "notifications", "exactAlarms", "ads"):
            if not isinstance(capabilities.get(field), bool): errors.append(f"capabilities.{field} must be boolean")
    constraints = data.get("constraints")
    if not isinstance(constraints, dict): errors.append("constraints must be an object")
    else:
        for field in ("offlineMode", "privacy", "accessibility", "performance"):
            if field not in constraints: errors.append(f"constraints.{field} is required")
    return errors, warnings


def validate_app_spec(root: str | Path) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    spec_root = Path(root).resolve()
    try:
        data = read_json(spec_root / "app-spec.json")
    except ProtocolError as exc:
        return None, [str(exc)], []
    errors, warnings = validate_app_spec_data(spec_root, data)
    return data, errors, warnings


def paths_within_boundaries(paths: Iterable[str], boundaries: Iterable[str]) -> bool:
    def normalized(value: str) -> str:
        result = PurePosixPath(value.replace("\\", "/")).as_posix()
        while result.startswith("./"):
            result = result[2:]
        return result
    normalized_boundaries = [normalized(v) for v in boundaries]
    for raw in paths:
        path = normalized(raw)
        if not any(fnmatch.fnmatchcase(path, boundary) or path == boundary.rstrip("/") or path.startswith(boundary.rstrip("/") + "/") for boundary in normalized_boundaries):
            return False
    return True


def workspace_drift_paths(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    old = {item["path"]: item.get("sha256") for item in previous.get("workingFiles", []) if isinstance(item, dict) and isinstance(item.get("path"), str)}
    new = {item["path"]: item.get("sha256") for item in current.get("workingFiles", []) if isinstance(item, dict) and isinstance(item.get("path"), str)}
    return sorted(path for path in set(old) | set(new) if old.get(path) != new.get(path))
