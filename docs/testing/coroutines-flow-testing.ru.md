# Тестирование Coroutines и Flow

В coroutine tests нужно контролировать порядок выполнения, виртуальное время и завершение работы. При тестировании Flow также нужна явная стратегия collection, потому что поток может быть cold, hot, конечным или бесконечным.

## Тестирование coroutines

### `runTest` и виртуальное время

`runTest` - основная точка входа из `kotlinx-coroutines-test`. Он создаёт `TestScope`, использует `TestDispatcher`, пропускает задержки под управлением scheduler и перед завершением ждёт дочерние корутины.

```kotlin
@Test
fun `timer completes after one second`() = runTest {
    var completed = false

    launch {
        delay(1_000)
        completed = true
    }

    runCurrent()
    assertFalse(completed)

    advanceTimeBy(1_000)
    runCurrent()

    assertTrue(completed)
}
```

`advanceTimeBy(1_000)` продвигает виртуальное время и выполняет работу, запланированную до целевой отметки. Затем `runCurrent()` выполняет задачи, назначенные точно на текущее время. Другие полезные операции:

- `runCurrent()` - выполнить задачи на текущей отметке виртуального времени;
- `advanceTimeBy(duration)` - продвинуть виртуальное время на указанный интервал;
- `advanceUntilIdle()` - выполнять запланированную работу, пока очередь не опустеет.

Используйте самую узкую операцию, выражающую ожидание теста. Повсеместный `advanceUntilIdle()` может скрыть, какой именно шаг должен завершить работу.

`runTest` контролирует только корутины, использующие его `TestCoroutineScheduler`. Реальные dispatchers, неуправляемые scopes и потоки остаются за пределами виртуального времени и могут сделать тест медленным или flaky.

### Test dispatchers и единый scheduler

Два основных dispatcher имеют разное поведение:

- `StandardTestDispatcher` ставит новые корутины в очередь и оставляет управление тесту. Это хороший вариант по умолчанию, который делает предположения о порядке заметными.
- `UnconfinedTestDispatcher` сразу запускает новую корутину до первой приостановки. Он упрощает некоторые тесты collection, но не воспроизводит production ordering.

Все `TestDispatcher` внутри одного теста должны разделять один scheduler:

```kotlin
@Test
fun `repository finishes initialization`() = runTest {
    val ioDispatcher = StandardTestDispatcher(testScheduler)
    val repository = UserRepository(ioDispatcher)

    repository.initialize()
    advanceUntilIdle()

    assertTrue(repository.isInitialized)
}
```

Передавайте dispatchers или dispatcher provider через зависимости вместо жёсткого использования `Dispatchers.IO` и `Dispatchers.Default`. В local tests кода с `Dispatchers.Main` заменяйте Main на `TestDispatcher` и сбрасывайте после теста. Готовое JUnit rule показано в статье [Тестирование ViewModel](viewmodel-testing.md).

Если вызывающей стороне нужно знать о завершении запущенной работы, лучше сделать API приостанавливаемым или вернуть объект завершения. Тест, вынужденный угадывать момент окончания фоновой работы, часто указывает на неясный production API.

### Ошибки и отмена

Проверяйте ошибку как наблюдаемый результат: возвращённое значение, выброшенное исключение или error state. Для контракта с исключением используйте `assertFailsWith`, а не перехватывайте ошибку только ради успешного завершения теста.

Для кода, чувствительного к cancellation, отмените job и проверьте нужную очистку либо отсутствие последующего результата. Тестируемый код должен поддерживать cooperative cancellation; CPU-intensive циклам нужны suspension points или явные проверки вроде `ensureActive()`.

## Тестирование Flow

### Конечные cold flows

Для конечного потока получите терминальный результат через `toList()`, `first()` или `single()`:

```kotlin
@Test
fun `flow maps all values`() = runTest {
    val values = flowOf(1, 2, 3)
        .map { it * 2 }
        .toList()

    assertEquals(listOf(2, 4, 6), values)
}
```

Используйте `first()`, если частью контракта является только первое подходящее значение. `single()` подходит лишь тогда, когда поток обязан выдать ровно один элемент и завершиться.

### Hot и бесконечные flows

Для `StateFlow`, `SharedFlow` и других долгоживущих потоков используйте Turbine или запускайте collector, который тест затем отменяет. Turbine делает подписку, проверки и завершение явными:

```kotlin
@Test
fun `state exposes loaded items`() = runTest {
    val viewModel = ItemsViewModel(FakeItemsRepository())

    viewModel.uiState.test {
        assertEquals(ItemsUiState.Loading, awaitItem())

        viewModel.load()

        assertEquals(
            ItemsUiState.Content(listOf("A", "B")),
            awaitItem(),
        )
        cancelAndIgnoreRemainingEvents()
    }
}
```

Подпишитесь до запуска действия для `SharedFlow` с `replay = 0`, поскольку он не хранит значения для будущих subscribers. `StateFlow` всегда предоставляет текущее значение, не отправляет обновление, равное текущему, и объединяет быстрые изменения, поэтому collector не обязан увидеть каждое промежуточное присваивание.

Если ручной collection должен работать весь тест, запустите его в `backgroundScope`. `runTest` отменит этот scope в конце и не позволит бесконечному collector заблокировать завершение:

```kotlin
val values = mutableListOf<Int>()
backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) {
    repository.scores.toList(values)
}
```

Для `StateFlow`, созданного через `stateIn(WhileSubscribed(...))`, сохраняйте активный collector во время проверки `.value`, иначе upstream может не запуститься.

### Операторы, зависящие от времени

Проверяйте `debounce`, `timeout`, задержки retry и похожие операторы через виртуальное время, а не реальное ожидание:

```kotlin
@Test
fun `debounce emits latest value`() = runTest {
    val input = MutableSharedFlow<String>()

    input.debounce(300).test {
        input.emit("a")
        advanceTimeBy(100)
        input.emit("ab")

        advanceTimeBy(300)
        runCurrent()

        assertEquals("ab", awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

Оператор и тест должны использовать dispatchers на одном scheduler. Если production-код переключается на реальный dispatcher, виртуальное время не сможет управлять этой частью.

## Отказ от ожидания реального времени

Не используйте `Thread.sleep()` и произвольные задержки для ожидания «на всякий случай». Они замедляют набор и делают результат зависимым от нагрузки CPU и скорости CI. Coroutine tests должны использовать виртуальное время или сигналы завершения. UI tests должны опираться на idling resources Espresso, синхронизацию Compose, `mainClock` или APIs ожидания условий.

## Связанные темы

- [Стратегия тестирования](strategy.md)
- [Тестирование ViewModel](viewmodel-testing.md)
- [Основы Flow](../coroutines-flow/flow-basics.md)
- [StateFlow и SharedFlow](../coroutines-flow/stateflow-sharedflow.md)
- [Coroutine scopes и cancellation](../coroutines-flow/scopes-cancellation.md)
