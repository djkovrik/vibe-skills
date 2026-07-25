---
name: vibe-persistence-engineer
description: Design and implement Kotlin Multiplatform persistence through SQLDelight and Multiplatform Settings, including domain contracts, schemas, queries, migrations, adapters, Android/iOS/test drivers, transactions, reactive query flows, snapshot export/replace, typed settings, defaults, codecs, legacy fallback, change tracking, and persistence tests. Use for tables, local cache, migrations, settings, preferences, or transaction boundaries.
---

# Vibe Persistence Engineer

## When to use

Own local durable data and settings. Route remote API transport to Network and cross-device conflict policy to Sync.

## Inputs

Read AppSpec data/privacy/offline rules and current schema/settings code. Use [sqldelight-schema-queries.md](references/sqldelight-schema-queries.md), [drivers-adapters-transactions.md](references/drivers-adapters-transactions.md), [reactive-and-snapshot-persistence.md](references/reactive-and-snapshot-persistence.md), [multiplatform-settings.md](references/multiplatform-settings.md), and [persistence-testing.md](references/persistence-testing.md). Consult adaptations only through the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Choose SQLDelight, Settings, or both.
2. Define domain persistence contracts before implementations.
3. Add schema/queries/migrations or typed setting keys/defaults/codecs.
4. Implement mappers, adapters, drivers, dispatchers, and transactions.
5. Separate local user-change tracking from remote-apply metadata.
6. Add migration, driver, reactive, transaction, legacy, and snapshot tests.

## Decision rules

```text
Related tabular data/queries/migrations/reactive lists -> SQLDelight.
Small user options/metadata/flags -> Settings.
Atomic cross-entity replacement -> database transaction.
Structured setting -> explicit codec plus fallback test.
```

Do not expose generated entities. Use stable timestamp/enum/collection encodings. Never replace a migration with destructive reset without explicit approval.

## Validation

Run real-schema test drivers, all migrations from supported versions, adapter round trips, transaction rollback, reactive emissions on injected dispatchers, default/legacy settings, snapshot replacement, and Android/iOS compilation.

## Escalation/hand-off

Domain owns data meaning; Sync owns conflict/remote-apply coordination; Platform owns native driver factories; Network owns remote DTO transport.

## Reusable learning

Propose durable persistence conventions for [learned-patterns.md](references/learned-patterns.md); never write them without approval.

