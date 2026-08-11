# Coroutine Scopes & Cancellation

Coroutine scope задаёт lifetime асинхронной работы. Cancellation останавливает эту работу, когда её owner больше не активен или когда новая операция заменяет старую.

В Android главный вопрос не только “как запустить coroutine?”, а “кто владеет этой работой и когда она должна остановиться?”.

## Выбирайте scope по владельцу

Coroutine должна запускаться в scope, который совпадает с lifetime работы:

- `viewModelScope` - состояние экрана и user actions, которыми владеет `ViewModel`;
- `lifecycleScope` - работа, которой владеет `Activity` или `Fragment`;
- `repeatOnLifecycle` / lifecycle-aware collection - UI collection, которая должна стартовать и останавливаться вместе с lifecycle state;
- `coroutineScope` - child work, которой владеет текущая suspend operation;
- `WorkManager` - deferrable work, которая должна жить дольше UI.

Не выбирайте scope только потому, что к нему легко обратиться. Lifetime определяет owner.

```kotlin
class ProfileViewModel(
    private val repository: ProfileRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            try {
                val profile = repository.loadProfile(userId)
                _uiState.update {
                    it.copy(isLoading = false, profile = profile)
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(isLoading = false, error = UiError.Network)
                }
            }
        }
    }
}
```

Здесь работа принадлежит `ViewModel`. Когда `ViewModel` будет очищена, запущенная coroutine отменится.

## Structured concurrency

Structured concurrency означает, что child coroutines запускаются внутри parent scope. Parent может ждать их завершения, отменять их и предсказуемо распространять ошибки.

Это не даёт async work “утекать” за пределы владельца. Если screen, request или use case завершён, связанная child work тоже должна завершиться или отмениться.

```kotlin
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val user = async { api.getUser() }
    val cards = async { api.getCards() }

    Dashboard(
        user = user.await(),
        cards = cards.await(),
    )
}
```

В `coroutineScope`, если один child падает, sibling coroutines отменяются, а ошибка уходит выше. Для all-or-nothing работы это обычно правильное поведение.

`GlobalScope` в Android обычно считается smell: у coroutine нет понятного owner, её сложнее отменять, тестировать и анализировать.

## `Job` и cancellation hierarchy

`Job` представляет cancellable coroutine work. Scope содержит `Job`, а child coroutines образуют под ним иерархию.

Когда parent `Job` отменяется, его children тоже отменяются.

```kotlin
val job = viewModelScope.launch {
    repository.sync()
}

job.cancel()
```

Ручное хранение `Job` полезно, когда новое user action заменяет старую операцию:

```kotlin
private var searchJob: Job? = null

fun onQueryChanged(query: String) {
    searchJob?.cancel()

    searchJob = viewModelScope.launch {
        val result = repository.search(query)
        _uiState.update { it.copy(result = result) }
    }
}
```

Для поиска на Flow такое поведение часто чище выражается через `flatMapLatest`.

## `coroutineScope` vs `supervisorScope`

Используйте `coroutineScope`, когда child tasks относятся к одной all-or-nothing operation. Ошибка одного child отменяет остальные.

Используйте `supervisorScope`, когда child tasks независимы и допустим partial success.

```kotlin
suspend fun loadBlocks(): Blocks = supervisorScope {
    val news = async { runCatching { api.getNews() } }
    val banners = async { runCatching { api.getBanners() } }

    Blocks(
        news = news.await().getOrDefault(emptyList()),
        banners = banners.await().getOrDefault(emptyList()),
    )
}
```

`supervisorScope` не означает “игнорировать exceptions”. Он только меняет propagation ошибок между children. Ошибку каждого child всё равно нужно обработать явно, если она не должна потеряться.

`SupervisorJob` даёт похожую supervision-семантику на уровне `Job`. Android `viewModelScope` использует supervision внутри, поэтому падение одной child coroutine не должно отменить весь `ViewModel` scope. Но это всё равно не заменяет error handling.

## `viewModelScope`

`viewModelScope` привязан к `ViewModel` и отменяется при вызове `onCleared()`.

Используйте его для screen-level async work:

- загрузка данных экрана;
- обработка user actions;
- обновление `StateFlow` и `SharedFlow`;
- вызовы repositories или use cases;
- координация UI state.

