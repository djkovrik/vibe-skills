#!/usr/bin/env python3
"""Compute deterministic AppSpec and Git workspace fingerprints.

The command-line contract intentionally emits the workspace fingerprint object
itself so build wrappers can embed the output directly in verification receipts:

    python compute-workspace-fingerprint.py <project-root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ALGORITHM = "sha256"
DELIVERY_ARTIFACT_PATTERNS = (
    ".vibe/delivery-ledger.json",
    ".vibe/closure-audit.json",
    ".vibe/receipts",
    "docs/requirement-traceability.generated.md",
    "docs/closure-audit.generated.md",
)


class FingerprintError(RuntimeError):
    """Raised when a requested fingerprint cannot be computed safely."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def _run_git(root: Path, arguments: list[str], *, allow_failure: bool = False) -> bytes:
    process = subprocess.run(
        ["git", "-C", os.fspath(root), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0 and not allow_failure:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise FingerprintError(detail or f"git {' '.join(arguments)} failed")
    return process.stdout if process.returncode == 0 else b""


def _is_delivery_artifact(path: str) -> bool:
    normalized = PurePosixPath(path.replace("\\", "/")).as_posix()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return any(
        normalized == pattern or normalized.startswith(pattern.rstrip("/") + "/")
        for pattern in DELIVERY_ARTIFACT_PATTERNS
    )


def _assert_git_worktree(root: Path) -> None:
    result = _run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if result.strip() != b"true":
        raise FingerprintError(f"not a Git worktree: {root}")


def compute_workspace_fingerprint(project_root: str | Path) -> dict[str, Any]:
    """Return a deterministic fingerprint of implementation-relevant Git state."""

    root = Path(project_root).resolve()
    if not root.is_dir():
        raise FingerprintError(f"project root does not exist: {root}")
    _assert_git_worktree(root)

    raw_head = _run_git(root, ["rev-parse", "--verify", "HEAD"], allow_failure=True)
    git_head = raw_head.decode("ascii", errors="strict").strip() or None

    pathspecs = ["."] + [
        f":(exclude){pattern}/**" if pattern.endswith("receipts") else f":(exclude){pattern}"
        for pattern in DELIVERY_ARTIFACT_PATTERNS
    ]
    if git_head is None:
        diff_arguments = ["diff", "--cached", "--relative", "--binary", "--no-ext-diff"]
    else:
        diff_arguments = [
            "diff",
            "--relative",
            "--binary",
            "--no-ext-diff",
            "HEAD",
        ]
    binary_diff = _run_git(root, [*diff_arguments, "--", *pathspecs])

    raw_untracked = _run_git(
        root, ["ls-files", "--others", "--exclude-standard", "-z", "--", "."]
    )
    untracked_paths = sorted(
        {
            item.decode("utf-8", errors="surrogateescape").replace("\\", "/")
            for item in raw_untracked.split(b"\0")
            if item
        }
    )
    untracked_files: list[dict[str, str]] = []
    for relative_path in untracked_paths:
        if _is_delivery_artifact(relative_path):
            continue
        candidate = (root / Path(relative_path)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise FingerprintError(
                f"Git returned an untracked path outside the project: {relative_path}"
            ) from exc
        if candidate.is_file():
            untracked_files.append(
                {"path": PurePosixPath(relative_path).as_posix(), "sha256": _sha256_bytes(candidate.read_bytes())}
            )

    payload: dict[str, Any] = {
        "algorithm": ALGORITHM,
        "gitHead": git_head,
        "binaryDiffSha256": _sha256_bytes(binary_diff),
        "untrackedFiles": untracked_files,
    }
    payload["digest"] = _canonical_digest(payload)
    return payload


def compute_app_spec_fingerprint(app_spec_root: str | Path) -> dict[str, Any]:
    """Fingerprint every normative JSON and Markdown file below an AppSpec root."""

    root = Path(app_spec_root).resolve()
    if not root.is_dir():
        raise FingerprintError(f"AppSpec root does not exist: {root}")
    files: list[dict[str, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold()):
        if path.is_file() and path.suffix.casefold() in {".json", ".md"}:
            files.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "sha256": _sha256_bytes(path.read_bytes()),
                }
            )
    if not files:
        raise FingerprintError(f"AppSpec has no normative JSON/Markdown files: {root}")
    payload: dict[str, Any] = {"algorithm": ALGORITHM, "files": files}
    payload["digest"] = _canonical_digest(payload)
    return payload


def _write_json(value: dict[str, Any], destination: Path | None) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if destination is None:
        sys.stdout.write(rendered)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path, help="Git project root to fingerprint")
    parser.add_argument("--output", type=Path, help="Write JSON to this file instead of stdout")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        fingerprint = compute_workspace_fingerprint(args.project_root)
        _write_json(fingerprint, args.output)
    except (FingerprintError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
