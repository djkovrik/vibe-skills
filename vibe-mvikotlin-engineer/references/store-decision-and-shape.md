# Store decision and shape

Use a Store for observable state, asynchronous work, bootstrap subscriptions, reducer-controlled transitions, one-off labels, or resume-aware behavior. Skip it for stateless output forwarding.

Preferred shape:

- internal Store contract with nested Intent/State/Label;
- optional Action from Bootstrapper and private Msg to Reducer;
- provider receiving StoreFactory and narrow dependencies;
- a new stateful Executor per factory call;
- pure stateless Reducer object;
- Store State independent of component UI models.

Official sources:

- https://arkivanov.github.io/MVIKotlin/
- https://arkivanov.github.io/MVIKotlin/store/
- https://arkivanov.github.io/MVIKotlin/view/

