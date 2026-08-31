# Lifecycle-aware Collection

Lifecycle-aware collection keeps UI subscriptions active only while the screen can use their values. This avoids unnecessary upstream work and prevents a stopped UI from reacting to updates.

## Android UI collection

### `collectAsStateWithLifecycle`

`collectAsStateWithLifecycle()` is the recommended Android Compose API for converting a `Flow` into Compose `State` with `Lifecycle` awareness. It is provided by `lifecycle-runtime-compose`.

For a `StateFlow`, the current value is used automatically:

```kotlin
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

For a general `Flow`, provide an initial value:

```kotlin
val items by viewModel.items.collectAsStateWithLifecycle(
    initialValue = emptyList(),
)
```

Collection runs while the lifecycle is at least `STARTED` by default. When it drops below that state, the collecting coroutine is cancelled; when the lifecycle becomes active again, collection restarts. A `StateFlow` immediately supplies its latest value after restart.

Use `collectAsStateWithLifecycle()` for observable screen state. Plain `collectAsState()` is lifecycle-agnostic and is mainly appropriate for platform-independent Compose code or flows whose lifetime is already controlled elsewhere.

Do not use state collection for one-off commands merely because it is convenient. State can be replayed after recreation, so navigation and snackbar behavior requires an explicit delivery design.

### `repeatOnLifecycle`

`repeatOnLifecycle()` runs a suspending block whenever a `Lifecycle` reaches a target state. It cancels the block and its child coroutines below that state, then starts a new block when the lifecycle returns.

Typical Fragment/View System collection:

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect(::render)
    }
}
```

Use `viewLifecycleOwner` for Fragment UI because the Fragment's view has a shorter lifecycle than the Fragment itself. This prevents updates from targeting a destroyed view.

If several flows must be collected concurrently, launch a child coroutine for each one. A `collect` call normally does not complete, so sequential calls would leave later collectors unreachable:

```kotlin
viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
    launch { viewModel.uiState.collect(::render) }
    launch { viewModel.messages.collect(::showMessage) }
}
```

Prefer `repeatOnLifecycle()` to the older `launchWhenStarted` / `launchWhenResumed` APIs. Those APIs suspend the consumer instead of cancelling it, so a flow's upstream producer may remain active while the UI is stopped.

### Effects in Compose

`LaunchedEffect` starts a coroutine tied to the composable's presence in the composition. It is useful for UI reactions such as showing a snackbar, scrolling or navigating, but **it is not Android lifecycle-aware by itself**.

For effects that should only be handled while the screen is `STARTED`, combine it with `repeatOnLifecycle()`:

```kotlin
val lifecycleOwner = LocalLifecycleOwner.current

LaunchedEffect(viewModel, lifecycleOwner) {
    lifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            when (event) {
                UiEvent.NavigateBack -> navController.popBackStack()
                is UiEvent.ShowSnackbar ->
                    snackbarHostState.showSnackbar(event.message)
            }
        }
    }
}
```

`LaunchedEffect` restarts when one of its keys changes. Choose stable keys that represent the subscription owner; an accidental key change can cancel and recreate the collector.

Lifecycle-aware collection does not guarantee event delivery. A `SharedFlow` with `replay = 0` drops emissions when no collector is active, while replaying an effect can execute it again after recreation. Keep critical outcomes in durable UI state and define loss, buffering and consumption semantics explicitly for transient effects.

## Related topics

- [StateFlow & SharedFlow](stateflow-sharedflow.md)
- [Coroutine Scopes & Cancellation](scopes-cancellation.md)
- [UI State Architecture](../architecture/ui-state.md)
