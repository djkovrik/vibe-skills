# Managers, events, and errors

- Use a manager/engine when a stable rule combines multiple sources or operations.
- Expose narrow suspend functions and watcher `Flow` contracts.
- Return compact domain results, not component UI models.
- Wrap fallible Manager operations in standard Kotlin `Result<T>` with `runCatching`; if a repository already returns `Result<T>`, use `getOrThrow()` inside that block so the Manager still exposes one flat Result.
- Do not model exception transport as a custom generic `Success`/`Failure` hierarchy. Keep sealed outcomes for domain alternatives that callers must exhaustively interpret.
- Preserve original causes when mapping low-level failures.
- Distinguish retryable, permission, validation, unavailable, unauthorized, and unknown outcomes only when callers can act differently.
- Use typed cross-feature events/outputs; keep navigation interpretation at the parent/root.
- Rethrow cancellation before broad exception mapping.

Blinkly adaptation: feature managers, central error/output types, and upward root routing are useful patterns. Empty flow catches and app-specific error names are not reusable rules.
