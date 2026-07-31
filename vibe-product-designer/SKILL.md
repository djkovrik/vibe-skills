---
name: vibe-product-designer
description: Research, design, critique, and improve Kotlin Multiplatform product UI and UX, including screen flows, information hierarchy, screen states, design systems, color, typography, shape, spacing, icon and asset inventories, light/dark themes, responsive layout, insets, accessibility, localization, preview contracts, and post-golden Lazyweb review. Use for new or existing screens, UI evidence, full-app design review, UX flows, theming, accessibility, icon decisions, or product-facing Compose work.
---

# Vibe Product Designer

## When to use

Own product UI decisions and evidence. Do not duplicate Compose API expertise or visual-golden mechanics.

## Inputs

Read AppSpec screens/flows/assets, product constraints, current screenshots, theme/components, and accessibility/localization requirements. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md) to product copy and app-bundled local datasets. Before design work read [lazyweb-routing.md](references/lazyweb-routing.md). Select [design-system-and-theme.md](references/design-system-and-theme.md), [screen-states-responsive-accessibility.md](references/screen-states-responsive-accessibility.md), [compose-expert-handoff.md](references/compose-expert-handoff.md), or [design-to-golden-loop.md](references/design-to-golden-loop.md) as needed. Local evidence paths live in the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Confirm `lazyweb_get_workflows`; on the first Lazyweb session call it with `operation=list` and `task_context="first run Lazyweb capabilities"`.
2. Run one `lazyweb_search` for each exact primary-screen pattern before design.
3. Route the full task through current Lazyweb workflow guidance. For current `lazyweb-design`, use create for a new screen, improve for existing quality, or optimize for an existing conversion metric.
4. Use screenshot upload flow for an existing full-resolution screen.
5. Convert evidence into hierarchy, states, actions, responsive/inset rules, accessibility, localization, semantic design tokens, typography roles, shared string-resource keys, and explicit text wrapping/truncation expectations.
6. Inventory every interactive element before implementation. Decide `icon`, `text`, `icon + text`, or `intentionally no icon`; record semantic purpose, source, selected/unselected variants, accessibility label, and asset status. Ask the user to approve the standard icon source or provide required custom/brand assets before Compose work starts. Put unresolved material choices in blocking AppSpec `openQuestions`.
7. Define the preview/golden matrix for every primary screen and applicable state: light and dark are mandatory; add the largest required font scale, longest supported locale, compact phone, and adaptive variants where they create distinct risk.
8. Hand Compose API/state/effect/performance/interop mechanics to Compose Expert. Compose delivery is incomplete until deterministic preview entry points implement the approved matrix.
9. Hand scanner/Paparazzi mechanics to Visual Testing.
10. After approved goldens exist, review all declared primary screens and flows through the current Lazyweb workflow, using one existing screen per improve report unless the live workflow explicitly supports a multi-screen artifact. Track screen, state, theme, locale, and font-scale coverage.
11. Audit the complete golden set for cross-screen consistency, fonts/glyphs, unintended wrapping or clipping, typography hierarchy, light/dark color and contrast, Material 3 component/state use, icon correctness and missing icon opportunities, touch targets, insets, accessibility, and localization. Route approved fixes back through Compose and repeat golden verification.

## Decision rules

- Provide loading/content/empty/error/offline/permission states where applicable.
- Keep all app-bundled user-visible strings in Compose Multiplatform Resources locale-specific `strings.xml` files, using one shared key across locales. New specs default to RU/EN unless explicitly overridden; adding a locale must not change domain or persistence schemas.
- Keep resolved catalog translations out of Store/component/domain/persistence models. Carry stable IDs/resource references to the presentation boundary; user-authored and server-owned dynamic text remains data.
- Keep component models UI-oriented and independent of raw Store state.
- Centralize tokens and verify light/dark/system variants.
- Support font scaling, touch targets, contrast, content descriptions, and reduced motion.
- Keep previews free of real services.
- Prefer canonical Material Symbols for standard actions when approved; require user-provided or explicitly licensed assets for custom/brand iconography. Do not replace clear text with icon-only controls merely to increase icon count.
- Treat unintended one-line-to-two-line wrapping, clipped glyphs, fallback-font changes, and hierarchy drift as defects. Treat intentional wrapping at the declared stress font scale as expected behavior.
- Treat approved design/spec as truth; goldens record it.
- If Lazyweb is unavailable, disclose this and use official platform guidance plus existing evidence without presenting taste as research.

## Validation

Trace decisions to evidence and screen IDs. Check every state, compact/expanded layout, safe-area ownership, production string-resource usage and locale key completeness, font loading and glyph coverage, line-count expectations, font scaling, screen reader order, contrast, touch targets, motion preference, RU/EN expansion, dark/light theme, icon inventory, preview determinism, golden coverage, Lazyweb report URLs, and disposition of every blocking finding.

## Escalation/hand-off

Compose APIs -> Compose Expert. Navigation -> Decompose. Product state -> Domain/MVIKotlin. Ads placement -> Monetization. Approved screenshots/goldens -> Visual Testing.

## Reusable learning

Propose evidence-backed design-system rules for [learned-patterns.md](references/learned-patterns.md); do not generalize a single visual preference.
