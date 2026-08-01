# Decompose component test harness

Use:

- `DefaultComponentContext` with a controlled `LifecycleRegistry`;
- real `DefaultStoreFactory` for Store-backed components;
- injected test dispatchers and `runTest`;
- public component callbacks/models/outputs;
- active `ChildStack` child and back dispatcher assertions.

Drive create/resume/pause/destroy explicitly. Advance virtual work after construction, flow emissions, callbacks, and lifecycle events. Do not inspect Store internals from a component test.

For a component with UI-visible `Value<Model>`, use its public callbacks and assert the mapped model. The production path must be `Default component -> retained Store -> State-to-Model mapper -> Value<Model>`; direct repository calls and production `MutableValue<Model>` updates are failures. Static `MutableValue` remains valid in preview/test component implementations.

Official sources:

- https://arkivanov.github.io/Decompose/component/overview/
- https://arkivanov.github.io/Decompose/navigation/overview/

Blinkly's centralized common component harness is an adaptation; choose the natural target module location.
