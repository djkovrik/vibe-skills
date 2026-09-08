#!/usr/bin/env python3
"""Render the deterministic Markdown view of a closure audit 2.0."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

def esc(value: Any) -> str: return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")

def render(data: dict[str, Any]) -> str:
    context, completion = data["auditorContext"], data["completion"]
    lines = ["# Closure audit", "", f"- Protocol: `{data['schemaVersion']}`", f"- Audit: `{data['auditId']}`", f"- Request: `{data['auditRequest']['requestId']}` / `{data['auditRequest']['sha256']}`", f"- Verdict: `{data['verdict']}`", f"- Started at: `{data['startedAt']}`", f"- Completed at: `{data['completedAt']}`", f"- Context: `{context['contextId']}` (`{context['invocationKind']}`)", f"- Implementation context available: `{'true' if context['implementationContextAvailable'] else 'false'}`", f"- Locally verified: `{'true' if completion['locallyVerified'] else 'false'}`", f"- Implementation complete: `{'true' if completion['implementationComplete'] else 'false'}`", f"- Release ready: `{'true' if completion['releaseReady'] else 'false'}`", "", "## Shadow inventory", "", "| Kind | IDs |", "| --- | --- |"]
    for key in ("requirementIds", "excludedRequirementIds", "acceptanceScenarioIds", "managedOperationIds", "qualityGateIds"):
        lines.append(f"| {esc(key)} | {esc(', '.join(data['shadowInventory'][key]) or '—')} |")
    lines += ["", "## Obligations", "", "| ID | Kind | Scope | Result | Surfaces |", "| --- | --- | --- | --- | --- |"]
    for item in data["obligations"]:
        lines.append(f"| {esc(item['id'])} | {esc(item['kind'])} | {esc(item['scope'])} | {esc(item['result'])} | {esc(', '.join(item['verificationSurfaces']))} |")
    lines += ["", "## Independently reviewed checks", "", "| ID | Exit | Coverage | argv |", "| --- | ---: | --- | --- |"]
    for check in data["checks"]:
        coverage = ", ".join(f"{c['obligationId']}:{c['surface']}" for c in check["coverage"])
        lines.append(f"| {esc(check['checkId'])} | {esc(check['exitCode'])} | {esc(coverage)} | `{esc(' '.join(check['argv']))}` |")
    lines += ["", "## Findings", ""]
    if not data["findings"]: lines.append("No findings.")
    else:
        for finding in data["findings"]: lines.append(f"- **{esc(finding.get('id'))}** ({esc(finding.get('kind'))}): {esc(finding.get('summary'))}")
    return "\n".join(lines).rstrip() + "\n"

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("audit", type=Path); parser.add_argument("output", type=Path); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    try: data = json.loads(args.audit.read_text(encoding="utf-8-sig")); expected = render(data)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc: print(f"ERROR: {exc}", file=sys.stderr); return 2
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8-sig") != expected: print(f"ERROR: generated report is stale: {args.output}", file=sys.stderr); return 1
        print(f"OK: {args.output} is current"); return 0
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(expected, encoding="utf-8", newline="\n"); print(f"WROTE: {args.output}"); return 0

if __name__ == "__main__": raise SystemExit(main())
