# Blinkly Result-unwrapping adaptation

Blinkly uses a centralized executor helper to turn manager `Result<T>` values into explicit success and error branches.

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

Do not copy package names, error classes, or cancellation behavior blindly. Keep failure causes, publish only intentional one-off labels, and test both branches. Locate the concrete helper through the shared source registry.

