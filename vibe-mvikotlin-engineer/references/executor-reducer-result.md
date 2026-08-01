# Executor, reducer, and Result

MVIKotlin's Store has Bootstrapper, Executor, and Reducer roles.

- Run side effects, flows, async work, and Manager calls in Executor.
- Dispatch Msg on the main thread and reduce synchronously/purely.
- Create Bootstrapper/Executor as stateful instances, not singletons.
- Use the Executor lifecycle scope so disposal cancels owned work.
- Keep persistence/network/settings/platform access behind a feature Manager; the Store never calls repositories/data sources directly.
- Have Manager operations return standard Kotlin `Result<T>` through `runCatching` and compact domain/feature data, not component models.
- Centralize Result mapping in a shared `unwrap` helper with explicit success, failure, nullable-success, and cancellation paths.
- When a lower boundary already returns `Result<T>`, call `getOrThrow()` inside the Manager's `runCatching` block to avoid `Result<Result<T>>`.
- Do not define a generic custom Success/Failure result wrapper; use sealed outcomes only for meaningful domain cases.
- Move complex calculations into Domain managers/engines.

Official source:

- https://arkivanov.github.io/MVIKotlin/store/
