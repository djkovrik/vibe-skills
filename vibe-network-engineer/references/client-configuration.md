# HttpClient configuration

- Create the client at one composition point and expose explicit ownership/close lifecycle.
- Choose engines per target from the target project/current Ktor docs.
- Install ContentNegotiation with an explicit `Json` instance.
- Configure timeouts, response validation, redirect policy, default headers, and logging deliberately.
- Redact authorization/cookies and disable verbose logging in production.
- Keep API implementations/DTOs internal.

Official sources:

- https://ktor.io/docs/client-create-multiplatform-application.html
- https://ktor.io/docs/client-serialization.html
- https://ktor.io/docs/client-response-validation.html

