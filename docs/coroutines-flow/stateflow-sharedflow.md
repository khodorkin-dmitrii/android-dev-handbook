# StateFlow & SharedFlow

`StateFlow` and `SharedFlow` are hot Flow primitives for sharing values with one or more collectors. Use `StateFlow` for observable state with a current value and `SharedFlow` for configurable broadcast-style emissions.

## State and events

### What is StateFlow?

`StateFlow` is a hot `Flow` that always stores a current value. A new collector immediately receives that value and then subsequent updates.

It requires an initial value and fits UI state in a `ViewModel`: loading/content/error, form input, selected items and derived screen data. Its current value is also available through `value`.

`StateFlow` is conflated. A slow collector may skip intermediate updates but receives the latest value. Updates equal to the previous value according to `equals()` are not emitted, so state models should have reliable equality and are usually immutable.

Expose a read-only flow and keep mutation private. For read-modify-write changes, `update` performs the change atomically:

```kotlin
private val _uiState = MutableStateFlow(UiState())
val uiState: StateFlow<UiState> = _uiState.asStateFlow()

fun selectItem(id: Long) {
    _uiState.update { current -> current.copy(selectedItemId = id) }
}
```

### What is SharedFlow?

`SharedFlow` is a hot `Flow` that broadcasts each emission to all active subscribers. It has no required initial value or `value` property.

Its delivery behavior is configured with:

- `replay` - values delivered to a new subscriber;
- `extraBufferCapacity` - additional space for slow active subscribers;
- `onBufferOverflow` - whether the emitter suspends or an old/new value is dropped when the buffer is full.

With the default `MutableSharedFlow()` configuration, `replay` and extra capacity are both zero. `emit` waits for active subscribers to accept the value, but returns immediately when there are no subscribers and the value is lost. Extra buffer capacity does not preserve values while there are no subscribers; only the replay cache does.

`SharedFlow` fits refresh signals, application-wide ticks, websocket updates and non-critical UI effects whose delivery rules are explicit:

```kotlin
private val _effects = MutableSharedFlow<UiEffect>(
    extraBufferCapacity = 1,
)
val effects: SharedFlow<UiEffect> = _effects.asSharedFlow()
```

With `replay = 0`, a collector that starts later does not receive an earlier emission. Increasing `replay` changes that behavior, but can also repeat an already handled effect after recreation. Therefore, `replay` is not a general exactly-once delivery mechanism.

Unlike `SharedFlow`, a `Channel` normally distributes each element to one competing receiver rather than broadcasting it to every subscriber. See [Channels](channels.md) for delivery trade-offs.

### StateFlow vs SharedFlow

| Property | StateFlow | SharedFlow |
| --- | --- | --- |
| Current value | Required and available through `value` | Not required |
| Initial value | Required | Not required |
| New subscriber | Receives the latest value | Receives `replay` cached values |
| Conflation | Based on `equals()` | Controlled through buffering and overflow policy |
| Typical use | Observable state | Shared signals and transient effects |

`StateFlow` is a specialized `SharedFlow` for state: it keeps one latest value, replays it to new subscribers and applies equality-based conflation.

Do not put a navigation or snackbar command into a simple `StateFlow` field when it must be consumed only once: a new collector can handle it again. However, replacing it with `SharedFlow(replay = 0)` introduces the opposite risk - the effect is lost when no collector is active.

### Converting cold flows with stateIn and shareIn

Collecting a cold `Flow` starts its upstream producer separately for every collector. Use `stateIn` when consumers need shared state, or `shareIn` when they need a shared stream of emissions.

```kotlin
val uiState: StateFlow<UiState> = repository.observeData()
    .map(::toUiState)
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = UiState.Loading,
    )
```

The supplied scope controls the lifetime of sharing. `SharingStarted.WhileSubscribed(...)` starts the upstream when subscribers appear and stops it after they disappear, optionally after a timeout. `Eagerly` starts immediately; `Lazily` starts on the first subscriber and then keeps running while the scope is alive.

### StateFlow vs LiveData

`LiveData` is an AndroidX observable holder that automatically stops notifying an observer when its `LifecycleOwner` is inactive. `StateFlow` is a Kotlin Coroutines primitive and does not know about the Android lifecycle.

Collect flows with lifecycle awareness: use `collectAsStateWithLifecycle()` in Compose or collect inside `repeatOnLifecycle()` in the View system. A plain `launch` or `launchIn` tied only to an `Activity` or `Fragment` scope can keep collecting while the UI is stopped.

`StateFlow` integrates naturally with Flow operators such as `map` and `combine`, coroutine test APIs and shared Kotlin architecture. `LiveData` remains common in existing View-based code, but `StateFlow` is usually the default for modern coroutine-based state.

### State vs events/effects

State describes what the screen should show now. It should be reproducible: collecting it again after recreation should render the same valid UI.

Effects are transient commands such as showing a snackbar, navigating, scrolling or launching a system picker. A separate `SharedFlow` or [Channel](channels.md#ui-events-and-effects) can be appropriate when the consequence is non-critical and behavior without an active collector is deliberately defined.

Critical outcomes should usually be reduced to durable state. For example, store that an operation succeeded or that data was saved; navigation or a confirmation message can then be derived from an explicit UI decision instead of being the only record of the result.

```kotlin
sealed interface UiEffect {
    data class ShowSnackbar(val message: String) : UiEffect
    data object NavigateBack : UiEffect
}
```

The choice is not simply “state uses `StateFlow`, events use `SharedFlow`.” First decide whether the information must survive the absence or recreation of the UI, then choose the primitive and buffering policy that provide those semantics.
