# UI State Architecture

UI state architecture describes who owns screen state, how UI receives data, and how one-off effects are separated from durable state.

## UI state

### ViewModel + UI state

In modern Android, `ViewModel` usually acts as a screen-level state holder: it receives events from UI, runs use cases/repository calls and publishes UI state for the screen.

UI state should describe what the screen needs to show right now: loading, data, error, selected values, input text, enabled/disabled states and other user-visible data.

A practical approach is to store UI state as an immutable data class or sealed hierarchy and expose it as a read-only `StateFlow`. UI only renders state and sends actions/events back to `ViewModel`.

```kotlin
data class ProfileUiState(
    val isLoading: Boolean = false,
    val userName: String = "",
    val errorMessage: String? = null
)

private val _uiState = MutableStateFlow(ProfileUiState())
val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()
```

**In short:** `ViewModel` owns screen UI state, exposes it as an observable immutable state, and handles user actions by updating that state through domain or data layer.

### Loading / content / error

Loading/content/error is a basic screen-state model that explicitly describes the main UI modes: data is loading, data is shown successfully, or an error happened.

For a simple screen, a sealed interface can work well:

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Content(val items: List<ItemUiModel>) : UiState
    data class Error(val message: String) : UiState
}
```

This approach is convenient when states are mutually exclusive: the screen is either loading, content or error. It reduces contradictory boolean flags such as `isLoading = true` and `error != null` at the same time.

For more complex screens, a data class state is often better: content can remain on screen during refresh, while loading/error are additional fields. For example, a list is already displayed, but a pull-to-refresh indicator or snackbar error appears on top.

**In short:** sealed state works well for mutually exclusive screen states, while data class state is better when content, loading and errors can coexist.

### State vs events/effects

State is a durable description of UI that can be rendered again after recomposition, rotation or a new subscription. Examples: item list, selected tab, input text, loading flag.

Events/effects are one-off actions that are not persistent screen state: navigation, snackbar, toast, scroll command, permission request, opening an external screen.

The main risk is putting a one-off event into regular UI state and accidentally repeating it after rotation or another collection. For example, if state contains `navigateBack = true`, a new UI collector may navigate again.

State is usually published through `StateFlow<UiState>`, while one-off effects are published through `SharedFlow<UiEvent>`, `Channel` or an explicit callback, depending on the project architecture.

**In short:** state describes what the UI should look like, effects describe one-time actions the UI should perform.

### One-off events

One-off event is an event that should be handled once: show a snackbar, open a screen, close a screen, request permission, scroll a list.

A typical `ViewModel` option:

```kotlin
sealed interface UiEvent {
    data class ShowSnackbar(val message: String) : UiEvent
    data object NavigateBack : UiEvent
}

private val _events = MutableSharedFlow<UiEvent>()
val events = _events.asSharedFlow()
```

UI collects events in a lifecycle-aware way and performs the side effect. In Compose this is often done with `LaunchedEffect`; in the View System, with `repeatOnLifecycle`.

**Important:** `SharedFlow` with `replay = 0` can lose an event if the collector is not active yet. This is often acceptable for non-critical UI effects, but important results are better modeled as part of `UiState`.

An alternative is an event wrapper/consumable state, but it can easily complicate the code. The important part is to choose the approach deliberately and not mix durable state with transient commands.

**In short:** one-off events should be separated from persistent UI state, but event delivery must be lifecycle-aware to avoid duplicates or lost events.

## Feature design

### How to design a feature flow from scratch?

When designing a feature flow from scratch, first understand the user scenario: what data the screen needs, which states are possible, which user actions exist and which side effects should happen.

A practical order: define the UI contract, describe `UiState`, `UiEvent` and `UserAction`, understand data sources, choose the state owner, then connect UI -> `ViewModel` -> use cases/repositories -> data sources.

Next, decide which operations are one-shot suspend functions and which are `Flow` streams. For example, loading a profile once can be a suspend function, while observing a robot status or database is better modeled with `Flow`.

Separate state from effects early: content/loading/error should be part of `UiState`, while navigation/snackbar/permission request should be separate events/effects if they are truly one-off.

Also consider lifecycle, process death, retry, offline/cache, error mapping, analytics, testing and module boundaries. A small screen does not need ideal Clean Architecture, but layer responsibilities should be clear.

**In short:** start from the UI contract and user actions, model durable `UiState` and one-off effects, then decide which logic belongs to `ViewModel`, domain/use cases, repositories and data sources.
