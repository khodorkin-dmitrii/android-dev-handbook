# Flow Operators

Flow operators помогают преобразовывать streams, объединять несколько источников, обрабатывать ошибки и управлять retry.

## Transform и combine

### `map` vs `flatMapLatest`

`map` преобразует каждое значение потока один-к-одному: value -> transformed value. Например, `User` -> `UserUiModel`.

`flatMapLatest` нужен, когда каждое входное значение создаёт новый inner `Flow`, и при новом входном значении старый inner `Flow` должен быть отменён.

```kotlin
selectedUserId
    .flatMapLatest { id -> repository.observeUser(id) }
    .map { user -> user.toUiModel() }
```

Если `selectedUserId` изменился, старая подписка `observeUser(oldId)` отменяется и начинается `observeUser(newId)`.

**Коротко:** `map` transforms values, `flatMapLatest` switches to a new inner `Flow` and cancels the previous one.

### `combine` vs `zip`

`combine` объединяет несколько `Flow` и emit-ит новое значение, когда любой источник изменился, используя последние значения остальных источников.

Это часто используют во `ViewModel` для сборки `UiState` из нескольких источников:

```kotlin
combine(userFlow, balanceFlow, cardsFlow) { user, balance, cards ->
    UiState(user, balance, cards)
}
```

`zip` ждёт пару новых emissions: одно значение из первого `Flow` и одно значение из второго `Flow`. Он объединяет значения попарно.

Для UI state чаще подходит `combine`, потому что экран должен обновляться при изменении любого источника. `zip` полезен реже, когда действительно нужны пары значений.

**Коротко:** `combine` reacts to any source using latest values; `zip` waits for paired emissions.

### `merge`

`merge` объединяет несколько `Flow` одного или совместимого типа и просто пропускает emissions из всех источников в один downstream `Flow`.

Он не комбинирует значения между собой и не ждёт пары. Он просто смешивает события по мере их прихода.

Пример использования: объединить `refreshClickFlow`, `retryClickFlow` и `pullToRefreshFlow` в один stream refresh events.

**Важно:** `merge` не сохраняет порядок между разными asynchronous sources в бизнес-смысле; он отдаёт emissions по фактическому приходу.

**Коротко:** `merge` is for listening to multiple independent streams of the same kind as one stream.

## Errors

### `retry` / `retryWhen`

`retry` и `retryWhen` позволяют повторить Flow upstream при ошибке.

`retry` обычно задаёт количество попыток и predicate. `retryWhen` даёт больше контроля: cause, attempt, delay/backoff и дополнительные условия.

```kotlin
flow.retryWhen { cause, attempt ->
    cause is IOException && attempt < 3
}
```

Retry подходит для временных technical errors, например network issue. Не стоит ретраить business errors: invalid credentials, validation error, insufficient permissions.

Для критичных операций вроде payment/transfer нужна idempotency или проверка статуса, потому что повтор может выполнить действие дважды.

**Коротко:** retry is for transient failures, `retryWhen` gives conditional retry logic; do not blindly retry business or critical operations.

### `catch`

`catch` обрабатывает exceptions из upstream `Flow` и может emit-ить fallback/error state.

```kotlin
repository.observeData()
    .map { data -> UiState.Content(data) }
    .catch { e -> emit(UiState.Error(e.toUiMessage())) }
    .collect { state -> render(state) }
```

**Важно:** `catch` ловит ошибки выше по chain, но не ловит ошибки, которые произошли внутри `collect` после `catch`. Для них нужен `try` / `catch` вокруг `collect` или обработка ниже по цепочке.

Не нужно проглатывать `CancellationException` как обычную ошибку. Если `catch` получает cancellation, обычно её нужно rethrow или не маппить в user-facing error.

**Коротко:** `catch` handles upstream `Flow` exceptions; it should map errors intentionally and must not swallow cancellation.
