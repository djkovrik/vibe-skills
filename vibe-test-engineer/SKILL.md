---
name: vibe-test-engineer
description: Design and implement the non-visual Kotlin Multiplatform test pyramid, including pure domain and manager tests, localization resource/key completeness, MVIKotlin Store behavior, Decompose component navigation/lifecycle/resume tests, persistence/network/sync tests, deterministic fakes and fixtures, coroutine virtual time, failure-cause assertions, and coverage quality gates. Use for unit, component, integration, localization contract, fixture, coroutine, or coverage work; exclude screenshot goldens.
---

# Vibe Test Engineer

## When to use

Own non-visual behavioral confidence. Use Decompose component tests through public contracts as the primary/default way to cover application behavior. Do not update screenshot goldens.

## Inputs

Read acceptance IDs, public contracts, owner-specific decision records, current test source sets, and CI. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md). Use [test-pyramid-and-doubles.md](references/test-pyramid-and-doubles.md), [mvi-store-tests.md](references/mvi-store-tests.md), [decompose-component-test-harness.md](references/decompose-component-test-harness.md), [persistence-network-sync-tests.md](references/persistence-network-sync-tests.md), and [coverage-and-ci.md](references/coverage-and-ci.md). Consult local examples through the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Map application acceptance scenarios to Decompose component tests by default, then move pure algorithms, infrastructure contracts, and native-only behavior to a lower or more specialized layer when that layer is more faithful.
2. Build deterministic fakes/fixtures and injected dispatchers/clock.
3. Cover pure rules and Managers, then Store/component behavior through public contracts and the Store-State-to-component-Model mapping.
4. Reproduce lifecycle and virtual-time transitions explicitly.
5. Cover persistence/network/sync contract and failure paths.
6. For app-bundled localized text, verify that English is the complete default/base resource set, compare key sets across every additional `app.locales` resource set, exercise ID/key mappings, system-locale changes and unsupported-locale-to-English fallback, assert the absence of a language picker/persisted locale/app override, and scan production source/seed data for hardcoded user-visible copy.
7. Keep the main component-test suite in the `root` component module when root is a separate module and can assemble the production component graph and fakes without reversing dependencies. Otherwise document the nearest natural aggregation module.
8. Run focused tests, then aggregate coverage/CI gates.

## Decision rules

- Prefer real `DefaultStoreFactory`, `DefaultComponentContext`, controlled lifecycle, and test dispatchers for component behavior.
- Treat Decompose component tests as the main application-level coverage, not as optional integration polish. Add narrower Store/domain/data tests where component tests would be indirect, slow, or unable to isolate the contract.
- Prefer the separate `root` component module for centralized component tests because it owns application assembly and cross-component flows; do not force this location when it creates invalid dependency direction or the root does not live in its own module.
- Disable MVIKotlin main-thread assertions only in test setup and restore them in teardown.
- Assert component outputs/models/navigation, not Store internals from component tests.
- For every production component `Value<Model>`, verify that callbacks drive Store transitions and mapped models; flag direct repository access or production `MutableValue` mutation as an architecture violation.
- Cover Manager Kotlin `Result` success, failure, nullable success, cause preservation, and cancellation; cover Executor `unwrap` branches without custom generic result wrappers.
- Preserve and assert failure causes.
- Use real SQLDelight schema/test driver, Ktor MockEngine, and sanitized JSON fixtures.
- Assert that persistence/Store/component fixtures keep stable IDs or localization keys rather than resolved translations; use production resources when the displayed copy itself matters.
- Treat coverage as a gap signal, not a substitute for assertions.

## Validation

Verify that acceptance coverage is led by public-contract Decompose component tests and that a separate `root` component module hosts the centralized suite when structurally valid. Also verify deterministic repeat runs, explicit create/resume/pause/destroy, virtual delays/cooldowns, active child/back dispatcher, success/failure/cancellation, English default/fallback behavior, locale key-set completeness, stable key mappings, hardcoded user-visible string checks, migration/schema/auth/conflict cases, teardown cleanup, and coverage gate exit codes.

## Escalation/hand-off

Contract ambiguity -> owning specialist/Developer. Visual diffs -> Visual Testing. Product UI expectations -> Product Designer. Platform-only behavior -> Platform.

## Reusable learning

Propose durable test-harness patterns for [learned-patterns.md](references/learned-patterns.md); never promote a one-off fixture.