`viewModelScope` не переживает process death и не предназначен для гарантированной background execution. Для надёжной deferrable work, которая должна продолжаться вне UI lifetime, используйте `WorkManager`.

`viewModelScope` по умолчанию использует main dispatcher. Тяжёлую CPU или I/O работу лучше переносить в repository/use case и там осознанно переключать dispatcher:

```kotlin
suspend fun parseLargeFile(file: File): ParsedData =
    withContext(Dispatchers.Default) {
        parser.parse(file)
    }
```

## Cooperative cancellation

Coroutine cancellation кооперативная. Coroutine не “убивается” мгновенно на произвольной инструкции. Она должна дойти до cancellable suspension point или явно проверить cancellation.

Обычно cancellation поддерживают:

- `delay()`;
- `withContext()`;
- Flow collection и operators;
- многие network/database calls, если библиотека это поддерживает;
- `withTimeout()`.

CPU-heavy loops должны проверять cancellation вручную:

```kotlin
suspend fun calculate(items: List<Item>): Result =
    withContext(Dispatchers.Default) {
        val builder = ResultBuilder()

        for (item in items) {
            ensureActive()
            builder.add(process(item))
        }

        builder.build()
    }
```

Типичные ошибки:

- использовать `GlobalScope` для обычной app work;
- ловить `Exception` и проглатывать `CancellationException`;
- запускать долгий CPU loop без `ensureActive()` или suspension points;
- не отменять старую работу, когда новое user action заменяет её;
- показывать cancellation пользователю как ошибку.

## `CancellationException`

`CancellationException` - это нормальный control signal для coroutine cancellation. Не обрабатывайте его как обычную ошибку.

Если вы ловите `Exception`, сначала rethrow `CancellationException`:

```kotlin
try {
    repository.load()
} catch (e: CancellationException) {
    throw e
} catch (e: IOException) {
    showNetworkError()
} catch (e: Exception) {
    showUnexpectedError()
}
```

То же правило работает для Flow:

```kotlin
flow
    .catch { e ->
        if (e is CancellationException) throw e
        emit(UiState.Error)
    }
    .collect { state ->
        render(state)
    }
```

Если проглотить cancellation, можно сломать structured concurrency и удерживать работу дольше, чем нужно.

## Cleanup и timeout

Используйте `try/finally`, когда нужно закрыть ресурсы или сбросить временный UI state после cancellation.

```kotlin
viewModelScope.launch {
    _uiState.update { it.copy(isLoading = true) }

    try {
        repository.refresh()
    } finally {
        _uiState.update { it.copy(isLoading = false) }
    }
}
```

Если cleanup сам должен вызвать suspend function после cancellation, оберните только эту маленькую cleanup-часть в `NonCancellable`:

```kotlin
try {
    uploadFile()
} finally {
    withContext(NonCancellable) {
        repository.markUploadFinished()
    }
}
```

Используйте `NonCancellable` осторожно. Он задерживает cancellation и не должен оставлять обычную business work жить после отмены owner.

Используйте `withTimeout()` или `withTimeoutOrNull()`, чтобы ограничить время выполнения:

```kotlin
val config = withTimeoutOrNull(10_000) {
    repository.fetchRemoteConfig()
}
```

`withTimeout()` бросает `TimeoutCancellationException`, subtype `CancellationException`. Timeout нужно сочетать с понятным error mapping и аккуратной retry policy. Не retry-те вслепую validation errors, payments или операции, которые могут создать duplicate effects.

## Практические Android-правила

- Выбирайте scope по lifetime владельца работы.
- Используйте `viewModelScope` для screen work, которой владеет `ViewModel`.
- Используйте lifecycle-aware APIs для UI collection.
- Используйте `WorkManager` для надёжной deferrable background work.
- Используйте `coroutineScope` для all-or-nothing parallel work.
- Используйте `supervisorScope` для независимых child tasks с partial success.
- Избегайте `GlobalScope` в обычном app code.
- Rethrow `CancellationException`.
- Добавляйте cancellation checks в CPU-heavy loops.
- Делайте cleanup маленьким и явным.

## Связанные темы

- [Coroutines Basics](basics.md)
- [Flow Basics](flow-basics.md)
- [Lifecycle-aware Collection](lifecycle-aware-collection.md)
- [UI State Architecture](../architecture/ui-state.md)
