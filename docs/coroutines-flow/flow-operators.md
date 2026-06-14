# Flow Operators

Flow operators help transform streams, combine several sources, handle errors and manage retry.

## Transform and combine

### `map` vs `flatMapLatest`

`map` transforms each stream value one-to-one: value -> transformed value. For example, `User` -> `UserUiModel`.

`flatMapLatest` is needed when each input value creates a new inner `Flow`, and when a new input value arrives, the old inner `Flow` should be canceled.

```kotlin
selectedUserId
    .flatMapLatest { id -> repository.observeUser(id) }
    .map { user -> user.toUiModel() }
```

If `selectedUserId` changes, the old `observeUser(oldId)` subscription is canceled and `observeUser(newId)` starts.

**In short:** `map` transforms values, `flatMapLatest` switches to a new inner `Flow` and cancels the previous one.

### `combine` vs `zip`

`combine` combines several `Flow`s and emits a new value whenever any source changes, using the latest values from the other sources.

This is often used in `ViewModel` to build `UiState` from several sources:

```kotlin
combine(userFlow, balanceFlow, cardsFlow) { user, balance, cards ->
    UiState(user, balance, cards)
}
```

`zip` waits for a pair of new emissions: one value from the first `Flow` and one value from the second `Flow`. It combines values pairwise.

For UI state, `combine` is usually a better fit because the screen should update when any source changes. `zip` is useful less often, when paired values are truly needed.

**In short:** `combine` reacts to any source using latest values; `zip` waits for paired emissions.

### `merge`

`merge` combines several `Flow`s of the same or compatible type and simply passes emissions from all sources into one downstream `Flow`.

It does not combine values with each other and does not wait for pairs. It simply mixes events as they arrive.

Example use case: combine `refreshClickFlow`, `retryClickFlow` and `pullToRefreshFlow` into one stream of refresh events.

**Important:** `merge` does not preserve order between different asynchronous sources in a business sense; it emits values by actual arrival.

**In short:** `merge` is for listening to multiple independent streams of the same kind as one stream.

## Errors

### `retry` / `retryWhen`

`retry` and `retryWhen` allow repeating Flow upstream on error.

`retry` usually defines the number of attempts and predicate. `retryWhen` gives more control: cause, attempt, delay/backoff and additional conditions.

```kotlin
flow.retryWhen { cause, attempt ->
    cause is IOException && attempt < 3
}
```

Retry fits temporary technical errors, for example network issue. Do not retry business errors: invalid credentials, validation error, insufficient permissions.

Critical operations such as payment/transfer need idempotency or status verification, because retry can perform the action twice.

**In short:** retry is for transient failures, `retryWhen` gives conditional retry logic; do not blindly retry business or critical operations.

### `catch`

`catch` handles exceptions from upstream `Flow` and can emit fallback/error state.

```kotlin
repository.observeData()
    .map { data -> UiState.Content(data) }
    .catch { e -> emit(UiState.Error(e.toUiMessage())) }
    .collect { state -> render(state) }
```

**Important:** `catch` catches errors above it in the chain, but does not catch errors that happen inside `collect` after `catch`. Those need `try` / `catch` around `collect` or handling lower in the chain.

Do not swallow `CancellationException` as a regular error. If `catch` receives cancellation, usually rethrow it or do not map it to a user-facing error.

**In short:** `catch` handles upstream `Flow` exceptions; it should map errors intentionally and must not swallow cancellation.
