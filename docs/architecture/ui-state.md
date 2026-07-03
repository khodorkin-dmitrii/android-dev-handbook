# UI State Architecture

UI state architecture describes who owns screen state, how UI receives data, how state is restored, and how one-off effects are separated from durable state.

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

### State ownership and restoration

A `ViewModel` is a good screen-level state holder, but it is not persistent storage. It survives common configuration changes, such as rotation, but it does not automatically survive process death.

This means `MutableStateFlow` inside a `ViewModel` is enough for many normal screen updates, but it is not enough for state that would be painful or dangerous to lose: long forms, onboarding progress, checkout steps, unsaved drafts or important user input.

When designing UI state, decide what should survive each lifecycle boundary:

- recomposition;
- temporary disappearance from composition;
- configuration change;
- navigation away and back;
- process death;
- app restart.

Different state needs different owners.

Small local UI state can live in `remember` or `rememberSaveable`. Screen-level state usually belongs to `ViewModel`. Small restorable screen state can be stored with `SavedStateHandle`. Important durable progress should usually be stored in a repository, database, DataStore or backend draft, not only in memory.

A useful rule:

```text
remember              -> survives recomposition
rememberSaveable      -> survives recomposition and simple recreation
ViewModel             -> survives configuration change
SavedStateHandle      -> restores small state after process death
Repository / storage  -> persists important state beyond the screen lifecycle
```

For example, a profile screen can reload data from repository by `profileId`, so the whole loaded profile does not necessarily need to be saved in `SavedStateHandle`. But a search query, selected tab, draft comment or current onboarding step may be worth saving.

```kotlin
@HiltViewModel
class SearchViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private var query: String
        get() = savedStateHandle["query"] ?: ""
        set(value) {
            savedStateHandle["query"] = value
        }

    private val _uiState = MutableStateFlow(
        SearchUiState(query = query)
    )
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()

    fun onQueryChanged(newQuery: String) {
        query = newQuery
        _uiState.update { it.copy(query = newQuery) }
    }
}
```

Do not put everything into `SavedStateHandle`. It is better for small, serializable restoration state, not for large lists, bitmaps, complex object graphs or data that should be the responsibility of the data layer.

Temporary UI scopes are a separate case. Some UI state should not survive at all. For example, a bottom sheet search session, temporary dialog state or local picker state may be intentionally cleared when that UI disappears.

In Compose, this means state ownership should follow the UI lifetime. If state belongs to the whole screen, keep it in the screen `ViewModel`. If it belongs only to a temporary UI element, keep it local to that element or use a shorter-lived state holder.

In newer Compose APIs, this can also be expressed by scoping a `ViewModelStoreOwner` to a temporary composable subtree, but the architectural decision is still the same: the state owner should match the intended lifetime of the UI state.

**In short:** `ViewModel` holds screen state during the screen lifecycle, but restoration is a separate design decision. Choose the state owner based on how long the state should live and how bad it is if the state is lost.

## Feature design

### How to design a feature flow from scratch?

When designing a feature flow from scratch, first understand the user scenario: what data the screen needs, which states are possible, which user actions exist and which side effects should happen.

A practical order: define the UI contract, describe `UiState`, `UiEvent` and `UserAction`, understand data sources, choose the state owner, then connect UI -> `ViewModel` -> use cases/repositories -> data sources.

Next, decide which operations are one-shot suspend functions and which are `Flow` streams. For example, loading a profile once can be a suspend function, while observing a robot status or database is better modeled with `Flow`.

Separate state from effects early: content/loading/error should be part of `UiState`, while navigation/snackbar/permission request should be separate events/effects if they are truly one-off.

Also consider lifecycle, process death, retry, offline/cache, error mapping, analytics, testing and module boundaries. A small screen does not need ideal Clean Architecture, but layer responsibilities should be clear.

The state restoration decision should be part of feature design, not an afterthought. For each important piece of state, decide whether it is derived from data sources, stored in memory, saved in `SavedStateHandle`, persisted locally or synchronized with backend.

For example:

- screen data loaded by id can usually be reloaded from repository;
- search query, selected tab or current step can often be restored from `SavedStateHandle`;
- long draft input or checkout/onboarding progress may need local storage or backend draft;
- snackbar/navigation effects should usually not be restored as state;
- temporary sheet/dialog state may intentionally disappear when the UI element is dismissed.

**In short:** start from the UI contract and user actions, model durable `UiState` and one-off effects, decide how state should be restored, then choose which logic belongs to `ViewModel`, domain/use cases, repositories and data sources.
