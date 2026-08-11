# Compose Expert hand-off

Product Designer owns:

- evidence, hierarchy, canonical layout, Material 3 component/variant mapping, state coverage, tokens, adaptive behavior, accessibility, localization, expressive intent/fallbacks, and acceptance intent.

Compose Expert owns:

- `@Composable` API design;
- state/effects/recomposition;
- layouts, modifiers, insets, focus, performance;
- navigation bindings and platform interop;
- current Compose Multiplatform/Material3 API details, stability, target availability, opt-ins, and semantic fallbacks.

Read [material3-compose-contract.md](material3-compose-contract.md). Provide Compose Expert the screen ID, approved reference/report, model contract, canonical layout and panes, navigation family, per-element Material 3 component/variant map, states, token roles, expressive scheme and baseline fallbacks, text line/overflow expectations, icon inventory and approved asset sources, inset/responsive rules, accessibility/localization constraints, and the exact preview matrix.

Require an API availability note with repository Compose Multiplatform/Material3 versions, exact selected APIs, stability/opt-ins, Android/iOS differences, and tested fallback. Require deterministic preview entry points alongside production screen implementation; Visual Testing owns scanner/Paparazzi wiring. Do not duplicate the Compose API corpus in this skill.
