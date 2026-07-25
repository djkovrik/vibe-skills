# Authentication, errors, and retries

- Use Ktor bearer auth or a dedicated policy with host scoping.
- Define token storage, refresh serialization, 401 retry limit, logout, and refresh-failure behavior.
- Never send a token to an untrusted redirected/alternate host.
- Distinguish timeout, connection/transport, HTTP status, serialization, auth, and domain failures.
- Read an error body once and bound/redact it.
- Rethrow cancellation.
- Retry only safe/idempotent operations with bounded attempts, backoff, and jitter.
- Generate idempotency keys from stable operation identity and persist them for retried operations.

Official sources:

- https://ktor.io/docs/client-bearer-auth.html
- https://ktor.io/docs/client-response-validation.html

