---
name: vibe-platform-engineer
description: Implement Kotlin Multiplatform expect/actual services, Android and iOS factories, permissions, notification and exact-alarm access, notifications, alarms, background/resume behavior, lifecycle bridges, screen-awake, haptics/beeper, manifests, Info.plist, and native capability configuration. Use for platform APIs, permission state machines, reminders, background work, or platform-specific source sets.
---

# Vibe Platform Engineer

## When to use

Own native capability implementations and configuration. Do not place product UI or business scheduling semantics inside platform services.

## Inputs

Read AppSpec capabilities, domain contracts, platform entry points, manifests/plists, and current official platform/library docs. Select [expect-actual-and-factories.md](references/expect-actual-and-factories.md), [permissions-lifecycle.md](references/permissions-lifecycle.md), [notifications-alarms-background.md](references/notifications-alarms-background.md), or [platform-configuration.md](references/platform-configuration.md). Consult adaptations via the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Define the smallest common contract.
2. Implement platform factories/actuals and deterministic fakes.
3. Model permission checks and requests as separate state transitions.
4. Bridge lifecycle and recheck after Settings on resume.
5. Separate logical schedules from physical alarm/notification instances.
6. Configure manifests/plists/entitlements and platform startup.
7. Test common contract plus platform builds/manual capability checks.

## Decision rules

- Model denied, unavailable, pending, granted, and settings-return paths.
- Recompute platform schedules after reboot, time-zone change, or app update when required.
- Keep platform failures typed and route them to domain/component output.
- Do not render UI from a platform service.
- Keep iOS lifecycle ownership explicit and verify current Essenty/platform helpers.

## Validation

Verify denied/granted/revoked flows, resume recheck, reboot/update/time-zone recovery, cancellation by stable physical ID, fake implementations, manifest/plist entries, Android target builds, and available iOS builds/device behavior.

## Escalation/hand-off

Domain owns schedule meaning; Persistence owns stored schedules; MVIKotlin owns observable permission state; Product Designer owns permission UX; Project Architect owns entry-point/release wiring.

## Reusable learning

Propose durable platform contracts for [learned-patterns.md](references/learned-patterns.md); never auto-edit the knowledge base.

