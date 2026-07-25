# MVIKotlin Store tests

- Use a real `DefaultStoreFactory` unless testing a factory wrapper.
- Control main-thread checks in setup only and restore them in teardown.
- Cover initial state, intents, actions/bootstrap, reducer transitions, manager success/failure, subscriptions, labels, cancellation, and disposal.
- Subscribe before manual initialization when startup labels are possible.
- Use virtual time for delays/cooldowns.
- Assert labels as one-off events and restoration separately from retention.

Primary source:

- https://arkivanov.github.io/MVIKotlin/store/

