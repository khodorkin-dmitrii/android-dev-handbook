# ViewModel Testing

This section covers `ViewModel` testing: state transitions, user actions, loading/error/content states and one-off events/effects.

## ViewModel tests

### How to test ViewModel?

`ViewModel` is usually tested like a regular Kotlin class: create fake dependencies, call public actions and check observable output, most often `StateFlow<UiState>` and an events/effects stream.

The main goal is to verify behavior, not internal implementation. The test should answer: "if the user performed an action or repository returned a result, which state/effect will UI observe?"

Usually the test needs:

- fake repository/use case;
- test dispatcher for coroutines;
- replacement for `Dispatchers.Main` if `ViewModel` uses `viewModelScope`;
- checks for initial state, state transitions and one-off events.

Example rule for replacing Main dispatcher:

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

Example test:

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

**Important:** if `ViewModel` starts loading in `init`, fake dependencies must be configured before creating `ViewModel`, otherwise the test may verify the wrong scenario.

**In short:** test `ViewModel` through public actions and observable state/effects, using fakes and test dispatchers instead of real network/database dependencies.

### Testing UiState transitions

UiState transitions are the sequence of states a screen goes through: for example initial -> loading -> content or initial -> loading -> error.

For simple synchronous scenarios, checking the final `uiState.value` is enough. But if the sequence itself matters, collect emissions.

Example with manual collection:

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

In practice, `Flow` and `StateFlow` tests often use Turbine because it makes assertions over emissions more convenient and readable:

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

**Important:** do not make a state test depend on every small intermediate detail if it is not part of the screen contract. Sometimes checking the final user-visible state is enough.

**In short:** state transition tests are useful for loading/content/error, retry, validation and complex flows, but they should verify observable UI contract, not internal implementation steps.

### Testing events/effects

Events/effects are one-off commands for UI: navigation, snackbar, toast, permission request, scroll command. They are usually published through `SharedFlow`, `Channel` or callback.

The test should verify that a specific action makes `ViewModel` send the expected effect, and that durable `UiState` is not used as a one-off command.

Example with `SharedFlow`:

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

If `Channel` is used, the public API often exposes `receiveAsFlow()`:

```kotlin
private val _events = Channel<UiEvent>(Channel.BUFFERED)
val events = _events.receiveAsFlow()
```

It is tested the same way as a regular `Flow`.

**Important:** event tests often depend on buffering. `MutableSharedFlow` with `replay = 0` can lose an event if the collector has not subscribed yet. In a test, start collection first, then call the action.

**In short:** one-off events are tested by collecting the event stream: subscribe first, then call the action, then assert the specific effect.
