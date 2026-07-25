# Managers, events, and errors

- Use a manager/engine when a stable rule combines multiple sources or operations.
- Expose narrow suspend functions and watcher `Flow` contracts.
- Return compact domain results, not component UI models.
- Preserve original causes when mapping low-level failures.
- Distinguish retryable, permission, validation, unavailable, unauthorized, and unknown outcomes only when callers can act differently.
- Use typed cross-feature events/outputs; keep navigation interpretation at the parent/root.
- Rethrow cancellation before broad exception mapping.

Blinkly adaptation: feature managers, central error/output types, and upward root routing are useful patterns. Empty flow catches and app-specific error names are not reusable rules.

