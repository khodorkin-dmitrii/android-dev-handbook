# StateFlow & SharedFlow

`StateFlow` and `SharedFlow` are hot Flow primitives for state, events and shared emissions.

## State and events

### What is StateFlow?

`StateFlow` - a hot `Flow` that always stores the current state value and immediately gives it to a new collector.

`StateFlow` always has an initial value. It fits UI state in `ViewModel` well: loading/content/error, form state, selected item, screen data and derived state.

`StateFlow` is conflated: if the value changes quickly, a collector usually receives the latest actual value and is not required to process every intermediate one. Also, `StateFlow` does not emit a new value if it `equals()` the old one.

Usually, `ViewModel` exposes read-only `StateFlow` and keeps `MutableStateFlow` internally:

```kotlin
private val _uiState = MutableStateFlow(UiState.Loading)
val uiState: StateFlow<UiState> = _uiState.asStateFlow()
```

**In short:** `StateFlow` is a hot observable state holder with a current value; it is a good fit for `ViewModel` UI state.

### What is SharedFlow?

`SharedFlow` - a hot `Flow` for broadcast-style emissions to several collectors.

Unlike `StateFlow`, `SharedFlow` does not have to have a current `value`. Its behavior is configured through `replay`, `extraBufferCapacity` and `onBufferOverflow`.

`SharedFlow` fits events or streams where there is not always a "current state": navigation events, snackbar messages, refresh triggers, analytics-like events, websocket updates.

For one-off UI events, `MutableSharedFlow` with `replay = 0` is often used so a new collector does not automatically receive an old event:

```kotlin
private val _events = MutableSharedFlow<UiEvent>()
val events = _events.asSharedFlow()
```

**Important:** events require careful lifecycle-aware collection, otherwise an event can be lost if the collector is not active yet. For critical events, it is sometimes better to model them as part of state.

**In short:** `SharedFlow` is a configurable hot broadcast stream; it is useful for events or shared emissions, not necessarily for state.

### StateFlow vs SharedFlow

`StateFlow` stores one current value and always has an initial value. A new collector immediately receives the latest value.

`SharedFlow` is more general: it can have a replay cache, buffer and does not have to have a current value. With `replay = 0`, a new collector does not receive old emissions.

For UI state, `StateFlow` is usually chosen because a screen always needs to know the current state. For one-off events or shared event streams, `SharedFlow` is usually chosen.

`StateFlow` can be viewed as a specialized `SharedFlow` for state: `replay = 1`, latest value, equality-based conflation and required initial value.

**Important:** do not store navigation/snackbar as a simple field in `StateFlow` if the event should be consumed once. But `SharedFlow` with `replay = 0` can also lose an event if there is no collector.

**In short:** `StateFlow` is for state with a current value, `SharedFlow` is for configurable shared emissions and events.

### StateFlow vs LiveData

`LiveData` - a lifecycle-aware observable data holder from AndroidX Lifecycle. It automatically accounts for `LifecycleOwner` and is active only in `STARTED` / `RESUMED` states.

`StateFlow` - a Kotlin Coroutines primitive. It does not know Android lifecycle by itself, so in UI it should be collected lifecycle-aware: `collectAsStateWithLifecycle()` in Compose or `repeatOnLifecycle()` in View System.

`StateFlow` integrates better with coroutines/Flow operators, `combine`, `stateIn`, testing through coroutines test APIs and Kotlin multiplatform-style architecture.

`LiveData` is still found in legacy Android projects and simple lifecycle-aware scenarios, but for modern Android Kotlin, `Flow` / `StateFlow` is usually preferred.

**Important:** if `StateFlow` is collected directly from `Activity` / `Fragment` without `repeatOnLifecycle`, collection may continue in an inappropriate lifecycle state and do unnecessary work or update inactive UI.

**In short:** `LiveData` is Android lifecycle-aware by design; `StateFlow` is coroutine-based and needs lifecycle-aware collection on Android.

### State vs events/effects

State describes the current screen state and should be reproducible: if the screen is recreated and the state is rendered again, UI should look correct.

Events/effects are one-time actions: navigation, snackbar, toast, open dialog, scroll command, permission request. They are not always convenient to store as regular state because they may repeat after recreation or a new collector.

For state, `StateFlow<UiState>` is most often used. For effects, `SharedFlow<UiEvent>`, `Channel`, UI callback or state-based event wrapper can be used depending on project architecture.

Main rule: critical data is better stored in state, while one-time UI commands belong in an effect/event stream. But the event stream must account for lifecycle, otherwise events can be lost.

```kotlin
sealed interface UiEvent {
    data class ShowSnackbar(val message: String) : UiEvent
    data object NavigateBack : UiEvent
}
```

**In short:** state is durable and describes what the UI should show; events/effects are one-time actions and need careful lifecycle handling.
