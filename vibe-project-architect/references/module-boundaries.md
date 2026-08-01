# Module boundaries

## Durable rules

- Point dependencies toward stable domain/public contracts.
- Keep feature UI/component implementation, domain, and infrastructure replaceable.
- Put shared contracts in `commonMain` and native implementations in platform source sets.
- Introduce a module only when it creates an enforceable ownership, dependency, build, or test boundary.
- Reject cycles and “shared-utils” dumping grounds.

For screen-level Decompose architecture, default to a component module per screen or cohesive nested flow. Let it own the public component contract, `integration/*Default`, optional `integration/*Preview`, Store, feature Manager/domain data, mapper, and focused wiring. Group only trivial callback-only leaves or inseparable screens when a separate module would enforce no boundary, and document that decision.

Inspect current Kotlin Multiplatform structure before editing:

- https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html
- https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html

## Blinkly adaptation

Blinkly demonstrates platform app -> root factory -> screen/flow component modules -> domain interfaces, with database/settings/notifier/alarm/compose modules around those contracts. Its `shared/component/**` graph is evidence for per-component ownership, not a required directory name. Resolve paths through the shared source registry.
