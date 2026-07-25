# Conflicts, merge, and tracking

- Define deterministic conflict policy per independent data domain.
- Compare local-change, remote-change, and common-baseline metadata.
- Resolve ties explicitly.
- Dedupe by stable identity and filter rows whose parents are absent.
- Preserve referential integrity inside one transaction.
- Suppress local-change tracking during remote apply.
- Run rescheduling/indexing/notification effects after commit only.
- Keep deletes/tombstones and retention policy explicit.

Test local-only, remote-only, both-changed, tie, repeat, rollback, dedupe, orphan, and side-effect failure paths.

