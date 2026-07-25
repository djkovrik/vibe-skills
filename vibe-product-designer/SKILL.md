---
name: vibe-product-designer
description: Research, design, critique, and improve Kotlin Multiplatform product UI and UX, including screen flows, information hierarchy, screen states, design systems, color, typography, shape, spacing, icons, light/dark themes, responsive layout, insets, accessibility, localization, and Compose implementation hand-off. Use for new or existing screens, UI evidence, design review, UX flows, theming, accessibility, or product-facing Compose work.
---

# Vibe Product Designer

## When to use

Own product UI decisions and evidence. Do not duplicate Compose API expertise or visual-golden mechanics.

## Inputs

Read AppSpec screens/flows/assets, product constraints, current screenshots, theme/components, and accessibility/localization requirements. Before design work read [lazyweb-routing.md](references/lazyweb-routing.md). Select [design-system-and-theme.md](references/design-system-and-theme.md), [screen-states-responsive-accessibility.md](references/screen-states-responsive-accessibility.md), [compose-expert-handoff.md](references/compose-expert-handoff.md), or [design-to-golden-loop.md](references/design-to-golden-loop.md) as needed. Local evidence paths live in the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Confirm `lazyweb_get_workflows`; on the first Lazyweb session call it with `operation=list` and `task_context="first run Lazyweb capabilities"`.
2. Run one `lazyweb_search` for the exact screen pattern before design.
3. Route the full task through current Lazyweb workflow guidance. For current `lazyweb-design`, use create for a new screen, improve for existing quality, or optimize for an existing conversion metric.
4. Use screenshot upload flow for an existing full-resolution screen.
5. Convert evidence into hierarchy, states, actions, responsive/inset rules, accessibility, localization, and design tokens.
6. Hand Compose API/state/effect/performance/interop mechanics to Compose Expert.
7. Implement/coordinate approved screen states, then hand previews and goldens to Visual Testing.

## Decision rules

- Provide loading/content/empty/error/offline/permission states where applicable.
- Keep all strings localizable; default to EN/RU when the spec says so.
- Keep component models UI-oriented and independent of raw Store state.
- Centralize tokens and verify light/dark/system variants.
- Support font scaling, touch targets, contrast, content descriptions, and reduced motion.
- Keep previews free of real services.
- Treat approved design/spec as truth; goldens record it.
- If Lazyweb is unavailable, disclose this and use official platform guidance plus existing evidence without presenting taste as research.

## Validation

Trace decisions to evidence and screen IDs. Check every state, compact/expanded layout, safe-area ownership, font scaling, screen reader order, contrast, touch targets, motion preference, EN/RU expansion, dark/light theme, and preview determinism.

## Escalation/hand-off

Compose APIs -> Compose Expert. Navigation -> Decompose. Product state -> Domain/MVIKotlin. Ads placement -> Monetization. Approved screenshots/goldens -> Visual Testing.

## Reusable learning

Propose evidence-backed design-system rules for [learned-patterns.md](references/learned-patterns.md); do not generalize a single visual preference.

