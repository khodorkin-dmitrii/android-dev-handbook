# Coroutines & Flow Testing

Coroutine tests should control execution order, virtual time and completion. Flow tests additionally need an explicit collection strategy because a stream may be cold, hot, finite or never-ending.

## Testing coroutines

### `runTest` and virtual time

`runTest` is the main entry point from `kotlinx-coroutines-test`. It creates a `TestScope`, uses a `TestDispatcher`, skips delays controlled by its scheduler and waits for child coroutines before returning.

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

`advanceTimeBy(1_000)` moves virtual time forward and runs work scheduled before the target time. `runCurrent()` then executes work scheduled exactly at the current time. Other useful operations are:

- `runCurrent()` - run tasks scheduled for the current virtual time;
- `advanceTimeBy(duration)` - move virtual time by a specific amount;
- `advanceUntilIdle()` - run scheduled work until no tasks remain.

Use the narrowest operation that expresses the expectation. Calling `advanceUntilIdle()` everywhere can hide which step should complete the work.

`runTest` controls only coroutines using its `TestCoroutineScheduler`. Real dispatchers, unmanaged scopes and threads remain outside virtual time and can make tests slow or flaky.

### Test dispatchers and one scheduler

The two common dispatchers have different scheduling behavior:

- `StandardTestDispatcher` queues new coroutines and gives the test explicit control. It is a good default and exposes ordering assumptions.
- `UnconfinedTestDispatcher` starts new coroutines eagerly until their first suspension. It can simplify basic collection tests, but does not reproduce production ordering.

All `TestDispatcher` instances in one test should share the same scheduler:

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

Inject dispatchers or a dispatcher provider instead of hardcoding `Dispatchers.IO` or `Dispatchers.Default`. For local tests of code using `Dispatchers.Main`, replace Main with a `TestDispatcher` and reset it after the test. See [ViewModel Testing](viewmodel-testing.md) for a reusable JUnit rule.

If callers must know when launched work finishes, prefer a suspending API or return a completion handle. A test that can only guess when background work is done often exposes an unclear production API.

### Failure and cancellation

Test failures as observable results: a returned error, thrown exception or error state. Use `assertFailsWith` for an exception contract and avoid catching exceptions only to make the test pass.

For cancellation-sensitive code, cancel the job and verify the relevant cleanup or absence of later output. The code under test must cooperate with cancellation; CPU-heavy loops need suspension points or explicit checks such as `ensureActive()`.

## Testing Flow

### Finite cold flows

For a finite flow, collect a terminal result with `toList()`, `first()` or `single()`:

```kotlin
@Test
fun `flow maps all values`() = runTest {
    val values = flowOf(1, 2, 3)
        .map { it * 2 }
        .toList()

    assertEquals(listOf(2, 4, 6), values)
}
```

Use `first()` when only the first matching value is part of the contract. Use `single()` only when the flow must emit exactly one element and complete.

### Hot and never-ending flows

For `StateFlow`, `SharedFlow` and other long-running streams, use Turbine or launch a collector that the test cancels. Turbine makes subscription, assertions and cleanup explicit:

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

Subscribe before triggering a `SharedFlow` with `replay = 0`, because it does not retain values for future subscribers. `StateFlow` always exposes its current value, suppresses updates equal to the current value and conflates rapid updates, so collectors are not guaranteed to observe every intermediate assignment.

When manual collection must continue for the whole test, launch it in `backgroundScope`. `runTest` cancels that scope at the end, preventing an infinite collector from blocking completion:

```kotlin
val values = mutableListOf<Int>()
backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) {
    repository.scores.toList(values)
}
```

For a `StateFlow` created with `stateIn(WhileSubscribed(...))`, keep an active collector while asserting `.value`; otherwise the upstream may never start.

### Time-based operators

Test `debounce`, `timeout`, retry delays and similar operators with virtual time, not real waiting:

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

The operator and the test must use dispatchers backed by the same scheduler. If production code switches to a real dispatcher, virtual time cannot control that part.

## Avoid real-time waiting

Do not use `Thread.sleep()` or arbitrary delays to wait "just in case". They slow the suite and make results depend on CPU load and CI speed. Coroutine tests should use virtual time or completion signals. UI tests should use Espresso idling resources, Compose synchronization, `mainClock` or condition-based waiting APIs.

## Related topics

- [Testing Strategy](strategy.md)
- [ViewModel Testing](viewmodel-testing.md)
- [Flow Basics](../coroutines-flow/flow-basics.md)
- [StateFlow & SharedFlow](../coroutines-flow/stateflow-sharedflow.md)
- [Coroutine Scopes & Cancellation](../coroutines-flow/scopes-cancellation.md)
