# Preview contract

- Use the production composable with a preview-only component/model.
- Keep data, clock, locale, theme, dimensions, and animation state deterministic.
- Avoid real network, database, SDK, permission, or platform services.
- Cover meaningful content, empty, error, loading, permission/offline, long text, font scale, light/dark, and responsive variants.
- Keep at least one realistic phone viewport for large variant boards.
- Treat preview compilation as a test obligation.

Primary source:

- https://developer.android.com/develop/ui/compose/tooling/previews

Blinkly adaptation: separate static preview component implementations are reusable evidence.

