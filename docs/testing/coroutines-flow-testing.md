# Coroutines & Flow Testing

This section covers testing coroutines and `Flow`: virtual time, test dispatchers, `runTest`, collection, cancellation and emission checks.

## Coroutines and Flow

### `runTest`

`runTest` is the main API from `kotlinx-coroutines-test` for testing suspend code and coroutines.

It creates a test coroutine scope, supports virtual time, correctly waits for child coroutines and helps detect unfinished jobs. Unlike `runBlocking`, `runTest` does not force the test to actually wait for `delay()`.

Example:

```kotlin
@Test
fun `load returns user`() = runTest {
    val repository = FakeUserRepository()

    val user = repository.loadUser()

    assertEquals("Ada", user.name)
}
```

If the code contains `delay(1_000)`, `runTest` can advance through it virtually:

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

Useful functions:

- `advanceUntilIdle()` - run everything scheduled until idle state;
- `advanceTimeBy(time)` - advance virtual time;
- `runCurrent()` - run tasks scheduled for the current virtual time.

**Important:** `runTest` controls only coroutines that use the test scheduler. If code switches to real `Dispatchers.IO` or creates its own unmanaged threads, the test can become flaky again.

**In short:** `runTest` provides a controlled coroutine test scope and virtual time, so suspend code is tested quickly and predictably.

### `TestDispatcher`

`TestDispatcher` is a dispatcher for coroutine tests that works with `TestCoroutineScheduler` and lets the test control task execution.

Most common options:

- `StandardTestDispatcher` - tasks run in a controlled way, and the test explicitly advances the scheduler through `advanceUntilIdle()`, `runCurrent()` or `advanceTimeBy()`;
- `UnconfinedTestDispatcher` - starts tasks more eagerly and is convenient for some simple tests, but can hide ordering issues.

For `ViewModel` tests, `Dispatchers.Main` is often replaced:

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

Good architecture does not hardcode dispatchers inside classes. It is better to pass a dispatcher or `DispatcherProvider` through DI:

```kotlin
interface DispatcherProvider {
    val io: CoroutineDispatcher
    val default: CoroutineDispatcher
    val main: CoroutineDispatcher
}
```

In tests, test dispatchers can be substituted so the code does not depend on real threads.

**In short:** `TestDispatcher` makes coroutine execution controllable; for stable tests, inject dispatchers and avoid hardcoding `Dispatchers.IO` inside logic.

### Testing Flow

`Flow` is tested by collecting emissions and checking the result. For finite flows, use `toList()`, `first()`, `single()`. For long-running flows, Turbine or manual collection with cancellation is more convenient.

Example finite flow:

```kotlin
@Test
fun `flow emits mapped values`() = runTest {
    val values = flowOf(1, 2, 3)
        .map { it * 2 }
        .toList()

    assertEquals(listOf(2, 4, 6), values)
}
```

Example `StateFlow`:

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

For hot flows, subscribe first and then call the action that emits a value. Otherwise `SharedFlow` with `replay = 0` can lose the emission.

Also remember `StateFlow`: it always has a current value and may not emit a new value if it is `equals()` to the old one.

**Important:** the test must finish collection of a long-running flow. Otherwise the test coroutine can hang or `runTest` can report unfinished work.

**In short:** Flow tests check emissions; for finite flows, `toList()` / `first()` is enough, while hot and long-running flows are easier with Turbine or controlled collection with cancellation.

### Why not use `Thread.sleep` in tests?

`Thread.sleep` in tests makes the suite slow, flaky and dependent on machine speed, CI, CPU load and real threads.

If a test waits "just in case", it either sometimes fails because sleep is too short, or always slows down because sleep is too long.

In coroutine tests, virtual time is used instead of `Thread.sleep`:

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

For UI tests, use idling resources, Compose test synchronization, `mainClock`, explicit assertions with waiting APIs or controlled fake dependencies instead of sleep.

**In short:** `Thread.sleep` waits for real time and makes tests unstable; coroutine tests should use virtual time, and UI tests should use synchronization mechanisms.
