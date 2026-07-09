# Side Effects

Side effects in Compose are work that happens outside pure UI description: launching coroutines, showing a snackbar, sending analytics, registering listeners, collecting events, scrolling, navigation and adapting external state sources.

Composable functions should ideally stay side-effect free. They can recompose many times, skip recomposition, restart with different keys or leave Composition. Effect APIs make side effects explicit and tie them to the lifecycle of a composable call site.

## Core rule

Do not start work directly from the composable body:

```kotlin
@Composable
fun ProfileScreen(userId: String) {
    // Bad: can run on every recomposition.
    viewModel.loadUser(userId)

    ProfileContent()
}
```

Use an effect when work must happen because a composable entered Composition, because a key changed or because a callback needs a composition-aware scope.

```kotlin
@Composable
fun ProfileScreen(
    userId: String,
    viewModel: ProfileViewModel
) {
    LaunchedEffect(userId) {
        viewModel.loadUser(userId)
    }

    ProfileContent()
}
```

In regular Android architecture, durable screen work usually belongs to `ViewModel`. Compose effects should mostly coordinate UI-related work: collect one-off UI events, show snackbars, scroll, bridge lifecycle listeners or publish state to non-Compose APIs.

## Which API to use

| Need | API |
|---|---|
| Run suspend work when a composable enters Composition or when a key changes | `LaunchedEffect` |
| Launch a coroutine from a user event callback | `rememberCoroutineScope` |
| Register something and clean it up | `DisposableEffect` |
| Publish Compose state to non-Compose code after recomposition | `SideEffect` |
| Keep the latest lambda or value inside a long-running effect without restarting it | `rememberUpdatedState` |
| Convert external async state into Compose `State` | `produceState` |
| Convert Compose state reads into a `Flow` | `snapshotFlow` |
| Cache derived state when the derived result changes less often than inputs | `derivedStateOf` |

## `LaunchedEffect`

`LaunchedEffect` starts a coroutine tied to the lifecycle of a specific composable call site.

When `LaunchedEffect` enters Composition, the coroutine starts. When it leaves Composition, the coroutine is canceled. If keys change, the current coroutine is canceled and the effect starts again with new keys.

```kotlin
@Composable
fun UserScreen(
    userId: String,
    viewModel: UserViewModel
) {
    LaunchedEffect(userId) {
        viewModel.load(userId)
    }

    UserContent()
}
```

Use it for suspend side effects:

- initial UI-related work;
- snackbar display;
- scroll or animation;
- collecting one-off UI events;
- navigation events emitted from UI state or event streams;
- analytics based on Compose state through `snapshotFlow`.

Keys matter. A key should include values whose changes require restarting the effect.

```kotlin
LaunchedEffect(userId) {
    viewModel.load(userId)
}
```

If a value or lambda must stay fresh inside a long-running effect, but should not restart that effect, use `rememberUpdatedState`.

```kotlin
@Composable
fun Timeout(onTimeout: () -> Unit) {
    val latestOnTimeout by rememberUpdatedState(onTimeout)

    LaunchedEffect(Unit) {
        delay(1_000)
        latestOnTimeout()
    }
}
```

`LaunchedEffect(Unit)` or `LaunchedEffect(true)` means "run for the lifetime of this call site". This is valid for cases like collecting a stable event stream, but it should be intentional.

```kotlin
LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        when (event) {
            is UiEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            is UiEvent.NavigateBack -> navController.popBackStack()
        }
    }
}
```

**In short:** `LaunchedEffect` runs suspend side effects scoped to Composition and restarts when its keys change.

## `rememberCoroutineScope`

`rememberCoroutineScope` returns a `CoroutineScope` tied to the current call site in Composition. The scope is canceled when this call site leaves Composition.

Use it when a coroutine should start from an event handler, not automatically when the composable appears.

```kotlin
@Composable
fun SaveButton(snackbarHostState: SnackbarHostState) {
    val scope = rememberCoroutineScope()

    Button(
        onClick = {
            scope.launch {
                snackbarHostState.showSnackbar("Saved")
            }
        }
    ) {
        Text("Save")
    }
}
```

Good use cases:

- `onClick`;
- `onDismiss`;
- swipe callbacks;
- local snackbar;
- short UI-related animation or scroll action.

Do not use it to hide business logic inside UI. If work must survive configuration changes or belong to screen state, move it to `ViewModel`.

**In short:** `rememberCoroutineScope` gives a composition-aware scope for launching coroutines from callbacks and UI events.

## `DisposableEffect`

`DisposableEffect` is used for side effects that need cleanup when leaving Composition or when keys change.

Typical scenarios:

- register and unregister a listener;
- observe lifecycle events;
- connect to an imperative API;
- subscribe to a callback source.

```kotlin
@Composable
fun LifecycleAnalytics(
    lifecycleOwner: LifecycleOwner = LocalLifecycleOwner.current,
    analytics: Analytics
) {
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_START) {
                analytics.trackScreenVisible()
            }
        }

        lifecycleOwner.lifecycle.addObserver(observer)

        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }
}
```

