#!/usr/bin/env python3
"""Render the deterministic Protocol 2.0 delivery-ledger projection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(SCRIPT_DIR))

from vibe_protocol import ProtocolError, read_json

def esc(value: Any) -> str: return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")

def render_report(ledger: dict[str, Any]) -> str:
    execution = ledger["execution"]
    lines = [
        "# Requirement traceability", "",
        f"- Protocol: `{ledger['schemaVersion']}`",
        f"- Ledger: `{ledger['ledgerId']}`",
        f"- Phase: `{execution['phase']}`",
        f"- Active AC: `{execution.get('activeAcceptanceScenarioId') or 'none'}`",
        f"- Ledger digest: `{ledger['ledgerDigest']}`",
        f"- AppSpec fingerprint: `{ledger['appSpec']['fingerprint']['digest']}`",
        f"- Workspace fingerprint: `{ledger['workspaceFingerprint']['digest']}`",
        f"- Next action: {execution['nextAction']}", "",
        "## Acceptance scenarios", "",
        "| ID | Requirement | Priority | Dependencies | Status | Surfaces | Owner | Receipts |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in sorted(ledger["acceptanceScenarios"], key=lambda v: v["id"]):
        lines.append("| " + " | ".join(esc(v) for v in (
            item["id"], item["requirementId"], item["priority"], ", ".join(item["dependsOnAcceptanceScenarioIds"]) or "—",
            item["status"], ", ".join(item["requiredVerificationSurfaces"]), item.get("owner"), ", ".join(item.get("receiptRefs", [])) or "—")) + " |")
    lines += ["", "## Quality gates", "", "| ID | Category | Platform | Applicability | Status | Surfaces | Receipts |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for item in sorted(ledger["qualityGates"], key=lambda v: v["id"]):
        lines.append("| " + " | ".join(esc(v) for v in (item["id"], item["category"], item["platform"], item["applicability"], item["status"], ", ".join(item["requiredVerificationSurfaces"]), ", ".join(item.get("receiptRefs", [])) or "—")) + " |")
    if ledger.get("workPackages"):
        lines += ["", "## Integrated flows (separate from AC verification)", "", "| Package | ACs | Integration | Goal |", "| --- | --- | --- | --- |"]
        for pid, package in sorted(ledger["workPackages"].items()):
            lines.append("| " + " | ".join(esc(v) for v in (pid, ", ".join(package.get("acceptanceScenarioIds", [])), package.get("status"), package.get("integrationGoal"))) + " |")
    lines += ["", "## Durable hand-offs", ""]
    if ledger.get("ingestedHandoffs"):
        lines.extend(f"- `{item['handoffId']}` — `{item['sha256']}` ({item['path']})" for item in ledger["ingestedHandoffs"])
    else: lines.append("None.")
    lines += ["", "## Closure bindings", "", f"- Final receipt: `{ledger.get('finalReceiptRef') or 'none'}`", f"- Audit request: `{ledger.get('closureAudit', {}).get('requestPath') or 'none'}`", f"- Closure audit: `{ledger.get('closureAudit', {}).get('auditPath') or 'none'}`"]
    return "\n".join(lines).rstrip() + "\n"

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path); parser.add_argument("--output", type=Path); parser.add_argument("--check", action="store_true")
    args = parser.parse_args(); root = args.project_root.resolve(); ledger_path = (args.ledger or root / ".vibe" / "delivery-ledger.json").resolve(); output = (args.output or root / "docs" / "requirement-traceability.generated.md").resolve()
    try: rendered = render_report(read_json(ledger_path))
    except (ProtocolError, OSError, KeyError, TypeError) as exc: print(f"ERROR: {exc}", file=sys.stderr); return 2
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8-sig") != rendered: print(f"ERROR: generated report is stale: {output}", file=sys.stderr); return 1
        print(f"OK: {output} is current"); return 0
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(rendered, encoding="utf-8", newline="\n"); print(f"WROTE: {output}"); return 0

if __name__ == "__main__": raise SystemExit(main())
