# Snapshot schema and mappers

- Give the remote DTO an explicit schema version.
- Reject unsupported major/incompatible versions before local mutation.
- Use portable primitives and explicit serializers.
- Keep domain/local/remote models separate with tested mappers.
- Include stable entity IDs and only conflict-policy metadata.
- Avoid platform timestamps or generated database entities on the wire.
- Test round trips and malformed/unknown versions.

Blinkly adaptation: versioned Firestore-like snapshots and per-domain data are implementation evidence, not a required backend.

