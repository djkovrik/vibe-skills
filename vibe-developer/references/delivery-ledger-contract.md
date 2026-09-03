# Delivery ledger and closure contract

## Durable artifacts

Create these tracked files in the target repository:

- `.vibe/delivery-ledger.json` — the only editable source of delivery state;
- `docs/requirement-traceability.generated.md` — deterministic ledger projection;
- `.vibe/closure-audit.json` and `docs/closure-audit.generated.md` — latest independent audit.

Do not edit generated Markdown by hand. Initialize the ledger before production changes and never overwrite an existing ledger:

```powershell
python <vibe-skills>\vibe-developer\scripts\init-delivery-ledger.py <app-spec-directory> --project-root <project-root>
```

Use `render-delivery-report.py` to update the projection and `--check` in final gates. Use `compute-workspace-fingerprint.py` everywhere a receipt or audit needs repository identity. Use `validate-delivery-ledger.py` for the final verdict.

## Ledger 1.0

The ledger records:

- SHA-256 fingerprints for every normative AppSpec JSON/Markdown file;
- a workspace fingerprint containing Git HEAD, binary-diff hash, and hashes of nonignored untracked files;
- one entry per acceptance scenario and quality gate;
- `not-started`, `implemented-unverified`, `verified`, `blocked-external`, or `waived` status;
- production evidence (`path`, `symbol`, `surface`) and test evidence (`path`, exact test name, `surface`);
- verification receipts with exact command, actual exit code, completion time, workspace fingerprint, and covered IDs;
- blocker or waiver metadata when applicable.

An orchestrator may update the ledger only from inspected artifacts and returned evidence packages. A waiver must reference an explicit durable user decision. Do not use `blocked-external` for missing repository work, tests, or local verification.

## Evidence and freshness

For a `verified` entry, require existing production and test evidence appropriate to its declared verification surfaces plus at least one successful receipt that names the entry ID. Paths, production symbols, exact test names, and test surfaces must resolve in the current workspace. The receipt fingerprint must equal the current workspace fingerprint.

Any normative AppSpec or workspace change invalidates affected receipts and the audit. Recompute and rerun; never merely replace stored fingerprints. Keep verification logs and receipts under ignored build output or the `.vibe` evidence area so evidence files do not invalidate their own fingerprint.

On Windows, only `$vibe-developer` invokes Gradle:

```powershell
& <vibe-skills>\vibe-developer\scripts\run-gradle.ps1 `
  -ProjectRoot <project-root> `
  -Tasks ':feature:test' `
  -LogPath <ignored-log-path> `
  -AcceptanceScenarioIds AC-001 `
  -QualityGateIds QG-001 `
  -ReceiptPath <project-root>\.vibe\receipts\AC-001.json
```

The runner serializes Gradle by canonical project path, enforces bounded lock/command timeouts, and writes a receipt only after the process actually exits. A completed failing command produces a receipt with its real nonzero exit code; a timeout or launch failure does not masquerade as a completed receipt.

## Verdicts

`implementation-complete` requires every mandatory acceptance scenario and repository gate to be `verified` or explicitly `waived`, fresh fingerprints, generated-report parity, and a fresh audit `PASS`.

`release-ready` additionally requires every applicable platform, external, and release gate to be `verified` or explicitly `waived`. It never permits `blocked-external`.

Keep every unfinished obligation as its own entry. Do not replace item-level truth with phrases such as “implemented baseline,” “mostly complete,” or a group-level “partial.”
