---
name: vibe-product-designer
description: Research, design, critique, and improve Material 3-first Kotlin Multiplatform product UI and UX, including M3 Expressive, component selection, adaptive screen flows, information hierarchy, states, design tokens, color, typography, shape, spacing, motion, icons and assets, light/dark themes, insets, accessibility, localization, preview contracts, and post-golden Lazyweb review. Use for new or existing screens, UI evidence, full-app design review, UX flows, theming, accessibility, Material component decisions, or product-facing Compose work.
---

# Vibe Product Designer

## When to use

Own product UI decisions and evidence. Do not duplicate Compose API expertise or visual-golden mechanics.

## Inputs

Read AppSpec screens/flows/assets, product constraints, current screenshots, theme/components, and accessibility/localization requirements. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md) to product copy and app-bundled local datasets. Before any product UI design or critique read [lazyweb-routing.md](references/lazyweb-routing.md) and [material3-foundations.md](references/material3-foundations.md). Read [material3-component-selection.md](references/material3-component-selection.md) whenever selecting, replacing, or auditing controls and surfaces. Read [material3-compose-contract.md](references/material3-compose-contract.md) before the Compose hand-off, and use [material3-screen-contract-example.md](references/material3-screen-contract-example.md) when producing or auditing the compliance matrix. Select [design-system-and-theme.md](references/design-system-and-theme.md), [screen-states-responsive-accessibility.md](references/screen-states-responsive-accessibility.md), [compose-expert-handoff.md](references/compose-expert-handoff.md), or [design-to-golden-loop.md](references/design-to-golden-loop.md) as needed. Local evidence paths live in the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Confirm `lazyweb_get_workflows`; on the first Lazyweb session call it with `operation=list` and `task_context="first run Lazyweb capabilities"`.
2. Run one `lazyweb_search` for each exact primary-screen pattern before design.
3. Route the full task through current Lazyweb workflow guidance. For current `lazyweb-design`, use create for a new screen, improve for existing quality, or optimize for an existing conversion metric.
4. Use screenshot upload flow for an existing full-resolution screen.
5. Establish the Material 3 design contract before inventing layouts or controls: choose the canonical layout, adaptive breakpoint behavior, navigation family, component variants, color/type/shape/spacing/elevation/motion tokens, and interaction-state treatment. Prefer M3 Expressive for new or substantially redesigned UI when its APIs are available and acceptable across declared targets; otherwise use baseline M3 and record the semantic fallback.
6. Convert evidence into hierarchy, states, actions, responsive/inset rules, accessibility, localization, semantic design tokens, typography roles, shared string-resource keys, and explicit text wrapping/truncation expectations. Use M3 as the interaction grammar and product tokens plus one or two intentional hero moments as the recognizable product expression.
7. Map every interactive or containing element to a canonical M3 component and variant before implementation. Record semantic purpose, prominence, persistence, modality, selection cardinality, window-size adaptation, required states, and any justified custom component or M3 deviation.
8. Decide `icon`, `text`, `icon + text`, or `intentionally no icon`; record source, selected/unselected variants, accessibility label, and asset status. Ask the user to approve the standard icon source or provide required custom/brand assets before Compose work starts. Put unresolved material choices in blocking AppSpec `openQuestions`.
9. Define the preview/golden matrix for every primary screen and applicable state: light and dark are mandatory; add the largest required font scale, longest supported locale, compact phone, and adaptive variants where they create distinct risk.
10. Hand the Material 3 component map and Compose API/state/effect/performance/interop mechanics to Compose Expert. Compose delivery is incomplete until the selected APIs are verified against the repository's Compose Multiplatform version and targets and deterministic preview entry points implement the approved matrix.
11. Hand scanner/Paparazzi mechanics to Visual Testing.
12. After approved goldens exist, build an ordered queue of all declared primary screens and review it through the current Lazyweb workflow. Use exactly one screen per report and keep exactly one Lazyweb review report in flight for the task. Do not batch screens, launch per-screen reviews through parallel agents/calls, or submit the next screen until the previous report reaches terminal completion, has been retrieved, and its URL, coverage, and findings are recorded. If a screen needs separate theme/state reports, run those sequentially before advancing to the next screen. Track screen, state, theme, locale, and font-scale coverage.
13. Audit the complete golden set against the Material 3 compliance matrix: component semantics and variants; layout and navigation adaptation; color-role pairings; typography hierarchy; shape, spacing, elevation, state layers, and motion; fonts/glyphs; unintended wrapping or clipping; light/dark contrast; icons; touch targets; insets; accessibility; localization; and restraint of expressive tactics. Route approved fixes back through Compose and repeat golden verification.

