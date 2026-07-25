# Network testing

Use Ktor `MockEngine` for deterministic request/response behavior:

- assert method, URL, host, headers, body, and redaction;
- cover success, each status family, malformed JSON, error-body mapping, timeouts, cancellation, and retry count;
- test refresh success/failure/concurrency and foreign-host behavior;
- test DTO mappers against UTF-8 sanitized fixtures;
- verify client closure and no leaked background work.

Official source:

- https://ktor.io/docs/client-testing.html

