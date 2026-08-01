---
name: vibe-persistence-engineer
description: Design and implement Kotlin Multiplatform persistence through SQLDelight and Multiplatform Settings, including domain contracts, localized local catalogs stored by stable resource key, schemas, queries, migrations, adapters, Android/iOS/test drivers, transactions, reactive query flows, snapshot export/replace, typed settings, defaults, codecs, legacy fallback, change tracking, and persistence tests. Use for tables, local catalog/database content, local cache, migrations, settings, preferences, or transaction boundaries.
---

# Vibe Persistence Engineer

## When to use

Own local durable data and settings. Route remote API transport to Network and cross-device conflict policy to Sync.

## Inputs

Read AppSpec data/privacy/offline/localization rules and current schema/settings code. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md) to app-bundled translatable data. Use [sqldelight-schema-queries.md](references/sqldelight-schema-queries.md), [drivers-adapters-transactions.md](references/drivers-adapters-transactions.md), [reactive-and-snapshot-persistence.md](references/reactive-and-snapshot-persistence.md), [multiplatform-settings.md](references/multiplatform-settings.md), and [persistence-testing.md](references/persistence-testing.md). Consult adaptations only through the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Choose SQLDelight, Settings, or both.
2. Define domain persistence contracts before implementations. Use plain values/flows or standard Kotlin `Result<T>` for an intentional repository failure boundary; never add an app-specific generic Success/Failure wrapper.
3. Add schema/queries/migrations or typed setting keys/defaults/codecs.
4. For bundled localized datasets, persist only stable item IDs/resource keys and keep every translation in Compose `strings.xml` resources.
5. Implement mappers, adapters, drivers, dispatchers, and transactions.
6. Separate local user-change tracking from remote-apply metadata.
7. Add migration, driver, reactive, transaction, legacy, localization-key round-trip, and snapshot tests.

## Decision rules

```text
Related tabular data/queries/migrations/reactive lists -> SQLDelight.
Small user options/metadata/flags -> Settings.
Atomic cross-entity replacement -> database transaction.
Structured setting -> explicit codec plus fallback test.
```

Do not expose generated entities. Use stable timestamp/enum/collection encodings. Never replace a migration with destructive reset without explicit approval.

Do not store resolved translations, per-locale text columns, or translation maps for app-bundled catalogs. Translation changes must not require a database/settings migration; only stable IDs or localization keys cross the persistence boundary.

Do not create a language/locale setting or migrate one forward. Locale selection is system-only and has no persistence contract.

Do not let MVIKotlin Stores or stateful Decompose components call persistence repositories directly. A feature Manager owns the data call and exposes a single Kotlin `Result<T>`; when the repository already returns `Result<T>`, the Manager flattens it with `getOrThrow()` inside its `runCatching` boundary.

## Validation

Run real-schema test drivers, all migrations from supported versions, adapter and localization-key round trips across locale changes, transaction rollback, reactive emissions on injected dispatchers, default/legacy settings, snapshot replacement, and Android/iOS compilation.

## Escalation/hand-off

Domain owns data meaning; Sync owns conflict/remote-apply coordination; Platform owns native driver factories; Network owns remote DTO transport.

## Reusable learning

Propose durable persistence conventions for [learned-patterns.md](references/learned-patterns.md); never write them without approval.