## Decision rules

- Provide loading/content/empty/error/offline/permission states where applicable.
- Treat current Material 3 as the default design system for all product-facing Compose UI. Use a canonical M3 component when it fits the semantic job; create a custom component only when no suitable component exists or a documented product requirement cannot be met through supported slots and tokens.
- Prefer semantic, system, and component tokens over raw visual values. Preserve documented foreground/background color-role pairs, component state behavior, and minimum target sizes when customizing.
- Do not use visual novelty as a reason to discard familiar Material behavior. Build recognition through coherent product tokens, expressive hierarchy, and at most one or two hero moments per product or flow.
- Treat M3 Expressive guidance as preferred design direction for new work, but do not require an experimental or unavailable Compose API. Require an explicit baseline M3 fallback and API-maturity note for every unavailable expressive component or style.
- Do not select a component by appearance alone. Match the action, selection model, prominence, persistence, modality, content hierarchy, and breakpoint behavior defined in the component-selection reference.
- Keep all app-bundled user-visible strings in Compose Multiplatform Resources locale-specific `strings.xml` files, using one shared key across locales. English is always the default/base locale; Russian is the initial additional locale. Adding a locale must not change the default locale or domain/persistence schemas.
- Do not design an in-app language picker or language setting. The active language follows the operating-system locale only; unsupported locales use English fallback.
- Keep resolved catalog translations out of Store/component/domain/persistence models. Carry stable IDs/resource references to the presentation boundary; user-authored and server-owned dynamic text remains data.
- Keep component models UI-oriented and independent of raw Store state.
- Centralize Material-aligned tokens and verify light/dark/system variants. Keep color, typography, shape, spacing, elevation, icon, and motion decisions traceable from semantic roles to component usage.
- Support font scaling, touch targets, contrast, content descriptions, and reduced motion.
- Keep previews free of real services.
- Prefer canonical Material Symbols for standard actions when approved; keep one style and coherent fill/weight behavior, and require user-provided or explicitly licensed assets for custom/brand iconography. Do not replace clear text with icon-only controls merely to increase icon count.
- Treat unintended one-line-to-two-line wrapping, clipped glyphs, fallback-font changes, and hierarchy drift as defects. Treat intentional wrapping at the declared stress font scale as expected behavior.
- Treat approved design/spec as truth; goldens record it.
- Treat one-screen-at-a-time Lazyweb review as a hard reliability constraint even when orchestration or tool batching could run requests concurrently.
- If Lazyweb is unavailable, disclose this and use official platform guidance plus existing evidence without presenting taste as research.

## Validation

Trace decisions to evidence and screen IDs. Require a per-screen Material 3 compliance matrix covering canonical layout, navigation, components/variants, tokens, interaction states, responsive adaptations, API maturity/fallbacks, accessibility, and justified deviations. Check every state, compact/expanded layout, safe-area ownership, production string-resource usage, system-locale behavior, absence of language-selection UI, EN default/fallback behavior and locale key completeness, font loading and glyph coverage, line-count expectations, font scaling, screen reader order, contrast, touch targets, motion preference, EN/RU expansion, dark/light theme, icon inventory, preview determinism, golden coverage, Lazyweb report URLs, and disposition of every blocking finding.

## Escalation/hand-off

Compose APIs -> Compose Expert. Navigation -> Decompose. Product state -> Domain/MVIKotlin. Ads placement -> Monetization. Approved screenshots/goldens -> Visual Testing.

## Reusable learning

Propose evidence-backed design-system rules for [learned-patterns.md](references/learned-patterns.md); do not generalize a single visual preference.
