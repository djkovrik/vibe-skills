# Initialization, retention, and logging

- `accept`, `init`, and `dispose` follow the MVIKotlin main-thread contract.
- Labels are uncached one-off events. If bootstrap may emit synchronously, create with `autoInit=false`, subscribe first, then call `init()`.
- Use Decompose InstanceKeeper to retain the whole Store when required.
- Use state preservation only for stable serializable truth; do not restore transient loading blindly.
- Keep logging/time travel in debug wiring and remove/redact sensitive payloads.

Official sources:

- https://arkivanov.github.io/MVIKotlin/store/
- https://arkivanov.github.io/MVIKotlin/binding_and_lifecycle/
- https://arkivanov.github.io/MVIKotlin/state_preservation/
- https://arkivanov.github.io/MVIKotlin/logging/

