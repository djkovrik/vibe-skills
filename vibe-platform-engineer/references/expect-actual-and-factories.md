# Expect/actual and factories

- Prefer a common interface plus platform factory when `expect/actual` is not needed for language-level declarations.
- Keep the common contract minimal and platform-neutral.
- Put Android/iOS implementations and native imports in their source sets.
- Define ownership, threading, close/cancel lifecycle, and typed failures.
- Supply deterministic common-test fakes.

Primary source:

- https://kotlinlang.org/docs/multiplatform/multiplatform-expect-actual.html

Blinkly adaptation: platform modules and root factories demonstrate explicit platform construction. Reuse the boundary, not project identifiers.

