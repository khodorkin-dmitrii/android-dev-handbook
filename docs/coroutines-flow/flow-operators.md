# Flow Operators

Flow operators build a pipeline between producer and collector. The important choice is not which operator is shortest, but what should happen to ordering, cancellation, errors, and slow consumers.

For cold and hot flow semantics, collection, and context, see [Flow Basics](flow-basics.md).

## Transform and filter

Most intermediate operators are lazy: they return a new `Flow` and run only when a terminal operator collects it.

| Intent | Operator |
| --- | --- |
| Transform every value | `map` |
| Keep matching values | `filter` / `filterNotNull` |
| Skip consecutive equal values | `distinctUntilChanged` |
| Perform a side effect without changing the value | `onEach` |
| Keep or skip a limited part of the stream | `take`, `drop`, `takeWhile` |

```kotlin
userDao.observeUsers()
    .map { users -> users.filter(User::isVisible) }
    .distinctUntilChanged()
    .onEach { users -> analytics.logVisibleCount(users.size) }
```

`distinctUntilChanged` compares consecutive values with `equals`. Applying it directly to `StateFlow` is redundant because `StateFlow` already suppresses equal consecutive values.

### `map` vs `flatMapLatest`

Use `map` when one input produces one output, including when the transformation calls a suspend function.

Use a `flatMap*` operator when each input produces another `Flow`:

| Operator | Inner flows |
| --- | --- |
| `flatMapConcat` | collects sequentially and preserves order |
| `flatMapMerge` | collects concurrently; results can interleave |
| `flatMapLatest` | cancels the previous inner flow when a new input arrives |

```kotlin
selectedUserId
    .distinctUntilChanged()
    .flatMapLatest(repository::observeUser)
    .map(User::toUiModel)
```

This models “observe the currently selected user”: changing the ID cancels the obsolete subscription. Do not use `flatMapLatest` when every inner operation must finish, such as a critical write.

## Combine several flows

`combine`, `zip`, and `merge` solve different problems:

| Operator | Result |
| --- | --- |
| `combine` | after every source has emitted once, recomputes when any source changes using the latest values |
| `zip` | pairs values by position and completes when either source completes |
| `merge` | forwards values from compatible flows as they arrive, without cross-source ordering guarantees |

`combine` is usually the right choice for building UI state:

```kotlin
combine(userFlow, balanceFlow, cardsFlow) { user, balance, cards ->
    UiState(user, balance, cards)
}
```

Use `zip` only when values form real pairs, not merely because two sources exist. Use `merge` for equivalent events, for example refresh button clicks and pull-to-refresh gestures.

## Timing and slow collectors

Search input commonly uses two operators together:

```kotlin
queryFlow
    .debounce(300)
    .distinctUntilChanged()
    .flatMapLatest(repository::search)
```

`debounce` emits a value after the source stays quiet for the configured interval. It reduces requests during fast input but deliberately adds latency.

Flows are sequential by default, so a slow downstream operator can suspend upstream. Choose an explicit policy only when needed:

| Operator | Slow-consumer behavior |
| --- | --- |
| `buffer` | lets upstream and downstream overlap; retains values until capacity is full |
| `conflate` | skips intermediate values while keeping the latest one |
| `collectLatest` | cancels the previous collector block for the newest value |

`conflate` and `collectLatest` are suitable only when old values become obsolete. They are unsafe for logs, payments, commands, or other streams where every value matters.

## Errors, retry, and completion

`retry` and `retryWhen` restart the upstream flow after a matching failure. `retryWhen` also exposes the zero-based retry attempt and can suspend for backoff:

```kotlin
repository.observeData()
    .retryWhen { cause, attempt ->
        if (cause !is IOException || attempt >= 3) return@retryWhen false
        delay(500L * (1L shl attempt.toInt()))
        true
    }
    .map(Data::toUiState)
    .catch { error -> emit(UiState.Error(error)) }
```

Operator order matters: `retryWhen` must be before `catch`, because `catch` handles the failure instead of rethrowing it. Both operators are transparent to downstream failures and cancellation.

Retry only transient, idempotent work. A payment or write can run twice unless the operation has an idempotency key or its result is verified.

`onStart` can emit a loading state before upstream begins. `onCompletion` observes normal completion, failure, or cancellation; unlike `catch`, it does not handle an exception by itself.

## Terminal operators

Terminal operators start collection:

| Need | Operator |
| --- | --- |
| Process every value | `collect` |
| Get the first value and cancel upstream | `first` / `firstOrNull` |
| Require exactly one value | `single` / `singleOrNull` |
| Accumulate a finite flow | `toList` |
| Collect in a supplied scope | `launchIn` |

Do not call `toList` or `single` on a hot or otherwise non-terminating flow: they wait for completion that may never happen.
