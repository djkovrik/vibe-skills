#!/usr/bin/env python3
"""Capture an already authorized user decision; never infer approval from elapsed time."""
import argparse
import re
from pathlib import Path
from vibe_protocol import ProtocolError, atomic_write_json, repository_path, sha256_bytes, utc_now


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--id", required=True)
    parser.add_argument("--kind", choices=("waiver", "steering", "spec-change"), required=True)
    parser.add_argument("--obligation-id", action="append", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--source", required=True, help="Repository file containing the captured user message")
    parser.add_argument("--message-id", required=True)
    parser.add_argument("--quote", required=True)
    parser.add_argument("--supersedes", action="append", default=[])
    args = parser.parse_args()
    try:
        if not re.fullmatch(r"DEC-[A-Za-z0-9-]+", args.id): raise ProtocolError("invalid decision ID")
        root = args.project_root.resolve()
        source = repository_path(root, args.source)
        if args.quote not in source.read_text(encoding="utf-8-sig") or not all(v.strip() for v in (args.quote, args.message_id, args.rationale)):
            raise ProtocolError("non-empty exact user quote, message ID, and rationale required")
        target = root / "docs" / "decisions" / f"{args.id}.json"
        for previous in args.supersedes:
            if not re.fullmatch(r"DEC-[A-Za-z0-9-]+", previous) or not (target.parent / f"{previous}.json").is_file(): raise ProtocolError("superseded decision must exist")
        decision = {"schemaVersion":"2.0", "decisionId":args.id, "kind":args.kind, "status":"accepted",
            "obligationIds":sorted(set(args.obligation_id)), "rationale":args.rationale, "recordedAt":utc_now(),
            "supersedes":args.supersedes, "userApproval":{"actor":"user", "path":args.source,
            "messageId":args.message_id, "quote":args.quote, "sha256":sha256_bytes(source.read_bytes())}}
        atomic_write_json(target, decision, refuse_existing=True)
        print(target.relative_to(root).as_posix())
        return 0
    except (ProtocolError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}"); return 1


if __name__ == "__main__": raise SystemExit(main())
