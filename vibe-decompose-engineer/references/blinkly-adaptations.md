# Blinkly adaptations

Resolve all paths through the shared source registry.

Useful adaptations:

- public contract + `integration/*Default` + `integration/*Preview` when previews exist + `integration/Mappers.kt` for stateful models;
- thin callback-only components without Stores;
- root/onboarding/home parents owning their own stacks;
- upward typed outputs interpreted by parents;
- retained Stores through InstanceKeeper;
- every UI-visible production model owned by a retained Store and exposed as `store.asValue().map(stateToModel)`;
- feature Managers between Stores and data/external interfaces;
- preview implementations with static `MutableValue` and no production services;
- screen/flow component modules under `shared/component/**`, with root-level wiring and centralized component tests;
- Paparazzi/ComposablePreviewScanner hosted by `shared/compose` because it owns the previews and resources.

Revalidate package layout, navigation owner, output types, and test location in the target project. Do not copy Blinkly names, packages, or hierarchy.
