# SQLDelight schema and queries

- Derive tables, keys, constraints, indexes, and query shapes from domain/data contracts.
- Keep generated row types behind mappers.
- Name queries by use case and make ordering explicit.
- Encode nullability and referential actions deliberately.
- Write forward migrations for every supported deployed schema.
- Never use destructive reset without explicit product/data approval.

Primary sources:

- https://sqldelight.github.io/sqldelight/
- https://kotlinlang.org/docs/multiplatform/multiplatform-ktor-sqldelight.html

Check the current SQLDelight docs for the target version before implementing migrations, adapters, or flows.

