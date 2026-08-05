# Decompose component test harness

Use:

- `DefaultComponentContext` with a controlled `LifecycleRegistry`;
- real `DefaultStoreFactory` for Store-backed components;
- injected test dispatchers and `runTest`;
- public component callbacks/models/outputs;
- active `ChildStack` child and back dispatcher assertions.

Drive create/resume/pause/destroy explicitly. Advance virtual work after construction, flow emissions, callbacks, and lifecycle events. Do not inspect Store internals from a component test.

This harness is the default vehicle for application acceptance coverage. If the production root component has its own module, centralize the main component suite there so tests can exercise the assembled child graph through root/public contracts. Keep focused feature-local component tests where they improve ownership or iteration speed; move the centralized suite only when root-hosting would violate dependency direction, and record why.

For a component with UI-visible `Value<Model>`, use its public callbacks and assert the mapped model. The production path must be `Default component -> retained Store -> State-to-Model mapper -> Value<Model>`; direct repository calls and production `MutableValue<Model>` updates are failures. Static `MutableValue` remains valid in preview/test component implementations.

Official sources:

- https://arkivanov.github.io/Decompose/component/overview/
- https://arkivanov.github.io/Decompose/navigation/overview/

Blinkly's centralized common component harness is supporting evidence for the preferred root-module arrangement, not merely a project-specific test-location accident.
