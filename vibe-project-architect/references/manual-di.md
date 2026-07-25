# Manual dependency injection

Define a small module interface, a companion dependencies interface, and a top-level factory returning an implementation with lazy-owned dependencies. Build the graph at a platform composition root.

Rules:

- Inject interfaces, dispatchers, clock, and platform factories explicitly.
- Make ownership/close lifecycle visible for databases and clients.
- Avoid service locators and dependencies in serialized navigation configs.
- Keep startup ordering explicit, especially native SDK initialization before shared graph creation.
- Add a DI framework only when the target project/user selects it and the migration benefit is measurable.

Blinkly adaptation: its domain/database/settings/notifier/alarm/sync modules and platform `RootComponentFactory` are concrete references listed through the shared source registry.

