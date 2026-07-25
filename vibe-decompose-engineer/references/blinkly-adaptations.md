# Blinkly adaptations

Resolve all paths through the shared source registry.

Useful adaptations:

- public contract + `integration/*Default` + optional preview/mappers;
- thin callback-only components without Stores;
- root/onboarding/home parents owning their own stacks;
- upward typed outputs interpreted by parents;
- retained Stores through InstanceKeeper;
- preview implementations with static `MutableValue` and no production services.

Revalidate package layout, navigation owner, output types, and test location in the target project. Do not copy Blinkly names, packages, or hierarchy.

