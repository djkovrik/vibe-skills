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
