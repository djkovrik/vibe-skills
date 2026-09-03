#!/usr/bin/env python3
"""Dependency-free structural and semantic validator for a Vibe closure audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


VERDICTS = {"PASS", "GAPS", "BLOCKED"}
OBLIGATION_RESULTS = {"verified", "gap", "blocked-external", "waived"}
FINDING_KINDS = {"gap", "audit-blocker", "external-blocker", "waiver", "observation"}
CHECK_RESULTS = {"pass", "fail", "blocked"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_timestamp(value: Any) -> bool:
    if not _nonempty(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _load_fingerprint_module() -> Any:
    path = Path(__file__).resolve().parents[2] / "vibe-developer" / "scripts" / "compute-workspace-fingerprint.py"
    spec = importlib.util.spec_from_file_location("vibe_workspace_fingerprint", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load shared fingerprint helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _valid_file_hashes(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, dict)
        and _nonempty(item.get("path"))
        and isinstance(item.get("sha256"), str)
        and SHA256_PATTERN.fullmatch(item["sha256"]) is not None
        for item in value
    )


def _validate_fingerprint(value: Any, kind: str, errors: list[str]) -> None:
    label = f"{kind}Fingerprint"
    if not isinstance(value, dict):
        errors.append(f"{label} must be a full fingerprint object")
        return
    if value.get("algorithm") != "sha256":
        errors.append(f"{label}.algorithm must be sha256")
    if not isinstance(value.get("digest"), str) or SHA256_PATTERN.fullmatch(value["digest"]) is None:
        errors.append(f"{label}.digest must be a lowercase SHA-256")
    if kind == "appSpec":
        if not _valid_file_hashes(value.get("files")):
            errors.append(f"{label}.files must contain path/SHA-256 records")
    else:
        if value.get("gitHead") is not None and not _nonempty(value.get("gitHead")):
            errors.append(f"{label}.gitHead must be a commit string or null")
        diff_hash = value.get("binaryDiffSha256")
        if not isinstance(diff_hash, str) or SHA256_PATTERN.fullmatch(diff_hash) is None:
            errors.append(f"{label}.binaryDiffSha256 must be a lowercase SHA-256")
        if not _valid_file_hashes(value.get("untrackedFiles")):
            errors.append(f"{label}.untrackedFiles must contain path/SHA-256 records")


def validate(
    data: Any,
    expected_app_spec: dict[str, Any] | None,
    expected_workspace: dict[str, Any] | None,
    repository: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["audit root must be an object"]

    required = {
        "schemaVersion", "verdict", "completedAt", "auditorContext",
        "appSpecFingerprint", "workspaceFingerprint", "shadowInventory",
        "obligations", "checks", "findings", "completion",
    }
    for key in sorted(required - data.keys()):
        errors.append(f"missing required field: {key}")

    if data.get("schemaVersion") != "1.0":
        errors.append("schemaVersion must be 1.0")
    verdict = data.get("verdict")
    if verdict not in VERDICTS:
        errors.append("verdict must be PASS, GAPS, or BLOCKED")
    if not _valid_timestamp(data.get("completedAt")):
        errors.append("completedAt must be an ISO 8601 timestamp")

    context = data.get("auditorContext")
    fresh = isinstance(context, dict) and context.get("fresh") is True
    if verdict != "BLOCKED" and not fresh:
        errors.append(f"{verdict} requires auditorContext.fresh=true")

    app_fp = data.get("appSpecFingerprint")
    workspace_fp = data.get("workspaceFingerprint")
    _validate_fingerprint(app_fp, "appSpec", errors)
    _validate_fingerprint(workspace_fp, "workspace", errors)
    if expected_app_spec is not None and app_fp != expected_app_spec:
        errors.append("stale AppSpec fingerprint")
    if expected_workspace is not None and workspace_fp != expected_workspace:
        errors.append("stale workspace fingerprint")

    inventory = data.get("shadowInventory")
    inventory_keys = ("requirementIds", "acceptanceScenarioIds", "managedOperationIds", "qualityGateIds")
    if not isinstance(inventory, dict):
        errors.append("shadowInventory must be an object")
        inventory = {}
    for key in inventory_keys:
        values = inventory.get(key)
        if not isinstance(values, list) or any(not _nonempty(item) for item in values):
            errors.append(f"shadowInventory.{key} must be an array of non-empty IDs")
        elif len(values) != len(set(values)):
            errors.append(f"shadowInventory.{key} contains duplicate IDs")

    obligations = data.get("obligations")
    obligation_ids: set[str] = set()
    obligation_results: list[str] = []
    verified_obligations: set[str] = set()
    completion_blocking_results: list[tuple[str, str]] = []
    if not isinstance(obligations, list):
        errors.append("obligations must be an array")
        obligations = []
    for index, item in enumerate(obligations):
        prefix = f"obligations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        obligation_id = item.get("id")
        if not _nonempty(obligation_id):
            errors.append(f"{prefix}.id must be non-empty")
        elif obligation_id in obligation_ids:
            errors.append(f"duplicate obligation id: {obligation_id}")
        else:
            obligation_ids.add(obligation_id)
        result = item.get("result")
        if result not in OBLIGATION_RESULTS:
            errors.append(f"{prefix}.result is invalid")
        else:
            obligation_results.append(result)
        if item.get("kind") not in {"acceptance-scenario", "managed-operation", "quality-gate"}:
            errors.append(f"{prefix}.kind is invalid")
        scope = item.get("scope")
        if scope not in {"repository", "platform", "external", "release"}:
            errors.append(f"{prefix}.scope is invalid")
        if result == "blocked-external" and scope == "repository":
            errors.append(f"{prefix} cannot use blocked-external for repository scope")
        if item.get("kind") in {"acceptance-scenario", "managed-operation"} or scope == "repository":
            completion_blocking_results.append((str(obligation_id), str(result)))
        surfaces = item.get("verificationSurfaces")
        if not isinstance(surfaces, list) or any(not _nonempty(v) for v in surfaces):
            errors.append(f"{prefix}.verificationSurfaces must be an ID array")
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{prefix}.evidence must be an array")
            evidence = []
        if result == "verified" and not evidence:
            errors.append(f"{prefix} is verified without evidence")
        if result == "verified" and _nonempty(obligation_id):
            verified_obligations.add(obligation_id)
            if item.get("kind") in {"acceptance-scenario", "managed-operation"}:
                has_production = any(isinstance(entry, dict) and _nonempty(entry.get("symbol")) and not entry.get("testName") for entry in evidence)
                has_test = any(isinstance(entry, dict) and _nonempty(entry.get("testName")) for entry in evidence)
                if not has_production:
                    errors.append(f"{prefix} is verified without production symbol evidence")
                if not has_test:
                    errors.append(f"{prefix} is verified without exact test evidence")
        if result == "waived" and not _nonempty(item.get("decisionReference")):
            errors.append(f"{prefix} is waived without decisionReference")
        for evidence_index, entry in enumerate(evidence):
            evidence_prefix = f"{prefix}.evidence[{evidence_index}]"
            if not isinstance(entry, dict) or not _nonempty(entry.get("path")) or not _nonempty(entry.get("surface")):
                errors.append(f"{evidence_prefix} requires path and surface")
                continue
            evidence_path = Path(entry["path"])
            if evidence_path.is_absolute() or ".." in evidence_path.parts:
                errors.append(f"{evidence_prefix}.path must be repository-relative")
                continue
            if repository is not None:
                target = repository / evidence_path
                if not target.is_file():
                    errors.append(f"{evidence_prefix}.path does not exist: {entry['path']}")
                    continue
                symbol = entry.get("symbol")
                test_name = entry.get("testName")
                if _nonempty(symbol) or _nonempty(test_name):
                    try:
                        source = target.read_text(encoding="utf-8-sig")
                    except (OSError, UnicodeError) as exc:
                        errors.append(f"{evidence_prefix}.path cannot be inspected: {exc}")
                        continue
                    if _nonempty(symbol) and symbol not in source:
                        errors.append(f"{evidence_prefix}.symbol not found: {symbol}")
                    if _nonempty(test_name) and test_name not in source:
                        errors.append(f"{evidence_prefix}.testName not found: {test_name}")

    expected_obligations = set(inventory.get("acceptanceScenarioIds", []))
    expected_obligations.update(inventory.get("managedOperationIds", []))
    expected_obligations.update(inventory.get("qualityGateIds", []))
    missing_obligations = expected_obligations - obligation_ids
    extra_obligations = obligation_ids - expected_obligations
    if missing_obligations:
        errors.append("missing obligation records: " + ", ".join(sorted(missing_obligations)))
    if extra_obligations:
        errors.append("obligation records absent from shadow inventory: " + ", ".join(sorted(extra_obligations)))

    checks = data.get("checks")
    if not isinstance(checks, list):
        errors.append("checks must be an array")
        checks = []
    for index, item in enumerate(checks):
        prefix = f"checks[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        result = item.get("result")
        exit_code = item.get("exitCode")
        if not _nonempty(item.get("id")):
            errors.append(f"{prefix}.id must be non-empty")
        if not _nonempty(item.get("command")):
            errors.append(f"{prefix}.command must be non-empty")
        if not _valid_timestamp(item.get("completedAt")):
            errors.append(f"{prefix}.completedAt must be an ISO 8601 timestamp")
        if result not in CHECK_RESULTS:
            errors.append(f"{prefix}.result is invalid")
        if result == "pass" and exit_code != 0:
            errors.append(f"{prefix} passes without exitCode 0")
        if result == "fail" and (not isinstance(exit_code, int) or exit_code == 0):
            errors.append(f"{prefix} fails without a non-zero exitCode")
        if result == "blocked" and exit_code is not None:
            errors.append(f"{prefix} blocked check must use exitCode null")
        if item.get("workspaceFingerprint") != workspace_fp:
            errors.append(f"{prefix} has a different workspace fingerprint")
        _validate_fingerprint(item.get("workspaceFingerprint"), "workspace", errors)
        refs = item.get("obligationIds")
        if not isinstance(refs, list) or any(ref not in obligation_ids for ref in refs):
            errors.append(f"{prefix}.obligationIds contains an unknown obligation")

    passed_check_obligations = {
        ref
        for item in checks
        if isinstance(item, dict) and item.get("result") == "pass" and item.get("exitCode") == 0
        for ref in item.get("obligationIds", [])
    }
    for obligation_id in sorted(verified_obligations - passed_check_obligations):
        errors.append(f"verified obligation has no successful audit-time check: {obligation_id}")

    findings = data.get("findings")
    finding_kinds: list[str] = []
    if not isinstance(findings, list):
        errors.append("findings must be an array")
        findings = []
    for index, item in enumerate(findings):
        prefix = f"findings[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        kind = item.get("kind")
        if kind not in FINDING_KINDS:
            errors.append(f"{prefix}.kind is invalid")
        else:
            finding_kinds.append(kind)
        refs = item.get("obligationIds")
        if not isinstance(refs, list) or (kind == "gap" and not refs):
            errors.append(f"{prefix}.obligationIds must identify affected obligations")
        elif any(ref not in obligation_ids for ref in refs):
            errors.append(f"{prefix}.obligationIds contains an unknown obligation")
        if not _nonempty(item.get("summary")):
            errors.append(f"{prefix}.summary must be non-empty")
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{prefix}.evidence must be an array")
        else:
            for evidence_index, entry in enumerate(evidence):
                evidence_prefix = f"{prefix}.evidence[{evidence_index}]"
                if not isinstance(entry, dict) or not _nonempty(entry.get("path")) or not _nonempty(entry.get("surface")):
                    errors.append(f"{evidence_prefix} requires path and surface")
        if kind == "gap" and not _nonempty(item.get("neededProof")):
            errors.append(f"{prefix}.neededProof is required for a gap")

    completion = data.get("completion")
    if not isinstance(completion, dict):
        errors.append("completion must be an object")
        completion = {}
    implementation_complete = completion.get("implementationComplete")
    release_ready = completion.get("releaseReady")
    if not isinstance(implementation_complete, bool) or not isinstance(release_ready, bool):
        errors.append("completion values must be booleans")
    if verdict in {"GAPS", "BLOCKED"} and (implementation_complete or release_ready):
        errors.append(f"{verdict} cannot claim completion")
    if verdict == "PASS" and not implementation_complete:
        errors.append("PASS requires implementationComplete=true")
    if verdict == "PASS" and any(kind in {"gap", "audit-blocker"} for kind in finding_kinds):
        errors.append("PASS conflicts with gap or audit-blocker findings")
    if verdict == "PASS" and any(isinstance(check, dict) and check.get("result") == "fail" for check in checks):
        errors.append("PASS conflicts with failed audit checks")
    if verdict == "GAPS" and ("gap" not in finding_kinds or "gap" not in obligation_results):
        errors.append("GAPS requires at least one gap finding and gap obligation")
    if verdict == "BLOCKED" and "audit-blocker" not in finding_kinds:
        errors.append("BLOCKED requires an audit-blocker finding")
    if implementation_complete and any(value == "gap" for value in obligation_results):
        errors.append("implementationComplete conflicts with gap obligations")
    if implementation_complete and "gap" in finding_kinds:
        errors.append("implementationComplete conflicts with gap findings")
    if implementation_complete and any(result not in {"verified", "waived"} for _, result in completion_blocking_results):
        errors.append("implementationComplete requires all acceptance, managed-operation, and repository obligations verified or waived")
    if release_ready and not implementation_complete:
        errors.append("releaseReady requires implementationComplete")
    if release_ready and any(value == "blocked-external" for value in obligation_results):
        errors.append("releaseReady conflicts with blocked-external obligations")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    parser.add_argument("--app-spec-root", type=Path, required=True, help="recompute the current AppSpec fingerprint")
    parser.add_argument("--repository", type=Path, required=True, help="recompute workspace freshness and verify evidence")
    args = parser.parse_args()

    try:
        data = json.loads(args.audit.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read audit: {exc}", file=sys.stderr)
        return 2

    repository = args.repository.resolve()
    try:
        fingerprint = _load_fingerprint_module()
        expected_app_spec = fingerprint.compute_app_spec_fingerprint(args.app_spec_root.resolve())
        expected_workspace = fingerprint.compute_workspace_fingerprint(repository)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: cannot compute current fingerprints: {exc}", file=sys.stderr)
        return 2
    errors = validate(data, expected_app_spec, expected_workspace, repository)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK: {args.audit} ({data['verdict']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
