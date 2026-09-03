#!/usr/bin/env python3
"""Render the deterministic Markdown view of a Vibe closure audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render(data: dict[str, Any]) -> str:
    inventory = data["shadowInventory"]
    completion = data["completion"]
    lines = [
        "# Closure audit",
        "",
        f"- Verdict: `{data['verdict']}`",
        f"- Completed at: `{data['completedAt']}`",
        f"- Fresh context: `{'true' if data['auditorContext']['fresh'] else 'false'}`",
        f"- Implementation complete: `{'true' if completion['implementationComplete'] else 'false'}`",
        f"- Release ready: `{'true' if completion['releaseReady'] else 'false'}`",
        f"- AppSpec fingerprint: `{data['appSpecFingerprint']['digest']}`",
        f"- Workspace fingerprint: `{data['workspaceFingerprint']['digest']}`",
        "",
        "## Shadow inventory",
        "",
        "| Kind | Count | IDs |",
        "| --- | ---: | --- |",
    ]
    labels = (
        ("Requirements", "requirementIds"),
        ("Acceptance scenarios", "acceptanceScenarioIds"),
        ("Managed operations", "managedOperationIds"),
        ("Quality gates", "qualityGateIds"),
    )
    for label, key in labels:
        values = inventory[key]
        lines.append(f"| {label} | {len(values)} | {_escape(', '.join(values) or '—')} |")

    lines.extend([
        "",
        "## Obligations",
        "",
        "| ID | Kind | Scope | Result | Surfaces | Evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for item in data["obligations"]:
        evidence = []
        for entry in item["evidence"]:
            detail = entry["path"]
            if entry.get("symbol"):
                detail += f"::{entry['symbol']}"
            if entry.get("testName"):
                detail += f"::{entry['testName']}"
            evidence.append(f"{detail} ({entry['surface']})")
        lines.append(
            f"| {_escape(item['id'])} | {_escape(item['kind'])} | {_escape(item['scope'])} | {_escape(item['result'])} | "
            f"{_escape(', '.join(item['verificationSurfaces']) or '—')} | {_escape('; '.join(evidence) or '—')} |"
        )

    lines.extend(["", "## Findings", ""])
    if not data["findings"]:
        lines.append("No findings.")
    else:
        for finding in data["findings"]:
            refs = ", ".join(finding["obligationIds"]) or "none"
            lines.append(f"### {finding['id']} — {finding['kind']}")
            lines.append("")
            lines.append(f"Obligations: `{_escape(refs)}`")
            lines.append("")
            lines.append(finding["summary"])
            if finding.get("neededProof"):
                lines.extend(["", f"Needed proof: {finding['neededProof']}"])
            lines.append("")

    lines.extend([
        "## Checks",
        "",
        "| ID | Result | Exit code | Obligations | Command |",
        "| --- | --- | ---: | --- | --- |",
    ])
    for check in data["checks"]:
        exit_code = "—" if check["exitCode"] is None else str(check["exitCode"])
        lines.append(
            f"| {_escape(check['id'])} | {_escape(check['result'])} | {exit_code} | "
            f"{_escape(', '.join(check['obligationIds']) or '—')} | `{_escape(check['command'])}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        data = json.loads(args.audit.read_text(encoding="utf-8-sig"))
        expected = render(data)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"ERROR: cannot render audit: {exc}", file=sys.stderr)
        return 2

    if args.check:
        try:
            actual = args.output.read_text(encoding="utf-8-sig")
        except OSError as exc:
            print(f"ERROR: cannot read rendered report: {exc}", file=sys.stderr)
            return 1
        if actual != expected:
            print(f"ERROR: generated report is stale: {args.output}", file=sys.stderr)
            return 1
        print(f"OK: {args.output} is current")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8", newline="\n")
    print(f"WROTE: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
