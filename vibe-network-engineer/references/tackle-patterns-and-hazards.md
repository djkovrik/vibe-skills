# Tackle adaptations and hazards

Locate Tackle sources through the shared source registry.

Useful adaptations:

- domain API contracts separated from internal Ktor implementations;
- internal request/response DTOs and explicit mappers;
- JSON fixture mapper tests;
- centralized network exception mapping.

Do not copy:

- trailing whitespace in `@SerialName("error_description ")`;
- model `hashCode()` as an idempotency key;
- an internally created HttpClient without explicit close ownership;
- exception handling that covers only an old Ktor subset;
- production classes with unconditional debug logging.

Re-check all APIs against the target Ktor version and official docs.

