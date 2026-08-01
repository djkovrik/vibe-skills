# Blinkly Result-unwrapping adaptation

Blinkly uses a centralized executor helper to turn Manager `Result<T>` values into explicit success and error branches. Generalize the pattern with `fold`; implementations based on `getOrNull()?.let` lose successful `null` values.

Adapt the idea:

```kotlin
result.fold(
    onSuccess = onSuccess,
    onFailure = { error ->
        if (error is CancellationException) throw error
        onFailure(mapError(error))
    },
)
```

Managers create the single result boundary around data/external work:

```kotlin
suspend fun load(): Result<Data> = runCatching {
    repository.load().getOrThrow().toDomain()
}
```

Omit `getOrThrow()` when the lower API returns a plain value. Do not create `Result<Result<T>>`.

Do not copy package names or error classes. Always rethrow `CancellationException`, preserve failure causes, publish only intentional one-off labels, and test success (including `null`), failure, and cancellation. Locate the concrete Blinkly helpers through the shared source registry.
