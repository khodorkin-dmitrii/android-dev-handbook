# ViewModel Testing

Test a `ViewModel` as a Kotlin class: provide controlled dependencies, call its public actions and assert the state or output visible to the UI. The purpose is to verify the UI contract, not coroutine launches or private method calls.

## Test setup

### Replace `Dispatchers.Main`

`viewModelScope` uses `Dispatchers.Main`, which is unavailable in a local JVM test. Replace it with a `TestDispatcher` and reset it after every test:

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

Use `runTest` for coroutine-based tests. Every `TestDispatcher` used by the test and its dependencies should share the same `TestCoroutineScheduler`; otherwise advancing virtual time may run only part of the work. Dispatchers created after `Dispatchers.setMain(testDispatcher)` can inherit its scheduler, or the test can pass `testScheduler` explicitly.

`StandardTestDispatcher` queues newly launched coroutines and gives precise scheduling control. `UnconfinedTestDispatcher` starts them eagerly and can simplify basic tests, but its execution order differs from production. Prefer the standard dispatcher when ordering or concurrency matters.

### Arrange before creating the ViewModel

Configure fakes before constructing a `ViewModel`, especially if work starts in `init`:

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

Use `advanceUntilIdle()` when the contract requires all queued work to finish. Use `runCurrent()` or `advanceTimeBy()` when the timing itself matters. Repeatedly advancing until idle can hide an API that starts work without exposing a completion signal; prefer suspending functions, returned jobs or observable state when callers need to know when work is complete.

## Testing UI state

### Final state

For most scenarios, assert the current `StateFlow.value` after the action completes. Cover the initial state and meaningful outcomes such as content, empty data, validation failure, repository error, retry and cancellation.

Avoid asserting fields that the UI does not consume. A single state assertion is usually more resilient than verifying the exact calls made by the `ViewModel`.

### State transitions

Collect emissions only when the sequence is part of the UI contract, for example when loading must be visible before an asynchronous result. Turbine keeps collection and cleanup explicit:

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

Here the fake suspends the request until `completeWithError()` is called, so loading is a real observable state rather than a scheduler accident.

`StateFlow` is conflated: a slow collector may skip intermediate values and always receives the latest state. Do not write a test that requires every rapid assignment unless those states are genuinely observable by design. If only the final screen state matters, assert `.value` instead.

When a `StateFlow` is produced with `stateIn(WhileSubscribed(...))`, it may require an active collector before its upstream starts. Keep a background collector running during the test, or test the upstream flow separately.

## Testing effects and events

Navigation, snackbars and permission requests are sometimes represented as an effect stream. Subscribe before triggering the action when using a `SharedFlow` with `replay = 0`:

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

This test also documents delivery semantics. A non-replayed `SharedFlow` may lose an effect when no collector is active; a buffered `Channel` has different behavior and still does not provide durable process-death delivery. If an outcome must survive collector absence or recreation, model it as durable state or use an explicit acknowledgement/persistence protocol.

Test that an action produces the intended effect and, when relevant, that repeated actions do not create duplicates. Do not test the private transport mechanism unless it is part of the contract.

## Saved state and boundaries

Pass a real `SavedStateHandle` with controlled values when the `ViewModel` reads navigation arguments or saves lightweight restorable state:

```kotlin
val savedStateHandle = SavedStateHandle(
    mapOf("profileId" to "42"),
)
val viewModel = ProfileViewModel(repository, savedStateHandle)
```

A local `ViewModel` test verifies how the class reads and writes the handle, not Android process recreation itself. Use an integration or instrumented test when the contract depends on Navigation, `SavedStateRegistry` or actual lifecycle restoration.

## Related topics

- [Testing Strategy](strategy.md)
- [Coroutines & Flow Testing](coroutines-flow-testing.md)
- [Android UI Testing](android-ui-testing.md)
- [UI State Architecture](../architecture/ui-state.md)
- [StateFlow & SharedFlow](../coroutines-flow/stateflow-sharedflow.md)
