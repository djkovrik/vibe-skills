# Learned patterns

ID: MVIKOTLIN-001
Status: accepted
Date: 2026-08-01
Scope: Store access to repositories, settings, network, persistence, and platform services.
Decision: Store Executors call feature Managers only. Managers create one standard Kotlin `Result<T>` with `runCatching`; existing lower `Result<T>` values are flattened with `getOrThrow()`. Executors consume results through one `fold`-based, cancellation-aware `unwrap`. Do not create custom generic Success/Failure wrappers.
Evidence: Blinkly Managers, StoreProviders, and `shared/utils/Unwrap.kt`; BulbMatch's custom `RepositoryResult` exposed unnecessary result plumbing.
Consequences: Data failures have one boundary and one Store branching policy; domain sealed outcomes remain available for semantic alternatives.
Validation: Test success including `null`, failure cause preservation, cancellation rethrow, Manager mapping, and Store messages/labels.
Supersedes: none

ID: MVIKOTLIN-002
Status: accepted
Date: 2026-08-09
Scope: MVIKotlin Stores owned by Decompose component modules.
Decision: Keep every feature Store and StoreProvider module-internal under the feature's dedicated `.store` package. Never flatten Store declarations into the public component package, `*Component.kt`, or `.integration`; prefer separate Store and provider files.
Evidence: Blinkly `shared/component/**/store` provides consistent discovery and boundary visibility; StainFirstAid placed Store files beside public contracts and Default implementations, obscuring the component-module roles.
Consequences: One extra package and usually two files per stateful component, with clearer public surface, ownership, and architecture review.
Validation: Source/package review maps every Store-backed component to `<feature>.store/*Store` and `*StoreProvider`, verifies internal visibility, and rejects root-package or integration-package Stores.
Supersedes: none
