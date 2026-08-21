# Coroutine Scopes & Cancellation

Coroutine scope defines the lifetime of asynchronous work. Cancellation stops that work when its owner is gone, or when a newer operation replaces it.

In Android, the key question is not just “how do I launch a coroutine?”, but “who owns this work, and when should it stop?”

## Choose scope by owner

A coroutine should run in a scope that matches the lifetime of the work:

- `viewModelScope` - screen state and user actions owned by a `ViewModel`;
- `lifecycleScope` - work owned by an `Activity` or `Fragment`;
- `repeatOnLifecycle` / lifecycle-aware collection - UI collection that should start and stop with lifecycle state;
- `coroutineScope` - child work owned by the current suspend operation;
- `WorkManager` - deferrable work that must outlive the UI.

Avoid choosing a scope just because it is easy to access. The owner determines the lifetime.

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

Here the work belongs to the `ViewModel`. When the `ViewModel` is cleared, the running coroutine is cancelled.

## Structured concurrency

Structured concurrency means child coroutines are launched inside a parent scope. The parent can wait for them, cancel them, and propagate failures in a predictable way.

This prevents asynchronous work from leaking outside its owner. If a screen, request, or use case is finished, related child work should also finish or be cancelled.

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

With `coroutineScope`, if one child fails, sibling coroutines are cancelled and the error is propagated upward. This is usually correct for all-or-nothing work.

`GlobalScope` is usually a smell in Android code because the coroutine has no clear owner. It is harder to cancel, test, and reason about.

## `Job` and cancellation hierarchy

A `Job` represents cancellable coroutine work. A scope contains a `Job`, and child coroutines form a hierarchy under it.

When a parent `Job` is cancelled, its children are cancelled too.

```kotlin
val job = viewModelScope.launch {
    repository.sync()
}

job.cancel()
```

Manual `Job` tracking is useful when a new user action replaces an old operation:

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

For Flow-based search, `flatMapLatest` often expresses the same replacement behavior more cleanly.

## `coroutineScope` vs `supervisorScope`

Use `coroutineScope` when child tasks belong to one all-or-nothing operation. Failure of one child cancels the others.

Use `supervisorScope` when child tasks are independent and partial success is valid.

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

`supervisorScope` does not mean “ignore exceptions”. It only changes failure propagation between children. Each failing child still needs explicit handling if the error should not be lost.

`SupervisorJob` has similar supervision semantics at the `Job` level. Android `viewModelScope` uses supervision internally, so failure of one launched child coroutine should not cancel the whole `ViewModel` scope. It still does not replace proper error handling.

## `viewModelScope`

`viewModelScope` is tied to a `ViewModel` and is cancelled when `onCleared()` is called.

Use it for screen-level asynchronous work:

- loading screen data;
- handling user actions;
- updating `StateFlow` and `SharedFlow`;
- calling repositories or use cases;
- coordinating UI state.

`viewModelScope` does not survive process death and is not a tool for guaranteed background execution. Use `WorkManager` for reliable deferrable work that must continue outside the UI lifetime.

`viewModelScope` uses the main dispatcher by default. Heavy CPU or I/O work should switch dispatcher inside the appropriate repository or use case:

```kotlin
suspend fun parseLargeFile(file: File): ParsedData =
    withContext(Dispatchers.Default) {
        parser.parse(file)
    }
```

## Cooperative cancellation

Coroutine cancellation is cooperative. A coroutine is not killed immediately at an arbitrary instruction. It must reach a cancellable suspension point or check cancellation explicitly.

Common cancellable points include:

- `delay()`;
- `withContext()`;
- Flow collection and operators;
- many network/database calls when the library supports cancellation;
- `withTimeout()`.

CPU-heavy loops should check cancellation manually:

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

Typical mistakes:

- using `GlobalScope` for regular app work;
- catching `Exception` and swallowing `CancellationException`;
- running a long CPU loop without `ensureActive()` or suspension points;
- not cancelling old work when a newer user action replaces it;
- showing cancellation as a user-visible error.

## `CancellationException`

`CancellationException` is the normal control signal for coroutine cancellation. Do not treat it as a regular failure.

If you catch `Exception`, rethrow `CancellationException` first:

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

The same rule applies to Flow:

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

Swallowing cancellation can break structured concurrency and keep work alive longer than expected.

## Cleanup and timeout

Use `try/finally` when resources must be closed or temporary UI state must be reset after cancellation.

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

If cleanup itself must call a suspend function after cancellation, wrap only that small cleanup part with `NonCancellable`:

```kotlin
try {
    uploadFile()
} finally {
    withContext(NonCancellable) {
        repository.markUploadFinished()
    }
}
```

Use `NonCancellable` carefully. It delays cancellation and should not keep ordinary business work alive after the owner was cancelled.

Use `withTimeout()` or `withTimeoutOrNull()` to limit execution time:

```kotlin
val config = withTimeoutOrNull(10_000) {
    repository.fetchRemoteConfig()
}
```

`withTimeout()` throws `TimeoutCancellationException`, a subtype of `CancellationException`. Timeout should be combined with clear error mapping and a careful retry policy. Do not blindly retry validation errors, payments, or operations that may create duplicate effects.

## Practical Android rules

- Choose the scope by the lifetime of the work owner.
- Use `viewModelScope` for `ViewModel`-owned screen work.
- Use lifecycle-aware APIs for UI collection.
- Use `WorkManager` for reliable deferrable background work.
- Use `coroutineScope` for all-or-nothing parallel work.
- Use `supervisorScope` for independent child tasks with partial success.
- Avoid `GlobalScope` in regular app code.
- Rethrow `CancellationException`.
- Add cancellation checks to CPU-heavy loops.
- Keep cleanup small and explicit.

## Related topics

- [Coroutines Basics](basics.md)
- [Flow Basics](flow-basics.md)
- [Channels](channels.md)
- [Lifecycle-aware Collection](lifecycle-aware-collection.md)
- [UI State Architecture](../architecture/ui-state.md)
