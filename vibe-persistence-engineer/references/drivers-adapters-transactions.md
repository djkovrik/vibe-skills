# Drivers, adapters, and transactions

- Provide Android, iOS, and test driver factories with explicit lifecycle.
- Run the same generated schema and migrations in tests.
- Define stable adapters for instants, local time, enums, UUIDs, and collections.
- Keep related writes and snapshot replacement in transactions.
- Ensure rollback leaves no partial metadata or side effects.
- Inject an IO dispatcher for blocking/expensive work.

Primary source:

- https://sqldelight.github.io/sqldelight/latest/multiplatform_sqlite/

Blinkly adaptation: database module factories, adapters, transactions, and test drivers provide concrete evidence through the shared source registry.

