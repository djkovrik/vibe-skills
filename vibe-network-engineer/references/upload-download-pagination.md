# Upload, download, and pagination

- Stream large bodies and expose cancellable progress without buffering everything.
- Define multipart filenames/content types and response size/destination ownership.
- Use temporary files plus atomic promotion for downloads when applicable.
- Model cursor/offset pagination explicitly, including terminal, duplicate, empty, and reordered pages.
- Keep retry and idempotency policy per operation.
- Validate checksums/content type when the contract provides them.

Primary references:

- https://ktor.io/docs/client-requests.html
- https://ktor.io/docs/client-responses.html

