---
name: vibe-decompose-engineer
description: Build and review Decompose component contracts, default and preview implementations, parent-child component hierarchies, ChildStack/ChildSlot/ChildPages/ChildPanels/ChildItems navigation, serializable configs, component outputs, lifecycle, StateKeeper/InstanceKeeper, back handling, and root wiring. Use for screens, flows, tabs, navigation, component factories, or stateless callback components.
---

# Vibe Decompose Engineer

## When to use

Own UI-independent lifecycle-aware component contracts and navigation. Prefer this skill, not MVIKotlin, for a stateless callback/output screen.

## Inputs

Read target instructions, component graph, AppSpec flows/screens, and [component-contract.md](references/component-contract.md). For navigation/root work read [navigation-and-root.md](references/navigation-and-root.md); for retention read [lifecycle-state-retention.md](references/lifecycle-state-retention.md). Read [blinkly-adaptations.md](references/blinkly-adaptations.md) only when local evidence is useful. Paths live in the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Define the public component model/callback/output contract.
2. Decide thin component versus Store-backed component.
3. Build strict parent-child factories with one `ComponentContext` per child.
4. Keep immutable serializable navigation arguments in configs; inject dependencies in factories.
5. Create navigation properties once and route child outputs upward.
6. Wire lifecycle, back handling, StateKeeper/InstanceKeeper, and platform root lifecycle.
7. Add preview implementation and hand behavior tests to Test Engineer.

## Decision rules

- UI depends on the component; the component never depends on Compose UI.
- Delegate `ComponentContext` in default implementations.
- Create root/navigation on the main/UI thread.
- Prefer double-click-safe stack operations and avoid duplicate configs.
- Keep callback-only features thin.
- Retain a Store only for state/async/subscription/resume needs.
- Map raw Store state to a UI-oriented component model.
- Subscribe to possible startup labels before manual Store initialization.

## Validation

Verify hierarchy/context uniqueness, serializable config restoration, active children, back behavior, lifecycle transitions, output routing, duplicate clicks, preview isolation, and root creation on both platforms.

## Escalation/hand-off

Hand Store internals to MVIKotlin, pure rules to Domain, Compose APIs/design to Product Designer/Compose Expert, and behavioral coverage to Test Engineer.

## Reusable learning

Propose reusable component/navigation rules for [learned-patterns.md](references/learned-patterns.md); never modify it without approval.

