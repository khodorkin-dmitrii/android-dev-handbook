# Coroutine Scopes & Cancellation

Coroutine scope задаёт lifecycle асинхронной работы, а cancellation позволяет безопасно остановить работу, когда owner больше не нужен.

## Scopes

### Structured concurrency

Structured concurrency означает, что coroutines запускаются внутри `CoroutineScope` и связаны с его lifecycle. Parent scope знает о child coroutines, ждёт их завершения и может отменить их вместе.

Идея в том, чтобы async work не "утекала" в никуда: если screen, request или use case завершён, связанные coroutines тоже должны быть завершены или отменены.

В Android это особенно важно для `ViewModel`, lifecycle-aware UI collection и долгих операций. `GlobalScope` обычно считается smell, потому что coroutine живёт вне понятного owner и её сложнее отменять и тестировать.

**Коротко:** structured concurrency keeps coroutines scoped, cancellable and tied to a clear lifecycle instead of launching unmanaged background work.

### `coroutineScope` vs `supervisorScope`

`coroutineScope` создаёт новый scope внутри suspend-функции и suspend-ится, пока все child coroutines не завершатся. Если один child падает с exception, scope отменяет остальные children и пробрасывает ошибку выше.

`supervisorScope` похож, но изолирует ошибки children: падение одной child coroutine не отменяет siblings автоматически. Это полезно, когда задачи независимы и UI может показать частичный результат.

`coroutineScope` подходит, когда нужен all-or-nothing результат. `supervisorScope` подходит, когда блоки экрана или независимые запросы могут завершаться отдельно.

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

Если `getUser()` упадёт, `getCards()` будет отменён. Для независимых блоков можно использовать `supervisorScope` и обработать ошибки каждого `async` отдельно.

**Коротко:** `coroutineScope` fails fast and cancels siblings, `supervisorScope` lets sibling coroutines fail independently.

### `viewModelScope`

`viewModelScope` - это `CoroutineScope`, привязанный к `ViewModel`. Он автоматически отменяется, когда `ViewModel` получает `onCleared()`.

Его используют для screen-level async работы: загрузка данных, обработка user actions, обновление `StateFlow` / `SharedFlow`, запуск repository calls и orchestration UI state.

**Важно:** `viewModelScope` не переживает уничтожение `ViewModel` при process death и не подходит для гарантированной фоновой работы. Для deferrable reliable background work лучше `WorkManager`.

Внутри `viewModelScope` по умолчанию используется Main dispatcher, поэтому тяжёлую CPU/I/O работу нужно переносить в repository/use case или переключать dispatcher осознанно.

**Коротко:** `viewModelScope` is the lifecycle-aware scope for `ViewModel` work; it is cancelled when the `ViewModel` is cleared.

## Cancellation

### Cancellation

Cancellation в coroutines кооперативная: coroutine не "убивается" мгновенно в произвольной точке. Она должна дойти до suspension point или сама проверить `isActive` / `ensureActive()`.

Обычные suspend-функции вроде `delay()`, `withContext()`, Flow collection и многие network/database APIs умеют реагировать на cancellation. CPU-heavy loop без suspension points может продолжать работать, пока не проверит cancellation вручную.

Когда parent `Job` отменяется, child coroutines тоже получают cancellation. Это основа structured concurrency и причина, почему важно запускать работу в правильном scope.

Типичные pitfalls: запускать работу в `GlobalScope`, ловить `Exception` и проглатывать cancellation, не отменять старый `Job` при новом user action, делать бесконечный loop без `isActive`.

**Коротко:** coroutine cancellation is cooperative; cancellation propagates through the `Job` hierarchy and works best when code reaches suspension points or checks `isActive`.

### `CancellationException`

`CancellationException` - специальное исключение, которым coroutines сигнализируют нормальную отмену.

Его не нужно обрабатывать как обычную ошибку и показывать пользователю как failure. Если `catch` ловит `Exception`, важно не проглотить `CancellationException` случайно.

```kotlin
try {
    repository.load()
} catch (e: CancellationException) {
    throw e
} catch (e: Exception) {
    handleError(e)
}
```

Это особенно важно в Flow/coroutines chains: проглоченная cancellation может сломать structured concurrency и оставить работу в некорректном состоянии.

**Коротко:** `CancellationException` is a normal control signal for coroutine cancellation and should usually be rethrown, not mapped to a user-facing error.

### Timeout

Timeout ограничивает время выполнения coroutine. Основные APIs: `withTimeout()` и `withTimeoutOrNull()`.

`withTimeout()` бросает `TimeoutCancellationException`, который является `CancellationException`. `withTimeoutOrNull()` возвращает `null` вместо exception.

Timeout полезен для network/database/remote operations, которые не должны висеть бесконечно. Но timeout не заменяет нормальную error handling стратегию и retry policy.

Важно не ретраить бездумно все операции: retry подходит для временных technical errors, но не для business errors вроде invalid credentials или validation error. Для критичных операций нужна idempotency или проверка статуса.

**Коротко:** timeout cancels a coroutine if it takes too long; `withTimeout()` throws, `withTimeoutOrNull()` returns `null`, and timeout should be combined with thoughtful error and retry handling.
