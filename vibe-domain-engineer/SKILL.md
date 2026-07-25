---
name: vibe-domain-engineer
description: Model Kotlin Multiplatform domain entities, value objects, invariants, pure algorithms, manager/watcher/provider contracts, sealed events and errors, time-zone and recurrence semantics, and cross-feature outputs. Use for business calculations, scheduling rules, domain vocabulary, Result-based boundaries, or extracting logic from Stores, components, UI, persistence, and platform code.
---

# Vibe Domain Engineer

## When to use

Own business meaning and pure rules. Do not orchestrate UI state machines or choose storage/network implementations.

## Inputs

Read AppSpec `domain.md`, requirements, flows, acceptance scenarios, and relevant target contracts/tests. Use [domain-modeling.md](references/domain-modeling.md), [managers-events-errors.md](references/managers-events-errors.md), and [time-and-scheduling.md](references/time-and-scheduling.md). Consult the shared [source registry](../vibe-developer/references/source-registry.md) only for adaptations.

## Workflow

1. Extract a glossary, invariants, inputs, outputs, and failure semantics.
2. Model entities/value objects and narrow external interfaces in common code.
3. Separate pure calculation from side effects and presentation state.
4. Put stable cross-source calculations behind manager/engine/provider contracts.
5. Represent recoverable boundaries with explicit `Result`/sealed outcomes while preserving causes.
6. Add table-driven and boundary tests, including multiple time zones where applicable.

## Decision rules

- Avoid Android/iOS types in `commonMain`.
- Inject clock/time-zone abstractions.
- Keep calculation deterministic and side effects outside pure functions.
- Use typed events/errors with actionable root/presentation semantics.
- Never swallow exceptions in empty `catch` or `.catch {}` blocks.
- If a Store becomes a calculation engine, move the calculation here and leave Store orchestration.

## Validation

Trace every invariant to requirements and acceptance IDs. Test valid/invalid boundaries, recurrence/DST/time-zone behavior, error causes, cancellation semantics, and cross-feature output exhaustiveness.

## Escalation/hand-off

Hand persistence contracts to Persistence, transport contracts to Network, platform scheduling to Platform, and observable orchestration to MVIKotlin. Ask Developer for materially ambiguous business choices.

## Reusable learning

Propose reusable domain rules for [learned-patterns.md](references/learned-patterns.md) with evidence and migration impact; never auto-apply them.

