---
name: vibe-test-engineer
description: Design and implement the non-visual Kotlin Multiplatform test pyramid, including pure domain and manager tests, localization resource/key completeness, MVIKotlin Store behavior, Decompose component navigation/lifecycle/resume tests, persistence/network/sync tests, deterministic fakes and fixtures, coroutine virtual time, failure-cause assertions, and coverage quality gates. Use for unit, component, integration, localization contract, fixture, coroutine, or coverage work; exclude screenshot goldens.
---

# Vibe Test Engineer

## When to use

Own non-visual behavioral confidence. Do not update screenshot goldens.

## Inputs

Read acceptance IDs, public contracts, owner-specific decision records, current test source sets, and CI. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md). Use [test-pyramid-and-doubles.md](references/test-pyramid-and-doubles.md), [mvi-store-tests.md](references/mvi-store-tests.md), [decompose-component-test-harness.md](references/decompose-component-test-harness.md), [persistence-network-sync-tests.md](references/persistence-network-sync-tests.md), and [coverage-and-ci.md](references/coverage-and-ci.md). Consult local examples through the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Map acceptance scenarios and risks to the smallest test layer.
2. Build deterministic fakes/fixtures and injected dispatchers/clock.
3. Cover pure rules, then Store/component behavior through public contracts.
4. Reproduce lifecycle and virtual-time transitions explicitly.
5. Cover persistence/network/sync contract and failure paths.
6. For app-bundled localized text, verify that English is the complete default/base resource set, compare key sets across every additional `app.locales` resource set, exercise ID/key mappings, system-locale changes and unsupported-locale-to-English fallback, assert the absence of a language picker/persisted locale/app override, and scan production source/seed data for hardcoded user-visible copy.
7. Run focused tests, then aggregate coverage/CI gates.

## Decision rules

- Prefer real `DefaultStoreFactory`, `DefaultComponentContext`, controlled lifecycle, and test dispatchers for component behavior.
- Disable MVIKotlin main-thread assertions only in test setup and restore them in teardown.
- Assert component outputs/models/navigation, not Store internals from component tests.
- Preserve and assert failure causes.
- Use real SQLDelight schema/test driver, Ktor MockEngine, and sanitized JSON fixtures.
- Assert that persistence/Store/component fixtures keep stable IDs or localization keys rather than resolved translations; use production resources when the displayed copy itself matters.
- Treat coverage as a gap signal, not a substitute for assertions.

## Validation

Verify deterministic repeat runs, explicit create/resume/pause/destroy, virtual delays/cooldowns, active child/back dispatcher, success/failure/cancellation, English default/fallback behavior, locale key-set completeness, stable key mappings, hardcoded user-visible string checks, migration/schema/auth/conflict cases, teardown cleanup, and coverage gate exit codes.

## Escalation/hand-off

Contract ambiguity -> owning specialist/Developer. Visual diffs -> Visual Testing. Product UI expectations -> Product Designer. Platform-only behavior -> Platform.

## Reusable learning

Propose durable test-harness patterns for [learned-patterns.md](references/learned-patterns.md); never promote a one-off fixture.
