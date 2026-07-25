#!/usr/bin/env python3
"""Read-only validator for Vibe AppSpec v1."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ID_PATTERNS = {
    "requirement": re.compile(r"\bREQ-\d{3,}\b"),
    "flow": re.compile(r"\bFLOW-\d{3,}\b"),
    "screen": re.compile(r"\bSCREEN-\d{3,}\b"),
    "acceptance": re.compile(r"\bAC-\d{3,}\b"),
}

CAPABILITY_TERMS = {
    "network": ("api", "http", "network", "remote"),
    "database": ("database", "table", "sqldelight", "cache"),
    "settings": ("settings", "preference", "flag"),
    "sync": ("sync", "conflict", "snapshot", "merge"),
    "authentication": ("auth", "oauth", "sign-in", "login", "token"),
    "notifications": ("notification", "push"),
    "exactAlarms": ("exact alarm", "schedule_exact_alarm", "reminder"),
    "ads": ("ad slot", "advert", "banner", "rewarded", "interstitial"),
}


def read_utf8(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="strict")
    except UnicodeError as exc:
        errors.append(f"{path}: not valid UTF-8: {exc}")
    except OSError as exc:
        errors.append(f"{path}: cannot read: {exc}")
    return ""


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate-app-spec.py <app-spec-directory>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    required = ("app-spec.json", "product.md", "domain.md", "data.md", "quality.md")

    expect(root.is_dir(), f"AppSpec directory does not exist: {root}", errors)
    if errors:
        return report(errors, warnings)

    for relative in required:
        expect((root / relative).is_file(), f"Missing required file: {relative}", errors)
    expect((root / "flows").is_dir(), "Missing required directory: flows", errors)
    expect((root / "screens").is_dir(), "Missing required directory: screens", errors)
    if errors:
        return report(errors, warnings)

    raw_json = read_utf8(root / "app-spec.json", errors)
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        errors.append(f"app-spec.json: invalid JSON: {exc}")
        return report(errors, warnings)

    expect(isinstance(data, dict), "app-spec.json root must be an object", errors)
    version = data.get("schemaVersion")
    expect(isinstance(version, str), "schemaVersion must be a string", errors)
    if isinstance(version, str):
        major = version.split(".", 1)[0]
        expect(major == "1", f"Unsupported schema major version: {version}", errors)

    app = data.get("app")
    requirements = data.get("requirements")
    flows = data.get("flows")
    screens = data.get("screens")
    capabilities = data.get("capabilities")
    constraints = data.get("constraints")
    for key, value, kind in (
        ("app", app, dict),
        ("requirements", requirements, list),
        ("flows", flows, list),
        ("screens", screens, list),
        ("capabilities", capabilities, dict),
        ("constraints", constraints, dict),
    ):
        expect(isinstance(value, kind), f"{key} must be {kind.__name__}", errors)

    if isinstance(app, dict):
        for key in ("name", "summary", "targets", "locales"):
            expect(key in app, f"app.{key} is required", errors)
    if isinstance(constraints, dict):
        for key in ("offlineMode", "privacy", "accessibility", "performance"):
            expect(key in constraints, f"constraints.{key} is required", errors)
    expect("openQuestions" in data and isinstance(data.get("openQuestions"), list),
           "openQuestions must be an array", errors)

    requirement_ids: list[str] = []
    requirement_acceptance: dict[str, list[str]] = {}
    if isinstance(requirements, list):
        for index, requirement in enumerate(requirements):
            if not isinstance(requirement, dict):
                errors.append(f"requirements[{index}] must be an object")
                continue
            for key in ("id", "title", "priority", "status", "acceptanceScenarioIds"):
                expect(key in requirement, f"requirements[{index}].{key} is required", errors)
            rid = requirement.get("id")
            if isinstance(rid, str):
                expect(bool(ID_PATTERNS["requirement"].fullmatch(rid)),
                       f"Invalid requirement ID: {rid}", errors)
                requirement_ids.append(rid)
                acceptance = requirement.get("acceptanceScenarioIds", [])
                if isinstance(acceptance, list):
                    requirement_acceptance[rid] = [item for item in acceptance if isinstance(item, str)]

    check_unique("requirement", requirement_ids, errors)
    flow_ids = [item for item in flows or [] if isinstance(item, str)]
    screen_ids = [item for item in screens or [] if isinstance(item, str)]
    check_unique("flow", flow_ids, errors)
    check_unique("screen", screen_ids, errors)

    flow_text: dict[str, str] = {}
    for flow_id in flow_ids:
        expect(bool(ID_PATTERNS["flow"].fullmatch(flow_id)), f"Invalid flow ID: {flow_id}", errors)
        path = root / "flows" / f"{flow_id}.md"
        expect(path.is_file(), f"Missing flow file: flows/{flow_id}.md", errors)
        if path.is_file():
            flow_text[flow_id] = read_utf8(path, errors)

    screen_text: dict[str, str] = {}
    for screen_id in screen_ids:
        expect(bool(ID_PATTERNS["screen"].fullmatch(screen_id)), f"Invalid screen ID: {screen_id}", errors)
        path = root / "screens" / f"{screen_id}.md"
        expect(path.is_file(), f"Missing screen file: screens/{screen_id}.md", errors)
        if path.is_file():
            screen_text[screen_id] = read_utf8(path, errors)

    acceptance_locations: dict[str, list[str]] = {}
    for flow_id, text in flow_text.items():
        for acceptance_id in set(ID_PATTERNS["acceptance"].findall(text)):
            acceptance_locations.setdefault(acceptance_id, []).append(flow_id)
        expect(flow_id in text, f"{flow_id}.md must contain its stable ID", errors)
        expect("Given" in text and "When" in text and "Then" in text,
               f"{flow_id}.md must contain Given/When/Then scenarios", errors)

    for screen_id, text in screen_text.items():
        expect(screen_id in text, f"{screen_id}.md must contain its stable ID", errors)
        linked_flow = bool(set(ID_PATTERNS["flow"].findall(text)) & set(flow_ids))
        linked_req = bool(set(ID_PATTERNS["requirement"].findall(text)) & set(requirement_ids))
        expect(linked_flow, f"{screen_id}.md must link to a declared flow", errors)
        expect(linked_req, f"{screen_id}.md must link to a declared requirement", errors)

    all_acceptance_refs: list[str] = []
    for rid, acceptance_ids in requirement_acceptance.items():
        expect(bool(acceptance_ids), f"{rid} must reference at least one acceptance scenario", errors)
        all_acceptance_refs.extend(acceptance_ids)
        linked_by_artifact = any(rid in text for text in (*flow_text.values(), *screen_text.values()))
        expect(linked_by_artifact, f"{rid} is not linked from any flow or screen", errors)
        for acceptance_id in acceptance_ids:
            locations = acceptance_locations.get(acceptance_id, [])
            expect(len(locations) == 1,
                   f"{rid} -> {acceptance_id} must resolve to exactly one flow; found {locations}", errors)
    check_unique("acceptance reference", all_acceptance_refs, errors)

    declared_acceptance = set(acceptance_locations)
    orphan_acceptance = declared_acceptance - set(all_acceptance_refs)
    if orphan_acceptance:
        warnings.append(f"Acceptance scenarios not referenced by requirements: {sorted(orphan_acceptance)}")

    corpus_lines = "\n".join(
        [read_utf8(root / "data.md", errors), *flow_text.values()]
    ).lower().splitlines()
    positive_lines = [
        line
        for line in corpus_lines
        if not line.lstrip().startswith("#")
        and not re.search(r"\b(no|none|without|not required|not applicable)\b", line)
    ]
    corpus = "\n".join(positive_lines)
    if isinstance(capabilities, dict):
        for capability, terms in CAPABILITY_TERMS.items():
            enabled = capabilities.get(capability)
            expect(isinstance(enabled, bool), f"capabilities.{capability} must be boolean", errors)
            mentioned = any(term in corpus for term in terms)
            if enabled is True and not mentioned:
                errors.append(f"Capability {capability}=true is not described in data.md or flows")
            elif enabled is False and mentioned:
                warnings.append(f"Capability {capability}=false but related terms appear in data/flows")

    if data.get("openQuestions"):
        warnings.append("openQuestions is not empty; resolve material product decisions before implementation")

    return report(errors, warnings)


def check_unique(label: str, values: list[str], errors: list[str]) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        errors.append(f"Duplicate {label} IDs: {duplicates}")


def report(errors: list[str], warnings: list[str]) -> int:
    print(f"ERRORS ({len(errors)})")
    for item in errors:
        print(f"- {item}")
    print(f"WARNINGS ({len(warnings)})")
    for item in warnings:
        print(f"- {item}")
    if errors:
        print("RESULT: INVALID")
        return 1
    print("RESULT: VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
