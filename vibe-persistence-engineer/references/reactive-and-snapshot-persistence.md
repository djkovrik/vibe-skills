# Reactive and snapshot persistence

- Convert queries to Flow using the integration supported by the target SQLDelight version.
- Execute query reads on an injected dispatcher.
- Define emission/deduplication and transaction visibility semantics.
- Export portable domain snapshots, not generated entities.
- Replace multi-table snapshots atomically.
- Keep local user-change timestamps separate from sync remote-apply suppression.
- Run post-commit effects only after successful replacement.

Primary source:

- https://sqldelight.github.io/sqldelight/latest/coroutines_extensions/

