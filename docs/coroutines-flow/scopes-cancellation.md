# Coroutine Scopes & Cancellation

Coroutine scope defines the lifecycle of asynchronous work, and cancellation allows safely stopping work when the owner is no longer needed.

## Scopes

### Structured concurrency

Structured concurrency means coroutines are launched inside `CoroutineScope` and tied to its lifecycle. Parent scope knows about child coroutines, waits for their completion and can cancel them together.

The idea is that async work should not "leak" into nowhere: if a screen, request or use case is finished, related coroutines should also complete or be canceled.

In Android, this is especially important for `ViewModel`, lifecycle-aware UI collection and long-running operations. `GlobalScope` is usually considered a smell because the coroutine lives outside a clear owner and is harder to cancel and test.

**In short:** structured concurrency keeps coroutines scoped, cancellable and tied to a clear lifecycle instead of launching unmanaged background work.

### `coroutineScope` vs `supervisorScope`

`coroutineScope` creates a new scope inside a suspend function and suspends until all child coroutines complete. If one child fails with an exception, the scope cancels the other children and propagates the error upward.

`supervisorScope` is similar, but isolates child failures: failure of one child coroutine does not automatically cancel siblings. This is useful when tasks are independent and UI can show partial result.

`coroutineScope` fits when an all-or-nothing result is needed. `supervisorScope` fits when screen blocks or independent requests can complete separately.

```kotlin
coroutineScope {
    val user = async { api.getUser() }
    val cards = async { api.getCards() }

    UiState(
        user = user.await(),
        cards = cards.await()
    )
}
```

If `getUser()` fails, `getCards()` will be canceled. For independent blocks, use `supervisorScope` and handle errors of each `async` separately.

**In short:** `coroutineScope` fails fast and cancels siblings, `supervisorScope` lets sibling coroutines fail independently.

### `viewModelScope`

`viewModelScope` - a `CoroutineScope` tied to `ViewModel`. It is automatically canceled when `ViewModel` receives `onCleared()`.

It is used for screen-level async work: loading data, handling user actions, updating `StateFlow` / `SharedFlow`, launching repository calls and orchestrating UI state.

**Important:** `viewModelScope` does not survive `ViewModel` destruction on process death and is not suitable for guaranteed background work. For deferrable reliable background work, prefer `WorkManager`.

Inside `viewModelScope`, Main dispatcher is used by default, so heavy CPU/I/O work should be moved to repository/use case or switch dispatcher intentionally.

**In short:** `viewModelScope` is the lifecycle-aware scope for `ViewModel` work; it is cancelled when the `ViewModel` is cleared.

## Cancellation

### Cancellation

Cancellation in coroutines is cooperative: a coroutine is not "killed" instantly at an arbitrary point. It must reach a suspension point or check `isActive` / `ensureActive()` itself.

Regular suspend functions like `delay()`, `withContext()`, Flow collection and many network/database APIs can react to cancellation. A CPU-heavy loop without suspension points can keep running until it checks cancellation manually.

When a parent `Job` is canceled, child coroutines also receive cancellation. This is the basis of structured concurrency and the reason work should be launched in the right scope.

Typical pitfalls: launching work in `GlobalScope`, catching `Exception` and swallowing cancellation, not canceling an old `Job` on a new user action, making an infinite loop without `isActive`.

**In short:** coroutine cancellation is cooperative; cancellation propagates through the `Job` hierarchy and works best when code reaches suspension points or checks `isActive`.

### `CancellationException`

`CancellationException` - a special exception used by coroutines to signal normal cancellation.

It should not be handled like a regular error or shown to the user as failure. If `catch` catches `Exception`, avoid accidentally swallowing `CancellationException`.

```kotlin
try {
    repository.load()
} catch (e: CancellationException) {
    throw e
} catch (e: Exception) {
    handleError(e)
}
```

This is especially important in Flow/coroutines chains: swallowed cancellation can break structured concurrency and leave work in an incorrect state.

**In short:** `CancellationException` is a normal control signal for coroutine cancellation and should usually be rethrown, not mapped to a user-facing error.

### Timeout

Timeout limits coroutine execution time. Main APIs: `withTimeout()` and `withTimeoutOrNull()`.

`withTimeout()` throws `TimeoutCancellationException`, which is a `CancellationException`. `withTimeoutOrNull()` returns `null` instead of an exception.

Timeout is useful for network/database/remote operations that should not hang forever. But timeout does not replace a normal error handling strategy and retry policy.

Do not blindly retry all operations: retry fits temporary technical errors, but not business errors such as invalid credentials or validation error. Critical operations need idempotency or status verification.

**In short:** timeout cancels a coroutine if it takes too long; `withTimeout()` throws, `withTimeoutOrNull()` returns `null`, and timeout should be combined with thoughtful error and retry handling.
