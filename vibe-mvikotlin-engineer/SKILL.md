---
name: vibe-mvikotlin-engineer
description: Decide whether a Kotlin Multiplatform feature needs MVIKotlin and design or review its Intent, Action, Msg, State, Label, StoreProvider, coroutine Executor, pure Reducer, startup initialization, Result mapping, retention, lifecycle, and debug logging. Use for observable state, async work, bootstrap subscriptions, resume-aware behavior, retained Stores, or Store-level orchestration.
---

# Vibe MVIKotlin Engineer

## When to use

Own Store state-machine orchestration. Do not create a Store for stateless callbacks or keep complex business calculations inside the Store.

## Inputs

Read the component/domain contracts and target MVIKotlin version. Use [store-decision-and-shape.md](references/store-decision-and-shape.md), [executor-reducer-result.md](references/executor-reducer-result.md), [initialization-retention-logging.md](references/initialization-retention-logging.md), and [blinkly-unwrap-pattern.md](references/blinkly-unwrap-pattern.md). Consult local paths only through the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Apply the Store decision gate.
2. Keep the Store module-internal and model raw feature/domain state.
3. Define Intent/Action/Msg/State/Label and a provider with a fresh stateful Executor.
4. Put side effects/subscriptions in Executor and state changes in a pure Reducer.
5. Map manager `Result` values with explicit success/failure/cancellation behavior.
6. Subscribe to startup labels before `init()` when required.
7. Retain the Store through InstanceKeeper and map state to the component model.
8. Enable logging only in debug wiring.

## Decision rules

```text
Stateless callback/output -> no Store; use Decompose.
Observable state, async/bootstrap/flow/resume behavior -> retained Store.
Complex calculation or multi-source business rule -> Domain manager/engine; Store orchestrates.
```

Honor MVIKotlin's main-thread contract for accept/init/dispose, dispatch, and labels. Use the Executor lifecycle scope for async work. Treat labels as uncached one-off events. Do not persist transient loading as restored truth.

## Validation

Test reducer transitions, intents/actions, bootstrap subscriptions, result branches, cancellation, startup labels, restoration/retention, disposal, and release wiring without logging.

## Escalation/hand-off

Hand public component mapping/lifecycle ownership to Decompose, calculations to Domain, IO implementations to the owning infrastructure skill, and tests to Test Engineer.

## Reusable learning

Propose reusable Store conventions for [learned-patterns.md](references/learned-patterns.md); do not apply them automatically.

