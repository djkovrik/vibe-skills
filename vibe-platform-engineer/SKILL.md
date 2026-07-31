---
name: vibe-platform-engineer
description: Implement Kotlin Multiplatform expect/actual services, Android and iOS factories, native localized resource fallbacks, permissions, notification and exact-alarm access, notifications, alarms, background/resume behavior, lifecycle bridges, screen-awake, haptics/beeper, manifests, Info.plist, and native capability configuration. Use for platform APIs, platform-specific localization, permission state machines, reminders, background work, or platform-specific source sets.
---

# Vibe Platform Engineer

## When to use

Own native capability implementations and configuration. Do not place product UI or business scheduling semantics inside platform services.

## Inputs

Read AppSpec capabilities/localization, domain contracts, platform entry points, manifests/plists, and current official platform/library docs. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md) whenever an `actual` or native API emits user-visible text. Select [expect-actual-and-factories.md](references/expect-actual-and-factories.md), [permissions-lifecycle.md](references/permissions-lifecycle.md), [notifications-alarms-background.md](references/notifications-alarms-background.md), or [platform-configuration.md](references/platform-configuration.md). Consult adaptations via the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Define the smallest common contract.
2. Implement platform factories/actuals and deterministic fakes.
3. Model permission checks and requests as separate state transitions.
4. Bridge lifecycle and recheck after Settings on resume.
5. Separate logical schedules from physical alarm/notification instances.
6. Configure manifests/plists/entitlements and platform startup.
7. Put native-only copy in Android `res/values*/strings.xml` or iOS string catalogs/localized `.strings` tables with stable keys. Keep English as the complete default/base localization and Russian as an additional localization; follow the operating-system locale without installing an app-specific override, and never embed translated literals in `actual` code.
8. Test common contract plus platform builds/manual capability and locale checks.

## Decision rules

- Model denied, unavailable, pending, granted, and settings-return paths.
- Recompute platform schedules after reboot, time-zone change, or app update when required.
- Keep platform failures typed and route them to domain/component output.
- Do not render UI from a platform service.
- Prefer Compose Multiplatform Resources for common text. When they are unavailable to the native boundary, resolve the shared semantic key through native platform localization resources rather than hardcoded strings; preserve English as the default fallback.
- Do not add Android per-app language APIs, iOS language overrides, or a locale preference unless a future explicit product decision changes this contract.
- Keep iOS lifecycle ownership explicit and verify current Essenty/platform helpers.

## Validation

Verify denied/granted/revoked flows, resume recheck, reboot/update/time-zone recovery, cancellation by stable physical ID, fake implementations, system-locale-driven native localization and English fallback without app overrides, manifest/plist entries, Android target builds, and available iOS builds/device behavior.

## Escalation/hand-off

Domain owns schedule meaning; Persistence owns stored schedules; MVIKotlin owns observable permission state; Product Designer owns permission UX; Project Architect owns entry-point/release wiring.

## Reusable learning

Propose durable platform contracts for [learned-patterns.md](references/learned-patterns.md); never auto-edit the knowledge base.
