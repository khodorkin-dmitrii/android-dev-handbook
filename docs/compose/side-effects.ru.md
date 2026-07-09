# Side Effects

Side effects в Compose - это работа за пределами чистого описания UI: запуск coroutines, показ snackbar, analytics, регистрация listeners, collection one-off events, scroll, navigation и адаптация внешних источников state.

Composable functions в идеале должны оставаться side-effect free. Они могут рекомпозироваться много раз, пропускать recomposition, перезапускаться с другими keys или выходить из Composition. Effect APIs делают side effects явными и привязывают их к lifecycle конкретного composable call site.

## Главное правило

Не запускай работу напрямую из body composable:

```kotlin
@Composable
fun ProfileScreen(userId: String) {
    // Плохо: может выполниться на каждой recomposition.
    viewModel.loadUser(userId)

    ProfileContent()
}
```

Используй effect, когда работа должна произойти из-за входа composable в Composition, изменения key или callback, которому нужен composition-aware scope.

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

В обычной Android-архитектуре durable screen work обычно находится во `ViewModel`. Compose effects чаще нужны для UI-related координации: collect one-off UI events, показать snackbar, выполнить scroll, подключить lifecycle listener или передать state во внешний non-Compose API.

## Какой API выбрать

| Задача | API |
|---|---|
| Запустить suspend work при входе composable в Composition или при изменении key | `LaunchedEffect` |
| Запустить coroutine из user event callback | `rememberCoroutineScope` |
| Зарегистрировать что-то и затем очистить | `DisposableEffect` |
| Передать Compose state в non-Compose code после recomposition | `SideEffect` |
| Держать свежую lambda или value внутри long-running effect без restart | `rememberUpdatedState` |
| Превратить внешний async state в Compose `State` | `produceState` |
| Превратить чтение Compose state в `Flow` | `snapshotFlow` |
| Закешировать derived state, когда результат меняется реже, чем inputs | `derivedStateOf` |

## `LaunchedEffect`

`LaunchedEffect` запускает coroutine, привязанную к lifecycle конкретного composable call site.

Когда `LaunchedEffect` входит в Composition, coroutine стартует. Когда он выходит из Composition, coroutine отменяется. Если меняются keys, текущая coroutine отменяется и effect запускается заново с новыми keys.

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

Используй его для suspend side effects:

- initial UI-related work;
- показ snackbar;
- scroll или animation;
- collection one-off UI events;
- navigation events из UI state или event streams;
- analytics на основе Compose state через `snapshotFlow`.

Keys важны. Key должен включать значения, изменение которых требует restart effect.

```kotlin
LaunchedEffect(userId) {
    viewModel.load(userId)
}
```

Если значение или lambda должны оставаться свежими внутри long-running effect, но сам effect не должен restart, используй `rememberUpdatedState`.

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

`LaunchedEffect(Unit)` или `LaunchedEffect(true)` означает "запустить на lifetime этого call site". Это нормально, например для collection стабильного event stream, но должно быть осознанным решением.

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

**Коротко:** `LaunchedEffect` запускает suspend side effects, scoped к Composition, и перезапускается при изменении keys.

## `rememberCoroutineScope`

`rememberCoroutineScope` возвращает `CoroutineScope`, привязанный к текущему call site в Composition. Scope отменяется, когда этот call site выходит из Composition.

Используй его, когда coroutine должна стартовать из event handler, а не автоматически при появлении composable.

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

Хорошие сценарии:

- `onClick`;
- `onDismiss`;
- swipe callbacks;
- локальный snackbar;
- короткий UI-related animation или scroll action.

Не используй его, чтобы спрятать business logic внутри UI. Если работа должна переживать configuration changes или относится к screen state, перенеси её во `ViewModel`.

**Коротко:** `rememberCoroutineScope` даёт composition-aware scope для запуска coroutines из callbacks и UI events.

## `DisposableEffect`

`DisposableEffect` используется для side effects, которым нужен cleanup при выходе из Composition или при изменении keys.

Типичные сценарии:

