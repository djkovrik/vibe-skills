# Lifecycle, state, and retention

- Use lifecycle callbacks for foreground/background ownership and cleanup.
- Use StateKeeper for serializable state restoration.
- Use InstanceKeeper for retaining a live non-serializable instance such as a Store.
- Do not confuse retained instance lifetime with persisted state.
- Register back handling at the owning component and test priority/enablement.
- Manually bridge lifecycle on non-Android hosts when the platform integration requires it.

Official sources:

- https://arkivanov.github.io/Decompose/component/overview/
- https://arkivanov.github.io/Decompose/tips-tricks/overview/
- https://arkivanov.github.io/Decompose/faq/

