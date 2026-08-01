# MVIKotlin Store tests

- Use a real `DefaultStoreFactory` unless testing a factory wrapper.
- Control main-thread checks in setup only and restore them in teardown.
- Cover initial state, intents, actions/bootstrap, reducer transitions, Manager standard-`Result` success/failure/nullable-success, `unwrap` cancellation rethrow, subscriptions, labels, and disposal.
- Subscribe before manual initialization when startup labels are possible.
- Use virtual time for delays/cooldowns.
- Assert labels as one-off events and restoration separately from retention.
- Test the dedicated `State -> Component.Model` mapper and ensure the production component exposes the mapped Store value without a mutable mirror.

Primary source:

- https://arkivanov.github.io/MVIKotlin/store/
