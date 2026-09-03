#!/usr/bin/env python3
"""Read-only validator for Vibe AppSpec v1."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ID_PATTERNS = {
    "requirement": re.compile(r"\bREQ-\d{3,}\b"),
    "flow": re.compile(r"\bFLOW-\d{3,}\b"),
    "screen": re.compile(r"\bSCREEN-\d{3,}\b"),
    "acceptance": re.compile(r"\bAC-\d{3,}\b"),
    "quality_gate": re.compile(r"\bQG-\d{3,}\b"),
}

CURRENT_MAJOR = 1
CURRENT_MINOR = 4
CRUD_OPERATIONS = ("create", "read", "update", "delete")
QUALITY_CATEGORIES = {"repository", "platform", "external", "release"}

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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app_spec_directory")
    parser.add_argument(
        "--require-current",
        action="store_true",
        help="reject legacy AppSpec versions that are insufficient for a full delivery cycle",
    )
    args = parser.parse_args()

    root = Path(args.app_spec_directory).resolve()
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
    version_major: int | None = None
    version_minor = 0
    if isinstance(version, str):
        version_match = re.fullmatch(r"(\d+)\.(\d+)(?:\.\d+)?", version)
        expect(version_match is not None, f"Invalid schemaVersion: {version}", errors)
        major_text = version.split(".", 1)[0]
        expect(major_text == str(CURRENT_MAJOR), f"Unsupported schema major version: {version}", errors)
        if version_match is not None:
            version_major = int(version_match.group(1))
            version_minor = int(version_match.group(2))
            if version_major == CURRENT_MAJOR and version_minor > CURRENT_MINOR:
                errors.append(
                    f"Unsupported newer schemaVersion {version}; this validator supports through "
                    f"{CURRENT_MAJOR}.{CURRENT_MINOR}"
                )
            elif version_major == CURRENT_MAJOR and version_minor < CURRENT_MINOR:
                warnings.append(
                    f"Legacy AppSpec {version} validated for narrow compatibility only; migrate to "
                    f"{CURRENT_MAJOR}.{CURRENT_MINOR} before a full or cross-cutting $vibe-developer cycle"
                )
                if args.require_current:
                    errors.append(
                        f"--require-current requires AppSpec {CURRENT_MAJOR}.{CURRENT_MINOR}; found {version}"
                    )

    app = data.get("app")
    requirements = data.get("requirements")
    flows = data.get("flows")
    screens = data.get("screens")
    capabilities = data.get("capabilities")
    constraints = data.get("constraints")
    localization = data.get("localization")
    architecture = data.get("architecture")
    ui_quality = data.get("uiQuality")
    acceptance_scenarios = data.get("acceptanceScenarios")
    managed_entities = data.get("managedEntities")
    quality_gates = data.get("qualityGates")
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
        locales = app.get("locales")
        expect(isinstance(locales, list) and bool(locales), "app.locales must be a non-empty array", errors)
        if isinstance(locales, list):
            locale_values = [item for item in locales if isinstance(item, str) and item.strip()]
            expect(
                len(locale_values) == len(locales),
                "app.locales must contain non-empty strings only",
                errors,
            )
            check_unique("locale", locale_values, errors)
    if isinstance(constraints, dict):
        for key in ("offlineMode", "privacy", "accessibility", "performance"):
            expect(key in constraints, f"constraints.{key} is required", errors)
    expect("openQuestions" in data and isinstance(data.get("openQuestions"), list),
           "openQuestions must be an array", errors)

    requires_ui_contract = version_major == 1 and version_minor >= 1
    requires_localization_contract = version_major == 1 and version_minor >= 2
    requires_architecture_contract = version_major == 1 and version_minor >= 3
    requires_atomic_contract = version_major == CURRENT_MAJOR and version_minor >= CURRENT_MINOR
    if requires_ui_contract:
        design_path = root / "design.md"
        expect(design_path.is_file(), "Missing required file for AppSpec 1.1+: design.md", errors)
        expect(isinstance(ui_quality, dict), "uiQuality must be an object for AppSpec 1.1+", errors)
    elif version_major == 1 and not isinstance(ui_quality, dict):
        warnings.append(
            "Legacy AppSpec has no uiQuality contract; previews, goldens, icons, and post-golden review "
            "must be derived and confirmed during implementation"
        )

    if isinstance(ui_quality, dict):
        validate_ui_quality(ui_quality, errors, warnings)

    if requires_localization_contract:
        expect(
            isinstance(localization, dict),
            "localization must be an object for AppSpec 1.2+",
            errors,
        )
    elif version_major == 1 and not isinstance(localization, dict):
        warnings.append(
            "Legacy AppSpec has no localization contract; Compose resources, stable localization keys, "
            "native fallbacks, and hardcoded-string policy must be derived and confirmed during implementation"
        )

    if isinstance(localization, dict):
        validate_localization(localization, errors)
        if isinstance(app, dict) and isinstance(app.get("locales"), list):
            expect(
                localization.get("defaultLocale") in app["locales"],
                "localization.defaultLocale must be included in app.locales",
                errors,
            )

    if requires_architecture_contract:
        expect(
            isinstance(architecture, dict),
            "architecture must be an object for AppSpec 1.3+",
            errors,
        )
    elif version_major == 1 and not isinstance(architecture, dict):
        warnings.append(
            "Legacy AppSpec has no architecture contract; Kotlin Result boundaries, Store-backed component "
            "models, Manager/unwrap data access, preview implementations, component modules, and screenshot "
            "host ownership must be derived and confirmed during implementation"
        )

    if isinstance(architecture, dict):
        validate_architecture(architecture, errors)

    if requires_atomic_contract:
        expect(
            isinstance(acceptance_scenarios, list) and bool(acceptance_scenarios),
            "acceptanceScenarios must be a non-empty array for AppSpec 1.4",
            errors,
        )
        expect(
            isinstance(managed_entities, list),
            "managedEntities must be an array for AppSpec 1.4",
            errors,
        )
        expect(
            isinstance(quality_gates, list) and bool(quality_gates),
            "qualityGates must be a non-empty array for AppSpec 1.4",
            errors,
        )

    open_questions = data.get("openQuestions")
    if isinstance(open_questions, list):
        for index, question in enumerate(open_questions):
            if not isinstance(question, dict):
                continue
            for key in ("id", "question", "blocking", "status"):
                expect(key in question, f"openQuestions[{index}].{key} is required", errors)
            if question.get("blocking") is True:
                status = question.get("status")
                if not isinstance(status, str) or status.lower() not in {"resolved", "waived"}:
                    errors.append(
                        f"openQuestions[{index}] is blocking and unresolved; obtain the user decision/assets "
                        "before implementation"
                    )

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
    acceptance_sections: dict[str, list[tuple[str, str]]] = {}
    for flow_id, text in flow_text.items():
        sections = extract_acceptance_sections(text)
        for acceptance_id, body in sections:
            acceptance_locations.setdefault(acceptance_id, []).append(flow_id)
            acceptance_sections.setdefault(acceptance_id, []).append((flow_id, body))
        expect(flow_id in text, f"{flow_id}.md must contain its stable ID", errors)
        if not requires_atomic_contract:
            expect("Given" in text and "When" in text and "Then" in text,
                   f"{flow_id}.md must contain Given/When/Then scenarios", errors)

    for screen_id, text in screen_text.items():
        expect(screen_id in text, f"{screen_id}.md must contain its stable ID", errors)
        linked_flow = bool(set(ID_PATTERNS["flow"].findall(text)) & set(flow_ids))
        linked_req = bool(set(ID_PATTERNS["requirement"].findall(text)) & set(requirement_ids))
        expect(linked_flow, f"{screen_id}.md must link to a declared flow", errors)
        expect(linked_req, f"{screen_id}.md must link to a declared requirement", errors)
        if requires_ui_contract:
            for heading in (
                "## Text layout expectations",
                "## Actions and iconography",
                "## Preview and golden matrix",
            ):
                expect(heading in text, f"{screen_id}.md must contain {heading}", errors)
            expect(
                "light" in text.lower() and "dark" in text.lower(),
                f"{screen_id}.md preview/golden matrix must cover light and dark",
                errors,
            )

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

    if requires_atomic_contract:
        scenario_ids: list[str] = []
        scenarios_by_id: dict[str, dict[str, object]] = {}
        if isinstance(acceptance_scenarios, list):
            for index, scenario in enumerate(acceptance_scenarios):
                if not isinstance(scenario, dict):
                    errors.append(f"acceptanceScenarios[{index}] must be an object")
                    continue
                for key in (
                    "id", "title", "requirementId", "flowId", "screenIds", "kind",
                    "subject", "operation", "verificationSurfaces",
                ):
                    expect(key in scenario, f"acceptanceScenarios[{index}].{key} is required", errors)
                acceptance_id = scenario.get("id")
                if not isinstance(acceptance_id, str):
                    continue
                expect(
                    bool(ID_PATTERNS["acceptance"].fullmatch(acceptance_id)),
                    f"Invalid acceptance scenario ID: {acceptance_id}",
                    errors,
                )
                scenario_ids.append(acceptance_id)
                scenarios_by_id.setdefault(acceptance_id, scenario)
                for key in ("title", "subject", "operation"):
                    value = scenario.get(key)
                    expect(
                        isinstance(value, str) and bool(value.strip()),
                        f"{acceptance_id}.{key} must be a non-empty string",
                        errors,
                    )
                expect(
                    scenario.get("kind") in {"action", "state", "failure"},
                    f"{acceptance_id}.kind must be action, state, or failure",
                    errors,
                )
                if scenario.get("reviewStatus") == "needs-review":
                    errors.append(
                        f"{acceptance_id}.reviewStatus is needs-review; manually approve or revise the migrated scenario"
                    )
                elif "reviewStatus" in scenario:
                    expect(
                        scenario.get("reviewStatus") == "approved",
                        f"{acceptance_id}.reviewStatus must be approved or needs-review",
                        errors,
                    )

                requirement_id = scenario.get("requirementId")
                expect(
                    isinstance(requirement_id, str) and requirement_id in requirement_ids,
                    f"{acceptance_id}.requirementId must reference a declared requirement; found {requirement_id!r}",
                    errors,
                )
                if isinstance(requirement_id, str) and requirement_id in requirement_acceptance:
                    expect(
                        acceptance_id in requirement_acceptance[requirement_id],
                        f"{acceptance_id} is not listed by its requirement {requirement_id}",
                        errors,
                    )

                flow_id = scenario.get("flowId")
                expect(
                    isinstance(flow_id, str) and flow_id in flow_ids,
                    f"{acceptance_id}.flowId must reference a declared flow; found {flow_id!r}",
                    errors,
                )
                linked_screens = scenario.get("screenIds")
                expect(
                    isinstance(linked_screens, list) and bool(linked_screens),
                    f"{acceptance_id}.screenIds must be a non-empty array",
                    errors,
                )
                if isinstance(linked_screens, list):
                    valid_linked_screens = [item for item in linked_screens if isinstance(item, str)]
                    expect(
                        len(valid_linked_screens) == len(linked_screens),
                        f"{acceptance_id}.screenIds must contain strings only",
                        errors,
                    )
                    check_unique(f"{acceptance_id}.screen", valid_linked_screens, errors)
                    for screen_id in valid_linked_screens:
                        expect(
                            screen_id in screen_ids,
                            f"{acceptance_id}.screenIds references undeclared screen {screen_id}",
                            errors,
                        )

                surfaces = scenario.get("verificationSurfaces")
                expect(
                    isinstance(surfaces, list) and bool(surfaces),
                    f"{acceptance_id}.verificationSurfaces must be a non-empty array",
                    errors,
                )
                if isinstance(surfaces, list):
                    valid_surfaces = [item for item in surfaces if isinstance(item, str) and item.strip()]
                    expect(
                        len(valid_surfaces) == len(surfaces),
                        f"{acceptance_id}.verificationSurfaces must contain non-empty strings only",
                        errors,
                    )
                    check_unique(f"{acceptance_id}.verification surface", valid_surfaces, errors)

                sections = acceptance_sections.get(acceptance_id, [])
                expect(
                    len(sections) == 1,
                    f"{acceptance_id} must have exactly one dedicated Markdown section; found "
                    f"{[item[0] for item in sections]}",
                    errors,
                )
                if len(sections) == 1:
                    section_flow_id, section_body = sections[0]
                    expect(
                        section_flow_id == flow_id,
                        f"{acceptance_id}.flowId is {flow_id!r} but its section is in {section_flow_id}",
                        errors,
                    )
                    expect(
                        has_own_given_when_then(section_body),
                        f"{acceptance_id} section must contain its own ordered Given/When/Then",
                        errors,
                    )
                    flow_document = flow_text.get(section_flow_id, "")
                    if isinstance(requirement_id, str):
                        expect(
                            requirement_id in flow_document,
                            f"{acceptance_id} flow {section_flow_id} does not link requirement {requirement_id}",
                            errors,
                        )
                    if isinstance(linked_screens, list):
                        for screen_id in linked_screens:
                            if isinstance(screen_id, str):
                                expect(
                                    screen_id in flow_document,
                                    f"{acceptance_id} flow {section_flow_id} does not link screen {screen_id}",
                                    errors,
                                )

        check_unique("acceptance scenario", scenario_ids, errors)
        requirement_ref_set = set(all_acceptance_refs)
        scenario_id_set = set(scenario_ids)
        missing_scenarios = requirement_ref_set - scenario_id_set
        unreferenced_scenarios = scenario_id_set - requirement_ref_set
        expect(
            not missing_scenarios and not unreferenced_scenarios,
            "requirements acceptanceScenarioIds and acceptanceScenarios IDs must be equal; "
            f"missing definitions={sorted(missing_scenarios)}, unreferenced definitions={sorted(unreferenced_scenarios)}",
            errors,
        )

        validate_managed_entities(managed_entities, scenarios_by_id, errors)
        targets = app.get("targets", []) if isinstance(app, dict) else []
        validate_quality_gates(root, quality_gates, targets, errors)

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
            mentioned = any(
                re.search(rf"\b{re.escape(term)}\b", corpus) is not None
                for term in terms
            )
            if enabled is True and not mentioned:
                errors.append(f"Capability {capability}=true is not described in data.md or flows")
            elif enabled is False and mentioned:
                warnings.append(f"Capability {capability}=false but related terms appear in data/flows")

    if requires_ui_contract:
        design_text = read_utf8(root / "design.md", errors)
        quality_text = read_utf8(root / "quality.md", errors)
        for heading in (
            "## Lazyweb evidence and direction",
            "## Typography and text layout",
            "## Iconography and assets",
            "## Preview and golden contract",
            "## Post-golden design review",
        ):
            expect(heading in design_text, f"design.md must contain {heading}", errors)
        for heading in (
            "## Preview and golden matrix",
            "## Visual quality and design review",
        ):
            expect(heading in quality_text, f"quality.md must contain {heading}", errors)

    if requires_localization_contract:
        data_text = read_utf8(root / "data.md", errors)
        quality_text = read_utf8(root / "quality.md", errors)
        expect(
            "## Localized text storage" in data_text,
            "data.md must contain ## Localized text storage for AppSpec 1.2+",
            errors,
        )
        expect(
            "## Localization resource checks" in quality_text,
            "quality.md must contain ## Localization resource checks for AppSpec 1.2+",
            errors,
        )

    if requires_architecture_contract:
        quality_text = read_utf8(root / "quality.md", errors)
        expect(
            "## Architecture checks" in quality_text,
            "quality.md must contain ## Architecture checks for AppSpec 1.3+",
            errors,
        )

    if data.get("openQuestions"):
        warnings.append("openQuestions is not empty; resolve material product decisions before implementation")

    return report(errors, warnings)


def extract_acceptance_sections(text: str) -> list[tuple[str, str]]:
    """Return dedicated AC headings and their bodies, preserving duplicates."""
    heading = re.compile(r"(?m)^#{2,6}\s+(AC-\d{3,})\b[^\n]*$")
    any_heading = re.compile(r"(?m)^#{1,6}\s+")
    matches = list(heading.finditer(text))
    result: list[tuple[str, str]] = []
    for match in matches:
        next_heading = any_heading.search(text, match.end())
        end = next_heading.start() if next_heading is not None else len(text)
        result.append((match.group(1), text[match.end():end]))
    return result


def has_own_given_when_then(section: str) -> bool:
    positions: list[int] = []
    for keyword in ("Given", "When", "Then"):
        match = re.search(rf"(?im)^\s*(?:[-*]\s*)?{keyword}\b", section)
        if match is None:
            return False
        positions.append(match.start())
    return positions == sorted(positions) and len(set(positions)) == 3


def validate_managed_entities(
    managed_entities: object,
    scenarios_by_id: dict[str, dict[str, object]],
    errors: list[str],
) -> None:
    if not isinstance(managed_entities, list):
        return
    names: list[str] = []
    for index, entity in enumerate(managed_entities):
        if not isinstance(entity, dict):
            errors.append(f"managedEntities[{index}] must be an object")
            continue
        name = entity.get("entity")
        expect(
            isinstance(name, str) and bool(name.strip()),
            f"managedEntities[{index}].entity must be a non-empty string",
            errors,
        )
        if isinstance(name, str):
            names.append(name)
        operations = entity.get("operations")
        expect(
            isinstance(operations, dict),
            f"managedEntities[{index}].operations must be an object",
            errors,
        )
        if not isinstance(operations, dict):
            continue
        for operation in CRUD_OPERATIONS:
            expect(
                operation in operations,
                f"managedEntities[{index}].operations.{operation} must explicitly decide required or not-applicable",
                errors,
            )
        for operation, decision in operations.items():
            expect(
                isinstance(operation, str) and bool(operation.strip()),
                f"managedEntities[{index}] operation names must be non-empty strings",
                errors,
            )
            if not isinstance(decision, dict):
                errors.append(f"managedEntities[{index}].operations.{operation} must be an object")
                continue
            status = decision.get("status")
            expect(
                status in {"required", "not-applicable"},
                f"managedEntities[{index}].operations.{operation}.status must be required or not-applicable",
                errors,
            )
            if status == "required":
                refs = decision.get("acceptanceScenarioIds")
                expect(
                    isinstance(refs, list) and bool(refs),
                    f"managedEntities[{index}].operations.{operation} requires acceptanceScenarioIds",
                    errors,
                )
                if isinstance(refs, list):
                    valid_refs = [item for item in refs if isinstance(item, str)]
                    expect(
                        len(valid_refs) == len(refs),
                        f"managedEntities[{index}].operations.{operation}.acceptanceScenarioIds must contain strings only",
                        errors,
                    )
                    check_unique(
                        f"managedEntities[{index}].operations.{operation} acceptance reference",
                        valid_refs,
                        errors,
                    )
                    for acceptance_id in valid_refs:
                        scenario = scenarios_by_id.get(acceptance_id)
                        expect(
                            scenario is not None,
                            f"managedEntities[{index}].operations.{operation} references unknown {acceptance_id}",
                            errors,
                        )
                        if scenario is not None and isinstance(name, str):
                            expect(
                                str(scenario.get("subject", "")).casefold() == name.casefold(),
                                f"{acceptance_id}.subject must match managed entity {name!r}",
                                errors,
                            )
                            expect(
                                str(scenario.get("operation", "")).casefold() == operation.casefold(),
                                f"{acceptance_id}.operation must match managed operation {operation!r}",
                                errors,
                            )
            elif status == "not-applicable":
                reason = decision.get("reason")
                expect(
                    isinstance(reason, str) and bool(reason.strip()),
                    f"managedEntities[{index}].operations.{operation}.reason is required for not-applicable",
                    errors,
                )
    duplicates = sorted({value for value in names if names.count(value) > 1})
    if duplicates:
        errors.append(f"Duplicate managed entity names: {duplicates}")


def validate_quality_gates(
    root: Path,
    quality_gates: object,
    targets: object,
    errors: list[str],
) -> None:
    if not isinstance(quality_gates, list):
        return
    gate_ids: list[str] = []
    valid_gates: list[dict[str, object]] = []
    target_values = [item for item in targets if isinstance(item, str)] if isinstance(targets, list) else []
    for index, gate in enumerate(quality_gates):
        if not isinstance(gate, dict):
            errors.append(f"qualityGates[{index}] must be an object")
            continue
        valid_gates.append(gate)
        for key in ("id", "title", "category", "platform", "requirement", "verificationMethod", "contractSource"):
            expect(key in gate, f"qualityGates[{index}].{key} is required", errors)
        gate_id = gate.get("id")
        if isinstance(gate_id, str):
            gate_ids.append(gate_id)
            expect(
                bool(ID_PATTERNS["quality_gate"].fullmatch(gate_id)),
                f"Invalid quality gate ID: {gate_id}",
                errors,
            )
        label = gate_id if isinstance(gate_id, str) else f"qualityGates[{index}]"
        for key in ("title", "platform", "verificationMethod", "contractSource"):
            value = gate.get(key)
            expect(
                isinstance(value, str) and bool(value.strip()),
                f"{label}.{key} must be a non-empty string",
                errors,
            )
        category = gate.get("category")
        expect(category in QUALITY_CATEGORIES, f"{label}.category is invalid: {category!r}", errors)
        requirement = gate.get("requirement")
        expect(
            requirement in {"required", "conditional"},
            f"{label}.requirement must be required or conditional",
            errors,
        )
        if requirement == "conditional":
            condition = gate.get("condition")
            expect(
                isinstance(condition, str) and bool(condition.strip()),
                f"{label}.condition is required for a conditional quality gate",
                errors,
            )
        platform = gate.get("platform")
        if isinstance(platform, str):
            expect(
                platform == "all" or platform in target_values,
                f"{label}.platform must be all or one of app.targets; found {platform!r}",
                errors,
            )
        source = gate.get("contractSource")
        if isinstance(source, str) and source.strip():
            source_path = source.split("#", 1)[0]
            expect(
                bool(source_path) and (root / source_path).is_file(),
                f"{label}.contractSource must name an existing AppSpec file; found {source!r}",
                errors,
            )

    check_unique("quality gate", gate_ids, errors)
    expect(
        any(gate.get("category") == "repository" and gate.get("requirement") == "required" for gate in valid_gates),
        "qualityGates must contain at least one required repository gate",
        errors,
    )
    expect(
        any(gate.get("category") == "release" and gate.get("requirement") == "required" for gate in valid_gates),
        "qualityGates must contain at least one required release gate",
        errors,
    )
    for target in target_values:
        expect(
            any(
                gate.get("category") == "platform"
                and gate.get("requirement") == "required"
                and gate.get("platform") == target
                for gate in valid_gates
            ),
            f"qualityGates must contain a required platform gate for target {target}",
            errors,
        )


def check_unique(label: str, values: list[str], errors: list[str]) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        errors.append(f"Duplicate {label} IDs: {duplicates}")


def validate_ui_quality(
    ui_quality: dict[str, object],
    errors: list[str],
    warnings: list[str],
) -> None:
    preview_themes = ui_quality.get("previewThemes")
    expect(isinstance(preview_themes, list), "uiQuality.previewThemes must be an array", errors)
    if isinstance(preview_themes, list):
        normalized_themes = {item.lower() for item in preview_themes if isinstance(item, str)}
        expect(
            {"light", "dark"}.issubset(normalized_themes),
            "uiQuality.previewThemes must include light and dark",
            errors,
        )

    font_scales = ui_quality.get("fontScales")
    expect(isinstance(font_scales, list) and bool(font_scales),
           "uiQuality.fontScales must be a non-empty array", errors)
    if isinstance(font_scales, list):
        numeric_scales = [
            float(item)
            for item in font_scales
            if isinstance(item, (int, float)) and not isinstance(item, bool)
        ]
        expect(len(numeric_scales) == len(font_scales),
               "uiQuality.fontScales must contain numbers only", errors)
        expect(any(abs(item - 1.0) < 0.001 for item in numeric_scales),
               "uiQuality.fontScales must include 1.0", errors)
        if not any(item > 1.0 for item in numeric_scales):
            warnings.append(
                "uiQuality.fontScales has no enlarged stress scale; confirm that increased font scaling "
                "is not required"
            )

    expect(
        ui_quality.get("localeCoverage") in {"all", "representative"},
        "uiQuality.localeCoverage must be all or representative",
        errors,
    )

    golden = ui_quality.get("goldenTesting")
    expect(isinstance(golden, dict), "uiQuality.goldenTesting must be an object", errors)
    if isinstance(golden, dict):
        expect(golden.get("required") is True, "uiQuality.goldenTesting.required must be true", errors)
        expect(golden.get("engine") == "paparazzi",
               "uiQuality.goldenTesting.engine must be paparazzi", errors)
        expect(
            golden.get("previewDiscovery") == "ComposablePreviewScanner",
            "uiQuality.goldenTesting.previewDiscovery must be ComposablePreviewScanner",
            errors,
        )

    review = ui_quality.get("designReview")
    expect(isinstance(review, dict), "uiQuality.designReview must be an object", errors)
    if isinstance(review, dict):
        expect(review.get("required") is True, "uiQuality.designReview.required must be true", errors)
        expect(review.get("provider") == "lazyweb",
               "uiQuality.designReview.provider must be lazyweb", errors)
        expect(review.get("trigger") == "after-goldens",
               "uiQuality.designReview.trigger must be after-goldens", errors)
        standards = review.get("standards")
        expect(isinstance(standards, list), "uiQuality.designReview.standards must be an array", errors)
        if isinstance(standards, list):
            normalized_standards = {item.lower() for item in standards if isinstance(item, str)}
            expect("material3" in normalized_standards,
                   "uiQuality.designReview.standards must include material3", errors)

    iconography = ui_quality.get("iconography")
    expect(isinstance(iconography, dict), "uiQuality.iconography must be an object", errors)
    if isinstance(iconography, dict):
        expect(
            iconography.get("inventoryStatus") in {"approved", "not-required"},
            "uiQuality.iconography.inventoryStatus must be approved or not-required",
            errors,
        )
        source = iconography.get("standardIconSource")
        expect(isinstance(source, str) and bool(source.strip()),
               "uiQuality.iconography.standardIconSource must be a non-empty string", errors)
        expect(
            iconography.get("customAssetsStatus") in {"provided", "not-required"},
            "uiQuality.iconography.customAssetsStatus must be provided or not-required",
            errors,
        )


def validate_localization(
    localization: dict[str, object],
    errors: list[str],
) -> None:
    expected = {
        "defaultLocale": "en",
        "localeSelection": "system-only",
        "resourceSystem": "compose-multiplatform-resources",
        "resourceFileFormat": "strings.xml",
        "keyStrategy": "shared-key-across-locales",
        "localDataTextStorage": "resource-keys-only",
        "nativeFallback": "platform-localized-resources",
        "hardcodedUserFacingStrings": False,
    }
    for key, value in expected.items():
        expect(
            localization.get(key) == value,
            f"localization.{key} must be {value!r}",
            errors,
        )


def validate_architecture(
    architecture: dict[str, object],
    errors: list[str],
) -> None:
    expected = {
        "resultType": "kotlin-result",
        "componentModel": "immutable-value",
        "stateOwner": "mvikotlin-store",
        "stateMapping": "store-state-to-component-model",
        "storeDataAccess": "manager-result-unwrap",
        "managerResultCapture": "runCatching",
        "previewComponent": "separate-preview-implementation",
        "componentModuleStrategy": "screen-or-flow-boundary",
    }
    for key, value in expected.items():
        expect(
            architecture.get(key) == value,
            f"architecture.{key} must be {value!r}",
            errors,
        )

    host = architecture.get("screenshotTestHost")
    expect(
        host in {"compose-ui-module", "dedicated-android-host-module"},
        "architecture.screenshotTestHost must be compose-ui-module or dedicated-android-host-module",
        errors,
    )
    rationale = architecture.get("screenshotTestHostRationale")
    expect(
        isinstance(rationale, str) and len(rationale.strip()) >= 20,
        "architecture.screenshotTestHostRationale must explain the target-specific ownership decision",
        errors,
    )


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
