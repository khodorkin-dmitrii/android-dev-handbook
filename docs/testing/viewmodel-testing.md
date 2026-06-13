# ViewModel Testing

Раздел про тестирование `ViewModel`: проверку state transitions, user actions, loading/error/content состояний и одноразовых events/effects.

## ViewModel tests

### Как тестировать ViewModel?

`ViewModel` обычно тестируют как обычный Kotlin-класс: создают fake dependencies, вызывают public actions и проверяют observable output - чаще всего `StateFlow<UiState>` и поток events/effects.

Главная цель - проверить поведение, а не внутреннюю реализацию. Тест должен отвечать на вопрос: "если пользователь сделал действие или repository вернул результат, какой state/effect увидит UI?"

Обычно в тесте нужны:

- fake repository/use case;
- test dispatcher для coroutines;
- замена `Dispatchers.Main`, если `ViewModel` использует `viewModelScope`;
- проверка initial state, state transitions и one-off events.

Пример правила для подмены Main dispatcher:

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

Пример теста:

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class ProfileViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val repository = FakeProfileRepository()

    @Test
    fun `load profile shows content`() = runTest {
        repository.result = User("Ada")
        val viewModel = ProfileViewModel(repository)

        viewModel.load()
        advanceUntilIdle()

        assertEquals(
            ProfileUiState(isLoading = false, userName = "Ada"),
            viewModel.uiState.value
        )
    }
}
```

**Важно:** если `ViewModel` стартует загрузку в `init`, fake dependencies нужно настроить до создания `ViewModel`, иначе тест может проверить не тот сценарий.

**Коротко:** тестируй `ViewModel` через public actions и observable state/effects, используя fakes и test dispatchers вместо реальных network/database dependencies.

### Testing UiState transitions

UiState transitions - это последовательность состояний, через которые проходит экран: например initial -> loading -> content или initial -> loading -> error.

Для простых synchronous сценариев достаточно проверить финальный `uiState.value`. Но если важна сама последовательность, нужно collect-ить emissions.

Пример с ручным collection:

```kotlin
@Test
fun `load emits loading then content`() = runTest {
    val repository = FakeProfileRepository(result = User("Ada"))
    val viewModel = ProfileViewModel(repository)

    val states = mutableListOf<ProfileUiState>()
    val job = launch {
        viewModel.uiState.toList(states)
    }

    viewModel.load()
    advanceUntilIdle()

    assertEquals(
        listOf(
            ProfileUiState(),
            ProfileUiState(isLoading = true),
            ProfileUiState(isLoading = false, userName = "Ada")
        ),
        states.take(3)
    )

    job.cancel()
}
```

На практике для `Flow` и `StateFlow` часто используют библиотеку Turbine, потому что она делает assertions по emissions удобнее и читабельнее:

```kotlin
@Test
fun `load emits loading then error`() = runTest {
    val repository = FakeProfileRepository(error = IOException())
    val viewModel = ProfileViewModel(repository)

    viewModel.uiState.test {
        assertEquals(ProfileUiState(), awaitItem())

        viewModel.load()

        assertEquals(ProfileUiState(isLoading = true), awaitItem())
        assertEquals(ProfileUiState(errorMessage = "Network error"), awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

**Важно:** не делай state test слишком завязанным на каждую промежуточную мелочь, если это не часть contract экрана. Иногда достаточно проверить финальный user-visible state.

**Коротко:** state transition tests полезны для loading/content/error, retry, validation и complex flows, но проверять нужно observable UI contract, а не внутренние шаги implementation.

### Testing events/effects

Events/effects - это одноразовые команды для UI: navigation, snackbar, toast, permission request, scroll command. Их обычно публикуют через `SharedFlow`, `Channel` или callback.

Тест должен проверить, что при конкретном action `ViewModel` отправляет нужный effect, и что durable `UiState` не используется как одноразовая команда.

Пример с `SharedFlow`:

```kotlin
@Test
fun `save success emits navigate back event`() = runTest {
    val repository = FakeProfileRepository(saveResult = Result.success(Unit))
    val viewModel = ProfileViewModel(repository)

    viewModel.events.test {
        viewModel.onSaveClicked()
        assertEquals(UiEvent.NavigateBack, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

Если используется `Channel`, наружу часто отдают `receiveAsFlow()`:

```kotlin
private val _events = Channel<UiEvent>(Channel.BUFFERED)
val events = _events.receiveAsFlow()
```

Тестируется это так же как обычный `Flow`.

**Важно:** event tests часто зависят от буфера. `MutableSharedFlow` с `replay = 0` может потерять событие, если collector ещё не подписан. В тесте сначала запускай collection, потом вызывай action.

**Коротко:** one-off events тестируют через collection event stream: сначала подписка, потом action, затем assertion на конкретный effect.