`DisposableEffect` must end with `onDispose`. If cleanup is empty, check whether `LaunchedEffect` or `SideEffect` fits better.

Keys should describe dependencies. If a listener depends on `lifecycleOwner`, then `lifecycleOwner` should be a key so the old observer is removed and the new one is registered.

**In short:** `DisposableEffect` is for effects with setup and cleanup.

## `SideEffect`

`SideEffect` runs a non-suspending side effect after every successful recomposition.

Use it to publish current Compose state to non-Compose code:

- analytics user properties;
- logging;
- imperative controller state;
- legacy UI integration;
- external object not managed by Compose.

```kotlin
@Composable
fun ProfileContent(
    user: User,
    analytics: Analytics
) {
    SideEffect {
        analytics.setUserType(user.type)
    }

    Text(user.name)
}
```

`SideEffect` runs after every successful recomposition. Do not use it for suspend work, subscriptions, cleanup or expensive operations. Coroutine work belongs to `LaunchedEffect`; setup and cleanup belong to `DisposableEffect`.

**In short:** `SideEffect` publishes Compose state to non-Compose code after successful recomposition.

## `produceState`

`produceState` converts external async state into Compose `State`.

It starts a coroutine scoped to Composition, returns `State<T>` and updates `value` from the producer block. When the composable leaves Composition, the producer is canceled. If keys change, the producer restarts.

```kotlin
@Composable
fun rememberUserState(
    userId: String,
    repository: UserRepository
): State<Result<User>> {
    return produceState<Result<User>>(
        initialValue = Result.Loading,
        key1 = userId
    ) {
        value = repository.loadUser(userId)
    }
}
```

For callback-based sources, use `awaitDispose` for cleanup.

```kotlin
@Composable
fun rememberNetworkState(
    monitor: NetworkMonitor
): State<Boolean> {
    return produceState(initialValue = monitor.isOnline) {
        val listener = NetworkListener { isOnline ->
            value = isOnline
        }

        monitor.addListener(listener)

        awaitDispose {
            monitor.removeListener(listener)
        }
    }
}
```

In regular Android apps, `Flow` from `ViewModel` is usually collected with `collectAsStateWithLifecycle()`. Use `produceState` mostly for custom adapters, local integrations or non-standard callback sources.

**In short:** `produceState` converts external async or callback-based state into Compose `State`.

## `snapshotFlow`

`snapshotFlow` converts reads of Compose state inside its block into a cold `Flow`.

It is useful when Compose state changes should drive Flow operators, analytics or event-like processing.

```kotlin
@Composable
fun ScrollAnalytics(
    listState: LazyListState,
    analytics: Analytics
) {
    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex }
            .map { index -> index > 0 }
            .distinctUntilChanged()
            .collect { hasScrolled ->
                if (hasScrolled) analytics.trackListScrolled()
            }
    }
}
```

Use it when you need Flow operators over Compose state. Do not use it for ordinary UI rendering; Compose can read state directly.

**In short:** `snapshotFlow` bridges Compose snapshot state into `Flow`.

## `derivedStateOf`

`derivedStateOf` creates derived Compose `State`.

Use it when input state changes more often than the UI should update, and the derived result changes less frequently.

```kotlin
@Composable
fun MessagesList(listState: LazyListState) {
    val showScrollToTop by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    if (showScrollToTop) {
        ScrollToTopButton()
    }
}
```

Do not use `derivedStateOf` for ordinary cheap calculations that should update whenever inputs update.

```kotlin
// Usually unnecessary.
val fullName by remember {
    derivedStateOf { "$firstName $lastName" }
}
```

That is overhead, not an optimization.

**In short:** `derivedStateOf` reduces unnecessary recomposition only when the derived result changes less often than its inputs.

## Common mistakes

### Launching work from the composable body

```kotlin
@Composable
fun BadScreen(viewModel: VM) {
    viewModel.load() // Bad
}
```

Use `LaunchedEffect` or move the trigger to `ViewModel`.

### Wrong keys

```kotlin
LaunchedEffect(Unit) {
    viewModel.load(userId)
}
```

If `userId` changes while the same call site stays in Composition, this effect will not restart. Prefer:

```kotlin
LaunchedEffect(userId) {
    viewModel.load(userId)
}
```

### Restarting too often

```kotlin
LaunchedEffect(onEvent) {
    delay(1_000)
    onEvent()
}
```

If `onEvent` is recreated often, the effect restarts often. Prefer `rememberUpdatedState` when restart is not intended.

### Empty cleanup

```kotlin
DisposableEffect(Unit) {
    onDispose { }
}
```

This is usually a sign that another effect API fits better.

## Related topics

- [State & Recomposition](state-recomposition.md)
- [Compose Performance](performance.md)
- [UI State Architecture](../architecture/ui-state.md)
- [Lifecycle-aware Collection](../coroutines-flow/lifecycle-aware-collection.md)
