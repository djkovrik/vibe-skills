# Expect/actual and factories

- Prefer a common interface plus platform factory when `expect/actual` is not needed for language-level declarations.
- Keep the common contract minimal and platform-neutral.
- Put Android/iOS implementations and native imports in their source sets.
- Define ownership, threading, close/cancel lifecycle, and typed failures.
- Supply deterministic common-test fakes.
- If an `actual` implementation must produce user-visible text and cannot consume Compose resources, resolve a stable key from Android `res/values*/strings.xml` or an iOS string catalog/localized `.strings` table. Keep translated literals out of platform code.

Primary source:

- https://kotlinlang.org/docs/multiplatform/multiplatform-expect-actual.html

Blinkly adaptation: platform modules and root factories demonstrate explicit platform construction. Reuse the boundary, not project identifiers.
