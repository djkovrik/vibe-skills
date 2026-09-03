#!/usr/bin/env python3
"""Safely stage an AppSpec 1.3 tree as an explicitly unapproved 1.4 draft."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import uuid
from pathlib import Path

VERSION_13 = re.compile(r"1\.3(?:\.\d+)?")
AC_ID = re.compile(r"\bAC-\d{3,}\b")
SCREEN_ID = re.compile(r"\bSCREEN-\d{3,}\b")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="legacy AppSpec 1.3 directory")
    parser.add_argument("output", help="new directory to create; it must not exist")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be an object")
    return data


def next_question_id(existing: object) -> int:
    maximum = 0
    if isinstance(existing, list):
        for item in existing:
            if isinstance(item, dict):
                match = re.fullmatch(r"OQ-(\d{3,})", str(item.get("id", "")))
                if match:
                    maximum = max(maximum, int(match.group(1)))
    return maximum + 1


def make_question(number: int, question: str, screens: list[str] | None = None) -> dict[str, object]:
    result: dict[str, object] = {
        "id": f"OQ-{number:03d}",
        "question": question,
        "blocking": True,
        "status": "open",
    }
    if screens:
        result["relatedScreens"] = screens
    return result


def flow_documents(source: Path, flow_ids: list[str]) -> dict[str, str]:
    documents: dict[str, str] = {}
    for flow_id in flow_ids:
        path = source / "flows" / f"{flow_id}.md"
        try:
            documents[flow_id] = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError):
            documents[flow_id] = ""
    return documents


def build_scenarios(
    data: dict[str, object],
    documents: dict[str, str],
) -> tuple[list[dict[str, object]], list[str]]:
    scenarios: list[dict[str, object]] = []
    ambiguities: list[str] = []
    declared_screens = [item for item in data.get("screens", []) if isinstance(item, str)]
    requirements = data.get("requirements", [])
    if not isinstance(requirements, list):
        return scenarios, ["requirements is not an array"]

    for requirement in requirements:
        if not isinstance(requirement, dict):
            ambiguities.append("a requirement entry is not an object")
            continue
        requirement_id = requirement.get("id")
        if not isinstance(requirement_id, str):
            ambiguities.append("a requirement has no stable string ID")
            continue
        acceptance_ids = requirement.get("acceptanceScenarioIds", [])
        if not isinstance(acceptance_ids, list):
            ambiguities.append(f"{requirement_id} acceptanceScenarioIds is not an array")
            continue
        for acceptance_id in acceptance_ids:
            if not isinstance(acceptance_id, str) or AC_ID.fullmatch(acceptance_id) is None:
                ambiguities.append(f"{requirement_id} has an invalid acceptance reference {acceptance_id!r}")
                continue
            locations = [flow_id for flow_id, text in documents.items() if acceptance_id in text]
            flow_id = locations[0] if len(locations) == 1 else next(iter(documents), "FLOW-NEEDS-REVIEW")
            if len(locations) != 1:
                ambiguities.append(
                    f"{acceptance_id} must be assigned to exactly one flow; source matches were {locations}"
                )
            flow_text = documents.get(flow_id, "")
            linked_screens = sorted(set(SCREEN_ID.findall(flow_text)) & set(declared_screens))
            if not linked_screens:
                linked_screens = declared_screens[:]
                ambiguities.append(
                    f"{acceptance_id} had no unambiguous screen link; review proposed screenIds {linked_screens}"
                )
            scenarios.append(
                {
                    "id": acceptance_id,
                    "title": f"Review migrated scenario for {requirement.get('title', requirement_id)}",
                    "requirementId": requirement_id,
                    "flowId": flow_id,
                    "screenIds": linked_screens,
                    "kind": "action",
                    "subject": "needs-review",
                    "operation": "needs-review",
                    "verificationSurfaces": ["needs-review"],
                    "reviewStatus": "needs-review",
                }
            )
    return scenarios, ambiguities


def build_quality_gates(targets: list[str]) -> list[dict[str, object]]:
    gates: list[dict[str, object]] = [
        {
            "id": "QG-001",
            "title": "Review repository verification gate",
            "category": "repository",
            "platform": "all",
            "requirement": "required",
            "verificationMethod": "needs-review",
            "contractSource": "quality.md",
            "reviewStatus": "needs-review",
        }
    ]
    for target in targets:
        gates.append(
            {
                "id": f"QG-{len(gates) + 1:03d}",
                "title": f"Review {target} platform verification gate",
                "category": "platform",
                "platform": target,
                "requirement": "required",
                "verificationMethod": "needs-review",
                "contractSource": "quality.md",
                "reviewStatus": "needs-review",
            }
        )
    gates.append(
        {
            "id": f"QG-{len(gates) + 1:03d}",
            "title": "Review release verification gate",
            "category": "release",
            "platform": "all",
            "requirement": "required",
            "verificationMethod": "needs-review",
            "contractSource": "quality.md",
            "reviewStatus": "needs-review",
        }
    )
    return gates


def migrate(source: Path, output: Path) -> None:
    source = source.resolve()
    output = output.resolve()
    if not source.is_dir():
        raise ValueError(f"source directory does not exist: {source}")
    if output.exists():
        raise ValueError(f"output path already exists; refusing to overwrite: {output}")
    if output == source or source in output.parents:
        raise ValueError("output must not be the source or a directory inside the source tree")
    if not output.parent.is_dir():
        raise ValueError(f"output parent directory does not exist: {output.parent}")

    data = read_json(source / "app-spec.json")
    version = data.get("schemaVersion")
    if not isinstance(version, str) or VERSION_13.fullmatch(version) is None:
        raise ValueError(f"migrator accepts AppSpec 1.3 only; found {version!r}")

    flow_ids = [item for item in data.get("flows", []) if isinstance(item, str)]
    documents = flow_documents(source, flow_ids)
    scenarios, ambiguities = build_scenarios(data, documents)
    targets = []
    app = data.get("app")
    if isinstance(app, dict) and isinstance(app.get("targets"), list):
        targets = [item for item in app["targets"] if isinstance(item, str)]

    data["schemaVersion"] = "1.4"
    data["acceptanceScenarios"] = scenarios
    data["managedEntities"] = []
    data["qualityGates"] = build_quality_gates(targets)
    questions = data.get("openQuestions")
    if not isinstance(questions, list):
        questions = []
    question_number = next_question_id(questions)
    questions.append(
        make_question(
            question_number,
            "Review every migrated acceptanceScenarios entry against its FLOW section, split compound outcomes, replace needs-review fields, and approve each scenario.",
        )
    )
    question_number += 1
    questions.append(
        make_question(
            question_number,
            "Inventory every managed entity and explicitly decide create/read/update/delete plus any product-specific operations.",
        )
    )
    question_number += 1
    questions.append(
        make_question(
            question_number,
            "Confirm required and conditional repository, platform, external, and release quality gates and replace every needs-review verification method.",
        )
    )
    question_number += 1
    for ambiguity in ambiguities:
        questions.append(make_question(question_number, f"Resolve migration ambiguity: {ambiguity}"))
        question_number += 1
    data["openQuestions"] = questions

    temporary = output.parent / f".{output.name}.migrating-{uuid.uuid4().hex}"
    temporary.mkdir()
    try:
        shutil.copytree(source, temporary, dirs_exist_ok=True)
        (temporary / "app-spec.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            errors="strict",
        )
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)


def main() -> int:
    args = parse_args()
    try:
        migrate(Path(args.source), Path(args.output))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Created unapproved AppSpec 1.4 migration draft: {Path(args.output).resolve()}")
    print("RESULT: NEEDS-REVIEW")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
