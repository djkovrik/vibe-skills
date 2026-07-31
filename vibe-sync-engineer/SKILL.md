---
name: vibe-sync-engineer
description: Design and implement Kotlin Multiplatform synchronization across authentication state, remote schema versions, local/remote snapshot mapping, per-domain timestamps and change tracking, deterministic conflict resolution, merge/replace, deduplication, orphan filtering, retry state, user-visible sync errors, and Firebase/Firestore-like platform adapters. Use for offline sync, snapshots, concurrent edits, remote apply, Firestore conflicts, or sync state.
---

# Vibe Sync Engineer

## When to use

Own coordination between auth, local persistence, and remote snapshot services. Do not own generic REST transport or local schema implementation.

## Inputs

Read AppSpec sync/offline/auth/privacy/localization rules, domain contracts, local snapshots, and remote schema. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md) when snapshots reference app-bundled localized data. Use [sync-contract-and-state.md](references/sync-contract-and-state.md), [snapshot-schema-and-mappers.md](references/snapshot-schema-and-mappers.md), [conflicts-merge-tracking.md](references/conflicts-merge-tracking.md), [auth-and-remote-adapters.md](references/auth-and-remote-adapters.md), and [sync-testing.md](references/sync-testing.md). Access local evidence only through the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Define identity/auth boundary and observable sync state.
2. Version the portable remote snapshot schema.
3. Map local domain snapshots to remote DTOs and back.
4. Define deterministic per-domain conflict policy.
5. Merge transactionally, dedupe stable IDs, and filter orphans.
6. Prevent remote apply from being tracked as a local edit.
7. Run post-merge side effects only after successful commit.
8. Add offline, partial, repeated, concurrent, and mismatch tests.

## Decision rules

- Reject incompatible remote schema explicitly.
- Compare independent timestamps for independent data domains.
- Preserve referential integrity during merge.
- Sync only stable item IDs/localization keys for app-bundled catalogs, never resolved translations or per-locale maps. Changing or adding a translation must not change the remote snapshot schema.
- Expose auth/sync/error/last-success state.
- Keep retries bounded and idempotent.
- Never let failed or partial merge trigger reminders or other side effects.

## Validation

Test schema compatibility, localization-key round trips where applicable, local-only/remote-only/both-changed paths, deterministic ties, dedupe, orphan filtering, rollback, remote-apply tracking, repeated sync, concurrent edits, offline/partial failure, auth changes, and post-merge effects.

## Escalation/hand-off

Persistence owns local storage/transactions; Network or Platform owns remote adapter transport; Domain owns merge semantics; Platform owns rescheduling side effects; MVIKotlin owns UI-facing orchestration.

## Reusable learning

Propose accepted sync policies for [learned-patterns.md](references/learned-patterns.md); never mutate policy from a one-off conflict.
