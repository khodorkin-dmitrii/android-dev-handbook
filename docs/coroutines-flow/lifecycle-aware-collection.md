# Lifecycle-aware Collection

Lifecycle-aware collection is needed so UI collects `Flow` only when the screen is active and does not continue unnecessary work in the background.

## Android UI collection

### `collectAsStateWithLifecycle`

`collectAsStateWithLifecycle()` - a Compose API from `lifecycle-runtime-compose` that collects `Flow` / `StateFlow` and converts it into Compose `State` with `Lifecycle` awareness.

It is used in Compose UI to safely subscribe to `uiState` from `ViewModel`:

```kotlin
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

Main benefit: collection is active only in the appropriate lifecycle state, usually `STARTED` and above. When the screen goes to the background, collection is paused; when it returns, collection resumes.

For `StateFlow`, this is especially convenient: UI immediately receives the latest value and does not start unnecessary work while the screen is inactive.

**Important:** do not use regular `collectAsState()` for Android screen-level flows without understanding lifecycle, because collection may continue when UI is already inactive.

**In short:** `collectAsStateWithLifecycle` is the recommended Compose way to collect `Flow` / `StateFlow` from `ViewModel` with Android lifecycle awareness.

### `repeatOnLifecycle`

`repeatOnLifecycle()` - a lifecycle-aware API for running a coroutine block only in a specific `Lifecycle.State`, for example `STARTED`.

When lifecycle reaches the target state, the block starts. When lifecycle drops below that state, the coroutine inside the block is canceled. When lifecycle returns to the target state, the block starts again.

Typical Fragment/View System example:

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state ->
            render(state)
        }
    }
}
```

Use `viewLifecycleOwner` for Fragment UI, not the lifecycle of the `Fragment` itself, because the View lifecycle is shorter than the Fragment lifecycle.

`repeatOnLifecycle` is better than `launchWhenStarted` / `launchWhenResumed` because it explicitly cancels and restarts collection, rather than just suspending execution in less obvious places.

**Important:** if several `Flow`s need to be collected in parallel inside `repeatOnLifecycle`, each `collect` should be in a separate `launch`; otherwise the first `collect` blocks the others.

**In short:** `repeatOnLifecycle` starts collection only when lifecycle is at least the target state and cancels it when the UI is stopped.

### `LaunchedEffect` for effects

In Compose, one-off UI effects are often collected through `LaunchedEffect` because it is a coroutine tied to composition lifecycle.

```kotlin
LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        when (event) {
            UiEvent.NavigateBack -> navController.popBackStack()
            is UiEvent.ShowSnackbar -> {
                snackbarHostState.showSnackbar(event.message)
            }
        }
    }
}
```

`LaunchedEffect` fits navigation, snackbar, scroll command, permission request trigger and other one-off effects that should run as a UI reaction to an event stream.

`LaunchedEffect` keys matter: if a key changes, the old coroutine is canceled and collection starts again. For a persistent subscription to events, usually use `LaunchedEffect(Unit)` or `LaunchedEffect(viewModel)` if changing the `ViewModel` should restart collection.

**Important:** `SharedFlow` with `replay = 0` can lose an event if the UI collector is not active yet. For critical events, prefer storing them in state or designing event delivery separately.

**In short:** in Compose, `LaunchedEffect` is used to collect one-off UI effects in a coroutine scoped to the composable lifecycle.
