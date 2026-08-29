# Flow Basics

`Flow<T>` is a coroutine-based stream that can emit values over time and then complete normally or with an exception.

## Flow basics

### What is Flow?

`Flow` is useful when a value can arrive more than once: database updates, search input, UI state, progress, polling, or realtime events. For suspension and coroutine scopes, see [Coroutines Basics](basics.md).

A flow has three main parts:

1. A **producer** emits values.
2. Intermediate operators transform them.
3. A terminal operator starts collection and consumes the result.

```kotlin
fun observeVisibleUsers(): Flow<List<User>> =
    userDao.observeUsers()              // Flow<List<User>>
        .map { users -> users.filter(User::isVisible) }

suspend fun printVisibleUsers() {
    observeVisibleUsers().collect { users ->
        println(users)
    }
}
```

Operators such as `map`, `filter`, `combine`, and `distinctUntilChanged` return a new `Flow`; they do not start it. `collect`, `first`, `single`, and `toList` are terminal operators. Most terminal operators are suspending functions.

Values normally move through a flow sequentially. Operators such as `buffer`, `conflate`, and `flatMapMerge` can change that behavior when concurrency or skipped values are intentional.

### Flow vs suspend function

A suspend function usually returns one result or throws one exception. It fits one-shot operations such as `login()`, `fetchUser()`, or `saveSettings()`.

`Flow` fits when several values may arrive over time: cached data followed by fresh data, database updates, download progress, or a changing device status.

If only one response is needed, a suspend function is usually simpler. Wrapping every single request in `Flow` adds collection and cancellation semantics without a real benefit.

### Cold Flow vs Hot Flow

Most flows created with `flow { ... }`, `flowOf(...)`, or repository transformations are **cold**. Their producer starts for each terminal operation, so two collectors can repeat the upstream work - including two network calls.

```kotlin
val userFlow = flow {
    emit(api.loadUser())
}

userFlow.collect(::renderUser) // Executes api.loadUser()
userFlow.collect(::cacheUser)  // Executes it again
```

A **hot** flow exists independently of a particular collector. `StateFlow` keeps the latest state, while `SharedFlow` broadcasts values according to its replay and buffering configuration.

In Android, a repository's cold flow is often converted to `StateFlow` in a `ViewModel` with `stateIn(...)`. The scope and `SharingStarted` policy then determine how long the shared upstream collection remains active.

`Channel` is also hot, but it is a separate communication primitive rather than a `Flow` subtype. By default, each channel element is handled by one receiver; see [Channels](channels.md).

### Collection, context, and cancellation

`collect` is a suspending terminal operator and runs in the collecting coroutine. A cold flow uses the collector's coroutine context unless its upstream context is changed with `flowOn`. `flowOn` affects only the operators above it; it does not move the collector to another dispatcher.

Collection follows structured concurrency. Cancelling the collecting coroutine also cancels collection and the cold upstream. In Android UI code, collect with lifecycle-aware APIs such as `repeatOnLifecycle` or `collectAsStateWithLifecycle` so work stops when the UI no longer needs it.

Do not swallow `CancellationException` in broad error handling: cancellation is a control signal, not a regular failure.

### Error handling

An unhandled upstream exception completes the flow and is rethrown by the terminal operator. `catch` handles only exceptions from operators placed before it and does not catch cancellation or failures in the downstream `collect` block.

```kotlin
repository.observeUsers()
    .map(::toUiModel)
    .catch { error -> emit(UserUiModel.Error(error)) }
    .collect(::render)
```

Use `catch` for expected recoverable failures or to emit an explicit error state. Unexpected failures should normally be rethrown rather than silently converted into empty data.

### `collect` vs `collectLatest`

`collect` processes every emission to completion. If processing is slow, later values wait unless buffering or concurrent operators change the pipeline.

`collectLatest` cancels the previous collector block when a new value arrives and starts it again with the latest value. This is useful for search-as-you-type, fast filter changes, or rendering work where an older result is obsolete.

Do not use `collectLatest` when every value must be processed, such as audit logging, payments, or critical writes: cancellation may stop the previous block halfway through.
