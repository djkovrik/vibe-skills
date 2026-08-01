# Learned patterns

ID: ARCH-001
Status: accepted
Date: 2026-08-01
Scope: Decompose screen modules and Compose screenshot-test hosting.
Decision: Default each screen-level component or cohesive flow to a component module owning its contract, Default/Preview implementations, Store, Manager, and mapper. Host Paparazzi/ComposablePreviewScanner in the Compose UI/resource-owning module. Group trivial leaves or use a dedicated screenshot module only with a documented enforceable-boundary, aggregation, or plugin/source-set reason.
Evidence: Blinkly `shared/component/**` and `shared/compose`; BulbMatch's monolithic `shared:app` and separate `screenshot-tests` add indirection without a demonstrated boundary.
Consequences: Clear feature ownership and simpler preview/resource wiring; avoids modules that enforce no boundary.
Validation: Review settings/dependency graph, module ownership, Android unit-test source wiring, generated-test dependencies, resource fidelity, and recorded exception rationale.
Supersedes: none
