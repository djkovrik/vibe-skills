# Module boundaries

## Durable rules

- Point dependencies toward stable domain/public contracts.
- Keep feature UI/component implementation, domain, and infrastructure replaceable.
- Put shared contracts in `commonMain` and native implementations in platform source sets.
- Introduce a module only when it creates an enforceable ownership, dependency, build, or test boundary.
- Reject cycles and “shared-utils” dumping grounds.

Inspect current Kotlin Multiplatform structure before editing:

- https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html
- https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html

## Blinkly adaptation

Blinkly demonstrates platform app -> root factory -> components -> domain interfaces, with database/settings/notifier/alarm/compose modules around those contracts. Treat its layout as evidence, not a required naming scheme. Resolve paths through the shared source registry.

