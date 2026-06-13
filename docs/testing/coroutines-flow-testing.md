# Coroutines & Flow Testing

Раздел про тестирование coroutines и `Flow`: virtual time, test dispatchers, `runTest`, collection, cancellation и проверку emissions.

## Coroutines и Flow

### `runTest`

`runTest` - основной API из `kotlinx-coroutines-test` для тестирования suspend-кода и coroutines.

Он создаёт test coroutine scope, поддерживает virtual time, корректно ждёт child coroutines и помогает находить незавершённые jobs. В отличие от `runBlocking`, `runTest` не заставляет тест реально ждать `delay()`.

Пример:

```kotlin
@Test
fun `load returns user`() = runTest {
    val repository = FakeUserRepository()

    val user = repository.loadUser()

    assertEquals("Ada", user.name)
}
```

Если внутри кода есть `delay(1_000)`, `runTest` может пройти его виртуально:

```kotlin
@Test
fun `timer emits after delay`() = runTest {
    var completed = false

    launch {
        delay(1_000)
        completed = true
    }

    assertFalse(completed)
    advanceTimeBy(1_000)
    assertTrue(completed)
}
```

Полезные функции:

- `advanceUntilIdle()` - выполнить всё запланированное до idle state;
- `advanceTimeBy(time)` - продвинуть virtual time;
- `runCurrent()` - выполнить задачи, запланированные на текущее virtual time.

**Важно:** `runTest` контролирует только coroutines, которые используют test scheduler. Если код уходит на реальный `Dispatchers.IO` или создаёт собственные unmanaged threads, тест может снова стать flaky.

**Коротко:** `runTest` даёт controlled coroutine test scope и virtual time, поэтому suspend-код тестируется быстро и предсказуемо.

### `TestDispatcher`

`TestDispatcher` - dispatcher для coroutine tests, который работает с `TestCoroutineScheduler` и позволяет управлять выполнением задач.

Чаще всего используют:

- `StandardTestDispatcher` - задачи запускаются контролируемо, тест явно двигает scheduler через `advanceUntilIdle()`, `runCurrent()` или `advanceTimeBy()`;
- `UnconfinedTestDispatcher` - запускает tasks более eagerly и удобен для некоторых простых tests, но может скрыть ordering issues.

Для `ViewModel` tests часто заменяют `Dispatchers.Main`:

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    val dispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

Хорошая архитектура не хардкодит dispatchers внутри классов. Лучше передавать dispatcher или `DispatcherProvider` через DI:

```kotlin
interface DispatcherProvider {
    val io: CoroutineDispatcher
    val default: CoroutineDispatcher
    val main: CoroutineDispatcher
}
```

В tests можно подставить test dispatchers и не зависеть от реальных threads.

**Коротко:** `TestDispatcher` делает coroutine execution управляемым; для стабильных tests лучше инжектить dispatchers и не хардкодить `Dispatchers.IO` внутри логики.

### Testing Flow

`Flow` тестируют через collection emissions и проверку результата. Для finite flows можно использовать `toList()`, `first()`, `single()`. Для long-running flows удобнее Turbine или ручной collection с cancel.

Пример finite flow:

```kotlin
@Test
fun `flow emits mapped values`() = runTest {
    val values = flowOf(1, 2, 3)
        .map { it * 2 }
        .toList()

    assertEquals(listOf(2, 4, 6), values)
}
```

Пример `StateFlow`:

```kotlin
@Test
fun `state flow emits content`() = runTest {
    val viewModel = ItemsViewModel(FakeItemsRepository())

    viewModel.uiState.test {
        assertEquals(ItemsUiState.Loading, awaitItem())

        viewModel.load()

        assertEquals(ItemsUiState.Content(listOf("A", "B")), awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

Для hot flows важно сначала подписаться, а потом вызывать action, который emit-ит значение. Иначе `SharedFlow` с `replay = 0` может потерять emission.

Также нужно помнить про `StateFlow`: он всегда имеет current value и может не emit-ить новое значение, если оно `equals()` старому.

**Важно:** тест должен завершать collection long-running flow. Иначе test coroutine может зависнуть или `runTest` сообщит о незавершённой работе.

**Коротко:** Flow tests проверяют emissions; для finite flows хватит `toList()` / `first()`, для hot и long-running flows удобнее Turbine или controlled collection с cancellation.

### Почему не использовать `Thread.sleep` в тестах?

`Thread.sleep` в тестах делает suite медленным, flaky и зависимым от скорости машины, CI, нагрузки CPU и реальных threads.

Если тест ждёт "на всякий случай", он либо иногда падает, потому что sleep слишком короткий, либо всегда тормозит, потому что sleep слишком длинный.

В coroutine tests вместо `Thread.sleep` используют virtual time:

```kotlin
@Test
fun `debounce emits latest value`() = runTest {
    val results = mutableListOf<String>()
    val input = MutableSharedFlow<String>()

    val job = launch {
        input
            .debounce(300)
            .toList(results)
    }

    input.emit("a")
    advanceTimeBy(100)
    input.emit("ab")
    advanceTimeBy(300)

    assertEquals(listOf("ab"), results)
    job.cancel()
}
```

Для UI tests вместо sleep лучше использовать idling resources, Compose test synchronization, `mainClock`, explicit assertions with waiting APIs или controlled fake dependencies.

**Коротко:** `Thread.sleep` ждёт реальное время и делает tests нестабильными; coroutine tests должны использовать virtual time, а UI tests - synchronization mechanisms.
