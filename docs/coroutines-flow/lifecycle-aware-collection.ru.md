# Lifecycle-aware Collection

Lifecycle-aware collection нужна, чтобы UI собирал `Flow` только тогда, когда экран активен, и не продолжал лишнюю работу в фоне.

## Android UI collection

### `collectAsStateWithLifecycle`

`collectAsStateWithLifecycle()` - Compose API из `lifecycle-runtime-compose`, который собирает `Flow` / `StateFlow` и конвертирует его в Compose `State` с учётом `Lifecycle`.

Он используется в Compose UI, чтобы безопасно подписаться на `uiState` из `ViewModel`:

```kotlin
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

Главная польза: collection активна только в подходящем lifecycle state, обычно `STARTED` и выше. Когда screen уходит в background, collection приостанавливается, а при возврате возобновляется.

Для `StateFlow` это особенно удобно: UI сразу получает latest value и не запускает лишнюю работу, пока экран неактивен.

**Важно:** не стоит использовать обычный `collectAsState()` для Android screen-level flows без понимания lifecycle, потому что collection может продолжаться, когда UI уже неактивен.

**Коротко:** `collectAsStateWithLifecycle` is the recommended Compose way to collect `Flow` / `StateFlow` from `ViewModel` with Android lifecycle awareness.

### `repeatOnLifecycle`

`repeatOnLifecycle()` - lifecycle-aware API для запуска coroutine block только в определённом `Lifecycle.State`, например `STARTED`.

Когда lifecycle достигает нужного состояния, block запускается. Когда lifecycle опускается ниже этого состояния, coroutine внутри block отменяется. При возврате в нужное состояние block запускается заново.

Типичный Fragment/View System пример:

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state ->
            render(state)
        }
    }
}
```

Важно использовать `viewLifecycleOwner` для Fragment UI, а не lifecycle самого `Fragment`, потому что View lifecycle короче Fragment lifecycle.

`repeatOnLifecycle` лучше, чем `launchWhenStarted` / `launchWhenResumed`, потому что явно отменяет и перезапускает collection, а не просто suspends execution в неочевидных местах.

**Важно:** если внутри `repeatOnLifecycle` нужно collect-ить несколько `Flow` параллельно, каждый `collect` должен быть в отдельном `launch`, иначе первый `collect` заблокирует остальные.

**Коротко:** `repeatOnLifecycle` starts collection only when lifecycle is at least the target state and cancels it when the UI is stopped.

### `LaunchedEffect` для effects

В Compose одноразовые UI effects часто collect-ят через `LaunchedEffect`, потому что это coroutine, привязанная к composition lifecycle.

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

`LaunchedEffect` подходит для navigation, snackbar, scroll command, permission request trigger и других one-off effects, которые должны выполняться как реакция UI на event stream.

Ключи `LaunchedEffect` важны: если key изменится, старая coroutine отменится и collection начнётся заново. Для постоянной подписки на events обычно используют `LaunchedEffect(Unit)` или `LaunchedEffect(viewModel)`, если именно смена `ViewModel` должна перезапустить collection.

**Важно:** `SharedFlow` с `replay = 0` может потерять event, если UI collector ещё не активен. Для критичных событий лучше хранить их в state или проектировать event delivery отдельно.

**Коротко:** in Compose, `LaunchedEffect` is used to collect one-off UI effects in a coroutine scoped to the composable lifecycle.
