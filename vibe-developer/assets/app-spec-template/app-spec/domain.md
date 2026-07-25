# Domain

## Glossary

- Preference: a user-selected application option.

## Entities and value objects

`PreferenceValue` is a validated value object.

## Invariants

Only supported values may be persisted.

## Time and scheduling

No time-based rules.

## Error semantics

Persistence failures preserve their cause and surface a retryable error.

