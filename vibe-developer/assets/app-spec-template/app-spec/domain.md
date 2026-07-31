# Domain

## Glossary

- Preference: a user-selected application option.

## Entities and value objects

`PreferenceValue` is a validated, language-neutral value object. Presentation maps its stable ID to the shared Compose string resource key; domain code does not contain translated labels or Compose resource types.

## Invariants

Only supported values may be persisted.

## Time and scheduling

No time-based rules.

## Error semantics

Persistence failures preserve their cause and surface a retryable error.
