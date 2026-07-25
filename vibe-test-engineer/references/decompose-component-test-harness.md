# Decompose component test harness

Use:

- `DefaultComponentContext` with a controlled `LifecycleRegistry`;
- real `DefaultStoreFactory` for Store-backed components;
- injected test dispatchers and `runTest`;
- public component callbacks/models/outputs;
- active `ChildStack` child and back dispatcher assertions.

Drive create/resume/pause/destroy explicitly. Advance virtual work after construction, flow emissions, callbacks, and lifecycle events. Do not inspect Store internals from a component test.

Official sources:

- https://arkivanov.github.io/Decompose/component/overview/
- https://arkivanov.github.io/Decompose/navigation/overview/

Blinkly's centralized common component harness is an adaptation; choose the natural target module location.

