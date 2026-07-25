# Coverage and CI

- Set coverage expectations by risk/module and inspect uncovered decision branches.
- Do not add meaningless assertions to raise a percentage.
- Run focused tests first, then aggregate KMP/Android/iOS checks.
- Publish test reports and actionable failure artifacts.
- Keep flaky retry/quarantine visible and time-bounded.
- Fail CI on non-zero task exit codes; do not infer success from log text.
- Keep visual verification in Visual Testing and combine its status only at the pipeline level.

Blinkly adaptation: Detekt, Kover, centralized component tests, and CI quality gates are useful local evidence through the shared source registry.

