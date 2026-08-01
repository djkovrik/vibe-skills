# Store decision and shape

Use a Store whenever a production Decompose component exposes UI-visible `Value<Model>`, as well as for asynchronous work, bootstrap subscriptions, reducer-controlled transitions, one-off labels, or resume-aware behavior. Skip it only for stateless output forwarding with no UI-visible model. Decompose router-owned `Value<Child*>` remains owned by the router.

Preferred shape:

- internal Store contract with nested Intent/State/Label;
- optional Action from Bootstrapper and private Msg to Reducer;
- provider receiving StoreFactory and narrow dependencies;
- a new stateful Executor per factory call;
- pure stateless Reducer object;
- Store State independent of component UI models.
- retained Store exposed as `store.asValue().map(stateToModel)` with no production `MutableValue` mirror.

Official sources:

- https://arkivanov.github.io/MVIKotlin/
- https://arkivanov.github.io/MVIKotlin/store/
- https://arkivanov.github.io/MVIKotlin/view/
