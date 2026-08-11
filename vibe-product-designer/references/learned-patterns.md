# Learned patterns

ID: PRODUCT-DESIGN-001
Status: accepted
Date: 2026-08-11
Scope: Product-facing Compose Multiplatform screens, flows, themes, components, and visual audits.
Decision: Use current Material 3 as the default interaction and visual grammar. Select canonical layouts and components by semantic job, apply reference/system/component tokens, and prefer M3 Expressive for new work when the required APIs are acceptable across declared targets. Create recognizable product identity through coherent tokens and one or two focused hero moments, not arbitrary custom controls. Require a baseline M3 fallback and API-maturity note for unavailable or experimental expressive features.
Evidence: Repeated cross-application drift toward generic UI; official Material 3 foundations and component guidance; M3 Expressive research and tactics; AndroidX Compose guidance; Compose Multiplatform shared Material3 support.
Consequences: Stricter Material alignment reduces unconstrained visual novelty and requires version/target checks, but improves familiarity, accessibility, adaptive behavior, consistency, product-wide expression, and implementation testability.
Validation: Require the per-screen contract in [material3-screen-contract-example.md](material3-screen-contract-example.md), deterministic preview/golden coverage, and an audit against [material3-foundations.md](material3-foundations.md), [material3-component-selection.md](material3-component-selection.md), and [material3-compose-contract.md](material3-compose-contract.md).
Supersedes: none
