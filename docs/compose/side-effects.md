# Side Effects

Side effects в Compose нужны для работы, которая выходит за рамки описания UI: coroutine, подписки, listeners, analytics, snackbar, navigation events и адаптация внешних источников state.

## Effect APIs

### `LaunchedEffect`

`LaunchedEffect` запускает coroutine, привязанную к lifecycle конкретного composable call site.

Когда `LaunchedEffect` входит в Composition, coroutine стартует. Когда он выходит из Composition, coroutine отменяется. Если меняются keys, текущая coroutine отменяется и effect запускается заново с новыми keys.

Используется для suspend side effects: initial load, one-off navigation/event collection, animation, delay, scroll, snackbar flow collection, analytics из `snapshotFlow`.

Ключи важны: key должен включать значения, при изменении которых effect нужно перезапустить. Если нужно использовать свежую lambda/value без restart, применяют `rememberUpdatedState`.

**Важно:** `LaunchedEffect(Unit)` или `LaunchedEffect(true)` означает effect на lifetime call site. Это допустимо, но требует осознанного понимания, почему restart не нужен.

**Коротко:** `LaunchedEffect` runs suspend side effects scoped to composition and restarts when its keys change.

### `rememberCoroutineScope`

`rememberCoroutineScope` возвращает `CoroutineScope`, привязанный к месту вызова в Composition. Scope автоматически отменяется, когда этот call site выходит из Composition.

Используется, когда coroutine нужно запускать не сразу при входе в composition, а из event handler: `onClick`, `onDismiss`, swipe callback. Например, показать `Snackbar`, запустить animation или выполнить короткое UI-related действие по событию пользователя.

Важно не запускать coroutine прямо в body composable. Для автоматического запуска при появлении composable лучше `LaunchedEffect`, для запуска по событию - `rememberCoroutineScope`.

**Коротко:** `rememberCoroutineScope` gives a composition-aware scope for launching coroutines from callbacks and UI events.

### `DisposableEffect`

`DisposableEffect` используется для side effects, которым нужен cleanup при выходе из Composition или при изменении keys.

Типичные сценарии: зарегистрировать listener/observer/broadcast callback, подписаться на lifecycle events, подключить внешний imperative API и гарантированно отписаться в `onDispose`.

`DisposableEffect` обязан завершаться блоком `onDispose`. Если cleanup пустой, стоит проверить, не подходит ли лучше `LaunchedEffect` или `SideEffect`.

Keys должны описывать зависимости effect. Если listener зависит от `lifecycleOwner`, `lifecycleOwner` должен быть key, чтобы старый observer снялся, а новый зарегистрировался.

**Коротко:** `DisposableEffect` is for effects with setup and cleanup, like registering and unregistering observers.

### `SideEffect`

`SideEffect` используется, чтобы выполнить non-suspending side effect после успешной recomposition.

Типичный сценарий - передать актуальное Compose state во внешний объект, которым Compose не управляет: analytics, logging, imperative controller, системный объект или legacy API.

`SideEffect` выполняется после каждой успешной recomposition, поэтому его не используют для suspend work, subscriptions или cleanup. Для coroutine work нужен `LaunchedEffect`, для register/unregister - `DisposableEffect`.

**Коротко:** `SideEffect` publishes Compose state to non-Compose code after a successful recomposition.

### `produceState` / `derivedStateOf`

`produceState` - effect API, который превращает внешний источник данных в Compose `State`. Он запускает coroutine, scoped к Composition, возвращает `State<T>` и обновляет `value` из producer block.

Используется, когда нужно адаптировать non-Compose state к Compose: suspend загрузку, callback/subscription API, `Flow` / `LiveData` / RxJava-like источник или custom observer.

Когда composable выходит из Composition, producer отменяется. Если меняются keys, producer перезапускается. Для callback-based источников cleanup можно делать через `awaitDispose`.

В обычной Android-архитектуре `Flow` из `ViewModel` чаще собирают через `collectAsStateWithLifecycle()`, а `produceState` полезен для custom adapters и локальных интеграций.

`derivedStateOf` создаёт derived Compose `State` и нужен, когда input state меняется чаще, чем UI реально должен обновляться. Например, scroll index меняется постоянно, но кнопка "scroll to top" должна появиться только при переходе через threshold.

**Важно:** `derivedStateOf` не нужно использовать для обычной склейки строк или простых вычислений, которые должны обновляться так же часто, как inputs. Это overhead, а не универсальная оптимизация.

**Коротко:** `produceState` converts external async state into Compose `State`, while `derivedStateOf` reduces recomposition only when derived result changes less often than its inputs.
