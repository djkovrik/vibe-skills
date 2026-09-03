#!/usr/bin/env python3
"""Validate Vibe delivery-ledger structure, evidence, freshness, and verdicts."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


LEDGER_VERSION = "1.0"
STATUSES = {
    "not-started",
    "implemented-unverified",
    "verified",
    "blocked-external",
    "waived",
}
APPLICABILITY = {"applicable", "not-applicable", "needs-review"}


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    implementation_complete: bool = False
    release_ready: bool = False
    audit_current_and_passed: bool = False

    @property
    def valid(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "implementationComplete": self.implementation_complete,
            "releaseReady": self.release_ready,
            "auditCurrentAndPassed": self.audit_current_and_passed,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def _load_fingerprint_module() -> Any:
    path = Path(__file__).with_name("compute-workspace-fingerprint.py")
    spec = importlib.util.spec_from_file_location("vibe_workspace_fingerprint", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load fingerprint implementation: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_audit_validator() -> Any | None:
    path = (
        Path(__file__).resolve().parents[2]
        / "vibe-acceptance-auditor"
        / "scripts"
        / "validate-closure-audit.py"
    )
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("vibe_closure_audit_validator", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object in {path}")
    return value


def _resolve_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty path")
    candidate = Path(value)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} escapes the project root: {value}") from exc
    return resolved


def _resolve_app_spec_path(project_root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("appSpec.root must be a non-empty path")
    candidate = Path(value)
    return candidate.resolve() if candidate.is_absolute() else (project_root / candidate).resolve()


def _id_map(items: Any, label: str, result: ValidationResult) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        result.errors.append(f"{label}: expected an array")
        return {}
    mapped: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            result.errors.append(f"{label}[{index}]: expected an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            result.errors.append(f"{label}[{index}].id: expected a non-empty string")
            continue
        if item_id in mapped:
            result.errors.append(f"{label}: duplicate id {item_id}")
            continue
        mapped[item_id] = item
    return mapped


def _fingerprints_equal(left: Any, right: Any) -> bool:
    return isinstance(left, dict) and isinstance(right, dict) and left == right


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _symbol_exists(path: Path, symbol: str) -> bool:
    try:
        content = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return False
    if not symbol.strip():
        return False
    parts = [part for part in re.split(r"[.#]", symbol) if part]
    for part in parts:
        pattern = r"(?<![A-Za-z0-9_])" + re.escape(part) + r"(?![A-Za-z0-9_])"
        if re.search(pattern, content) is None:
            return False
    return True


def _validate_evidence(
    project_root: Path,
    item: dict[str, Any],
    item_label: str,
    result: ValidationResult,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    production = item.get("productionEvidence")
    tests = item.get("testEvidence")
    if not isinstance(production, list):
        result.errors.append(f"{item_label}.productionEvidence: expected an array")
        production = []
    if not isinstance(tests, list):
        result.errors.append(f"{item_label}.testEvidence: expected an array")
        tests = []

    def validate_entries(entries: list[Any], *, test: bool) -> list[dict[str, Any]]:
        valid_entries: list[dict[str, Any]] = []
        symbol_field = "testName" if test else "symbol"
        evidence_label = "testEvidence" if test else "productionEvidence"
        for index, entry in enumerate(entries):
            prefix = f"{item_label}.{evidence_label}[{index}]"
            if not isinstance(entry, dict):
                result.errors.append(f"{prefix}: expected an object")
                continue
            surface = entry.get("surface")
            symbol = entry.get(symbol_field)
            if not isinstance(surface, str) or not surface.strip():
                result.errors.append(f"{prefix}.surface: expected a non-empty string")
            if not isinstance(symbol, str) or not symbol.strip():
                result.errors.append(f"{prefix}.{symbol_field}: expected an exact non-empty name")
            try:
                path = _resolve_path(project_root, entry.get("path"), f"{prefix}.path")
            except ValueError as exc:
                result.errors.append(str(exc))
                continue
            if not path.is_file():
                result.errors.append(f"{prefix}.path: file does not exist: {entry.get('path')}")
                continue
            if isinstance(symbol, str) and symbol.strip() and not _symbol_exists(path, symbol):
                result.errors.append(
                    f"{prefix}.{symbol_field}: {symbol!r} was not found in {entry.get('path')}"
                )
                continue
            valid_entries.append(entry)
        return valid_entries

    return validate_entries(production, test=False), validate_entries(tests, test=True)


def _load_receipt(
    project_root: Path, raw: Any, label: str, result: ValidationResult
) -> dict[str, Any] | None:
    if isinstance(raw, str):
        path_value = raw
    elif isinstance(raw, dict) and set(raw) == {"path"}:
        path_value = raw["path"]
    elif isinstance(raw, dict):
        return raw
    else:
        result.errors.append(f"{label}: expected a receipt path or object")
        return None
    try:
        path = _resolve_path(project_root, path_value, f"{label}.path")
    except ValueError as exc:
        result.errors.append(str(exc))
        return None
    if not path.is_file():
        result.errors.append(f"{label}.path: receipt does not exist: {path_value}")
        return None
    try:
        return _read_json(path)
    except RuntimeError as exc:
        result.errors.append(f"{label}: {exc}")
        return None


def _validate_receipts(
    project_root: Path,
    item: dict[str, Any],
    item_id: str,
    item_kind: str,
    current_workspace: dict[str, Any],
    result: ValidationResult,
) -> list[dict[str, Any]]:
    raw_receipts = item.get("verificationReceipts")
    label = f"{item_kind}.{item_id}.verificationReceipts"
    if not isinstance(raw_receipts, list):
        result.errors.append(f"{label}: expected an array")
        return []
    receipts: list[dict[str, Any]] = []
    owner_field = "acceptanceScenarioIds" if item_kind == "acceptanceScenarios" else "qualityGateIds"
    for index, raw in enumerate(raw_receipts):
        receipt_label = f"{label}[{index}]"
        receipt = _load_receipt(project_root, raw, receipt_label, result)
        if receipt is None:
            continue
        for field_name in (
            "schemaVersion",
            "command",
            "exitCode",
            "completedAt",
            "workspaceFingerprint",
            "acceptanceScenarioIds",
            "qualityGateIds",
        ):
            if field_name not in receipt:
                result.errors.append(f"{receipt_label}.{field_name}: required field is missing")
        if receipt.get("schemaVersion") != "1.0":
            result.errors.append(f"{receipt_label}.schemaVersion: expected '1.0'")
        if not isinstance(receipt.get("command"), str) or not receipt.get("command", "").strip():
            result.errors.append(f"{receipt_label}.command: expected a non-empty string")
        if not isinstance(receipt.get("exitCode"), int) or isinstance(receipt.get("exitCode"), bool):
            result.errors.append(f"{receipt_label}.exitCode: expected an integer")
        if not _valid_timestamp(receipt.get("completedAt")):
            result.errors.append(f"{receipt_label}.completedAt: expected an RFC3339 timestamp")
        for id_field in ("acceptanceScenarioIds", "qualityGateIds"):
            ids = receipt.get(id_field)
            if not isinstance(ids, list) or any(not isinstance(value, str) for value in ids):
                result.errors.append(f"{receipt_label}.{id_field}: expected an array of IDs")
        owner_ids = receipt.get(owner_field)
        if isinstance(owner_ids, list) and item_id not in owner_ids:
            result.errors.append(f"{receipt_label}.{owner_field}: does not include owner {item_id}")
        if item.get("status") == "verified" and not _fingerprints_equal(
            receipt.get("workspaceFingerprint"), current_workspace
        ):
            result.errors.append(f"{receipt_label}.workspaceFingerprint: receipt is stale")
        elif not _fingerprints_equal(receipt.get("workspaceFingerprint"), current_workspace):
            result.warnings.append(f"{receipt_label}.workspaceFingerprint: historical receipt is stale")
        receipts.append(receipt)
    return receipts


def _validate_status_metadata(item: dict[str, Any], label: str, result: ValidationResult) -> None:
    status = item.get("status")
    if status not in STATUSES:
        result.errors.append(f"{label}.status: unsupported value {status!r}")
        return
    blocker = item.get("blocker")
    waiver = item.get("waiver")
    if status == "blocked-external":
        if not isinstance(blocker, dict) or not isinstance(blocker.get("reason"), str) or not blocker["reason"].strip():
            result.errors.append(f"{label}.blocker.reason: required for blocked-external")
    elif blocker is not None:
        result.errors.append(f"{label}.blocker: only blocked-external entries may carry a blocker")
    if status == "waived":
        if not isinstance(waiver, dict):
            result.errors.append(f"{label}.waiver: required for waived")
        else:
            for field_name in ("reason", "userDecisionRef"):
                if not isinstance(waiver.get(field_name), str) or not waiver[field_name].strip():
                    result.errors.append(f"{label}.waiver.{field_name}: required for waived")
    elif waiver is not None:
        result.errors.append(f"{label}.waiver: only waived entries may carry a waiver")


def _validate_item_evidence(
    project_root: Path,
    item: dict[str, Any],
    item_id: str,
    item_kind: str,
    current_workspace: dict[str, Any],
    result: ValidationResult,
) -> None:
    label = f"{item_kind}.{item_id}"
    _validate_status_metadata(item, label, result)
    production, tests = _validate_evidence(project_root, item, label, result)
    receipts = _validate_receipts(
        project_root, item, item_id, item_kind, current_workspace, result
    )
    if item.get("status") != "verified":
        return
    if not production:
        result.errors.append(f"{label}: verified entry requires production evidence")
    if not tests:
        result.errors.append(f"{label}: verified entry requires test evidence")
    successful = [receipt for receipt in receipts if receipt.get("exitCode") == 0]
    if not successful:
        result.errors.append(f"{label}: verified entry requires a current zero-exit verification receipt")
    if item_kind == "acceptanceScenarios":
        required_surfaces = item.get("requiredTestSurfaces")
        if not isinstance(required_surfaces, list) or any(
            not isinstance(surface, str) or not surface for surface in required_surfaces
        ):
            result.errors.append(f"{label}.requiredTestSurfaces: expected an array of surface names")
        else:
            actual_surfaces = {entry.get("surface") for entry in tests}
            for surface in required_surfaces:
                if surface not in actual_surfaces:
                    result.errors.append(f"{label}: missing required test surface {surface!r}")


def _validate_audit(
    project_root: Path,
    ledger: dict[str, Any],
    app_spec: dict[str, Any],
    current_app_spec: dict[str, Any],
    current_workspace: dict[str, Any],
    expected_implementation_complete: bool,
    expected_release_ready: bool,
    result: ValidationResult,
) -> None:
    audit_ref = ledger.get("closureAudit")
    if not isinstance(audit_ref, dict):
        result.errors.append("closureAudit: expected an object with path")
        return
    try:
        audit_path = _resolve_path(project_root, audit_ref.get("path"), "closureAudit.path")
    except ValueError as exc:
        result.errors.append(str(exc))
        return
    if not audit_path.is_file():
        result.errors.append(f"closure-audit.missing: {audit_ref.get('path')}")
        return
    try:
        audit = _read_json(audit_path)
    except RuntimeError as exc:
        result.errors.append(f"closureAudit: {exc}")
        return
    audit_validator = _load_audit_validator()
    if audit_validator is None:
        result.errors.append(
            "closureAudit.validator.missing: vibe-acceptance-auditor validator is required"
        )
    else:
        audit_for_contract = audit
        if "completedAt" not in audit and "auditedAt" in audit:
            audit_for_contract = dict(audit)
            audit_for_contract["completedAt"] = audit["auditedAt"]
        for error in audit_validator.validate(
            audit_for_contract, current_app_spec, current_workspace, project_root
        ):
            result.errors.append(f"closureAudit.contract: {error}")

    if audit.get("schemaVersion") != "1.0":
        result.errors.append("closureAudit.schemaVersion: expected '1.0'")
    verdict = audit.get("verdict")
    if verdict not in {"PASS", "GAPS", "BLOCKED"}:
        result.errors.append("closureAudit.verdict: expected PASS, GAPS, or BLOCKED")
    audit_timestamp = audit.get("completedAt", audit.get("auditedAt"))
    if not _valid_timestamp(audit_timestamp):
        result.errors.append("closureAudit.completedAt: expected an RFC3339 timestamp")
    if not isinstance(audit.get("checks"), list):
        result.errors.append("closureAudit.checks: expected an array")
    if not isinstance(audit.get("findings"), list):
        result.errors.append("closureAudit.findings: expected an array")

    inventory = audit.get("shadowInventory")
    if isinstance(inventory, dict):
        expected_requirements = {
            item.get("id")
            for item in app_spec.get("requirements", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        expected_scenarios = {
            item.get("id")
            for item in app_spec.get("acceptanceScenarios", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        expected_gates = {
            item.get("id")
            for item in app_spec.get("qualityGates", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        expected_operations: set[str] = set()
        for entity in app_spec.get("managedEntities", []):
            if not isinstance(entity, dict):
                continue
            entity_id = entity.get("entity", entity.get("id"))
            operations = entity.get("operations")
            if not isinstance(entity_id, str) or not isinstance(operations, dict):
                continue
            for operation, decision in operations.items():
                if isinstance(decision, dict) and decision.get("status") == "required":
                    expected_operations.add(f"{entity_id}:{operation}")
        expected_inventory = {
            "requirementIds": expected_requirements,
            "acceptanceScenarioIds": expected_scenarios,
            "managedOperationIds": expected_operations,
            "qualityGateIds": expected_gates,
        }
        for field_name, expected_ids in expected_inventory.items():
            values = inventory.get(field_name)
            if isinstance(values, list) and set(values) != expected_ids:
                result.errors.append(
                    f"closureAudit.shadowInventory.{field_name}: does not match AppSpec"
                )
    completion = audit.get("completion")
    if isinstance(completion, dict):
        if completion.get("implementationComplete") is not expected_implementation_complete:
            result.errors.append(
                "closureAudit.completion.implementationComplete: conflicts with ledger obligations"
            )
        if completion.get("releaseReady") is not expected_release_ready:
            result.errors.append(
                "closureAudit.completion.releaseReady: conflicts with ledger obligations"
            )
    app_current = _fingerprints_equal(audit.get("appSpecFingerprint"), current_app_spec)
    workspace_current = _fingerprints_equal(audit.get("workspaceFingerprint"), current_workspace)
    if not app_current:
        result.errors.append("closure-audit.stale-app-spec: fingerprint does not match current AppSpec")
    if not workspace_current:
        result.errors.append("closure-audit.stale-workspace: fingerprint does not match current workspace")
    if verdict != "PASS":
        result.errors.append(f"closure-audit.verdict: completion requires PASS, found {verdict!r}")
    result.audit_current_and_passed = verdict == "PASS" and app_current and workspace_current


def _resolved_gate(gate: dict[str, Any]) -> bool:
    applicability = gate.get("applicability")
    if applicability == "not-applicable":
        return isinstance(gate.get("applicabilityReason"), str) and bool(
            gate["applicabilityReason"].strip()
        )
    return applicability == "applicable" and gate.get("status") in {"verified", "waived"}


def validate_ledger(project_root: Path, ledger_path: Path) -> ValidationResult:
    result = ValidationResult()
    project_root = project_root.resolve()
    fingerprint = _load_fingerprint_module()
    ledger = _read_json(ledger_path)
    if ledger.get("schemaVersion") != LEDGER_VERSION:
        result.errors.append(f"schemaVersion: expected {LEDGER_VERSION!r}")

    app_spec_ref = ledger.get("appSpec")
    if not isinstance(app_spec_ref, dict):
        result.errors.append("appSpec: expected an object")
        return result
    try:
        app_spec_root = _resolve_app_spec_path(project_root, app_spec_ref.get("root"))
        app_spec = _read_json(app_spec_root / "app-spec.json")
        current_app_spec = fingerprint.compute_app_spec_fingerprint(app_spec_root)
        current_workspace = fingerprint.compute_workspace_fingerprint(project_root)
    except (RuntimeError, ValueError, OSError) as exc:
        result.errors.append(str(exc))
        return result

    if app_spec.get("schemaVersion") != "1.4":
        result.errors.append("appSpec: full delivery ledger requires AppSpec 1.4")
    if not _fingerprints_equal(app_spec_ref.get("fingerprint"), current_app_spec):
        result.errors.append("app-spec.fingerprint.stale: ledger does not match normative AppSpec files")
    if not _fingerprints_equal(ledger.get("workspaceFingerprint"), current_workspace):
        result.errors.append("workspace.fingerprint.stale: ledger does not match the current workspace")

    spec_scenarios = _id_map(app_spec.get("acceptanceScenarios"), "appSpec.acceptanceScenarios", result)
    ledger_scenarios = _id_map(ledger.get("acceptanceScenarios"), "acceptanceScenarios", result)
    spec_gates = _id_map(app_spec.get("qualityGates"), "appSpec.qualityGates", result)
    ledger_gates = _id_map(ledger.get("qualityGates"), "qualityGates", result)
    if set(spec_scenarios) != set(ledger_scenarios):
        missing = sorted(set(spec_scenarios) - set(ledger_scenarios))
        extra = sorted(set(ledger_scenarios) - set(spec_scenarios))
        result.errors.append(f"acceptanceScenarios inventory mismatch; missing={missing}, extra={extra}")
    if set(spec_gates) != set(ledger_gates):
        missing = sorted(set(spec_gates) - set(ledger_gates))
        extra = sorted(set(ledger_gates) - set(spec_gates))
        result.errors.append(f"qualityGates inventory mismatch; missing={missing}, extra={extra}")

    for item_id, item in ledger_scenarios.items():
        spec_item = spec_scenarios.get(item_id)
        if spec_item is not None:
            expected = {
                "requirementId": spec_item.get("requirementId"),
                "flowId": spec_item.get("flowId"),
                "screenIds": spec_item.get("screenIds", []),
                "requiredTestSurfaces": spec_item.get("verificationSurfaces", []),
            }
            for field_name, value in expected.items():
                if item.get(field_name) != value:
                    result.errors.append(
                        f"acceptanceScenarios.{item_id}.{field_name}: does not match AppSpec"
                    )
        _validate_item_evidence(
            project_root, item, item_id, "acceptanceScenarios", current_workspace, result
        )

    for item_id, item in ledger_gates.items():
        spec_item = spec_gates.get(item_id)
        if spec_item is not None:
            expected = {
                "category": spec_item.get("category"),
                "platform": spec_item.get("platform"),
                "requirement": spec_item.get("requirement"),
                "verificationMethod": spec_item.get("verificationMethod"),
                "contractSource": spec_item.get("contractSource"),
            }
            for field_name, value in expected.items():
                if item.get(field_name) != value:
                    result.errors.append(f"qualityGates.{item_id}.{field_name}: does not match AppSpec")
        applicability = item.get("applicability")
        if applicability not in APPLICABILITY:
            result.errors.append(f"qualityGates.{item_id}.applicability: unsupported value {applicability!r}")
        if item.get("requirement") == "required" and applicability != "applicable":
            result.errors.append(f"qualityGates.{item_id}: required gate must be applicable")
        if applicability == "needs-review":
            result.errors.append(f"qualityGates.{item_id}: conditional applicability still needs review")
        if applicability == "not-applicable" and (
            not isinstance(item.get("applicabilityReason"), str)
            or not item["applicabilityReason"].strip()
        ):
            result.errors.append(f"qualityGates.{item_id}.applicabilityReason: required")
        if item.get("readinessScope") not in {"implementation", "release"}:
            result.errors.append(f"qualityGates.{item_id}.readinessScope: expected implementation or release")
        _validate_item_evidence(project_root, item, item_id, "qualityGates", current_workspace, result)

    required_scenarios_complete = all(
        not bool(item.get("required", True)) or item.get("status") in {"verified", "waived"}
        for item in ledger_scenarios.values()
    )
    implementation_gates_complete = all(
        _resolved_gate(item)
        for item in ledger_gates.values()
        if item.get("readinessScope") == "implementation"
    )
    all_gates_complete = all(_resolved_gate(item) for item in ledger_gates.values())
    no_external_blockers = all(
        item.get("status") != "blocked-external"
        for item in [*ledger_scenarios.values(), *ledger_gates.values()]
    )
    ledger_implementation_complete = (
        required_scenarios_complete and implementation_gates_complete
    )
    ledger_release_ready = (
        ledger_implementation_complete and all_gates_complete and no_external_blockers
    )
    _validate_audit(
        project_root,
        ledger,
        app_spec,
        current_app_spec,
        current_workspace,
        ledger_implementation_complete,
        ledger_release_ready,
        result,
    )

    fingerprints_current = (
        _fingerprints_equal(app_spec_ref.get("fingerprint"), current_app_spec)
        and _fingerprints_equal(ledger.get("workspaceFingerprint"), current_workspace)
    )
    result.implementation_complete = (
        required_scenarios_complete
        and implementation_gates_complete
        and result.audit_current_and_passed
        and fingerprints_current
        and not result.errors
    )
    result.release_ready = (
        result.implementation_complete and all_gates_complete and no_external_blockers
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path, help="Ledger path")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable result")
    parser.add_argument(
        "--require",
        choices=("implementation-complete", "release-ready"),
        help="Fail unless the selected verdict is true",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = args.project_root.resolve()
    ledger_path = (args.ledger or project_root / ".vibe" / "delivery-ledger.json").resolve()
    try:
        result = validate_ledger(project_root, ledger_path)
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for warning in result.warnings:
            print(f"WARNING: {warning}")
        for error in result.errors:
            print(f"ERROR: {error}")
        print(f"implementation-complete: {'YES' if result.implementation_complete else 'NO'}")
        print(f"release-ready: {'YES' if result.release_ready else 'NO'}")
    required_verdict = (
        result.implementation_complete
        if args.require == "implementation-complete"
        else result.release_ready
        if args.require == "release-ready"
        else True
    )
    return 0 if result.valid and required_verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
