---
name: vibe-mvikotlin-engineer
description: Design and review Kotlin Multiplatform MVIKotlin Stores for every Decompose component with a UI-visible model, including Intent, Action, Msg, State, Label, StoreProvider, Manager-mediated data access, Kotlin Result/unwrap handling, coroutine Executor, pure Reducer, startup initialization, retention, lifecycle, mapping, and debug logging. Use for observable component state, async work, bootstrap subscriptions, resume-aware behavior, or Store-level orchestration.
---

# Vibe MVIKotlin Engineer

## When to use

Own Store state-machine orchestration. Every production Decompose `Value<Model>` is Store-backed; do not create a Store for a component with only stateless callbacks/outputs or keep complex business calculations inside the Store.

## Inputs

Read the component/domain contracts and target MVIKotlin version. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md) when state represents app-bundled localized content. Use [store-decision-and-shape.md](references/store-decision-and-shape.md), [executor-reducer-result.md](references/executor-reducer-result.md), [initialization-retention-logging.md](references/initialization-retention-logging.md), and [blinkly-unwrap-pattern.md](references/blinkly-unwrap-pattern.md). Consult local paths only through the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Apply the Store decision gate: a UI-visible component model requires a Store; a truly stateless callback/output component does not.
2. Keep the Store module-internal in the component module's dedicated `.store` package and model raw feature/domain state.
3. Define Intent/Action/Msg/State/Label and a provider with a fresh stateful Executor.
4. Put side effects/subscriptions in Executor and state changes in a pure Reducer.
5. Put data/external calls behind a feature Manager, return standard Kotlin `Result<T>` built with `runCatching`, and map it in the Executor through the shared cancellation-aware `unwrap` helper.
6. Subscribe to startup labels before `init()` when required.
7. Retain the Store through InstanceKeeper and expose `store.asValue().map(stateToModel)`; never duplicate its state in a production `MutableValue`.
8. Enable logging only in debug wiring.

## Decision rules

```text
Stateless callback/output with no UI-visible model -> no Store; use Decompose.
Production Value<Model>, async/bootstrap/flow/resume behavior -> retained Store.
Complex calculation or multi-source business rule -> Domain manager/engine; Store orchestrates.
```

Use `Result<T>` from the Kotlin standard library. Do not introduce a generic custom `Success`/`Failure` wrapper that merely duplicates Kotlin `Result`; keep sealed outcomes only when their cases are domain data rather than exception transport. A Store must not call a repository/data source directly. Its Manager owns data calls, mapping/calculation, and the `runCatching` boundary; if a lower layer already returns `Result<T>`, consume it with `getOrThrow()` inside the Manager boundary rather than returning `Result<Result<T>>`.

Honor MVIKotlin's main-thread contract for accept/init/dispose, dispatch, and labels. Use the Executor lifecycle scope for async work. Treat labels as uncached one-off events. Do not persist transient loading as restored truth.

Inside a Decompose component module, place `*Store` and `*StoreProvider` in the feature's `.store` package, separate from the root component contract and `.integration` implementations. Keep the Store contract/provider internal unless a cross-module contract is explicitly required. Do not put Store declarations in `*Component.kt`, `*ComponentDefault.kt`, or the feature package root.

Keep Store state locale-neutral for app-bundled content: carry stable domain IDs/localization keys, not resolved strings or generated Compose resource types. Map those IDs/keys at the component/presentation boundary so locale changes do not require Store reload or persistence changes.

Do not add `selectedLocale` state, language-selection intents, or locale-override effects. The resource environment follows the operating-system locale only.

## Validation

Test reducer transitions, intents/actions, bootstrap subscriptions, Manager result branches, nullable successes, cancellation rethrow, State-to-Model mapping, startup labels, restoration/retention, disposal, dedicated `.store` package placement, internal visibility, and release wiring without logging.

## Escalation/hand-off

Hand public component mapping/lifecycle ownership to Decompose, calculations to Domain, IO implementations to the owning infrastructure skill, and tests to Test Engineer.

## Reusable learning

Propose reusable Store conventions for [learned-patterns.md](references/learned-patterns.md); do not apply them automatically.
