# Тестирование ViewModel

`ViewModel` тестируют как обычный Kotlin-класс: передают контролируемые зависимости, вызывают публичные действия и проверяют состояние или результат, доступный UI. Цель - проверить контракт UI, а не запуск корутин или вызовы private-методов.

## Настройка теста

### Замена `Dispatchers.Main`

`viewModelScope` использует `Dispatchers.Main`, который недоступен в локальном JVM-тесте. Заменяйте его на `TestDispatcher` и сбрасывайте после каждого теста:

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    val testDispatcher: TestDispatcher = StandardTestDispatcher(),
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

Для тестов с корутинами используйте `runTest`. Все `TestDispatcher` в тесте и его зависимостях должны разделять один `TestCoroutineScheduler`, иначе управление виртуальным временем может выполнить только часть работы. Dispatchers, созданные после `Dispatchers.setMain(testDispatcher)`, могут унаследовать его scheduler; также можно явно передать `testScheduler`.

`StandardTestDispatcher` ставит новые корутины в очередь и даёт точный контроль над выполнением. `UnconfinedTestDispatcher` запускает их сразу и иногда упрощает базовые тесты, но порядок выполнения отличается от production. Если важны порядок или конкуренция, предпочитайте стандартный dispatcher.

### Настройка до создания ViewModel

Настройте fakes до создания `ViewModel`, особенно если работа запускается в `init`:

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class ProfileViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load profile exposes content`() = runTest {
        val repository = FakeProfileRepository(
            result = User("Ada"),
        )
        val viewModel = ProfileViewModel(repository)

        viewModel.load()
        advanceUntilIdle()

        assertEquals(
            ProfileUiState(userName = "Ada"),
            viewModel.uiState.value,
        )
    }
}
```

Используйте `advanceUntilIdle()`, когда по контракту нужно завершить всю запланированную работу. Если важен момент выполнения, применяйте `runCurrent()` или `advanceTimeBy()`. Постоянный вызов `advanceUntilIdle()` может скрыть API, который запускает работу, но не сообщает о её завершении. Когда вызывающей стороне нужно дождаться результата, лучше использовать suspend-функцию, возвращаемый job или наблюдаемое состояние.

## Тестирование UI state

### Итоговое состояние

В большинстве сценариев после завершения действия достаточно проверить текущее `StateFlow.value`. Покройте начальное состояние и важные результаты: content, пустые данные, validation error, repository error, retry и cancellation.

Не проверяйте поля, которые UI не использует. Одна проверка состояния обычно устойчивее, чем проверка точной последовательности вызовов внутри `ViewModel`.

### Переходы состояния

Собирайте emissions только тогда, когда их последовательность является частью UI-контракта, например loading должен быть виден перед асинхронным результатом. Turbine делает collection и завершение явными:

```kotlin
@Test
fun `load exposes loading then error`() = runTest {
    val repository = ControllableProfileRepository()
    val viewModel = ProfileViewModel(repository)

    viewModel.uiState.test {
        assertEquals(ProfileUiState(), awaitItem())

        viewModel.load()

        assertEquals(
            ProfileUiState(isLoading = true),
            awaitItem(),
        )

        repository.completeWithError(IOException())

        assertEquals(
            ProfileUiState(errorMessage = "Network error"),
            awaitItem(),
        )
        cancelAndIgnoreRemainingEvents()
    }
}
```

В этом примере fake приостанавливает запрос до вызова `completeWithError()`, поэтому loading является реально наблюдаемым состоянием, а не случайным результатом работы scheduler.

`StateFlow` использует conflation: медленный collector может пропустить промежуточные значения и всегда получает последнее состояние. Не требуйте в тесте каждое быстрое присваивание, если эти состояния не гарантированно наблюдаемы по дизайну. Если важен только итоговый экран, проверяйте `.value`.

Если `StateFlow` создан через `stateIn(WhileSubscribed(...))`, для запуска upstream может потребоваться активный collector. Поддерживайте фоновую подписку во время теста или тестируйте upstream flow отдельно.

## Тестирование effects и events

Navigation, snackbars и запросы разрешений иногда представлены потоком effects. При использовании `SharedFlow` с `replay = 0` подпишитесь до вызова действия:

```kotlin
@Test
fun `successful save requests navigation back`() = runTest {
    val viewModel = ProfileViewModel(
        FakeProfileRepository(saveSucceeds = true),
    )

    viewModel.effects.test {
        viewModel.onSaveClicked()
        assertEquals(UiEffect.NavigateBack, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

Такой тест также фиксирует семантику доставки. `SharedFlow` без replay может потерять effect при отсутствии collector; буферизованный `Channel` ведёт себя иначе, но тоже не обеспечивает надёжную доставку после смерти процесса. Если результат должен пережить отсутствие подписчика или recreation, представьте его как устойчивое состояние либо используйте явный протокол подтверждения или сохранения.

Проверяйте, что действие создаёт нужный effect и, если это важно, что повторные действия не создают дубликаты. Не тестируйте private-механизм передачи, если он не является частью контракта.

## Saved state и границы теста

Передайте настоящий `SavedStateHandle` с контролируемыми значениями, если `ViewModel` читает navigation arguments или хранит лёгкое восстанавливаемое состояние:

```kotlin
val savedStateHandle = SavedStateHandle(
    mapOf("profileId" to "42"),
)
val viewModel = ProfileViewModel(repository, savedStateHandle)
```

Локальный тест `ViewModel` проверяет чтение и запись handle, а не пересоздание Android-процесса. Если контракт зависит от Navigation, `SavedStateRegistry` или реального lifecycle restoration, нужен integration или instrumented test.

## Связанные темы

- [Стратегия тестирования](strategy.md)
- [Тестирование Coroutines и Flow](coroutines-flow-testing.md)
- [Тестирование Android UI](android-ui-testing.md)
- [Архитектура UI State](../architecture/ui-state.md)
- [StateFlow и SharedFlow](../coroutines-flow/stateflow-sharedflow.md)
