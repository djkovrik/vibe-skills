# Platform configuration

Audit the full capability contract:

- Android manifest permissions, receivers, services, queries, exported flags, and build variants;
- iOS Info.plist purpose strings, background modes, entitlements, capabilities, and target membership;
- minimum OS/API and current SDK requirements;
- platform initialization ordering and environment/build-config values;
- preview/test disabling and release diagnostics.

Never copy signing data, bundle IDs, Firebase files, ad IDs, or reference-project minimums. Verify current official platform/library documentation and both platform builds.

