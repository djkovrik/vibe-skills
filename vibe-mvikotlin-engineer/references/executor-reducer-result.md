# Executor, reducer, and Result

MVIKotlin's Store has Bootstrapper, Executor, and Reducer roles.

- Run side effects, flows, async work, and manager calls in Executor.
- Dispatch Msg on the main thread and reduce synchronously/purely.
- Create Bootstrapper/Executor as stateful instances, not singletons.
- Use the Executor lifecycle scope so disposal cancels owned work.
- Centralize Result mapping with explicit success, failure, and cancellation paths.
- Move complex calculations into Domain managers/engines.

Official source:

- https://arkivanov.github.io/MVIKotlin/store/

