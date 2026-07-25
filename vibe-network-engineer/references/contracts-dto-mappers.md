# Contracts, DTOs, and mappers

- Define domain API interfaces/models without Ktor or wire DTO types.
- Keep request/response DTOs internal and map at the infrastructure boundary.
- Use `@SerialName` exactly as documented; test suspicious whitespace/casing.
- Choose defaults and `ignoreUnknownKeys` based on compatibility requirements.
- Validate required fields rather than converting missing data into misleading defaults.
- Store endpoint documentation links beside the domain API contract.
- Use sanitized real-shape fixtures for mapper tests.

Tackle adaptation: domain API contracts, internal DTOs/mappers, and fixture tests are useful evidence. Its trailing-space `error_description ` field is an explicit hazard, not a convention.

