# Permissions and lifecycle

Model permissions as a state machine:

```text
unknown -> checking -> granted | denied | unavailable
denied -> requesting -> granted | denied
denied -> settings pending -> recheck on resume
```

- Separate checking from requesting.
- Explain rationale in product UI, not the platform service.
- Handle revoked access and “do not ask again”.
- Recheck after Settings or foreground resume.
- Bridge iOS/UIKit and Android host lifecycle explicitly.

Primary sources:

- https://developer.android.com/training/permissions/requesting
- https://developer.apple.com/documentation/uikit/protecting-the-user-s-privacy

Blinkly adaptation: exact-alarm and notification flows retain a pending action and recheck on resume.

