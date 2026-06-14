# Side Effects

Side effects in Compose are needed for work that goes beyond describing UI: coroutine, subscriptions, listeners, analytics, snackbar, navigation events and adapting external state sources.

## Effect APIs

### `LaunchedEffect`

`LaunchedEffect` starts a coroutine tied to the lifecycle of a specific composable call site.

When `LaunchedEffect` enters Composition, the coroutine starts. When it leaves Composition, the coroutine is canceled. If keys change, the current coroutine is canceled and the effect starts again with new keys.

It is used for suspend side effects: initial load, one-off navigation/event collection, animation, delay, scroll, snackbar flow collection, analytics from `snapshotFlow`.

Keys matter: a key should include values whose changes require restarting the effect. If a fresh lambda/value is needed without restart, use `rememberUpdatedState`.

**Important:** `LaunchedEffect(Unit)` or `LaunchedEffect(true)` means an effect for the lifetime of the call site. This is acceptable, but requires a clear understanding of why restart is not needed.

**In short:** `LaunchedEffect` runs suspend side effects scoped to composition and restarts when its keys change.

### `rememberCoroutineScope`

`rememberCoroutineScope` returns a `CoroutineScope` tied to the call site in Composition. The scope is automatically canceled when this call site leaves Composition.

It is used when a coroutine should not start immediately on entering composition, but from an event handler: `onClick`, `onDismiss`, swipe callback. For example, to show a `Snackbar`, start an animation or perform a short UI-related action from a user event.

Do not launch a coroutine directly in the composable body. For automatic launch when a composable appears, prefer `LaunchedEffect`; for launch from an event, use `rememberCoroutineScope`.

**In short:** `rememberCoroutineScope` gives a composition-aware scope for launching coroutines from callbacks and UI events.

### `DisposableEffect`

`DisposableEffect` is used for side effects that need cleanup when leaving Composition or when keys change.

Typical scenarios: registering a listener/observer/broadcast callback, subscribing to lifecycle events, connecting an external imperative API and reliably unsubscribing in `onDispose`.

`DisposableEffect` must end with an `onDispose` block. If cleanup is empty, check whether `LaunchedEffect` or `SideEffect` fits better.

Keys should describe effect dependencies. If a listener depends on `lifecycleOwner`, `lifecycleOwner` should be a key so the old observer is removed and the new one is registered.

**In short:** `DisposableEffect` is for effects with setup and cleanup, like registering and unregistering observers.

### `SideEffect`

`SideEffect` is used to run a non-suspending side effect after successful recomposition.

A typical scenario is passing current Compose state to an external object not managed by Compose: analytics, logging, imperative controller, system object or legacy API.

`SideEffect` runs after every successful recomposition, so it is not used for suspend work, subscriptions or cleanup. Coroutine work needs `LaunchedEffect`; register/unregister work needs `DisposableEffect`.

**In short:** `SideEffect` publishes Compose state to non-Compose code after a successful recomposition.

### `produceState` / `derivedStateOf`

`produceState` - an effect API that turns an external data source into Compose `State`. It starts a coroutine scoped to Composition, returns `State<T>` and updates `value` from the producer block.

It is used when non-Compose state needs to be adapted to Compose: suspend loading, callback/subscription API, `Flow` / `LiveData` / RxJava-like source or custom observer.

When the composable leaves Composition, the producer is canceled. If keys change, the producer restarts. For callback-based sources, cleanup can be done through `awaitDispose`.

In regular Android architecture, `Flow` from `ViewModel` is usually collected through `collectAsStateWithLifecycle()`, while `produceState` is useful for custom adapters and local integrations.

`derivedStateOf` creates derived Compose `State` and is needed when input state changes more often than UI should actually update. For example, scroll index changes constantly, but a "scroll to top" button should appear only when crossing a threshold.

**Important:** `derivedStateOf` should not be used for ordinary string concatenation or simple calculations that should update as often as inputs. It is overhead, not a universal optimization.

**In short:** `produceState` converts external async state into Compose `State`, while `derivedStateOf` reduces recomposition only when derived result changes less often than its inputs.