- зарегистрировать и снять listener;
- observe lifecycle events;
- подключить imperative API;
- подписаться на callback source.

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

`DisposableEffect` обязан завершаться `onDispose`. Если cleanup пустой, проверь, не подходит ли лучше `LaunchedEffect` или `SideEffect`.

Keys должны описывать зависимости. Если listener зависит от `lifecycleOwner`, то `lifecycleOwner` должен быть key, чтобы старый observer снялся, а новый зарегистрировался.

**Коротко:** `DisposableEffect` подходит для effects с setup и cleanup.

## `SideEffect`

`SideEffect` запускает non-suspending side effect после каждой успешной recomposition.

Используй его, чтобы передать текущий Compose state в non-Compose code:

- analytics user properties;
- logging;
- imperative controller state;
- legacy UI integration;
- внешний объект, которым Compose не управляет.

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

`SideEffect` выполняется после каждой успешной recomposition. Не используй его для suspend work, subscriptions, cleanup или дорогих операций. Coroutine work относится к `LaunchedEffect`; setup и cleanup - к `DisposableEffect`.

**Коротко:** `SideEffect` публикует Compose state в non-Compose code после успешной recomposition.

## `produceState`

`produceState` превращает внешний async state в Compose `State`.

Он запускает coroutine, scoped к Composition, возвращает `State<T>` и обновляет `value` из producer block. Когда composable выходит из Composition, producer отменяется. Если меняются keys, producer перезапускается.

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

Для callback-based sources используй `awaitDispose` для cleanup.

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

В обычных Android-приложениях `Flow` из `ViewModel` чаще собирают через `collectAsStateWithLifecycle()`. Используй `produceState` в основном для custom adapters, локальных интеграций и нестандартных callback sources.

**Коротко:** `produceState` превращает внешний async или callback-based state в Compose `State`.

## `snapshotFlow`

`snapshotFlow` превращает чтение Compose state внутри своего block в cold `Flow`.

Это полезно, когда изменения Compose state должны пройти через Flow operators, analytics или event-like processing.

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

Используй его, когда нужны Flow operators поверх Compose state. Не используй его для обычного UI rendering: Compose может читать state напрямую.

**Коротко:** `snapshotFlow` связывает Compose snapshot state с `Flow`.

## `derivedStateOf`

`derivedStateOf` создаёт derived Compose `State`.

Используй его, когда input state меняется чаще, чем UI должен обновляться, а derived result меняется реже.

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

Не используй `derivedStateOf` для обычных дешёвых вычислений, которые должны обновляться вместе с inputs.

```kotlin
// Обычно не нужно.
val fullName by remember {
    derivedStateOf { "$firstName $lastName" }
}
```

Это overhead, а не optimization.

**Коротко:** `derivedStateOf` уменьшает лишнюю recomposition только когда derived result меняется реже, чем inputs.

## Частые ошибки

### Запуск работы из composable body

```kotlin
@Composable
fun BadScreen(viewModel: VM) {
    viewModel.load() // Плохо
}
```

Используй `LaunchedEffect` или перенеси trigger во `ViewModel`.

### Неправильные keys

```kotlin
LaunchedEffect(Unit) {
    viewModel.load(userId)
}
```

Если `userId` изменится, пока тот же call site остаётся в Composition, effect не перезапустится. Лучше:

```kotlin
LaunchedEffect(userId) {
    viewModel.load(userId)
}
```

### Слишком частый restart

```kotlin
LaunchedEffect(onEvent) {
    delay(1_000)
    onEvent()
}
```

Если `onEvent` часто создаётся заново, effect будет часто restart. Используй `rememberUpdatedState`, если restart не нужен.

### Пустой cleanup

```kotlin
DisposableEffect(Unit) {
    onDispose { }
}
```

Обычно это признак, что лучше подходит другой Effect API.

## Related topics

- [State & Recomposition](state-recomposition.md)
- [Compose Performance](performance.md)
- [UI State Architecture](../architecture/ui-state.md)
- [Lifecycle-aware Collection](../coroutines-flow/lifecycle-aware-collection.md)
