# Flow Basics

`Flow` - a coroutine-based data stream that allows describing multiple asynchronous values over time.

## Flow basics

### What is Flow?

`Flow` - an asynchronous data stream from Kotlin Coroutines that can emit several values over time.

A regular `Flow` is cold by default: code inside `flow { ... }` does not start until it is collected.

`Flow` is used to observe changes: database updates, search input, UI state, realtime updates, polling, websocket-like streams and combining several data sources.

```kotlin
fun observeUser(id: String): Flow<User> = flow {
    emit(api.getUser(id))
}
```

**In short:** `Flow` is a coroutine-based asynchronous stream; by default it is cold and starts when collected.

### Flow vs suspend function

Suspend function usually returns one result or one error. It fits one-shot operations well: `login()`, `fetchUser()`, `saveSettings()`, `sendAnalytics()`.

`Flow` fits when there can be several values over time: first cached data, then fresh data, then database updates or realtime status updates.

If one response is needed, suspend function is usually simpler and clearer. If an update stream or reactive chain is needed, use `Flow`.

Typical pitfall: using `Flow` for a simple single request and complicating the API without real benefit.

**In short:** `suspend` is for a single asynchronous result, `Flow` is for multiple values over time.

### Cold Flow vs Hot Flow

Cold Flow starts work only on collection. Each new collector usually restarts the upstream.

For example, if there is `flow { api.load() }`, two collectors may trigger two separate API calls.

Hot Flow exists independently of a specific collector and can store or emit values even without active subscribers. `StateFlow` and `SharedFlow` are hot flows.

`Channel` is also hot, but it is a separate point-to-point communication primitive rather than a Flow subtype. Each element is received by one receiver; see [Channels](channels.md).

In Android, a cold flow from a repository is often converted to hot `StateFlow` in `ViewModel` through `stateIn(viewModelScope, SharingStarted.WhileSubscribed(...), initialValue)`, so UI gets stable state and upstream does not start chaotically.

**In short:** cold flows are started by collectors, hot flows live independently of collectors.

### `collect` vs `collectLatest`

`collect` processes every value to completion. If a new value arrives, it waits until previous processing is finished.

`collectLatest` cancels processing of the previous value when a new one arrives. This is useful when the old result is no longer relevant.

Typical examples of `collectLatest`: search-as-you-type, fast filter changes, UI updates where only the latest input matters.

**Important:** `collectLatest` cancels the collection body, so it must not be used where every value must be processed, for example audit/logging/critical write operation.

**In short:** `collect` processes every emission, `collectLatest` cancels previous processing when a new value arrives.
