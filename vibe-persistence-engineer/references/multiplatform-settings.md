# Multiplatform Settings

- Expose typed domain-facing settings properties/flows.
- Treat defaults as product contracts.
- Centralize keys and stable codecs.
- Encode structured values explicitly as JSON/string with version/fallback behavior.
- Test missing, legacy, malformed, update, observation, and reset paths.
- Do not log sensitive settings.
- Separate change tracking from ordinary storage so remote apply is not treated as user edit.

Primary source:

- https://github.com/russhwolf/multiplatform-settings

Blinkly adaptation: typed contracts, defaults, codecs, fallbacks, and tracking decorators are useful evidence.

