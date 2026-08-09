# Learned patterns

ID: DECOMPOSE-001
Status: accepted
Date: 2026-08-09
Scope: Production Decompose component modules, UI-visible models, and Compose-rendered component contracts.
Decision: Keep the public contract at the feature package root, Default/Preview/mappers in `integration`, Store/provider in `store`, and feature Managers/models in `domain`. Expose an immutable `Value<Model>` from a `*ComponentDefault` through retained Store State and a dedicated mapper. Do not mutate production `MutableValue<Model>` or call repositories directly. Every Compose-rendered contract, including a stateless one, gets a sibling Store-free `*ComponentPreview`; only navigation-only components without a Compose render surface are excluded with a documented exception.
Evidence: Blinkly `shared/component/**` consistently separates these package roles and owns previews in component modules; BulbMatch showed state-ownership drift, while StainFirstAid flattened Component/Default/Store/Manager files, co-located one Preview with a Default, and implemented the remaining preview fakes in the Compose module.
Consequences: More small files and packages, but stable discoverability, one testable state owner, reusable deterministic previews, and no duplicated Compose-local fake contracts.
Validation: Architecture review checks package paths and rejects co-located Stores; component tests drive public callbacks and assert mapped models; preview coverage maps every Compose-rendered component contract to its component-module `*ComponentPreview` or a documented navigation-only exception.
Supersedes: none
