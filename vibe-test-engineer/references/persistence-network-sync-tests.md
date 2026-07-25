# Persistence, network, and sync tests

Persistence:

- real schema/test driver, migrations, adapters, transactions, reactive queries, settings legacy/defaults.

Network:

- Ktor MockEngine, sanitized JSON fixtures, request shape, failures, auth refresh, cancellation, retry/idempotency.

Sync:

- schema mismatch, local/remote/both changed, ties, dedupe, orphan filtering, remote-apply tracking, rollback, repeated/concurrent/offline/partial failure.

Primary sources:

- https://ktor.io/docs/client-testing.html
- https://sqldelight.github.io/sqldelight/

